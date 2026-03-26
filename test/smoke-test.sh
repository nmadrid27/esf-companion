#!/usr/bin/env bash
# ESF Companion smoke test
# Installs both platform modes in temp git repos and asserts key contracts.
#
# Usage: bash test/smoke-test.sh
# Exit 0: all assertions pass
# Exit 1: one or more assertions failed

set -e

INSTALL_SH="$(cd "$(dirname "$0")/.." && pwd)/install.sh"
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

# Phase 2 accessibility exception: conversational drafting exception present
assert "Phase 2 accessibility exception in esf-project" \
  "$(grep -q 'Conversational drafting\|accessibility\|processing barrier\|articulation support' \
      .claude/skills/esf-project/SKILL.md && echo 0 || echo 1)"

# Disclosure contract: Companion drafts, user approves
assert "Disclosure: Companion drafts candidate"        \
  "$(grep -q 'The Companion drafts the disclosure candidate' \
      .claude/skills/esf-project/SKILL.md && echo 0 || echo 1)"
assert "Disclosure: approval mandatory"                \
  "$(grep -q 'explicit approval\|explicitly approves' \
      .claude/skills/esf-project/SKILL.md && echo 0 || echo 1)"

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

# Phase 2 accessibility exception: present in conversation prompt
assert "Phase 2 accessibility exception in project-workflow" \
  "$(grep -q 'Conversational drafting\|accessibility\|processing barrier\|articulation support' \
      prompts/project-workflow.md && echo 0 || echo 1)"

# PROJECT.md handoff: session end emits PROJECT.md
assert "Session end emits PROJECT.md block"            \
  "$(grep -q 'PROJECT.md' prompts/project-workflow.md && echo 0 || echo 1)"
assert "Cross-session note references PROJECT.md"      \
  "$(grep -q 'paste your PROJECT.md\|Paste it at the start' \
      prompts/project-workflow.md && echo 0 || echo 1)"

# Disclosure: conversation prompt also offers to draft
assert "Disclosure: Companion offers to draft in conversation" \
  "$(grep -q "draft a disclosure\|I will pull from" \
      prompts/project-workflow.md && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 3: Onboarding can complete without course data"

assert "Universal identity question present"           \
  "$(grep -q 'Tell me about yourself' \
      "$INSTALL_SH" 2>/dev/null || \
     grep -q 'Tell me about yourself' \
      "$CLAUDE_DIR/.claude/skills/esf-onboarding/SKILL.md" && echo 0 || echo 1)"

assert "No dead courses/ yaml fallback"                \
  "$(grep -q 'courses/{code}.yaml\|courses/.*yaml' \
      "$CLAUDE_DIR/.claude/skills/esf-onboarding/SKILL.md" && echo 1 || echo 0)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 4: Piped-stdin guard on setup-repo.sh"

SETUP_SH="$(cd "$(dirname "$0")/.." && pwd)/setup-repo.sh"
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
