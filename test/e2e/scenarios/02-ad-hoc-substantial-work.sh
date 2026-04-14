#!/usr/bin/env bash
# Scenario 02: Ad hoc substantial work with Current Project "not set"
#
# Setup: install + seeded companion-state.md where Current Project = "not set"
# Trigger: a substantial content request with no logged project
# Expect:
#   - Agent pauses before drafting
#   - Offers to log the project (ad hoc project logging block)
#   - Does not produce the requested content
#
# Failure modes caught: observed failure #4 from round one (Current Project
# was "not set" throughout a session and substantial work got created with no
# project context)

set -u

WORKSPACE="$1"
REPO_ROOT="$2"

cd "$WORKSPACE"

bash "$REPO_ROOT/install.sh" --force --platform claude --source "$REPO_ROOT" > install.log 2>&1 || {
  echo "  install.sh failed. See $WORKSPACE/install.log"
  exit 1
}

# Seed state: identity present, Current Project deliberately "not set"
mkdir -p projects/_esf
cat > projects/_esf/companion-state.md <<'EOF'
---
type: companion-state
last-updated: 2026-04-14
---

# ESF Companion State

## Identity
- **Name:** E2E Test User
- **Role:** professor
- **Discipline:** Applied AI

## Active Contexts
- institutional — Academic administration

## Current Project
- **Context:** institutional
- **Project name:** not set
- **Phase:** not set
- **Scaffolding level:** Independent

## Preferences
- **silent_mode:** false

## Growth Record

None yet.
EOF

RESPONSE=$(claude -p "I need a research guide for graduate students working with AI. Can you draft it?" 2>&1)
echo "$RESPONSE" > transcript.log

FAIL=0

check_present() {
  local pattern="$1"
  local desc="$2"
  if echo "$RESPONSE" | grep -qE "$pattern"; then
    echo "  ✓ $desc"
  else
    echo "  ✗ MISS: $desc (pattern: $pattern)"
    FAIL=1
  fi
}

check_absent() {
  local pattern="$1"
  local desc="$2"
  if echo "$RESPONSE" | grep -qE "$pattern"; then
    echo "  ✗ UNEXPECTED: $desc (pattern matched: $pattern)"
    FAIL=1
  else
    echo "  ✓ $desc"
  fi
}

# Status line still fires
check_present "ESF Companion active" "activation marker present"

# Ad hoc project logging surfaces. Accept the literal block header or any
# clear behavioral indicator (acknowledging no project set + offering to log).
check_present "New document, no project logged|★ New document|Current Project.*not set|[Nn]ot set.*project|offer to (log|set).*project|set this as the active project|active project in companion-state" \
              "ad hoc project logging surfaces"

# Agent should offer to log a project. Accept the literal low-friction phrasings
# or any clear "would you like me to log this" / "log this as a project" offer.
# Some responses combine the log offer directly into the brief flow (log +
# four questions in one pass), which still counts as offering to log.
check_present "name and (a )?(one|1).*sentence|[Pp]roject name|twenty seconds|What should I call|name.*description|[Ww]ould you like me to log|log this as a project|log it as a project|set (this|it) up as a project|set this as the active project|log.*project first" \
              "agent offers to log the project"

# The agent should NOT have produced the guide itself
check_absent "^# Research Guide|^Introduction[[:space:]]*$|^## [0-9]\. " \
             "no research guide drafted before project is logged"

exit $FAIL
