#!/usr/bin/env bash
# ESF Companion session status — SessionStart hook.
#
# Reads companion-state.md and outputs the activation status line to stderr
# so it appears in Claude's context before the first response.
#
# Follows the 3-location lookup: context/ → projects/_esf/ → workspace root.
# Always exits 0 (fail-open — never interrupts the session).

WORKSPACE="$(cd "${PWD}" 2>/dev/null && pwd -P || echo "${PWD}")"

# 3-location lookup for companion-state.md
COMPANION_STATE=""
for candidate in \
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
PHASE=$(grep -m1 '^\- \*\*Phase:\*\*' "$COMPANION_STATE" \
    | sed 's/- \*\*Phase:\*\* //' | sed 's/[[:space:]]*$//')
LAST_SESSION=$(grep -m1 '^\- \*\*Last session:\*\*' "$COMPANION_STATE" \
    | sed 's/- \*\*Last session:\*\* //' | sed 's/[[:space:]]*$//')

[ -z "$CURRENT_PROJECT" ] && CURRENT_PROJECT="not set"
[ -z "$CONTEXT" ]         && CONTEXT="none"
[ -z "$PHASE" ]           && PHASE="not set"
[ -z "$LAST_SESSION" ]    && LAST_SESSION="none"

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

echo "" >&2
echo "ESF Companion active. Project: ${CURRENT_PROJECT}. Context: ${CONTEXT}. Phase: ${PHASE}. Active corrections: ${ACTIVE_CORRECTIONS}. Last session: ${LAST_SESSION}." >&2
echo "" >&2
exit 0
