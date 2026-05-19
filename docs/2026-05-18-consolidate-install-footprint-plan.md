---
type: implementation-plan
date: 2026-05-18
status: draft
project: esf-companion
sources:
  - conversation 2026-05-18: scattered install footprint diagnosis
---

# Consolidate Install Footprint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the toolkit files the installer writes (prompts, templates, WORKFLOW.md, START_HERE.md, GEMINI.md, chatgpt-instructions.md) under `esf/toolkit/` so an install drops at most two visible folders (`esf/` and `.claude/`) plus `CLAUDE.md` into a user's project root, instead of scattering five top-level folders and 3–4 top-level files.

**Architecture:** Install destination only — the repo's source layout (`prompts/`, `templates/`, `WORKFLOW.md`, etc. at top) is unchanged so the README's Path-1 zero-install template download URLs keep working. The change is entirely in `install.sh` (where files land), `/esf-update` (which calls install.sh), the smoke test (which asserts the new paths), and all references in docs/skills/prompts that name those paths. A migration block in `install.sh` detects legacy installs and relocates them with a snapshot for rollback.

**Tech Stack:** bash, curl, python3 (already used by install.sh for settings.json merging), GitHub Releases for tagged version resolution.

---

## File Structure

**install.sh changes** (single file, ~80 lines added/changed):
- All `fetch_if_missing` and `curl ... -o` calls for prompts/templates/workflow/start-here change their destination.
- New `mkdir -p esf/toolkit/{prompts,templates}` replaces the old `mkdir -p prompts` and `mkdir -p templates`.
- New migration block (~40 lines) runs before any fetches.
- `git add` lines change to track new paths.
- Next-steps echo messages reference new paths.

**.claude/skills/esf-update/SKILL.md** — message text only; the curl-to-installer line is unchanged because install.sh handles the migration itself.

**test/smoke-test.sh** — every `[ -f templates/... ]` and `[ -f prompts/... ]` and `[ -f WORKFLOW.md ]` check moves to the new path. New test cases for the migration path.

