# ESF Companion vault and repo separation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate the ESF Companion dev repo from the vault's daily runtime so dev edits do not change runtime, and move the repo from inside the vault to `~/projects/`.

**Architecture:** Three phases. Phase A prepares the repo on a feature branch (upstreams v0.7.0 to the Claude Code variant of `esf-project`, retargets `/esf-update` to follow tags, merges to main, tags `v0.7.0`). Phase B bootstraps the vault runtime by running the existing `/esf-update` once, which pulls the new tag-tracking version over itself. Phase C moves the repo to `~/projects/esf-companion/`, deletes the three vault symlinks, and cleans the path audit hits.

**Tech Stack:** bash, git, GitHub API, Claude Code skills (markdown SKILL.md files), Obsidian vault filesystem.

**Spec:** `docs/2026-05-12-vault-repo-separation-design.md`.

---

## File Structure

Files created or modified across the plan:

**Phase A (in the repo):**
- Modify: `.claude/skills/esf-project/SKILL.md` (add Nudge Mode and Gate Mode section structure with hybrid nudge, NUDGE-SELECTION buffer write, Session Memory row, Growth Snapshot line)
- Modify: `.claude/skills/esf-verify/SKILL.md` (sync drift from Cowork variant)
- Modify: `.claude/skills/esf-update/SKILL.md` (replace main curls with tag-resolved curls)
- Modify: `install.sh` (replace `TOOLKIT_BASE` main default with tag-resolved default)

**Phase B (vault):**
- Created by `/esf-update`: `~/Obsidian/.claude/skills/esf-{onboarding,project,verify,update,git,cognitive}/SKILL.md` (real files, no symlinks)

**Phase C (vault filesystem + ~/projects/):**
- Move: `~/Obsidian/Writing/epistemic-stewardship/esf-companion/` → `~/projects/esf-companion/`
- Delete: three symlinks under `~/Obsidian/.claude/skills/esf-{onboarding,project,verify}`
- Modify: `~/Obsidian/.claude/hooks/check-cross-file-consistency.sh:19`
- Modify: `~/Obsidian/.claude/settings.local.json` (drop dead entries)
- Delete: `~/Obsidian/Writing/epistemic-stewardship/.claude/settings.local.json`
- Modify: `~/Obsidian/Writing/workshops/repository/faculty/redesign-workflow-layer-ai/workshop.md:93`
- Archive: `~/Obsidian/.agents/skills/` → `~/Obsidian/Archive/2026-05-pre-separation-agents-skills-snapshot/`
- Create: `~/Obsidian/Writing/epistemic-stewardship/esf-companion.md` (pointer note)
- Create: temporary symlink `~/Obsidian/Writing/epistemic-stewardship/esf-companion` → `~/projects/esf-companion` (48 hours)
- Modify: `~/projects/README.md` (inventory)

**Verification model:** This is migration/refactor work, not feature development. Most tasks verify via existing smoke tests (`bash test/smoke-test.sh`) and manual bootstrap checks in Nathan's real vault environment. TDD-style failing-test-first does not apply.

---

## Phase A: Prepare the repo

### Task 1: Create feature branch

**Files:** None modified. Branch creation only.

- [ ] **Step 1: Verify clean working tree**

```bash
cd ~/Obsidian/Writing/epistemic-stewardship/esf-companion
git status
```

Expected: `On branch main. Your branch is up to date with 'origin/main'. Working tree clean.` (or only `.qwen/` untracked, which is fine).

- [ ] **Step 2: Create and check out the feature branch**

```bash
git checkout -b feature/v0.7.0-claude-code-variant-and-tag-based-update
```

Expected: `Switched to a new branch 'feature/v0.7.0-claude-code-variant-and-tag-based-update'`.

---

### Task 2: Upstream v0.7.0 hybrid nudge to Claude Code variant of esf-project

**Files:**
- Source (read): `platforms/cowork/skills/esf-project/SKILL.md` (Cowork variant, lines 284-345 carry the new Nudge Mode and Gate Mode section; lines 711-on carry the Session Memory and Growth Snapshot updates)
- Modify: `.claude/skills/esf-project/SKILL.md` (Claude Code variant; has Position Statement Gate at line 170 but no Nudge Mode section structure)

**Context note:** The Cowork variant has a parent section "Position Statement: Nudge Mode and Gate Mode" (line 284) with subsections "Nudge Mode (default)" (line 294) and Gate Mode behavior. The Claude Code variant has a flat "Position Statement Gate: CHECK THIS FIRST" section (line 170) with no separate Nudge Mode treatment. The port grafts the Nudge Mode structure into the Claude Code variant alongside its existing Gate content.

- [ ] **Step 1: Read both files end-to-end**

Read `platforms/cowork/skills/esf-project/SKILL.md` and `.claude/skills/esf-project/SKILL.md` fully. Map the Cowork variant's structure (Silence Mode → Demo Mode → Five Phases → Position Statement: Nudge Mode and Gate Mode → ... → Session Memory → Growth Snapshot) against the Claude Code variant's structure. Identify the exact insertion points for the new content.

- [ ] **Step 2: Port the Nudge Mode and Gate Mode parent section**

