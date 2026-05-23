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
    """Render the curated Key Decisions as a sequence of declarative argument blocks.

    Each decision is its own visible article — not a collapsed details widget.
    The narration (the student's in-voice argument for why this moment matters)
    is the lead content. The underlying RoR record appears as collapsible
    evidence below. If no matching record was found (narrative references a
    record number that doesn't exist), the narration stands on its own.
    """
    if not pack.key_decisions:
        return "<p><em>No key decisions curated.</em></p>"

    total = len(pack.key_decisions)
    parts: list[str] = []
    for idx, kd in enumerate(pack.key_decisions, start=1):
        ror = next(
            (r for r in pack.records_of_resistance if r.record_number == kd.record_number),
            None,
        )
        # Find the narration text — the student's in-voice argument.
        narration = ""
        if pack.narrative:
            entry = next(
                (
                    e for e in pack.narrative.decision_walkthrough
                    if e["record_number"] == kd.record_number
                ),
                None,
            )
            if entry:
                narration = entry["narration"]

        # Headline: only show if it adds information beyond the narration.
        # When the parser auto-generates headline from the narration's first
        # line, showing both produces duplication. Skip headline if it's a
        # substring of the narration's first ~80 chars.
        headline = (kd.headline or "").strip().rstrip("…").strip()
        narration_lead = (narration or "").strip()[:100]
        show_headline = bool(headline) and headline not in narration_lead

        # Source attribution
        source_line = ""
        if ror and ror.source:
            source_line = (
                f'<p class="kd-source">From <code>{_esc(ror.source)}</code></p>'
            )

        # Evidence body (collapsible). Only render if there's actual content.
        evidence_block = ""
        if ror:
            structured_filled = any(
                s.strip() for s in (ror.ai_suggested, ror.why_rejected, ror.what_i_did_instead)
            )
            if structured_filled:
                evidence_inner = (
                    f'<h4>What AI suggested</h4><p>{_esc(ror.ai_suggested)}</p>'
                    f'<h4>Why I overruled it</h4><p>{_esc(ror.why_rejected)}</p>'
                    f'<h4>What I did instead</h4><p>{_esc(ror.what_i_did_instead)}</p>'
                )
            elif ror.inline_narrative.strip():
                evidence_inner = (
                    f'<div class="inline-resist"><pre class="block">'
                    f'{_esc(ror.inline_narrative)}</pre></div>'
                )
            else:
                evidence_inner = ""

            if evidence_inner:
                evidence_block = f"""
<details class="kd-evidence">
  <summary>The underlying record</summary>
  {evidence_inner}
</details>
"""

        # Build the article
        header_parts = [f'<p class="kd-num">Key decision {idx} of {total}</p>']
        if show_headline:
            header_parts.append(f'<h3 class="kd-headline">{_esc(headline)}</h3>')

        narration_block = ""
        if narration_lead:
            narration_block = f'<div class="kd-narration"><p>{_esc(narration)}</p></div>'

        # Presenter notes are kept available but only differ from narration
        # when the SKILL adds a separate cue. For now they mirror the narration
        # for the live-walkthrough mode, but hidden by default.
        presenter_block = ""
        if narration and any(
            cue in narration.lower() for cue in ("[note:", "[cue:", "[remember:")
        ):
            # Only emit a presenter-only block when the narration contains an
            # explicit cue marker — otherwise we'd be duplicating content.
            presenter_block = (
                f'<p class="presenter-notes"><strong>Speaker note</strong> '
                f'{_esc(narration)}</p>'
            )

        parts.append(f"""
<article class="key-decision" id="ror-{kd.record_number}">
  {''.join(header_parts)}
  {source_line}
  {narration_block}
  {presenter_block}
  {evidence_block}
</article>
""")
    return "\n".join(parts)


def _ror_body_html(ror) -> str:
    """Render the content of one Record of Resistance.

    A record may carry structured fields (canonical RoR file with three labeled
    sections) OR an inline narrative block (extracted from a @resist tag in a
    process blog). Show whichever is populated. Both can coexist when the
    structured fields are populated AND a narrative is preserved for context.
    """
    structured_filled = any(
        s.strip() for s in (ror.ai_suggested, ror.why_rejected, ror.what_i_did_instead)
    )
    parts: list[str] = []
    if structured_filled:
        parts.append(f"<h4>What AI suggested</h4><p>{_esc(ror.ai_suggested)}</p>")
        parts.append(f"<h4>Why I rejected/revised</h4><p>{_esc(ror.why_rejected)}</p>")
        parts.append(f"<h4>What I did instead</h4><p>{_esc(ror.what_i_did_instead)}</p>")
    if ror.inline_narrative:
        parts.append(
            f'<div class="inline-resist"><pre class="block">{_esc(ror.inline_narrative)}</pre></div>'
        )
    if not parts:
        parts.append("<p><em>(No content extracted.)</em></p>")
    return "\n".join(parts)


def _appendix_html(pack: DefensePack) -> str:
    """Render the full Records of Resistance appendix as a unified list.

    All RoRs — whether from dedicated `records-of-resistance/*.md` files or from
    inline `@resist` tags in process blog files — are the same kind of artifact.
    They're grouped by source file for navigability (some session blogs contain
    many @resist moments), but presentationally there's no formal-vs-inline
    distinction.
    """
    if not pack.records_of_resistance:
        return "<p><em>No Records of Resistance recorded.</em></p>"

    # Group by source file. RoRs without a source (legacy or test fixtures) get
    # bucketed under "(unknown source)".
    by_source: dict = {}
    for r in pack.records_of_resistance:
        src_file = r.source.split(" (@")[0] if " (@" in r.source else (r.source or "(unknown source)")
        by_source.setdefault(src_file, []).append(r)

    total = len(pack.records_of_resistance)
    parts: list[str] = [
        f'<p class="appendix-note">{total} Record(s) of Resistance across '
        f'{len(by_source)} source(s). Click any group to expand.</p>'
    ]

    # Sort sources so dedicated record-of-resistance files come first, then
    # process-blog files. Within a group, sort by record_number.
    def _source_key(src: str) -> tuple:
        is_process_blog = "process-blog" in src or "session-" in src
        return (is_process_blog, src)

    for src_file in sorted(by_source.keys(), key=_source_key):
        recs = sorted(by_source[src_file], key=lambda r: r.record_number)
        count_label = f"{len(recs)} record{'s' if len(recs) != 1 else ''}"
        parts.append(f"""
<details class="ror source-group">
  <summary><code>{_esc(src_file)}</code> — {count_label}</summary>
""")
        for ror in recs:
            date_str = f" · {_esc(ror.date)}" if ror.date else ""
            parts.append(f"""
<div class="ror-entry" id="ror-{ror.record_number}-full">
  <h4 class="ror-id">#{ror.record_number}{date_str}</h4>
  {_ror_body_html(ror)}
</div>
""")
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
