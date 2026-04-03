# ESF Companion — Cowork Guide

This file is for Claude Desktop Cowork users. It maps verbal phrases to the ESF Companion behaviors that Claude Code users invoke with `/` commands. Read this once so you know what to say.

---

## How Cowork Works With the Companion

When you open a Cowork session and point Claude to this folder, the Companion agent (`esf-companion.md`) loads automatically. Your identity, project context, and current phase are read from `projects/_esf/companion-state.md`.

You do not need to invoke skills manually. Use the phrases below and Claude responds with the equivalent behavior.

---

## Verbal Commands

### Session Start

> "Start my session" / "Let's work on [project]" / "Pick up where we left off"

Claude reads your companion state, shows your current phase and project, and orients you to where you left off. If you have a session log, it surfaces what you noted for next time.

---

### Project Work

> "I want to start a new project" / "Set up [project name]"

Claude walks you through creating a companion-state entry, a brief (if needed), and your Position Statement. Same flow as `/esf-onboarding` for a new context.

> "Here is my Position Statement" / "I've written my position"

Paste your Position Statement and Claude saves it, runs a readability pass, and opens Phase 3 (Explore).

> "Let's explore" / "Challenge my thinking"

Opens the Explore phase. Claude pressure-tests your position, offers alternatives, and surfaces tensions — one thread at a time.

> "Let's build" / "I'm ready to make"

Opens Phase 4 (Make). Claude tracks your deliverables, prompts Records of Resistance when you reject or revise AI output, and monitors for drift.

> "Run the Five Questions" / "Final check before I submit"

Opens Phase 5 (Reflect). Claude walks through all five questions and prompts your disclosure statement.

---

### Drift and Cognitive Support

> "Drift check" / "Am I still on track?"

Claude compares your current work against your Position Statement and flags any direction, priority, or boundary drift it detects.

> "I'm stuck" / "Help me get unstuck" / "Cognitive techniques"

Claude offers one relevant technique based on where you are and what kind of stuck you seem to be. It will name the technique and show how to apply it to your specific problem right now.

---

### Records and Logs

> "I rejected that" / "I changed this" / "Record of Resistance"

Claude prompts you through a Record of Resistance: what AI suggested, what you changed, and why. Saves it to `projects/[context]/records-of-resistance/`.

> "Log that" / "Add to my AI Use Log"

Claude adds an entry to your AI Use Log for the current session exchange.

---

### Session End

> "Done for today" / "Wrap up" / "End session"

Claude generates your AI Use Log draft, presents the session log for review, saves it after confirmation, updates your project state, and clears the session buffer.

---

## Notes on Cowork vs. Claude Code

| Feature | Cowork | Claude Code |
|---|---|---|
| Agent identity | Automatic | Automatic |
| Skill invocation | Verbal phrases (this file) | `/` commands |
| Drift detection | Always on | Always on |
| Cognitive techniques | Offered proactively by agent | Offered by `esf-project` skill |
| Session memory | Manual (companion-state.md) | Automatic |
| File creation | Claude creates files for you | Claude creates files for you |

Everything in Cowork works — it just uses natural language instead of commands.
