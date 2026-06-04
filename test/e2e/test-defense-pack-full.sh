#!/usr/bin/env bash
# E2E test: run aggregator + renderer against the full fixture, verify outputs.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FIXTURE="$ROOT/test/fixtures/defense-pack/full"
WORKDIR="$(mktemp -d -t esf-defense-pack-e2e-XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT

cp -R "$FIXTURE/." "$WORKDIR/"

"$ROOT/.claude/skills/esf-defense-pack/bin/aggregate.py" "$WORKDIR" --out "$WORKDIR/pack.json"

python3 - <<PY
import json
p = json.load(open("$WORKDIR/pack.json"))
assert p["project_name"] == "responsive-system", p["project_name"]
assert p["context"] == "test-course"
assert len(p["records_of_resistance"]) == 5
assert not any(g["severity"] == "hard_stop" for g in p["gaps"]), p["gaps"]
print("aggregate.py: OK")
PY

cat > "$WORKDIR/narrative.md" <<'EOF'
# Defense: responsive-system

## How I came in
Friction not flow.

## What I set out to protect
Aesthetic resistance.

## The key decisions

### Decision #1
On the grid: I rejected the 12-column proposal.

### Decision #3
On hover: I rejected feel-good states.

## How my position held (or shifted)
Minor drift, owned.

## What I'd defend if asked
Every choice maps to my stance.

## Disclosure
This work was produced with AI assistance.
EOF

"$ROOT/.claude/skills/esf-defense-pack/bin/render.py" "$WORKDIR/pack.json" "$WORKDIR/narrative.md" --out-dir "$WORKDIR/out"

test -f "$WORKDIR/out/defense-pack.html" || { echo "FAIL: no HTML"; exit 1; }
test -f "$WORKDIR/out/defense-pack.md" || { echo "FAIL: no MD"; exit 1; }
grep -q "responsive-system" "$WORKDIR/out/defense-pack.html" || { echo "FAIL: HTML missing project name"; exit 1; }
grep -q '\[~' "$WORKDIR/out/defense-pack.md" || { echo "FAIL: MD missing timing cues"; exit 1; }

if [ -f "$WORKDIR/out/defense-pack.pdf" ]; then
    test -s "$WORKDIR/out/defense-pack.pdf" || { echo "FAIL: PDF empty"; exit 1; }
    head -c 4 "$WORKDIR/out/defense-pack.pdf" | grep -q "%PDF" || { echo "FAIL: PDF magic bytes wrong"; exit 1; }
    echo "render.py: OK (HTML + MD + PDF)"
else
    echo "render.py: OK (HTML + MD; PDF skipped, weasyprint not installed)"
fi
echo "PASS: e2e full fixture"
