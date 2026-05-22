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


@dataclass
class Narrative:
    intro: str
    position_summary: str
    # {record_number, narration} dicts in this build; dedicated dataclass deferred to a later task.
    decision_walkthrough: list[dict]
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
