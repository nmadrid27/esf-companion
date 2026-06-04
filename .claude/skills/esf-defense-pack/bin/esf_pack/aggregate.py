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
    extract_inline_resists,
)
from .gaps import detect_gaps


COMPANION_VERSION = "0.9.1"


def find_context_root(start: Path) -> Path:
    """Walk upward from `start` until we find a companion-state.md."""
    p = start.resolve()
    while p != p.parent:
        if (p / "companion-state.md").exists():
            return p
        p = p.parent
    raise FileNotFoundError(f"No companion-state.md found from {start}")


_COMPANION_STATE_LOCATIONS = (
    "companion-state.md",                    # canonical (v0.8.0+)
    "esf/companion-state.md",                # canonical alt
    "projects/_esf/companion-state.md",      # pre-v0.8.0 layout (real users in the wild)
    "_esf/companion-state.md",               # variant pre-v0.8.0
    ".esf/companion-state.md",               # variant
)


# Directory names skipped when auto-discovering cycle-based layouts. The
# blacklist guards against accidentally pulling RoRs out of canonical install
# trees (where they're already discovered), virtualenvs, VCS metadata, and
# template/example directories that look like records but aren't.
_CYCLE_DIR_BLACKLIST = frozenset({
    "esf", "projects", "_esf", ".esf",
    "templates", "examples", "node_modules",
    "venv", ".venv", "__pycache__",
    ".git", ".github", ".claude",
    "test", "tests",
})

# A cycle-dir candidate must contain at least one file matching one of these
# patterns. Defines what "looks like a cycle dir" without keying on dir names
# (students name them p2-break-through, milestone-3, cycle-1, etc.).
_CYCLE_DIR_MARKER_PATTERNS = (
    "record-of-resistance*.md",
    "position-statement*.md",
)


def _discover_cycle_dirs(workspace: Path) -> list[Path]:
    """Find direct-child directories that look like ESF cycle/phase dirs.

    A cycle dir is a top-level directory in the workspace that holds ESF
    artifacts directly (no `records-of-resistance/` subfolder), as students
    sometimes organize work by milestone/cycle (e.g. `p2-break-through/`,
    `p3-next-steps/`) rather than by artifact type. Returns sorted list so
    aggregation order is deterministic across runs.
    """
    discovered: list[Path] = []
    if not workspace.is_dir():
        return discovered
    # Guard against unreadable workspaces — a directory we can stat but not
    # read raises PermissionError/OSError from iterdir(). Returning [] is the
    # safe fallback; downstream gap detection surfaces the missing artifacts
    # rather than crashing the whole aggregator on a permission error.
    try:
        children = sorted(workspace.iterdir())
    except OSError:
        return discovered
    for child in children:
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        # Lowercase the comparison so case-insensitive filesystems (macOS APFS
        # default, NTFS) don't let `Templates/` or `Tests/` bypass the guard.
        # The blacklist itself is already all-lowercase.
        if child.name.lower() in _CYCLE_DIR_BLACKLIST:
            continue
        for pattern in _CYCLE_DIR_MARKER_PATTERNS:
            if any(child.glob(pattern)):
                discovered.append(child)
                break
    return discovered


def _find_companion_state(workspace: Path) -> Path:
    """Locate companion-state.md across known install layouts.

    The v0.8.0 release consolidated everything under `esf/toolkit/`, but real
    student workspaces in the wild were installed under earlier versions that
    placed companion-state in `projects/_esf/` or similar. Searching a small
    set of known locations means the Defense Pack works against existing
    workspaces without requiring a re-install or migration.
    """
    for rel in _COMPANION_STATE_LOCATIONS:
        candidate = workspace / rel
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"companion-state.md not found in {workspace} or any known subdirectory "
        f"({', '.join(_COMPANION_STATE_LOCATIONS)}). "
        f"Run /esf-onboarding to initialize the workspace, or move your "
        f"companion-state.md to {workspace}/companion-state.md."
    )


