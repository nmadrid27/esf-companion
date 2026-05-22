import json
import unittest
from dataclasses import asdict
from pathlib import Path

from esf_pack.aggregate import aggregate_from_dir, find_context_root


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "defense-pack"


class TestAggregate(unittest.TestCase):
    def test_aggregate_full_fixture(self):
        pack = aggregate_from_dir(FIXTURES / "full")
        self.assertEqual(pack.project_name, "responsive-system")
        self.assertEqual(pack.context, "test-course")
        self.assertEqual(pack.scaffolding_level, "Independent")
        self.assertEqual(len(pack.records_of_resistance), 5)
        self.assertIsNotNone(pack.reflection)
        self.assertIsNotNone(pack.ai_use_log)
        self.assertTrue(pack.position_statement.stance.startswith("I"))
        warning_artifacts = [g.artifact for g in pack.gaps if g.severity.value == "warning"]
        self.assertEqual(warning_artifacts, [])

    def test_find_context_root_locates_companion_state(self):
        root = find_context_root(FIXTURES / "full" / "esf" / "test-course")
        self.assertEqual(root.name, "full")


class TestSnapshots(unittest.TestCase):
    def _compare_to_snapshot(self, fixture_name):
        pack = aggregate_from_dir(FIXTURES / fixture_name)
        actual = asdict(pack)
        actual["export_timestamp"] = "FIXED"
        # Convert enum values to strings for comparison
        for g in actual["gaps"]:
            sev = g["severity"]
            g["severity"] = sev.value if hasattr(sev, "value") else sev
        expected = json.loads((FIXTURES / "expected" / f"{fixture_name}.pack.json").read_text())
        self.assertEqual(actual["project_name"], expected["project_name"])
        self.assertEqual(len(actual["records_of_resistance"]), len(expected["records_of_resistance"]))
        actual_gap_artifacts = sorted([g["artifact"] for g in actual["gaps"]])
        expected_gap_artifacts = sorted([g["artifact"] for g in expected["gaps"]])
        self.assertEqual(actual_gap_artifacts, expected_gap_artifacts)

    def test_full_snapshot(self):
        self._compare_to_snapshot("full")

    def test_partial_snapshot(self):
        self._compare_to_snapshot("partial")

    def test_minimal_snapshot(self):
        self._compare_to_snapshot("minimal")


class TestProjectFilter(unittest.TestCase):
    """Aggregator must exclude RoRs whose frontmatter `project` doesn't match
    the current project, and must surface them as a warning gap so the student
    knows their work didn't silently disappear.
    """

    def test_mismatched_ror_excluded_and_surfaced(self):
        import tempfile
        import shutil
        from pathlib import Path
        from esf_pack.aggregate import aggregate_from_dir

        src = FIXTURES / "full"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            # Insert a misfiled RoR — frontmatter says project=other-project
            misfiled = tmp / "ws" / "esf" / "test-course" / "records-of-resistance" / "99-misfiled.md"
            misfiled.write_text(
                "---\n"
                "type: record-of-resistance\n"
                "context: test-course\n"
                "project: other-project\n"
                "date: 2026-05-19\n"
                "record-number: 99\n"
                "---\n\n"
                "## What AI Suggested\n\n> Something.\n\n"
                "## Why I Rejected or Revised It\n\n> Reason.\n\n"
                "## What I Did Instead\n\n> Alternative.\n",
                encoding="utf-8",
            )
            pack = aggregate_from_dir(tmp / "ws")

        # The misfiled RoR should be excluded from records_of_resistance
        self.assertEqual(
            len(pack.records_of_resistance), 5,
            "expected 5 matching RoRs (original full fixture), misfiled one excluded",
        )
        self.assertNotIn(99, [r.record_number for r in pack.records_of_resistance])

        # A warning gap should describe the mismatch
        mismatch_gaps = [
            g for g in pack.gaps
            if g.artifact == "record_of_resistance" and "different `project` frontmatter" in g.message
        ]
        self.assertEqual(len(mismatch_gaps), 1)
        self.assertIn("99-misfiled.md", mismatch_gaps[0].message)
        self.assertIn("other-project", mismatch_gaps[0].message)


if __name__ == "__main__":
    unittest.main()
