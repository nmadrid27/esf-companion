import json, subprocess, sys, tempfile, unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "esf-defense-pack" / "bin"
AGG = BIN / "aggregate.py"


def _ws(tmp: Path) -> Path:
    (tmp / "companion-state.md").write_text(
        "# State\n## Current Project\n"
        "- **Context:** test-course\n- **Project name:** widget\n",
        encoding="utf-8",
    )
    briefs = tmp / "esf" / "test-course" / "briefs"
    briefs.mkdir(parents=True)
    (briefs / "widget-brief.md").write_text(
        "---\nrecords-of-resistance-minimum: 3\n---\n# Brief\n", encoding="utf-8"
    )
    return tmp


class TestScanOnlyPayload(unittest.TestCase):
    def test_snapshot_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = _ws(Path(tmp))
            r = subprocess.run([sys.executable, str(AGG), str(ws), "--scan-only"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertIn("project_name", data)
            self.assertIn("gaps", data)
            self.assertIn("artifacts", data)
            self.assertEqual(data["artifacts"]["records_of_resistance"]["minimum"], 3)

    def test_no_workspace_exits_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(AGG), tmp, "--scan-only"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertEqual(data["error"], "no_workspace")

    def test_scan_only_strict_no_workspace_does_not_crash(self):
        # --scan-only + --strict on a missing workspace must not NameError on the
        # strict check (pack is None on the no-workspace path); exits 0.
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(AGG), tmp, "--scan-only", "--strict"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)["error"], "no_workspace")


if __name__ == "__main__":
    unittest.main()
