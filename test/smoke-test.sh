#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion smoke test
# Installs both platform modes in temp git repos and asserts key contracts.
#
# Usage: bash test/smoke-test.sh
# Exit 0: all assertions pass
# Exit 1: one or more assertions failed
#
# Both the install path and the content assertions run against the local
# checkout. install.sh is invoked with --source $REPO_ROOT, which switches
# its fetch URLs to file:// pointing at the working tree, so the smoke test
# is a reliable pre-merge gate for both installer mechanics and the content
# being installed.

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
  git config commit.gpgsign false
  # Seed with an initial commit so git log/show work
  touch .gitkeep
  git add .gitkeep
  git commit -q -m "init" 2>/dev/null || true
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
bash "$INSTALL_SH" --force --platform claude --source "$REPO_ROOT" > /dev/null 2>&1
EXIT=$?

assert "install exits 0"                               "$EXIT"
assert "esf-companion agent present"                   "$([ -f .claude/agents/esf-companion.md ]  && echo 0 || echo 1)"
assert "esf-project skill present"                     "$([ -f .claude/skills/esf-project/SKILL.md ] && echo 0 || echo 1)"
assert "esf-cognitive skill present"                   "$([ -f .claude/skills/esf-cognitive/SKILL.md ] && echo 0 || echo 1)"
assert "esf-onboarding skill present"                  "$([ -f .claude/skills/esf-onboarding/SKILL.md ] && echo 0 || echo 1)"
assert "START_HERE.md present in esf/toolkit"          "$([ -f esf/toolkit/START_HERE.md ] && echo 0 || echo 1)"
assert "WORKFLOW.md present in esf/toolkit"            "$([ -f esf/toolkit/WORKFLOW.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "esf/toolkit in git commit"                     "$(git show --name-only HEAD | grep -q 'esf/toolkit/' && echo 0 || echo 1)"
assert "esf-cognitive in git commit"                   "$(git show --name-only HEAD | grep -q 'esf-cognitive' && echo 0 || echo 1)"

# Phase 2 conversational drafting option present
assert "Phase 2 conversational drafting in esf-project" \
  "$(grep -q 'Conversational drafting\|Talk it through' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"
assert "Phase 1 redirect includes inquiry questions in esf-project" \
  "$(grep -A5 'Phase 1' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" | \
      grep -q 'What is this project asking' && echo 0 || echo 1)"
assert "Position Statement spec includes non-negotiable in esf-project" \
  "$(grep -A10 'What a Position Statement Contains' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" | \
      grep -q 'non-negotiable' && echo 0 || echo 1)"
assert "esf-cognitive defines trigger detection guidance" \
  "$(grep -q 'How to detect them' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && \
    grep -q 'count consecutive AI suggestions' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && \
    grep -q 'rapid agreement' "$REPO_ROOT/.claude/skills/esf-cognitive/SKILL.md" && echo 0 || echo 1)"

# Disclosure contract: AI drafts, user approves (checked against source)
assert "Disclosure: AI drafts candidate"               \
  "$(grep -q 'draft the disclosure candidate' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"
assert "Disclosure: approval mandatory"                \
  "$(grep -q 'explicit approval\|explicitly approves' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"

# Phase 5 sequence: reflection before disclosure
assert "Phase 5: reflection appears before disclosure in esf-project" \
  "$(awk '/\*\*Reflection:\*\*/{r=NR} /\*\*Disclosure generation:\*\*/{d=NR} END{print (r<d)?"0":"1"}' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md")"

# No jargon in user-facing files
assert "No 'epistemic development' in esf-companion agent" \
  "$(grep -q 'epistemic development' \
      "$REPO_ROOT/.claude/agents/esf-companion.md" && echo 1 || echo 0)"
assert "No 'Accessibility exception' in esf-project" \
  "$(grep -q 'Accessibility exception' \
      "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 1 || echo 0)"

# Conversational drafting is first-class (not labeled as exception)
assert "Conversational drafting not labeled as exception in prompts" \
  "$(grep -q 'Accessibility exception' \
      "$REPO_ROOT/prompts/esf-companion.md" && echo 1 || echo 0)"

# Build Practice present in esf-project
assert "Build Practice Define/Order/Check in esf-project" \
  "$(grep -q 'Step 1: Define' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && \
    grep -q 'Step 2: Order' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && \
    grep -q 'Step 3: Check' "$REPO_ROOT/.claude/skills/esf-project/SKILL.md" && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 2: Conversation install (--force --platform conversation)"

