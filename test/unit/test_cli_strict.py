"""--strict makes the CLIs exit non-zero when the pack has a HARD_STOP gap.

Regression guard for #30: aggregate.py and render.py always exited 0, so an
automated/CI caller could not detect that the produced pack was non-defensible
(e.g. a missing Position Statement). Default behavior is unchanged; --strict
opts into the non-zero exit.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "esf-defense-pack" / "bin"
AGGREGATE = BIN / "aggregate.py"
RENDER = BIN / "render.py"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "defense-pack"


def _run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def _hard_stop_workspace(tmp: Path) -> Path:
    # A project logged in companion-state but NO Position Statement -> HARD_STOP.
    (tmp / "companion-state.md").write_text(
        "# State\n## Current Project\n"
        "- **Context:** test-course\n"
        "- **Project name:** ghost-project\n",
        encoding="utf-8",
    )
    return tmp


class TestAggregateStrict(unittest.TestCase):
    def test_strict_exits_nonzero_on_hard_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _hard_stop_workspace(Path(tmp))
            r = _run(AGGREGATE, ws, "--strict", "--out", ws / "pack.json")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_default_exits_zero_on_hard_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _hard_stop_workspace(Path(tmp))
            r = _run(AGGREGATE, ws, "--out", ws / "pack.json")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_strict_exits_zero_when_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "pack.json"
            r = _run(AGGREGATE, FIXTURES / "full", "--strict", "--out", out)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


def _hard_stop_pack(tmp: Path):
    pack = {
        "project_name": "ghost", "context": "test-course", "student_name": "",
        "scaffolding_level": "Independent", "phase_at_export": "Reflect",
        "export_timestamp": "2026-05-20T120000Z", "companion_version": "0.9.1",
        "schema_version": "1.0",
        "position_statement": None, "records_of_resistance": [], "key_decisions": [],
        "ai_use_log": None, "reflection": None, "disclosure": None,
        "evolution_log_entries": [], "narrative": None,
        "gaps": [{"artifact": "position_statement", "severity": "hard_stop",
                  "message": "Position Statement is empty or incomplete."}],
    }
    pj = tmp / "pack.json"
    pj.write_text(json.dumps(pack), encoding="utf-8")
    nar = tmp / "narrative.md"
    nar.write_text("## How I came in\n\n> x\n", encoding="utf-8")
    return pj, nar


class TestRenderStrict(unittest.TestCase):
    def test_strict_exits_nonzero_on_hard_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            pj, nar = _hard_stop_pack(Path(tmp))
            r = _run(RENDER, pj, nar, "--out-dir", Path(tmp) / "out", "--strict")
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_default_exits_zero_on_hard_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            pj, nar = _hard_stop_pack(Path(tmp))
            r = _run(RENDER, pj, nar, "--out-dir", Path(tmp) / "out")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
