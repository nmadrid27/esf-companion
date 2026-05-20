import unittest
from esf_pack.parsers import parse_frontmatter_and_body, extract_sections, is_section_empty


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


if __name__ == "__main__":
    unittest.main()
