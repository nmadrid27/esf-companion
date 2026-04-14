#!/usr/bin/env bash
# Scenario 03: Bulk production without a brief triggers the forcing function
#
# Setup: install + seeded companion-state.md, no brief file for the project
# Trigger: a bulk-production command ("draft all N ...")
# Expect:
#   - Brief forcing function fires (insight block + four questions)
#   - Moment 1 bulk override fires (PS check triggered regardless of clarity)
#   - No drafted posts in the response
#
# Failure modes caught: #2, #3, #6 from Nathan's second-round observations
# (brief missing for Track B, biographical inference risk, "draft all" as
# high-volume production bypass)

set -u

WORKSPACE="$1"
REPO_ROOT="$2"

cd "$WORKSPACE"

# Install the plugin
bash "$REPO_ROOT/install.sh" --force --platform claude --source "$REPO_ROOT" > install.log 2>&1 || {
  echo "  install.sh failed. See $WORKSPACE/install.log"
  exit 1
}

# Seed state: logged project, no brief
mkdir -p projects/_esf
cat > projects/_esf/companion-state.md <<'EOF'
---
type: companion-state
last-updated: 2026-04-14
---

# ESF Companion State

## Identity
- **Name:** E2E Test User
- **Role:** independent creator
- **Discipline:** Writing

## Active Contexts
- social — Social Media Content

## Current Project
- **Context:** social
- **Project name:** launch-posts
- **Phase:** Make
- **Scaffolding level:** Supported

## Preferences
- **silent_mode:** false

## Growth Record

None yet.
EOF

# Explicitly no brief file at projects/social/briefs/

# Drive one turn with a bulk-production command
RESPONSE=$(claude -p "Let's draft all five social media posts for the launch series." 2>&1)
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

# The brief forcing function must fire before drafting
check_present "Bulk production without a brief|★ Bulk production" \
              "brief forcing function insight block fires"

check_present "What is this project|in one sentence" \
              "four-question brief flow begins"

# The bulk-production Moment 1 override must also fire (PS check)
# (The spec says bulk triggers Moment 1 unconditionally. For this scenario
# without a PS, the agent should also surface the direction question.)
check_present "Position Statement|before I start drafting|what you're making" \
              "Moment 1 or PS check surfaces"

# The agent must NOT have drafted the five posts
# Heuristic: look for post-like output patterns
check_absent "^Post 1:|^Post 2:|^Post 3:|^Post 4:|^Post 5:" \
             "no post drafts produced before brief/PS"

check_absent "Here are the five posts|Here are all five" \
             "no bulk-drafted response produced"

exit $FAIL