Insert a new section "## Position Statement: Nudge Mode and Gate Mode" in the Claude Code variant, immediately before the existing "## Position Statement Gate: CHECK THIS FIRST". Copy the parent section's framing paragraphs (PS lookup, Install hygiene) and the entire `### Nudge Mode (default)` subsection from Cowork lines 284-345 verbatim. The existing "Position Statement Gate: CHECK THIS FIRST" section becomes the Gate Mode subsection; either renumber it as `### Gate Mode` under the new parent, or leave it as-is and add a one-line pointer from the new section.

Excluded content (do NOT port):
- The `## Demo Mode` section (Cowork lines 211-269)
- Any references to `.esf-demo` manifest, Demo Mode behavior, or `/esf-demo`

- [ ] **Step 3: Port the Session Memory row**

In the Session Memory section of the Claude Code variant (line 727), add the row from the Cowork variant: "Nudge selection card fires" with the appropriate persistence behavior. Match the existing table format.

- [ ] **Step 4: Port the Growth Snapshot distribution line**

In the Growth Snapshot section of the Claude Code variant (line 794), add the line from the Cowork variant: "Nudge selection distribution: [N write-now / N talk-through / N skip-doc / N skip-session]".

- [ ] **Step 5: Sanity-check for Demo Mode leakage**

```bash
grep -nE "Demo Mode|\.esf-demo|/esf-demo|esf-demo" .claude/skills/esf-project/SKILL.md
```

Expected: no matches. If any match appears, remove the line and re-run.

- [ ] **Step 6: Sanity-check for hybrid nudge presence**

```bash
grep -cE "Nudge Mode|AskUserQuestion|NUDGE-SELECTION" .claude/skills/esf-project/SKILL.md
```

Expected: at least 3 matches (Nudge Mode heading, the AskUserQuestion call site, the NUDGE-SELECTION buffer write description).

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/esf-project/SKILL.md
git commit -m "feat(claude-code-skill): port v0.7.0 hybrid nudge from cowork variant

Adds Nudge Mode and Gate Mode parent section to .claude/skills/esf-project
with two-tier nudge behavior (inline first-touch + AskUserQuestion
selection card on structural-edit re-fire) and NUDGE-SELECTION buffer
write. Excludes Cowork-only Demo Mode and /esf-demo references.

Source: platforms/cowork/skills/esf-project/SKILL.md
Closes the v0.7.0 'untouched parallel Claude Code skill' open item
from 2026-05-06."
```

---

### Task 3: Sync esf-verify drift between variants

**Files:**
- Source (read): `platforms/cowork/skills/esf-verify/SKILL.md`
- Modify (if drift): `.claude/skills/esf-verify/SKILL.md`

The two variants differ by approximately 121 lines of diff output as of 2026-05-12. Some of that may be plugin-form vs skill-form differences that should NOT port (e.g., AskUserQuestion calls that are plugin-specific). Read both before porting.

- [ ] **Step 1: Inspect the diff**

```bash
diff -u .claude/skills/esf-verify/SKILL.md platforms/cowork/skills/esf-verify/SKILL.md | less
```

Read all the diff. For each block, decide:
- Behavioral change (port to Claude Code variant)
- Plugin-form-specific (skip; e.g., Cowork-only tool calls)
- Phrasing-only (port for consistency)

- [ ] **Step 2: Apply the port**

Edit `.claude/skills/esf-verify/SKILL.md` to incorporate the behavioral and phrasing changes. Do not introduce plugin-specific tool calls that have no Claude-Code skill equivalent.

- [ ] **Step 3: Sanity-check**

```bash
diff -u .claude/skills/esf-verify/SKILL.md platforms/cowork/skills/esf-verify/SKILL.md | grep -c "^+"
```

Expected: a small number (lines of remaining plugin-form-specific diff). If still large, re-inspect.

- [ ] **Step 4: Commit (skip if no changes)**

```bash
git add .claude/skills/esf-verify/SKILL.md
git commit -m "chore(claude-code-skill): sync esf-verify drift from cowork variant"
```

If nothing changed, skip the commit.

---

### Task 4: Modify /esf-update SKILL.md to pull from latest tag

**Files:**
- Modify: `.claude/skills/esf-update/SKILL.md`

Current state (lines 19-29):
```
1. Read the local version from `.claude/esf-version`.
2. Fetch the remote version from `https://raw.githubusercontent.com/nmadrid27/esf-companion/main/.claude/esf-version`. ...
4. If the user confirms the update, run:
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash -s -- --force --platform claude
```

Target state: replace `main` with a resolved latest tag in both curls. Add explicit fail-loud behavior on API failure.

- [ ] **Step 1: Edit step 2 of the SKILL.md**

Replace step 2 with:

```markdown
2. Fetch the latest release tag from the GitHub API:
   ```
   curl -fsSL https://api.github.com/repos/nmadrid27/esf-companion/tags
   ```
   Parse the response and pick the highest semver tag matching the `companion-vX.Y.Z` pattern (the dedicated namespace for Companion releases; older `vX.Y.Z` manuscript tags and `cowork-vX.Y.Z` plugin tags are intentionally excluded). Use version-sort, not lexicographic-sort: `companion-v0.10.0` must beat `companion-v0.9.0`. Store it as `LATEST_TAG` (e.g., `companion-v0.7.0`).

   If the API call fails (rate limit, network error, malformed response, or no matching tags returned), tell the user:
   > "Could not resolve the latest companion-vX.Y.Z release tag from GitHub. Aborting update. Try again later, or run the installer manually with --force --source <path> against a local clone."
   Stop. Do not fall back to `main`.

