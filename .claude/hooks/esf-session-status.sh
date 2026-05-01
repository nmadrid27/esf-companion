#!/usr/bin/env bash
# ESF Companion session status — SessionStart hook.
#
# Reads companion-state.md and outputs the activation status line to stderr
# so it appears in Claude's context before the first response.
#
# Follows the 4-location lookup: esf/ → context/ → projects/_esf/ (legacy) → workspace root.
# Always exits 0 (fail-open — never interrupts the session).

# Prefer CLAUDE_PROJECT_DIR (set by Claude Code for hooks) over PWD,
# so the hook works even when the session was launched from a subdirectory.
WORKSPACE="${CLAUDE_PROJECT_DIR:-${PWD}}"

# 4-location lookup for companion-state.md
COMPANION_STATE=""
for candidate in \
    "$WORKSPACE/esf/companion-state.md" \
    "$WORKSPACE/context/companion-state.md" \
    "$WORKSPACE/projects/_esf/companion-state.md" \
    "$WORKSPACE/companion-state.md"
do
    if [ -f "$candidate" ]; then
        COMPANION_STATE="$candidate"
        break
    fi
done

if [ -z "$COMPANION_STATE" ]; then
    echo "ESF Companion: companion-state.md not found. Run /esf-onboarding to initialize." >&2
    exit 0
fi

# Parse key fields from companion-state.md
CURRENT_PROJECT=$(grep -m1 '^\- \*\*Project name:\*\*' "$COMPANION_STATE" \
    | sed 's/- \*\*Project name:\*\* //' | sed 's/[[:space:]]*$//')
CONTEXT=$(grep -m1 '^\- \*\*Context:\*\*' "$COMPANION_STATE" \
    | sed 's/- \*\*Context:\*\* //' | sed 's/[[:space:]]*$//')

[ -z "$CURRENT_PROJECT" ] && CURRENT_PROJECT="not set"
[ -z "$CONTEXT" ]         && CONTEXT="none"

# Count active corrections from companion-notes.md (skip HTML comment blocks)
COMPANION_DIR="${COMPANION_STATE%/*}"
NOTES_FILE="$COMPANION_DIR/companion-notes.md"
ACTIVE_CORRECTIONS=0
if [ -f "$NOTES_FILE" ]; then
    ACTIVE_CORRECTIONS=$(awk '
        {
            if (/<!--/) { if (/-->/) next; in_comment=1; next }
            if (in_comment) { if (/-->/) in_comment=0; next }
            if (/^## Active Corrections/) { in_section=1; next }
            if (/^## /) { in_section=0 }
            if (in_section && /^- [^[:space:]]/) count++
        }
        END { print count+0 }
    ' "$NOTES_FILE")
fi

# Derive context data base from where companion-state.md was found.
# projects/_esf/ is state-only; context artifacts live one level up at projects/[context]/.
COMPANION_BASE="${COMPANION_STATE%/companion-state.md}"
case "$COMPANION_BASE" in
    */_esf) CONTEXT_BASE="${COMPANION_BASE%/_esf}" ;;
    *)      CONTEXT_BASE="$COMPANION_BASE" ;;
esac
CONTEXT_BASE_REL="${CONTEXT_BASE#$WORKSPACE/}"

# Session buffer path
SESSION_BUFFER="will create on first decision"
if [ "$CONTEXT" != "none" ] && [ -n "$CONTEXT" ]; then
    BUFFER_REL="${CONTEXT_BASE_REL}/${CONTEXT}/logs/.session-buffer.md"
    if [ -f "$WORKSPACE/$BUFFER_REL" ]; then
        SESSION_BUFFER="$BUFFER_REL"
    fi
fi

# Last session log (most recent session-*.md in the context logs dir)
LAST_SESSION_LOG="none"
if [ "$CONTEXT" != "none" ] && [ -n "$CONTEXT" ]; then
    LOG_DIR="$CONTEXT_BASE/${CONTEXT}/logs"
    if [ -d "$LOG_DIR" ]; then
        LATEST=$(ls -1 "$LOG_DIR"/session-*.md 2>/dev/null | sort | tail -1)
        if [ -n "$LATEST" ]; then
            LAST_SESSION_LOG="${CONTEXT_BASE_REL}/${CONTEXT}/logs/$(basename "$LATEST")"
        fi
    fi
fi

echo "" >&2
echo "ESF Companion active. Project: ${CURRENT_PROJECT}. Context: ${CONTEXT}. Active corrections: ${ACTIVE_CORRECTIONS}. Session buffer: ${SESSION_BUFFER}. Last session log: ${LAST_SESSION_LOG}." >&2
echo "" >&2
exit 0