CONV_DIR="/tmp/esf-smoke-conversation"
make_git_repo "$CONV_DIR"
bash "$INSTALL_SH" --force --platform conversation --source "$REPO_ROOT" > /dev/null 2>&1
EXIT=$?

assert "install exits 0"                               "$EXIT"
assert "esf/toolkit/prompts/companion.md present"      "$([ -f esf/toolkit/prompts/companion.md ] && echo 0 || echo 1)"
assert "esf/toolkit/prompts/project-workflow.md"       "$([ -f esf/toolkit/prompts/project-workflow.md ] && echo 0 || echo 1)"
assert "esf/toolkit/templates/position-statement"      "$([ -f esf/toolkit/templates/position-statement-template.md ] && echo 0 || echo 1)"
assert "esf/toolkit/START_HERE.md present"             "$([ -f esf/toolkit/START_HERE.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "esf/toolkit in git commit"                     "$(git show --name-only HEAD | grep -q 'esf/toolkit/' && echo 0 || echo 1)"

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
  "$(grep -q 'Tell me about a project' \
      "$REPO_ROOT/.claude/skills/esf-onboarding/SKILL.md" && echo 0 || echo 1)"

assert "No dead courses/ yaml fallback"                \
  "$(grep -q 'courses/{code}.yaml\|courses/.*yaml' \
      "$REPO_ROOT/.claude/skills/esf-onboarding/SKILL.md" && echo 1 || echo 0)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 4: Cowork plugin parity"

COWORK_SKILL="$REPO_ROOT/platforms/cowork/skills/esf-project/SKILL.md"
COWORK_START="$REPO_ROOT/platforms/cowork/commands/esf-start.md"
COWORK_README="$REPO_ROOT/platforms/cowork/README.md"

# Build Practice present in Cowork
assert "Cowork: Build Practice Define/Order/Check present" \
  "$(grep -q 'Step 1: Define' "$COWORK_SKILL" && \
    grep -q 'Step 2: Order' "$COWORK_SKILL" && \
    grep -q 'Step 3: Check' "$COWORK_SKILL" && echo 0 || echo 1)"

# Build Environment section present
assert "Cowork: Build Environment section present" \
  "$(grep -q 'Build Environment' "$COWORK_SKILL" && echo 0 || echo 1)"

# Project Scope has Intent section
assert "Cowork: Project Scope includes Intent" \
  "$(grep -q '## Intent' "$COWORK_SKILL" && echo 0 || echo 1)"

# Thread Tracking present
assert "Cowork: Thread Tracking present" \
  "$(grep -q 'Thread Tracking' "$COWORK_SKILL" && echo 0 || echo 1)"

# Phase 5 sequence: reflection before disclosure
assert "Cowork: reflection before disclosure" \
  "$(awk '/\*\*Reflection:\*\*/{r=NR} /\*\*Disclosure generation:\*\*/{d=NR} END{print (r<d)?"0":"1"}' \
      "$COWORK_SKILL")"

# No "close this tool" in Cowork files
assert "Cowork: no 'close this tool' in SKILL" \
  "$(grep -q 'close this tool\|Close this tool' "$COWORK_SKILL" && echo 1 || echo 0)"
assert "Cowork: no 'close this tool' in esf-start" \
  "$(grep -q 'close this tool\|Close this tool\|closing this tool' "$COWORK_START" && echo 1 || echo 0)"

# Folder structure uses [context] not [project-name]
assert "Cowork: esf-start uses [context] path" \
  "$(grep -A2 'Set Up Folder' "$COWORK_START" | grep -q 'project-name' && echo 1 || echo 0)"
assert "Cowork: README uses [context] path" \
  "$(grep 'briefs/' "$COWORK_README" | head -1 | grep -q 'project-name' && echo 1 || echo 0)"

# No jargon in Cowork
assert "Cowork: no 'Accessibility exception' in SKILL" \
  "$(grep -q 'Accessibility exception' "$COWORK_SKILL" && echo 1 || echo 0)"

# Disclosure: AI drafts in Cowork too
assert "Cowork: Disclosure AI-drafted with user review" \
  "$(grep -q 'draft the disclosure candidate' "$COWORK_SKILL" && \
    grep -q 'explicit.*approval\|explicitly approves' "$COWORK_SKILL" && echo 0 || echo 1)"

