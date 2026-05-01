# Record of Resistance: 02

**Project:** Responsive System | **BUILD level | Alex Rivera, BFA Motion Media Design**
**Date:** Week 6, Wednesday

---

## What the AI Suggested

I was implementing the visual rendering layer for my reaction-diffusion system and asked the AI about options for real-time pattern display. It recommended a well-known JavaScript canvas library with built-in animation loops, noting that the library would handle frame timing, pixel manipulation, and scaling automatically. The suggestion included sample code with a clean API and would have saved me several hours of setup.

---

## What I Chose Instead

I wrote the rendering directly using the Canvas API with raw pixel buffer manipulation. No library layer between my simulation data and the screen.

---

## Why

The library would have abstracted away the exact thing I want to control. My position statement says the system should feel like an instrument, where the relationship between input and output is immediate and legible. Every abstraction layer adds latency and interpretation. The library's animation loop would impose its own timing logic on top of my simulation's update cycle, and the two clocks would drift.

More importantly: I want to understand what every pixel is doing. The reaction-diffusion simulation produces a float array. I want to map those floats to colors myself, because the color mapping is an aesthetic decision, not a technical one. The library's default rendering would impose its own interpolation and color space, and I would spend more time overriding its defaults than I would save by using it.

This is a creative computing project. The computation is the medium. Abstracting it away defeats the purpose.

---

## What Happened

The raw Canvas approach took longer to set up, about four extra hours of work on the pixel buffer pipeline. But I now have direct control over every step from simulation state to screen pixel. The color mapping I built produces a visual quality I could not have gotten from the library: the patterns have a granular, almost biological texture because I am mapping the float values through a custom transfer function instead of a standard gradient.

The performance is also fine. For a single-channel reaction-diffusion system at the resolution I need, raw canvas is fast enough.

---

## Would I Change This Decision?

No. The four hours of extra setup produced a rendering pipeline I fully understand and can modify at any point. When I change the color mapping for the demo, which I will, I will not have to fight a library's abstractions to do it. The technical decision and the aesthetic decision are the same decision here, and that is the point.
