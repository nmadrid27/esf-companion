import json
import unittest
from dataclasses import asdict, fields
from esf_pack.schema import (
    DefensePack, PositionStatement, RecordOfResistance, Gap, GapSeverity,
    Narrative, DecisionWalkthroughEntry,
)
from render import _to_dataclass


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

    def test_decision_walkthrough_survives_round_trip(self):
        """A DefensePack with a non-empty decision_walkthrough must survive
        asdict → json.dumps → json.loads → _to_dataclass with .record_number
        and .narration accessible via attribute (not subscript).

        This also guards backwards compatibility: older pack.json files in the
        wild serialized decision_walkthrough as plain dicts; the round-trip
        must read them as DecisionWalkthroughEntry instances.
        """
        pack = DefensePack(
            project_name="test-project",
            context="test-course",
            student_name="Test Student",
            scaffolding_level="Independent",
            phase_at_export="Reflect",
            export_timestamp="2026-05-20T12:00:00Z",
            companion_version="0.8.0",
            position_statement=None,
            records_of_resistance=[],
            key_decisions=[],
            ai_use_log=None,
            reflection=None,
            disclosure=None,
            evolution_log_entries=[],
            narrative=Narrative(
                intro="",
                position_summary="",
                decision_walkthrough=[
                    DecisionWalkthroughEntry(record_number=1, narration="First."),
                    DecisionWalkthroughEntry(record_number=3, narration="Third."),
                ],
                reflection_summary="",
                closing="",
                user_approved=True,
                drafted_at="2026-05-20T12:00:00Z",
            ),
            gaps=[],
        )

        round_tripped = _to_dataclass(DefensePack, json.loads(json.dumps(asdict(pack))))
        assert round_tripped is not None
        assert round_tripped.narrative is not None
        walkthrough = round_tripped.narrative.decision_walkthrough
        self.assertEqual(len(walkthrough), 2)
        # Attribute access, not subscript — the whole point of the dataclass.
        self.assertEqual(walkthrough[0].record_number, 1)
        self.assertEqual(walkthrough[0].narration, "First.")
        self.assertEqual(walkthrough[1].record_number, 3)
        self.assertEqual(walkthrough[1].narration, "Third.")
        self.assertIsInstance(walkthrough[0], DecisionWalkthroughEntry)

    def test_decision_walkthrough_reads_legacy_dict_shape(self):
        """Older pack.json files persist decision_walkthrough as plain dicts.
        The round-trip must tolerate that shape and produce typed entries."""
        legacy_narrative = {
            "intro": "",
            "position_summary": "",
            "decision_walkthrough": [
                {"record_number": 7, "narration": "Legacy entry."},
            ],
            "reflection_summary": "",
            "closing": "",
            "user_approved": True,
            "drafted_at": "",
        }
        narrative = _to_dataclass(Narrative, legacy_narrative)
        assert narrative is not None
        self.assertEqual(len(narrative.decision_walkthrough), 1)
        self.assertIsInstance(narrative.decision_walkthrough[0], DecisionWalkthroughEntry)
        self.assertEqual(narrative.decision_walkthrough[0].record_number, 7)
        self.assertEqual(narrative.decision_walkthrough[0].narration, "Legacy entry.")


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


    def test_round_trip_preserves_every_declared_field(self):
        """asdict() -> pack.json -> _to_dataclass() must not drop any field.

        render.py used to rehydrate DefensePack from a hand-written argument
        list, which silently dropped resist_count, default_count, shift_count,
        and process_blog_sources: a pack recording 147 @resist moments rendered
        as 0. Assert over fields(DefensePack) rather than naming those four, so
        a field added to the schema later is covered without editing this test.
        """
        pack = _sample_pack(
            resist_count=147,
            default_count=22,
            shift_count=9,
            process_blog_sources=["session-01.md", "session-02.md"],
        )
        wire = json.loads(json.dumps(asdict(pack), default=str))
        rebuilt = _to_dataclass(DefensePack, wire)
        self.assertIsNotNone(rebuilt)
        for f in fields(DefensePack):
            self.assertEqual(
                getattr(rebuilt, f.name),
                getattr(pack, f.name),
                f"field {f.name!r} did not survive the pack.json round trip",
            )


if __name__ == "__main__":
    unittest.main()
