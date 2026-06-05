#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Defense Pack manifest guard.
#
# install.sh fetches every esf-defense-pack file listed in
# .claude/skills/esf-defense-pack/MANIFEST.txt. If someone adds a new
# module under bin/ or render/ but forgets to update the manifest, the
# installer will silently ship a broken skill on the next release.
#
# This script asserts the manifest exactly matches the tracked set of
# files under bin/ and render/ (both directions):
#   1. every file under bin/ and render/ appears in MANIFEST.txt
#   2. every path in MANIFEST.txt exists in the tree (no stale entries)
#
# Usage: bash test/check-defense-pack-manifest.sh
# Exit 0: manifest is in sync.
# Exit 1: manifest drift detected; the diff is printed.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/esf-defense-pack"
MANIFEST="$SKILL_DIR/MANIFEST.txt"

if [ ! -f "$MANIFEST" ]; then
  echo "FAIL: MANIFEST.txt missing at $MANIFEST" >&2
  exit 1
fi

# Actual files in the tree, relative to the skill dir. We exclude __pycache__
# because it is a runtime artifact, not a shipped source file.
ACTUAL="$(mktemp)"
(
  cd "$SKILL_DIR"
  find bin render -type f \
    -not -path '*/__pycache__/*' \
    -not -name '*.pyc' \
    | LC_ALL=C sort
) > "$ACTUAL"

# Manifest entries, with blank lines stripped, sorted for set comparison.
DECLARED="$(mktemp)"
grep -v '^[[:space:]]*$' "$MANIFEST" | LC_ALL=C sort > "$DECLARED"

if diff -u "$DECLARED" "$ACTUAL" > /dev/null; then
  echo "PASS  esf-defense-pack MANIFEST.txt matches bin/ + render/ ($(wc -l < "$DECLARED" | tr -d ' ') files)"
  rm -f "$ACTUAL" "$DECLARED"
  exit 0
fi

echo "FAIL  esf-defense-pack MANIFEST.txt is out of sync with bin/ + render/." >&2
echo "      Update .claude/skills/esf-defense-pack/MANIFEST.txt so install.sh" >&2
echo "      ships every module. Diff (declared vs. actual):" >&2
echo "" >&2
diff -u "$DECLARED" "$ACTUAL" >&2 || true
rm -f "$ACTUAL" "$DECLARED"
exit 1