3. Fetch the remote version from `https://raw.githubusercontent.com/nmadrid27/esf-companion/<LATEST_TAG>/.claude/esf-version`. If that fetch fails, abort with the same message.
```

Renumber the existing steps 3 and 4 to 4 and 5.

- [ ] **Step 2: Edit step 5 (the install curl)**

Replace the install command with:

```markdown
5. If the user confirms the update, run:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/<LATEST_TAG>/install.sh | bash -s -- --force --platform claude
   ```
   The `<LATEST_TAG>` is the tag resolved in step 2 (e.g., `companion-v0.7.0`). The `--force` flag skips interactive prompts unnecessary during an update. The `--platform claude` flag ensures the full Claude Code install path runs.
```

- [ ] **Step 3: Verify the file reads cleanly**

```bash
cat .claude/skills/esf-update/SKILL.md
```

Confirm steps flow 1 → 2 → 3 → 4 → 5 → 6 with no broken numbering.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/esf-update/SKILL.md
git commit -m "feat(esf-update): pull from latest tag instead of main

Replaces main-tracking curls with GitHub-API-resolved latest tag.
Fail-loud on API failure (no silent fallback to main). The vault
runtime now follows releases, not whatever happens to be on main."
```

---

### Task 5: Modify install.sh TOOLKIT_BASE to default to latest tag

**Files:**
- Modify: `install.sh` (lines 81-83)

Current state:
```bash
if [ -n "$SOURCE_DIR" ]; then
  TOOLKIT_BASE="file://$(cd "$SOURCE_DIR" && pwd)"
else
  TOOLKIT_BASE="https://raw.githubusercontent.com/nmadrid27/esf-companion/main"
fi
```

Target state: when no `--source` is provided, resolve `LATEST_TAG` from GitHub API and use `https://raw.githubusercontent.com/nmadrid27/esf-companion/<LATEST_TAG>` instead of `/main`. Same fail-loud behavior as `/esf-update`.

- [ ] **Step 1: Add a tag-resolution function**

Near the top of `install.sh` (after the existing helper functions, before `TOOLKIT_BASE` is set), add:

```bash
resolve_latest_tag() {
  local api_response
  api_response=$(curl -fsSL https://api.github.com/repos/nmadrid27/esf-companion/tags 2>/dev/null) || return 1
  local tag
  tag=$(echo "$api_response" | grep -oE '"name": *"companion-v[0-9]+\.[0-9]+\.[0-9]+"' | grep -oE 'companion-v[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
  if [ -z "$tag" ]; then
    return 1
  fi
  echo "$tag"
}
```

The picker matches only `companion-vX.Y.Z` tags (the dedicated namespace for Companion releases). Older `vX.Y.Z` manuscript tags and `cowork-vX.Y.Z` plugin tags are intentionally excluded. `sort -V` does proper version-sort so `companion-v0.10.0` beats `companion-v0.9.0`. If no matching tag exists, the function returns failure and the caller aborts.

- [ ] **Step 2: Update the TOOLKIT_BASE assignment**

Replace lines 81-83 (the `if [ -n "$SOURCE_DIR" ]` block) with:

```bash
if [ -n "$SOURCE_DIR" ]; then
  TOOLKIT_BASE="file://$(cd "$SOURCE_DIR" && pwd)"
else
  RESOLVED_TAG=$(resolve_latest_tag) || {
    echo "Error: could not resolve latest release tag from GitHub API." >&2
    echo "Try again later, or run installer with --source <path> against a local clone." >&2
    exit 1
  }
  TOOLKIT_BASE="https://raw.githubusercontent.com/nmadrid27/esf-companion/${RESOLVED_TAG}"
fi
```

- [ ] **Step 3: Update line 187 (SETUP_URL)**

Find the line `SETUP_URL="https://raw.githubusercontent.com/nmadrid27/esf-companion/main/setup-repo.sh"` and change `main` to `${RESOLVED_TAG:-main}`. The fallback to main is for the `--source` code path (which sets `TOOLKIT_BASE` to `file://` and does not touch `RESOLVED_TAG`); when `setup-repo.sh` is fetched, it should still come from a real version.

Actually, simpler: only update SETUP_URL inside the no-source branch. If a smoke test using `--source` needs setup-repo.sh, it should also be passed locally. Adjust to:

```bash
# Inside the same `else` branch in step 2 above:
  SETUP_URL="https://raw.githubusercontent.com/nmadrid27/esf-companion/${RESOLVED_TAG}/setup-repo.sh"
```

Move the SETUP_URL definition into the no-source branch if it currently sits outside.

- [ ] **Step 4: Verify install.sh still parses**

