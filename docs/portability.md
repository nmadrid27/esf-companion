# Portability: What Works Where

ESF Companion is designed to work across any AI tool and any folder structure. This document maps which parts of the workflow are available at each setup level.

---

## Setup levels

| Level | What it requires | What you have |
|---|---|---|
| **Templates only** | Any text editor | Position Statement, Records of Resistance, AI Use Log, Five Questions, Disclosure |
| **Conversation tool** | Any AI chat tool + companion prompt | All templates + AI-guided process in chat |
| **Claude Code** | Claude Code CLI + installer | Full agent: drift detection, skills, session memory, gates |

---

## Feature availability by level

| Feature | Templates only | Conversation tool | Claude Code |
|---|---|---|---|
| Position Statement | Manual (fill in template) | AI prompts and saves | Automatic gate |
| Records of Resistance | Manual (fill in template) | AI prompts | AI prompts, pre-fills "what AI produced" |
| Five Questions | Manual (fill in template) | AI guides | Gate enforced at milestones |
| Disclosure Statement | Manual (fill in template) | AI drafts from session | AI drafts from session logs |
| Drift detection | Self-directed (reread PS each session) | Prompt-guided (ask "am I drifting?") | Automatic (reads PS, flags gaps) |
| Session memory | None | Manual paste or Projects upload | Automatic (`companion-state.md`, session logs) |
| Phase gates | Self-enforced | AI asks but cannot block | Enforced — Companion stops until gate is cleared |
| Scaffolding levels | Not applicable | Not applicable | Guided / Supported / Independent |
| Cognitive techniques | Not applicable | Available on request | Proactive + reactive cadence |
| Educator brief config | Not applicable | Partially (manually described) | Full frontmatter control |

---

## What "portability" means for drift detection

Drift detection without Claude Code is a human practice, not an automated check.

**How to run it yourself:**

Before each AI session, open your Position Statement and read it. Then ask three questions:

1. Is the work still heading where I said it should?
2. Have I made any changes in the last session that I cannot explain without referencing what AI said?
3. Does the current draft still reflect my stated priorities and constraints?

If any answer is no, treat that as a drift flag. Write a Record of Resistance or update your Position Statement with a versioned revision.

The Companion automates this check in Claude Code. In every other setup, the Position Statement is the anchor. The practice is the same; only the automation differs.

---

## Onboarding step audit

Every step in `/esf-onboarding` labeled by what it requires:

| Step | Label | Notes |
|---|---|---|
| Step 0: Workspace scan | Claude Code only | Filesystem scan requires Claude Code tools |
| Step 1: Welcome and ESF overview | Required (any platform) | Can run as a chat message on conversation tools |
| Step 2: What are you working on | Required (any platform) | Role inference works identically in chat |
| Step 2b: Educator path | Required (any platform) | Conversation-guided; no automation needed |
| Step 3: Active contexts | Required (any platform) | Collecting context labels; no filesystem needed |
| Step 4: Current project | Required (any platform) | Optional; same in chat |
| Step 5-6: Create and write companion-state.md | Claude Code only | File creation requires Claude Code or manual creation |
| Step 7: Create folder structure | Claude Code only | `mkdir` commands require Claude Code |
| Step 8: Explain ESF process | Required (any platform) | Pure explanation; works in any medium |
| Step 9: Confirm and close | Required (any platform) | Closing instruction; platform-agnostic |

**On conversation tools:** Steps 0, 5-6, and 7 are skipped or replaced with instructions for manual setup. The conversation prompt in `prompts/esf-companion.md` covers the equivalent of Steps 1-4 and 8-9 on first use.

**Zero-install path:** Steps 0 and 5-9 are replaced by a single instruction: fill in `position-statement.md` before your next AI session. No setup, no state file, no folder structure required.

---

## What any-repo means

The Companion does not require a specific folder structure. It works in:

- An existing git repository (add templates alongside your files)
- A folder on your desktop with no version control
- A shared folder in Dropbox, Google Drive, or iCloud
- A Notion workspace (copy template text into a page)
- A plain text file with no folder at all

The only requirement is that the Position Statement exists before AI enters the work. Everything else is optional scaffolding that you add when it becomes useful.
