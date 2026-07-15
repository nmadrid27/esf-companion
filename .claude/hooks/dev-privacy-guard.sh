#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion maintainer dev hook: privacy guard.
#
# PostToolUse hook. Fires after a Write/Edit/MultiEdit. Scans the edited file
# for personal/institutional/student identifiers that must not appear in this
# PUBLIC repo (SCAD, scad.edu, real home paths, student names, ai-os, SCAD
# course codes). Catches re-introduction at edit time instead of in CI/review.
#
# Maintainer-only: install.sh fetches hooks by explicit name, so this file is
# never shipped to end users.
#
# Contract: reads the PostToolUse JSON payload on stdin and extracts
# .tool_input.file_path. Exit 0 when clean or not applicable (fail-open).
# Exit 2 (with guidance on stderr) when a forbidden identifier is found, so
# Claude sees it and fixes it.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
SCANNER="$PROJECT_DIR/test/check-privacy.py"

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
[ -f "$FILE_PATH" ] || exit 0
[ -f "$SCANNER" ] || exit 0

# Only scan files that could actually be committed to THIS repo. A file outside
# the repo tree (e.g. a ~/.claude memory note) can't leak into it, and a
# gitignored file (local-only) never reaches the public remote.
case "$FILE_PATH" in
  "$PROJECT_DIR"/*) ;;
  *) exit 0 ;;
esac
git -C "$PROJECT_DIR" check-ignore -q "$FILE_PATH" 2>/dev/null && exit 0

OUTPUT="$(python3 "$SCANNER" --file "$FILE_PATH" 2>&1)"
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  {
    echo "$OUTPUT"
    echo ""
    echo "This repo is public; the identifier above must not be committed."
  } >&2
  exit 2
fi

exit 0
