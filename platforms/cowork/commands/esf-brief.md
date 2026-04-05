---
description: Load a project brief and set up milestone tracking
allowed-tools: Read, Write, Glob
---

Read a project brief, extract milestones and deliverables, set up a milestone tracker, and orient the user to their first action. Works with any brief format: course assignments, client scopes, research proposals, personal project specs, or freeform descriptions.

**All files are created in the user's selected folder.** Every Write, Edit, and Glob call targets paths relative to the workspace root (the folder the user selected in Cowork). Never write to temporary or sandbox paths.

## Step 1: Find or Receive the Brief

**First, read `projects/_esf/companion-state.md`.** If not found, check `companion-state.md` at root and `*/companion-state.md` one level deep for backwards compatibility. Ignore matches under `sample/`, `examples/`, or `templates/`. Extract the current project name, context, and brief path (if set).

**Then look for briefs using the known project path.** If `companion-state.md` has a brief path, check that specific file. If it has a project name but no brief path, check `projects/[project-name]/briefs/` directly. Only fall back to `projects/*/briefs/*.md` if no project context is available.

If one or more briefs exist, present them via `mcp__cowork__present_files` and use AskUserQuestion:

Question: "Which brief are you working with?"
- List each found brief as an option with a preview showing the first few lines.
- Include **"I'll describe my project instead"** as the final option with preview: "No document needed. Answer 4 quick questions and I'll generate a brief you can edit."

If no briefs exist in the folder structure, skip straight to Step 2.

---

## Step 2: Parse or Build the Brief

**If a brief file was selected:**

Read the full file. Extract in this order:

1. **Frontmatter fields** (if present): `position-statement`, `five-questions`, `ror-minimum`, `ai-use`, `allow-silent-mode`
2. **Deliverables**: What the user needs to produce. Look for sections labeled Deliverables, Outputs, Requirements, Scope, or What You'll Make.
3. **Milestones or timeline**: Any dates, phases, sprints, checkpoints, or due dates. Look for sections labeled Timeline, Milestones, Schedule, Phases, or any table with dates.
4. **AI boundaries**: Any stated policy on AI use. Look for sections labeled AI Use, AI Policy, Collaboration Policy, or Tools.
5. **Success criteria**: How the work will be evaluated. Look for sections labeled Grading, Assessment, Evaluation, Done Criteria, or Acceptance Criteria.
6. **ESF requirements**: Position Statement, Records of Resistance, Five Questions — either by name or by equivalent language (Design Intent = Position Statement, "document AI decisions" = Records of Resistance, self-assessment questions = Five Questions).

If the brief has no frontmatter, infer ESF settings from the prose. If no ESF language exists at all, default all fields to `optional`.

**If no brief file — build one conversationally:**

Ask 4 questions (use AskUserQuestion or conversational flow depending on complexity):

1. "What are you making? Describe the project in a sentence or two."
2. "What does done look like? List the deliverables, outputs, or artifacts."
3. "What's the timeline? Key milestones, deadlines, or checkpoints."
4. "Where's the line for AI? What parts do you want to keep human-only, and where is AI welcome?"

Generate a minimal brief in markdown:

```markdown
---
type: project-brief
project: [project name from companion-state.md]
position-statement: optional
five-questions: optional
---

# [Project Name]

## What I'm Making
[User's description]

## Deliverables
[Bulleted list]

## Timeline
[Milestone table or list]

## AI Boundaries
[User's stated policy]
```

Present the draft and ask: "Does this capture it? I'll save it to your briefs folder."

Save to `projects/[context]/briefs/[project-name]-brief.md`.

---

## Step 3: Summarize What You Found

Present a clear summary:

> **Brief loaded: [project name]**
>
> Deliverables: [list each]
> Timeline: [milestone summary with dates if available]
> Position Statement: [required / optional / not required]
> Records of Resistance: [minimum N / not specified]
> Five Questions: [required / optional / not required]
> AI boundaries: [summary of policy]

If anything is ambiguous or missing, flag it: "Your brief doesn't specify [X]. Want to set that now, or leave it open?"

---

## Step 4: Set Up Milestone Tracker

Extract every milestone, checkpoint, or deliverable with a date or sequence position.

**Important:** Do not overwrite the phase tracker. The `esf-project` skill maintains a combined TodoWrite list with phase items first. Read `companion-state.md` to determine the current phase, then write a single TodoWrite call that includes all five phase items (with correct status) followed by a separator and the milestone items:

```
Phase 1: Inquire          — [status based on current phase]
Phase 2: Position         — [status based on current phase]
Phase 3: Explore          — [status based on current phase]
Phase 4: Make             — [status based on current phase]
Phase 5: Reflect          — [status based on current phase]
── Milestones ──          — pending (visual separator, always pending)
Milestone: [name] — [date or "Week N"] — pending
Milestone: [name] — [date or "Week N"] — pending
...
Final: [name] — [date] — pending
```

Mark each milestone as `pending`. As the user completes milestones across sessions, update only the milestone items while preserving phase items.

If the brief has no explicit milestones, propose a default breakdown:

> "Your brief doesn't have specific milestones. Here's a suggested breakdown based on the deliverables and timeline:
>
> 1. Position Statement complete
> 2. [First deliverable or research phase]
> 3. [Second deliverable or draft phase]
> 4. [Final deliverable]
> 5. Reflection and disclosure
>
> Want to use this, adjust it, or skip milestone tracking?"

---

## Step 5: Update companion-state.md

Update the Current Project block with the brief path and any extracted ESF requirements.

---

## Step 6: Orient to Next Action

Based on the current phase in `companion-state.md`:

- **Inquire or Position:** "Your brief is loaded and milestones are set. Phase 1 is still yours alone — close this tool and work through your initial thinking offline. Come back when your Position Statement is ready."
- **Explore or later:** "Brief loaded. Your current phase is [phase]. Ready to continue?" Then invoke `esf-project` and proceed.

Present the brief file via `mcp__cowork__present_files` so the user has it as a clickable card for reference.
