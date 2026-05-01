---
description: Save session log and update project state
allowed-tools: Read, Write, Edit, Glob
---

Run end-of-session synthesis: save the session log, update PROJECT.md, and clear the session buffer.

**All files are written to the user's selected folder.** Every Write, Edit, and Glob call targets paths relative to the workspace root (the folder the user selected in Cowork). Never write to temporary or sandbox paths.

## Step 1: Read the Session Buffer

Glob for `projects/*/logs/.session-buffer.md` in the selected folder. Ignore any matches under `sample/`, `examples/`, or `templates/`.

If no session buffer exists, check if there is recent session activity to synthesize from the current conversation context.

If nothing exists to synthesize, tell the user: "No session activity found to log. The buffer is empty." Stop.

## Step 2: Generate the Session Log

Synthesize the session buffer into a session log entry using this template:

```markdown
---
type: session-log
project: [project name]
date: [today's date]
phase: [phase at end of session]
---

# Session Log: [today's date]

## What we worked on

[2-4 sentences summarizing the main activity: what phase, what the user built or explored, what decisions were made]

## Phase progress

- Started this session: [phase at session start]
- Ended this session: [phase at session end]
- Phase gate cleared: [yes / no / not applicable]

## Position Statement status

- [unchanged / updated to v[N], reason: brief note]

## Five Questions (if completed this session)

| Question | Response |
|----------|----------|
| Can I defend this? | [Y / N / partial] |
| Is this mine? | [Y / N / partial] |
| Did I verify? | [Y / N / partial] |
| Would I teach this? | [Y / N / partial] |
| Is my disclosure honest? | [Y / N / partial] |

## Records of Resistance this session

- [count] documented
- [Brief description of each, or "none this session"]

## Drift observations

- [none / minor: note / significant: note]

## Prompt evolution

[One observation about how the user's prompting changed across this session: more specific, more directed, better constraints, etc. Observational, not evaluative.]

## Next session

- [2-3 specific items: what to work on, what to decide, what to finish]
```

Also draft an AI Use Log update from buffer entries only. Target the existing log at `projects/[context]/ai-use-logs/[project-name]-ai-use-log.md` (created during Phase 3 initialization). If the file is missing, create it from `templates/ai-use-log-template.md` before drafting the update. Do not fabricate beyond what the buffer supports.

Present both drafts to the user:

> "Here is your session log and AI Use Log update. Review them and edit anything that's off. I'll save them when you confirm."

## Step 3: Save After User Confirms

Once the user confirms (or makes edits and confirms), save:

- Session log → `projects/[context]/logs/session-[YYYY-MM-DD].md`
- AI Use Log update → append to `projects/[context]/ai-use-logs/[project-name]-ai-use-log.md`

## Step 4: Update PROJECT.md

Write or update `projects/[context]/PROJECT.md`:

```markdown
# Project: [name]

Phase: [current phase]
Position Statement: [one-line summary of current PS, with version if applicable]
Records of Resistance: [count] documented ([minimum] required by brief)
Last session: [date]. [Brief status note].
Next: [what to work on next session, pulled from session log "Next session" section]
```

## Step 5: Update companion-state.md

**Read `projects/_esf/companion-state.md` first.** If not found, check `companion-state.md` at root and `*/companion-state.md` one level deep for backwards compatibility. Ignore matches under `sample/`, `examples/`, or `templates/`.

Then use the Edit tool to update only the Phase and Last session fields in the Current Project block. Do not rewrite the entire file. Set Phase to the current phase and Last session to today's date with a brief note from the session log's "What we worked on" section.

## Step 6: Clear the Session Buffer

Use the Write tool to overwrite `projects/[context]/logs/.session-buffer.md` with an empty string (zero-byte file). Do not delete the file. Overwrite it so the path remains valid for the next session.

Confirm to the user:

> "Session logged and saved. Project state updated. See you next time."
