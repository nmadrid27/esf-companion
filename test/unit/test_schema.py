import unittest
from dataclasses import asdict
from esf_pack.schema import DefensePack, PositionStatement, RecordOfResistance, Gap, GapSeverity


class TestSchema(unittest.TestCase):
    def test_defensepack_round_trips_to_dict(self):
        pack = DefensePack(
            project_name="test-project",
            context="test-course",
            student_name="Test Student",
            scaffolding_level="Independent",
            phase_at_export="Reflect",
            export_timestamp="2026-05-20T12:00:00Z",
            companion_version="0.8.0",
            position_statement=PositionStatement(
                stance="My stance",
                what_matters_most="What matters",
                non_negotiables="Non-negotiables",
                drift_level=None,
                drift_what_shifted=None,
                drift_was_user_decision=None,
            ),
            records_of_resistance=[
                RecordOfResistance(
                    record_number=1,
                    date="2026-05-01",
                    ai_suggested="x",
                    why_rejected="y",
                    what_i_did_instead="z",
                )
            ],
            key_decisions=[],
            ai_use_log=None,
            reflection=None,
            disclosure=None,
            evolution_log_entries=[],
            narrative=None,
            gaps=[Gap(artifact="reflection", severity=GapSeverity.WARNING, message="missing")],
        )
        d = asdict(pack)
        self.assertEqual(d["project_name"], "test-project")
        self.assertEqual(len(d["records_of_resistance"]), 1)
        self.assertEqual(d["gaps"][0]["artifact"], "reflection")


if __name__ == "__main__":
    unittest.main()
