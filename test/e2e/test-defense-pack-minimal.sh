#!/usr/bin/env bash
# Minimal fixture: Position Statement only. RoRs absent → warning, not hard stop.
# Also verifies: if the Position Statement is blanked, the aggregator returns a hard_stop gap.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORKDIR="$(mktemp -d -t esf-defense-pack-minimal-XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT
cp -R "$ROOT/test/fixtures/defense-pack/minimal/." "$WORKDIR/"

"$ROOT/.claude/skills/esf-defense-pack/bin/aggregate.py" "$WORKDIR" --out "$WORKDIR/pack.json"
python3 - <<PY
import json
p = json.load(open("$WORKDIR/pack.json"))
warnings = sorted({g["artifact"] for g in p["gaps"] if g["severity"] == "warning"})
assert "record_of_resistance" in warnings, warnings
assert "ai_use_log" in warnings
assert "reflection" in warnings
assert not any(g["severity"] == "hard_stop" for g in p["gaps"])
print("minimal aggregate: OK (warnings:", warnings, ")")
PY

PS_FILE="$WORKDIR/esf/test-course/position-statements/minimal-project.md"
python3 - <<PY
import re, pathlib
p = pathlib.Path("$PS_FILE")
text = p.read_text()
# Wipe the three Element quote contents to empty blockquotes
text = re.sub(r"(## Element \d+:.+?\n\n)>\s*[^\n]+", r"\1>", text)
p.write_text(text)
PY

set +e
"$ROOT/.claude/skills/esf-defense-pack/bin/aggregate.py" "$WORKDIR" --out "$WORKDIR/pack-blanked.json"
rc=$?
set -e
test $rc -eq 0 || { echo "FAIL: aggregator should not crash on empty PS, just report hard_stop"; exit 1; }
python3 - <<PY
import json
p = json.load(open("$WORKDIR/pack-blanked.json"))
hs = [g for g in p["gaps"] if g["severity"] == "hard_stop"]
assert hs, "expected hard_stop gap for empty Position Statement"
assert hs[0]["artifact"] == "position_statement"
print("hard-stop gap: OK")
PY

echo "PASS: e2e minimal fixture (hard-stop gap surfaces correctly)"
