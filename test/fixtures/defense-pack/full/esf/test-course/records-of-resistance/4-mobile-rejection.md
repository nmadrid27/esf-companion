---
type: record-of-resistance
context: test-course
project: responsive-system
date: 2026-05-01
record-number: 4
---

# Record of Resistance

**Course:** test-course
**Project:** responsive-system
**Date:** 2026-05-01
**Record #:** 4

---

## What AI Suggested

> AI proposed fluid mobile reflow using percentage widths and viewport-relative units so the layout scales continuously across breakpoints.

---

## Why I Rejected or Revised It

> Continuous reflow softens the system's stance. The layout should commit to a position at each breakpoint, not negotiate with the viewport in real time.

---

## What I Did Instead

> Authored a parallel layout per breakpoint with no continuous in-between. Each breakpoint is its own composition; the transition between them is a hard switch at the threshold.
