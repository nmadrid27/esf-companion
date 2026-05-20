---
type: record-of-resistance
context: test-course
project: responsive-system
date: 2026-05-08
record-number: 5
---

# Record of Resistance

**Course:** test-course
**Project:** responsive-system
**Date:** 2026-05-08
**Record #:** 5

---

## What AI Suggested

> AI proposed adding subtle continuous motion to indicate state changes for screen-reader and low-vision users, framing it as an accessibility requirement.

---

## Why I Rejected or Revised It

> I agreed that motion-on-state-change is necessary, but the specific suggestion (subtle, continuous) conflicted with Element 3. Accessibility cannot be the trojan horse for smoothing the system back into conventional polish.

---

## What I Did Instead

> Added discrete, non-decorative motion paired with ARIA live-region updates so state changes are announced. All motion respects `prefers-reduced-motion`, and the discrete style is preserved across the accessible path.
