#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion maintainer dev hook — shell syntax check on edit.
#
# PostToolUse hook. Fires after a Write/Edit/MultiEdit. If the edited file is
# a shell script, runs `bash -n` (parse-only, no execution) so syntax errors
# in install.sh (~50K of bash) and the release/test scripts surface at edit
# time. If shellcheck is installed, its findings are reported as advisory.
#
# Maintainer-only: install.sh fetches hooks by explicit name, so this file
# is never shipped to end users.
#
# Contract: reads the PostToolUse JSON payload on stdin, extracts
# .tool_input.file_path. Exit 2 (with the error on stderr) on a `bash -n`
# syntax error, so Claude sees it and fixes it. Exit 0 otherwise (fail-open);
# shellcheck findings are informational and never block.

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

# Only react to shell scripts. Match the .sh extension or a bash/sh shebang.
case "$FILE_PATH" in
  *.sh) ;;
  *)
    head -1 "$FILE_PATH" 2>/dev/null | grep -qE '^#!.*\b(bash|sh)\b' || exit 0
    ;;
esac

ERR="$(bash -n "$FILE_PATH" 2>&1)"
if [ -n "$ERR" ]; then
  {
    echo "Shell syntax error (bash -n) in:"
    echo "  $FILE_PATH"
    echo ""
    echo "$ERR"
  } >&2
  exit 2
fi

# Advisory: shellcheck if available. Non-blocking — exit 0 regardless.
if command -v shellcheck >/dev/null 2>&1; then
  SC="$(shellcheck -S warning "$FILE_PATH" 2>&1)"
  if [ -n "$SC" ]; then
    {
      echo "shellcheck advisory for $FILE_PATH (non-blocking):"
      echo "$SC"
    } >&2
  fi
fi

exit 0
