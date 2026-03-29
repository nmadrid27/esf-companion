# courses/

This folder is available for educators who want to distribute pre-configured course templates to students.

It is not required by the Companion at runtime. The Companion reads course-specific requirements from each student's `projects/_esf/companion-state.md`, not from here.

---

## What this folder is for

If you teach a course that uses ESF Companion, you can place a course configuration template here so students can reference the expected ESF requirements for your course before or during onboarding.

A course config is a plain Markdown file that documents:
- The course name and code
- The ESF level your course uses (full, lightweight, or drift-only)
- Required Records of Resistance count (if any)
- Position Statement requirements (required, optional, or self-defined)
- Five Questions enforcement (gate mode or mirror mode)
- Any course-specific context notes students should know

---

## Example config file

Create a file like `courses/AI-180.md`:

```markdown
# AI 180: Artificial Intelligence in Creative Practice

**ESF level:** full
**Position Statement:** required before AI engagement (Phase 2)
**Records of Resistance:** minimum 3 per project
**Five Questions:** required at project close (gate mode)
**Notes:** Position Statements are called "Design Intent" in this course.
```

Students can read this during onboarding to know what your course requires
before they configure their own `companion-state.md`.

---

## Distribution option

If you fork this repo for your course, you can pre-populate `courses/` with your
course configs so they are included when students run the install script.

See `docs/institutional-adoption.md` for full educator distribution guidance.
