"""Aggregator: walks a project workspace, produces a DefensePack."""
from __future__ import annotations
import datetime
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


def aggregate_from_dir(workspace: Path) -> DefensePack:
    workspace = Path(workspace)
    state = _read_state(workspace)
    project_name = state.get("Project name", "")
    context = state.get("Context", "")
    scaffolding_level = state.get("Scaffolding level", "")
    phase = state.get("Phase", "")
    student_name = state.get("Preferred name", "") or state.get("Name", "")

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
        auto_disclosure = Disclosure(
            form="short",
            text=(
                f"This work was produced through structured human-AI collaboration. "
                f"The author directed all substantive decisions consistent with their Position Statement. "
                f"{len(rors)} Records of Resistance document specific decisions to reject or revise AI suggestions."
                f"{log_clause}"
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

    return pack
