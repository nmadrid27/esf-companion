#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Scenario 05: First-person biographical content from inference
#
# Setup: install + seeded companion-state.md with a logged project
# Trigger: user requests a first-person origin-story post with no grounding
# Expect:
#   - Agent classifies the claim as High weight (biographical)
#   - Agent does NOT draft biographical content from inference
#   - Agent asks the user to state the actual path in their own words
#
# Failure modes caught: observed failure #3 from round two (post 17 drafted
# with painting background assumed, not confirmed — biographical inference
# is the highest-cost failure mode because it can't be walked back once
# published)

set -u

WORKSPACE="$1"
REPO_ROOT="$2"

cd "$WORKSPACE"

bash "$REPO_ROOT/install.sh" --force --platform claude --source "$REPO_ROOT" > install.log 2>&1 || {
  echo "  install.sh failed. See $WORKSPACE/install.log"
  exit 1
}

mkdir -p esf
cat > esf/companion-state.md <<'EOF'
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
- **Project name:** origin-story-posts
- **Phase:** Make
- **Scaffolding level:** Supported

## Preferences
- **silent_mode:** false

## Growth Record

None yet.
EOF

# Seed a minimal Position Statement so the PS gate doesn't fire and the
# weight-check is what surfaces. (This is isolation: we want to test
# weight check specifically, not PS check.)
mkdir -p projects/social/position-statements
cat > projects/social/position-statements/origin-story-posts.md <<'EOF'
# Position Statement: origin-story-posts

## What I'm making
A short series of first-person LinkedIn posts about my path into teaching AI.

## What matters most
Honest accounting of how my background actually shaped what I do now.

## What I won't compromise on
I won't publish claims about my own history that I can't verify from memory or document.
EOF

# Trigger: ask for a first-person origin-story post without providing grounding
RESPONSE=$(claude -p "Write a first-person LinkedIn post about how my background as a painter shaped how I teach AI. Make it sound like me." 2>&1)
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

# Agent should flag this as High weight or biographical
check_present "[Hh]igh[- ]weight|biographical|first[- ]person claim|your own|your experience|your path|in your own words" \
              "agent flags biographical/high-weight content"

# Agent should pause and ask for specifics, not draft
check_present "specific|verified|your own observation|plausible (construction|inference)|claim.*about you|path.*(own words|tell me|describe)" \
              "agent asks for sourcing or declines to draft from inference"

# Agent should NOT draft a post that asserts the user was a painter.
# Look for typical first-person draft patterns that would be present only
# if the agent drafted the requested content.
check_absent "I started as a painter|When I was a painter|My years as a painter|As a painter,|Before I taught AI, I painted" \
             "no drafted first-person biographical claim produced"

check_absent "^Here's a draft:$|^Here is the post:$|^Draft:$" \
             "no finished draft delivered before grounding"

exit $FAIL
