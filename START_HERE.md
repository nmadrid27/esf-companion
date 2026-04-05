# Start Here

You just installed the ESF Companion.

---

## What got installed

**Claude Code install:**

```
.claude/
├── agents/esf-companion.md       ← AI companion identity
├── skills/                       ← Six skills (onboarding, project, git, verify, update, cognitive)
└── reference/                    ← Framework guide and disclosure protocol
templates/                        ← Blank forms for each ESF practice
prompts/                          ← System prompt for conversation tools
WORKFLOW.md                       ← Visual process diagram
```

**Conversation tool install (Claude.ai, ChatGPT, Gemini):**

```
templates/                        ← Blank forms for each ESF practice
prompts/                          ← System prompt and quick-start document
WORKFLOW.md                       ← Visual process diagram
```

---

## Your next 3 steps

**If you are on Claude Code:**

1. Open Claude Code in your project directory: `claude`
2. Run `/esf-onboarding` — it walks you through writing a Position Statement for your project and sets up your workspace
3. If you wrote your Position Statement during onboarding, you can jump straight into Phase 3. Otherwise, write it offline and come back when it's ready

**If you are on Claude.ai, ChatGPT, Gemini, or another conversation tool:**

1. Open `prompts/quick-start.md`
2. Fill in your information at the top
3. Paste the whole document as your first message — that is your entire setup

**If you are on Claude.ai Projects:**

1. Create a project in Claude.ai
2. Upload `companion-state.md` and your brief as project knowledge
3. Set `prompts/esf-companion.md` as the system prompt — your context loads automatically each session

---

## What success looks like

After setup, the ESF Companion has one job: keep your thinking yours when you work with AI.

You will know it is working when:

- You write a Position Statement before AI sees your project, not after
- You can explain any part of your work without referencing what AI said
- Your Records of Resistance show decisions you made, not just output you accepted
- Your disclosure statement is honest and matches what actually happened

The Position Statement is the gate. Everything else follows from it.

---

## Customizing the Companion

**Silence mode** reduces how often the Companion speaks during a session. To turn it on, open `projects/_esf/companion-state.md` and set:

```
## Preferences

- **silent_mode:** true
```

With silent mode on, the Companion suppresses proactive prompts, phase announcements, drift observations for low-significance moments, and unprompted check-ins. It still enforces the Position Statement gate, Five Questions, and disclosure requirement. Those cannot be silenced.

**If you are a student:** Silent mode is accepted, but a warning will appear once per session noting that blocking checkpoints remain active. If your instructor's brief requires full scaffolding, silent mode will be overridden automatically.

---

## Reference links

- **[WALKTHROUGH.md](WALKTHROUGH.md)** — Complete guide: onboarding, all five phases, worked examples
- **[WORKFLOW.md](WORKFLOW.md)** — Visual process diagram
- **[templates/](templates/)** — Blank forms: Position Statement, Record of Resistance, AI Use Log, Five Questions, Disclosure
- **[examples](https://github.com/nmadrid27/esf-companion/tree/main/examples)** — Filled samples across design, writing, research, and consulting
- **[ROADMAP.md](ROADMAP.md)** — What is shipped, what is coming
