---
name: esf-defense-pack
description: Generate a Defense Pack for the user's current ESF project: a portable bundle (HTML/PDF/recording script) the user can walk through in an oral defense or crit. Aggregates existing Position Statement, Records of Resistance, AI Use Log, Reflection, and Disclosure into a single defensible artifact. Use when the user invokes /esf-defense-pack or asks to prepare a defense or crit walkthrough for a project.
---

<!--
MANAGED FILE: do not edit directly.
Changes made here will be overwritten on the next /esf-update run.
To customize Companion behavior, edit companion-notes.md instead.
To report a bug or suggest a change: https://github.com/nmadrid27/esf-companion
-->

# ESF Defense Pack

You generate the **Defense Pack** for the user's current ESF project: a packaged, portable export the user can walk through in an oral defense or crit. The pack does not require new authoring; it aggregates what the user has already produced.

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

Resolve `<context>`, `<project>`, and `<timestamp>` from `companion-state.md`. Use a **compact UTC** timestamp for `<timestamp>` (e.g. `2026-05-20T194743Z`) so the folder name matches the `export_timestamp` field the aggregator writes into `pack.json`; the two should be in the same timezone. Construct with `date -u +%Y-%m-%dT%H%M%SZ`.

If aggregation reports a hard-stop gap (e.g. missing or empty Position Statement), surface the gap, point the user to the relevant template, and stop. Do not try to fill it in for them.

### 2. Surface what you found

Show the user a one-screen summary parsed from `pack.json`:

```
[Defense Pack: <project>]
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

From the Records of Resistance, propose **all available RoRs up to 5** (3–5 is the target range; fewer is acceptable when fewer exist). If fewer than 3 RoRs exist, note that to the user; defense panels usually expect at least three points of resistance, and a thin record may signal the project needs more RoRs before defense, not that the pack should be padded.

Rank by:

1. **PS-language echo:** `why_rejected` field uses phrases or concepts from the Position Statement's Element 2 (What Matters Most) or Element 3 (Non-negotiables). This is the strongest signal.
2. **Named in the PS drift section or Reflection's "temptation moments":** the student themselves flagged this decision as load-bearing. If the PS drift section mentions "Record #3" or the Reflection's temptation field names a specific topic, that record is a strong candidate.
3. **Partial acceptance or genuine tradeoff:** prefer records where the student kept some of the AI's suggestion and rejected part. Defense panels probe nuance, not reflex rejection. Avoid choosing two records that make the same argument (e.g., two "smoothness is bad" rejections).

Present the proposal:

```
Proposed key decisions to feature:
  · #1: <one-line headline>: <one-sentence why this record is load-bearing>
  · #3: <one-line headline>: <one-sentence why>
  · #5: <one-line headline>: <one-sentence why>

Confirm, swap, or pick manually?
```

Accept one of:
- "use those" → proceed
- "swap #X for #Y" → adjust and re-show
- "let me pick" → list all RoRs with numbers; user provides their picks
- "[number list]" → use those exact picks

In `--ci` mode, pick the first three RoRs in `record_number` order without prompting.

### 3.5. Persist curated decisions to pack.json

**Critical:** the renderer reads `key_decisions` from `pack.json`, not from the narrative. After the user confirms in step 3, write the selected decisions back to the existing `pack.json`:

```python
# Conceptual:
pack["key_decisions"] = [
    {"record_number": 1, "headline": "<one-line headline>", "curation_source": "ai_proposed_user_confirmed"},
    {"record_number": 3, "headline": "<one-line headline>", "curation_source": "ai_proposed_user_confirmed"},
    {"record_number": 5, "headline": "<one-line headline>", "curation_source": "user_selected"},
]
```

If you skip this step, the HTML/PDF will display "No key decisions curated" while the recording script narrates them; the artifact will contradict itself. (The renderer has a fallback that materializes key_decisions from the narrative's decision_walkthrough, but that's a safety net, not the intended flow.)

### 4. Extract the student's voice before drafting

Read the Position Statement and (if present) the Reflection. Extract 3–5 **short verbatim phrases** that show the student's voice, aiming for 3–10 words each, not full sentences (e.g., "Rejection is editorial"; "The aesthetic discomfort is the point"; "I will not let AI flatten it"). List them before you draft.

**The narrative must land at least two of those phrases unchanged.**

Avoid:
- Em dashes (the project's voice guidelines prohibit them)
- AI-style transitions ("That said," "Importantly," "Ultimately," "It's worth noting that")
- Smoothing the student's deliberate roughness ("staccato" → "concise" is a betrayal)
- Hedging where the student is direct
- Generic academic register where the student is plain-spoken (or vice versa)

### 5. Draft the narrative

Write `esf/<context>/defense-packs/<project>-<timestamp>/defense-narrative.md` using the structure from `templates/defense-narrative-template.md` (also installed at `esf/toolkit/templates/defense-narrative-template.md`).

**Required H2 sections; the renderer parses by exact heading text:**
- `## How I came in`: position summary in student voice (becomes the body of the HTML's position section)
- `## What I set out to protect`: what mattered most + non-negotiables, in the student's voice
- `## The key decisions`: contains `### Decision #N` sub-blocks, one per curated record
- `## How my position held` (or `## How my position held (or shifted)`)
- `## What I'd defend if asked`: five numbered claims (`1.`, `2.`, etc.) the student would say out loud
- `## Disclosure`: short AI disclosure (overrides the auto-generated one if present)
- `## Opening` (optional): explicit opening line. If omitted, the renderer skips Opening rather than duplicating "How I came in".

