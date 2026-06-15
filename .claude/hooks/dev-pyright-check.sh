#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion maintainer dev hook — Pyright type check on Python edits.
#
# PostToolUse hook. Fires after a Write/Edit/MultiEdit. If the edited file is
# a Python source file under the repo (Defense Pack tooling or tests), runs
# Pyright on it using the repo's pyrightconfig.json. Reports type errors so
# they surface at edit time.
#
# Optional / fail-open: if pyright is not installed, the hook exits silently.
# This keeps it from bothering contributors who do not have pyright, while
# still helping maintainers who do. Remove it from settings.json if unwanted.
#
# Maintainer-only: install.sh fetches hooks by explicit name, so this file
# is never shipped to end users.
#
# Contract: reads the PostToolUse JSON payload on stdin, extracts
# .tool_input.file_path. Exit 2 (errors on stderr) when Pyright reports type
# errors, so Claude sees them. Exit 0 otherwise (fail-open).

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"

# Fail-open if pyright is not available.
command -v pyright >/dev/null 2>&1 || exit 0

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

# Only Python sources, and skip virtualenvs and caches.
case "$FILE_PATH" in
  *.py) ;;
  *) exit 0 ;;
esac
case "$FILE_PATH" in
  */.venv*|*/__pycache__/*) exit 0 ;;
esac

# Only files inside this repo (pyrightconfig.json lives at the repo root).
case "$FILE_PATH" in
  "$PROJECT_DIR"/*) ;;
  *) exit 0 ;;
esac

# Run from the repo root so pyrightconfig.json (extraPaths, pythonVersion)
# applies. Pyright exits non-zero when it reports errors.
OUTPUT="$(cd "$PROJECT_DIR" && pyright --outputjson "$FILE_PATH" 2>/dev/null)"

ERROR_COUNT="$(printf '%s' "$OUTPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get("summary", {}).get("errorCount", 0))
except Exception:
    print(0)
' 2>/dev/null)"

if [ "${ERROR_COUNT:-0}" -gt 0 ] 2>/dev/null; then
  SUMMARY="$(printf '%s' "$OUTPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for d in data.get("generalDiagnostics", []):
    if d.get("severity") != "error":
        continue
    rng = d.get("range", {}).get("start", {})
    line = rng.get("line", 0) + 1
    col = rng.get("character", 0) + 1
    print(f"  {d.get(\"file\",\"\")}:{line}:{col}  {d.get(\"message\",\"\").splitlines()[0]}")
' 2>/dev/null)"
  {
    echo "Pyright reported $ERROR_COUNT type error(s) in:"
    echo "  $FILE_PATH"
    echo ""
    [ -n "$SUMMARY" ] && echo "$SUMMARY"
  } >&2
  exit 2
fi

exit 0
