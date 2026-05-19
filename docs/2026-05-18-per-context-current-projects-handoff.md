---
title: Per-Context Current Projects — Brainstorming Handoff
date: 2026-05-18
status: brainstorming in progress, ~50% through design presentation
next-step: resume design presentation at Section 3 (activation status line)
skill-to-resume: superpowers:brainstorming
---

# Handoff: Per-Context Current Projects (ESF Companion)

## Why this exists

A user (Nathan) had a completed project (`dev-ambient-agent`, finished 2026-04-29) sitting in `companion-state.md` as Current Project for ~19 days while working on unrelated things. The Companion kept checking new work against the wrong Position Statement context. This is a behavioral-correctness issue, not cosmetic.

Root cause: companion-state.md has a single Current Project slot. The completion rule is soft (text comment). Nothing catches "user moved on without an explicit wrap-up signal." Same gap exists for any external user with multiple projects.

## What we're designing

Replace the single Current Project slot with **per-context current-project slots**. Each Active Context (AI-180, AI-201, etc.) can have its own current project. Session-start logic resolves CWD to a context, then reads that context's current project. Idle projects in other contexts sit harmlessly; the status line only ever surfaces the project matching today's CWD.

Originally framed as "stale-project detection." Pivoted upstream when Nathan asked about multi-project persistence. Per-context slots make the contamination problem largely disappear without an explicit staleness check.

## Decisions made (with reasoning)

| # | Decision | Reasoning |
|---|---|---|
| 1 | Harm = wrong-PS contamination | Behavioral correctness; justifies session-start friction |
| 2 | Stale signal = path-mismatch (CWD vs. base path) | Immediate detection vs. delayed time-based |
| 3 | Action menu = Clear or Switch | Forcing choice; "Other" is the escape hatch |
| 4 | silent_mode does NOT suppress | Same logic as PS gate and disclosure: safety, not scaffolding |
| 5 | Data model = per-context current projects | Incremental schema change; scales without history limit |
| 6 | No staleness check on top | Per-context model solves the problem; ship lean |
| 7 | File format = compact list (one bullet per context) | Hand-editable, matches existing file style; colons not em dashes |

## Design sections — progress

### Section 1: Schema change to companion-state.md  ✅ APPROVED

Replace `## Current Project` block with `## Current Projects`. Compact list, one bullet per active context:

```
- [context-code]: [project-name] ([base-path], [scaffolding-level])
- [context-code]: not set
```

Completion-rule comment tells users to flip a project to "not set" when done. Never delete the context's line. PS state stays at `esf/[context]/position-statements/[project-slug].md` (existing canonical convention); not duplicated into state file. Only contexts in `## Active Contexts` are allowed in `## Current Projects` (enforced by migration logic, not parser hardness).

### Section 2: Session Start Protocol — context resolution  🟡 PRESENTED, AWAITING APPROVAL

New step between current step 4 ("Read current project state") and step 4a ("Emit activation status line").

1. Determine session CWD.
2. For each context in `## Active Contexts`, compare CWD against the base path. Match = CWD equals base path or is inside it. Deepest match wins.
3. Exactly one match: that's the **session context**. Look up its **session project** in `## Current Projects`.
4. No match: session context = `none`, session project = `not set`. Existing ad-hoc forcing function still fires when substantial content is requested.
5. Multiple matches at same depth: pick-one prompt.

Session context and session project are what downstream behavior reads (PS lookup, Moment 1, status line, session buffer path). The global "Current Project" concept goes away.

### Sections 3–7: still to present

- **Section 3:** Activation status line format. Show session context + session project, format when no match.
- **Section 4:** Migration handling. Detect old single-slot format on first session, convert in-place using the existing values. Surface a one-time notice.
- **Section 5:** Onboarding update. `/esf-onboarding` writes the new format from scratch. Update the template at `.claude/skills/esf-onboarding/`.
- **Section 6:** Variant parity. Both `.claude/agents/esf-companion.md` (Claude Code) and `platforms/cowork/skills/esf-project/SKILL.md` (Cowork) need the same logic. Identify minimum diff per variant.
- **Section 7:** Testing approach. New companion-state.md fixtures, CWD-resolution unit tests, migration test, both-variants smoke test.

## Files in scope

```
~/projects/esf-companion/
├── .claude/agents/esf-companion.md          # Claude Code agent (917 lines)
├── platforms/cowork/skills/esf-project/SKILL.md  # Cowork variant (872 lines)
├── .claude/skills/esf-onboarding/SKILL.md   # Onboarding flow
├── prompts/esf-companion.md                 # Short summary file (66 lines)
└── test/                                    # Smoke tests
```

Key reference sections in the Claude Code agent (verified 2026-05-18 against tip of `feature/v0.8.0-consolidate-install-footprint`):
- Session Start Protocol: section starts at line 507; step 4 (read current project state) at line 546; the new context-resolution step inserts between line 546 and step 4a at line 548
- Activation status line: line 548
- Ad-hoc project forcing function (`## Project Logging on Ad Hoc Substantial Work`): line 671
- companion-state.md lookup chain: lines 442–451 (Workspace State section runs 437–454)
- Moment 4 (Ownership): line 244

## Out of scope (explicitly)

- Time-based staleness check (rejected — per-context model is enough)
- Project history / stack (rejected — over-engineering)
- Per-folder PROJECT.md as source of truth (rejected — too big a refactor)
- Pausing projects to history (rejected — not in action menu)
- "Keep as-is" action on mismatch (rejected — "Other" is the escape hatch)

## How to resume

In a new session at `~/projects/esf-companion/`:

> Read `docs/2026-05-18-per-context-current-projects-handoff.md` and resume the brainstorming. We finished Section 2 (Session Start Protocol context resolution) and need approval on it before moving to Sections 3–7. Use the `superpowers:brainstorming` skill.

After all sections approve: write the spec to `docs/2026-05-18-per-context-current-projects-design.md`, run spec self-review, get Nathan's spec approval, then invoke `superpowers:writing-plans` to produce the implementation plan.

## Unrelated state from this session

The prior conversation also ran a separate task — moving `~/Obsidian/.claude/rules/` to `~/Obsidian/rules-registry/` to stop the harness from auto-inlining the rules registry into every session's context (~5,600 token savings). That work is **done and tested** but **uncommitted** across two repos:

- `~/Obsidian/` (vault): rules-registry rename, CLAUDE.md pointer updates, vault-system-cheatsheet + install-guide edits, companion-state.md cleared dev-ambient-agent Current Project
- `~/Developer/vault-system-mcp/`: `tools/rules.py:21`, `config.py:86`, 5 test files. 196/196 tests pass. Launchd service restarted.

If the next session wants a clean slate, commit those first.
