"""Prose blocks in render_html must preserve paragraph and line structure.

Regression guards for #30: multi-paragraph fields (intro, what-set-out-to-protect,
closing) were collapsed into a single <p>, and multi-line decision narrations lost
their line breaks in HTML while the recording-script .md kept them.
"""
import unittest

from esf_pack.render_html import (
    _intro_section,
    _protect_block,
    _closing_html,
    _decisions_html,
)
from esf_pack.schema import DecisionWalkthroughEntry
from test.unit.test_render_script import _full_pack


class TestProseParagraphs(unittest.TestCase):
    def test_intro_two_paragraphs_emit_two_p_tags(self):
        pack = _full_pack()
        pack.narrative.intro = "First paragraph.\n\nSecond paragraph."
        html = _intro_section(pack)
        self.assertEqual(html.count("<p>"), 2, html)
        self.assertIn("First paragraph.", html)
        self.assertIn("Second paragraph.", html)

    def test_protect_two_paragraphs_emit_two_p_tags(self):
        pack = _full_pack()
        pack.narrative.what_set_out_to_protect = "Protect one.\n\nProtect two."
        html = _protect_block(pack)
        self.assertEqual(html.count("<p>"), 2, html)
        self.assertIn("Protect one.", html)
        self.assertIn("Protect two.", html)

    def test_closing_fallback_two_paragraphs_emit_two_p_tags(self):
        pack = _full_pack()
        # Force the prose fallback path: no numbered defend_claims.
        pack.narrative.defend_claims = []
        pack.narrative.closing = "Closing one.\n\nClosing two."
        html = _closing_html(pack)
        self.assertEqual(html.count("<p>"), 2, html)
        self.assertIn("Closing one.", html)
        self.assertIn("Closing two.", html)


class TestDecisionNarrationLineBreaks(unittest.TestCase):
    def test_intra_paragraph_newline_becomes_br(self):
        pack = _full_pack()
        pack.narrative.decision_walkthrough[0] = DecisionWalkthroughEntry(
            record_number=1, narration="Line one.\nLine two."
        )
        html = _decisions_html(pack)
        self.assertIn("<br>", html)
        self.assertIn("Line one.", html)
        self.assertIn("Line two.", html)

    def test_blank_line_in_narration_splits_paragraphs(self):
        pack = _full_pack()
        pack.narrative.decision_walkthrough[0] = DecisionWalkthroughEntry(
            record_number=1, narration="Para one.\n\nPara two."
        )
        html = _decisions_html(pack)
        # The two paragraphs must land in separate <p> elements, not one.
        self.assertIn("<p>Para one.</p>", html)
        self.assertIn("<p>Para two.</p>", html)


if __name__ == "__main__":
    unittest.main()
