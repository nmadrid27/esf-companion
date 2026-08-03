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
from dataclasses import MISSING, fields
from pathlib import Path
from typing import TypeVar, Type, Optional, Any, cast

T = TypeVar("T")

sys.path.insert(0, str(Path(__file__).parent))

from esf_pack.schema import (
    DefensePack, Narrative, PositionStatement, RecordOfResistance,
    KeyDecision, AIUseLog, Reflection, Disclosure, Gap, GapSeverity,
    DecisionWalkthroughEntry,
)
from esf_pack.gaps import has_hard_stop
from esf_pack.parsers import _normalize
from esf_pack.render_html import render_html
from esf_pack.render_pdf import render_pdf_or_skip
from esf_pack.render_script import render_script


# Nested dataclass fields of DefensePack, by field name. Everything not listed
# here (and not `gaps`) is a plain value that round-trips as-is.
_PACK_NESTED: dict[str, type] = {
    "position_statement": PositionStatement,
    "ai_use_log": AIUseLog,
    "reflection": Reflection,
    "disclosure": Disclosure,
    "narrative": Narrative,
}
_PACK_NESTED_LISTS: dict[str, type] = {
    "records_of_resistance": RecordOfResistance,
    "key_decisions": KeyDecision,
}


def _to_dataclass(cls: Type[T], data: Optional[dict]) -> Optional[T]:
    if data is None:
        return None
    if cls is Narrative:
        # Convert decision_walkthrough dicts → DecisionWalkthroughEntry on round-trip
        # so older pack.json files (which serialize the entries as plain dicts) read
        # back into the typed dataclass without breaking. asdict() of a
        # DecisionWalkthroughEntry produces the same `{record_number, narration}`
        # shape, so the wire format stays compatible.
        field_names = {f.name for f in fields(cast(Any, Narrative))}
        kwargs = {k: v for k, v in data.items() if k in field_names}
        raw_walkthrough = kwargs.get("decision_walkthrough", []) or []
        kwargs["decision_walkthrough"] = [
            entry if isinstance(entry, DecisionWalkthroughEntry)
            else DecisionWalkthroughEntry(
                record_number=entry["record_number"],
                narration=entry["narration"],
            )
            for entry in raw_walkthrough
        ]
        return cast(T, Narrative(**kwargs))
    if cls is DefensePack:
        # Driven off fields(DefensePack) rather than a hand-written argument list:
        # an enumerated list silently drops any field added to the schema later
        # (resist_count and friends were lost this way, rendering as 0). Only the
        # nested types need naming; everything else round-trips by name.
        #
        # A field absent from an older pack.json falls back to its dataclass
        # default, or to "" for the required identity scalars that have none, so
        # older packs still load instead of raising KeyError/TypeError.
        kwargs: dict[str, Any] = {}
        for f in fields(cast(Any, DefensePack)):
            if f.name in _PACK_NESTED:
                kwargs[f.name] = _to_dataclass(_PACK_NESTED[f.name], data.get(f.name))
            elif f.name in _PACK_NESTED_LISTS:
                kwargs[f.name] = [
                    x for x in (_to_dataclass(_PACK_NESTED_LISTS[f.name], e)
                                for e in data.get(f.name) or [])
                    if x is not None
                ]
            elif f.name == "gaps":
                kwargs[f.name] = [
                    Gap(
                        artifact=g["artifact"],
                        severity=GapSeverity(g["severity"]) if isinstance(g["severity"], str) else g["severity"],
                        message=g["message"],
                    )
                    for g in data.get("gaps", [])
                ]
            elif f.name in data:
                kwargs[f.name] = data[f.name]
            elif f.default is MISSING and f.default_factory is MISSING:
                kwargs[f.name] = ""
        return cast(T, DefensePack(**kwargs))
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
      - 'How my position held (or shifted)' (canonical) or the shorter
        'How my position held' (back-compat with older narrative files)
      - 'What I'd defend if asked' — numbered claims
      - 'Disclosure' — overrides auto-generated disclosure if present
    """
    text = _normalize(text)  # strip UTF-8 BOM / CRLF so the ^## anchor matches
    sections = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL):
        sections[m.group(1).strip()] = m.group(2).strip()

    decision_walkthrough: list[DecisionWalkthroughEntry] = []
    decisions_text = sections.get("The key decisions", "")
    for m in re.finditer(r"###\s*Decision\s*#(\d+).*?\n(.*?)(?=^### |\Z)", decisions_text, re.MULTILINE | re.DOTALL):
        decision_walkthrough.append(DecisionWalkthroughEntry(
            record_number=int(m.group(1)),
            narration=_strip_blockquote_markers(m.group(2)),
        ))

    came_in = _strip_blockquote_markers(sections.get("How I came in", ""))
    # Prefer the canonical (longer) heading the template ships, but accept the
    # shorter form so narrative.md files written under earlier examples still
    # render rather than silently losing the section.
    held = _strip_blockquote_markers(
        sections.get("How my position held (or shifted)", "")
        or sections.get("How my position held", "")
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
    ap.add_argument("--strict", action="store_true",
                    help="Exit non-zero if the pack has a HARD_STOP gap (for CI)")
    args = ap.parse_args()

    data = json.loads(args.pack_json.read_text(encoding="utf-8"))
    pack = _to_dataclass(DefensePack, data)
    assert pack is not None, "pack.json should never produce None"
    pack.narrative = _parse_narrative_md(args.narrative_md.read_text(encoding="utf-8"))

    # Fallback: if the SKILL didn't persist curated key_decisions to pack.json
    # but the user's narrative walks through specific records, materialize
    # key_decisions from the walkthrough so HTML and recording-script renderers
    # stay in sync. The renderer surfaces narration even when the RoR link is
    # broken (record_number in narrative doesn't match any record in the pack)
    # so the student's curated argument isn't silently dropped.
    if not pack.key_decisions and pack.narrative and pack.narrative.decision_walkthrough:
        for entry in pack.narrative.decision_walkthrough:
            rec_num = entry.record_number
            # Headline: first non-empty line of narration, truncated.
            first_line = next(
                (ln.strip() for ln in entry.narration.splitlines() if ln.strip()),
                "",
            )
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

    # --strict: artifacts are still written, but signal non-defensibility to
    # automated callers via a non-zero exit when the pack has a HARD_STOP gap.
    if args.strict and has_hard_stop(pack.gaps):
        sys.exit(1)


if __name__ == "__main__":
    main()
