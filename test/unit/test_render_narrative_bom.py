"""render.py must tolerate a UTF-8 BOM at the head of defense-narrative.md.

Regression guard for #30: Windows Notepad writes UTF-8 with a leading BOM by
default. The BOM sat before the first `## How I came in` heading, so the
MULTILINE `^## ` section regex could not anchor and the first section was
silently dropped on `render.py --skip-narrative` re-runs.
"""
import unittest

from render import _parse_narrative_md

BOM = "﻿"


class TestNarrativeBOM(unittest.TestCase):
    def test_bom_prefixed_narrative_parses_first_section(self):
        md = BOM + "## How I came in\n\n> I came in wanting durable structure.\n"
        nar = _parse_narrative_md(md)
        self.assertIn("durable structure", nar.position_summary)

    def test_no_bom_still_parses(self):
        md = "## How I came in\n\n> Plain narrative, no BOM.\n"
        nar = _parse_narrative_md(md)
        self.assertIn("Plain narrative", nar.position_summary)


if __name__ == "__main__":
    unittest.main()
