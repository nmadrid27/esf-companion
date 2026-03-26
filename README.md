# ESF Companion

An extended thinking partner that helps you direct AI from a position you can defend.

No institution, course, or program required. If you use AI to write, research, design, code, or create, the ESF Companion gives you a repeatable process for keeping the work genuinely yours.

---

## Understanding ESF

New to the framework? Start here:

- **[Essentials](docs/essentials.md)** — The three core practices in under two minutes
- **[What Is ESF?](docs/what-is-esf.md)** — How the framework works, where it came from, and why it is tool-agnostic

---

## What This Is

Five practices, applied before, during, and after AI-assisted work:

1. **Position Statement** — Write down your direction before AI enters. What is your stance? What matters most? What will you not compromise on? This anchors the session so AI assists your thinking rather than replacing it.

2. **Five Questions** — At every decision point, ask: Can I defend this? Is this mine? Did I verify? Would I teach this? Is my disclosure honest? If any answer is no, stop and fix it.

3. **Records of Resistance** — When you reject, revise, or override an AI suggestion, write down what you changed and why. This builds a record of your judgment, not just the AI's output.

4. **AI Use Log** — Track what AI contributed to each piece of work: tool used, what you asked, what it produced, what you kept, what you changed.

5. **Disclosure** — State honestly what AI contributed and what you contributed. Match the level of detail to the audience and stakes.

---

## Who This Is For

- Writers, researchers, and journalists working with AI drafting tools
- Designers using generative AI in their creative process
- Developers using AI coding assistants
- Consultants producing client deliverables with AI support
- Anyone who needs to answer: "Is this actually my work?"

---

## Quick Start

After installing, open **[START_HERE.md](START_HERE.md)** for your next steps.

See **[examples/](examples/)** for filled-in Position Statements, Records of Resistance, and Disclosure Statements.

### Which path should I use?

| | **Templates only** | **ChatGPT / Gemini** | **Claude Cowork** | **Claude Code** |
|---|---|---|---|---|
| **What you get** | Markdown files to fill in | AI follows ESF process via custom instructions | AI reads ESF files from your computer | Full agent with drift detection, skills, and session memory |
| **Requirements** | None | Any AI chat tool | Claude Desktop (Pro+) | Claude Code CLI, `bash`, `curl`, `git` |
| **Install** | Download ZIP | Download ZIP or run installer | Download ZIP | Run installer |
| **Best for** | Trying ESF on one project | Regular AI chat users | Desktop Claude users | Developers, power users, students in AI courses |

### Path 1: Download and use the templates (no install needed)

1. Click the green **Code** button at the top of this page, then **Download ZIP**
2. Unzip and open `templates/`
3. Copy `position-statement.md` into your project folder and fill it in before opening any AI tool

```
templates/
├── position-statement.md      ← Fill out before each AI session
├── record-of-resistance.md    ← One per decision to reject/revise AI output
├── ai-use-log.md              ← One per project or document
├── five-questions-checklist.md ← Run at each review point
└── disclosure-statement.md    ← Add to finished deliverables
```

### Path 2: Use with ChatGPT, Gemini, or any conversation tool

Open `prompts/esf-companion.md`, copy the contents, and paste into your AI tool's custom instructions. The AI will follow the ESF process and ask for your Position Statement before helping with project work.

Or run the installer for a cleaner setup:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

Choose option 2 (conversation tools) when prompted. This installs the prompt file, templates, and workflow diagram.

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
- Auto-commits toolkit files to git (only toolkit files, not your existing work)
- Does NOT send data anywhere. Everything is local.

**Already have work in this directory?** The installer adds ESF files alongside your existing files. It will not modify or overwrite your work. See [Using ESF with Existing Work](docs/existing-work.md).

---

## FAQ

**Do I need Claude Code?** No. ESF Companion works with any AI tool. Claude Code gives you the richest experience (drift detection, session memory, skills). ChatGPT and Gemini get the core process via the companion prompt.

**Can I use this with existing work?** Yes. Run the installer inside your existing project directory. It adds ESF files without touching your work. See [Using ESF with Existing Work](docs/existing-work.md).

**Does the installer create a new folder?** It asks if you want one. If you say yes, it creates the folder and installs inside it. If you are already in a project directory, it installs there.

**What is the difference between `companion.md` and `esf-companion.md`?** Both are companion prompts. `esf-companion.md` is the original full prompt. `companion.md` is a streamlined version. Use whichever works for your AI tool's custom instructions limit.

---

## The Process

```
1. POSITION    Write your Position Statement. No AI yet.
       ↓
2. EXPLORE     Bring AI in as a thinking partner. It challenges
               your position, surfaces alternatives, asks questions.
               It does not originate direction.
       ↓
3. BUILD       Work with AI on the deliverable. Log AI contributions.
               Record every time you reject or revise AI output.
       ↓
4. VALIDATE    Run the Five Questions. Fix anything that fails.
       ↓
5. DISCLOSE    Write an honest disclosure statement.
               Attach it to the finished work.
```

The Position Statement is the gate. Everything downstream depends on it. Without it, you have no anchor for evaluating whether the AI's contributions serve your intent or replace it.

---

## Folder Structure (After Installer)

```
your-project/
├── .claude/                          ← Claude Code configuration (optional)
│   ├── agents/
│   │   └── esf-companion.md         ← AI companion identity
│   └── reference/
│       └── esf-guide.md             ← Framework reference
├── templates/                        ← Blank templates for each practice
├── prompts/
│   └── esf-companion.md             ← Paste-anywhere system prompt
├── projects/
│   └── [your-project]/
│       ├── position-statement.md     ← Your direction (write this first)
│       ├── records-of-resistance/    ← Your decisions about AI output
│       ├── ai-use-log.md            ← What AI contributed
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
