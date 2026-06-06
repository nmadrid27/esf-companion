import unittest
from esf_pack.schema import (
    DefensePack, PositionStatement, RecordOfResistance, GapSeverity,
)
from esf_pack.gaps import detect_gaps, has_hard_stop


def _pack(**overrides):
    base = dict(
        project_name="p", context="c", student_name="t", scaffolding_level="Independent",
        phase_at_export="Reflect", export_timestamp="2026-05-20T000000Z",
        companion_version="0.8.0",
        position_statement=PositionStatement(
            stance="x", what_matters_most="y", non_negotiables="z",
            drift_level=None, drift_what_shifted=None, drift_was_user_decision=None,
        ),
        records_of_resistance=[],
        key_decisions=[],
        ai_use_log=None,
        reflection=None,
        disclosure=None,
        evolution_log_entries=[],
        narrative=None,
        gaps=[],
    )
    base.update(overrides)
    return DefensePack(**base)


class TestGapDetection(unittest.TestCase):
    def test_no_rors_warns(self):
        pack = _pack()
        gaps = detect_gaps(pack)
        artifacts = [g.artifact for g in gaps]
        self.assertIn("record_of_resistance", artifacts)
        ror_gap = next(g for g in gaps if g.artifact == "record_of_resistance")
        self.assertEqual(ror_gap.severity, GapSeverity.WARNING)

    def test_missing_ai_use_log_warns(self):
        pack = _pack()
        gaps = detect_gaps(pack)
        self.assertTrue(any(g.artifact == "ai_use_log" and g.severity == GapSeverity.WARNING for g in gaps))

    def test_missing_reflection_warns(self):
        pack = _pack()
        gaps = detect_gaps(pack)
        self.assertTrue(any(g.artifact == "reflection" and g.severity == GapSeverity.WARNING for g in gaps))

    def test_missing_disclosure_is_info(self):
        pack = _pack()
        gaps = detect_gaps(pack)
        self.assertTrue(any(g.artifact == "disclosure" and g.severity == GapSeverity.INFO for g in gaps))

    def test_empty_position_stance_is_hard_stop(self):
        ps = PositionStatement(
            stance="", what_matters_most="", non_negotiables="",
            drift_level=None, drift_what_shifted=None, drift_was_user_decision=None,
        )
        pack = _pack(position_statement=ps)
        gaps = detect_gaps(pack)
        self.assertTrue(any(g.artifact == "position_statement" and g.severity == GapSeverity.HARD_STOP for g in gaps))
        self.assertTrue(has_hard_stop(gaps))

    def test_full_pack_no_warnings(self):
        ror = RecordOfResistance(
            record_number=1, date="2026-05-01",
            ai_suggested="x", why_rejected="y", what_i_did_instead="z",
        )
        pack = _pack(
            records_of_resistance=[ror],
            ai_use_log="present_stub",  # gap detector checks truthiness, not type
            reflection="present_stub",
            disclosure="present_stub",
        )
        gaps = detect_gaps(pack)
        warnings = [g for g in gaps if g.severity == GapSeverity.WARNING]
        self.assertEqual(warnings, [])


from esf_pack.schema import BriefRequirements


class TestCountAwareGaps(unittest.TestCase):
    def _rors(self, n):
        from esf_pack.schema import RecordOfResistance
        return [RecordOfResistance(i, "2026-01-01", "a", "b", "c") for i in range(1, n + 1)]

    def test_below_minimum_warns_with_count(self):
        pack = _pack(records_of_resistance=self._rors(1))
        gaps = detect_gaps(pack, BriefRequirements(ror_minimum=3))
        ror = [g for g in gaps if g.artifact == "record_of_resistance"]
        self.assertEqual(len(ror), 1)
        self.assertEqual(ror[0].severity, GapSeverity.WARNING)
        self.assertIn("1 of 3", ror[0].message)

    def test_zero_with_minimum_replaces_generic(self):
        pack = _pack(records_of_resistance=[])
        gaps = detect_gaps(pack, BriefRequirements(ror_minimum=3))
        ror = [g for g in gaps if g.artifact == "record_of_resistance"]
        self.assertEqual(len(ror), 1)
        self.assertIn("0 of 3", ror[0].message)
        self.assertNotIn("No Records of Resistance found", ror[0].message)

    def test_at_or_above_minimum_no_gap(self):
        pack = _pack(records_of_resistance=self._rors(3))
        gaps = detect_gaps(pack, BriefRequirements(ror_minimum=3))
        self.assertEqual([g for g in gaps if g.artifact == "record_of_resistance"], [])

    def test_no_requirements_one_arg_unchanged(self):
        pack = _pack(records_of_resistance=[])
        gaps = detect_gaps(pack)  # one-arg call must still work
        ror = [g for g in gaps if g.artifact == "record_of_resistance"]
        self.assertEqual(len(ror), 1)
        self.assertIn("No Records of Resistance found", ror[0].message)


if __name__ == "__main__":
    unittest.main()
