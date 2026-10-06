"""Gap detection logic. Reused by Defense Pack aggregator and (future) periodic scanner."""
from __future__ import annotations
from .schema import DefensePack, Gap, GapSeverity, BriefRequirements


def detect_gaps(pack: DefensePack, requirements: "BriefRequirements | None" = None) -> list[Gap]:
    """Return list of Gap objects describing what's missing or insufficient."""
    gaps: list[Gap] = []

    ps = pack.position_statement
    if not ps or not (ps.stance and ps.what_matters_most and ps.non_negotiables):
        gaps.append(Gap(
            artifact="position_statement",
            severity=GapSeverity.HARD_STOP,
            message="Position Statement is empty or incomplete. Defense Pack requires "
                    "stance, what matters most, and non-negotiables. "
                    "See templates/position-statement-template.md.",
        ))

    ror_min = requirements.ror_minimum if requirements else None
    ror_count = len(pack.records_of_resistance)
    if ror_min is not None and ror_count < ror_min:
        gaps.append(Gap(
            artifact="record_of_resistance",
            severity=GapSeverity.WARNING,
            message=f"Records of Resistance: {ror_count} of {ror_min} required "
                    f"(below the brief's minimum).",
        ))
    elif ror_min is None and ror_count == 0:
        gaps.append(Gap(
            artifact="record_of_resistance",
            severity=GapSeverity.WARNING,
            message="No Records of Resistance found. Defense rests on Position Statement "
                    "and Reflection only. Consider whether this matches your scaffolding level.",
        ))

    log = pack.ai_use_log
    if log is None:
        gaps.append(Gap(
            artifact="ai_use_log",
            severity=GapSeverity.WARNING,
            message="No AI Use Log found. Pack includes Records of Resistance and Reflection only.",
        ))
    elif not (log.interaction_count
              or log.intervention_summary.strip()
              or log.pattern_analysis.strip()):
        # A log whose headings don't match the parser produces an object with
        # every field blank. Without this it renders as an empty section and
        # nothing warns the student, which is the one place a silent gap is
        # least affordable: they find out during the defense.
        gaps.append(Gap(
            artifact="ai_use_log",
            severity=GapSeverity.WARNING,
            message="AI Use Log found but empty: no interactions logged, no intervention "
                    "summary, and no pattern analysis. It will render as a blank section. "
                    "Check that its headings match the template you started from.",
        ))

    if pack.reflection is None:
        gaps.append(Gap(
            artifact="reflection",
            severity=GapSeverity.WARNING,
            message="No Reflection found. Pack does not include the Five Questions check or "
                    "the kept/revised/rejected summary.",
        ))

    if pack.disclosure is None:
        gaps.append(Gap(
            artifact="disclosure",
            severity=GapSeverity.INFO,
            message="No Disclosure found. A short-form disclosure will be auto-generated.",
        ))

    if not pack.evolution_log_entries:
        gaps.append(Gap(
            artifact="evolution_log",
            severity=GapSeverity.INFO,
            message="No Evolution Log entries reference this project. (Optional artifact.)",
        ))

    return gaps


def has_hard_stop(gaps: list[Gap]) -> bool:
    return any(g.severity == GapSeverity.HARD_STOP for g in gaps)
