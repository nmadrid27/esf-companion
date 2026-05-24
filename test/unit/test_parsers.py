import unittest
from esf_pack.parsers import (
    parse_frontmatter_and_body,
    extract_sections,
    is_section_empty,
    quote_content,
    parse_position_statement,
    parse_record_of_resistance,
    parse_ai_use_log,
    parse_reflection,
)
from esf_pack.schema import PositionStatement, RecordOfResistance, AIUseLog, Reflection


SAMPLE = """---
type: position-statement
project: responsive-system
date: 2026-04-15
---

# Position Statement

## Element 1: My Stance

> I want to make X.

## Element 2: What Matters Most

> Y.

## Element 3: What I Will Not Compromise On

>
"""


class TestFrontmatterParser(unittest.TestCase):
    def test_parses_frontmatter_keys(self):
        fm, _ = parse_frontmatter_and_body(SAMPLE)
        self.assertEqual(fm["type"], "position-statement")
        self.assertEqual(fm["project"], "responsive-system")
        self.assertEqual(fm["date"], "2026-04-15")

    def test_body_excludes_frontmatter(self):
        _, body = parse_frontmatter_and_body(SAMPLE)
        self.assertFalse(body.startswith("---"))
        self.assertIn("Element 1", body)

    def test_missing_frontmatter_returns_empty_dict(self):
        fm, body = parse_frontmatter_and_body("# Just a heading\n")
        self.assertEqual(fm, {})
        self.assertIn("Just a heading", body)


class TestSectionExtractor(unittest.TestCase):
    def test_extracts_h2_sections(self):
        _, body = parse_frontmatter_and_body(SAMPLE)
        sections = extract_sections(body)
        self.assertIn("Element 1: My Stance", sections)
        self.assertIn("I want to make X.", sections["Element 1: My Stance"])

    def test_section_quote_content_extracted(self):
        _, body = parse_frontmatter_and_body(SAMPLE)
        sections = extract_sections(body)
        self.assertEqual(sections["Element 2: What Matters Most"].strip(), "> Y.")


class TestEmptyCheck(unittest.TestCase):
    def test_empty_quote_block_is_empty(self):
        self.assertTrue(is_section_empty(">"))
        self.assertTrue(is_section_empty(">\n"))
        self.assertTrue(is_section_empty("> \n"))
        self.assertTrue(is_section_empty(""))

    def test_non_empty_quote_is_not_empty(self):
        self.assertFalse(is_section_empty("> something here"))


POSITION_SAMPLE = """---
type: position-statement
project: responsive-system
date: 2026-04-15
---

# Position Statement

## Element 1: My Stance

> I want to make a responsive system.

## Element 2: What Matters Most

> The system must respond.

## Element 3: What I Will Not Compromise On

> No autoplay.

## After the AI Session

**Drift level:** minor
**What shifted:**

> Started leaning toward more feedback.

**Was the shift your decision, or did you follow AI's framing without questioning it?**

> Mine.
"""


class TestPositionStatementParser(unittest.TestCase):
    def test_parses_three_elements(self):
        ps = parse_position_statement(POSITION_SAMPLE)
        self.assertIsInstance(ps, PositionStatement)
        self.assertEqual(ps.stance, "I want to make a responsive system.")
        self.assertEqual(ps.what_matters_most, "The system must respond.")
        self.assertEqual(ps.non_negotiables, "No autoplay.")

    def test_parses_drift(self):
        ps = parse_position_statement(POSITION_SAMPLE)
        self.assertEqual(ps.drift_level, "minor")
        self.assertEqual(ps.drift_what_shifted, "Started leaning toward more feedback.")
        self.assertTrue(ps.drift_was_user_decision)

    def test_missing_drift_section_returns_none(self):
        no_drift = POSITION_SAMPLE.split("## After")[0]
        ps = parse_position_statement(no_drift)
        self.assertIsNone(ps.drift_level)


ROR_SAMPLE = """---
type: record-of-resistance
project: responsive-system
date: 2026-04-20
record-number: 1
---

# Record of Resistance

## What AI Suggested
> 12-column grid.

## Why I Rejected or Revised It
> Conflicts with friction premise.

## What I Did Instead
> Off-grid staggered layout.
"""


