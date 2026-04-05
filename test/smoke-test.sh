#!/usr/bin/env bash
# ESF Companion smoke test
# Installs both platform modes in temp git repos and asserts key contracts.
#
# Usage: bash test/smoke-test.sh
# Exit 0: all assertions pass
# Exit 1: one or more assertions failed
#
# Content assertions run against local source files (faster, no CDN lag).
# Install assertions run against temp git repos (fresh installs).
#
# Known limitation: install.sh fetches from GitHub main, not the local
# checkout. Content assertions use $REPO_ROOT to validate local source,
# but the install path validates remote main. For pre-merge testing,
# content assertions are the reliable gate; install assertions confirm
# the installer script mechanics, not the content being installed.

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_SH="$REPO_ROOT/install.sh"
PASS=0
FAIL=0

assert() {
  local label="$1"
  local result="$2"
  if [ "$result" = "0" ]; then
    echo "  PASS  $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $label"
    FAIL=$((FAIL + 1))
  fi
}

make_git_repo() {
  local dir="$1"
  rm -rf "$dir"
  mkdir -p "$dir"
  cd "$dir"
  git init -q -b main
  git config user.email "smoke@test.local"
  git config user.name "Smoke Test"
}

# ────────────────────────────────────────────────────────────────
echo ""
echo "ESF Companion smoke test"
echo "────────────────────────────────────────────────────────────"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 1: Claude install (--force --platform claude)"

CLAUDE_DIR="/tmp/esf-smoke-claude"
make_git_repo "$CLAUDE_DIR"
bash "$INSTALL_SH" --force --platform claude > /dev/null 2>&1
EXIT=$?

assert "install exits 0"                               "$EXIT"
assert "esf-companion agent present"                   "$([ -f .claude/agents/esf-companion.md ]  && echo 0 || echo 1)"
assert "esf-project skill present"                     "$([ -f .claude/skills/esf-project/SKILL.md ] && echo 0 || echo 1)"
assert "esf-cognitive skill present"                   "$([ -f .claude/skills/esf-cognitive/SKILL.md ] && echo 0 || echo 1)"
assert "esf-onboarding skill present"                  "$([ -f .claude/skills/esf-onboarding/SKILL.md ] && echo 0 || echo 1)"
assert "START_HERE.md present"                         "$([ -f START_HERE.md ] && echo 0 || echo 1)"
assert "WORKFLOW.md present"                           "$([ -f WORKFLOW.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "START_HERE.md in git commit"                   "$(git show --name-only HEAD | grep -q 'START_HERE.md' && echo 0 || echo 1)"
assert "esf-cognitive in git commit"                   "$(git show --name-only HEAD | grep -q 'esf-cognitive' && echo 0 || echo 1)"

# Phase 2 conversational drafting option present
assert "Phase 2 conversational drafting in esf-project" \
  "$(grep -q 'Conversational drafting\|Talk it through' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"
assert "Phase 1 redirect includes inquiry questions in esf-project" \
  "$(grep -A5 'Phase 1 is yours alone' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" | \
      grep -q 'What is this project asking' && echo 0 || echo 1)"
assert "Position Statement spec includes non-negotiable in esf-project" \
  "$(grep -A10 'What a Position Statement Contains' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" | \
      grep -q 'non-negotiable' && echo 0 || echo 1)"
assert "esf-cognitive defines trigger detection guidance" \
  "$(grep -q 'How to detect them' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && \
    grep -q 'count consecutive AI suggestions' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && \
    grep -q 'rapid agreement' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && echo 0 || echo 1)"

# Disclosure contract: Companion drafts, user approves (checked against source)
assert "Disclosure: Companion drafts candidate"        \
  "$(grep -q 'The Companion drafts the disclosure candidate' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"
assert "Disclosure: approval mandatory"                \
  "$(grep -q 'explicit approval\|explicitly approves' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 2: Conversation install (--force --platform conversation)"

