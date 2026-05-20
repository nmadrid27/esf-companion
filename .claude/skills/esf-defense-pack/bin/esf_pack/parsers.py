"""Markdown frontmatter + H2 section parser. Stdlib only."""
from __future__ import annotations
import re
from typing import Tuple

from .schema import PositionStatement, RecordOfResistance


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def parse_frontmatter_and_body(text: str) -> Tuple[dict, str]:
    """Return (frontmatter_dict, body_without_frontmatter).

    Frontmatter is parsed as simple key: value lines. Empty strings allowed.
    No nested YAML support — ESF templates only use flat keys.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def extract_sections(body: str) -> dict:
    """Split body by H2 headings; return {heading_text: section_content_until_next_h2}."""
    sections = {}
    matches = list(_H2_RE.finditer(body))
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[heading] = body[start:end].strip()
    return sections


def is_section_empty(content: str) -> bool:
    """A section is empty if it contains only blank lines or empty blockquote markers."""
    stripped = content.strip()
    if not stripped:
        return True
    cleaned = "\n".join(line.lstrip("> ").strip() for line in stripped.splitlines())
    return not cleaned.strip()


def quote_content(content: str) -> str:
    """Extract the user's prose from a `> ...` blockquote, joining lines, stripping markers."""
    lines = [line.lstrip("> ").rstrip() for line in content.splitlines() if line.strip()]
    return " ".join(lines).strip()


def parse_position_statement(text: str) -> PositionStatement:
    _, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    stance = quote_content(sections.get("Element 1: My Stance", ""))
    matters = quote_content(sections.get("Element 2: What Matters Most", ""))
    non_neg = quote_content(sections.get("Element 3: What I Will Not Compromise On", ""))

    drift_level = None
    drift_what = None
    drift_user_decision = None
    after = sections.get("After the AI Session", "")
    if after:
        for line in after.splitlines():
            if line.startswith("**Drift level:**"):
                value = line.split("**Drift level:**", 1)[1].strip()
                if value and value not in ("not set", "—"):
                    drift_level = value
        quotes = re.findall(r"^>\s*(.+)$", after, re.MULTILINE)
        if len(quotes) >= 1:
            drift_what = quotes[0].strip()
        if len(quotes) >= 2:
            answer = quotes[1].strip().lower()
            drift_user_decision = "mine" in answer or "my decision" in answer or answer.startswith("yes")

    return PositionStatement(
        stance=stance,
        what_matters_most=matters,
        non_negotiables=non_neg,
        drift_level=drift_level,
        drift_what_shifted=drift_what,
        drift_was_user_decision=drift_user_decision,
    )


def parse_record_of_resistance(text: str) -> RecordOfResistance:
    fm, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    record_number = int(fm.get("record-number", 0))
    date = fm.get("date", "")
    return RecordOfResistance(
        record_number=record_number,
        date=date,
        ai_suggested=quote_content(sections.get("What AI Suggested", "")),
        why_rejected=quote_content(sections.get("Why I Rejected or Revised It", "")),
        what_i_did_instead=quote_content(sections.get("What I Did Instead", "")),
    )