class TestRoRParser(unittest.TestCase):
    def test_parses_record(self):
        ror = parse_record_of_resistance(ROR_SAMPLE)
        self.assertIsInstance(ror, RecordOfResistance)
        self.assertEqual(ror.record_number, 1)
        self.assertEqual(ror.date, "2026-04-20")
        self.assertEqual(ror.ai_suggested, "12-column grid.")
        self.assertEqual(ror.why_rejected, "Conflicts with friction premise.")
        self.assertEqual(ror.what_i_did_instead, "Off-grid staggered layout.")


AIUSE_SAMPLE = """---
type: esf-template
project: responsive-system
---

# AI Use Log

## Intervention Summary

| Moment | AI Output | My Decision | Reasoning |
|--------|-----------|-------------|-----------|
| RoR #1 | grid | Reject | conflicts |
| RoR #3 | curves | Reject | same |

## Pattern Analysis

> Rejected when AI optimized for comfort.

## Summary Reflection

**Total AI interactions logged:** 12
**Percentage of AI output incorporated without major revision:** 35%
**Percentage substantially revised:** 25%
**Percentage rejected:** 40%
"""


REFLECTION_SAMPLE = """---
type: esf-template
project: responsive-system
---

# Reflection

## What I Kept, Revised, and Rejected

**Kept (and why):** Technical scaffolding.

**Revised (what changed and why):** Color palette.

**Rejected (and why):** Easing curves.

## The Five Questions

| # | Question | Answer | Notes |
|---|----------|--------|-------|
| 1 | Can I defend this? | Yes | |
| 2 | Is this mine? | Yes | |
| 3 | Did I verify? | Yes | |
| 4 | Would I teach this? | Yes | |
| 5 | Is my disclosure honest? | Yes | |

## Reflection

**What did I learn from this project that I would not have learned without AI?**
> That my instincts sharpen.

**What did I learn despite using AI?**
> Rejection is editorial.

**Where was I most tempted to accept AI output uncritically, and why?**
> Around accessibility.
"""


class TestAIUseLogParser(unittest.TestCase):
    def test_parses_log_counts(self):
        log = parse_ai_use_log(AIUSE_SAMPLE)
        self.assertIsInstance(log, AIUseLog)
        self.assertEqual(log.interaction_count, 12)
        self.assertIn("comfort", log.pattern_analysis)
        self.assertEqual(log.intervention_summary.count("Reject"), 2)


class TestReflectionParser(unittest.TestCase):
    def test_parses_five_questions(self):
        r = parse_reflection(REFLECTION_SAMPLE)
        self.assertIsInstance(r, Reflection)
        self.assertTrue(r.five_questions["defend"])
        self.assertTrue(r.five_questions["mine"])
        self.assertEqual(r.kept, "Technical scaffolding.")
        self.assertIn("instincts sharpen", r.learning)


PS_TEMPLATE_VARIANT = """---
type: position-statement
project: writer-example
date: 2026-04-01
---

# Position Statement

## Element 1: My Stance

> A.

---

## Element 2: What Matters Most

> B.

---

## Element 3: What I Will Not Compromise

> C.

---

## After Drafting

**Drift level:** minor
**What shifted:**

> A small thing.

**Was the shift your decision, or did you follow AI's framing without questioning it?**

> Mine.
"""


ROR_WITH_FOOTER = """---
type: record-of-resistance
project: x
date: 2026-04-20
record-number: 1
---

# Record of Resistance

## What AI Suggested

> Standard grid.

## Why I Rejected or Revised It

> Conflicts with friction.

## What I Did Instead

> Off-grid staggered layout.

---

*Epistemic Stewardship Framework, Record of Resistance Template*
*Document moments where you deliberately did not follow an AI suggestion, and why.*
"""


