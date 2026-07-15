# Defense Pack: example output

A rendered Defense Pack produced from the synthetic `responsive-system` test fixture. This is what `/esf-defense-pack` emits for a project that has a Position Statement, five Records of Resistance, an AI Use Log, and a Reflection.

## Files

| File | What it is |
|---|---|
| [`defense-pack.html`](defense-pack.html) | Interactive single-page HTML. Opens in any browser. Self-contained: no external CSS, fonts, or scripts. Drop into Canvas, email it, host it anywhere static. |
| [`defense-pack.pdf`](defense-pack.pdf) | Print-ready PDF rendered by WeasyPrint. Page numbers, running header, layout preserved from the HTML. ~74 KB. |
| [`defense-pack.md`](defense-pack.md) | Recording script with `[~X min]` timing cues. The student reads this aloud for an async video defense; aim for 12–15 minutes total. |
| [`defense-narrative.md`](defense-narrative.md) | The narrative the renderer consumed. Drafted by AI (per the SKILL prompt) and edited by the student before render. The pack rests on this. |

## Sample project

This example uses a fictional design project: `responsive-system`, a Motion Media Design exploration of "time as friction, not flow." The student (`Alex Rivera`) wrote a Position Statement, kept five Records of Resistance during the build, and ran their Reflection at the end.

The underlying source files are in [`test/fixtures/defense-pack/full/`](../../test/fixtures/defense-pack/full/); that's the workspace structure `/esf-defense-pack` was run against.

## How to reproduce

In a project with the ESF Companion installed (Path 4, Claude Code):

```bash
/esf-defense-pack
```

The skill walks you through: aggregate → propose key decisions → draft narrative → render. The output folder lives at `esf/<context>/defense-packs/<project>-<timestamp>/` and contains the same four files as above.

To reproduce *this exact pack* by hand:

```bash
# Aggregate the synthetic fixture
.claude/skills/esf-defense-pack/bin/aggregate.py \
  test/fixtures/defense-pack/full \
  --out /tmp/pack.json

# Render against the narrative in this folder
.claude/skills/esf-defense-pack/bin/render.py \
  /tmp/pack.json \
  examples/defense-pack/defense-narrative.md \
  --out-dir /tmp/out
```

## What you're looking at

The Defense Pack is the **curated argument** a student walks an instructor through during an oral defense or crit. It's distinct from a process book:

- **Process book**: exploratory documentation, browsable, multi-page. The full record of how the work evolved.
- **Defense Pack**: the curated argument extracted from that documentation, sequential, single-page. Designed for a specific 15-minute defense moment.

Both visual languages overlap on purpose; students producing a process book in the canonical aesthetic get a Defense Pack that feels like the same project.
