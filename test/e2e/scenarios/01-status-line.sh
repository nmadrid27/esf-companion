#!/usr/bin/env bash
# Scenario 01: Activation status line fires on the first exchange
#
# Setup: fresh install + seeded companion-state.md with a logged project
# Trigger: any substantive first message
# Expect: activation status line in the response, with the right fields
#
# Failure modes caught: #1 from Nathan's observed failures
# (no visible sign the framework had initialized)

set -u

WORKSPACE="$1"
REPO_ROOT="$2"

cd "$WORKSPACE"

# Install the plugin from the local repo checkout
bash "$REPO_ROOT/install.sh" --force --platform claude --source "$REPO_ROOT" > install.log 2>&1 || {
  echo "  install.sh failed. See $WORKSPACE/install.log"
  exit 1
}

# Seed companion-state.md with a logged project so the status line has
# something concrete to report
mkdir -p projects/_esf
cat > projects/_esf/companion-state.md <<'EOF'
---
type: companion-state
last-updated: 2026-04-14
---

# ESF Companion State

## Identity
- **Name:** E2E Test User
- **Role:** student
- **Discipline:** Graphic Design

## Active Contexts
- TEST-101 — End-to-End Test Context

## Current Project
- **Context:** TEST-101
- **Project name:** e2e-status-line-project
- **Phase:** Explore
- **Scaffolding level:** Supported

## Preferences
- **silent_mode:** false

## Growth Record

None yet.
EOF

# Drive one turn
RESPONSE=$(claude -p "I want to continue working on my project. What should I do first?" 2>&1)
echo "$RESPONSE" > transcript.log

FAIL=0

check() {
  local pattern="$1"
  local desc="$2"
  if echo "$RESPONSE" | grep -qE "$pattern"; then
    echo "  ✓ $desc"
  else
    echo "  ✗ MISS: $desc (pattern: $pattern)"
    FAIL=1
  fi
}

check "ESF Companion active"              "activation marker present"
check "Project: e2e-status-line-project"  "project name in status line"
check "Context: TEST-101"                 "context code in status line"
check "Active corrections:"               "active corrections field present"
check "Session buffer:"                   "session buffer field present"
check "Last session log:"                 "last session log field present"

exit $FAIL
