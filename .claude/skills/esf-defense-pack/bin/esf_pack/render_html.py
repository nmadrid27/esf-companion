"""HTML renderer for Defense Pack. Pure stdlib + string.Template."""
from __future__ import annotations
import html
import re
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
                    if e.record_number == kd.record_number
                ),
                None,
            )
            if entry:
                narration = entry.narration

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
            narration_block = f'<div class="kd-narration">{_prose_paragraphs_html(narration, line_breaks=True)}</div>'

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


def _is_inline_record(ror) -> bool:
    """Whether the record came from a @resist tag in a process blog (vs. a
    dedicated records-of-resistance/*.md file)."""
    if ror.inline_narrative:
        return True
    src = (ror.source or "").lower()
    return "process-blog" in src or "session-" in src


def _record_title_from_content(ror) -> str:
    """Derive a short title (the resistance decision) from the record's content.

    For structured records, prefer the first line of why_rejected (the
    reasoning), falling back to ai_suggested.
    For inline records, take the first non-bullet, non-heading line of the
    narrative as the title.
    """
    # Structured: first meaningful line of why_rejected or ai_suggested
    if (ror.why_rejected or "").strip():
        first = next((ln.strip() for ln in ror.why_rejected.splitlines() if ln.strip()), "")
        if first:
            return first[:140].rstrip(",;:.") + ("…" if len(first) > 140 else "")
    if (ror.ai_suggested or "").strip():
        first = next((ln.strip() for ln in ror.ai_suggested.splitlines() if ln.strip()), "")
        if first:
            return first[:140].rstrip(",;:.") + ("…" if len(first) > 140 else "")
    # Inline: scan for first prose line, skipping markdown headings and bullet markers
    if ror.inline_narrative:
        for line in ror.inline_narrative.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("---"):
                continue
            cleaned = re.sub(r"^[-*]\s*\**", "", stripped)
            cleaned = re.sub(r"\*\*", "", cleaned)
            cleaned = re.sub(r"^@\w+\b\s*[—–-]?\s*", "", cleaned)
            cleaned = cleaned.strip()
            if cleaned:
                return cleaned[:140] + ("…" if len(cleaned) > 140 else "")
    return f"Record #{ror.record_number}"


def _record_html(ror) -> str:
    """Render one Record of Resistance as a full-width featured block.

    Header: RoR N · date · @resist · (milestone if available)
    Title: short headline of the decision
    Body: 'What AI suggested' / 'What I did instead' / 'Why' if structured;
          inline narrative block otherwise.
    Source: file path attribution at the bottom.
    """
    # Header line
    header_parts = [f'<span class="ror-num">RoR {ror.record_number}</span>']
    if ror.date:
        header_parts.append(f'<span class="ror-date">{_esc(ror.date)}</span>')
    header_parts.append('<span class="tag">@resist</span>')
    # Join with explicit dot-separators in the markup
    header_inner = ' <span aria-hidden="true">·</span> '.join(header_parts)

    title = _record_title_from_content(ror)

    structured_filled = any(
        s.strip() for s in (ror.ai_suggested, ror.why_rejected, ror.what_i_did_instead)
    )
    body_parts: list[str] = []
    if structured_filled:
        if ror.ai_suggested.strip():
            body_parts.append('<p class="field-label">What AI suggested</p>')
            body_parts.append(f'<blockquote class="suggested">{_esc(ror.ai_suggested)}</blockquote>')
        if ror.what_i_did_instead.strip():
            body_parts.append('<p class="field-label">What I did instead</p>')
            body_parts.append(f'<p>{_esc(ror.what_i_did_instead)}</p>')
        if ror.why_rejected.strip():
            body_parts.append('<p class="field-label">Why</p>')
            body_parts.append(f'<p>{_esc(ror.why_rejected)}</p>')
    elif ror.inline_narrative.strip():
        body_parts.append(f'<pre class="inline-block">{_esc(ror.inline_narrative)}</pre>')
    else:
        body_parts.append("<p><em>(No content extracted.)</em></p>")

    source_html = ""
    if ror.source:
        # Strip the "@resist #N" suffix when present — the header already says @resist.
        clean_source = ror.source.split(" (@")[0] if " (@" in ror.source else ror.source
        source_html = f'<p class="source-line">Source: <code>{_esc(clean_source)}</code></p>'

    return f"""
<article class="record" id="ror-{ror.record_number}">
  <div class="record-header">{header_inner}</div>
  <h3 class="record-title">{_esc(title)}</h3>
  {''.join(body_parts)}
  {source_html}
</article>
"""


