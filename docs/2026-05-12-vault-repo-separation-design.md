---
type: design-spec
date: 2026-05-12
status: draft
project: esf-companion
sources:
  - "[[2026-05-12-esf-companion-vault-remote-review]]"
  - "[[2026-05-07-esf-companion-v0.7.0-shipped-and-git-investigation]]"
  - "[[2026-05-06-esf-companion-v0.7.0-and-demo-addon]]"
  - "[[esf-project]]"
---

# Design: ESF Companion vault and repo separation

## Context

The ESF Companion currently lives in three overlapping forms inside Nathan's Obsidian vault.

1. **Dev repo.** A git checkout at `~/Obsidian/Writing/epistemic-stewardship/esf-companion/`, synced to `github.com/nmadrid27/esf-companion`. Local main is at `cf8ff91` as of 2026-05-12.
2. **Installed runtime.** Three symlinks at `~/Obsidian/.claude/skills/esf-{onboarding,project,verify}` point into the repo's working tree. Two of the three (`esf-project`, `esf-verify`) target the Cowork plugin variant under `platforms/cowork/skills/`. The third (`esf-onboarding`) targets the Claude Code variant under `.claude/skills/`.
3. **Tool artifacts.** Nathan's own ESF work product: `companion-state.md`, position statements, Records of Resistance, AI use logs, session buffers. These already live outside the repo, in `~/Obsidian/projects/[context]/esf/`.

Forms 1 and 2 are tangled. Dev edits to the repo's skill files immediately change the daily vault runtime through the symlinks. This created the v0.7.0 staging hazard recorded in `esf-project.md`: skill changes ship to Nathan's real sessions before they ship to GitHub. The 2026-05-12 remote/local review surfaced a related symptom: a working tree that looked dirty was actually byte-identical to origin, and `git pull --ff-only` refused on the stale index.

Hosting the repo inside the vault also crosses concerns that should stay apart. Vault writing-skill gates fire on code, configuration, and hook edits because the path lives under `Writing/**`. Vault auto-backup runs on the outer non-repo root and cannot see commit activity inside the nested repo. Vault sessions touch repo files for non-git reasons (rendering, plugin caches, scratch directories), which produces stale-index drift.

This design separates the three forms into three locations with three lifecycles.

## Goals

- The vault's daily ESF runtime stops tracking uncommitted dev edits.
- Dev work on the repo stops triggering vault writing-skill gates.
- `/esf-update` becomes the only path that changes vault runtime; it follows tagged releases, not whatever is on main.
- The move is reversible if anything breaks.

## Non-goals

- Consolidating the parallel Cowork and Claude Code variants of `esf-project` and `esf-verify`. This design ports v0.7.0 from Cowork to Claude Code once; the long-run drift question stays open.
- Porting `/esf-demo` to a Claude Code skill. It stays a Cowork plugin slash command.
- Running pre-release validation scenarios for v0.7.0 (silent_mode suppression, structural-edit selection card on a document with no Position Statement, NUDGE-SELECTION buffer write, /esf-demo sandbox creation and reset). These remain open from 2026-05-06 and are scheduled separately.

## Architecture after the move

Three concerns, three locations, three lifecycles.

| Concern | Location | Lifecycle |
|---|---|---|
| Repo (dev source) | `~/projects/esf-companion/` | Git checkout outside the vault. Dev edits, commits, and pushes happen here. |
| Vault runtime | `~/Obsidian/.claude/skills/esf-{onboarding,project,verify,update,git,cognitive}/SKILL.md` | Real files written by `/esf-update`. No symlinks. Refreshed on demand from the latest tag. |
| Tool artifacts | `~/Obsidian/projects/[context]/esf/` | Nathan's ESF work product. Already separate. No change. |

The runtime lifecycle changes in two ways.

First, the three vault symlinks are deleted. `/esf-update` writes real files at the same paths. The runtime is now an independent copy, not a live view into the repo.

Second, `/esf-update` shifts from main-tracking to tag-tracking, in a dedicated tag namespace. New releases use the prefix `companion-vX.Y.Z` (e.g., `companion-v0.7.0`). Older `vX.Y.Z` manuscript tags and `cowork-vX.Y.Z` plugin-specific tags are retained but no longer match the release resolver. The SKILL.md fetches the GitHub API tag list, picks the highest `companion-vX.Y.Z` tag by version-sort, and curls files from `raw.githubusercontent.com/nmadrid27/esf-companion/<tag>/...` instead of from `/main/...`. The same change applies to `install.sh`'s `TOOLKIT_BASE` default. The vault now follows tagged releases rather than whatever happens to be on main, and the namespace prevents the resolver from picking up old tags that semver-sort higher than current releases (e.g., `v1.6.0` would otherwise win against `companion-v0.7.0` on pure semver).

The variant question resolves by upstreaming. The hybrid nudge selection card and v0.7.0 Session Memory / Growth Snapshot additions live in `platforms/cowork/skills/esf-project/SKILL.md`. They get ported to `.claude/skills/esf-project/SKILL.md` as a single commit on a feature branch. Any drift between the Cowork and Claude Code variants of `esf-verify` gets the same treatment. The `## Demo Mode` section in the Cowork variant does not port; `/esf-demo` is a Cowork-only command.

