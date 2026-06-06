#!/usr/bin/env bash
# Hermetic tests for esf-update-check.sh. No network (ESF_UPDATE_LATEST seam).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$HERE/../.claude/hooks/esf-update-check.sh"
PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); }
bad()  { FAIL=$((FAIL+1)); echo "FAIL: $1"; }
check(){ if eval "$2"; then ok; else bad "$1"; fi; }

newtmp() { mktemp -d "${TMPDIR:-/tmp}/esfupd.XXXXXX"; }

# --- resolve: prints local + latest, validates injected tag ---
T=$(newtmp); echo "companion-v0.9.1" > "$T/esf-version"
out=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
      ESF_UPDATE_LATEST="companion-v0.10.0" bash "$HELPER" resolve)
check "resolve prints local"  '[[ "$out" == *"local=companion-v0.9.1"* ]]'
check "resolve prints latest" '[[ "$out" == *"latest=companion-v0.10.0"* ]]'

# --- invalid injected tag is rejected (no latest emitted) ---
out=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
      ESF_UPDATE_LATEST="cowork-v1.0.0" bash "$HELPER" resolve)
check "invalid latter rejected" '[[ "$out" != *"latest=cowork"* ]]'

# --- exit code is always 0 (fail-open) ---
ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/nope" bash "$HELPER" resolve >/dev/null 2>&1
check "resolve exits 0 even with missing version file" '[ $? -eq 0 ]'

rm -rf "$T"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