CONV_DIR="/tmp/esf-smoke-conversation"
make_git_repo "$CONV_DIR"
bash "$INSTALL_SH" --force --platform conversation > /dev/null 2>&1
EXIT=$?

assert "install exits 0"                               "$EXIT"
assert "prompts/companion.md present"                  "$([ -f prompts/companion.md ] && echo 0 || echo 1)"
assert "prompts/project-workflow.md present"           "$([ -f prompts/project-workflow.md ] && echo 0 || echo 1)"
assert "templates/position-statement-template.md"      "$([ -f templates/position-statement-template.md ] && echo 0 || echo 1)"
assert "START_HERE.md present"                         "$([ -f START_HERE.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "START_HERE.md in git commit"                   "$(git show --name-only HEAD | grep -q 'START_HERE.md' && echo 0 || echo 1)"

# Phase 2 conversational drafting option present in conversation prompt
assert "Phase 2 conversational drafting in project-workflow" \
  "$(grep -q 'Conversational drafting\|Talk it through' \
      "$REPO_ROOT/prompts/project-workflow.md" && echo 0 || echo 1)"
assert "Phase 1 redirect includes inquiry questions in project-workflow" \
  "$(grep -A5 'Phase 1 is yours alone' "$REPO_ROOT/prompts/project-workflow.md" | \
      grep -q 'What is this project asking' && echo 0 || echo 1)"
assert "Position Statement spec includes non-negotiable in project-workflow" \
  "$(grep -A10 'What a Position Statement Contains' "$REPO_ROOT/prompts/project-workflow.md" | \
      grep -q 'non-negotiable' && echo 0 || echo 1)"

# PROJECT.md handoff: session end emits PROJECT.md (checked against source)
assert "Session end emits PROJECT.md block"            \
  "$(grep -q 'PROJECT.md' "$REPO_ROOT/prompts/project-workflow.md" && echo 0 || echo 1)"
assert "Cross-session note references PROJECT.md"      \
  "$(grep -q 'paste your PROJECT.md\|Paste it at the start' \
      "$REPO_ROOT/prompts/project-workflow.md" && echo 0 || echo 1)"

# Disclosure: conversation prompt also offers to draft (checked against source)
assert "Disclosure: Companion offers to draft in conversation" \
  "$(grep -q "draft a disclosure\|I will pull from" \
      "$REPO_ROOT/prompts/project-workflow.md" && echo 0 || echo 1)"
assert "Disclosure: no conflicting manual-only instruction in conversation" \
  "$([ "$(grep -c 'Do not draft it for them' "$REPO_ROOT/prompts/project-workflow.md")" -eq 0 ] && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 3: Onboarding can complete without course data"

assert "Universal identity question present"           \
  "$(grep -q 'Tell me about yourself' \
      "$REPO_ROOT/.claude/skills/esf-onboarding/SKILL.md" && echo 0 || echo 1)"

assert "No dead courses/ yaml fallback"                \
  "$(grep -q 'courses/{code}.yaml\|courses/.*yaml' \
      "$REPO_ROOT/.claude/skills/esf-onboarding/SKILL.md" && echo 1 || echo 0)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 4: Piped-stdin guard on setup-repo.sh"

SETUP_SH="$REPO_ROOT/setup-repo.sh"
GUARD_OUTPUT=$(echo "" | bash "$SETUP_SH" 2>&1 || true)

assert "guard blocks piped stdin"                      \
  "$(echo "$GUARD_OUTPUT" | grep -q 'requires an interactive terminal' && echo 0 || echo 1)"

assert "guard shows correct download command"          \
  "$(echo "$GUARD_OUTPUT" | grep -q '\-o setup-repo.sh && bash setup-repo.sh' && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Cleanup"
rm -rf /tmp/esf-smoke-claude /tmp/esf-smoke-conversation
echo "  Temp dirs removed"

# ────────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────────────────────"
echo "Results: $PASS passed, $FAIL failed"
echo "────────────────────────────────────────────────────────────"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
