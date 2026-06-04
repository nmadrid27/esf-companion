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


class TestPathSegmentValidation(unittest.TestCase):
    """companion-state.md isn't schema-enforced; reject obviously-unsafe path
    segments to prevent traversal even though execution is local-only.
    """

    def _ws_with_state(self, state_text: str):
        import tempfile
        from pathlib import Path
        tmp = Path(tempfile.mkdtemp(prefix="esf-agg-test-"))
        (tmp / "companion-state.md").write_text(state_text, encoding="utf-8")
        return tmp

    def test_traversal_in_context_rejected(self):
        from esf_pack.aggregate import aggregate_from_dir
        ws = self._ws_with_state(
            "# State\n## Current Project\n"
            "- **Context:** ../etc\n"
            "- **Project name:** x\n"
        )
        with self.assertRaises(ValueError) as ctx:
            aggregate_from_dir(ws)
        self.assertIn("Context", str(ctx.exception))

    def test_empty_state_raises_hard(self):
        from esf_pack.aggregate import aggregate_from_dir
        ws = self._ws_with_state("# Heading only with no bullets\n")
        with self.assertRaises(ValueError) as ctx:
            aggregate_from_dir(ws)
        self.assertIn("companion-state.md", str(ctx.exception))


class TestDuplicateRecordNumbers(unittest.TestCase):
    """Two RoRs sharing the same record-number must surface as a warning gap."""

    def test_duplicate_numbers_warned(self):
        import tempfile
        import shutil
        from pathlib import Path
        from esf_pack.aggregate import aggregate_from_dir
        src = FIXTURES / "full"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            # Add an RoR with record-number 1 (collides with existing #1)
            dup = tmp / "ws" / "esf" / "test-course" / "records-of-resistance" / "1b-duplicate.md"
            dup.write_text(
                "---\ntype: record-of-resistance\ncontext: test-course\n"
                "project: responsive-system\ndate: 2026-05-19\n"
                "record-number: 1\n---\n\n"
                "## What AI Suggested\n\n> x\n\n"
                "## Why I Rejected or Revised It\n\n> y\n\n"
                "## What I Did Instead\n\n> z\n",
                encoding="utf-8",
            )
            pack = aggregate_from_dir(tmp / "ws")
        dup_gaps = [g for g in pack.gaps if "Duplicate Record" in g.message]
        self.assertEqual(len(dup_gaps), 1)
        self.assertIn("#1", dup_gaps[0].message)


class TestZeroRoRDisclosure(unittest.TestCase):
    """Auto-disclosure must read naturally when zero RoRs are included."""

    def test_zero_rors_phrased_naturally(self):
        import tempfile
        import shutil
        from pathlib import Path
        from esf_pack.aggregate import aggregate_from_dir
        src = FIXTURES / "minimal"  # has PS, no RoRs
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            pack = aggregate_from_dir(tmp / "ws")
        self.assertIsNotNone(pack.disclosure)
        self.assertNotIn("0 Records of Resistance", pack.disclosure.text)
        self.assertIn("No Records of Resistance", pack.disclosure.text)


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


