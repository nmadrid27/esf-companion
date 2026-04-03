# ESF Companion

An extended thinking partner that helps you direct AI from a position you can defend.

No institution, course, or program required. If you use AI to write, research, design, code, or create, the ESF Companion gives you a repeatable process for keeping the work genuinely yours.

---

## Quick Start

**Just installed?** Open **[START_HERE.md](START_HERE.md)** — it covers what got installed, your next 3 steps, and what success looks like.

**[WALKTHROUGH.md](WALKTHROUGH.md)** is the complete guide: install, onboarding, all five phases, and worked examples.

See **[examples](https://github.com/nmadrid27/esf-companion/tree/main/examples)** for filled-in Position Statements, Records of Resistance, and Disclosure Statements across design, writing, research, and consulting contexts.

### Which path should I use?

| | **Templates only** | **Claude.ai / ChatGPT / Gemini** | **Claude Cowork** | **Claude Code** |
|---|---|---|---|---|
| **What you get** | Markdown files to fill in | AI follows ESF process via custom instructions. Claude.ai Projects adds persistent file context. | AI reads ESF files from your computer | Full agent with drift detection, skills, and session memory |
| **Requirements** | None | Any AI chat tool. Claude.ai Projects requires a free or paid Claude.ai account. | Claude Desktop (Pro+) | Claude Code CLI, `bash`, `curl`, `git` |
| **Install** | Download ZIP | Download ZIP or run installer | Download ZIP | Run installer |
| **Best for** | Trying ESF on one project | Regular AI chat users | Desktop Claude users | Developers, power users, students in AI courses |

### Path 1: Download and use the templates (no install needed)

1. Click the green **Code** button at the top of this page, then **Download ZIP**
2. Unzip and open `templates/`
3. Copy `position-statement.md` into your project folder and fill it in before opening any AI tool

```
templates/
├── position-statement.md       ← Write this before AI enters. Every project.
├── record-of-resistance.md     ← One per decision to reject or revise AI output
├── ai-use-log.md               ← One per project: what AI contributed
├── five-questions-checklist.md ← Run at decision points and before submission
└── disclosure-statement.md     ← Add to finished work
```

**Start here:** Copy `position-statement.md` into your project folder and fill it in before opening any AI tool.

### Path 2: Use with Claude.ai, ChatGPT, Gemini, or any conversation tool

Open `prompts/esf-companion.md`, copy the contents, and paste into your AI tool's custom instructions. The AI will follow the ESF process and ask for your Position Statement before helping with project work.

Or run the installer for a cleaner setup:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

Choose option 2 (conversation tools) when prompted. This installs the prompt file, templates, and workflow diagram.

**Claude.ai Projects (recommended):** Create a project in Claude.ai, upload your `companion-state.md` and brief as project knowledge, and paste `prompts/esf-companion.md` as the system prompt. Your context loads automatically every session — no manual paste needed as long as you re-upload `companion-state.md` after each session.

**Next step:** Open `prompts/quick-start.md`, fill in your information at the top, and paste the whole document as your first message.

### Path 3: Use with Claude Cowork (no terminal needed)

1. Download and unzip the repo (see Path 1)
2. Open Claude Desktop and start a Cowork session
3. Point Claude to your folder. It reads the ESF companion prompt and templates directly.

Available on Pro, Max, Team, and Enterprise plans.

### Path 4: Use with Claude Code (full experience)

```bash
mkdir my-project && cd my-project && git init
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

Choose option 1 (Claude Code) when prompted. This installs the agent, skills, reference files, prompts, and templates. Then:

```bash
claude
/esf-onboarding
```

**What the installer does:**
- Asks which AI tool you use
- Asks for a project folder name (creates it if needed)
- Downloads files into your current directory
- Auto-commits Companion files to git (only Companion files, not your existing work)
- Does NOT send data anywhere. Everything is local.

**Already have work in this directory?** The installer adds ESF files alongside your existing files. It will not modify or overwrite your work. See [Using ESF with Existing Work](docs/existing-work.md).

**Next step:** Run `claude`, then `/esf-onboarding`. Close Claude Code after onboarding and write your Position Statement before your first AI session.

---

## Who This Is For

- Writers, researchers, and journalists working with AI drafting tools
- Designers using generative AI in their creative process
- Developers using AI coding assistants
- Consultants producing client deliverables with AI support
- Anyone who needs to answer: "Is this actually my work?"

---

## What This Is

Three stages. Five practices.

**Before AI enters your project:**

- **Position Statement** — Write your direction: your stance, what matters most, what you will not compromise on. This is the gate. AI does not see your project until this exists.

**While working with AI:**

- **Records of Resistance** — Each time you reject or revise an AI suggestion, write what you changed and why. One file per decision.
- **AI Use Log** — Track what AI contributed: tool used, what you asked, what it produced, what you kept, what you changed.
- **Five Questions** — At every decision point: Can I defend this? Is this mine? Did I verify? Would I teach this? Is my disclosure honest?

**Before you submit:**

- **Five Questions** — Run the final check. If any answer is no, stop and fix it.
- **Disclosure** — State honestly what AI contributed and what you contributed. Match detail to audience and stakes.

---

## Just want to start with one thing?

Download `templates/position-statement.md`, fill it in before your next AI session, and stop there. That single step changes the dynamic. Add the other practices when they feel useful.

---

## Understanding ESF

New to the framework?

- **[Essentials](docs/essentials.md)** — The three core practices in under two minutes
- **[What Is ESF?](docs/what-is-esf.md)** — How the framework works, where it came from, and why it is tool-agnostic

---

## FAQ

**Do I need Claude Code?** No. ESF Companion works with any AI tool. Claude Code gives you the richest experience (drift detection, session memory, skills). Claude.ai, ChatGPT, and Gemini get the core process via the companion prompt. Claude.ai Projects adds persistent context without the paste workflow.

**Can I use this with existing work?** Yes. Run the installer inside your existing project directory. It adds ESF files without touching your work. See [Using ESF with Existing Work](docs/existing-work.md).

**Does the installer create a new folder?** It asks if you want one. If you say yes, it creates the folder and installs inside it. If you are already in a project directory, it installs there.

**What is the difference between the companion prompts?** Three options in `prompts/`: `quick-start.md` is a single-paste document (fill in your info, paste the whole thing as your first message — fastest to get started). `companion.md` is a fill-in-your-information template for returning users who have already set up their context. `esf-companion.md` is the full system prompt if you want to configure the AI separately from your context.

---

## The Process

```
1. INQUIRE     Read the brief. Ask yourself what you know, what you
               don't, and what you're assuming. No AI.
       ↓
2. POSITION    Write your Position Statement: your stance, what
               matters most, what you will not compromise on. No AI.
       ↓
3. EXPLORE     Bring AI in as a thinking partner. It challenges
               your position, surfaces alternatives, asks questions.
               It does not originate direction.
       ↓
4. MAKE        Work with AI on the deliverable. Log AI contributions.
               Record every time you reject or revise AI output.
       ↓
5. REFLECT     Run the Five Questions. Write an honest disclosure.
               Compare final work to your Position Statement.
```

The Position Statement is the gate. Everything downstream depends on it. Without it, you have no anchor for evaluating whether the AI's contributions serve your intent or replace it.

---

## Folder Structure (After Installer)

```
your-project/
├── .claude/                          ← Claude Code configuration (optional)
│   ├── agents/
│   │   └── esf-companion.md         ← AI companion identity
│   ├── skills/
│   │   ├── esf-onboarding/          ← Setup wizard
│   │   ├── esf-project/             ← Five-phase workflow
│   │   ├── esf-git/                 ← Commit discipline
│   │   ├── esf-verify/              ← Source verification
│   │   ├── esf-update/              ← Self-update
│   │   └── esf-cognitive/           ← Cognitive techniques
│   └── reference/
│       └── esf-guide.md             ← Framework reference
├── templates/                        ← Blank templates for each practice
├── prompts/
│   ├── esf-companion.md             ← Paste-anywhere system prompt
│   └── companion.md                 ← Compact companion prompt
├── projects/
│   ├── _esf/
│   │   └── companion-state.md       ← Your identity and active contexts
│   └── [your-project]/
│       ├── position-statements/      ← Your direction (write this first)
│       ├── records-of-resistance/    ← Your decisions about AI output
│       ├── ai-use-logs/             ← What AI contributed
│       └── work/                     ← Your deliverables
└── WORKFLOW.md                       ← Process diagram
```

---

## Adapting to Your Domain

The templates use generic language. Adapt them:

| Domain | Position Statement becomes | Records of Resistance track |
|--------|---------------------------|----------------------------|
| Writing | "My argument is X, structured as Y" | Rejected phrasings, restructured sections, removed AI framings |
| Design | "My concept is X, constrained by Y" | Rejected compositions, overridden style suggestions, revised layouts |
| Code | "My architecture is X, optimized for Y" | Rejected implementations, rewritten algorithms, overridden patterns |
| Research | "My hypothesis is X, grounded in Y" | Rejected interpretations, revised analyses, challenged claims |
| Consulting | "My recommendation is X, based on Y" | Rejected framings, revised conclusions, removed unsupported claims |

---

## Adopting ESF for Your Institution

If you teach at a university, college, or training program, see [Adopting ESF for Your Institution](docs/institutional-adoption.md) for a step-by-step customization guide covering agent configuration, project minimums, student distribution, and assessment approaches.

---

## Roadmap

The ESF Companion is actively developed. See [ROADMAP.md](ROADMAP.md) for the full product vision, research foundation (30+ sources), and version plan.

For the complete walkthrough, see [WALKTHROUGH.md](WALKTHROUGH.md).

---

*ESF Companion*
*Nathan Madrid*
*Licensed under CC BY 4.0*
