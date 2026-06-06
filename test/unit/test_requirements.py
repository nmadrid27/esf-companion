# test/unit/test_requirements.py
import dataclasses
import tempfile
import unittest
from pathlib import Path

from esf_pack.aggregate import resolve_requirements
from esf_pack.schema import BriefRequirements


class TestBriefRequirements(unittest.TestCase):
    def test_defaults_to_none(self):
        self.assertIsNone(BriefRequirements().ror_minimum)

    def test_holds_a_minimum(self):
        self.assertEqual(BriefRequirements(ror_minimum=3).ror_minimum, 3)

    def test_is_frozen(self):
        r = BriefRequirements(ror_minimum=3)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            r.ror_minimum = 5  # type: ignore[misc]


_STATE = (
    "# State\n## Current Project\n"
    "- **Context:** test-course\n"
    "- **Project name:** widget\n"
)


def _ws(brief_body: str | None):
    tmp = Path(tempfile.mkdtemp(prefix="esf-req-"))
    (tmp / "companion-state.md").write_text(_STATE, encoding="utf-8")
    if brief_body is not None:
        d = tmp / "esf" / "test-course" / "briefs"
        d.mkdir(parents=True)
        (d / "widget-brief.md").write_text(brief_body, encoding="utf-8")
    return tmp


class TestResolveRequirements(unittest.TestCase):
    def test_canonical_key(self):
        ws = _ws("---\nrecords-of-resistance-minimum: 3\n---\n# Brief\n")
        self.assertEqual(resolve_requirements(ws).ror_minimum, 3)

    def test_ror_minimum_alias(self):
        ws = _ws("---\nror-minimum: 2\n---\n# Brief\n")
        self.assertEqual(resolve_requirements(ws).ror_minimum, 2)

    def test_no_brief_file(self):
        ws = _ws(None)
        self.assertIsNone(resolve_requirements(ws).ror_minimum)

    def test_brief_without_frontmatter(self):
        ws = _ws("# Brief\nProse only, no frontmatter.\n")
        self.assertIsNone(resolve_requirements(ws).ror_minimum)

    def test_non_integer_minimum(self):
        ws = _ws("---\nrecords-of-resistance-minimum: lots\n---\n# Brief\n")
        self.assertIsNone(resolve_requirements(ws).ror_minimum)

    def test_no_companion_state(self):
        tmp = Path(tempfile.mkdtemp(prefix="esf-req-"))
        self.assertIsNone(resolve_requirements(tmp).ror_minimum)


if __name__ == "__main__":
    unittest.main()