class TestCycleBasedLayout(unittest.TestCase):
    """Workspaces organized by milestone/cycle directories (CJ Snyder layout, issue #25).

    Artifacts live at the top of cycle dirs (`p2-break-through/`, `p3-next-steps/`)
    instead of under `records-of-resistance/`. The aggregator must auto-discover
    them without an explicit `## Defense Pack Paths` override.
    """

    def test_position_statement_discovered_in_cycle_dir(self):
        pack = aggregate_from_dir(FIXTURES / "cycle-based")
        self.assertIsNotNone(pack.position_statement)
        self.assertTrue(pack.position_statement.stance.startswith("I want my work"))

    def test_records_aggregated_across_multiple_cycle_dirs(self):
        pack = aggregate_from_dir(FIXTURES / "cycle-based")
        # 4 RoRs: 1 in p2-break-through/, 3 in p3-next-steps/
        self.assertEqual(len(pack.records_of_resistance), 4)
        numbers = [r.record_number for r in pack.records_of_resistance]
        self.assertEqual(numbers, [1, 2, 3, 4])
        # Sources should reflect the cycle dirs they came from
        sources = [r.source for r in pack.records_of_resistance]
        self.assertTrue(any("p2-break-through" in s for s in sources))
        self.assertTrue(any("p3-next-steps" in s for s in sources))

    def test_templates_dir_excluded_from_cycle_scan(self):
        pack = aggregate_from_dir(FIXTURES / "cycle-based")
        # The fixture has templates/record-of-resistance-template.md which must
        # NOT appear in the pack (template, not a record).
        sources = [r.source or "" for r in pack.records_of_resistance]
        self.assertFalse(any("templates/" in s for s in sources))
        self.assertFalse(any("template" in s.lower() for s in sources))

    def test_auto_discovery_surfaces_info_gap(self):
        pack = aggregate_from_dir(FIXTURES / "cycle-based")
        layout_gaps = [g for g in pack.gaps if g.artifact == "workspace_layout"]
        self.assertEqual(len(layout_gaps), 1)
        self.assertEqual(layout_gaps[0].severity.value, "info")
        # Message should name the discovered dirs and mention the override path
        self.assertIn("p2-break-through", layout_gaps[0].message)
        self.assertIn("p3-next-steps", layout_gaps[0].message)
        self.assertIn("Defense Pack Paths", layout_gaps[0].message)

    def test_explicit_override_suppresses_cycle_discovery(self):
        """When the user declares `## Defense Pack Paths`, the cycle-based
        fallback must NOT fire — the INFO gap is the test signal.
        """
        import tempfile
        import shutil
        from pathlib import Path

        src = FIXTURES / "cycle-based"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            # Override RoR + PS dirs explicitly. p2-break-through has exactly
            # one record so the count is unambiguous.
            state = (tmp / "ws" / "companion-state.md").read_text(encoding="utf-8")
            state += (
                "\n## Defense Pack Paths\n"
                "- **Records of Resistance:** p2-break-through\n"
                "- **Position Statement:** p3-next-steps/position-statement.md\n"
            )
            (tmp / "ws" / "companion-state.md").write_text(state, encoding="utf-8")
            pack = aggregate_from_dir(tmp / "ws")

        # Override scoped to p2-break-through → only the one RoR there
        self.assertEqual(len(pack.records_of_resistance), 1)
        self.assertEqual(pack.records_of_resistance[0].record_number, 1)
        # No workspace_layout INFO gap — override means no auto-discovery happened
        layout_gaps = [g for g in pack.gaps if g.artifact == "workspace_layout"]
        self.assertEqual(layout_gaps, [])

    def test_reflection_discovered_in_cycle_dir(self):
        """Regression: the cycle-pattern filter must not drop `*reflection*.md`.

        Reflection has only one glob fallback; an over-eager filter once
        excluded it, making Reflections in cycle layouts undiscoverable while
        PS and RoRs were found.
        """
        import tempfile
        import shutil
        from pathlib import Path

        src = FIXTURES / "cycle-based"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            (tmp / "ws" / "p3-next-steps" / "reflection.md").write_text(
                "---\ntype: reflection\nproject: P1-cycle-project\n"
                "context: AI180\n---\n\n# Reflection\n\n"
                "End-of-project synthesis of what was kept, revised, rejected.\n",
                encoding="utf-8",
            )
            pack = aggregate_from_dir(tmp / "ws")

        self.assertIsNotNone(
            pack.reflection,
            "reflection.md in a cycle dir must be auto-discovered",
        )
        reflection_gaps = [g for g in pack.gaps if g.artifact == "reflection"]
        self.assertEqual(
            reflection_gaps, [],
            "no 'missing reflection' gap when a reflection exists in a cycle dir",
        )

    def test_single_cycle_dir_does_not_slurp_non_records(self):
        """Regression: a layout with exactly ONE cycle dir must still use the
        strict record glob, not `*.md`.

        A `len(ror_dirs) > 1` proxy once caused single-cycle-dir workspaces to
        glob `*.md`, pulling position-statement.md / reflection.md into the RoR
        list as phantom records.
        """
        import tempfile
        import shutil
        from pathlib import Path

        src = FIXTURES / "cycle-based"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            # Collapse to a single cycle dir: p3-next-steps holds the PS plus
            # records 02-04. p2 is removed.
            shutil.rmtree(tmp / "ws" / "p2-break-through")
            pack = aggregate_from_dir(tmp / "ws")

        sources = [r.source or "" for r in pack.records_of_resistance]
        self.assertFalse(
            any("position-statement" in s or "reflection" in s for s in sources),
            f"non-record markdown leaked into RoR list: {sources}",
        )
        # Only the three record-of-resistance-*.md files in p3-next-steps
        self.assertEqual(len(pack.records_of_resistance), 3)


class TestHybridMigrationLayout(unittest.TestCase):
    """A workspace mid-migration may have BOTH `esf/<ctx>/records-of-resistance/`
    and `projects/<ctx>/records-of-resistance/` on disk. Both are dedicated RoR
    dirs (not cycle dirs), so the permissive `*.md` glob must still apply —
    records using canonical filenames like `1-grid-rejection.md` must not be
    dropped just because two RoR dirs coexist.
    """

    def test_canonical_records_kept_when_legacy_dir_also_exists(self):
        import tempfile
        import shutil
        from pathlib import Path

        src = FIXTURES / "full"  # 5 records under esf/test-course/records-of-resistance
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shutil.copytree(src, tmp / "ws")
            # Create an (empty) legacy RoR dir so two dirs resolve.
            (tmp / "ws" / "projects" / "test-course" / "records-of-resistance").mkdir(parents=True)
            pack = aggregate_from_dir(tmp / "ws")

        self.assertEqual(
            len(pack.records_of_resistance), 5,
            "canonical records must survive when a legacy RoR dir also exists",
        )
        # This is not a cycle layout — no workspace_layout gap.
        layout_gaps = [g for g in pack.gaps if g.artifact == "workspace_layout"]
        self.assertEqual(layout_gaps, [])


class TestCanonicalLayoutSilentOnCycles(unittest.TestCase):
    """Canonical-layout fixtures must NOT emit a cycle-layout INFO gap. Regression
    guard: cycle discovery should only fire when canonical paths are absent.
    """

    def test_full_fixture_no_cycle_gap(self):
        pack = aggregate_from_dir(FIXTURES / "full")
        layout_gaps = [g for g in pack.gaps if g.artifact == "workspace_layout"]
        self.assertEqual(layout_gaps, [])


class TestExportTimestampShape(unittest.TestCase):
    """export_timestamp must match the SKILL.md folder convention
    `date -u +%Y-%m-%dT%H%M%SZ` (compact, no colons in the time portion) so the
    pack.json field and its containing folder name are visibly the same shape.
    """

    def test_export_timestamp_is_compact_utc(self):
        import re as _re
        pack = aggregate_from_dir(FIXTURES / "full")
        self.assertRegex(
            pack.export_timestamp,
            _re.compile(r"^\d{4}-\d{2}-\d{2}T\d{6}Z$"),
            f"export_timestamp {pack.export_timestamp!r} should be compact UTC "
            f"(`YYYY-MM-DDTHHMMSSZ`, no colons in time)",
        )


if __name__ == "__main__":
    unittest.main()
