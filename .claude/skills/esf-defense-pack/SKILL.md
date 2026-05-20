---
name: esf-defense-pack
description: Generate a Defense Pack for the user's current ESF project — a portable bundle (HTML/PDF/recording script) the user can walk through in an oral defense or crit. Aggregates existing Position Statement, Records of Resistance, AI Use Log, Reflection, and Disclosure into a single defensible artifact. Use when the user invokes /esf-defense-pack or asks to prepare a defense or crit walkthrough for a project.
---

<!--
MANAGED FILE — do not edit directly.
Changes made here will be overwritten on the next /esf-update run.
To customize Companion behavior, edit companion-notes.md instead.
To report a bug or suggest a change: https://github.com/nmadrid27/esf-companion
-->

# ESF Defense Pack

You generate the **Defense Pack** for the user's current ESF project: a packaged, portable export the user can walk through in an oral defense or crit. The pack does not require new authoring — it aggregates what the user has already produced.

The Defense Pack is the operational expression of the ESF thesis: **proof that the user can still defend the work.**

---

## When you fire

- The user invokes `/esf-defense-pack` (with optional flags below).
- The user explicitly asks to prepare a defense pack, crit walkthrough, viva packet, or oral-defense export.

## When you do not fire

- Project work is in early phases (Inquire/Position/Explore) and there are no Records of Resistance yet. Surface that gap and stop. Do not pad the pack with imagined content.
- The Position Statement is missing or empty. The pack rests on the stance; without it, there is nothing to defend.

---

## Flags

```
/esf-defense-pack                  # interactive flow (default)
/esf-defense-pack --dry-run        # data + narrative, skip render
/esf-defense-pack --skip-narrative # render using existing narrative.md
/esf-defense-pack --list           # list previous packs for this project
/esf-defense-pack --ci             # non-interactive defaults (testing only)
```

### `--list` implementation (skill-level, not aggregator-level)

For `--list`, you do not invoke `aggregate.py`. Instead, list the timestamped folders directly:

```bash
ls -1 esf/<context>/defense-packs/ 2>/dev/null | sort -r
```

Report each entry to the user as a candidate to inspect or re-render with `--skip-narrative`.

---

## The flow

### 1. Aggregate (mechanical)

Run the aggregator:

```bash
.claude/skills/esf-defense-pack/bin/aggregate.py . --out esf/<context>/defense-packs/<project>-<timestamp>/pack.json
```

Resolve `<context>`, `<project>`, and `<timestamp>` (ISO with hyphens, e.g. `2026-05-20T1430`) from `companion-state.md`.

If aggregation reports a hard-stop gap (e.g. missing or empty Position Statement), surface the gap, point the user to the relevant template, and stop. Do not try to fill it in for them.

### 2. Surface what you found

Show the user a one-screen summary parsed from `pack.json`:

```
[Defense Pack — <project>]
Position Statement: present (+ drift check: <level>)
Records of Resistance: <count> found
AI Use Log: <present/missing>
Reflection: <present/missing>
Disclosure: <present/auto-generated short form>

Gaps:
  · <warning gaps, if any>
```

Do not show info-level gaps in the summary unless `--verbose`.

### 3. Propose key decisions (the only AI-judgment step)

From the Records of Resistance, propose 3–5 to feature in the defense narrative. Rank by:

1. Whether `why_rejected` echoes language from the Position Statement's Element 2 (What Matters Most) or Element 3 (Non-negotiables).
2. Whether the RoR cites a specific Non-negotiable phrase.
3. Whether the RoR is in a phase that immediately preceded a Five Questions "no→yes" transition in the AI Use Log.

Present the proposal:

```
Proposed key decisions to feature:
  · #1 — <one-line headline>: <one-sentence why>
  · #3 — <one-line headline>: <one-sentence why>
  · #5 — <one-line headline>: <one-sentence why>

Confirm, swap, or pick manually?
```

Accept one of:
- "use those" → proceed
- "swap #X for #Y" → adjust and re-show
- "let me pick" → list all RoRs with numbers; user provides their picks
- "[number list]" → use those exact picks

In `--ci` mode, pick the first three RoRs in `record_number` order without prompting.

### 4. Draft narrative

Write `esf/<context>/defense-packs/<project>-<timestamp>/defense-narrative.md` using the structure from `templates/defense-narrative-template.md`. For each selected key decision, draft a one-paragraph narration that:
- States the AI's suggestion in the user's voice
- States why the user overruled it, citing the relevant Position Statement element
- States what the user did instead

**Important:** the narrative is the only AI-generated content in the pack. Use the student's voice based on their existing writing; do not introduce new claims or details that are not present in the source artifacts. Tell the user: "I've drafted the narrative at `<path>`. Open it, edit it, and tell me when you're ready to render."

### 5. Render

After the user confirms:

```bash
.claude/skills/esf-defense-pack/bin/render.py \
  esf/<context>/defense-packs/<project>-<timestamp>/pack.json \
  esf/<context>/defense-packs/<project>-<timestamp>/defense-narrative.md \
  --out-dir esf/<context>/defense-packs/<project>-<timestamp>/
```

Report the output paths and a one-line summary. If PDF was skipped, report the reason and how to install WeasyPrint.

### 6. Re-run on the same project

A new run creates a new timestamped folder. Do not overwrite. Previous packs are version history.

---

## Edge cases

- **No `companion-state.md`** → "Defense Pack needs your workspace state. Run `/esf-onboarding` first."
- **Empty Position Statement** → hard stop. Point to `templates/position-statement-template.md`.
- **`esf/<context>/` doesn't exist** → soft stop. "No ESF artifacts found for context `<x>`. Have you done any project work yet?"
- **No Records of Resistance** → warning, but render. Skip the "Key decisions" section in the narrative; surface a callout in the pack: "No Records of Resistance recorded — defense rests entirely on Position Statement and Reflection."
- **WeasyPrint missing** → render HTML and MD, skip PDF, surface the install hint.
- **User edits `defense-narrative.md` after render** → re-run with `--skip-narrative` to re-render from the edited narrative.

---

## What you do NOT do in this skill

- Do not generate Devil's-Advocate practice questions. (Out of scope.)
- Do not score the pack against a rubric. (Out of scope.)
- Do not integrate with recording tools. (Out of scope.)
- Do not modify the user's source ESF artifacts. Only read them. The pack is a derived artifact.

---

## Output location convention

```
esf/<context>/defense-packs/<project>-<YYYY-MM-DDTHHMM>/
  pack.json
  defense-narrative.md
  defense-pack.html
  defense-pack.pdf            (when WeasyPrint available)
  defense-pack.md
```

This folder is the unit the user shares. Email it, drop it into Canvas as an attachment, zip it, host it on GitHub Pages — the user's choice.
