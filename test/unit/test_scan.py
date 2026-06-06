import unittest
from esf_pack.schema import BriefRequirements
from esf_pack.scan import build_scan_snapshot
from test.unit.test_render_script import _full_pack


class TestBuildScanSnapshot(unittest.TestCase):
    def test_top_level_additive_fields(self):
        snap = build_scan_snapshot(_full_pack(), BriefRequirements(ror_minimum=3))
        self.assertEqual(snap["project_name"], "responsive-system")
        self.assertIn("gaps", snap)
        self.assertEqual(snap["schema_version"], "1.0")

    def test_records_count_and_minimum(self):
        snap = build_scan_snapshot(_full_pack(), BriefRequirements(ror_minimum=3))
        ror = snap["artifacts"]["records_of_resistance"]
        self.assertEqual(ror["count"], 3)
        self.assertEqual(ror["minimum"], 3)

    def test_minimum_none_without_requirements(self):
        snap = build_scan_snapshot(_full_pack())
        self.assertIsNone(snap["artifacts"]["records_of_resistance"]["minimum"])

    def test_position_statement_present(self):
        snap = build_scan_snapshot(_full_pack())
        self.assertEqual(snap["artifacts"]["position_statement"], "present")


if __name__ == "__main__":
    unittest.main()