```bash
bash -n install.sh
```

Expected: no output (syntax OK). If any error, fix.

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat(install.sh): TOOLKIT_BASE defaults to latest companion-vX.Y.Z tag

Adds resolve_latest_tag() helper that queries GitHub API for the
highest companion-vX.Y.Z tag. Old vX.Y.Z manuscript tags and
cowork-vX.Y.Z plugin tags are excluded. TOOLKIT_BASE and SETUP_URL
use the resolved tag when --source is not provided. Aborts with a
clear error if the API call fails. --source path unchanged."
```

- [ ] **Step 6: Add CHANGELOG entry**

Edit `CHANGELOG.md`. Add a section under the appropriate header (typically a new `## [companion-v0.7.0]` block):

```markdown
## [companion-v0.7.0]

### Added
- v0.7.0 hybrid Position Statement nudge ported to the Claude Code variant of `esf-project` (the Cowork plugin variant has carried this since the 2026-05-06 release). Selection card on structural-edit re-fire, four options, NUDGE-SELECTION telemetry to `.session-buffer.md`, Growth Snapshot distribution line.

### Changed
- `/esf-update` and `install.sh` now pull from the latest `companion-vX.Y.Z` tag instead of `main`. The vault runtime now follows tagged releases rather than whatever happens to be on `main`. No action required by users; the transition is automatic on the next `/esf-update` run.

### Notes
- New tag namespace: `companion-vX.Y.Z`. Older `vX.Y.Z` and `cowork-vX.Y.Z` tags are retained but no longer matched by the release-resolution logic. They are kept for historical reference.
```

Commit:

```bash
git add CHANGELOG.md
git commit -m "docs: changelog for companion-v0.7.0"
```

---

### Task 6: Smoke test on the branch

**Files:**
- Run: `test/smoke-test.sh`

- [ ] **Step 1: Run the existing smoke test**

```bash
bash test/smoke-test.sh
```

Expected: existing smoke tests pass.

- [ ] **Step 2: Manual test — tag-resolution success path**

Before this test: at least one `companion-vX.Y.Z` tag must exist on the remote. If none yet exists, this test will fail by design (the resolver should abort). Either: (a) push the v0.7.0 tag first via Task 7's reordered flow, then re-run this test; or (b) push a temporary tag like `companion-v0.0.0-rc1` for the duration of the test and delete it after.

In a scratch directory:

```bash
mkdir -p /tmp/esf-tag-test && cd /tmp/esf-tag-test
bash ~/Obsidian/Writing/epistemic-stewardship/esf-companion/install.sh --force --platform claude
```

Expected: install runs, resolves a `companion-vX.Y.Z` tag (visible in echoed `TOOLKIT_BASE` if debug-printed), pulls files from the tag path. If you do not see the tag echoed, add a temporary `echo "Using tag: $RESOLVED_TAG"` and re-run, then remove the echo.

- [ ] **Step 3: Manual test — tag-resolution failure path**

Simulate API failure by adding `https://api.github.com` to `/etc/hosts` as `127.0.0.1` temporarily, or by running the install with `HTTPS_PROXY=http://127.0.0.1:1` to force a connection error. Run install again.

Expected: install aborts with the "could not resolve latest companion-vX.Y.Z release tag" message. No silent fallback to main.

Remove the simulated failure after the test.

- [ ] **Step 4: Manual test — --source still works**

```bash
mkdir -p /tmp/esf-source-test && cd /tmp/esf-source-test
bash ~/Obsidian/Writing/epistemic-stewardship/esf-companion/install.sh --force --platform claude --source ~/Obsidian/Writing/epistemic-stewardship/esf-companion
```

Expected: install runs from the local checkout (no API call). This is the path the existing smoke test uses.

- [ ] **Step 5: Commit any test-infra changes (skip if none)**

If you added or modified anything in `test/`, commit it.

---

### Task 7: Tag, push, PR, merge (reordered for user safety)

**Files:** None modified in working tree. Git operations only.

**Order matters.** The tag is pushed BEFORE the PR is merged so that the `companion-v0.7.0` tag exists from the moment `main` contains the new tag-resolution code. Otherwise, any user running the new `install.sh` from `main` between merge and tag would abort (no matching tag) or pull a stale version.

- [ ] **Step 1: Push the branch**

```bash
git push -u origin feature/v0.7.0-claude-code-variant-and-tag-based-update
```

- [ ] **Step 2: Tag companion-v0.7.0 on the branch HEAD**

```bash
git tag companion-v0.7.0
```

The tag points at the feature branch's HEAD commit. This commit will become part of `main`'s history once the PR is merged with a merge commit (Step 6), so the tag remains reachable from `main`. Do NOT use squash-merge; it produces a new commit that the tag does not point at.

- [ ] **Step 3: Push the tag**

```bash
git push --tags
```

- [ ] **Step 4: Verify the tag is visible on GitHub**

```bash
curl -fsSL https://api.github.com/repos/nmadrid27/esf-companion/tags | grep -m1 '"name"'
```

Expected: `"name": "companion-v0.7.0"`.

- [ ] **Step 5: Open the PR**

