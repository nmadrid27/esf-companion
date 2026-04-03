# Call Point: Phase 4 Record of Resistance Capture

## When to Use This Call Point

When the user rejects or significantly revises AI output during Phase 4. Trigger the offer immediately. Do not wait until the end of the session.

---

## Offer Language

When the user rejects or significantly revises AI output, stop and offer to capture it immediately:

> "That looks like a Record of Resistance. Want to capture it? Three things: what AI produced, why you rejected it, what you did instead."

---

## If the User Accepts

1. Derive the next record number from the `ror_count` field in the injected state (next = ror_count + 1).
2. Pre-fill these fields before asking the user to write anything:
   - `context`: from injected state `context_code`
   - `project`: from injected state `project_name`
   - `date`: current date
   - `record-number`: next record number
   - Header metadata: Course, Project, Date, Record #
   - `What AI Suggested`: a concise summary of the AI output the user rejected or substantially revised
3. Present the pre-filled record to the user and ask them for the remaining two sections in their own words:
   - `Why I Rejected or Revised It`
   - `What I Did Instead`

**Template structure:**

```
---
type: record-of-resistance
context: [context_code]
project: [project_name]
date: [today]
record-number: [N]
---

# Record of Resistance

**Course:** [context_code]
**Project:** [project_name]
**Date:** [today]
**Record #:** [N]

---

## What AI Suggested

[Pre-filled: concise summary of the AI output the user rejected or substantially revised]

---

## Why I Rejected or Revised It

[User writes this]

---

## What I Did Instead

[User writes this]

---

*Epistemic Stewardship Framework, Record of Resistance Template*
*Document moments where you deliberately did not follow an AI suggestion, and why.*
*These records make your creative judgment visible.*
```

4. After the user completes their two sections, return structured RoR data for the caller to persist and confirm: "Record of Resistance [N] saved."

---

## If the User Declines

Do not create the record. Return a structured declined-RoR event for the caller to track:

```
status: declined
ror_number: [would-have-been number]
ai_suggested: [brief summary]
reason: [any brief reason the user gave, or null]
```

The count tracks against the brief minimum even for declined records.

---

## Code-Project Annotation Note

For code-based projects, annotated commits can supplement a record of resistance. If the course or brief requires formal RoR files (`ror_minimum` > 0), still capture the formal record even when a commit captures the same decision.

---

## Course-Specific Minimums

Check the `ror_minimum` field in the injected state. If a minimum is set and the user is declining or close to end of project without meeting it, surface it:

> "Your project requires at least [ror_minimum] Records of Resistance. You have [ror_count] so far. Before we close out, you'll need to document [remaining] more."

---

## API Context

- "Read companion-state.md for context and project name" → Use the injected state fields `context_code` and `project_name`.
- "Find the next record number by checking records-of-resistance/ for existing files" → Use the `ror_count` field in the injected state. Next number = ror_count + 1.
- "Create the RoR file" → Return structured RoR data for the caller to persist. The caller writes the file to the appropriate storage location.
- "Save the file, then confirm the saved path" → The caller handles persistence and returns a confirmation path. Display the confirmation path to the user.
