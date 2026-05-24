"""PDF rendering via WeasyPrint. Optional dependency — gracefully skipped if missing."""
from __future__ import annotations
from typing import Optional, Tuple
from .render_html import render_html
from .schema import DefensePack


try:
    from weasyprint import HTML as _HTML  # pyright: ignore[reportMissingImports]
    WEASYPRINT_AVAILABLE = True
except ImportError:
    _HTML = None
    WEASYPRINT_AVAILABLE = False


_SKIP_MESSAGE = (
    "PDF generation requires weasyprint. Install with `pip install weasyprint` "
    "(on macOS you may also need `brew install pango`). "
    "HTML and recording-script outputs were produced successfully. "
    "You can also open the HTML in a browser and use Print → Save as PDF."
)


def render_pdf(pack: DefensePack) -> bytes:
    if not WEASYPRINT_AVAILABLE or _HTML is None:
        raise RuntimeError("weasyprint not installed")
    html_str = render_html(pack)
    return _HTML(string=html_str).write_pdf()


def render_pdf_or_skip(pack: DefensePack) -> Tuple[Optional[bytes], str]:
    """Return (pdf_bytes, '') on success, (None, message) on graceful skip."""
    if not WEASYPRINT_AVAILABLE:
        return None, _SKIP_MESSAGE
    try:
        return render_pdf(pack), ""
    except Exception as e:
        return None, f"PDF generation failed: {e}. HTML and MD outputs are still available."