```bash
gh pr create --title "feat: companion-v0.7.0 — port hybrid nudge to Claude Code variant + tag-based /esf-update" --body "$(cat <<'EOF'
## Summary

- Upstreams v0.7.0 hybrid nudge from the Cowork plugin variant to the Claude Code variant of `esf-project` (closes the 'untouched parallel Claude Code skill' open item from 2026-05-06).
- Syncs `esf-verify` drift between Cowork and Claude Code variants.
- Retargets `/esf-update` and `install.sh` from main-tracking to tag-tracking. New tag namespace: `companion-vX.Y.Z`. Older `vX.Y.Z` and `cowork-vX.Y.Z` tags are intentionally excluded by the new resolver. Fail-loud on API failure; no silent fallback to main.

## Why

The vault was running the Cowork variants via symlinks into the repo's working tree. Daily ESF runtime tracked uncommitted dev edits. This PR removes that hazard by giving the Claude Code variant feature parity (so `/esf-update` can take over) and shifting `/esf-update` to tagged releases.

Full design: `docs/2026-05-12-vault-repo-separation-design.md`.

## User impact

- Existing users: next `/esf-update` run pulls from `main` (old behavior) and installs the new tag-tracking version. All subsequent runs follow tagged releases. No action required.
- New users: `install.sh` from `main` resolves `companion-v0.7.0` (already pushed, see PR description) and installs from that tag.

## Merge requirement

**Use a merge commit, not squash.** The `companion-v0.7.0` tag points at this branch's HEAD; squash would create a new commit the tag does not reference.

## Test plan

- [x] `bash test/smoke-test.sh` passes
- [x] Manual: install resolves `companion-vX.Y.Z` tag and pulls from that path
- [x] Manual: install aborts cleanly on simulated API failure (no silent fallback)
- [x] Manual: `--source` path still works for local-clone testing
- [x] CHANGELOG entry for `companion-v0.7.0`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 6: Merge the PR with a merge commit (not squash)**

After review, merge:

```bash
gh pr merge --merge
```

The `--merge` flag uses a true merge commit. This preserves the feature-branch HEAD in main's history, so the `companion-v0.7.0` tag remains reachable from main. Do NOT use `--squash` or `--rebase`.

- [ ] **Step 7: Pull main locally and verify the tag is still reachable**

```bash
git checkout main
git pull
git log --oneline companion-v0.7.0..HEAD
git tag --contains companion-v0.7.0 | grep main >/dev/null && echo "tag in main ancestry" || echo "WARNING: tag not in main ancestry — investigate"
```

Expected: `companion-v0.7.0..HEAD` shows zero or a small number of commits (HEAD is at or just past the tag). The merge-base check confirms the tag is in main's history.

---

## Phase B: Bootstrap the vault runtime

### Task 8: Run /esf-update from vault root once

**Files:**
- Triggers: `~/Obsidian/.claude/skills/esf-{onboarding,project,verify,update,git,cognitive}/SKILL.md` (real files written by installer)

Before running: the three symlinks under `~/Obsidian/.claude/skills/` still point into the repo working tree. The existing `/esf-update` skill pulls from `main` (because the new version was just merged there). It will write real files at those paths, overwriting/replacing the symlinks with concrete files.

- [ ] **Step 1: Open a Claude Code session at the vault root**

```bash
cd ~/Obsidian && claude
```

- [ ] **Step 2: Run /esf-update**

In the session, run `/esf-update`. Confirm the update when prompted.

Expected: installer runs to completion. After completion, the new tag-tracking `/esf-update` is now the version on disk.

- [ ] **Step 3: Verify real files at skill paths**

```bash
ls -la ~/Obsidian/.claude/skills/esf-onboarding/SKILL.md ~/Obsidian/.claude/skills/esf-project/SKILL.md ~/Obsidian/.claude/skills/esf-verify/SKILL.md ~/Obsidian/.claude/skills/esf-update/SKILL.md
```

Expected: all four are regular files (the `l` permission marker is gone). File sizes are non-zero.

---

### Task 9: Verify the bootstrap via smoke test

**Files:** None modified. Manual verification only.

- [ ] **Step 1: Open a fresh Claude Code session in the vault**

Quit the previous session and reopen at `~/Obsidian`.

- [ ] **Step 2: Confirm ambient ESF block fires**

The session-start output should include the ESF Companion ambient status line. If it does not, investigate before proceeding.

- [ ] **Step 3: Trigger the hybrid nudge selection card**

Make a structural edit to any document under a context where no Position Statement exists yet. The first-touch inline nudge should appear. Make a second structural edit to the same document; the AskUserQuestion selection card with four options should fire.

Expected: behavior matches the v0.7.0 spec. If the inline nudge appears but the selection card does not, the port is incomplete; return to Task 2 Step 6 and re-check.

- [ ] **Step 4: Confirm silent_mode suppression**

Set `silent_mode: true` in `companion-state.md`. Re-trigger the same structural edit on a no-PS document. Expected: no inline nudge, no selection card. Reset `silent_mode` after the test.

This task is the bootstrap smoke test, not the full v0.7.0 validation suite. The full suite (NUDGE-SELECTION buffer write verification, /esf-demo sandbox creation/reset) remains deferred per the design's non-goals.

---

## Phase C: Move the repo and clean stale paths

### Task 10: Take a vault snapshot

**Files:** None. Backup operation.

- [ ] **Step 1: Trigger the vault's normal backup mechanism**

Run whatever produces the vault auto-backup (the `vault: 2026-05-12 ...` commits in git history). This provides a recovery point.

- [ ] **Step 2: Note the commit hash for rollback**

```bash
cd ~/Obsidian && git log -1 --format="%H %s"
```

Record the hash. If Phase C goes wrong, this is the rollback target.

---

### Task 11: Move the repo to ~/projects/

**Files:**
- Move: `~/Obsidian/Writing/epistemic-stewardship/esf-companion/` → `~/projects/esf-companion/`

- [ ] **Step 1: Verify ~/projects/ exists and esf-companion is not already there**

```bash
ls -d ~/projects/
ls -d ~/projects/esf-companion 2>/dev/null && echo "EXISTS — abort" || echo "ok, not present"
```

Expected: `~/projects/` exists; `~/projects/esf-companion` does not.

- [ ] **Step 2: Move the repo**

```bash
mv ~/Obsidian/Writing/epistemic-stewardship/esf-companion ~/projects/esf-companion
```

- [ ] **Step 3: Verify git remote and status still resolve**

```bash
cd ~/projects/esf-companion
git remote -v
git status
git log -1 --oneline
```

Expected: remote points at `github.com/nmadrid27/esf-companion`. Status is clean (or only `.qwen/` untracked). HEAD is the v0.7.0 merge commit.

---

### Task 12: Delete the three vault symlinks

**Files:**
- Delete: `~/Obsidian/.claude/skills/esf-onboarding`, `~/Obsidian/.claude/skills/esf-project`, `~/Obsidian/.claude/skills/esf-verify`

Wait. After Task 8, those paths were overwritten with real files (or were they? `curl -o` against a symlink replaces the symlink target's file, not the symlink itself). Verify before deleting.

- [ ] **Step 1: Check the current state of those three paths**

```bash
ls -la ~/Obsidian/.claude/skills/esf-onboarding ~/Obsidian/.claude/skills/esf-project ~/Obsidian/.claude/skills/esf-verify
```

Two cases:

**Case A (real files):** all three are regular files. Skip to Step 3.

**Case B (still symlinks pointing into old repo path):** the symlinks were not replaced because `curl -o` followed them and wrote into the linked location (which is now `~/projects/esf-companion/...`). The vault symlinks are now broken (point at a moved path).

- [ ] **Step 2: If Case B, remove the broken symlinks and re-run /esf-update**

```bash
rm ~/Obsidian/.claude/skills/esf-onboarding ~/Obsidian/.claude/skills/esf-project ~/Obsidian/.claude/skills/esf-verify
```

Then in a Claude Code session at `~/Obsidian`, run `/esf-update` again. The installer now writes real files at those paths.

- [ ] **Step 3: Verify all six ESF skills are real files**

```bash
for d in esf-onboarding esf-project esf-verify esf-update esf-git esf-cognitive; do
  ls -la ~/Obsidian/.claude/skills/$d/SKILL.md
