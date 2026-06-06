import unittest
from esf_pack.schema import BriefRequirements
from esf_pack.scan import build_scan_snapshot, gap_report
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


def _snap(scaffolding="Supported", minimum=None, count=2, gaps=None):
    return {
        "schema_version": "1.0", "project_name": "p", "context": "c",
        "phase": "Explore", "scaffolding_level": scaffolding,
        "artifacts": {
            "position_statement": "present",
            "records_of_resistance": {"count": count, "minimum": minimum},
            "ai_use_log": "absent", "reflection": "absent", "disclosure": "present",
        },
        "gaps": gaps or [],
    }


class TestGapReport(unittest.TestCase):
    def test_minimum_line_shows_n_of_m(self):
        out = gap_report(_snap(minimum=3, count=1))
        self.assertIn("1 of 3", out)

    def test_no_minimum_line_has_no_denominator(self):
        out = gap_report(_snap(minimum=None, count=2))
        self.assertIn("Records of Resistance: 2", out)
        self.assertNotIn("of None", out)
        self.assertNotIn("0 required", out)

    def test_zero_gaps_states_complete(self):
        out = gap_report(_snap(gaps=[]))
        self.assertIn("No gaps", out)

    def test_independent_omits_info_keeps_warning(self):
        gaps = [
            {"artifact": "disclosure", "severity": "info", "message": "info gap"},
            {"artifact": "record_of_resistance", "severity": "warning", "message": "warn gap"},
        ]
        out = gap_report(_snap(scaffolding="Independent", gaps=gaps))
        self.assertIn("warn gap", out)
        self.assertNotIn("info gap", out)

    def test_supported_shows_info(self):
        gaps = [{"artifact": "disclosure", "severity": "info", "message": "info gap"}]
        out = gap_report(_snap(scaffolding="Supported", gaps=gaps))
        self.assertIn("info gap", out)

    def test_guided_hints_only_templated_artifacts(self):
        gaps = [
            {"artifact": "record_of_resistance", "severity": "warning", "message": "ror gap"},
            {"artifact": "evolution_log", "severity": "info", "message": "evo gap"},
        ]
        out = gap_report(_snap(scaffolding="Guided", gaps=gaps))
        self.assertIn("(template: esf/toolkit/templates/record-of-resistance-template.md)", out)
        evo_line = [ln for ln in out.splitlines() if "evo gap" in ln][0]
        self.assertNotIn("template", evo_line)


if __name__ == "__main__":
    unittest.main()
