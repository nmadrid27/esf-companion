---
description: Initialize or resume an ESF project session
allowed-tools: Read, Write, Glob
---

Initialize or resume an ESF Companion session. Follow this sequence exactly.

**All files are created in the user's selected folder.** Every Write, Edit, and Glob call targets paths relative to the workspace root (the folder the user selected in Cowork). Never write to temporary or sandbox paths.

## Step 1: Check for companion-state.md

Search for `projects/_esf/companion-state.md` in the selected folder. If not found, also check `companion-state.md` at root and `*/companion-state.md` one level deep for backwards compatibility. Ignore any match whose path contains `sample/`, `examples/`, or `templates/`.

**If companion-state.md exists:**
Read it. Extract: user name/role, active contexts (courses or projects), current project name, current phase, and last session date. Then use AskUserQuestion with preview cards:

Question: "Welcome back, [name]. What would you like to do?"
- **Continue [project name]** — preview: "Phase [N]: [phase name]. Last session: [date] — [brief note]. [List the immediate next action based on current phase, e.g. 'Ready to move into Explore — your Position Statement is saved.']"
- **Start a new project** — preview: "Set up a new project from scratch. I'll ask about your brief, create the folder structure, and get you oriented to Phase 1."

If the user wants to continue: invoke the `esf-project` skill and proceed from the current phase.

If the user wants to start a new project: go to Step 3.

**If companion-state.md does not exist:**
Go to Step 2 (first-time setup).

---

## Step 2: First-Time Setup (New Users Only)

Greet the user and lead with a hands-on demonstration:

> "Welcome to the ESF Companion. Here's the core idea: **you write a short Position Statement before AI enters your project.** Then the Companion watches for drift between what you said and where the work is heading.
>
> Let me show you how it works. **Tell me about a project you're working on** — something where you're using or planning to use AI."

From their answer, infer:
- **Role:** student / educator / professional / independent creator
- **Discipline or field**
- **Context:** course name, project type, or client work
- **Current period:** quarter, semester, or date range

Walk them through writing a Position Statement using three questions: "What are you making?", "What matters most to you about this project?", "What should AI not touch?" Draft from their answers, read it back, confirm it sounds like them.

Then explain what the statement does:

> "That's your Position Statement. When we work together, I'll challenge your thinking and push on assumptions — but this statement is the anchor. If the work drifts from what you said here, I'll flag it and you decide what to do."

Then ask about scaffolding level using AskUserQuestion with preview cards:

Question: "How much guidance do you want as you work?"
- **Guided** — preview: "Full phase-by-phase walkthrough. I'll prompt you at every transition and offer thinking exercises between phases. Best for your first few projects."
- **Supported** — preview: "Check-ins at key moments. I'll surface drift and run ownership checks, but won't narrate every step."
- **Independent** — preview: "Minimal interruption. I'll flag significant drift and respond when you ask, but stay out of the way otherwise."

If they have a project (which they should, from the demo): go to Step 3. Carry the Position Statement and project info forward.
If they are just setting up: create `projects/_esf/companion-state.md` with their identity and an empty Current Project block, confirm it is saved, and tell them to run `/esf-start` again when they are ready.

---

## Step 3: Initialize a New Project

Ask:
1. "What's the name of this project?"
2. "Is there a project brief? If so, drop it into `projects/[course-or-context]/briefs/` and I'll read it. Or you can describe the project and I'll help you build a brief."

**If a brief exists:** Read it. Extract deliverables, AI use policy, timeline, ESF requirements (position-statement, five-questions frontmatter values). Summarize what you found: "Your brief calls for [deliverables]. Position Statement is [required/optional]. Records of Resistance minimum is [N or not specified]. Due: [date]."

**If no brief:** Ask 4 questions to build a minimal brief:
1. "What are you making?"
2. "What does done look like? What are the deliverables?"
3. "What's your deadline or key milestone?"
4. "Where is the line for AI on this project — what tasks do you want to keep human-only?"

Generate a minimal brief in markdown, present it, and ask: "Does this capture it? I'll save it to `projects/[context]/briefs/[project-name]-brief.md`."

---

## Step 4: Set Up Folder Structure

Create the following folders if they do not exist:

```
projects/
├── _esf/
├── [project-name]/
│   ├── briefs/
│   ├── position-statements/
│   ├── records-of-resistance/
│   ├── ai-use-logs/
│   ├── gate-records/
│   ├── reflections/
│   └── logs/
```

---

## Step 5: Update companion-state.md

Write or update `projects/_esf/companion-state.md` with the current project and set Phase to "Inquire". Use `templates/companion-state-template.md` as the starting structure:

```markdown
---
type: companion-state
last-updated: [today's date]
---

# ESF Companion State

## Identity

- **Name:** [name]
- **Preferred name:** [preferred name]
- **Role or program:** [student / educator / professional / independent creator]
- **Discipline or focus:** [field]
- **Current period:** [current quarter or date range]

## Active Contexts

[List of courses or project contexts with ESF requirements]

## Current Project

- **Context:** [course or project context]
- **Project name:** [project name]
- **Brief location:** `projects/[context]/briefs/[brief-file].md`
- **Position Statement:** `projects/[context]/position-statements/[project-name].md`
- **Phase:** Inquire
- **Last session:** [today's date] — Project initialized.
- **Scaffolding level:** [Guided / Supported / Independent]

## Preferences

- **silent_mode:** false

## Growth Record

None yet.
```

---

## Step 6: Initialize Phase Tracker and Orient

**Create the initial phase tracker** using TodoWrite. Set Phase 1 to `in_progress` and all others to `pending`. If a brief was loaded in Step 3 and milestones were extracted, include them below a separator:

```
Phase 1: Inquire          — in_progress
Phase 2: Position         — pending
Phase 3: Explore          — pending
Phase 4: Make             — pending
Phase 5: Reflect          — pending
```

If no brief was loaded during setup, add a note about `/esf-brief`:

> "You're set up for [project name]. If you have a project brief (assignment, scope doc, spec, or similar), run `/esf-brief` to load it and set up milestone tracking. Otherwise, you can skip that step.
>
> Phase 1 — Inquire — is yours alone. That means closing this tool and working offline: notebook, blank doc, or just your thoughts. Write out what you already know, what you're uncertain about, and your first instinct. No AI yet.
>
> Come back when you've written something down and run `/esf-start` again. I'll pick up from there."

If a brief was already loaded in Step 3:

> "You're set up for [project name] and your brief is loaded. Phase 1 — Inquire — is yours alone. Close this tool and work offline: write out what you already know, what you're uncertain about, and your first instinct. No AI yet.
>
> Come back when you've written something down and run `/esf-start` again. I'll pick up from there."
