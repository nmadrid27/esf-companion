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
        # Strip trailing punctuation that students naturally add to headings
        # (`## What AI Suggested:` instead of `## What AI Suggested`). Without
        # this, downstream `sections.get("What AI Suggested", "")` lookups
        # return empty and the student silently loses their whole section.
        heading = m.group(1).strip().rstrip(":").rstrip()
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

# Module-level compiled regexes used in section-specific parsers. Compiling
# once at module load is negligibly faster for our usual 5-10-RoR pack size,
# but keeps each regex visible in one place and is hygienic.
# Capture the body of a single-line blockquote (`> text`). The horizontal
# whitespace class is `[ \t]*` rather than `\s*` so it cannot span newlines —
# otherwise an empty `>` line followed by a `**Bold question?**` paragraph
# would have its `(.+)` match the bold question line and mis-attribute it as
# the drift quote.
_DRIFT_QUOTE_RE = re.compile(r"^>[ \t]*(.+)$", re.MULTILINE)
_INTERACTION_COUNT_RE = re.compile(r"Total AI interactions logged:\*\*\s*(\d+)")
_CHECKLIST_RE = re.compile(r"^\s*[-*]\s*\[([xX ])\]", re.MULTILINE)
_LEARNING_RE = re.compile(
    r"would not have learned without AI\?\*\*\s*>[ \t]*(.+?)(?=\n\s*\*\*|$)",
    re.DOTALL,
)
_TEMPTATION_RE = re.compile(
    r"tempted to accept AI output uncritically.*?\*\*\s*>[ \t]*(.+?)(?=\n\s*\*\*|$)",
    re.DOTALL,
)


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


# Element heading aliases. Real students adapt the templates — they write
# "## My Stance (Creative Direction)" instead of "## Element 1: My Stance", or
# "## Design Intent" instead of "## Element 2: What Matters Most". We accept
# any of the canonical Element-N phrasing plus a curated set of common variants
# so a Defense Pack can be produced against a Position Statement the student
# actually wrote in their own structure.
_ELEMENT_1_ALIASES = (
    "element 1",
    "my stance",
    "stance",
    "creative direction",
    "design intent",
)
_ELEMENT_2_ALIASES = (
    "element 2",
    "what matters most",
    "matters most",
    "values",
    "core values",
    "principles",
)
_ELEMENT_3_ALIASES = (
    "element 3",
    "what i will not compromise",
    "non-negotiables",
    "non negotiables",
    "hard lines",
    "lines i won't cross",
    "what i won't compromise",
)


