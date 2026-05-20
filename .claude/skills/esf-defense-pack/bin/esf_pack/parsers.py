"""Markdown frontmatter + H2 section parser. Stdlib only."""
from __future__ import annotations
import re
from typing import Tuple

from .schema import PositionStatement, RecordOfResistance, AIUseLog, Reflection


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


def parse_ai_use_log(text: str) -> AIUseLog:
    _, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    intervention = sections.get("Intervention Summary", "")
    pattern = quote_content(sections.get("Pattern Analysis", ""))
    summary = sections.get("Summary Reflection", "")

    interaction_count = 0
    m = re.search(r"Total AI interactions logged:\*\*\s*(\d+)", summary)
    if m:
        interaction_count = int(m.group(1))

    # Five Questions pass rate: count "[x]" or "Yes" checks across the log
    yes_count = len(re.findall(r"\[x\]", body, re.IGNORECASE))
    total_q = len(re.findall(r"\[\s*[xX ]\s*\]", body))
    pass_rate = (yes_count / total_q) if total_q else None

    return AIUseLog(
        interaction_count=interaction_count,
        verification_count=body.count("Checked?"),
        intervention_summary=intervention.strip(),
        pattern_analysis=pattern,
        five_questions_pass_rate=pass_rate,
    )


def parse_reflection(text: str) -> Reflection:
    _, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    krr = sections.get("What I Kept, Revised, and Rejected", "")

    def _after(label: str) -> str:
        m = re.search(rf"\*\*{re.escape(label)}\*\*\s*(.*?)(?=\n\s*\*\*|$)", krr, re.DOTALL)
        return m.group(1).strip() if m else ""

    kept = _after("Kept (and why):")
    revised = _after("Revised (what changed and why):")
    rejected = _after("Rejected (and why):")

    five_q_table = sections.get("The Five Questions", "")

    def _q(pattern: str) -> bool:
        m = re.search(rf"{pattern}.*?\|\s*(\w+)", five_q_table, re.IGNORECASE)
        return bool(m and "yes" in m.group(1).lower())

    five_questions = {
        "defend": _q(r"defend"),
        "mine": _q(r"mine\?"),
        "verify": _q(r"verify\?"),
        "teach": _q(r"teach this\?"),
        "disclose": _q(r"disclosure honest\?"),
    }

    reflection_section = sections.get("Reflection", "")
    learning_m = re.search(r"would not have learned without AI\?\*\*\s*>\s*(.+?)(?=\n\s*\*\*|$)", reflection_section, re.DOTALL)
    learning = learning_m.group(1).strip() if learning_m else ""
    temptation_m = re.search(r"tempted to accept AI output uncritically.*?\*\*\s*>\s*(.+?)(?=\n\s*\*\*|$)", reflection_section, re.DOTALL)
    temptation = temptation_m.group(1).strip() if temptation_m else ""

    return Reflection(
        kept=kept,
        revised=revised,
        rejected=rejected,
        five_questions=five_questions,
        learning=learning,
        temptation_moments=temptation,
    )
