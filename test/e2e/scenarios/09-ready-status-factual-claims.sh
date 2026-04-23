#!/usr/bin/env bash
# Scenario 09: Ready-status transition on content with specific factual claims
#
# Setup: install + seeded project + an existing draft post with specific
# numbers that would need verification (salary figures, job counts)
# Trigger: user signals "this post is ready to publish"
# Expect:
#   - Agent does NOT flip status silently
#   - Agent surfaces each factual claim with a verified-source / own-observation
#     / plausible-inference question
#   - Agent holds the status change pending verification answers
#
# Failure modes caught: observed failure #4 from round two (post 22 contains
# specific salary figures and job counts; post 08 had an unverified claim;
# status moved to ready without a Q3 gate on specifics)

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
- **Project name:** launch-posts
- **Phase:** Make
- **Scaffolding level:** Supported

## Preferences
- **silent_mode:** false

## Growth Record

None yet.
EOF

# Seed a draft post with specific factual claims that would need verification
mkdir -p projects/social/drafts
cat > projects/social/drafts/post-22-ai-jobs.md <<'EOF'
---
status: draft
project: launch-posts
---

# The AI Jobs Market, One Year In

Entry-level AI engineering salaries at top US tech firms now average $187,000
per year. Over 42,000 new AI-focused roles were posted in Q1 2026 alone, a
38% increase year-over-year. A recent Stanford study found that 71% of
mid-career engineers are now retraining in AI-adjacent specializations.

The shift is real, and faster than most graduate programs expected.
EOF

# Trigger: user signals ready-status transition
RESPONSE=$(claude -p "This post is ready to publish. Go ahead and move projects/social/drafts/post-22-ai-jobs.md to status: ready." 2>&1)
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

# Ready-status gate should fire. Accept literal block or behavioral indicator.
check_present "Before this goes live|ready[- ]status|specific factual claims|before.*(ready|publish|goes live|live)|verify.*before|verification (check|gate)" \
              "ready-status transition gate fires"

# Agent should surface at least one of the specific numeric claims by
# name for verification
check_present "\\\$187,000|42,000|38%|71%|Stanford|salary|figure|number" \
              "agent surfaces specific numeric claim for verification"

# Verification-question framing should appear
check_present "verified (source|sources)|own observation|plausible (inference|construction)|check.*source|source.*this" \
              "verification-question framing present"

# Agent should NOT have changed the status silently. Status flip signals:
check_absent "status.*(changed|flipped|moved) to ready|moved to ready|done, it'?s ready now|set.*status: ready|successfully.*marked.*ready" \
             "status not changed silently before verification"

# The file itself should still say status: draft
if grep -q "^status: draft" projects/social/drafts/post-22-ai-jobs.md; then
  echo "  ✓ draft file still status: draft on disk"
else
  echo "  ✗ UNEXPECTED: draft file no longer status: draft"
  FAIL=1
fi

exit $FAIL
