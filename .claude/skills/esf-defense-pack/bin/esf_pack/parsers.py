"""Markdown frontmatter + H2 section parser. Stdlib only."""
from __future__ import annotations
import re
from typing import Tuple


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)
_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def parse_frontmatter_and_body(text: str) -> Tuple[dict, str]:
    """Return (frontmatter_dict, body_without_frontmatter).

    Frontmatter is parsed as simple key: value lines. Empty strings allowed.
    No nested YAML support — ESF templates only use flat keys.
    """
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
    """Split body by H2 headings; return {heading_text: section_content_until_next_h2}."""
    sections = {}
    matches = list(_H2_RE.finditer(body))
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


def quote_content(content: str) -> str:
    """Extract the user's prose from a `> ...` blockquote, joining lines, stripping markers."""
    lines = [line.lstrip("> ").rstrip() for line in content.splitlines() if line.strip()]
    return " ".join(lines).strip()
