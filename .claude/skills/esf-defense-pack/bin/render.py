#!/usr/bin/env python3
"""CLI for the Defense Pack renderer.

Usage:
    render.py <pack.json> <narrative.md> --out-dir <dir>

Reads the aggregated pack.json, merges in the user-approved narrative.md content,
and emits defense-pack.html, defense-pack.pdf, defense-pack.md to <out-dir>.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import fields
from pathlib import Path
from typing import TypeVar, Type, Optional, Any, cast

T = TypeVar("T")

sys.path.insert(0, str(Path(__file__).parent))

from esf_pack.schema import (
    DefensePack, Narrative, PositionStatement, RecordOfResistance,
    KeyDecision, AIUseLog, Reflection, Disclosure, Gap, GapSeverity,
)
from esf_pack.render_html import render_html
from esf_pack.render_pdf import render_pdf_or_skip
from esf_pack.render_script import render_script


def _to_dataclass(cls: Type[T], data: Optional[dict]) -> Optional[T]:
    if data is None:
        return None
    if cls is DefensePack:
        # Use .get() with sensible defaults throughout so an older pack.json
        # missing a field (added in a later schema revision) doesn't crash with
        # an unhelpful KeyError. Required identity fields still default to "".
        return cast(T, DefensePack(
            project_name=data.get("project_name", ""),
            context=data.get("context", ""),
            student_name=data.get("student_name", ""),
            scaffolding_level=data.get("scaffolding_level", ""),
            phase_at_export=data.get("phase_at_export", ""),
            export_timestamp=data.get("export_timestamp", ""),
            companion_version=data.get("companion_version", ""),
            position_statement=_to_dataclass(PositionStatement, data.get("position_statement")),
            records_of_resistance=[
                r for r in (_to_dataclass(RecordOfResistance, x) for x in data.get("records_of_resistance", []))
                if r is not None
            ],
            key_decisions=[
                k for k in (_to_dataclass(KeyDecision, x) for x in data.get("key_decisions", []))
                if k is not None
            ],
            ai_use_log=_to_dataclass(AIUseLog, data.get("ai_use_log")),
            reflection=_to_dataclass(Reflection, data.get("reflection")),
            disclosure=_to_dataclass(Disclosure, data.get("disclosure")),
            evolution_log_entries=data.get("evolution_log_entries", []),
            narrative=_to_dataclass(Narrative, data.get("narrative")),
            gaps=[
                Gap(
                    artifact=g["artifact"],
                    severity=GapSeverity(g["severity"]) if isinstance(g["severity"], str) else g["severity"],
                    message=g["message"],
                )
                for g in data.get("gaps", [])
            ],
        ))
    field_names = {f.name for f in fields(cast(Any, cls))}
    return cast(T, cls(**{k: v for k, v in data.items() if k in field_names}))


_BLOCKQUOTE_PREFIX_RE = re.compile(r"^>\s?")


def _strip_blockquote_markers(text: str) -> str:
    """Strip leading '> ' from each line so blockquote markdown doesn't render literally.

    The narrative template instructs students to write content as `> ...`
    blockquotes. Without this, the renderer would emit literal '> Text' in HTML
    and PDF.

    Uses a regex (not str.lstrip) because lstrip is a character-set strip —
    `>>>nested` would collapse to `nested` and `> ` / `>>` would be
    indistinguishable. We only want one prefix level removed.
    """
    out_lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            out_lines.append(_BLOCKQUOTE_PREFIX_RE.sub("", line, count=1).rstrip())
        else:
            out_lines.append(line.rstrip())
    return "\n".join(out_lines).strip()


def _extract_numbered_items(text: str) -> list[str]:
    """Pull `1.` / `2.` / ... numbered-list items out of narrative prose."""
    items: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def _parse_narrative_md(text: str) -> Narrative:
    """Read the user's approved defense-narrative.md and turn it into a Narrative.

    Expected H2 sections (all optional except 'How I came in'):
      - 'Opening' — optional dedicated opening line; otherwise derived from 'How I came in'
      - 'How I came in' — position summary in student voice
      - 'What I set out to protect' — what mattered most + non-negotiables
      - 'The key decisions' — `### Decision #N` blocks with narration
      - 'How my position held' (or 'How my position held (or shifted)')
      - 'What I'd defend if asked' — numbered claims
      - 'Disclosure' — overrides auto-generated disclosure if present
    """
    sections = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL):
        sections[m.group(1).strip()] = m.group(2).strip()

    decision_walkthrough: list[dict] = []
    decisions_text = sections.get("The key decisions", "")
    for m in re.finditer(r"###\s*Decision\s*#(\d+).*?\n(.*?)(?=^### |\Z)", decisions_text, re.MULTILINE | re.DOTALL):
        decision_walkthrough.append({
            "record_number": int(m.group(1)),
            "narration": _strip_blockquote_markers(m.group(2)),
        })

    came_in = _strip_blockquote_markers(sections.get("How I came in", ""))
    held = _strip_blockquote_markers(
        sections.get("How my position held", "")
        or sections.get("How my position held (or shifted)", "")
    )
    protect = _strip_blockquote_markers(sections.get("What I set out to protect", "")) or None
    closing_text = sections.get("What I'd defend if asked", "")
    defend_claims = _extract_numbered_items(closing_text)
    disclosure_text = _strip_blockquote_markers(sections.get("Disclosure", "")) or None

    # Opening: prefer an explicit '## Opening' section. Otherwise leave intro empty
    # rather than duplicate the first sentence of 'How I came in' (which the previous
    # implementation did, producing audible duplication in the recording script).
    explicit_opening = _strip_blockquote_markers(sections.get("Opening", ""))
    intro = explicit_opening  # may be empty; renderer/template handle that gracefully

    return Narrative(
        intro=intro,
        position_summary=came_in,
        decision_walkthrough=decision_walkthrough,
        reflection_summary=held,
        closing=_strip_blockquote_markers(closing_text),
        user_approved=True,
        drafted_at="",
        what_set_out_to_protect=protect,
        defend_claims=defend_claims,
        disclosure_override=disclosure_text,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_json", type=Path)
    ap.add_argument("narrative_md", type=Path)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()

    data = json.loads(args.pack_json.read_text(encoding="utf-8"))
    pack = _to_dataclass(DefensePack, data)
    assert pack is not None, "pack.json should never produce None"
    pack.narrative = _parse_narrative_md(args.narrative_md.read_text(encoding="utf-8"))

    # Fallback: if the SKILL didn't persist curated key_decisions to pack.json but
    # the user's narrative walks through specific records, materialize key_decisions
    # from the walkthrough so HTML and recording-script renderers stay in sync.
    if not pack.key_decisions and pack.narrative and pack.narrative.decision_walkthrough:
        for entry in pack.narrative.decision_walkthrough:
            rec_num = entry["record_number"]
            ror = next((r for r in pack.records_of_resistance if r.record_number == rec_num), None)
            if not ror:
                continue
            # Headline: first non-empty line of narration, truncated.
            first_line = next((ln.strip() for ln in entry["narration"].splitlines() if ln.strip()), "")
            headline = first_line[:80] + ("…" if len(first_line) > 80 else "")
            pack.key_decisions.append(KeyDecision(
                record_number=rec_num,
                headline=headline or f"Decision #{rec_num}",
                curation_source="narrative_inferred",
            ))

    # Override auto-disclosure with the user's explicit disclosure if they wrote one.
    if pack.narrative and pack.narrative.disclosure_override:
        pack.disclosure = Disclosure(form="user", text=pack.narrative.disclosure_override)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    html_out = args.out_dir / "defense-pack.html"
    html_out.write_text(render_html(pack), encoding="utf-8")

    script_out = args.out_dir / "defense-pack.md"
    script_out.write_text(render_script(pack), encoding="utf-8")

    pdf_bytes, msg = render_pdf_or_skip(pack)
    if pdf_bytes is not None:
        (args.out_dir / "defense-pack.pdf").write_bytes(pdf_bytes)
        print(f"Wrote: {html_out}, {args.out_dir / 'defense-pack.pdf'}, {script_out}")
    else:
        print(f"Wrote: {html_out}, {script_out}")
        print(f"PDF skipped: {msg}")


if __name__ == "__main__":
    main()
