# ESF State Injection Schema

## Purpose

State injection is the mechanism by which the ESF Companion receives user context at the start of each API call. Because the v4 Claude API architecture has no persistent memory between calls, all session context that the Companion needs to behave correctly — who the user is, what project they are on, what phase they are in, whether they have a confirmed Position Statement — must be provided by the calling service layer before the conversation turn is processed. The injection replaces what the v1 local workflow reads from `projects/_esf/companion-state.md` and related files. The Java service layer (Plan B) is responsible for fetching this data from the database, formatting it per the schema below, and prepending it to the user's message or inserting it as a system context block.

---

## Fields

| Field | Type | Source (v1 local) | Notes |
|-------|------|-------------------|-------|
| user_name | string | companion-state.md → identity.name | Display name |
| user_role | string | companion-state.md → identity.role | "student", "educator", "professional" |
| discipline | string | companion-state.md → identity.discipline | e.g. "Graphic Design" |
| context_code | string | active context | e.g. "AI-201" |
| context_name | string | active context | e.g. "Creative Computing with AI" |
| project_name | string | current project | |
| phase | enum | current project state | Inquire / Position / Explore / Make / Reflect |
| scaffolding_level | enum | current project state | Guided / Supported / Independent |
| silent_mode | bool | companion-state.md → preferences | default false |
| position_statement | text | position-statements/*.md | Full confirmed text; "[No confirmed PS]" if absent |
| ror_count | int | count of RoR files for current project | |
| consecutive_unmodified | int | session-level counter | Reset to 0 on any modification or rejection |
| ror_minimum | int | brief frontmatter or admin config | default 2 |
| position_statement_required | bool | brief frontmatter or admin config | default true |
| five_questions_required | bool | brief frontmatter or admin config | default true |
| allow_silent_mode | bool | brief frontmatter or admin config | default true; set false to enforce instructor lock |
| last_session_next | text | most recent session log → Next Session section | Used for session-start re-entry framing; null if no prior session |
| project_scope | text | project-scope-[slug].md | Full confirmed scope text; null if not yet created |

---

## Injection Format

See `EsfState.to_injection_text()` in `harness/state.py` for the canonical rendered format.
The Java service layer (Plan B) must produce identical output.

The injection text is prepended as a system block before the user's message. Example structure:

```
[ESF_STATE]
user_name: Jordan
user_role: student
discipline: Graphic Design
context_code: AI-180
context_name: AI and Creative Practice
project_name: Bias Artifact
phase: Explore
scaffolding_level: Guided
silent_mode: false
position_statement: |
  <full confirmed position statement text>
ror_count: 1
consecutive_unmodified: 0
ror_minimum: 2
position_statement_required: true
five_questions_required: true
allow_silent_mode: true
last_session_next: |
  <Next Session section from most recent session log, or null>
project_scope: null
[/ESF_STATE]
```

---

## Caller Responsibilities

The service layer must:

1. Fetch current user profile and project state from the database before each call.
2. Render the injection block using the schema above.
3. Prepend the injection block to the system prompt or insert it as a dedicated system context message.
4. Parse structured return data from the Companion's response and persist any state updates (phase transitions, checkpoint saves, session log entries, RoR records, growth snapshots).
5. Maintain the `consecutive_unmodified` counter in session memory and reset it to 0 whenever the user modifies, rejects, or explicitly engages critically with an AI suggestion.

---

## Return Data Format

When the Companion produces structured state updates (phase transitions, checkpoint saves, session log entries, RoR records), they are returned in a structured block the caller must parse. Example:

```
[ESF_UPDATE]
type: phase_transition
new_phase: Make
timestamp: 2026-04-03T10:15:00Z
[/ESF_UPDATE]
```

```
[ESF_UPDATE]
type: ror_captured
ror_number: 2
status: saved
ai_suggested: AI suggested using a grid-based layout for the bias artifact
why: Felt too structured; the artifact is meant to feel ambiguous
did_instead: Used free-form collage approach instead
timestamp: 2026-04-03T10:22:00Z
[/ESF_UPDATE]
```

The Java service layer must define a parser for these blocks and route them to the appropriate persistence operations.
