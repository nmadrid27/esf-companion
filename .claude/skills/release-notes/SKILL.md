---
name: release-notes
description: Draft the next CHANGELOG [Unreleased] section from Conventional Commits since the latest companion-v* tag, then hand off to scripts/release.sh. Use when preparing a release or when release-drift shows unreleased work.
disable-model-invocation: true
allowed-tools: Bash, Read, Edit
---

<!--
MAINTAINER-ONLY dev skill. Not shipped by install.sh, not managed by /esf-update.
Edit freely. Lives only in the source repo to support the release workflow.
-->

Draft the next release's CHANGELOG entries for a maintainer. You assemble and propose the notes; the maintainer reviews them and runs `scripts/release.sh` to actually cut the release. You never tag, push, or publish.

## Steps

1. **Find the unreleased commits.** Run:
   ```bash
   bash scripts/release-drift.sh
   ```
   This prints `drift=N` and the one-line commits since the latest `companion-v*` tag. If `drift=0`, stop and tell the maintainer there is nothing to release.

2. **Read the current CHANGELOG.** Read the top of `CHANGELOG.md`, including the existing `## [Unreleased]` section. Anything already written there is intentional; merge with it, do not discard it.

3. **Group commits by Conventional Commit type.** Map prefixes to CHANGELOG headings:
   - `feat:` -> **Added** (or **Changed** if it modifies existing behavior)
   - `fix:` -> **Fixed**
   - `docs:`, `chore:`, `refactor:`, `test:`, `ci:` -> usually omit from user-facing notes unless the change affects what users install or run. When in doubt, ask the maintainer rather than padding the notes.
   Rewrite each kept commit as a user-facing line: what changed and why it matters to someone using the toolkit, not the internal diff. Match the repo's CHANGELOG voice: terse, active, no em dashes.

4. **Propose the section.** Show the maintainer the drafted entries grouped under `## [Unreleased]`. Flag anything ambiguous (a commit you could not classify, a breaking change, a feat that might be a fix). Do not invent entries that no commit supports.

5. **On approval, write it.** Edit `CHANGELOG.md` so the approved entries sit under `## [Unreleased]`. Do not add a dated version heading; `scripts/release.sh` dates the section and opens a fresh empty `[Unreleased]` when the release is cut.

6. **Hand off.** Remind the maintainer of the release command and that minor bump = new features, patch = fixes:
   ```bash
   scripts/release.sh companion-vX.Y.Z --dry-run   # preview
   scripts/release.sh companion-vX.Y.Z             # then for real
   ```

## Guardrails

- Relay real commits only. If `release-drift.sh` shows nothing, there are no notes to write.
- Never run `release.sh`, `git tag`, `git push`, or `gh release` yourself. Drafting notes and cutting a release are separate acts; the maintainer owns the second.
- Preserve existing `[Unreleased]` content. You add to it; you do not rewrite history the maintainer already recorded.
