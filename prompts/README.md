# ESF Companion: Prompts for Any LLM

The ESF Companion is framework-agnostic. The `.claude/` directory is the Claude Code implementation. This folder contains the same content as plain-text prompts you can use with ChatGPT, Gemini, Claude.ai, or any other AI assistant.

---

## How to Use

### Step 1: Set up your companion prompt

Open `companion.md` and fill in every `[PLACEHOLDER]` with your information. Save it in your project folder so the AI can find it.

This is your persistent identity file. It tells the AI who you are, what courses you are in, and what project you are currently working on.

### Step 2: Start a session

**If you use Claude Code:** The AI reads your `companion.md` and `project-workflow.md` automatically from your toolkit folder. Just tell it what project you want to work on.

**If you use ChatGPT, Gemini, or another tool:** Paste your filled-in `companion.md` as your first message (or as a system prompt if your tool supports it). Then paste `project-workflow.md` as a second message.

```
[paste companion.md with your info filled in]
[paste project-workflow.md]

Now: I want to work on [project name].
```

The AI now has your identity context and the full ESF workflow instructions.
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

When you start a new course, update the Enrolled Courses and Current Project sections of your `companion.md`. Previous course entries stay; they are part of your record.
