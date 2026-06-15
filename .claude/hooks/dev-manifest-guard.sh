#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion maintainer dev hook — Defense Pack MANIFEST drift guard.
#
# PostToolUse hook. Fires after a Write/Edit/MultiEdit. If the edited file
# lives under the Defense Pack bin/ or render/ tree, re-runs the manifest
# guard so MANIFEST.txt drift is caught at edit time instead of in CI.
# install.sh fetches every Defense Pack file listed in MANIFEST.txt; a new
# module that is not listed ships a broken skill on the next release.
#
# Maintainer-only: install.sh fetches hooks by explicit name, so this file
# is never shipped to end users.
#
# Contract: reads the PostToolUse JSON payload on stdin and extracts
# .tool_input.file_path. Exit 0 when in sync or not applicable (fail-open).
# Exit 2 (with guidance on stderr) when drift is detected, so Claude sees it
# and updates MANIFEST.txt.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
GUARD="$PROJECT_DIR/test/check-defense-pack-manifest.sh"

# Extract the edited file path from the hook payload. Fail-open on any parse
# error: a hook must never interrupt the session.
FILE_PATH="$(python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("tool_input", {}).get("file_path", ""))
except Exception:
    print("")
' 2>/dev/null)"

[ -z "$FILE_PATH" ] && exit 0

# Only react to changes inside the Defense Pack bin/ or render/ trees.
case "$FILE_PATH" in
  */esf-defense-pack/bin/*|*/esf-defense-pack/render/*) ;;
  *) exit 0 ;;
esac

[ -x "$GUARD" ] || [ -f "$GUARD" ] || exit 0

OUTPUT="$(bash "$GUARD" 2>&1)"
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  {
    echo "Defense Pack MANIFEST.txt is out of sync (detected after editing"
    echo "  $FILE_PATH; the drift may pre-date this change):"
    echo ""
    echo "$OUTPUT"
    echo ""
    echo "Update .claude/skills/esf-defense-pack/MANIFEST.txt so install.sh ships"
    echo "every module, then this guard will pass."
  } >&2
  exit 2
fi

exit 0