def _read_state(workspace: Path) -> dict:
    """Parse companion-state.md into a flat dict of the keys we need.

    Also extracts a 'Defense Pack Paths' override section if present — students
    with non-canonical workspace layouts can point the aggregator at their
    actual artifact locations explicitly.
    """
    state_path = _find_companion_state(workspace)
    text = state_path.read_text(encoding="utf-8")
    state: dict = {}
    in_defense_paths = False
    defense_paths: dict = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        # Detect the optional "## Defense Pack Paths" section. While inside it,
        # bullet keys collect into a separate dict (e.g. {"Position Statement": "..."})
        # rather than into the flat state.
        if line.startswith("## "):
            in_defense_paths = line.lower().startswith("## defense pack paths")
            continue
        if line.startswith("- **") and ":**" in line:
            k, _, v = line.partition(":**")
            key = k.lstrip("- *").strip()
            value = v.strip().rstrip("*").strip()
            if in_defense_paths:
                defense_paths[key] = value
            else:
                state[key] = value
    if defense_paths:
        state["__defense_paths__"] = defense_paths  # special key, consumed by aggregator
    return state


def _validate_path_segment(value: str, field_name: str) -> None:
    """Reject path-traversal patterns in single-segment path fields.

    Applied to fields that name ONE directory or file component (Project name,
    Context). Forbids `..`, `/`, `\\`, and null bytes. Real project names
    contain spaces, parens, and other ordinary characters and remain legal.
    """
    if not value:
        return
    forbidden = ["..", "/", "\\", "\x00"]
    for bad in forbidden:
        if bad in value:
            raise ValueError(
                f"companion-state.md `{field_name}` contains a path-traversal "
                f"pattern ({bad!r}) that isn't allowed: {value!r}."
            )


