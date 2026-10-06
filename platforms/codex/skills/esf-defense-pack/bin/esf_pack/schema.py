"""DefensePack data structure — contract between aggregator and renderer."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GapSeverity(str, Enum):
    HARD_STOP = "hard_stop"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Gap:
    artifact: str
    severity: GapSeverity
    message: str


@dataclass(frozen=True)
class BriefRequirements:
    """Assignment/course requirements parsed from the project brief.

    Kept OFF DefensePack (which is the serialized artifact contract). Passed to
    gap detection as injected config so requirements never leak into pack.json.
    """
    ror_minimum: Optional[int] = None


@dataclass
class PositionStatement:
    stance: str
    what_matters_most: str
    non_negotiables: str
    drift_level: Optional[str]
    drift_what_shifted: Optional[str]
    drift_was_user_decision: Optional[bool]


@dataclass
class RecordOfResistance:
    record_number: int
    date: str
    ai_suggested: str
    why_rejected: str
    what_i_did_instead: str
    project: str = ""  # frontmatter `project:` — used by aggregator to filter mismatched RoRs
    source: str = ""   # provenance ("file.md" or "process-blog/session-07.md @resist #3")
    inline_narrative: str = ""  # full paragraph when extracted from a tagged process blog
                                # (no field split possible). When set, renderer shows this
                                # block in place of the three structured fields.


@dataclass
class KeyDecision:
    record_number: int
    headline: str
    curation_source: str


@dataclass
class AIUseLog:
    interaction_count: int
    verification_count: int
    intervention_summary: str
    pattern_analysis: str
    five_questions_pass_rate: Optional[float]


@dataclass
class Reflection:
    kept: str
    revised: str
    rejected: str
    five_questions: dict[str, bool]
    learning: str
    temptation_moments: str


@dataclass
class Disclosure:
    form: str
    text: str


@dataclass(frozen=True)
class DecisionWalkthroughEntry:
    record_number: int
    narration: str


@dataclass
class Narrative:
    intro: str
    position_summary: str
    decision_walkthrough: list[DecisionWalkthroughEntry]
    reflection_summary: str
    closing: str
    user_approved: bool
    drafted_at: str
    # New narrative.md sections that were previously silently dropped:
    what_set_out_to_protect: Optional[str] = None
    defend_claims: list[str] = field(default_factory=list)
    disclosure_override: Optional[str] = None


@dataclass
class DefensePack:
    project_name: str
    context: str
    student_name: str
    scaffolding_level: str
    phase_at_export: str
    export_timestamp: str
    companion_version: str
    position_statement: Optional[PositionStatement]
    records_of_resistance: list[RecordOfResistance]
    key_decisions: list[KeyDecision]
    ai_use_log: Optional[AIUseLog]
    reflection: Optional[Reflection]
    disclosure: Optional[Disclosure]
    evolution_log_entries: list[str]
    narrative: Optional[Narrative]
    gaps: list[Gap]
    # Process tag counts — when the workspace uses the taught @resist / @default / @shift
    # convention in process blog files, the aggregator counts occurrences across the
    # corpus. These provide defensible quantitative evidence ("147 documented resistance
    # moments across 14 sessions") that complements the curated decisions.
    resist_count: int = 0
    default_count: int = 0
    shift_count: int = 0
    process_blog_sources: list[str] = field(default_factory=list)
    # Schema version of the pack. Bumped only on breaking shape changes (renames,
    # removals, type changes); additive fields stay at the same major.minor.
    # Consumers reading a pack.json should fall back gracefully when the field
    # is absent (treat as the default), but can assert on a major-version match
    # before relying on any field that wasn't present at 1.0.
    schema_version: str = "1.0"
