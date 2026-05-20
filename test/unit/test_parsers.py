import unittest
from esf_pack.parsers import (
    parse_frontmatter_and_body,
    extract_sections,
    is_section_empty,
    parse_position_statement,
)
from esf_pack.schema import PositionStatement


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


if __name__ == "__main__":
    unittest.main()
