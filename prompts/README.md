# ESF Companion: Prompts for Any LLM

The ESF Companion is framework-agnostic. The `.claude/` directory is the Claude Code implementation. This folder contains the same content as plain-text prompts you can use with ChatGPT, Gemini, Claude.ai, or any other AI assistant.

---

## Which File Should I Use?

| File | Use when |
|------|----------|
| `quick-start.md` | **New user. Fastest path.** Fill in your info at the top, paste the whole file as your first message. One step. |
| `companion.md` | Returning user. Fill in your current context and paste as a system prompt or first message. |
| `esf-companion.md` | Full system prompt only. Use if you want to set up the AI instructions separately from your identity context. |
| `project-workflow.md` | Full workflow instructions. Paste alongside `companion.md` for the complete session setup. |

**Recommended for new users:** Open `quick-start.md`, fill in the four placeholders at the top, paste the entire file as your first message. You are ready to work.

---

## How to Use

### Step 1: Set up your companion prompt

**New users:** Open `quick-start.md`, fill in your name, discipline, project, and current phase. Paste the whole document as your first message.

**Returning users:** Open `companion.md` and fill in every `[PLACEHOLDER]` with your information. Save it in your project folder so the AI can find it. This is your persistent identity file. It tells the AI who you are, what courses you are in, and what project you are currently working on.

### Step 2: Start a session

**If you use Claude Code:** The AI reads your `companion.md` and `project-workflow.md` automatically from your Companion folder. Just tell it what project you want to work on.

**If you use Claude.ai, ChatGPT, Gemini, or another conversation tool:**

*First session on a project:* Paste your filled-in `companion.md` as your first message (or as a system prompt if your tool supports it). Then paste `project-workflow.md` as a second message.

```
[paste companion.md with your info filled in]
[paste project-workflow.md]

Now: I want to work on [project name].
```

*Returning to a project:* Paste `PROJECT.md` first, then paste `project-workflow.md`. PROJECT.md is the portable context object the Companion generates at the end of each session — it carries your phase, position summary, Records of Resistance count, and next step.

```
[paste PROJECT.md from your last session]
[paste project-workflow.md]

Now: picking up from where I left off.
```

The AI now has your current project context and the full ESF workflow instructions.

**If you use Claude.ai Projects:**

Projects let you skip most of the paste workflow. Create a project, add these files as project knowledge, and set `esf-companion.md` as the system prompt:

- `companion.md` (your filled-in identity file)
- Your project brief (if you have one)

The Companion loads your context automatically at the start of every conversation. For returning sessions, still paste your PROJECT.md to restore where you left off — project knowledge does not carry session-level continuity on its own.
### Step 3: Maintain your project files

Keep your project files organized the same way as the Claude Code version:

```
your-project-folder/
├── briefs/                 ← Drop your project brief here
├── position-statements/    ← Write this before any AI engagement
├── records-of-resistance/  ← Document your deliberate choices
└── work/                   ← Your project output
```

When referencing a file, copy its contents into your chat. The AI cannot read your file system; you bring the content to it.

---

## Differences from Claude Code

| Feature | Claude Code | Any LLM |
|---------|-------------|---------|
| User context | Loaded automatically | Paste at session start |
| Position Statement gate | Checks file system automatically | You confirm verbally or paste the file |
| File creation | AI creates files for you | You create files yourself |
| Session memory | Persists within session | Persists within conversation |
| Onboarding | Interactive `/esf-onboarding` skill | Fill in placeholders manually |

The ESF process works the same way in both. The difference is automation, not substance.

---

## Updating Your Companion Prompt

When you start a new project or context, update the Current Project section of your `companion.md`. Previous entries stay; they are part of your record.

Also save the PROJECT.md block the Companion generates at the end of each session. That file is your portable context object: paste it at the start of your next session instead of re-explaining where you left off.
