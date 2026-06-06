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


if __name__ == "__main__":
    unittest.main()
