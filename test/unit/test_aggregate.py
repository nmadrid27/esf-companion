import unittest
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


if __name__ == "__main__":
    unittest.main()