def _validate_relative_path(value: str, field_name: str) -> None:
    """Reject only true traversal in multi-segment override paths.

    Applied to the optional Defense Pack Paths override values, which ARE
    relative paths (e.g. `projects/AI201/references/M2-position-statement.md`)
    and legitimately contain `/`. We block parent-directory references (`..`),
    absolute paths (leading `/`), and null bytes.
    """
    if not value:
        return
    if value.startswith("/") or value.startswith("\\"):
        raise ValueError(
            f"companion-state.md Defense Pack Paths `{field_name}` must be a "
            f"relative path (no leading `/`): {value!r}."
        )
    if "\x00" in value:
        raise ValueError(
            f"companion-state.md Defense Pack Paths `{field_name}` contains a "
            f"null byte: {value!r}."
        )
    # Walk segments looking for `..`
    for segment in value.replace("\\", "/").split("/"):
        if segment == "..":
            raise ValueError(
                f"companion-state.md Defense Pack Paths `{field_name}` contains "
                f"a parent-directory reference (`..`) that isn't allowed: {value!r}."
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

    # Resolve artifact locations. Order:
    #   1. Explicit overrides from companion-state's "Defense Pack Paths" section
    #   2. Canonical v0.8.0+ layout: esf/<context>/...
    #   3. Pre-v0.8.0 fallback layout: projects/<context>/...
    #   4. Filename-pattern fallback (real students rename files: M2-position-statement.md)
    #   5. Cycle-based layout (top-level milestone dirs holding artifacts directly)
    overrides: dict = state.get("__defense_paths__", {}) or {}
    cycle_dirs = _discover_cycle_dirs(workspace)
    # Track which artifact names came from cycle discovery (rather than a single
    # boolean). This drives a precise INFO gap message: a workspace where only
    # the PS resolves through the cycle path but RoRs are in canonical
    # `records-of-resistance/` shouldn't claim that artifacts (plural) were in
    # milestone dirs.
    cycle_resolved_artifacts: set = set()

    def _resolve_file(
        override_key: str,
        canonical_subdir: str,
        filename_patterns: list,
        cycle_artifact_name: str = "",
    ) -> Path:
        """Resolve a file path: override → canonical → legacy → glob fallback → cycle dirs.

        `filename_patterns` are glob-style patterns tried in order against each
        candidate directory until a match is found. `cycle_artifact_name`, if
        non-empty, is the artifact label recorded into `cycle_resolved_artifacts`
        when the resolution falls through to the cycle-based fallback.
        """
        override = overrides.get(override_key, "").strip()
        if override and override.lower() not in ("(none)", "none", "n/a", "-"):
            _validate_relative_path(override, override_key)
            return workspace / override
        candidate_dirs = [
            workspace / "esf" / context / canonical_subdir,
            workspace / "projects" / context / canonical_subdir,
            workspace / "projects" / context / "references",
            workspace / "projects" / context,
        ]
        for d in candidate_dirs:
            if not d.exists():
                continue
            for pattern in filename_patterns:
                matches = sorted(d.glob(pattern))
                if matches:
                    return matches[0]
        # Cycle-based fallback: scan top-level milestone dirs for the same patterns.
        # Drop only the bare `<project_name>.md` catch-all (index 0) — in a mixed
        # milestone dir, matching a file by project name is too loose and would
        # grab unrelated artifacts. Keep every artifact-specific glob, including
        # single-pattern ones like `*reflection*.md` (dropping those left whole
        # artifacts undiscoverable in cycle layouts).
        cycle_patterns = [p for p in filename_patterns if p.startswith("*")]
        for d in cycle_dirs:
            for pattern in cycle_patterns:
                matches = sorted(d.glob(pattern))
                if matches:
                    if cycle_artifact_name:
                        cycle_resolved_artifacts.add(cycle_artifact_name)
                    return matches[0]
        # Return canonical-path-that-doesn't-exist so gap detection fires cleanly.
        return workspace / "esf" / context / canonical_subdir / filename_patterns[0].lstrip("*")

    def _resolve_ror_dirs(override_key: str, canonical_subdir: str) -> tuple[list[Path], bool]:
        """Resolve RoR scan roots. Returns (dirs, from_cycle).

        `from_cycle` is True only when the returned dirs are milestone/cycle
        directories that hold MIXED artifacts (records alongside the position
        statement, reflection, etc.). The scanner uses that flag to pick a
        strict `record-of-resistance*.md` glob for cycle dirs versus the
        permissive `*.md` for dedicated `records-of-resistance/` dirs. It is NOT
        derived from how many dirs are returned: canonical+legacy can both exist
        (two dedicated dirs) without being cycle dirs, and a lone milestone dir
        is still a cycle dir.
        """
        override = overrides.get(override_key, "").strip()
        if override and override.lower() not in ("(none)", "none", "n/a", "-"):
            _validate_relative_path(override, override_key)
            return [workspace / override], False
        existing = [
            d for d in (
                workspace / "esf" / context / canonical_subdir,
                workspace / "projects" / context / canonical_subdir,
            )
            if d.exists()
        ]
        if existing:
            return existing, False
        if cycle_dirs:
            cycle_resolved_artifacts.add("Records of Resistance")
            return list(cycle_dirs), True
        # Nothing found — return canonical-path-that-doesn't-exist so the empty
        # scan downstream surfaces as a "no RoRs" gap rather than a crash.
        return [workspace / "esf" / context / canonical_subdir], False

    # Build per-artifact filename patterns. Project names with spaces/parens are
    # used as-is in the canonical pattern; the slug-like fallbacks catch the
    # common real-student renames.
    ps_path = _resolve_file(
        "Position Statement",
        "position-statements",
        [
            f"{project_name}.md",          # canonical
            "*position-statement*.md",     # M2-position-statement.md, etc.
            "*position*.md",               # broad fallback
        ],
        cycle_artifact_name="Position Statement",
    )
    ror_dirs, ror_dirs_are_cycle = _resolve_ror_dirs("Records of Resistance", "records-of-resistance")
    log_path = _resolve_file(
        "AI Use Log",
        "ai-use-logs",
        [
            f"{project_name}.md",
            "*ai-use-log*.md",
            "*ai-log*.md",
        ],
        cycle_artifact_name="AI Use Log",
    )
    reflection_path = _resolve_file(
        "Reflection",
        "reflections",
        [
            f"{project_name}.md",
            "*reflection*.md",
        ],
        cycle_artifact_name="Reflection",
    )

    ps = None
    if ps_path.exists():
        ps = parse_position_statement(ps_path.read_text(encoding="utf-8"))

    rors: list = []
    mismatched_rors: list = []
    # Skip summary/compilation files — they're metadata, not discrete records.
    _RECORD_SKIP_RE = __import__("re").compile(
        r"(compiled|summary|index|readme|template)",
        __import__("re").IGNORECASE,
    )
    auto_number = 0
    # Cycle/milestone dirs hold mixed artifacts (records alongside the position
    # statement, reflection, log), so restrict the glob to record files there.
    # Dedicated `records-of-resistance/` dirs (canonical or legacy) hold only
    # records, so `*.md` is correct and preserves back-compat with arbitrarily
    # named record files (e.g. `1-grid-rejection.md`, `01-pivot.md`).
    ror_file_pattern = "record-of-resistance*.md" if ror_dirs_are_cycle else "*.md"
    seen_files: set = set()  # guard against double-counting if dirs overlap
    for ror_dir in ror_dirs:
        if not ror_dir.exists():
            continue
        for f in sorted(ror_dir.glob(ror_file_pattern)):
            if f.resolve() in seen_files:
                continue
            seen_files.add(f.resolve())
            if _RECORD_SKIP_RE.search(f.name):
                continue
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
            try:
                ror.source = str(f.relative_to(workspace))
            except ValueError:
                ror.source = f.name
            # Auto-assign record numbers when frontmatter doesn't have one.
            # Without this, records in directories that don't use record-number
            # frontmatter all collide at 0 and the duplicate-warning fires for
            # every file.
            if ror.record_number == 0:
                auto_number += 1
                ror.record_number = auto_number
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

    # Scan process-blog files for inline @resist / @default / @shift tags. This
    # supports the taught convention where students annotate their session
    # narrative inline rather than (or in addition to) producing discrete RoR
    # files. Each @resist tag becomes a supplementary RecordOfResistance with
    # the surrounding paragraph as the inline_narrative.
    resist_count = 0
    default_count = 0
    shift_count = 0
    process_blog_sources: list[str] = []
    # Canonical process-blog locations, plus the discovered cycle dirs so that
    # students who keep inline @resist/@default/@shift tags in milestone notes
    # (e.g. p2-break-through/session-notes.md) get a non-zero resist_count.
    blog_search_roots = [
        workspace / "esf" / context / "process-blog",
        workspace / "projects" / context / "process-blog",
        workspace / "process-blog",
    ]
    blog_search_roots.extend(cycle_dirs)
    inline_record_offset = max((r.record_number for r in rors), default=0) + 1000
    inline_seq = 0
    # Skip filenames that are templates, readmes, or example/instruction files.
    _BLOG_SKIP_RE = __import__("re").compile(
        r"(template|readme|instructions?|example|tutorial)",
        __import__("re").IGNORECASE,
    )
    # Cycle dirs also hold the record-of-resistance / position-statement /
    # reflection / ai-use-log markdown files; those have already been parsed
    # above and must not be re-scanned for inline @resist tags (a record-of-
    # resistance file isn't a process-blog session). Skip these markers in
    # cycle-dir scans only — canonical process-blog/ dirs shouldn't contain
    # them at all.
    _CYCLE_BLOG_SKIP_RE = __import__("re").compile(
        r"(record-of-resistance|position-statement|reflection|ai-use-log|ai-log)",
        __import__("re").IGNORECASE,
    )
    # Path-based dedupe so a file that happens to appear under multiple roots
    # (e.g. cycle_dir overlapping with a canonical root in some odd layout)
    # is only counted once. process_blog_sources alone wasn't enough: it
    # short-circuits the list-append but not the resist_count increment.
    seen_blog_files: set = set()
    consumed_any_canonical = False
    for root in blog_search_roots:
        if not root.exists():
            continue
        is_cycle_dir = root in cycle_dirs
        # Preserve the historical behavior of consuming only the first existing
        # canonical root. Cycle dirs are additive: scan every one of them so a
        # student with both p2- and p3- session notes gets both counted.
        if not is_cycle_dir and consumed_any_canonical:
            continue
        for blog_file in sorted(root.glob("*.md")):
            if _BLOG_SKIP_RE.search(blog_file.name):
                continue
            if is_cycle_dir and _CYCLE_BLOG_SKIP_RE.search(blog_file.name):
                continue
            resolved = blog_file.resolve()
            if resolved in seen_blog_files:
                continue
            seen_blog_files.add(resolved)
            try:
                text = blog_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            inline_rors, rc, dc, sc = extract_inline_resists(
                text, source_label=str(blog_file.relative_to(workspace)),
            )
            resist_count += rc
            default_count += dc
            shift_count += sc
            if blog_file.relative_to(workspace).as_posix() not in process_blog_sources:
                process_blog_sources.append(blog_file.relative_to(workspace).as_posix())
            for inline_ror in inline_rors:
                inline_seq += 1
                inline_ror.record_number = inline_record_offset + inline_seq
                inline_ror.project = project_name  # not filtered; treated as belonging
                rors.append(inline_ror)
        if not is_cycle_dir:
            consumed_any_canonical = True

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
        # Process tag metrics — quantitative evidence when present.
        metrics_clause = ""
        if resist_count + default_count + shift_count > 0:
            metrics_clause = (
                f" Process tracking across {len(process_blog_sources)} session "
                f"blog(s) records {resist_count} @resist moment(s), "
                f"{default_count} @default acceptance(s), and {shift_count} "
                f"@shift redirect(s)."
            )
        auto_disclosure = Disclosure(
            form="short",
            text=(
                f"This work was produced through structured human-AI collaboration. "
                f"The author directed all substantive decisions consistent with their "
                f"Position Statement. {ror_clause}{log_clause}{metrics_clause}"
            ),
        )

    pack = DefensePack(
        resist_count=resist_count,
        default_count=default_count,
        shift_count=shift_count,
        process_blog_sources=process_blog_sources,
        project_name=project_name,
        context=context,
        student_name=student_name,
        scaffolding_level=scaffolding_level,
        phase_at_export=phase,
        # Compact UTC form aligns with the SKILL folder-name convention
        # (`date -u +%Y-%m-%dT%H%M%SZ`) so the pack's `export_timestamp` field
        # and the timestamped folder name share the same shape (no colons,
        # trailing `Z`).
        export_timestamp=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ"),
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

    # Soften the AI Use Log and Reflection warnings when a process blog is
    # present — for students using the @resist / @default / @shift convention,
    # the process blog substitutes for both artifacts. The warnings would
    # otherwise mislead faculty into thinking work is missing when it just
    # lives in a different format.
    if pack.process_blog_sources:
        from .schema import GapSeverity
        for g in pack.gaps:
            if g.artifact == "ai_use_log" and g.severity == GapSeverity.WARNING:
                g.message = (
                    f"No dedicated AI Use Log file found, but {pack.resist_count} "
                    f"AI interactions are documented inline across "
                    f"{len(pack.process_blog_sources)} process-blog session(s) "
                    f"via the @resist/@default/@shift convention. The process blog "
                    f"substitutes for a discrete log file."
                )
                g.severity = GapSeverity.INFO
            elif g.artifact == "reflection" and g.severity == GapSeverity.WARNING:
                g.message = (
                    f"No discrete Reflection file found. Process-blog sessions may "
                    f"contain in-session reflection; the Five Questions checklist "
                    f"can be run independently before submission."
                )
                # Leave as warning — process blog doesn't fully substitute for
                # a Reflection (which captures end-of-project synthesis).

    # Surface mismatched RoRs as a warning gap so the student knows their work
    # didn't silently disappear.
    if mismatched_rors:
        from .schema import Gap, GapSeverity
        details = ", ".join(f"{name} (project={proj!r})" for name, proj in mismatched_rors)
        scanned = ", ".join(str(d) for d in ror_dirs) or "(no RoR directory resolved)"
        pack.gaps.append(Gap(
            artifact="record_of_resistance",
            severity=GapSeverity.WARNING,
            message=(
                f"{len(mismatched_rors)} Record(s) of Resistance under {scanned} have a "
                f"different `project` frontmatter than `{project_name}` and were NOT "
                f"included in this pack: {details}. If they belong to this project, "
                f"update their frontmatter; otherwise move them to the correct project's "
                f"directory."
            ),
        ))

    # Surface cycle-based auto-discovery as an INFO gap. Not a problem; just a
    # breadcrumb so faculty understand where artifacts came from, and so the
    # student knows they can declare `## Defense Pack Paths` for determinism.
    # Only name the artifacts that actually resolved through the cycle path,
    # not the union of every artifact in the pack — otherwise a workspace where
    # only PS lives in a milestone dir while RoRs sit in canonical
    # `records-of-resistance/` misleads the reader about which paths were used.
    if cycle_resolved_artifacts:
        from .schema import Gap, GapSeverity
        try:
            discovered_names = ", ".join(sorted(d.name for d in cycle_dirs))
        except Exception:
            discovered_names = "(unavailable)"
        resolved_list = ", ".join(sorted(cycle_resolved_artifacts))
        pack.gaps.append(Gap(
            artifact="workspace_layout",
            severity=GapSeverity.INFO,
            message=(
                f"Auto-discovered cycle-based workspace layout. The following "
                f"artifact(s) were located in milestone directories "
                f"({discovered_names}) rather than their canonical folders: "
                f"{resolved_list}. The pack is complete; consider declaring an "
                f"explicit `## Defense Pack Paths` section in companion-state.md "
                f"if you want the layout pinned rather than auto-detected."
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
