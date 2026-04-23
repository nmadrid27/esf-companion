# Position Statement: Responsive System
**BUILD level, Project 2 | Alex Rivera | Written: Week 4, before AI engagement**

---

## What I Understand About This Project

The brief says to build something that responds to real-time input and has emergent behavior. The emergent behavior part is what I keep getting stuck on. I know it means something that wasn't explicitly coded, like how flocking behavior in birds emerges from three simple rules. But I don't know yet whether I can actually build something like that or if I'll just end up faking it.

The demo scares me more than the build. I need the thing to not crash and to have something worth showing in 2–3 minutes.

---

## My Questions Before Starting

- What counts as "emergent" vs. just "complex"? The brief doesn't define this.
- If I use particle systems, is the movement emergent or just physics simulation?
- Can the input source be text? Or does "real-time" imply something physical?
- How much does the visual output matter vs. the interaction design?

I'm going to try to answer these myself before asking anyone.

---

## My Position

I want to build something that uses sound as input (specifically microphone amplitude) and generates a visual system where entities have simple rules that produce patterns I can't fully predict. I've been thinking about reaction-diffusion systems after seeing some examples online. The idea is: sound changes a parameter in the system, which shifts which pattern emerges.

I'm drawn to this because it feels genuinely responsive in a way that isn't just "louder = bigger." The same amplitude at different moments in the system's state should produce different results.

---

## Design Intent

**My position on the creative/technical problem:**
I want to explore whether a biological simulation model can be made musically responsive in a way that feels intuitive to interact with, not just technically correct but experientially interesting. The challenge is keeping the system legible enough that users notice their effect on it, without making the connection so obvious it becomes boring.

**Tools I plan to use and why:**
I'm going to research p5.js and shader-based approaches this week. I've used p5 before for simpler sketches, so it's lower risk. But I'm suspicious it might not handle the computation load well. I want to find at least one alternative before committing.

I will use AI tools to help me understand reaction-diffusion math (which I don't fully grasp yet) and to generate alternative approaches I can evaluate. I will not use AI to write the core system logic until I understand what I'm asking it to do.

**What success looks like on my own terms:**
The system runs live without crashing. Someone who has never seen it can interact with it for 30 seconds and notice that their voice or sound is changing something. The emergent behavior is something I discovered during testing, not something I designed deliberately. My Records of Resistance document at least 3 moments where I pushed back on a direction the AI (or my first instinct) suggested.
