"""PDF rendering via WeasyPrint. Optional dependency — gracefully skipped if missing."""
from __future__ import annotations
import re
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


# Absolute paths embedded in WeasyPrint exception messages (and in Windows
# variants like `C:\Users\foo\...`) leak the user's home directory into anything
# downstream that surfaces or logs the error. Replace each path with just its
# basename so the diagnostic still names the offending file but not its location.
_ABSPATH_RE = re.compile(r"(?:[A-Za-z]:)?[\\/](?:[^\s\\/'\"]+[\\/])+[^\s\\/'\")]+")


def _scrub_paths(msg: str) -> str:
    """Replace absolute filesystem paths in `msg` with their basename only."""
    def _to_basename(match: re.Match) -> str:
        path = match.group(0)
        # Use forward-slash split for Unix and backslash for Windows; the last
        # non-empty segment is the basename either way.
        for sep in ("/", "\\"):
            if sep in path:
                path = path.rsplit(sep, 1)[-1]
        return path
    return _ABSPATH_RE.sub(_to_basename, msg)


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
        scrubbed = _scrub_paths(str(e))
        return None, f"PDF generation failed: {scrubbed}. HTML and MD outputs are still available."
