"""Aggregator: walks a project workspace, produces a DefensePack."""
from __future__ import annotations
import datetime
import re
from pathlib import Path
from .schema import DefensePack, Disclosure
from .parsers import (
    parse_position_statement,
    parse_record_of_resistance,
    parse_ai_use_log,
    parse_reflection,
)
from .gaps import detect_gaps


COMPANION_VERSION = "0.8.0"


def find_context_root(start: Path) -> Path:
    """Walk upward from `start` until we find a companion-state.md."""
    p = start.resolve()
    while p != p.parent:
        if (p / "companion-state.md").exists():
            return p
        p = p.parent
    raise FileNotFoundError(f"No companion-state.md found from {start}")


def _read_state(workspace: Path) -> dict:
    """Parse companion-state.md into a flat dict of the keys we need."""
    text = (workspace / "companion-state.md").read_text(encoding="utf-8")
    state: dict = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- **") and ":**" in line:
            k, _, v = line.partition(":**")
            state[k.lstrip("- *").strip()] = v.strip().rstrip("*").strip()
    return state


_SAFE_PATH_SEGMENT_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def _validate_path_segment(value: str, field_name: str) -> None:
    """Reject path-traversal characters and separators in path-component fields.

    The threat is hypothetical (single-user, local execution) but companion-state.md
    is a hand-edited markdown file with no schema enforcement. A typo or copy/paste
    accident could leave a `..` or a `/` in `Context` or `Project name` that
    silently directs reads outside the intended directory tree.
    """
    if value and not _SAFE_PATH_SEGMENT_RE.match(value):
        raise ValueError(
            f"companion-state.md `{field_name}` contains characters that aren't "
            f"safe as a directory or file segment: {value!r}. Use only letters, "
            f"digits, dots, underscores, and dashes."
        )


def aggregate_from_dir(workspace: Path) -> DefensePack:
    workspace = Path(workspace)
    state = _read_state(workspace)
    if not state:
        # Empty companion-state.md (or absent / malformed) produces an aggregator
        # that points at `esf//position-statements/.md` — a garbage path that
        # later surfaces as a confusing "no Position Statement" gap. Catch it
        # here as a hard-stop with clear messaging.
        raise ValueError(
            f"companion-state.md at {workspace} could not be parsed or is empty. "
            f"Expected bullet lines like `- **Project name:** my-project`. "
            f"Run /esf-onboarding to (re)initialize the workspace."
        )
    project_name = state.get("Project name", "")
    context = state.get("Context", "")
    scaffolding_level = state.get("Scaffolding level", "")
    phase = state.get("Phase", "")
    student_name = state.get("Preferred name", "") or state.get("Name", "")
    _validate_path_segment(project_name, "Project name")
    _validate_path_segment(context, "Context")

    ctx_root = workspace / "esf" / context
    ps_path = ctx_root / "position-statements" / f"{project_name}.md"
    ror_dir = ctx_root / "records-of-resistance"
    log_path = ctx_root / "ai-use-logs" / f"{project_name}.md"
    reflection_path = ctx_root / "reflections" / f"{project_name}.md"

    ps = None
    if ps_path.exists():
        ps = parse_position_statement(ps_path.read_text(encoding="utf-8"))

    rors: list = []
    mismatched_rors: list = []
    if ror_dir.exists():
        for f in sorted(ror_dir.glob("*.md")):
            try:
                ror = parse_record_of_resistance(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            # Filter by frontmatter `project` match. RoRs filed under a different
            # project (or with no project frontmatter) shouldn't silently leak
            # into this pack — that would mix unrelated decisions into a defense.
            if ror.project and ror.project != project_name:
                mismatched_rors.append((f.name, ror.project))
                continue
            rors.append(ror)
        rors.sort(key=lambda r: r.record_number)

    # Detect duplicate record-numbers and collect for a warning gap below.
    # Two RoRs sharing a number means at least one was misnumbered; the sort
    # above is stable but order between duplicates becomes filename-dependent.
    seen_numbers: dict = {}
    duplicate_numbers: list = []
    for r in rors:
        if r.record_number in seen_numbers:
            duplicate_numbers.append(r.record_number)
        seen_numbers[r.record_number] = True

    log = parse_ai_use_log(log_path.read_text(encoding="utf-8")) if log_path.exists() else None
    refl = parse_reflection(reflection_path.read_text(encoding="utf-8")) if reflection_path.exists() else None

    # Auto-disclosure is generated whenever there's a Position Statement.
    # The log presence affects the disclosure's specificity (interaction count etc.),
    # but its absence shouldn't leave the disclosure section empty in partial packs.
    auto_disclosure = None
    if ps:
        log_clause = ""
        if log:
            log_clause = f" {log.interaction_count} AI interactions are logged."
        # Adjust the RoR clause to read naturally for 0, 1, and N records.
        if len(rors) == 0:
            ror_clause = (
                "No Records of Resistance are included in this pack; the defense "
                "rests on the Position Statement and Reflection."
            )
        elif len(rors) == 1:
            ror_clause = (
                "1 Record of Resistance documents a specific decision to reject "
                "or revise an AI suggestion."
            )
        else:
            ror_clause = (
                f"{len(rors)} Records of Resistance document specific decisions "
                f"to reject or revise AI suggestions."
            )
        auto_disclosure = Disclosure(
            form="short",
            text=(
                f"This work was produced through structured human-AI collaboration. "
                f"The author directed all substantive decisions consistent with their "
                f"Position Statement. {ror_clause}{log_clause}"
            ),
        )

    pack = DefensePack(
        project_name=project_name,
        context=context,
        student_name=student_name,
        scaffolding_level=scaffolding_level,
        phase_at_export=phase,
        export_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        companion_version=COMPANION_VERSION,
        position_statement=ps,
        records_of_resistance=rors,
        key_decisions=[],
        ai_use_log=log,
        reflection=refl,
        disclosure=auto_disclosure,
        evolution_log_entries=[],
        narrative=None,
        gaps=[],
    )
    pack.gaps = detect_gaps(pack)

    # Surface mismatched RoRs as a warning gap so the student knows their work
    # didn't silently disappear.
    if mismatched_rors:
        from .schema import Gap, GapSeverity
        details = ", ".join(f"{name} (project={proj!r})" for name, proj in mismatched_rors)
        pack.gaps.append(Gap(
            artifact="record_of_resistance",
            severity=GapSeverity.WARNING,
            message=(
                f"{len(mismatched_rors)} Record(s) of Resistance in {ror_dir} have a "
                f"different `project` frontmatter than `{project_name}` and were NOT "
                f"included in this pack: {details}. If they belong to this project, "
                f"update their frontmatter; otherwise move them to the correct project's "
                f"directory."
            ),
        ))

    # Surface duplicate record-numbers — the pack will still render but the
    # order between duplicates is filename-dependent, which can change defenses.
    if duplicate_numbers:
        from .schema import Gap, GapSeverity
        uniq = sorted(set(duplicate_numbers))
        pack.gaps.append(Gap(
            artifact="record_of_resistance",
            severity=GapSeverity.WARNING,
            message=(
                f"Duplicate Record of Resistance number(s) found: "
                f"{', '.join(f'#{n}' for n in uniq)}. The duplicates were included "
                f"in the pack but their order in the defense is filename-dependent. "
                f"Renumber to a unique sequence before the defense."
            ),
        ))

    return pack
