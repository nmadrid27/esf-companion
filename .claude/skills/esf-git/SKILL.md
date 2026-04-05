---
name: esf-git
description: Use when a user is ready to commit work. Frames git commits as thinking artifacts, not just version control. Surfaces when a commit is also a Record of Resistance.
---

# ESF Git: Commits as Thinking Artifacts

## When to Use

Invoke when the user says "commit," "save my work," "push," or finishes a piece during Build Practice. Do not invoke during Phases 1-2 (human only).

## The Commit Prompt

Walk the user through one question before committing:

> "What did you just build, and does it still reflect your Position Statement?"

Their answer becomes the commit message. Help them structure it as:

```
[piece]: what was built + alignment note

Example:
interaction-layer: built input mapping; aligns with Position Statement re: user agency
pipeline-sketch: revised after AI suggested simpler flow; kept my original architecture (RoR)
```

## Record of Resistance Detection

If the user's answer mentions rejecting, revising, or overriding AI output, flag it:

> "That sounds like a Record of Resistance. Want me to tag this commit as one?"

If yes, add `(RoR)` to the commit message and log it to the session buffer.

## Commit Workflow

1. User describes what they built and whether it aligns
2. You draft the commit message from their description
3. User confirms or edits
4. Stage relevant files (`git add` specific files, not `git add .`)
5. Commit with the confirmed message
6. Log the commit to the session buffer (piece name, weight, RoR flag)

## What Not to Do

- Do not auto-commit without user confirmation
- Do not write commit messages the user did not describe
- Do not introduce branching, PRs, or advanced git workflows
- Do not commit `.session-buffer.md` or other dot-prefixed files