def _records_html(pack: DefensePack) -> str:
    """Render the Records of Resistance section — formal records, sequential.

    Only the dedicated records-of-resistance/*.md files get featured here.
    Inline @resist tags from process blogs are rendered in the timeline section
    (and would overwhelm this section at typical real-student volumes).
    """
    if not pack.records_of_resistance:
        return "<p><em>No Records of Resistance recorded for this project.</em></p>"

    formal = [r for r in pack.records_of_resistance if not _is_inline_record(r)]
    if not formal:
        return (
            '<p class="section-intro">No discrete Record of Resistance files in '
            'this project. See the Process Blog Timeline below for individual '
            '<code>@resist</code> moments tagged inline.</p>'
        )

    formal.sort(key=lambda r: r.record_number)
    return "\n".join(_record_html(r) for r in formal)


def _timeline_section(pack: DefensePack) -> str:
    """Render the Process Blog Timeline as a list of session-row cards.

    Each row shows: session ID, brief title (from filename), tag counts, and
    expands to reveal the individual @resist records pulled from that session.

    Returns empty string when no process-blog files were scanned (in which case
    the template's $timeline_section placeholder produces no section).
    """
    if not pack.process_blog_sources:
        return ""

    inline = [r for r in pack.records_of_resistance if _is_inline_record(r)]
    if not inline and pack.resist_count == 0:
        return ""

    # Group inline records by source file
    by_source: dict = {}
    for r in inline:
        src_file = r.source.split(" (@")[0] if " (@" in r.source else (r.source or "(unknown)")
        by_source.setdefault(src_file, []).append(r)

    # Per-session tag counts. We have whole-pack totals (resist_count, default_count,
    # shift_count) but not per-session breakdowns. Show resist count per session
    # (derived from records found); default/shift are pack-wide.
    rows: list[str] = []
    for src_file in sorted(by_source.keys()):
        records = sorted(by_source[src_file], key=lambda r: r.record_number)
        # Derive session ID from filename: "session-03.md" → "Session 03"
        basename = src_file.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        m = re.search(r"session[-_ ]?(\d+)", basename, re.IGNORECASE)
        session_id = f"Session {m.group(1)}" if m else basename
        # Tag counts for this session
        resist_n = len(records)
        tag_counts = (
            f'<span class="resist">@resist ×{resist_n}</span>'
        )
        # Title: just show file path or first record's title
        title = records[0] and _record_title_from_content(records[0]) or basename

        records_html = "\n".join(_record_html(r) for r in records)

        rows.append(f"""
<details class="session-row">
  <summary>
    <span class="session-id">{_esc(session_id)}</span>
    <span class="session-title">{_esc(title)}</span>
    <span class="tag-counts">{tag_counts}</span>
  </summary>
  <div class="session-records">
    {records_html}
  </div>
</details>
""")

    return f"""
<section id="timeline">
  <p class="section-eyebrow">§ 04 · Process blog timeline</p>
  <h2>Inline @resist moments by session</h2>
  <p class="section-intro">Each session in the process blog is below. Tag counts show resistance moments per session; expand a row to read the records.</p>
  <div class="timeline">
    {''.join(rows)}
  </div>
</section>
"""


def _section_cards(pack: DefensePack) -> str:
    """Section-card navigation near the top of the pack.

    Equal-weight scannable destinations (process-book aesthetic) rather than a
    flat inline TOC. Cards omit themselves when their section is empty.
    """
    formal_count = sum(1 for r in pack.records_of_resistance if not _is_inline_record(r))
    inline_count = sum(1 for r in pack.records_of_resistance if _is_inline_record(r))
    cards: list[tuple[str, str, str, str]] = []
    # (eyebrow, title, meta, anchor)
    cards.append(("§ 01", "Position", "Stance · what matters · non-negotiables", "#position"))
    if pack.key_decisions:
        kd_n = len(pack.key_decisions)
        cards.append(("§ 02", "Key decisions", f"{kd_n} curated decision{'s' if kd_n != 1 else ''}", "#decisions"))
    if formal_count:
        cards.append((
            "§ 03",
            "Records of Resistance",
            f"{formal_count} formal record{'s' if formal_count != 1 else ''}",
            "#records",
        ))
    if pack.process_blog_sources:
        cards.append((
            "§ 04",
            "Process blog timeline",
            f"{inline_count} @resist · {len(pack.process_blog_sources)} sessions",
            "#timeline",
        ))
    cards.append(("§ 05", "Reflection", "How the position held", "#reflection"))
    cards.append(("§ 06", "Defense", "What I would defend", "#closing"))
    cards.append(("§ 07", "Disclosure", "AI collaboration statement", "#disclosure"))
    return "\n".join(
        f'<a href="{anchor}"><span class="card-eyebrow">{_esc(eyebrow)}</span>'
        f'<span class="card-title">{_esc(title)}</span>'
        f'<span class="card-meta">{_esc(meta)}</span></a>'
        for eyebrow, title, meta, anchor in cards
    )


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


