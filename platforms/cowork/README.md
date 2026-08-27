# ESF Companion Plugin

**Current version:** 0.11.0 ([changelog](https://github.com/nmadrid27/esf-companion/blob/main/CHANGELOG.md) · [releases](https://github.com/nmadrid27/esf-companion/releases))

A toolkit for AI-assisted creative work. Helps students, educators, and professionals stay the author of their own thinking by enforcing the right sequence: your position before AI engagement, then monitoring for drift throughout.

Built on the [Epistemic Stewardship Framework](https://github.com/nmadrid27/esf-companion).

---

## What It Does

The ESF Companion works through five phases:

1. **Inquire.** Human only. No AI. You work out what you already know and think.
2. **Position.** Human only. You write a Position Statement before AI enters.
3. **Explore.** AI challenges your position. Expands, probes, and pressure-tests your thinking.
4. **Make.** AI as drafting support. Builds with you, anchored to your Position Statement.
5. **Reflect.** AI reviews the work. Five Questions, reflection, disclosure, and session synthesis.

Drift detection runs continuously. When your work moves away from your stated position, or when you start accepting AI output without evaluation, the Companion surfaces it as a question, not a command. You decide what to do.

**Position Statement nudges (v0.7.0).** When you start substantive work without a Position Statement on file, the Companion uses a two-tier nudge. The first touch is a one-line inline reminder you can ignore, dismiss, or answer. If you make a structural edit (changing a claim, an attributed quote, a specific datum, or the document's argument) and still have no Position Statement, the Companion escalates to a selection card with four options: write one offline, talk it through in three questions, skip for this document, or skip for this session. `silent_mode: true` in `companion-state.md` suppresses both tiers; the Position Statement gate in Gate Mode still applies.

---

## Components

### Skills

| Skill | Triggers |
|-------|----------|
| `esf-project` | Starting or resuming a project, any ESF phase work, "start my project," "let's explore," "help me make," "review my work" |
| `esf-verify` | "Verify those claims," "check what you said," `/esf-verify`, after AI produces factual claims in Phase 3 or 4 |

### Commands

| Command | What it does |
|---------|-------------|
| `/esf-start` | Initialize a new ESF workspace or resume an existing one. First-time users get a short onboarding. Returning users pick up from their current phase. |
| `/esf-brief` | Load a project brief (course assignment, client scope, research proposal, or personal spec) and set up milestone tracking. Parses deliverables, timeline, and ESF requirements from any format. |
| `/esf-status` | One-screen snapshot: current phase, Position Statement status, Records of Resistance count vs. required minimum, session log history, and next action. |
| `/esf-cognitive` | Run a cognitive technique on demand: lateral thinking, perspective shift, analogical reasoning, or constraint manipulation. Preview cards show what each technique involves before you commit. |
| `/esf-log` | End-of-session synthesis. Reads the session buffer, generates a session log for your review, saves it, and updates PROJECT.md and companion-state.md. |
| `/esf-demo` | Run a guided demo session on a sample studio project. Scaffolds a sandbox at `demo/critical-cartography/` and walks through all five phases at accelerated pace, exercising every gate, prompt, and selection card. Use `/esf-demo --reset` to clear the sandbox. |

---

## Setup

1. Install this plugin in Cowork.
2. Open the folder where you want to work (your project folder, course folder, or ESF workspace).
3. Run `/esf-start`.

That's it. The plugin reads `companion-state.md` from your selected folder to carry state across sessions. If the file doesn't exist, `/esf-start` creates it during onboarding.

**Note on full onboarding:** The complete ESF Companion onboarding (structured-workspace detection, companion-notes setup, position-statement draft from existing content) runs via the Claude Code path (`/esf-onboarding`), not this plugin. If you are setting up a new workspace from scratch, run onboarding in Claude Code first. The `companion-state.md` and `companion-notes.md` files that onboarding creates carry over automatically when you open the same folder in Cowork.

**No environment variables or external services required.** All state lives in markdown files in your selected folder.

---

## Usage

### Starting fresh

```
/esf-start
```

The Companion will ask about your role and context, then walk you through initializing a project. At the end of setup, you'll be oriented to Phase 1 and told to work offline before returning.

### Resuming a project

```
/esf-start
```

Same command. If `companion-state.md` exists, it reads your current state and orients you to where you left off.

### Loading a brief

```
/esf-brief
```

Drop a brief into `esf/[context]/briefs/` and run this command. It reads any format: course assignments, client scopes, research proposals, personal project specs. Extracts deliverables, timeline, AI boundaries, and ESF requirements. Sets up a milestone tracker in the sidebar. If you don't have a document, it asks 4 questions and generates one.

### Running a cognitive technique

```
/esf-cognitive
```

Breaks fixation and reframes thinking on demand. Choose from lateral thinking, perspective shift, analogical reasoning, or constraint manipulation. Each technique takes 5 to 10 minutes and connects back to your Position Statement.

### Checking where you are

```
/esf-status
```

Shows your current phase, what artifacts exist, what's missing, and your next recommended action.

### Ending a session

```
/esf-log
```

Saves your session log, updates PROJECT.md, and clears the session buffer. Run this at the end of every working session.

### Verifying AI claims

```
/esf-verify
```

Or just ask "let's verify that" after AI produces factual claims. Surfaces the claims as a numbered list, walks you through checking each one, and logs results to your AI Use Log.

---

## Folder Structure

After running `/esf-start`, your project folder will look like this:

```
your-workspace/
└── esf/
    ├── companion-state.md      # Your identity, active contexts, current project
    └── [context]/
        ├── briefs/             # Project brief goes here
        ├── position-statements/
        ├── records-of-resistance/
        ├── ai-use-logs/
        ├── gate-records/
        ├── reflections/
        ├── logs/               # Session logs and .session-buffer.md
        └── PROJECT.md          # Current project state (one screen)
```

---

## Brief Formats

The plugin works with any brief format. `/esf-brief` reads the document and extracts what it can.

**Structured briefs** with YAML frontmatter give the most precise control:

```yaml
---
position-statement: required    # required / optional / not-required
five-questions: required
ror-minimum: 3
ai-use: permitted-after-position
---
```

**Unstructured briefs** (client scopes, research proposals, personal specs) work too. The plugin reads the prose, extracts deliverables and timeline, and asks you about anything it can't infer.

**No brief at all** is fine. Run `/esf-brief` and answer 4 questions. The plugin generates a minimal brief you can edit.

For educators: place course briefs in `esf/[course]/briefs/`. When anyone runs `/esf-start` and then `/esf-brief`, the Companion reads the requirements automatically.

---

## Source

This plugin is the Cowork-packaged version of the ESF Companion, which also runs in Claude Code, ChatGPT (custom instructions), and any AI tool that accepts system prompts.

Full source, install script, and documentation: [github.com/nmadrid27/esf-companion](https://github.com/nmadrid27/esf-companion)