## Phased plan

The work splits into three phases. Phase A and Phase C touch different surfaces and can be reasoned about independently. Phase B is the single bootstrap step that connects them.

### Phase A: prepare the repo (branch + PR + tag)

All work happens on a feature branch off `main`: `feature/v0.7.0-claude-code-variant-and-tag-based-update`. The branch isolates the dev work from main while it is in progress, so any `/esf-update` run during this phase still pulls a stable v0.6.x state.

1. **Upstream v0.7.0 to the Claude Code variant.** Port the hybrid nudge from `platforms/cowork/skills/esf-project/SKILL.md` to `.claude/skills/esf-project/SKILL.md`. Includes the two-tier Nudge Mode rewrite, the AskUserQuestion selection card with four options, the Re-fire ceiling, the NUDGE-SELECTION block written to `.session-buffer.md`, the Session Memory persistence table row, and the Growth Snapshot distribution line. Excludes the `## Demo Mode` section. Diff `esf-verify` between the two locations; if there is drift, sync it.
2. **Modify `/esf-update` to pull from latest tag.** Edit `.claude/skills/esf-update/SKILL.md`:
   - Replace step 2's curl of `.claude/esf-version` from main with a GitHub API call to `https://api.github.com/repos/nmadrid27/esf-companion/tags`. Pick the highest semver-sorted tag.
   - Replace step 4's curl of `install.sh` from main with the same tag-pinned path.
   - Add a failure path: if the API call fails or returns no tags, abort with a clear message. Do not silently fall back to main.
3. **Modify `install.sh` `TOOLKIT_BASE` default.** Same tag-resolution logic. Keep `--source <local-dir>` behavior unchanged for smoke testing.
4. **Smoke test on the branch.** `bash test/smoke-test.sh`. Manual test cases for the new tag-resolution logic: tag exists, no tags, API failure, tag matches local version.
5. **Tag `companion-v0.7.0` on the branch HEAD; push the tag.** `git tag companion-v0.7.0 && git push --tags`. Tagging before merge protects open-source users: anyone running the new `install.sh` from `main` between merge and tag would otherwise abort (no matching tag) or pull a stale version. With the tag pushed first, the tag exists from the moment `main` contains the new resolver code.
6. **Open PR, review, merge with a merge commit (not squash).** The tag points at the feature branch's HEAD. A squash-merge produces a new commit the tag does not reference; a true merge commit preserves the tagged commit in main's history. Use `gh pr merge --merge`.

### Phase B: bootstrap the vault runtime (one command, on demand)

Phase A produces the `companion-v0.7.0` tag with the new `/esf-update` baked in. The vault still runs the old main-tracking version. The bootstrap transitions the vault to the new world.

7. **Run the existing `/esf-update` from the vault root once.** The old skill pulls from main, which now contains the merged Phase A work. It writes real files at `~/Obsidian/.claude/skills/esf-{onboarding,project,verify,update,git,cognitive}/SKILL.md`. The new tag-tracking `/esf-update` overwrites the old main-tracking one in place. From this point forward, all `/esf-update` runs resolve and pull from the latest `companion-vX.Y.Z` tag.
8. **Verify the bootstrap.** Open a fresh Claude Code session in the vault. Confirm the ambient ESF block fires. Run a structural edit on a document with no Position Statement and confirm the hybrid nudge selection card appears. This is a smoke test for the bootstrap path, not the full v0.7.0 validation suite (which stays deferred per the non-goals).

The bootstrap depends on `main` containing the merged Phase A work and the `companion-v0.7.0` tag existing on the remote. Phase A's tag-before-merge ordering makes both true before any user (or the bootstrap itself) hits the new resolver. The window between tag-push and update-run is owned by Nathan, who runs `/esf-update` once he confirms the merge and tag are live on GitHub.

### Phase C: move the repo and clean stale paths

With the vault runtime now an independent copy, the repo can move without changing what the vault runs.

9. **Take a vault snapshot via normal backup.** Reversibility insurance.
10. **Move the repo.** `mv ~/Obsidian/Writing/epistemic-stewardship/esf-companion ~/projects/esf-companion`. Verify `git remote -v` and `git status` after the move.
11. **Delete the three vault symlinks.** `rm ~/Obsidian/.claude/skills/esf-{onboarding,project,verify}`. They were superseded by real files in Step 7; they would now point at nothing anyway.
12. **Path audit cleanups.** Seven hits surfaced in the 2026-05-12 audit.
    - `~/Obsidian/.claude/hooks/check-cross-file-consistency.sh:19`: change `ESF_COMPANION="$VAULT_DIR/Writing/epistemic-stewardship/esf-companion"` to `ESF_COMPANION="$HOME/projects/esf-companion"`.
    - `~/Obsidian/.claude/settings.local.json`: remove dead allow-list entries that reference the old vault path (six Read globs and Bash invocations on lines 285-369).
    - `~/Obsidian/Writing/epistemic-stewardship/.claude/settings.local.json`: delete the file. Its absolute paths into the repo no longer resolve, and the parent folder is no longer the repo's parent.
    - `~/Obsidian/Writing/workshops/repository/faculty/redesign-workflow-layer-ai/workshop.md:93`: replace the wikilink `[[Writing/epistemic-stewardship/esf-companion/]]` with a GitHub URL or a pointer-note wikilink.
    - `~/Obsidian/.agents/skills/`: archive the entire directory (26 stale skill copies from 2026-04-03) to `Archive/2026-05-pre-separation-agents-skills-snapshot/`. Nothing in active config reads from it.
