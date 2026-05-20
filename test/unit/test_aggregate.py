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


if __name__ == "__main__":
    unittest.main()
