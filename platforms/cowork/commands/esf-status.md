---
description: Show current ESF project status snapshot
allowed-tools: Read, Glob
---

Display a one-screen status snapshot of the current ESF project. Follow this sequence.

## Step 1: Read companion-state.md

Search for `companion-state.md` using a two-pass shallow glob: first `companion-state.md` at root, then `*/companion-state.md` one level deep. Ignore matches whose path contains `sample/`, `examples/`, or `templates/`. If not found, tell the user: "No ESF workspace found in this folder. Run `/esf-start` to set one up." Stop.

If found, read it and extract: project name, current phase, last session date.

## Step 2: Check Project Artifacts

Using the project name and context from `companion-state.md`, check for the following. Note what exists and what is missing.

| Artifact | Check |
|----------|-------|
| Project brief | `projects/*/briefs/*.md` |
| Position Statement | `projects/*/position-statements/*.md` |
| Records of Resistance | `projects/*/records-of-resistance/*.md` — count entries |
| AI Use Log | `projects/*/ai-use-logs/*.md` |
| Session logs | `projects/*/logs/session-*.md` — count and find most recent |
| Active session buffer | `projects/*/logs/.session-buffer.md` |

Read the brief frontmatter to find: RoR minimum required, position-statement setting (required / optional / not-required), five-questions setting.

## Step 3: Display the Snapshot

Present in this format:

---

**ESF Status — [Project Name]**

Phase: [current phase] ([phase number]/5)
Last session: [date] — [brief note if available]

Position Statement: [exists at path / NOT YET WRITTEN]
Records of Resistance: [N] documented[, minimum [M] required] / [not required]
AI Use Log: [exists / not started]
Session logs: [N] saved / most recent [date]

**What's next:** [one sentence orienting the user to their immediate next action based on current phase and missing artifacts]

After displaying the snapshot, use `mcp__cowork__present_files` to surface the project brief and Position Statement (if they exist) as clickable cards so the user can quickly reference them.

---

## Step 4: Add a Context Note

If there is an active session buffer from an interrupted session, add:

> "You have an unsaved session buffer from a previous session. Run `/esf-log` to save it before starting new work."

If the Position Statement does not exist and the current phase is Explore or later, add:

> "Your Position Statement is missing. The ESF workflow requires it before Phase 3. Run `/esf-start` to review your setup."

If the RoR count is below the required minimum and the user is in Phase 4 or 5, add:

> "You have [N] Records of Resistance. Your brief requires [M]. Document at least [M - N] more before submitting."