done
```

Expected: all six are regular files, no `l` permission marker.

---

### Task 13: Update check-cross-file-consistency.sh hook path

**Files:**
- Modify: `~/Obsidian/.claude/hooks/check-cross-file-consistency.sh:19`

Current line: `ESF_COMPANION="$VAULT_DIR/Writing/epistemic-stewardship/esf-companion"`

Target: `ESF_COMPANION="$HOME/projects/esf-companion"`

- [ ] **Step 1: Edit the line**

In `~/Obsidian/.claude/hooks/check-cross-file-consistency.sh`, find line 19 and replace with:

```bash
ESF_COMPANION="$HOME/projects/esf-companion"
```

- [ ] **Step 2: Verify the hook still parses**

```bash
bash -n ~/Obsidian/.claude/hooks/check-cross-file-consistency.sh
```

Expected: no output.

- [ ] **Step 3: Smoke-test the hook by editing a file inside the moved repo**

In a Claude Code session, make a trivial edit (add a trailing newline) to any file inside `~/projects/esf-companion/`. The hook should fire without error and identify related files using the new path.

Expected: no hook error in session output.

---

### Task 14: Clean dead entries in ~/Obsidian/.claude/settings.local.json

**Files:**
- Modify: `~/Obsidian/.claude/settings.local.json`

The 2026-05-12 audit found six entries referencing the old vault path at lines 285, 286, 300, 306, 307, 362, 363, 369 (Read globs and Bash invocations).

- [ ] **Step 1: List the dead entries**

```bash
grep -n "Writing/epistemic-stewardship/esf-companion" ~/Obsidian/.claude/settings.local.json
```

- [ ] **Step 2: Remove each entry**

For each line returned, remove the entry from the JSON array. The entries are permission allow-list patterns that no longer match any real path. They will silently do nothing if left in place, but removing them keeps the settings honest.

- [ ] **Step 3: Verify JSON is still valid**

```bash
python3 -c "import json; json.load(open('$HOME/Obsidian/.claude/settings.local.json'))"
```

Expected: no output (valid JSON). If a JSONDecodeError appears, fix the trailing-comma or missing-bracket issue.

---

### Task 15: Delete Writing/epistemic-stewardship/.claude/settings.local.json

**Files:**
- Delete: `~/Obsidian/Writing/epistemic-stewardship/.claude/settings.local.json`

This file sat in the *parent* of the repo. Its absolute paths into the repo no longer resolve.

- [ ] **Step 1: Confirm contents are no longer needed**

```bash
cat ~/Obsidian/Writing/epistemic-stewardship/.claude/settings.local.json
```

Expected: entries reference `~/Obsidian/Writing/epistemic-stewardship/esf-companion/` paths that no longer exist.

- [ ] **Step 2: Delete the file**

```bash
rm ~/Obsidian/Writing/epistemic-stewardship/.claude/settings.local.json
```

- [ ] **Step 3: Remove the now-empty `.claude/` directory if appropriate**

```bash
rmdir ~/Obsidian/Writing/epistemic-stewardship/.claude 2>/dev/null || echo "directory not empty (other files present); leaving in place"
```

---

### Task 16: Fix workshop.md wikilink

**Files:**
- Modify: `~/Obsidian/Writing/workshops/repository/faculty/redesign-workflow-layer-ai/workshop.md:93`

Current line: `- Background: [[Writing/epistemic-stewardship/esf-companion/]]`

Target: a link that resolves. Options: (a) external URL to GitHub; (b) wikilink to the new vault pointer note created in Task 18.

- [ ] **Step 1: Pick the target**

Choose Option B if Task 18 creates the pointer note. Choose Option A if you prefer external. (Recommendation: Option B for consistency with vault wikilink conventions.)

- [ ] **Step 2: Edit the line**

```markdown
- Background: [[Writing/epistemic-stewardship/esf-companion]] (pointer note; repo moved to `~/projects/esf-companion/`)
```

- [ ] **Step 3: Verify**

Open the workshop.md in Obsidian and confirm the wikilink resolves to the pointer note (after Task 18 creates it).

---

### Task 17: Archive .agents/skills/ snapshot

**Files:**
- Archive: `~/Obsidian/.agents/skills/` → `~/Obsidian/Archive/2026-05-pre-separation-agents-skills-snapshot/`

26 stale skill directories from 2026-04-03. Nothing in active config reads from them.

- [ ] **Step 1: Confirm nothing references the path**

```bash
grep -rl "\.agents/skills" ~/Obsidian/.claude/ ~/.claude/ 2>/dev/null | grep -v "/cache/\|/projects/-Users-\|janitor-report"
```

Expected: empty (the only matches should be plugin caches and old worktree janitor reports, which are not active config).

- [ ] **Step 2: Move the directory**

```bash
mkdir -p ~/Obsidian/Archive
mv ~/Obsidian/.agents ~/Obsidian/Archive/2026-05-pre-separation-agents-snapshot
```

(Move the parent `.agents/` directory, not just `skills/` inside it. The whole `.agents/` is stale.)

- [ ] **Step 3: Verify the move**

```bash
ls -d ~/Obsidian/.agents 2>/dev/null && echo "STILL THERE — investigate" || echo "moved"
ls -la ~/Obsidian/Archive/2026-05-pre-separation-agents-snapshot/
```

---

### Task 18: Create vault pointer note

**Files:**
- Create: `~/Obsidian/Writing/epistemic-stewardship/esf-companion.md`

- [ ] **Step 1: Write the pointer note**

Create the file with this content:

```markdown
---
type: pointer
status: moved
moved-on: 2026-05-12
moved-to: ~/projects/esf-companion/
github: https://github.com/nmadrid27/esf-companion
---

