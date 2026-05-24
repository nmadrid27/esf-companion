import unittest
from esf_pack.render_html import render_html
from test.unit.test_render_script import _full_pack


class TestRenderHTML(unittest.TestCase):
    def test_contains_required_sections(self):
        out = render_html(_full_pack())
        for marker in ["Defense Pack", "Position", "Key decisions", "responsive-system"]:
            self.assertIn(marker, out)

    def test_presenter_mode_supported(self):
        out = render_html(_full_pack())
        self.assertIn("presenter", out)
        self.assertIn("?presenter=1", out)

    def test_has_deep_links_to_records(self):
        out = render_html(_full_pack())
        self.assertIn("ror-1", out)
        self.assertIn("ror-3", out)

    def test_self_contained_no_external_resources(self):
        out = render_html(_full_pack())
        self.assertNotIn('src="http', out)
        self.assertNotIn('href="http', out)


if __name__ == "__main__":
    unittest.main()
