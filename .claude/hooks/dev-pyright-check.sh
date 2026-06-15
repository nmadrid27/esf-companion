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
# Coverage note: pyrightconfig.json currently lists the Defense Pack bin/ tree
# in extraPaths, so pyright treats those files as a library and analyzes none
# of them (filesAnalyzed=0). When that happens this hook prints a transparent
# "not analyzed" note and exits 0 rather than reporting a false clean pass.
# See issue #46. test/ and any other non-extraPaths Python is checked normally.
#
# Maintainer-only: install.sh fetches hooks by explicit name, so this file
# is never shipped to end users.
#
# Contract: reads the PostToolUse JSON payload on stdin, extracts
# .tool_input.file_path. Exit 2 (errors on stderr) when Pyright reports type
# errors in an analyzed file, so Claude sees them. Exit 0 otherwise (fail-open).

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

# Normalize a relative file_path to absolute against the project dir, so the
# repo gate below (anchored on an absolute prefix) matches whether Claude Code
# sent an absolute or a relative path.
case "$FILE_PATH" in
  /*) ;;
  *) FILE_PATH="$PROJECT_DIR/$FILE_PATH" ;;
esac

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
[ -z "$OUTPUT" ] && exit 0   # pyright produced nothing parseable; fail-open

# Read filesAnalyzed and errorCount in one pass ("- -" on a parse failure).
SUMMARY_LINE="$(printf '%s' "$OUTPUT" | python3 -c '
import json, sys
try:
    s = json.load(sys.stdin).get("summary", {})
    print(s.get("filesAnalyzed", 0), s.get("errorCount", 0))
except Exception:
    print("- -")
' 2>/dev/null)"
FILES_ANALYZED="${SUMMARY_LINE%% *}"
ERROR_COUNT="${SUMMARY_LINE##* }"

# Unparseable summary -> fail-open.
case "$FILES_ANALYZED" in ''|*[!0-9]*) exit 0 ;; esac

# Transparent skip: pyright analyzed nothing, so the file is excluded by
# pyrightconfig.json (e.g. it sits under an extraPaths library root). Surface
# the gap instead of a false clean pass, but do not block. See issue #46.
if [ "$FILES_ANALYZED" -eq 0 ]; then
  echo "Pyright did not analyze $FILE_PATH (excluded by pyrightconfig.json; see issue #46). Not type-checked." >&2
  exit 0
fi

case "$ERROR_COUNT" in ''|*[!0-9]*) exit 0 ;; esac
if [ "$ERROR_COUNT" -gt 0 ]; then
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
    fname = d.get("file", "")
    msg = (d.get("message", "").splitlines() or [""])[0]
    print(f"  {fname}:{line}:{col}  {msg}")
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
