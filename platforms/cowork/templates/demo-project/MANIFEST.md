# Demo project manifest

This directory is the source of truth for the `/esf-demo` sandbox. The `esf-demo` command copies these files into `demo/critical-cartography/` in the user's selected workspace.

## Files in this template

- `briefs/cartography.md`: the project brief. Contains `position-statement: required` in frontmatter so the gate fires on first substantive request.
- `planning-notes.md`: a rough, user-voice planning note. Written deliberately to match what a real student would write before AI involvement: incomplete, opinionated, fragmented. This file is the source the gate's "draft from your materials" path will use.

## What this template does NOT include

- A pre-written Position Statement. The whole point of the demo is to walk the user through the gate path, including the offer to draft from materials. If a Position Statement existed, the gate would not fire.
- AI Use Log, Records of Resistance, gate records, or session logs. These are produced by the live session, not pre-seeded.
- A sample artist statement or any deliverable content. The user (or the demo session) writes those during the walkthrough.

## Demo session pacing (for the skill)

The skill should run the demo at accelerated pace. Specifically:

1. **Phase 2 gate.** Fire normally. Offer the "draft from your materials" path. Read the brief and planning note. Draft a Position Statement that distills the user's voice from the planning note (do not invent direction). Present, ask the user to confirm, save.

2. **Phase 3 readability pass.** Run normally. Brief.

3. **Phase 3 Explore.** Run one challenge thread only, derived from the planning note's "uncertain" list. Skip the verification prompt for the demo (or run it as a single example claim).

4. **Phase 3 transition.** Skip the full Project Scope step. Use a condensed scope based on the brief.

5. **Phase 4 Build Practice.** Suggest the following pieces (the user can confirm or modify):
   - [H] Concept and series direction
   - [H] Map symbology system
   - [M] Wall text and captions
   - [M] Print layout
   - [L] Print specs and bleed

6. **Phase 4 trigger event.** After Build Practice confirms, fire one structural-edit re-fire selection card deterministically (do not wait for an actual structural edit). Use this as the question text:

   "This edit changes the wall text's argument frame. The current Position Statement says the maps refuse the colonial frame, not just illustrate it. The wall text draft is starting to explain the colonial frame to the audience. Is that intentional?"

   Standard four options. Whatever the user picks, route through normally.

7. **Phase 4 drift prompt.** Fire once at midpoint:

   "Your Position Statement says every map must name what has been erased, by name. The current draft has one map using a shaded region instead of names. Is that a deliberate choice or did the framing slip?"

8. **Phase 5 Reflect.** Run condensed: one reflection prompt, generate the disclosure draft, ask for approval.

9. **End of demo.** Tell the user: "Demo complete. The disclosure draft is at `demo/critical-cartography/reflections/cartography-disclosure.md`. To clear the sandbox, run `/esf-demo --reset`. To turn this into a real project, copy the files out of `demo/` and add the project to your normal workspace."

## What about silent_mode?

Demo mode runs even when `silent_mode: true`. The user explicitly requested the demo by typing `/esf-demo`; that is consent to see the full scaffolding.

## Sandbox boundary

The skill must never write outside `demo/critical-cartography/` during a demo session. If the user attempts to redirect work to a real project mid-demo (for example, "actually let's apply this to my real thesis"), the skill should stop and ask: "You are in a demo session. Want to end the demo and switch to a real project, or finish the demo first?"