Within `## The key decisions`, use sub-headers `### Decision #1`, `### Decision #3`, etc., matching the record numbers from step 3. The body of each is one paragraph in the student's voice.

For each decision, the narration must:
- State what the AI suggested (paraphrased from the source RoR, not invented)
- State why the student overruled it, citing the relevant Position Statement element
- State what the student did instead
- Connect that choice to the Position Statement

### 6. Anti-invention check (run before saving)

After drafting, scan each sentence. Each sentence must be one of:

- **(a) Verbatim quotation** from a source artifact (Position Statement, Record of Resistance, AI Use Log, Reflection)
- **(b) Light grammatical bridging** between verbatim quotes (verb tense adjustments, subject substitution, joining clauses)
- **(c) Direct restatement** of a source claim in close paraphrase

If a sentence is **none of these**, if it's editorial sharpening, characterization, or a new claim, delete it OR mark it `[verify: <reason>]` for the student to confirm. Editorialization is invention; the student adds those themselves.

Common invention failures to watch for:
- "This is the suggestion my Position Statement was written to reject." (causal claim, not in source)
- "The AI suggestion was technically reasonable but..." (characterization, not in source)
- "...where I was most tempted." (could be source-grounded; verify it's actually in the Reflection)

When in doubt, delete and let the student write it.

**Meta-check:** if you find yourself adding `[verify: ...]` to *every* Decision block, stop and ask the user before continuing. That pattern means the source artifacts probably don't actually belong to this project; RoRs may be misfiled, or the student copied a template without updating the body. Surface the suspicion rather than papering over it with verify markers everywhere.

### 7. Tell the user, with explicit invitation to edit

After drafting, tell the user:

> I've drafted the narrative at `<path>`. The Position Statement, RoRs, and Reflection were the source; nothing in the narrative is a new claim. Read it carefully; anything that sounds off probably is. Edit freely, then tell me when you're ready to render.

### 8. Render

After the user confirms:

```bash
.claude/skills/esf-defense-pack/bin/render.py \
  esf/<context>/defense-packs/<project>-<timestamp>/pack.json \
  esf/<context>/defense-packs/<project>-<timestamp>/defense-narrative.md \
  --out-dir esf/<context>/defense-packs/<project>-<timestamp>/
```

Report the output paths and a one-line summary. If PDF was skipped, report the reason and how to install WeasyPrint.

**PDF dependencies (macOS):** WeasyPrint requires the `pango` system library. If `pip install weasyprint` succeeds but `python -c "import weasyprint"` fails at runtime with a `libpango` error, the user needs `brew install pango`. On macOS, set `DYLD_LIBRARY_PATH=/opt/homebrew/lib` when invoking render.py if the Python interpreter can't find the library. The graceful-skip path will print these hints automatically; surface them clearly to the user instead of swallowing the message.

### 9. Re-run on the same project

A new run creates a new timestamped folder. Do not overwrite. Previous packs are version history.

---

## Edge cases

- **No `companion-state.md`** → "Defense Pack needs your workspace state. Run `/esf-onboarding` first."
- **Empty Position Statement** → hard stop. Point to `templates/position-statement-template.md`.
- **`esf/<context>/` doesn't exist** → soft stop. "No ESF artifacts found for context `<x>`. Have you done any project work yet?"
- **Cycle-based / milestone-organized workspace** (e.g. `p2-break-through/`, `p3-next-steps/` with artifacts in each rather than `records-of-resistance/`) → the aggregator auto-discovers them and emits an INFO-severity `workspace_layout` gap. The pack is complete; surface the gap only with `--verbose`. Suggest declaring `## Defense Pack Paths` in companion-state.md if the user wants the layout pinned.
- **Records of Resistance with mismatched `project:` frontmatter** → the aggregator excludes them and emits a warning gap. Surface the gap to the user explicitly; they may have misfiled an RoR, or the work belongs to a sibling project in the same context. Do not silently include or silently exclude.
- **No Records of Resistance** → warning, but render. Skip the "Key decisions" section in the narrative; surface a callout in the pack: "No Records of Resistance recorded; defense rests entirely on Position Statement and Reflection."
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

This folder is the unit the user shares. Email it, drop it into Canvas as an attachment, zip it, host it on GitHub Pages, the user's choice.