class TestPrefixMatching(unittest.TestCase):
    """Tolerant heading matches for headings that drift across templates and examples."""

    def test_element_3_without_trailing_On(self):
        ps = parse_position_statement(PS_TEMPLATE_VARIANT)
        self.assertEqual(ps.non_negotiables, "C.")

    def test_drift_section_with_after_drafting_heading(self):
        ps = parse_position_statement(PS_TEMPLATE_VARIANT)
        self.assertEqual(ps.drift_level, "minor")
        self.assertEqual(ps.drift_what_shifted, "A small thing.")
        self.assertTrue(ps.drift_was_user_decision)


class TestFooterStripping(unittest.TestCase):
    """Template footer artifacts must not leak into rendered fields."""

    def test_quote_content_strips_trailing_thematic_break(self):
        self.assertEqual(quote_content("> something\n\n---"), "something")
        self.assertEqual(quote_content("> a\n> b\n\n---\n---"), "a b")

    def test_quote_content_strips_trailing_italic_footer(self):
        out = quote_content("> something\n\n*Epistemic Stewardship Framework, Record of Resistance Template*")
        self.assertEqual(out, "something")

    def test_ror_parser_drops_template_footer(self):
        ror = parse_record_of_resistance(ROR_WITH_FOOTER)
        self.assertEqual(ror.what_i_did_instead, "Off-grid staggered layout.")
        self.assertNotIn("Epistemic", ror.what_i_did_instead)
        self.assertNotIn("---", ror.what_i_did_instead)


class TestEncodingAndLineEndings(unittest.TestCase):
    """Real files in the wild use CRLF (Windows / web editors) or have a UTF-8 BOM.
    The parser must handle both transparently — Track-D-equivalent bugs surfaced
    by the post-merge code review.
    """

    def test_crlf_frontmatter_parses(self):
        crlf = "---\r\ntype: record-of-resistance\r\nproject: x\r\ndate: 2026-01-01\r\nrecord-number: 1\r\n---\r\n\r\n## What AI Suggested\r\n\r\n> a\r\n\r\n## Why I Rejected or Revised It\r\n\r\n> b\r\n\r\n## What I Did Instead\r\n\r\n> c\r\n"
        ror = parse_record_of_resistance(crlf)
        self.assertEqual(ror.record_number, 1)
        self.assertEqual(ror.date, "2026-01-01")
        self.assertEqual(ror.ai_suggested, "a")

    def test_utf8_bom_frontmatter_parses(self):
        bom = "﻿" + SAMPLE  # SAMPLE defined above
        fm, _ = parse_frontmatter_and_body(bom)
        self.assertEqual(fm.get("type"), "position-statement")


class TestRecordNumberDefensive(unittest.TestCase):
    """A blank or non-numeric `record-number:` must not raise; defaults to 0
    so the aggregator can surface it as a duplicate-number warning rather than
    silently dropping the file.
    """

    def _ror_with_number(self, raw: str) -> str:
        return (
            f"---\ntype: record-of-resistance\nproject: x\ndate: 2026-01-01\n"
            f"record-number: {raw}\n---\n\n"
            f"## What AI Suggested\n\n> a\n\n"
            f"## Why I Rejected or Revised It\n\n> b\n\n"
            f"## What I Did Instead\n\n> c\n"
        )

    def test_blank_record_number_defaults_to_zero(self):
        ror = parse_record_of_resistance(self._ror_with_number(""))
        self.assertEqual(ror.record_number, 0)

    def test_non_numeric_record_number_defaults_to_zero(self):
        ror = parse_record_of_resistance(self._ror_with_number("1a"))
        self.assertEqual(ror.record_number, 0)


class TestBlockquotePrefixStrip(unittest.TestCase):
    """str.lstrip('> ') is a character-set strip, not a prefix strip — would
    treat `>>>nested` as `nested` and `> ` / `>>` identically. The fixed
    parser uses a regex single-level strip so legitimate content with leading
    `>` characters survives.
    """

    def test_single_level_blockquote_stripped(self):
        self.assertEqual(quote_content("> hello"), "hello")

    def test_nested_blockquote_keeps_inner_marker(self):
        # `>> nested` should produce `> nested` (one level removed), not `nested`
        self.assertEqual(quote_content(">> nested"), "> nested")


if __name__ == "__main__":
    unittest.main()
