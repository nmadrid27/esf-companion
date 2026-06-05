import json
import unittest
from dataclasses import asdict, fields
from esf_pack.schema import DefensePack, PositionStatement, RecordOfResistance, Gap, GapSeverity


def _sample_pack(**overrides) -> DefensePack:
    base = dict(
        project_name="test-project",
        context="test-course",
        student_name="Test Student",
        scaffolding_level="Independent",
        phase_at_export="Reflect",
        export_timestamp="2026-05-20T120000Z",
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
    base.update(overrides)
    return DefensePack(**base)


class TestSchema(unittest.TestCase):
    def test_defensepack_round_trips_to_dict(self):
        pack = _sample_pack()
        d = asdict(pack)
        self.assertEqual(d["project_name"], "test-project")
        self.assertEqual(len(d["records_of_resistance"]), 1)
        self.assertEqual(d["gaps"][0]["artifact"], "reflection")


class TestSchemaVersion(unittest.TestCase):
    """`schema_version` is the contract field readers use to know which shape
    they're parsing. It must survive the asdict -> json.dumps -> json.loads
    round trip used by the renderer when loading pack.json.
    """

    def test_default_schema_version_is_1_0(self):
        pack = _sample_pack()
        self.assertEqual(pack.schema_version, "1.0")

    def test_schema_version_present_in_asdict(self):
        d = asdict(_sample_pack())
        self.assertIn("schema_version", d)
        self.assertEqual(d["schema_version"], "1.0")

    def test_schema_version_survives_json_round_trip(self):
        original = _sample_pack()
        serialized = json.dumps(asdict(original))
        revived = json.loads(serialized)
        self.assertEqual(revived["schema_version"], "1.0")

    def test_default_applies_when_field_absent(self):
        # Older packs predate `schema_version`; constructing without it should
        # fall back to the dataclass default rather than crashing.
        rebuilt = _sample_pack()
        # The field is on the dataclass so absence in input data is handled by
        # the default factory; verify the field is declared, not just present
        # on the instance.
        field_names = {f.name for f in fields(DefensePack)}
        self.assertIn("schema_version", field_names)
        self.assertEqual(rebuilt.schema_version, "1.0")


if __name__ == "__main__":
    unittest.main()
