import unittest
from unittest.mock import patch
from esf_pack.render_pdf import render_pdf, WEASYPRINT_AVAILABLE, render_pdf_or_skip
from test.unit.test_render_script import _full_pack


class TestRenderPDF(unittest.TestCase):
    def test_returns_bytes_when_available(self):
        if not WEASYPRINT_AVAILABLE:
            self.skipTest("weasyprint not installed in this environment")
        out = render_pdf(_full_pack())
        self.assertIsInstance(out, bytes)
        self.assertTrue(out.startswith(b"%PDF"))

    def test_or_skip_returns_none_when_unavailable(self):
        with patch("esf_pack.render_pdf.WEASYPRINT_AVAILABLE", False):
            result, msg = render_pdf_or_skip(_full_pack())
            self.assertIsNone(result)
            self.assertIn("weasyprint", msg.lower())

    def test_or_skip_returns_bytes_when_available(self):
        with patch("esf_pack.render_pdf.WEASYPRINT_AVAILABLE", True), \
             patch("esf_pack.render_pdf.render_pdf", return_value=b"%PDF-fake"):
            result, msg = render_pdf_or_skip(_full_pack())
            self.assertEqual(result, b"%PDF-fake")
            self.assertEqual(msg, "")


if __name__ == "__main__":
    unittest.main()
