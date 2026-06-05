---
description: Show current ESF project status snapshot
allowed-tools: Read, Glob
---

Display a one-screen status snapshot of the current ESF project. Follow this sequence.

## Step 1: Read companion-state.md

Search for `esf/companion-state.md` first. If not found, check `projects/_esf/companion-state.md` (legacy pre-v0.7 layout), `companion-state.md` at root, and `*/companion-state.md` one level deep for backwards compatibility. Ignore matches whose path contains `sample/`, `examples/`, or `templates/`. If not found, tell the user: "No ESF workspace found in this folder. Run `/esf-start` to set one up." Stop.

If found, read it and extract: project name, current phase, last session date.

## Step 2: Check Project Artifacts

Using the project name and context from `companion-state.md`, check for the following. Note what exists and what is missing.

| Artifact | Check |
|----------|-------|
| Project brief | `esf/*/briefs/*.md` |
| Position Statement | `esf/*/position-statements/*.md` |
| Records of Resistance | `esf/*/records-of-resistance/*.md` (count entries) |
| AI Use Log | `esf/*/ai-use-logs/*.md` |
| Session logs | `esf/*/logs/session-*.md` (count and find most recent) |
| Gate records | `esf/*/gate-records/*.md` (count entries) |
| Active session buffer | `esf/*/logs/.session-buffer.md` |

If no `esf/` artifacts are found, repeat these checks against the legacy `projects/*/` layout so workspaces not yet migrated to the v0.7+ structure still resolve.

Read the brief frontmatter to find: RoR minimum required, position-statement setting (required / optional / not-required), five-questions setting.

## Step 3: Display the Snapshot

Present in this format:

---

**ESF Status: [Project Name]**

Phase: [current phase] ([phase number]/5)
Last session: [date] ([brief note if available])

Position Statement: [exists at path / NOT YET WRITTEN]
Records of Resistance: [N] documented[, minimum [M] required] / [not required]
AI Use Log: [exists / not started]
Gate records: [N] saved
Session logs: [N] saved / most recent [date]

**What's next:** [one sentence orienting the user to their immediate next action based on current phase and missing artifacts]

After displaying the snapshot, surface the project brief and Position Statement (if they exist) so the user can quickly reference them. When the `mcp__cowork__present_files` tool is available, call it to render each as a clickable card. Otherwise, print the relative path of each file on its own line under a "Reference:" heading. Do not silently skip the surface.

---

## Step 4: Add a Context Note

If there is an active session buffer from an interrupted session, add:

> "You have an unsaved session buffer from a previous session. Run `/esf-log` to save it before starting new work."

If the Position Statement does not exist and the current phase is Explore or later, add:

> "Your Position Statement is missing. The ESF workflow requires it before Phase 3. Run `/esf-start` to review your setup."

If the RoR count is below the required minimum and the user is in Phase 4 or 5, add:

> "You have [N] Records of Resistance. Your brief requires [M]. Document at least [M - N] more before submitting."