def _prose_paragraphs_html(text: str, line_breaks: bool = False) -> str:
    """Render free-text prose as one <p> per blank-line-separated paragraph.

    With line_breaks=True, single newlines inside a paragraph become <br> so a
    multi-line field keeps its structure in HTML (matching the recording-script
    .md). Without it, paragraphs are emitted the way _reflection_html always has.
    Returns "" for empty input.
    """
    paragraphs = [p.strip() for p in (text or "").split("\n\n") if p.strip()]
    if line_breaks:
        return "\n".join(
            "<p>" + "<br>".join(_esc(line) for line in p.split("\n")) + "</p>"
            for p in paragraphs
        )
    return "\n".join(f"<p>{_esc(p)}</p>" for p in paragraphs)


def _protect_block(pack: DefensePack) -> str:
    if not pack.narrative or not pack.narrative.what_set_out_to_protect:
        return ""
    return f'<div class="protect"><h3>What I set out to protect</h3>{_prose_paragraphs_html(pack.narrative.what_set_out_to_protect)}</div>'


def _intro_section(pack: DefensePack) -> str:
    """Render the Opening section only if the narrative provided one.

    Previously the renderer always emitted an Opening section using the first
    line of "How I came in", which duplicated content in the script. Now Opening
    is skipped entirely if the narrative.md doesn't include a dedicated `## Opening`.
    """
    if not pack.narrative or not pack.narrative.intro:
        return ""
    return f'<section id="intro"><h2>Opening</h2>{_prose_paragraphs_html(pack.narrative.intro)}</section>'


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
    return _prose_paragraphs_html(pack.narrative.closing if pack.narrative else "")


def _reflection_html(pack: DefensePack) -> str:
    """Reflection summary, preserving paragraph breaks from the narrative."""
    if not pack.narrative or not pack.narrative.reflection_summary:
        return "<p><em>No reflection summary provided.</em></p>"
    return _prose_paragraphs_html(pack.narrative.reflection_summary)


def render_html(pack: DefensePack) -> str:
    if not pack.narrative:
        raise ValueError("Cannot render HTML without an approved narrative.")
    template_str = (_RENDER_DIR / "template.html").read_text(encoding="utf-8")
    css = (_RENDER_DIR / "print.css").read_text(encoding="utf-8")
    ps = pack.position_statement
    timestamp = _esc(pack.export_timestamp) or "[date unavailable]"
    # Truncate scaffolding level for cover display — real students sometimes
    # write multi-clause descriptions ("Prototype iteration — Homepage + 2
    # functional tests built (Bilateral Coordination, Reaction Time)") that
    # overflow the cover meta line. Keep first clause; full text remains in
    # pack.json for traceability.
    scaffolding = pack.scaffolding_level or ""
    if len(scaffolding) > 60:
        scaffolding = scaffolding.split("—")[0].split(":")[0].strip()[:60].rstrip(", ")
    # Use substitute (not safe_substitute) so a missing template key raises a
    # clear KeyError at render time. safe_substitute leaves literal "$placeholder"
    # in the output, which would ship as visible junk to a faculty member.
    return Template(template_str).substitute(
        project_name=_esc(pack.project_name),
        student_name=_esc(pack.student_name),
        context=_esc(pack.context),
        phase=_esc(pack.phase_at_export),
        timestamp=timestamp,
        scaffolding_level=_esc(scaffolding),
        companion_version=_esc(pack.companion_version),
        print_css=css,
        intro_section=_intro_section(pack),
        toc_intro_link=_toc_intro_link(pack),
        ps_stance=_esc(ps.stance if ps else ""),
        ps_matters=_esc(ps.what_matters_most if ps else ""),
        ps_non_neg=_esc(ps.non_negotiables if ps else ""),
        protect_block=_protect_block(pack),
        drift_block=_drift_block(pack),
        section_cards=_section_cards(pack),
        decisions_html=_decisions_html(pack),
        process_metrics_block=_process_metrics_block(pack),
        records_html=_records_html(pack),
        timeline_section=_timeline_section(pack),
        reflection_html=_reflection_html(pack),
        closing_html=_closing_html(pack),
        disclosure_text=_esc(pack.disclosure.text if pack.disclosure else ""),
        gaps_block=_gaps_block(pack),
    )