**Documentation** (~60 path references across these files):
- README.md (Folder Structure section, install commands, Path 1 instructions)
- GETTING_STARTED.md, WALKTHROUGH.md, START_HERE.md (moving copy; also itself moves)
- WORKFLOW.md (moving copy; also itself moves)
- GEMINI.md, chatgpt-instructions.md (moving copies)
- docs/*.md (cohort-analysis, essentials, existing-work, getting-started, institutional-adoption, portability, what-is-esf, the two 2026-05-12 design/plan docs)
- prompts/*.md (companion, esf-companion, project-workflow, cowork, quick-start, README)

**Skills** (path references inside SKILL bodies that tell the model where to look for templates):
- `.claude/skills/esf-onboarding/SKILL.md` (4 refs)
- `.claude/skills/esf-project/SKILL.md` (6 refs)
- `.claude/reference/evolution-protocol.md` (1 ref)

**Agent file** — `.claude/agents/esf-companion.md` likely contains additional path references; grep before editing.

**Ambient block in install.sh** — already references `esf/[context]/...` paths only, no toolkit paths. No change needed, but verify.

---

### Task 1: Add migration test scaffolding to smoke test

**Files:**
- Modify: `test/smoke-test.sh` — add Test 6 (migration)

- [ ] **Step 1: Write the failing test**

Add at the end of `test/smoke-test.sh`, before the Cleanup section:

```bash
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
```

Also update the Cleanup section to remove the new temp dir:

```bash
rm -rf /tmp/esf-smoke-claude /tmp/esf-smoke-conversation /tmp/esf-smoke-migrate
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash test/smoke-test.sh`
Expected: Test 6 fails on every assertion (legacy files still at root, esf/toolkit doesn't exist, no snapshot).

- [ ] **Step 3: Commit the failing test**

```bash
git add test/smoke-test.sh
git commit -m "test: add migration scenario for esf/toolkit consolidation"
```

---

### Task 2: Update existing smoke test assertions to expect new paths

**Files:**
- Modify: `test/smoke-test.sh:69-72` (Test 1: Claude install assertions)
- Modify: `test/smoke-test.sh:132-137` (Test 2: Conversation install assertions)

- [ ] **Step 1: Update Test 1 path assertions**

Replace lines 69–72 with:

```bash
assert "START_HERE.md present in esf/toolkit"          "$([ -f esf/toolkit/START_HERE.md ] && echo 0 || echo 1)"
assert "WORKFLOW.md present in esf/toolkit"            "$([ -f esf/toolkit/WORKFLOW.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "esf/toolkit in git commit"                     "$(git show --name-only HEAD | grep -q 'esf/toolkit/' && echo 0 || echo 1)"
assert "esf-cognitive in git commit"                   "$(git show --name-only HEAD | grep -q 'esf-cognitive' && echo 0 || echo 1)"
```

- [ ] **Step 2: Update Test 2 path assertions**

Replace lines 132–137 with:

```bash
assert "install exits 0"                               "$EXIT"
assert "esf/toolkit/prompts/companion.md present"      "$([ -f esf/toolkit/prompts/companion.md ] && echo 0 || echo 1)"
assert "esf/toolkit/prompts/project-workflow.md"       "$([ -f esf/toolkit/prompts/project-workflow.md ] && echo 0 || echo 1)"
assert "esf/toolkit/templates/position-statement"      "$([ -f esf/toolkit/templates/position-statement-template.md ] && echo 0 || echo 1)"
assert "esf/toolkit/START_HERE.md present"             "$([ -f esf/toolkit/START_HERE.md ] && echo 0 || echo 1)"
assert "git commit created"                            "$(git log --oneline | grep -q 'Install ESF Companion' && echo 0 || echo 1)"
assert "esf/toolkit in git commit"                     "$(git show --name-only HEAD | grep -q 'esf/toolkit/' && echo 0 || echo 1)"
```

- [ ] **Step 3: Run smoke test to verify it now fails on the path expectations**

Run: `bash test/smoke-test.sh`
Expected: Test 1 and Test 2 fail on the new path assertions (because install.sh still writes to old paths). Test 6 still fails. This is the red-bar state we want before touching install.sh.

- [ ] **Step 4: Commit**

```bash
git add test/smoke-test.sh
git commit -m "test: expect esf/toolkit install paths"
```

---

### Task 3: Add migration block to install.sh

**Files:**
- Modify: `install.sh` — insert migration block after the install-directory resolution (around line 189), BEFORE the `Check for git repo` block.

- [ ] **Step 1: Write the migration block**

Insert this block in `install.sh` immediately after the install-directory resolution (after the `fi` closing the `if [ "$FORCE" != true ]` block that resolves `$DIR_CHOICE`, around line 189):

```bash
# ─── Migration: relocate legacy install footprint into esf/toolkit/ ────
# Older Companion installs (≤ v0.7.x) scattered prompts/, templates/,
# WORKFLOW.md, START_HERE.md, GEMINI.md, and chatgpt-instructions.md at
# the project root. We now consolidate those under esf/toolkit/ so the
# install drops a single visible folder. Detect legacy paths and move them.
LEGACY_PATHS=()
[ -d "prompts" ] && [ ! -d "esf/toolkit/prompts" ] && LEGACY_PATHS+=("prompts")
[ -d "templates" ] && [ ! -d "esf/toolkit/templates" ] && LEGACY_PATHS+=("templates")
[ -f "WORKFLOW.md" ] && [ ! -f "esf/toolkit/WORKFLOW.md" ] && LEGACY_PATHS+=("WORKFLOW.md")
[ -f "START_HERE.md" ] && [ ! -f "esf/toolkit/START_HERE.md" ] && LEGACY_PATHS+=("START_HERE.md")
[ -f "GEMINI.md" ] && [ ! -f "esf/toolkit/GEMINI.md" ] && LEGACY_PATHS+=("GEMINI.md")
[ -f "chatgpt-instructions.md" ] && [ ! -f "esf/toolkit/chatgpt-instructions.md" ] && LEGACY_PATHS+=("chatgpt-instructions.md")

if [ "${#LEGACY_PATHS[@]}" -gt 0 ]; then
  MIGRATION_DATE=$(date +%Y-%m-%d)
  SNAPSHOT_DIR="esf/.migration-snapshot-${MIGRATION_DATE}"
  echo ""
  echo -e "${YELLOW}Detected legacy Companion install layout. Migrating to esf/toolkit/...${NC}"
  mkdir -p "$SNAPSHOT_DIR"
  mkdir -p esf/toolkit
  for p in "${LEGACY_PATHS[@]}"; do
    cp -R "$p" "$SNAPSHOT_DIR/" 2>/dev/null || true
    if [ -d "$p" ]; then
      mv "$p" "esf/toolkit/$p"
    else
      mv "$p" "esf/toolkit/$p"
    fi
  done
  echo -e "  ${GREEN}Migrated: ${LEGACY_PATHS[*]} → esf/toolkit/${NC}"
  echo -e "  ${YELLOW}Snapshot for rollback: $SNAPSHOT_DIR${NC}"
fi
# ─── end migration ───
```

- [ ] **Step 2: Sanity-check the block in isolation (lint)**

Run: `bash -n install.sh`
Expected: no syntax errors.

- [ ] **Step 3: Run smoke test**

Run: `bash test/smoke-test.sh`
Expected: Test 6 partially passes (legacy paths now removed from root and present in `esf/toolkit/`). Test 6 idempotency assertion still passes because the second run detects no legacy paths (the migration condition checks both existence AND absence-of-new-path). Test 1 and Test 2 still fail because fresh installs still write to the OLD paths — that's Task 4.

- [ ] **Step 4: Commit**

```bash
git add install.sh
git commit -m "feat(install): migrate legacy footprint into esf/toolkit"
```

---

### Task 4: Redirect fresh-install fetches to esf/toolkit/ (Claude Code path)

**Files:**
- Modify: `install.sh:557-562` (mkdir block)
- Modify: `install.sh:663-690` (Claude Code path: fetch prompts and templates)
- Modify: `install.sh:700-704` (Claude Code path: WORKFLOW.md and START_HERE.md fetch)
- Modify: `install.sh:807-815` (git add lines in auto-commit)
- Modify: `install.sh:830-859` (next-steps echo messages)

- [ ] **Step 1: Update mkdir block (Claude Code path)**

Replace lines 557–562:

```bash
mkdir -p .claude/agents
mkdir -p .claude/skills/esf-onboarding
mkdir -p .claude/skills/esf-project
mkdir -p .claude/reference
mkdir -p esf/toolkit/prompts
mkdir -p esf/toolkit/templates
```

- [ ] **Step 2: Update prompts fetch block**

Replace lines 663–669 with:

```bash
echo "  Fetching prompts..."
fetch_if_missing "$TOOLKIT_BASE/prompts/companion.md" esf/toolkit/prompts/companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/esf-companion.md" esf/toolkit/prompts/esf-companion.md
fetch_if_missing "$TOOLKIT_BASE/prompts/project-workflow.md" esf/toolkit/prompts/project-workflow.md
fetch_if_missing "$TOOLKIT_BASE/prompts/cowork.md" esf/toolkit/prompts/cowork.md
fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" esf/toolkit/prompts/README.md
```

- [ ] **Step 3: Update templates fetch block**

Replace lines 671–689 with the same fetch lines but with `esf/toolkit/templates/` as the destination prefix:

```bash
echo "  Fetching templates..."
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" esf/toolkit/templates/position-statement-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" esf/toolkit/templates/position-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" esf/toolkit/templates/ai-use-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-lite-template.md" esf/toolkit/templates/ai-use-log-lite-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" esf/toolkit/templates/ai-use-log.md
fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" esf/toolkit/templates/companion-state-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/companion-notes-template.md" esf/toolkit/templates/companion-notes-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" esf/toolkit/templates/record-of-resistance-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" esf/toolkit/templates/record-of-resistance.md
fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" esf/toolkit/templates/five-questions-checklist.md
fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" esf/toolkit/templates/disclosure-statement.md
fetch_if_missing "$TOOLKIT_BASE/templates/evolution-log-template.md" esf/toolkit/templates/evolution-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/session-log-template.md" esf/toolkit/templates/session-log-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/reflection-template.md" esf/toolkit/templates/reflection-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-brief-template.md" esf/toolkit/templates/project-brief-template.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-plan.md" esf/toolkit/templates/project-plan.md
fetch_if_missing "$TOOLKIT_BASE/templates/project-scope-template.md" esf/toolkit/templates/project-scope-template.md
```

- [ ] **Step 4: Update WORKFLOW.md and START_HERE.md fetch block**

Replace lines 700–704 with:

```bash
if [ ! -f "esf/toolkit/WORKFLOW.md" ]; then
  curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o esf/toolkit/WORKFLOW.md
fi
fetch_if_missing "$TOOLKIT_BASE/START_HERE.md" esf/toolkit/START_HERE.md
```

- [ ] **Step 5: Update git auto-commit add lines**

Replace lines 807–811 with:

```bash
if [ -d ".git" ]; then
  git add .claude/ esf/toolkit/ 2>/dev/null
  [ -f .gitignore ] && git add .gitignore 2>/dev/null
  [ -f CLAUDE.md ]  && git add CLAUDE.md 2>/dev/null
  [ -f .claude/settings.json ] && git add .claude/settings.json 2>/dev/null
  # Snapshot dir from migration, if present
  [ -d "esf/.migration-snapshot-"* ] 2>/dev/null && git add esf/.migration-snapshot-* 2>/dev/null
```

- [ ] **Step 6: Update next-steps echo messages**

Replace lines 833–858 to point users at the new paths. Notably the `For a quick overview, read START_HERE.md` line and the closing `Installed to:` should point inside `esf/toolkit/`:

```bash
echo "  Installed to: $(pwd)"
echo "  Toolkit files: $(pwd)/esf/toolkit/"
echo ""
echo "──────────────────────────────────────"
echo -e "${CYAN}Next steps:${NC}"
echo ""

if [ "$SAMPLE" = true ]; then
  echo "  Sample data installed. Open Claude Code and try:"
  echo "     cd $(pwd) && claude"
  echo "  Then: \"I want to keep working on my responsive system.\""
  echo ""
  echo "  When you're ready to set up your own profile, run:"
  echo "     /esf-onboarding"
else
  echo "  1. Open Claude Code in your project folder:"
  echo "     cd $(pwd) && claude"
  echo ""
  echo "  2. Run onboarding to personalize your workspace:"
  echo "     /esf-onboarding"
  echo ""
  echo "  Onboarding takes about 5 minutes and sets up your identity,"
  echo "  project context, and folder structure."
  echo ""
  echo "  For a quick overview, read esf/toolkit/START_HERE.md"
  echo ""
  echo "  Starting a new project later? Re-run /esf-onboarding and say 'update'."
fi
```

- [ ] **Step 7: Lint and smoke test**

Run: `bash -n install.sh && bash test/smoke-test.sh`
Expected: Test 1 passes all new path assertions. Test 6 passes. Test 2 still fails (conversation path not yet updated — Task 5).

- [ ] **Step 8: Commit**

```bash
git add install.sh
git commit -m "feat(install): write Claude Code toolkit into esf/toolkit/"
```

---

### Task 5: Redirect fresh-install fetches to esf/toolkit/ (conversation/chatgpt/gemini/codex path)

**Files:**
- Modify: `install.sh:350-380` (Conversation-mode mkdir and fetches)
- Modify: `install.sh:383-396` (Platform-specific config: chatgpt, gemini, codex)
- Modify: `install.sh:399-407` (Conversation-mode git auto-commit)
- Modify: `install.sh:417-477` (Conversation-mode next-steps echo)

- [ ] **Step 1: Update mkdir and fetches in conversation path**

Replace lines 350–366 with:

```bash
  mkdir -p esf/toolkit/prompts
  mkdir -p esf/toolkit/templates

  echo "  Fetching companion prompts..."
  fetch_if_missing "$TOOLKIT_BASE/prompts/companion.md" esf/toolkit/prompts/companion.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/esf-companion.md" esf/toolkit/prompts/esf-companion.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/project-workflow.md" esf/toolkit/prompts/project-workflow.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/quick-start.md" esf/toolkit/prompts/quick-start.md
  fetch_if_missing "$TOOLKIT_BASE/prompts/README.md" esf/toolkit/prompts/README.md

  echo "  Fetching templates..."
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement-template.md" esf/toolkit/templates/position-statement-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/position-statement.md" esf/toolkit/templates/position-statement.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance-template.md" esf/toolkit/templates/record-of-resistance-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/record-of-resistance.md" esf/toolkit/templates/record-of-resistance.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log-template.md" esf/toolkit/templates/ai-use-log-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/ai-use-log.md" esf/toolkit/templates/ai-use-log.md
  fetch_if_missing "$TOOLKIT_BASE/templates/companion-state-template.md" esf/toolkit/templates/companion-state-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/companion-notes-template.md" esf/toolkit/templates/companion-notes-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/five-questions-checklist.md" esf/toolkit/templates/five-questions-checklist.md
  fetch_if_missing "$TOOLKIT_BASE/templates/disclosure-statement.md" esf/toolkit/templates/disclosure-statement.md
  fetch_if_missing "$TOOLKIT_BASE/templates/session-log-template.md" esf/toolkit/templates/session-log-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/reflection-template.md" esf/toolkit/templates/reflection-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/project-plan.md" esf/toolkit/templates/project-plan.md
  fetch_if_missing "$TOOLKIT_BASE/templates/project-scope-template.md" esf/toolkit/templates/project-scope-template.md
  fetch_if_missing "$TOOLKIT_BASE/templates/evolution-log-template.md" esf/toolkit/templates/evolution-log-template.md
```

- [ ] **Step 2: Update WORKFLOW.md and START_HERE.md in conversation path**

Replace lines 377–380 with:

```bash
  if [ ! -f "esf/toolkit/WORKFLOW.md" ]; then
    curl -fsSL "$TOOLKIT_BASE/WORKFLOW.md" -o esf/toolkit/WORKFLOW.md
  fi
  fetch_if_missing "$TOOLKIT_BASE/START_HERE.md" esf/toolkit/START_HERE.md
```

- [ ] **Step 3: Update platform-specific config destinations (chatgpt, gemini)**

Replace lines 383–396 with:

```bash
  # Platform-specific config file
  case "$PLATFORM" in
    chatgpt)
      echo "  Fetching ChatGPT custom instructions..."
      fetch_if_missing "$TOOLKIT_BASE/chatgpt-instructions.md" esf/toolkit/chatgpt-instructions.md
      ;;
    gemini)
      echo "  Fetching Gemini system prompt..."
      fetch_if_missing "$TOOLKIT_BASE/GEMINI.md" esf/toolkit/GEMINI.md
      ;;
    codex)
      echo "  Fetching Codex CLI agent config..."
      mkdir -p .codex
      fetch_if_missing "$TOOLKIT_BASE/.codex/AGENTS.md" .codex/AGENTS.md
      ;;
  esac
```

Note: `.codex/AGENTS.md` stays at `.codex/` — Codex CLI requires that path. This is intentional and matches `.claude/` and `CLAUDE.md` staying at root.

- [ ] **Step 4: Update conversation-mode git auto-commit**

Replace lines 399–408 with:

```bash
  # Auto-commit if in a git repo
  if [ -d ".git" ]; then
    git add esf/toolkit/ 2>/dev/null
    [ -f .gitignore ] && git add .gitignore 2>/dev/null
    [ -d .codex ] && git add .codex/ 2>/dev/null
    # Snapshot dir from migration, if present
    [ -d "esf/.migration-snapshot-"* ] 2>/dev/null && git add esf/.migration-snapshot-* 2>/dev/null
    git commit -m "Install ESF Companion ($PLATFORM)" --quiet 2>/dev/null && \
      echo -e "  ${GREEN}Companion files committed to git.${NC}" || true
  fi
```

- [ ] **Step 5: Update conversation-mode next-steps echo messages**

In the case block around lines 417–467, update every path reference:
- `chatgpt-instructions.md` → `esf/toolkit/chatgpt-instructions.md`
- `GEMINI.md` → `esf/toolkit/GEMINI.md`
- `prompts/quick-start.md` → `esf/toolkit/prompts/quick-start.md`
- `prompts/esf-companion.md` → `esf/toolkit/prompts/esf-companion.md`
- `templates/` folder → `esf/toolkit/templates/`
- `WORKFLOW.md` → `esf/toolkit/WORKFLOW.md`
- `START_HERE.md` → `esf/toolkit/START_HERE.md`

Also update lines 471–474:

```bash
  echo "  Templates are in esf/toolkit/templates/."
  echo "  The visual process diagram is in esf/toolkit/WORKFLOW.md."
  echo ""
  echo "  For a quick overview, read esf/toolkit/START_HERE.md"
```

- [ ] **Step 6: Lint and smoke test**

Run: `bash -n install.sh && bash test/smoke-test.sh`
Expected: All tests pass (1, 2, 3, 4, 5, 6).

- [ ] **Step 7: Commit**

```bash
git add install.sh
git commit -m "feat(install): write conversation-mode toolkit into esf/toolkit/"
```

---

### Task 6: Sweep doc references to old paths

**Files (read first, then edit):**
- `README.md`
- `GETTING_STARTED.md`
- `WALKTHROUGH.md`
- `START_HERE.md`
- `WORKFLOW.md`
- `chatgpt-instructions.md`
- `GEMINI.md`
- `docs/getting-started.md`
- `docs/essentials.md`
- `docs/existing-work.md`
- `docs/cohort-analysis.md`
- `docs/portability.md`
- `docs/institutional-adoption.md`
- `docs/what-is-esf.md`

- [ ] **Step 1: Generate the exact reference list to fix**

Run:

```bash
cd /Users/nathanmadrid/projects/esf-companion
grep -rn "templates/\|prompts/\|WORKFLOW.md\|START_HERE.md\|GEMINI.md\|chatgpt-instructions.md" \
  README.md GETTING_STARTED.md WALKTHROUGH.md START_HERE.md WORKFLOW.md \
  chatgpt-instructions.md GEMINI.md docs/*.md > /tmp/path-refs.txt
wc -l /tmp/path-refs.txt
cat /tmp/path-refs.txt
```

Expected: ~48 hits. Review the list. Two classes of reference exist:

1. **Repo source paths** in install instructions / Path 1 / GitHub URLs. These DO NOT change because the repo source layout is unchanged. Example: `Download templates/position-statement.md and templates/record-of-resistance.md from the [templates folder](https://github.com/.../templates)` — leave alone.
2. **User-facing post-install paths** ("Open templates/position-statement.md and fill it in"). These DO change to `esf/toolkit/templates/...`.

Discrimination rule: if the sentence is about the GitHub repo or download, keep root paths. If the sentence is about a file the user opens AFTER install, change to `esf/toolkit/...`.

- [ ] **Step 2: Update README.md Folder Structure section**

In README.md, around the `## Folder Structure (After Installer)` block (line ~255), replace the tree with:

```
your-project/
├── .claude/                            ← Claude Code configuration
│   ├── agents/esf-companion.md         ← AI companion identity
│   ├── skills/                         ← Onboarding, project workflow, git, verify, update, cognitive
│   └── reference/esf-guide.md          ← Framework reference
├── CLAUDE.md                           ← Ambient activation block
└── esf/
    ├── companion-state.md              ← Your identity and active contexts
    ├── companion-notes.md              ← Corrections the Companion applies every session
    ├── toolkit/                        ← The Companion's own files
    │   ├── prompts/                    ← Paste-anywhere system prompts
    │   ├── templates/                  ← Blank templates for each practice
    │   ├── WORKFLOW.md                 ← Process diagram
    │   └── START_HERE.md               ← First-read overview
    └── [your-context]/
        ├── briefs/                     ← Project briefs
        ├── position-statements/        ← Your direction (write this first)
        ├── records-of-resistance/      ← Your decisions about AI output
        ├── ai-use-logs/                ← What AI contributed
        └── logs/                       ← Session logs
```

- [ ] **Step 3: Update Path-1 wording in README.md**

Around lines 35–43, clarify that Path 1 downloads are about the GitHub repo source. After:

> 1. Download `templates/position-statement.md` and `templates/record-of-resistance.md` from the [templates folder](https://github.com/nmadrid27/esf-companion/tree/main/templates)
> 2. Copy `position-statement.md` into your current project folder

Add or refine:

> If you later run the installer, those same files will be set up for you at `esf/toolkit/templates/`. The GitHub download path and the installed path differ on purpose; the GitHub paths are the source of truth and easy to share as a URL.

- [ ] **Step 4: Sweep GETTING_STARTED.md, WALKTHROUGH.md, START_HERE.md, WORKFLOW.md**

For each file, run `grep -n "templates/\|prompts/\|WORKFLOW.md\|START_HERE.md"` and update every post-install user-facing path to `esf/toolkit/...`. Do not touch GitHub download URLs.

- [ ] **Step 5: Sweep chatgpt-instructions.md and GEMINI.md**

These are paste-source files the user reads. They reference templates and prompts the user will open after install. Update post-install path references to `esf/toolkit/...`.

- [ ] **Step 6: Sweep docs/*.md**

Open each:
- `docs/getting-started.md`
- `docs/essentials.md`
- `docs/existing-work.md`
- `docs/cohort-analysis.md`
- `docs/portability.md`
- `docs/institutional-adoption.md`
- `docs/what-is-esf.md`

Apply the same discrimination rule. The two existing design docs (`docs/2026-05-12-vault-repo-separation-{design,plan}.md`) are historical records — do not edit them.

- [ ] **Step 7: Verify no stale post-install paths remain in user-facing docs**

Run:

```bash
grep -n " templates/\| prompts/" README.md GETTING_STARTED.md WALKTHROUGH.md \
  START_HERE.md WORKFLOW.md docs/getting-started.md docs/essentials.md \
  docs/existing-work.md docs/portability.md docs/institutional-adoption.md \
  docs/what-is-esf.md chatgpt-instructions.md GEMINI.md 2>/dev/null
```

Expected: only hits should be GitHub repo URLs (lines containing `github.com` or "download") or repo source-tree references. If any user-facing "open `templates/foo.md`" remains, fix it.

- [ ] **Step 8: Commit**

```bash
git add README.md GETTING_STARTED.md WALKTHROUGH.md START_HERE.md WORKFLOW.md \
  chatgpt-instructions.md GEMINI.md docs/
git commit -m "docs: update post-install paths to esf/toolkit/"
```

---

### Task 7: Sweep skill and reference references to old paths

**Files:**
- Modify: `.claude/skills/esf-onboarding/SKILL.md` (4 refs at lines 371, 373, 375, 532, 558)
- Modify: `.claude/skills/esf-project/SKILL.md` (6 refs at lines 369, 401, 471, 561, 609, 835)
- Modify: `.claude/reference/evolution-protocol.md` (1 ref at line 56)
- Verify and possibly modify: `.claude/agents/esf-companion.md`
- Verify and possibly modify: `prompts/*.md`

- [ ] **Step 1: Update esf-onboarding SKILL.md**

Edit `.claude/skills/esf-onboarding/SKILL.md`:

- Line 371: `templates/companion-state-template.md` → `esf/toolkit/templates/companion-state-template.md`
- Line 373: `templates/companion-notes-template.md` → `esf/toolkit/templates/companion-notes-template.md`
- Line 375: same as 373
- Line 532: `templates/project-brief-template.md` → `esf/toolkit/templates/project-brief-template.md`
- Line 558: same as 532

- [ ] **Step 2: Update esf-project SKILL.md**

Edit `.claude/skills/esf-project/SKILL.md`:

- Line 369: `templates/project-plan.md` → `esf/toolkit/templates/project-plan.md`
- Line 401: `templates/ai-use-log-template.md` → `esf/toolkit/templates/ai-use-log-template.md`
- Line 471: `templates/project-scope-template.md` → `esf/toolkit/templates/project-scope-template.md`
- Line 561: `templates/record-of-resistance-template.md` → `esf/toolkit/templates/record-of-resistance-template.md`
- Line 609: `templates/reflection-template.md` → `esf/toolkit/templates/reflection-template.md`
- Line 835: `templates/session-log-template.md` → `esf/toolkit/templates/session-log-template.md`

- [ ] **Step 3: Update evolution-protocol.md**

Edit `.claude/reference/evolution-protocol.md:56`:

`templates/evolution-log-template.md` → `esf/toolkit/templates/evolution-log-template.md`

- [ ] **Step 4: Sweep esf-companion agent and prompts**

Run:

```bash
grep -n "templates/\|prompts/\|WORKFLOW.md\|START_HERE.md" \
  .claude/agents/esf-companion.md prompts/*.md
```

Apply the discrimination rule from Task 6 Step 1: only change user-facing post-install paths. GitHub-source references stay. For each hit, update or leave as appropriate.

- [ ] **Step 5: Verify**

Run the smoke test:

```bash
bash test/smoke-test.sh
```

Expected: all assertions pass. The smoke test greps inside skill content for behavior strings (not paths), so the path edits should not break existing assertions.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/ .claude/reference/ .claude/agents/ prompts/
git commit -m "feat(skills): reference esf/toolkit/templates/ for user-facing paths"
```

---

### Task 8: Update ambient block path examples in install.sh

**Files:**
- Modify: `install.sh:720-770` (the ambient block heredoc that gets written into CLAUDE.md)

- [ ] **Step 1: Verify whether the ambient block references any toolkit paths**

Run:

```bash
sed -n '720,770p' install.sh | grep -n "templates/\|prompts/\|WORKFLOW.md\|START_HERE.md"
```

Expected: zero hits. The ambient block uses `esf/[context]/...` paths exclusively. If there are hits, update them to `esf/toolkit/...`.

- [ ] **Step 2: If any hits, edit install.sh; if none, skip to commit**

(No commit needed if no edits.)

---

### Task 9: Update setup-repo.sh if it touches affected paths

**Files:**
- Verify: `setup-repo.sh`

- [ ] **Step 1: Check setup-repo.sh for path references**

```bash
grep -n "templates/\|prompts/\|WORKFLOW.md\|START_HERE.md\|GEMINI.md\|chatgpt-instructions" setup-repo.sh
```

- [ ] **Step 2: If hits exist, update them; if not, skip**

`setup-repo.sh` exists to create a git repo for new users — it likely does not touch toolkit paths, so this is a verification step. No expected edits.

---

### Task 10: Manual verification matrix

This task is not automatable through the smoke test. Run it from `/tmp/esf-manual-verify/`.

- [ ] **Step 1: Fresh install, Claude Code, project scope**

```bash
rm -rf /tmp/esf-manual-verify
mkdir -p /tmp/esf-manual-verify && cd /tmp/esf-manual-verify
git init -q -b main && git commit --allow-empty -q -m init
bash /Users/nathanmadrid/projects/esf-companion/install.sh \
  --force --platform claude --scope project \
  --source /Users/nathanmadrid/projects/esf-companion
ls -la
```

Expected at root: `.claude/`, `CLAUDE.md`, `esf/`, `.gitignore`, `.git/`, `.gitkeep`. **No** `prompts/`, `templates/`, `WORKFLOW.md`, `START_HERE.md` at root.

Expected inside `esf/`: `toolkit/` containing `prompts/`, `templates/`, `WORKFLOW.md`, `START_HERE.md`.

- [ ] **Step 2: Fresh install, conversation platform**

```bash
rm -rf /tmp/esf-manual-verify && mkdir -p /tmp/esf-manual-verify && cd /tmp/esf-manual-verify
git init -q -b main && git commit --allow-empty -q -m init
bash /Users/nathanmadrid/projects/esf-companion/install.sh \
  --force --platform conversation \
  --source /Users/nathanmadrid/projects/esf-companion
ls -la
```

Expected: similar root cleanliness; toolkit content under `esf/toolkit/`.

- [ ] **Step 3: Repeat for chatgpt, gemini, codex platforms**

For each, verify the platform-specific paste-source file lands at `esf/toolkit/chatgpt-instructions.md` or `esf/toolkit/GEMINI.md` (or `.codex/AGENTS.md` for codex, unchanged).

- [ ] **Step 4: Migration from legacy install**

```bash
rm -rf /tmp/esf-manual-verify && mkdir -p /tmp/esf-manual-verify && cd /tmp/esf-manual-verify
git init -q -b main
# Simulate legacy install: copy old layout from a tagged checkout
git clone --depth 1 --branch companion-v0.7.2 \
  https://github.com/nmadrid27/esf-companion.git /tmp/esf-legacy-checkout
cp -r /tmp/esf-legacy-checkout/templates /tmp/esf-legacy-checkout/prompts .
cp /tmp/esf-legacy-checkout/WORKFLOW.md /tmp/esf-legacy-checkout/START_HERE.md .
git add . && git commit -q -m "simulated legacy install"
# Now run the new installer
bash /Users/nathanmadrid/projects/esf-companion/install.sh \
  --force --platform claude --source /Users/nathanmadrid/projects/esf-companion
ls -la
ls esf/toolkit/
ls -d esf/.migration-snapshot-*
```

Expected: legacy folders/files gone from root; toolkit content now under `esf/toolkit/`; snapshot directory exists with copies of legacy paths.

- [ ] **Step 5: Sample install**

```bash
rm -rf /tmp/esf-manual-verify && mkdir -p /tmp/esf-manual-verify && cd /tmp/esf-manual-verify
git init -q -b main && git commit --allow-empty -q -m init
bash /Users/nathanmadrid/projects/esf-companion/install.sh \
  --force --platform claude --sample \
  --source /Users/nathanmadrid/projects/esf-companion
ls esf/
```

Expected: both `esf/toolkit/` AND `esf/build-course/` (sample data) coexist.

- [ ] **Step 6: Cleanup**

```bash
rm -rf /tmp/esf-manual-verify /tmp/esf-legacy-checkout
```

---

### Task 11: Update CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add a new version entry**

Add an entry at the top of CHANGELOG.md for `companion-v0.8.0` (or whatever the next version is per the existing pattern). Include:

```markdown
## v0.8.0 — 2026-05-XX

### Changed
- Install footprint consolidated: prompts, templates, WORKFLOW.md, START_HERE.md, GEMINI.md, and chatgpt-instructions.md now install under `esf/toolkit/` instead of scattering at the project root. Fresh installs drop two visible folders (`esf/`, `.claude/`) and one file (`CLAUDE.md`) into the project, instead of five folders and 3–4 files.
- Re-running the installer on a v0.7.x install auto-migrates legacy paths into `esf/toolkit/` and writes a rollback snapshot to `esf/.migration-snapshot-YYYY-MM-DD/`.

### Compatibility
- Repo source layout is unchanged. The Path-1 "download templates directly from GitHub" flow still works against the same URLs.
- All Companion skill references to user-facing template paths updated to `esf/toolkit/templates/...`. The skills do not break for users who haven't migrated yet, but the in-skill instructions will point at the new path.
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): consolidate install footprint into esf/toolkit"
```

---

### Task 12: Tag the release

This step happens at the end and follows the pattern established in `docs/2026-05-12-vault-repo-separation-design.md`: tag BEFORE the merge commit lands on main so anyone hitting the new resolver finds the tag immediately.

- [ ] **Step 1: Final smoke test on the feature branch**

```bash
cd /Users/nathanmadrid/projects/esf-companion
bash test/smoke-test.sh
```

Expected: all tests pass, including the new Test 6.

- [ ] **Step 2: Bump the version file**

```bash
echo "companion-v0.8.0" > .claude/esf-version
git add .claude/esf-version
git commit -m "chore: bump version to companion-v0.8.0"
```

- [ ] **Step 3: Tag the feature branch HEAD**

```bash
git tag companion-v0.8.0
```

DO NOT push the tag yet. Push happens after PR review per the established pattern.

- [ ] **Step 4: Open PR; on approval, push tag then merge with --merge**

This is a human-judgment step. The PR description should link this plan document and the design issue.

```bash
git push origin <feature-branch>
gh pr create --title "Consolidate install footprint into esf/toolkit" \
  --body "$(cat <<'EOF'
## Summary
- Installer now writes toolkit files under `esf/toolkit/` instead of scattering at project root
- Re-running the installer on v0.7.x installs auto-migrates legacy paths with a rollback snapshot
- Source repo layout unchanged so Path-1 GitHub download URLs keep working

## Test plan
- [x] `bash test/smoke-test.sh` passes including new Test 6 (migration)
- [x] Manual: fresh install all 6 platforms — toolkit under `esf/toolkit/`
- [x] Manual: legacy install migration with rollback snapshot present
- [x] Manual: sample install — toolkit and sample context coexist

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
# After approval:
git push origin companion-v0.8.0
gh pr merge --merge
```

---

## Self-Review

**Spec coverage:**
- Consolidate install destination: Tasks 4, 5 ✓
- Auto-migrate legacy installs: Tasks 1, 3 ✓
- Folder name `esf/toolkit/`: used throughout ✓
- Don't break Path-1 zero-install: Task 6 Step 3 calls this out explicitly ✓
- Update skill references: Task 7 ✓
- Update doc references: Task 6 ✓
- Verification: Tasks 1, 10 ✓
- Release hygiene: Tasks 11, 12 ✓

**Placeholder scan:** No TBDs or "implement later" found.

**Type/path consistency:**
- `esf/toolkit/` used everywhere (not `esf/_toolkit/` or `esf/companion/`).
- `esf/.migration-snapshot-${MIGRATION_DATE}` used consistently in Tasks 1 and 3.
- `companion-v0.8.0` is a placeholder version label — the engineer running this should verify the actual next version against the latest tag at time of work.

**Known footguns flagged in the plan:**
- The migration block runs on every install, not just updates. Idempotency is guarded by the `[ ! -d "esf/toolkit/..." ]` condition. If a user manually creates `esf/toolkit/` empty before running, the migration won't fire on legacy paths. That's an unusual case; not worth defending against.
- Test 6 asserts a snapshot directory exists. The glob expansion in `ls -d esf/.migration-snapshot-*` can match nothing on day-of-test if the date changes between snapshot creation and test assertion (extremely unlikely; happens only across midnight). Acceptable.
- `cp -R "$p" "$SNAPSHOT_DIR/"` in the migration block uses `cp -R` to preserve directories. If the source is a single file, `cp -R` still works (copies the file).

## Execution Handoff

Plan complete and saved to `docs/2026-05-18-consolidate-install-footprint-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session, batch with checkpoints for review.

Which approach?