def _heading_lead(heading: str) -> str:
    """Normalized heading with trailing parenthetical removed."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", heading).strip().lower()


def _heading_paren(heading: str) -> str:
    """Normalized contents of trailing parenthetical (empty if none)."""
    m = re.search(r"\(([^)]*)\)\s*$", heading)
    return m.group(1).strip().lower() if m else ""


def _match_element_sections(
    sections: dict,
    alias_sets: list,
) -> list:
    """Assign each heading to at most one element.

    `alias_sets` is a list of alias tuples in element order. Returns a parallel
    list of section contents (or "" when no match).

    Resolution rules:
      1. Lead-match (canonical part of heading) is preferred over parenthetical-match.
      2. Each heading is assigned to at most one element (no double-counting).
      3. Element order is used as a tie-breaker when one heading would match two
         element alias sets via the same path.

    Designed for real student PSes like:
      "## What Matters Most (Non-Negotiables)"
        → lead matches Element 2; paren matches Element 3.
        Lead wins, so this section becomes Element 2.
      "## AI Boundaries (What I Will Not Compromise On)"
        → lead doesn't match anything; paren matches Element 3.
        Paren-match for Element 3 wins.
    """
    n = len(alias_sets)
    matched_content = [""] * n
    used_headings: set = set()

    # Pass 1: lead matches (most specific). Each heading can match at most one
    # element; prefer the earliest element index when there's a conflict.
    for heading, content in sections.items():
        if heading in used_headings:
            continue
        lead = _heading_lead(heading)
        for i, aliases in enumerate(alias_sets):
            if matched_content[i]:
                continue  # element already assigned via lead
            for alias in aliases:
                if lead.startswith(alias):
                    matched_content[i] = content
                    used_headings.add(heading)
                    break
            if heading in used_headings:
                break

    # Pass 2: parenthetical matches for elements still empty.
    for heading, content in sections.items():
        if heading in used_headings:
            continue
        paren = _heading_paren(heading)
        if not paren:
            continue
        for i, aliases in enumerate(alias_sets):
            if matched_content[i]:
                continue
            for alias in aliases:
                if paren.startswith(alias):
                    matched_content[i] = content
                    used_headings.add(heading)
                    break
            if heading in used_headings:
                break

    return matched_content


def parse_position_statement(text: str) -> PositionStatement:
    _, body = parse_frontmatter_and_body(text)
    sections = extract_sections(body)
    matched = _match_element_sections(
        sections,
        [_ELEMENT_1_ALIASES, _ELEMENT_2_ALIASES, _ELEMENT_3_ALIASES],
    )
    stance = quote_content(matched[0])
    matters = quote_content(matched[1])
    non_neg = quote_content(matched[2])

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
        quotes = _DRIFT_QUOTE_RE.findall(after)
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


# Inline-tag extractor for the taught @resist / @default / @shift convention.
# @resist marks a record of resistance directly inline in a process blog or
# similar narrative file. @default marks acceptance, @shift marks a redirect.
# We only convert @resist hits into RoRs; the other tags are counted for the
# pack's process-metrics summary.
_RESIST_RE = re.compile(r"@resist\b", re.IGNORECASE)
_DEFAULT_RE = re.compile(r"@default\b", re.IGNORECASE)
_SHIFT_RE = re.compile(r"@shift\b", re.IGNORECASE)

# Package scopes (@types/foo, @babel/core) and CSS at-rules (@keyframes, @media)
# match a naive @-tag regex if we're not careful, but @resist has no NPM / CSS
# twin. The DEFAULT / SHIFT regexes are also safe — no common package or CSS
# rule is named exactly @default or @shift. Callers should still scope the
# scan to process-blog files specifically, not arbitrary node_modules trees.


_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)")


def _extract_paragraph_around(text: str, pos: int) -> str:
    """Return the markdown block containing position `pos`.

    A 'block' is bounded by blank lines, thematic breaks, or markdown headings
    (any level). List items get special handling: each bullet/numbered item is
    its own block (plus any indented continuation lines), so a bulleted list of
    `- @resist on X` / `- @resist on Y` produces two distinct blocks rather than
    one — otherwise the inline-tag scanner would either dedupe distinct
    decisions into a single record or inflate the count past the records list.
    """
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)
    if line_end == -1:
        line_end = len(text)
    current_line = text[line_start:line_end]

    # List item: block is this item plus indented continuation. Each item in a
    # tight bulleted list is its own block, so multiple `@resist` tags in one
    # list produce one record per item.
    if _LIST_ITEM_RE.match(current_line):
        end = line_end
        while end < len(text):
            next_end = text.find("\n", end + 1)
            if next_end == -1:
                next_end = len(text)
            next_line = text[end + 1:next_end]
            if not next_line.strip():
                break
            # Continuation must be indented further than the list marker.
            if not next_line.startswith(("  ", "\t")):
                break
            end = next_end
        return text[line_start:end].strip()

    # Prose paragraph: walk back to the first blank line or heading.
    cursor = line_start
    while cursor > 0:
        prev_end = text.rfind("\n", 0, cursor - 1)
        prev_line_start = prev_end + 1 if prev_end != -1 else 0
        prev_line = text[prev_line_start:cursor - 1] if prev_end != -1 else text[:cursor - 1]
        if not prev_line.strip():
            break
        if re.match(r"^#{1,6}\s", prev_line) or prev_line.strip() == "---":
            cursor = prev_line_start
            break
        # Stop at the preceding list item too — prose that follows a bullet
        # list shouldn't get glued to the list above.
        if _LIST_ITEM_RE.match(prev_line):
            break
        cursor = prev_line_start

    end_cursor = text.find("\n", pos)
    if end_cursor == -1:
        end_cursor = len(text)
    while end_cursor < len(text):
        next_end = text.find("\n", end_cursor + 1)
        if next_end == -1:
            next_end = len(text)
        next_line = text[end_cursor + 1:next_end]
        if not next_line.strip():
            break
        if re.match(r"^#{1,6}\s", next_line) or next_line.strip() == "---":
            break
        # End of a prose paragraph when the next line starts a list item.
        if _LIST_ITEM_RE.match(next_line):
            break
        end_cursor = next_end

    return text[cursor:end_cursor].strip()


def extract_inline_resists(
    text: str,
    source_label: str,
) -> tuple[list[RecordOfResistance], int, int, int]:
    """Scan `text` for @resist / @default / @shift tags.

    Returns (records, resist_count, default_count, shift_count). The records
    list contains one RecordOfResistance per @resist hit, with the surrounding
    block as `inline_narrative`. The counts include all occurrences of each tag
    (a single block can be one record but still count its tags).
    """
    text = _normalize(text)
    resist_count = len(_RESIST_RE.findall(text))
    default_count = len(_DEFAULT_RE.findall(text))
    shift_count = len(_SHIFT_RE.findall(text))

    records: list[RecordOfResistance] = []
    seen_blocks: set = set()
    for i, m in enumerate(_RESIST_RE.finditer(text), start=1):
        block = _extract_paragraph_around(text, m.start())

        # Skip tagging-legend / template blocks: if the block contains all three
        # of @resist, @default, and @shift, it's almost certainly explaining the
        # convention rather than tagging a real moment.
        has_resist = bool(_RESIST_RE.search(block))
        has_default = bool(_DEFAULT_RE.search(block))
        has_shift = bool(_SHIFT_RE.search(block))
        if has_resist and has_default and has_shift:
            continue

        # Skip blocks that are just placeholder text — the canonical pattern is
        # `[what you ...]` square-bracket fill-ins from the template.
        if re.search(r"\[(what|brief|tag).*?\]", block, re.IGNORECASE):
            continue

        # Dedupe within a single file when the same block contains multiple
        # @resist mentions (common in lists). Use first 200 chars as key.
        key = block[:200]
        if key in seen_blocks:
            continue
        seen_blocks.add(key)
        records.append(RecordOfResistance(
            record_number=0,  # aggregator assigns final numbers
            date="",
            ai_suggested="",
            why_rejected="",
            what_i_did_instead="",
            source=f"{source_label} (@resist #{i})",
            inline_narrative=block,
        ))
    return records, resist_count, default_count, shift_count


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
    m = _INTERACTION_COUNT_RE.search(summary)
    if m:
        interaction_count = int(m.group(1))

    # Five Questions pass rate. Scope the checklist scan to the Five-Questions
    # section specifically — globally scanning the body would mis-count any
    # markdown task list elsewhere in the log (a `## Next Steps` to-do list, an
    # action-items section, retro notes) as Five-Questions answers and fabricate
    # a pass rate. Accept the canonical heading plus the obvious variants.
    five_q_section = next(
        (sections[k] for k in sections
         if "five" in k.lower() and "question" in k.lower()),
        "",
    )
    checklist_lines = _CHECKLIST_RE.findall(five_q_section)
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

    # Terminate each Kept/Revised/Rejected block at the start of the NEXT
    # labeled block, not at any inline `**bold**` token. A naive `(?=\n\s*\*\*|$)`
    # truncates the field as soon as the student writes an emphasized phrase
    # (e.g. `**Layout principles** — the friction premise`), silently dropping
    # everything from the bold-list onward.
    _NEXT_KRR_LABEL_RE = (
        r"\n\*\*(?:Kept\s*\(and why\)|Revised\s*\(what changed and why\)|Rejected\s*\(and why\)):\*\*"
    )

    def _after(label: str) -> str:
        m = re.search(
            rf"\*\*{re.escape(label)}\*\*\s*(.*?)(?={_NEXT_KRR_LABEL_RE}|$)",
            krr,
            re.DOTALL,
        )
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
    learning_m = _LEARNING_RE.search(reflection_section)
    learning = learning_m.group(1).strip() if learning_m else ""
    temptation_m = _TEMPTATION_RE.search(reflection_section)
    temptation = temptation_m.group(1).strip() if temptation_m else ""

    return Reflection(
        kept=kept,
        revised=revised,
        rejected=rejected,
        five_questions=five_questions,
        learning=learning,
        temptation_moments=temptation,
    )
