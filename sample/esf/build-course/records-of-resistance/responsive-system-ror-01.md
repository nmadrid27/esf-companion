# Record of Resistance: 01
**Project:** Responsive System | **BUILD level | Alex Rivera**
**Date:** Week 5, Tuesday

---

## What the AI Suggested

I asked Claude to help me think through how to make the reaction-diffusion parameters respond to sound amplitude. It suggested mapping amplitude directly to the feed rate (F): so louder input increases F, which controls how fast the "activator" chemical is added to the system. It gave me specific value ranges and noted this would produce a visible shift from spots to stripes as input got louder.

The suggestion was clear and technically sound. It would have worked.

---

## What I Chose Instead

I didn't map amplitude to F. I mapped it to the ratio between F and the kill rate (k): keeping their relationship constant but shifting both values together along a diagonal of the parameter space. This means amplitude moves the system through a trajectory of pattern types rather than sliding one parameter while the other stays fixed.

---

## Why

The AI's suggestion would have created a linear response: louder = more activator = different pattern. Mine creates a non-linear one: the system moves through a phase space, and different regions of that space have qualitatively different behavior (spots, stripes, labyrinthine patterns, near-extinction). The interaction becomes about finding and holding a region, not just turning a dial.

I also wanted to avoid the obvious move. The AI gave me the technically correct answer. I wanted the experientially interesting one.

---

## What Happened

It mostly worked. The transitions between pattern types are visible but not always smooth, there are some stability issues at the edges of certain regions I need to investigate. This is actually interesting. The instability might be part of the experience rather than a bug to fix.

---

## Would I Change This Decision?

Not yet. I want to see how it feels in the demo context before deciding whether the instability is a feature or a problem.