# Version lockstep: plugin.json version must match the value baked into /esf-start
# so the in-session version check doesn't emit spurious update notices.
COWORK_MANIFEST="$REPO_ROOT/platforms/cowork/.claude-plugin/plugin.json"
COWORK_VERSION=$(grep '"version"' "$COWORK_MANIFEST" | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

assert "Cowork: plugin.json has a parseable version"   \
  "$([ -n "$COWORK_VERSION" ] && echo 0 || echo 1)"

# The version should appear at least twice in esf-start.md Step 0:
# once in "shipped with this command is `X.Y.Z`" and once in "(you have vX.Y.Z)".
BAKED_COUNT=$(grep -E "\`${COWORK_VERSION}\`|v${COWORK_VERSION}" "$COWORK_START" 2>/dev/null | wc -l | tr -d ' ')
assert "Cowork: esf-start.md baked-in version matches plugin.json ($COWORK_VERSION)" \
  "$([ "$BAKED_COUNT" -ge 2 ] && echo 0 || echo 1)"

# CHANGELOG should mention the current Cowork plugin version somewhere.
# Loose check: the version string appears in the file. Exact formatting is
# freeform, so we don't assert section structure.
assert "Cowork: CHANGELOG mentions plugin v$COWORK_VERSION" \
  "$(grep -q "v${COWORK_VERSION}\|${COWORK_VERSION}" "$REPO_ROOT/CHANGELOG.md" && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 5: Piped-stdin guard on setup-repo.sh"

SETUP_SH="$REPO_ROOT/setup-repo.sh"
GUARD_OUTPUT=$(echo "" | bash "$SETUP_SH" 2>&1 || true)

assert "guard blocks piped stdin"                      \
  "$(echo "$GUARD_OUTPUT" | grep -q 'requires an interactive terminal' && echo 0 || echo 1)"

assert "guard shows correct download command"          \
  "$(echo "$GUARD_OUTPUT" | grep -q '\-o setup-repo.sh && bash setup-repo.sh' && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 6: Migration from legacy install footprint"

MIGRATE_DIR="/tmp/esf-smoke-migrate"
make_git_repo "$MIGRATE_DIR"

# Simulate legacy v0.7.x install: scatter the old toolkit paths at root
mkdir -p prompts templates
echo "legacy prompt" > prompts/companion.md
echo "legacy template" > templates/position-statement-template.md
echo "legacy workflow" > WORKFLOW.md
echo "legacy start" > START_HERE.md
git add . && git commit -q -m "legacy install"

# Run installer — migration should fire
bash "$INSTALL_SH" --force --platform claude --source "$REPO_ROOT" > /dev/null 2>&1
EXIT=$?

assert "migration install exits 0"                     "$EXIT"
assert "legacy prompts/ removed from root"             "$([ ! -d prompts ] && echo 0 || echo 1)"
assert "legacy templates/ removed from root"           "$([ ! -d templates ] && echo 0 || echo 1)"
assert "legacy WORKFLOW.md removed from root"          "$([ ! -f WORKFLOW.md ] && echo 0 || echo 1)"
assert "legacy START_HERE.md removed from root"        "$([ ! -f START_HERE.md ] && echo 0 || echo 1)"
assert "esf/toolkit/prompts/companion.md present"      "$([ -f esf/toolkit/prompts/companion.md ] && echo 0 || echo 1)"
assert "esf/toolkit/templates/ populated"              "$([ -f esf/toolkit/templates/position-statement-template.md ] && echo 0 || echo 1)"
assert "esf/toolkit/WORKFLOW.md present"               "$([ -f esf/toolkit/WORKFLOW.md ] && echo 0 || echo 1)"
assert "esf/toolkit/START_HERE.md present"             "$([ -f esf/toolkit/START_HERE.md ] && echo 0 || echo 1)"
assert "migration snapshot directory exists"           "$(ls -d esf/.migration-snapshot-* 2>/dev/null | head -1 | grep -q . && echo 0 || echo 1)"

# Idempotency: running again is a no-op
bash "$INSTALL_SH" --force --platform claude --source "$REPO_ROOT" > /dev/null 2>&1
EXIT=$?
assert "second install run exits 0 (idempotent)"       "$EXIT"
SNAPSHOT_COUNT=$(ls -d esf/.migration-snapshot-* 2>/dev/null | wc -l | tr -d ' ')
assert "no duplicate snapshot on second run"           "$([ "$SNAPSHOT_COUNT" = "1" ] && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Test 7: Migration preserves user-custom files in shared namespaces"

# Real-world v0.7.x install in an Obsidian vault: templates/ and prompts/ are
# SHARED between the Companion (canonical files) and the user (custom files).
# Migration must move only canonical files, leaving user content untouched at
# root. The directory itself must remain if any user files remain inside it.

SHARED_DIR="/tmp/esf-smoke-shared"
make_git_repo "$SHARED_DIR"

# Seed shared namespaces with BOTH canonical Companion files AND user content
mkdir -p prompts templates
# Canonical templates
echo "canonical position-statement" > templates/position-statement-template.md
echo "canonical ai-use-log"         > templates/ai-use-log-template.md
# User-custom templates (Obsidian-style)
echo "user custom template body"    > "templates/My Custom Template.md"
echo "user daily research note"     > "templates/Daily Research.md"
# Canonical prompts (esf-companion.md doubles as the migration-gate signal)
echo "canonical esf-companion"      > prompts/esf-companion.md
echo "canonical companion"          > prompts/companion.md
# User-custom prompt
echo "user personal prompt"         > prompts/my-personal-prompt.md
# Canonical-uniqueish root files
echo "legacy workflow"              > WORKFLOW.md
echo "legacy start"                 > START_HERE.md
git add . && git commit -q -m "legacy install with user content"

bash "$INSTALL_SH" --force --platform claude --source "$REPO_ROOT" > /dev/null 2>&1
EXIT=$?

assert "shared-namespace install exits 0"              "$EXIT"

# Canonical files migrated into esf/toolkit/
assert "canonical templates/position-statement moved"  "$([ -f esf/toolkit/templates/position-statement-template.md ] && echo 0 || echo 1)"
assert "canonical templates/ai-use-log moved"          "$([ -f esf/toolkit/templates/ai-use-log-template.md ] && echo 0 || echo 1)"
assert "canonical prompts/esf-companion moved"         "$([ -f esf/toolkit/prompts/esf-companion.md ] && echo 0 || echo 1)"
assert "canonical prompts/companion moved"             "$([ -f esf/toolkit/prompts/companion.md ] && echo 0 || echo 1)"
assert "WORKFLOW.md migrated to esf/toolkit"           "$([ -f esf/toolkit/WORKFLOW.md ] && [ ! -f WORKFLOW.md ] && echo 0 || echo 1)"
assert "START_HERE.md migrated to esf/toolkit"         "$([ -f esf/toolkit/START_HERE.md ] && [ ! -f START_HERE.md ] && echo 0 || echo 1)"

# User-custom files preserved at root (the whole point of this test)
assert "user-custom templates/My Custom Template.md preserved" \
  "$([ -f "templates/My Custom Template.md" ] && echo 0 || echo 1)"
assert "user-custom templates/Daily Research.md preserved" \
  "$([ -f "templates/Daily Research.md" ] && echo 0 || echo 1)"
assert "user-custom prompts/my-personal-prompt.md preserved" \
  "$([ -f prompts/my-personal-prompt.md ] && echo 0 || echo 1)"

# Shared directories must remain at root because user content still lives in them
assert "templates/ directory still at root"            "$([ -d templates ] && echo 0 || echo 1)"
assert "prompts/ directory still at root"              "$([ -d prompts ] && echo 0 || echo 1)"

# Snapshot exists and captured both canonical and user content (proves nothing
# was deleted unrecoverably even if Task B has a bug)
SHARED_SNAPSHOT=$(ls -d esf/.migration-snapshot-* 2>/dev/null | head -1)
assert "shared-namespace snapshot exists"              "$([ -n "$SHARED_SNAPSHOT" ] && [ -d "$SHARED_SNAPSHOT" ] && echo 0 || echo 1)"
assert "snapshot captured canonical template"          "$([ -f "$SHARED_SNAPSHOT/templates/position-statement-template.md" ] && echo 0 || echo 1)"
assert "snapshot captured user-custom template"        "$([ -f "$SHARED_SNAPSHOT/templates/My Custom Template.md" ] && echo 0 || echo 1)"

# ────────────────────────────────────────────────────────────────
echo ""
echo "Cleanup"
rm -rf /tmp/esf-smoke-claude /tmp/esf-smoke-conversation /tmp/esf-smoke-migrate /tmp/esf-smoke-shared
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
