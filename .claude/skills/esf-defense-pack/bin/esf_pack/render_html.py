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
    """Render the full Records of Resistance appendix.

    Handles two flavors:
      - Structured RoRs (canonical format with ai_suggested / why_rejected /
        what_i_did_instead H2 sections) — rendered as three labeled fields.
      - Inline RoRs (extracted from @resist tags in process blogs) — rendered
        as a single content block with source attribution. No empty field labels.

    When the pack has many inline RoRs (Lily's case: 80+), they're grouped by
    source file and rendered collapsed by default; faculty can drill in if they
    want to read the full narrative.
    """
    if not pack.records_of_resistance:
        return "<p><em>No Records of Resistance recorded.</em></p>"

    # Split records by type
    structured = [r for r in pack.records_of_resistance if not r.inline_narrative]
    inline = [r for r in pack.records_of_resistance if r.inline_narrative]

    parts: list[str] = []

    if structured:
        parts.append('<h3 class="appendix-subhead">Formal Records of Resistance</h3>')
        for ror in structured:
            parts.append(f"""
<details class="ror" id="ror-{ror.record_number}-full">
  <summary>#{ror.record_number} · {_esc(ror.date)}</summary>
  <h4>What AI suggested</h4><p>{_esc(ror.ai_suggested)}</p>
  <h4>Why I rejected/revised</h4><p>{_esc(ror.why_rejected)}</p>
  <h4>What I did instead</h4><p>{_esc(ror.what_i_did_instead)}</p>
</details>
""")

    if inline:
        # Group inline RoRs by source file
        by_source: dict = {}
        for r in inline:
            # source is "<file> (@resist #N)" — group by the file portion
            src_file = r.source.split(" (@")[0] if " (@" in r.source else r.source
            by_source.setdefault(src_file, []).append(r)

        parts.append(f'<h3 class="appendix-subhead">Inline @resist Records ({len(inline)} from {len(by_source)} sources)</h3>')
        parts.append(
            '<p class="appendix-note"><em>These are <code>@resist</code>-tagged moments '
            'extracted from the student\'s process blog. Each block is the surrounding '
            'paragraph from the source file.</em></p>'
        )
        for src_file, recs in sorted(by_source.items()):
            parts.append(f"""
<details class="ror inline-group">
  <summary><code>{_esc(src_file)}</code> — {len(recs)} moment(s)</summary>
""")
            for ror in recs:
                # Show inline narrative with light markdown handling — convert blank
                # lines to paragraph breaks, keep blockquote/list markers visible.
                escaped_block = _esc(ror.inline_narrative)
                parts.append(
                    f'<div class="inline-resist"><pre class="block">{escaped_block}</pre></div>'
                )
            parts.append("</details>\n")

    return "\n".join(parts)


def _process_metrics_block(pack: DefensePack) -> str:
    """Render @resist / @default / @shift counts when a process blog was scanned.

    These provide quantitative evidence of disciplined AI use across the work —
    "92 documented resistance moments, 31 default acceptances, 16 shifts across
    19 session blogs" is itself a defensible artifact.
    """
    if not pack.process_blog_sources:
        return ""
    return f"""
<aside class="process-metrics">
  <h3>Process tracking</h3>
  <div class="metrics-grid">
    <div class="metric"><span class="metric-num">{pack.resist_count}</span><span class="metric-label">@resist moments</span></div>
    <div class="metric"><span class="metric-num">{pack.default_count}</span><span class="metric-label">@default acceptances</span></div>
    <div class="metric"><span class="metric-num">{pack.shift_count}</span><span class="metric-label">@shift redirects</span></div>
    <div class="metric"><span class="metric-num">{len(pack.process_blog_sources)}</span><span class="metric-label">session blogs documented</span></div>
  </div>
  <p class="metrics-note"><em>Tagged inline using the taught @resist / @default / @shift convention. Full inline records appear in the appendix.</em></p>
</aside>
"""


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
    """Render warning + hard_stop gaps with severity-specific visual treatment.

    Info-level gaps are not surfaced (they describe optional artifacts).
    Hard-stop gaps render with stronger emphasis than warnings.
    """
    visible_gaps = [g for g in pack.gaps if g.severity.value != "info"]
    if not visible_gaps:
        return ""
    items = "".join(
        f'<div class="gap {_esc(g.severity.value)}"><strong>{_esc(g.severity.value.replace("_", " ").title())}:</strong> {_esc(g.message)}</div>'
        for g in visible_gaps
    )
    return f'<aside class="gaps" role="note" aria-label="Gaps in this defense pack"><h3>Gaps in this pack</h3>{items}</aside>'


