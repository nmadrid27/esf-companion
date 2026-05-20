"""Recording-script renderer with timing cues."""
from __future__ import annotations
from pathlib import Path
from string import Template
from .schema import DefensePack


_TEMPLATE_PATH = Path(__file__).resolve().parents[1].parent / "render" / "script.md.tmpl"


def _walkthrough_text(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.decision_walkthrough:
        return "(No key decisions captured.)"
    chunks = []
    for entry in pack.narrative.decision_walkthrough:
        rec_num = entry["record_number"]
        ror = next((r for r in pack.records_of_resistance if r.record_number == rec_num), None)
        if ror:
            chunks.append(
                f"**Decision #{rec_num} ({ror.date}).** "
                f"AI suggested: {ror.ai_suggested} "
                f"I overruled because: {ror.why_rejected} "
                f"What I did: {ror.what_i_did_instead}\n\n"
                f"{entry['narration']}\n"
            )
    return "\n".join(chunks)


def render_script(pack: DefensePack) -> str:
    if not pack.narrative:
        raise ValueError("Cannot render script without an approved narrative.")
    tmpl = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    return tmpl.safe_substitute(
        project_name=pack.project_name,
        narrative_intro=pack.narrative.intro,
        position_summary=pack.narrative.position_summary,
        decision_walkthrough=_walkthrough_text(pack),
        reflection_summary=pack.narrative.reflection_summary,
        closing=pack.narrative.closing,
        timestamp=pack.export_timestamp,
    )
