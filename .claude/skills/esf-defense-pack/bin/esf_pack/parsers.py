"""Markdown frontmatter + H2 section parser. Stdlib only."""
from __future__ import annotations
import re
from typing import Tuple

from .schema import PositionStatement, RecordOfResistance, AIUseLog, Reflection


# Frontmatter regex accepts either LF or CRLF line endings so files saved by
# Windows editors or pasted from web editors parse correctly.
_FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)", re.DOTALL)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)


def _normalize(text: str) -> str:
    """Strip UTF-8 BOM and normalize CRLF to LF before parsing.

    Some macOS/Windows editors silently prepend a BOM or use CRLF line endings;
    both break naive regex parsing. We normalize once at the entry point so the
    rest of the parser can assume LF and no BOM.
    """
    return text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")


def parse_frontmatter_and_body(text: str) -> Tuple[dict, str]:
    """Return (frontmatter_dict, body_without_frontmatter).

    Frontmatter is parsed as simple key: value lines. Empty strings allowed.
    No nested YAML support — ESF templates only use flat keys.

    Tolerates UTF-8 BOM and CRLF line endings transparently.
    """
    text = _normalize(text)
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
    """Split body by H2 headings; return {heading_text: section_content_until_next_h2}.

    Strips fenced code blocks (```...```) before splitting so that an H2-looking
    line *inside* a code block doesn't falsely terminate the surrounding section.
    Code-block content within a section is preserved by replacing matched fences
    with a placeholder string of equal-ish length before regex matching, then
    restoring; in our markdown-template use case ESF templates don't currently
    use fenced blocks, but this guard prevents the worst-case parser-confusion
    silently dropping section content if the convention ever changes.
    """
    # Replace fenced code blocks with a placeholder of matching length so offsets
    # stay aligned (cheap and easy: same-length spaces).
    placeholder_body = _FENCED_CODE_RE.sub(lambda m: " " * len(m.group(0)), body)
    sections = {}
    matches = list(_H2_RE.finditer(placeholder_body))
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


_THEMATIC_BREAK_RE = re.compile(r"-{3,}")
_ITALIC_FOOTER_RE = re.compile(r"\*[^*]+\*")
# Single-level blockquote prefix strip: `> ` optionally with one extra `>` for
# legacy/edge cases. Uses a regex (not lstrip) because str.lstrip("> ") is a
# character-set strip — it would collapse `>>>nested` to `nested` and treat
# `>>` and `> ` identically, eating legitimate content.
_BLOCKQUOTE_PREFIX_RE = re.compile(r"^>\s?")


def _strip_blockquote_prefix(line: str) -> str:
    return _BLOCKQUOTE_PREFIX_RE.sub("", line, count=1)


def quote_content(content: str) -> str:
    """Extract the user's prose from a `> ...` blockquote, joining lines, stripping markers.

    Also strips trailing thematic-break lines (`---`) and trailing italic-only lines
    that come from template footers (e.g. `*Epistemic Stewardship Framework, ...*`).
    Those are template artifacts, not user content, and would otherwise bleed into
    the rendered defense pack and the recording script.
    """
    lines: list[str] = []
    for line in content.splitlines():
        if not line.strip():
            continue
        stripped = _strip_blockquote_prefix(line).rstrip()
        if not stripped:
            continue
        lines.append(stripped)
    while lines and (
        _THEMATIC_BREAK_RE.fullmatch(lines[-1])
        or _ITALIC_FOOTER_RE.fullmatch(lines[-1])
    ):
        lines.pop()
    return " ".join(lines).strip()


def _section_by_prefix(sections: dict, prefix: str) -> str:
    """Return the first section whose heading starts with `prefix`, or empty string.

    Used for headings that drift across templates and examples (e.g. "Element 3:
    What I Will Not Compromise" with or without trailing "On"; "After the AI
    Session" vs. "After Drafting" vs. "After the Engagement").
    """
    for k, v in sections.items():
        if k.startswith(prefix):
            return v
    return ""


def parse_position_statement(text: str) -> PositionStatement:
    _, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    stance = quote_content(sections.get("Element 1: My Stance", ""))
    matters = quote_content(sections.get("Element 2: What Matters Most", ""))
    non_neg = quote_content(_section_by_prefix(sections, "Element 3: What I Will Not Compromise"))

    drift_level = None
    drift_what = None
    drift_user_decision = None
    after = _section_by_prefix(sections, "After ")
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
    # Defensive parse of record-number: blank, non-numeric, or missing all
    # default to 0 rather than raising. The blanket `except Exception` in the
    # aggregator's RoR loop would otherwise silently drop the file with no
    # signal to the student. A 0-numbered record will sort first and the
    # aggregator's duplicate-detection (see S4) will surface collisions.
    raw_num = fm.get("record-number", "0")
    try:
        record_number = int(str(raw_num).strip() or "0")
    except (ValueError, TypeError):
        record_number = 0
    date = fm.get("date", "")
    project = fm.get("project", "")
    return RecordOfResistance(
        record_number=record_number,
        date=date,
        ai_suggested=quote_content(sections.get("What AI Suggested", "")),
        why_rejected=quote_content(sections.get("Why I Rejected or Revised It", "")),
        what_i_did_instead=quote_content(sections.get("What I Did Instead", "")),
        project=project,
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

    # Five Questions pass rate. Restrict the match to actual checklist lines
    # (lines starting with `-` or `*` bullet, optionally indented) so we don't
    # accidentally count any literal `[ ]` in prose as an unchecked question.
    checklist_lines = re.findall(r"^\s*[-*]\s*\[([xX ])\]", body, re.MULTILINE)
    if checklist_lines:
        yes_count = sum(1 for c in checklist_lines if c.lower() == "x")
        pass_rate = yes_count / len(checklist_lines)
    else:
        pass_rate = None

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
