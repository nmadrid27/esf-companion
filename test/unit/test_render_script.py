import unittest
from esf_pack.schema import DefensePack, PositionStatement, RecordOfResistance, Narrative, KeyDecision
from esf_pack.render_script import render_script


def _full_pack():
    return DefensePack(
        project_name="responsive-system",
        context="test-course",
        scaffolding_level="Independent",
        phase_at_export="Reflect",
        export_timestamp="2026-05-20T12:00:00Z",
        companion_version="0.8.0",
        position_statement=PositionStatement(
            stance="X.", what_matters_most="Y.", non_negotiables="Z.",
            drift_level="minor", drift_what_shifted="A.", drift_was_user_decision=True,
        ),
        records_of_resistance=[
            RecordOfResistance(1, "2026-04-20", "grid", "smooth", "off-grid"),
            RecordOfResistance(2, "2026-04-22", "ease", "soft", "snap"),
            RecordOfResistance(3, "2026-04-25", "hover", "fluff", "discrete"),
        ],
        key_decisions=[
            KeyDecision(1, "I rejected the grid", "ai_proposed_user_confirmed"),
            KeyDecision(3, "I rejected hover fluff", "user_selected"),
        ],
        ai_use_log=None,
        reflection=None,
        disclosure=None,
        evolution_log_entries=[],
        narrative=Narrative(
            intro="Intro text.",
            position_summary="Position summary.",
            decision_walkthrough=[
                {"record_number": 1, "narration": "On the grid: I chose off-grid."},
                {"record_number": 3, "narration": "On hover: I chose discrete."},
            ],
            reflection_summary="What I learned.",
            closing="What I'd defend.",
            user_approved=True,
            drafted_at="2026-05-20T12:00:00Z",
        ),
        gaps=[],
    )


class TestRenderScript(unittest.TestCase):
    def test_has_timing_cues(self):
        out = render_script(_full_pack())
        self.assertIn("[~", out)  # timing cue pattern e.g. [~2 min]
        self.assertGreaterEqual(out.count("[~"), 4)  # one per major section

    def test_includes_project_name(self):
        out = render_script(_full_pack())
        self.assertIn("responsive-system", out)

    def test_walks_key_decisions(self):
        out = render_script(_full_pack())
        self.assertIn("off-grid", out)
        self.assertIn("discrete", out)


if __name__ == "__main__":
    unittest.main()