13. **Leave a pointer note in the vault.** Create `~/Obsidian/Writing/epistemic-stewardship/esf-companion.md` with one paragraph: "Repo moved to `~/projects/esf-companion/` on 2026-05-12. GitHub: nmadrid27/esf-companion. Vault runtime installed via `/esf-update`."
14. **Add a temporary back-pointing symlink for 48 hours.** `ln -s ~/projects/esf-companion ~/Obsidian/Writing/epistemic-stewardship/esf-companion`. Anything that breaks because of a path I missed will resolve through the symlink and surface in error logs rather than failing silently. Remove the symlink after 48 hours if no hook log, launchd plist, or vault session has referenced the old path during that window.
15. **Update `~/projects/README.md`.** Add `esf-companion` to the inventory.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Tag-resolution logic fails (rate limit, network, malformed response) and `/esf-update` silently installs from main as a fallback. | Explicit fail-loud behavior in Step 2: abort on API failure with a clear message. Smoke test covers the failure cases. |
| Open-source users hit the new resolver in `install.sh` before any `companion-vX.Y.Z` tag exists, causing aborted installs. | Phase A tags `companion-v0.7.0` BEFORE merging the PR. The tag is reachable from main from the moment the merge commit lands. Window is zero. |
| The resolver picks an old `vX.Y.Z` manuscript tag (e.g., `v1.6.0`) instead of the current `companion-v0.7.0`, silently downgrading users. | Dedicated tag namespace. The resolver matches only `companion-vX.Y.Z`. Older `vX.Y.Z` and `cowork-vX.Y.Z` tags are retained for history but invisible to the resolver. |
| Path audit missed a hard-coded reference somewhere. | Temporary back-pointing symlink in Step 14 catches references for 48 hours. Errors surface in logs rather than failing silently. |
| Cowork and Claude Code variants of `esf-project` and `esf-verify` diverge again on the next feature. | Out of scope for this design. Flagged as an open architectural question below. |
| Untracked files in the repo (`.qwen/` and similar) follow the repo to `~/projects/`. | Either add to `.gitignore` during Phase A or accept; the move itself does not break. |
| Rollback. | Reversible at any phase. Phase A is on a branch until merged. Phase B is a one-command operation that produces files that can be deleted. Phase C is a `mv` that can be reversed. Vault snapshot in Step 9 covers the worst case. |

## Testing

- **Phase A, before merge.** `bash test/smoke-test.sh` passes. Manual: `/esf-update` correctly handles tag exists, no tags returned, API failure, and tag matches local version.
- **Phase B, after bootstrap.** Fresh Claude Code session in the vault. Ambient ESF block fires. Hybrid nudge selection card appears on a structural edit to a document with no Position Statement. `silent_mode: true` in `companion-notes.md` suppresses it.
- **Phase C, after move and symlink delete.** Trigger the cross-file-consistency hook on a file inside the moved repo to confirm it still fires. Open one ESF skill from the vault and confirm it loads as a real file (`ls -la` shows file, not symlink).
- **48 hours after move.** Check error logs for any hook or process that referenced the old path. Remove the temporary back-pointing symlink.

## Open architectural questions

These are outside the scope of this design but worth recording.

1. **Cowork vs Claude Code variant consolidation.** Two parallel sets of `esf-project` and `esf-verify` skills will continue to drift as long as new features land in one without explicit upstreaming to the other. A future design should pick one variant as canonical and either drop the other or generate it from the canonical source. Bigger work; deferred.
2. **Plugin-based distribution for the vault runtime.** Today the vault runs the Claude Code variant installed via `/esf-update`. The Cowork variant is meant to be loaded as a Claude Code plugin (marketplace or local). A future design could move the vault to plugin-based distribution and retire the install.sh-based path entirely. Larger scope; deferred.
3. **`/esf-demo` parity in the canonical path.** The Cowork plugin ships a `/esf-demo` slash command with a sample studio project. The canonical Claude Code install path does not. If colleagues adopt the Claude Code path and want to demo the tool, `/esf-demo` would need a skill-form port. Not in scope here.

## Disclosure

This design spec was produced through human-AI collaboration. Nathan directed the move, the runtime model, the bootstrap approach, and the branch-versus-direct decision. AI ran the path audit, identified the variant-drift issue, structured the three phases, and drafted this document. The Five Questions were applied before saving.
