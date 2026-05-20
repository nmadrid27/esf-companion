"""HTML renderer for Defense Pack. Pure stdlib + string.Template."""
from __future__ import annotations
import html
from pathlib import Path
from string import Template
from .schema import DefensePack


_RENDER_DIR = Path(__file__).resolve().parents[1].parent / "render"


def _esc(s: str) -> str:
    return html.escape(s or "")


def _decisions_html(pack: DefensePack) -> str:
    if not pack.key_decisions:
        return "<p><em>No key decisions curated.</em></p>"
    parts = []
    for kd in pack.key_decisions:
        ror = next((r for r in pack.records_of_resistance if r.record_number == kd.record_number), None)
        if not ror:
            continue
        narration = ""
        if pack.narrative:
            entry = next((e for e in pack.narrative.decision_walkthrough if e["record_number"] == kd.record_number), None)
            if entry:
                narration = entry["narration"]
        parts.append(f"""
<details class="ror" data-key="true" id="ror-{ror.record_number}">
  <summary>#{ror.record_number} — {_esc(kd.headline)}</summary>
  <p class="presenter-notes"><strong>Speaker note:</strong> {_esc(narration)}</p>
  <h4>What AI suggested</h4>
  <p>{_esc(ror.ai_suggested)}</p>
  <h4>Why I overruled it</h4>
  <p>{_esc(ror.why_rejected)}</p>
  <h4>What I did instead</h4>
  <p>{_esc(ror.what_i_did_instead)}</p>
</details>
""")
    return "\n".join(parts)


def _appendix_html(pack: DefensePack) -> str:
    if not pack.records_of_resistance:
        return "<p><em>No Records of Resistance recorded.</em></p>"
    parts = []
    for ror in pack.records_of_resistance:
        parts.append(f"""
<details class="ror" id="ror-{ror.record_number}-full">
  <summary>#{ror.record_number} · {_esc(ror.date)}</summary>
  <h4>What AI suggested</h4><p>{_esc(ror.ai_suggested)}</p>
  <h4>Why I rejected/revised</h4><p>{_esc(ror.why_rejected)}</p>
  <h4>What I did instead</h4><p>{_esc(ror.what_i_did_instead)}</p>
</details>
""")
    return "\n".join(parts)


def _drift_block(pack: DefensePack) -> str:
    ps = pack.position_statement
    if not ps or not ps.drift_level:
        return ""
    return f"""
<div class="drift">
  <h3>Drift check</h3>
  <p><strong>Level:</strong> {_esc(ps.drift_level)}</p>
  <p><strong>What shifted:</strong> {_esc(ps.drift_what_shifted or '')}</p>
  <p><strong>User's decision:</strong> {'Yes' if ps.drift_was_user_decision else 'Not confirmed'}</p>
</div>
"""


def _gaps_block(pack: DefensePack) -> str:
    visible_gaps = [g for g in pack.gaps if g.severity.value != "info"]
    if not visible_gaps:
        return ""
    items = "".join(f"<li>{_esc(g.message)}</li>" for g in visible_gaps)
    return f'<aside class="gaps"><h3>Gaps in this pack</h3><ul>{items}</ul></aside>'


def render_html(pack: DefensePack) -> str:
    if not pack.narrative:
        raise ValueError("Cannot render HTML without an approved narrative.")
    template_str = (_RENDER_DIR / "template.html").read_text(encoding="utf-8")
    css = (_RENDER_DIR / "print.css").read_text(encoding="utf-8")
    ps = pack.position_statement
    return Template(template_str).safe_substitute(
        project_name=_esc(pack.project_name),
        context=_esc(pack.context),
        phase=_esc(pack.phase_at_export),
        timestamp=_esc(pack.export_timestamp),
        scaffolding_level=_esc(pack.scaffolding_level),
        companion_version=_esc(pack.companion_version),
        print_css=css,
        narrative_intro=_esc(pack.narrative.intro),
        ps_stance=_esc(ps.stance if ps else ""),
        ps_matters=_esc(ps.what_matters_most if ps else ""),
        ps_non_neg=_esc(ps.non_negotiables if ps else ""),
        drift_block=_drift_block(pack),
        decisions_html=_decisions_html(pack),
        reflection_summary=_esc(pack.narrative.reflection_summary),
        closing=_esc(pack.narrative.closing),
        disclosure_text=_esc(pack.disclosure.text if pack.disclosure else ""),
        appendix_html=_appendix_html(pack),
        gaps_block=_gaps_block(pack),
    )