# ESF Companion

This was the ESF Companion git repo's location until 2026-05-12. The repo moved out of the vault to `~/projects/esf-companion/` as part of the vault and repo separation (see `Writing/ai-workflow/logs/2026-05-12-esf-companion-vault-remote-review.md` for context and `Writing/epistemic-stewardship/esf-companion/docs/2026-05-12-vault-repo-separation-design.md` for the design).

**Where things live now:**

- Repo: `~/projects/esf-companion/`
- GitHub: https://github.com/nmadrid27/esf-companion
- Vault runtime: `~/Obsidian/.claude/skills/esf-{onboarding,project,verify,update,git,cognitive}/`
- Runtime is refreshed by `/esf-update`, which pulls from the latest tagged release.
- Tool artifacts (your ESF work product): `~/Obsidian/projects/[context]/esf/`
```

- [ ] **Step 2: Verify the wikilink from workshop.md resolves**

Open `Writing/workshops/repository/faculty/redesign-workflow-layer-ai/workshop.md` in Obsidian. Click the `[[Writing/epistemic-stewardship/esf-companion]]` link. It should resolve to this pointer note.

---

### Task 19: Add temporary back-pointing symlink

**Files:**
- Create (temporary): `~/Obsidian/Writing/epistemic-stewardship/esf-companion` → `~/projects/esf-companion`

Wait. Task 18 just created `~/Obsidian/Writing/epistemic-stewardship/esf-companion.md` (a regular file, not a directory). A symlink at `~/Obsidian/Writing/epistemic-stewardship/esf-companion` (no `.md`) would be a different filesystem entry. Verify both can coexist.

- [ ] **Step 1: Verify the pointer note has a `.md` extension**

```bash
ls ~/Obsidian/Writing/epistemic-stewardship/esf-companion*
```

Expected: one entry — `esf-companion.md`. Nothing at `esf-companion` (no extension).

- [ ] **Step 2: Create the symlink**

```bash
ln -s ~/projects/esf-companion ~/Obsidian/Writing/epistemic-stewardship/esf-companion
```

Now there are two entries: the pointer note `.md` file and the back-pointing symlink (a directory-like target).

- [ ] **Step 3: Verify the symlink resolves**

```bash
ls -la ~/Obsidian/Writing/epistemic-stewardship/esf-companion
ls ~/Obsidian/Writing/epistemic-stewardship/esf-companion/
```

Expected: the first shows the symlink. The second shows the contents of `~/projects/esf-companion/`.

Note: this symlink is temporary insurance. Remove it in Task 21 after 48 hours of clean operation.

---

### Task 20: Update ~/projects/README.md inventory

**Files:**
- Modify: `~/projects/README.md`

- [ ] **Step 1: Read the current inventory**

```bash
head -60 ~/projects/README.md
```

Identify the inventory table or list.

- [ ] **Step 2: Add esf-companion entry**

Add a row matching the existing format. Example:

```markdown
| esf-companion | `projects/esf-companion/` | Claude Code skills + Cowork plugin | Moved from vault 2026-05-12. GitHub: nmadrid27/esf-companion. |
```

Match the columns of the existing table.

- [ ] **Step 3: Verify**

```bash
grep "esf-companion" ~/projects/README.md
```

Expected: at least one match (the new row).

---

### Task 21: 48-hour cleanup — remove back-pointing symlink

**Files:**
- Delete: `~/Obsidian/Writing/epistemic-stewardship/esf-companion` (the temporary symlink)

Run this 48 hours after Task 19 only if no hook log, launchd plist, or vault session has referenced the old path during that window.

- [ ] **Step 1: Check for any references to the old path in logs**

```bash
# Adjust paths to your log locations
grep -r "Writing/epistemic-stewardship/esf-companion" ~/Obsidian/context/ 2>/dev/null | grep -v "2026-05-12\|pointer\|moved-on" | head -10
```

Expected: no matches (other than narrative entries that document the move itself, which are fine).

- [ ] **Step 2: If clean, remove the symlink**

```bash
rm ~/Obsidian/Writing/epistemic-stewardship/esf-companion
```

- [ ] **Step 3: Verify only the pointer note remains**

```bash
ls ~/Obsidian/Writing/epistemic-stewardship/esf-companion*
```

Expected: only `esf-companion.md`.

- [ ] **Step 4: Commit the vault state**

The vault state (settings.local.json edits, hooks edit, pointer note, removed symlink) is now stable. Let the vault's auto-backup commit catch up, or commit manually:

```bash
cd ~/Obsidian
git add .
git commit -m "chore: complete esf-companion vault/repo separation (2026-05-12)"
```

---

## Self-Review

Spec coverage check:

- Spec Goal 1 ("vault stops tracking uncommitted dev edits"): Tasks 8, 12 (symlinks replaced by real files).
- Spec Goal 2 ("dev work stops triggering vault writing-skill gates"): Tasks 10-11 (repo moved out of `Writing/`).
- Spec Goal 3 ("/esf-update follows tagged releases"): Tasks 4-5 (SKILL.md + install.sh tag-resolution), Task 7 (tag created).
- Spec Goal 4 ("reversible"): Task 10 (snapshot), Task 19 (back-pointing symlink for 48 hours).
- Spec Non-goal 1 ("variant consolidation"): not addressed; remains open per design.
- Spec Non-goal 2 ("/esf-demo Claude Code port"): not addressed per design.
- Spec Non-goal 3 ("full v0.7.0 validation suite"): Task 9 is a bootstrap smoke test only; full suite deferred per design.

All 15 design steps map to tasks above. Phase A maps to Tasks 1-7. Phase B maps to Tasks 8-9. Phase C maps to Tasks 10-21.

Placeholder scan: no TBD or TODO. Conditional steps (Task 3 Step 4 "skip if no changes", Task 6 Step 5 "skip if none") are scoped, not placeholders.

Type consistency: tag names (`v0.7.0`), branch name (`feature/v0.7.0-claude-code-variant-and-tag-based-update`), file paths, and the `LATEST_TAG` / `RESOLVED_TAG` variables are used consistently across Tasks 4, 5, 7.

---

## Disclosure

This plan was produced through human-AI collaboration. Nathan directed the move, the runtime model, the bootstrap approach, and the branch-versus-direct decision. AI ran the path audit, identified the variant-drift issue, structured the three phases, and drafted this plan in service of the spec at `docs/2026-05-12-vault-repo-separation-design.md`. The Five Questions were applied before saving.
