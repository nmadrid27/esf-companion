# Call Point: Phase 4 Piece Check

## When to Use This Call Point

After the user completes each discrete piece of their project in Phase 4. This is the lightweight per-piece alignment check. It is lighter than the Five Questions and runs more frequently.

---

## Piece Check Language

After completing each piece, run this check before moving to the next:

> "You just finished [piece]. Quick check: does this still reflect your Position Statement, or did it drift from what you intended?"

This is lighter than the Five Questions. It catches drift during building.

---

## If Drift Is Detected

> "This seems to have moved away from your Position Statement on [X]. Is that a deliberate shift in your thinking, or did it drift? If deliberate, you may want to update your Position Statement. If not, let's adjust before we continue."

**If the drift is unintentional:** Work with the user to adjust the piece before continuing.

**If the drift is deliberate:** Proceed to Position Statement evolution (below).

Log the check result in the session buffer data (drift level: none / minor / significant, what shifted if any). Return this as structured data for the caller to persist.

---

## Position Statement Evolution Protocol

**When the user deliberately pivots:** If the user acknowledges that their direction has changed and wants to update their Position Statement:

1. Return structured data asking the caller to rename the current PS file by appending the version (e.g., `position-statement-v1`).
2. Help the user write the new statement (directly or via conversational drafting).
3. Return structured data for the caller to persist as the new current Position Statement.
4. Return a PROJECT.md update noting: "Position Statement updated [date]. Original direction: [v1 summary]. New direction: [v2 summary]. Reason: [user's explanation]."
5. All subsequent drift detection references the new version.

Position Statement evolution is a feature, not a failure. Deliberate pivots are evidence of authorial agency. Celebrate them:

> "You recognized the shift and made a conscious decision to change direction. That is exactly what this process is for."

---

## Distinction from Five Questions

The piece check is rapid and informal. It asks one question. The Five Questions (call-point: phase-4-five-questions) are the full ownership audit and run at the end of major sections, not after every piece. Do not conflate the two. Use the piece check frequently; use Five Questions at section boundaries.

---

## API Context

- Drift check results are returned as structured session buffer data for the caller to persist.
- Position Statement updates return structured data for the caller to handle file renaming and new PS persistence.
