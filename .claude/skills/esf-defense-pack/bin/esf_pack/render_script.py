"""Recording-script renderer with timing cues.

The script is what the student reads aloud during a defense or records into a
video. It leads with the student's own narration; the raw RoR fields appear as
a brief reference line only, not as a competing summary. The full RoR detail
lives in the HTML/PDF appendix — the script doesn't reprint it.
"""
from __future__ import annotations
from pathlib import Path
from string import Template
from .schema import DefensePack


_TEMPLATE_PATH = Path(__file__).resolve().parents[1].parent / "render" / "script.md.tmpl"


def _walkthrough_text(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.decision_walkthrough:
        return "*(No key decisions captured — defense rests on Position Statement and Reflection only.)*"
    chunks = []
    for entry in pack.narrative.decision_walkthrough:
        rec_num = entry["record_number"]
        ror = next((r for r in pack.records_of_resistance if r.record_number == rec_num), None)
        narration = entry.get("narration", "").strip()
        # Lead with the student's narration. Add a short reference line afterward
        # pointing to the appendix entry, without restating the RoR's three fields
        # (the appendix has them in full; reciting them aloud duplicates).
        ref = ""
        if ror:
            # Build the reference line conditionally — empty date parens look broken.
            date_str = f" ({ror.date})" if ror.date else ""
            source_str = f" from `{ror.source}`" if ror.source else ""
            ref = f"\n\n> *Reference: Record #{rec_num}{date_str}{source_str}. Full detail in the appendix.*"
        chunks.append(f"### Decision #{rec_num}\n\n{narration}{ref}\n")
    return "\n".join(chunks)


def _opening_block(pack: DefensePack) -> str:
    """Render the Opening section only if the narrative provided an explicit intro.

    Previously the script always emitted an Opening section using the first line
    of "How I came in", which caused audible duplication ("...one." → next
    paragraph: "...one.") when read aloud.
    """
    if not pack.narrative or not pack.narrative.intro:
        return "*(Opening omitted: jump straight into 'How I came in'.)*"
    return f"## Opening `[~1 min]`\n\n{pack.narrative.intro}"


def _protect_block(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.what_set_out_to_protect:
        return ""
    return f"### What I set out to protect\n\n{pack.narrative.what_set_out_to_protect}\n"


def _disclosure_block(pack: DefensePack) -> str:
    if pack.narrative and pack.narrative.disclosure_override:
        return pack.narrative.disclosure_override
    if pack.disclosure and pack.disclosure.text:
        return pack.disclosure.text
    return "*(No disclosure provided.)*"


def render_script(pack: DefensePack) -> str:
    if not pack.narrative:
        raise ValueError("Cannot render script without an approved narrative.")
    tmpl = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    # substitute (not safe_substitute) so missing keys raise loudly.
    return tmpl.substitute(
        project_name=pack.project_name,
        student_name=pack.student_name or "[student name not set]",
        opening_block=_opening_block(pack),
        position_summary=pack.narrative.position_summary,
        protect_block=_protect_block(pack),
        decision_walkthrough=_walkthrough_text(pack),
        reflection_summary=pack.narrative.reflection_summary,
        closing=pack.narrative.closing,
        disclosure=_disclosure_block(pack),
        timestamp=pack.export_timestamp or "[date unavailable]",
    )