def _protect_block(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.what_set_out_to_protect:
        return ""
    return f'<div class="protect"><h3>What I set out to protect</h3><p>{_esc(pack.narrative.what_set_out_to_protect)}</p></div>'


def _intro_section(pack: DefensePack) -> str:
    """Render the Opening section only if the narrative provided one.

    Previously the renderer always emitted an Opening section using the first
    line of "How I came in", which duplicated content in the script. Now Opening
    is skipped entirely if the narrative.md doesn't include a dedicated `## Opening`.
    """
    if not pack.narrative or not pack.narrative.intro:
        return ""
    return f'<section id="intro"><h2>Opening</h2><p>{_esc(pack.narrative.intro)}</p></section>'


def _toc_intro_link(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.intro:
        return ""
    return '<a href="#intro">Opening</a>'


def _closing_html(pack: DefensePack) -> str:
    """Render 'What I'd defend if asked' as an <ol> when numbered claims exist,
    falling back to the raw prose otherwise.
    """
    if pack.narrative and pack.narrative.defend_claims:
        items = "".join(f"<li>{_esc(c)}</li>" for c in pack.narrative.defend_claims)
        return f'<ol class="defend-list">{items}</ol>'
    return f'<p>{_esc(pack.narrative.closing if pack.narrative else "")}</p>'


def _reflection_html(pack: DefensePack) -> str:
    """Reflection summary, preserving paragraph breaks from the narrative."""
    if not pack.narrative or not pack.narrative.reflection_summary:
        return "<p><em>No reflection summary provided.</em></p>"
    paragraphs = [p.strip() for p in pack.narrative.reflection_summary.split("\n\n") if p.strip()]
    return "\n".join(f"<p>{_esc(p)}</p>" for p in paragraphs)


def render_html(pack: DefensePack) -> str:
    if not pack.narrative:
        raise ValueError("Cannot render HTML without an approved narrative.")
    template_str = (_RENDER_DIR / "template.html").read_text(encoding="utf-8")
    css = (_RENDER_DIR / "print.css").read_text(encoding="utf-8")
    ps = pack.position_statement
    timestamp = _esc(pack.export_timestamp) or "[date unavailable]"
    # Use substitute (not safe_substitute) so a missing template key raises a
    # clear KeyError at render time. safe_substitute leaves literal "$placeholder"
    # in the output, which would ship as visible junk to a faculty member.
    return Template(template_str).substitute(
        project_name=_esc(pack.project_name),
        student_name=_esc(pack.student_name),
        context=_esc(pack.context),
        phase=_esc(pack.phase_at_export),
        timestamp=timestamp,
        scaffolding_level=_esc(pack.scaffolding_level),
        companion_version=_esc(pack.companion_version),
        print_css=css,
        intro_section=_intro_section(pack),
        toc_intro_link=_toc_intro_link(pack),
        ps_stance=_esc(ps.stance if ps else ""),
        ps_matters=_esc(ps.what_matters_most if ps else ""),
        ps_non_neg=_esc(ps.non_negotiables if ps else ""),
        protect_block=_protect_block(pack),
        drift_block=_drift_block(pack),
        decisions_html=_decisions_html(pack),
        process_metrics_block=_process_metrics_block(pack),
        reflection_html=_reflection_html(pack),
        closing_html=_closing_html(pack),
        disclosure_text=_esc(pack.disclosure.text if pack.disclosure else ""),
        appendix_html=_appendix_html(pack),
        gaps_block=_gaps_block(pack),
    )
