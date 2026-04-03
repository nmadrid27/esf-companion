from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Phase(str, Enum):
    INQUIRE = "Inquire"
    POSITION = "Position"
    EXPLORE = "Explore"
    MAKE = "Make"
    REFLECT = "Reflect"


class ScaffoldingLevel(str, Enum):
    GUIDED = "Guided"
    SUPPORTED = "Supported"
    INDEPENDENT = "Independent"


@dataclass
class PositionStatement:
    stance: str
    matters_most: str
    non_negotiable: str
    version: int = 1
    confirmed: bool = False

    def to_text(self) -> str:
        return (
            f"**What I am making and why:** {self.stance}\n\n"
            f"**What matters most to me:** {self.matters_most}\n\n"
            f"**What I will not compromise on:** {self.non_negotiable}"
        )


@dataclass
class EsfState:
    user_name: str
    user_role: str          # "student", "educator", "professional"
    discipline: str
    context_code: str
    context_name: str
    project_name: str
    phase: Phase
    scaffolding_level: ScaffoldingLevel
    position_statement: Optional[PositionStatement] = None
    ror_count: int = 0
    consecutive_unmodified: int = 0   # agency drift counter
    ror_minimum: int = 2
    position_statement_required: bool = True
    five_questions_required: bool = True
    allow_silent_mode: bool = True
    silent_mode: bool = False

    def to_injection_text(self) -> str:
        ps_text = (
            self.position_statement.to_text()
            if self.position_statement and self.position_statement.confirmed
            else "[No confirmed Position Statement yet]"
        )
        return (
            f"## Current Session State\n\n"
            f"**User:** {self.user_name} ({self.user_role}, {self.discipline})\n"
            f"**Context:** {self.context_name} ({self.context_code})\n"
            f"**Project:** {self.project_name}\n"
            f"**Phase:** {self.phase.value}\n"
            f"**Scaffolding Level:** {self.scaffolding_level.value}\n"
            f"**Silent Mode:** {'on' if self.silent_mode else 'off'}\n\n"
            f"**Brief Requirements:**\n"
            f"- Position Statement: {'required' if self.position_statement_required else 'optional'}\n"
            f"- Five Questions: {'required' if self.five_questions_required else 'optional'}\n"
            f"- Records of Resistance minimum: {self.ror_minimum}\n"
            f"- RoR documented this project: {self.ror_count}\n\n"
            f"**Agency Drift Counter:** {self.consecutive_unmodified} consecutive "
            f"unmodified AI acceptances\n\n"
            f"**Current Position Statement:**\n{ps_text}"
        )
