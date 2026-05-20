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
        return cast(T, DefensePack(
            project_name=data["project_name"],
            context=data["context"],
            student_name=data.get("student_name", ""),
            scaffolding_level=data["scaffolding_level"],
            phase_at_export=data["phase_at_export"],
            export_timestamp=data["export_timestamp"],
            companion_version=data["companion_version"],
            position_statement=_to_dataclass(PositionStatement, data["position_statement"]),
            records_of_resistance=[
                r for r in (_to_dataclass(RecordOfResistance, x) for x in data["records_of_resistance"])
                if r is not None
            ],
            key_decisions=[
                k for k in (_to_dataclass(KeyDecision, x) for x in data["key_decisions"])
                if k is not None
            ],
            ai_use_log=_to_dataclass(AIUseLog, data["ai_use_log"]),
            reflection=_to_dataclass(Reflection, data["reflection"]),
            disclosure=_to_dataclass(Disclosure, data["disclosure"]),
            evolution_log_entries=data["evolution_log_entries"],
            narrative=_to_dataclass(Narrative, data["narrative"]),
            gaps=[
                Gap(
                    artifact=g["artifact"],
                    severity=GapSeverity(g["severity"]) if isinstance(g["severity"], str) else g["severity"],
                    message=g["message"],
                )
                for g in data["gaps"]
            ],
        ))
    field_names = {f.name for f in fields(cast(Any, cls))}
    return cast(T, cls(**{k: v for k, v in data.items() if k in field_names}))


def _parse_narrative_md(text: str) -> Narrative:
    """Read the user's approved defense-narrative.md and turn it into a Narrative.

    Expected H2 sections: 'How I came in', 'What I set out to protect',
    'The key decisions', 'How my position held', 'What I'd defend if asked',
    'Disclosure' (optional).
    """
    sections = {}
    for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL):
        sections[m.group(1).strip()] = m.group(2).strip()

    decision_walkthrough = []
    decisions_text = sections.get("The key decisions", "")
    for m in re.finditer(r"###\s*Decision\s*#(\d+).*?\n(.*?)(?=^### |\Z)", decisions_text, re.MULTILINE | re.DOTALL):
        decision_walkthrough.append({
            "record_number": int(m.group(1)),
            "narration": m.group(2).strip(),
        })

    came_in = sections.get("How I came in", "")
    held = sections.get("How my position held", "") or sections.get("How my position held (or shifted)", "")

    return Narrative(
        intro=came_in.splitlines()[0] if came_in else "",
        position_summary=came_in,
        decision_walkthrough=decision_walkthrough,
        reflection_summary=held,
        closing=sections.get("What I'd defend if asked", ""),
        user_approved=True,
        drafted_at="",
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
