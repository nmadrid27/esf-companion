#!/usr/bin/env bash
# Partial fixture: aggregator succeeds with warnings; render still works.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORKDIR="$(mktemp -d -t esf-defense-pack-partial-XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT
cp -R "$ROOT/test/fixtures/defense-pack/partial/." "$WORKDIR/"

"$ROOT/.claude/skills/esf-defense-pack/bin/aggregate.py" "$WORKDIR" --out "$WORKDIR/pack.json"

python3 - <<PY
import json
p = json.load(open("$WORKDIR/pack.json"))
warnings = sorted({g["artifact"] for g in p["gaps"] if g["severity"] == "warning"})
assert "ai_use_log" in warnings, warnings
assert "reflection" in warnings, warnings
assert not any(g["severity"] == "hard_stop" for g in p["gaps"])
print("partial aggregate: OK (warnings:", warnings, ")")
PY

cat > "$WORKDIR/narrative.md" <<'EOF'
# Defense: partial-project
## How I came in
x
## What I set out to protect
y
## The key decisions
### Decision #1
z
## How my position held
ok
## What I'd defend if asked
ok
## Disclosure
ok
EOF

"$ROOT/.claude/skills/esf-defense-pack/bin/render.py" "$WORKDIR/pack.json" "$WORKDIR/narrative.md" --out-dir "$WORKDIR/out"
grep -q "Gaps in this pack" "$WORKDIR/out/defense-pack.html" || { echo "FAIL: gaps not surfaced in HTML"; exit 1; }
echo "PASS: e2e partial fixture (gaps visible in HTML)"
