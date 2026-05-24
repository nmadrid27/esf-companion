# ESF Companion

A toolkit for directing AI from a position you can defend.

No institution, course, or program required. If you use AI to write, research, design, code, or create, the ESF Companion gives you a repeatable process for keeping the work genuinely yours.

---

## Quick Start

**Just installed?** Open `esf/toolkit/START_HERE.md` in your project: it covers what got installed, your next 3 steps, and what success looks like.

**[WALKTHROUGH.md](WALKTHROUGH.md)** is the complete guide: install, onboarding, all five phases, and worked examples.

See **[examples](https://github.com/nmadrid27/esf-companion/tree/main/examples)** for filled-in Position Statements, Records of Resistance, and Disclosure Statements across design, writing, research, and consulting contexts.

### Which setup is right for me?

**Three questions:**

1. Do you use the command line (Terminal or bash)? No → go to 2. Yes → go to 4.
2. Do you have Claude Desktop (Pro+ plan)? Yes → Path 3 (Cowork). No → go to 3.
3. Do you want the AI to follow the ESF process automatically in chat? No → Path 1 (templates only). Yes → Path 2 (conversation tool).
4. Do you want drift detection, session memory, and `/` commands? Yes → Path 4 (Claude Code). Not sure → Path 1 or Path 2 first.

| | **Templates only** | **Claude.ai / ChatGPT / Gemini** | **Claude Cowork** | **Claude Code** |
|---|---|---|---|---|
| **What you get** | Markdown files to fill in | AI follows ESF process via custom instructions. Claude.ai Projects adds persistent file context. | AI reads ESF files from your computer | Full agent with drift detection, skills, and session memory |
| **Requirements** | None | Any AI chat tool | Claude Desktop (Pro+) | Claude Code CLI, `bash`, `curl`, `git` (see [Windows instructions](#windows-installation)) |
| **Install** | None | Download ZIP or run installer | Download ZIP | Run installer |
| **Best for** | Any tool, any folder, no setup | Regular AI chat users | Desktop Claude users | Developers, power users, students in AI courses |

**Not sure where to start?** Path 1 is the zero-install option. No terminal, no account, no install script. Download two files, open one, fill it in.

### Path 1: Download and use the templates (no install needed)

**Minimum viable setup (two files):**

1. Download `templates/position-statement.md` and `templates/record-of-resistance.md` from the [templates folder](https://github.com/nmadrid27/esf-companion/tree/main/templates)
2. Copy `position-statement.md` into your current project folder
3. Fill it in before opening any AI tool

That is a complete ESF setup for one project. No folder structure required. Works in any text editor, on any AI tool, in any repo.

**Full templates folder (when you want more):**

```
templates/
├── position-statement.md       ← Write this before AI enters. Every project.
├── record-of-resistance.md     ← One per decision to reject or revise AI output
├── ai-use-log.md               ← One per project: what AI contributed
├── five-questions-checklist.md ← Run at decision points and before submission
└── disclosure-statement.md     ← Add to finished work
```

**Drift detection on Path 1:** Without Claude Code, drift detection is self-directed. Before each session, reread your Position Statement and ask: is the work still heading where I said it should? The Companion cannot run this check automatically without Claude Code, but your Position Statement gives you the anchor to run it yourself. That is intentional: the practice is the point, not the automation.

**To download the full repo instead:**

1. Click the green **Code** button at the top of this page, then **Download ZIP**
2. Unzip and open `templates/`
3. Copy any template into your project folder and fill it in

**Start here:** Copy `position-statement.md` into your project folder and fill it in before opening any AI tool.

If you later run the installer, those same files are set up for you at `esf/toolkit/templates/`. The GitHub download path and the installed path differ on purpose: GitHub paths stay at the repo root so the no-install workflow has simple download URLs.

### Path 2: Use with Claude.ai, ChatGPT, Gemini, or any conversation tool

Open `prompts/esf-companion.md`, copy the contents, and paste into your AI tool's custom instructions. The AI will follow the ESF process and ask for your Position Statement before helping with project work.

Or run the installer for a cleaner setup:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

Choose option 2 (conversation tools) when prompted. This installs the prompt file, templates, and workflow diagram.

After install, those files live under `esf/toolkit/prompts/`. The installer creates that layout; the GitHub repo source keeps `prompts/` at the root for the no-install workflow.

**Claude.ai Projects (recommended):** Create a project in Claude.ai, upload your `companion-state.md` and brief as project knowledge, and paste `esf/toolkit/prompts/esf-companion.md` as the system prompt. Your context loads automatically every session (no manual paste needed as long as you re-upload `companion-state.md` after each session).

**Next step:** Open `esf/toolkit/prompts/quick-start.md`, fill in your information at the top, and paste the whole document as your first message.

### Path 3: Use with Claude Cowork (no terminal needed)

1. Download and unzip the repo (see Path 1)
2. Open Claude Desktop and start a Cowork session
3. Point Claude to your folder. It reads the ESF companion prompt and templates directly.

Available on Pro, Max, Team, and Enterprise plans.

### Path 4: Use with Claude Code (full experience)

```bash
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

**Next step:** Run `claude`, then `/esf-onboarding`.

### `/esf-defense-pack`

Generate a portable **Defense Pack** from your existing ESF artifacts: a self-contained HTML walkthrough, a print-ready document, and a recording script with timing cues, all built from your Position Statement, Records of Resistance, AI Use Log, and Reflection. Walk an instructor through it in an oral defense or crit. See [Defense Pack design](docs/2026-05-20-defense-pack-design.md).

- Path 1 users: see `templates/defense-pack-checklist.md` for manual assembly.
- Path 2 users: the conversational Companion prompt now includes Defense Pack assembly guidance.

### Windows Installation

The installer requires `bash`, which is not built into Windows. There are three ways to run it.

**Option A: Git Bash (recommended for most users)**

[Git for Windows](https://gitforwindows.org/) includes Git Bash, a terminal that supports `bash`, `curl`, and `git` out of the box.

1. Install [Git for Windows](https://gitforwindows.org/) if you have not already
2. Open **Git Bash** (search for it in the Start menu)
3. Navigate to your project folder:
   ```bash
   cd /c/Users/YourName/projects/my-project
   ```
4. Run the installer:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
   ```

Everything else works the same as on macOS or Linux.

**Option B: WSL (Windows Subsystem for Linux)**

If you already use WSL, run the installer from your WSL terminal. Your Windows files are accessible at `/mnt/c/`.

1. Open your WSL terminal (Ubuntu, Debian, etc.)
2. Navigate to your project folder:
   ```bash
   cd /mnt/c/Users/YourName/projects/my-project
   ```
3. Run the installer:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
   ```

**Option C: Download manually (no terminal needed)**

If you do not want to use a terminal at all, use Path 1 (templates only) or Path 2 (conversation tool):

1. Click the green **Code** button at the top of this page, then **Download ZIP**
2. Unzip into your project folder
3. For conversation tools: open `prompts/quick-start.md`, fill in your info, and paste into your AI tool
4. For templates only: copy `templates/position-statement.md` into your project and fill it in

**Using Claude Code on Windows:**

Claude Code runs on Windows via WSL. To set it up:

1. Install WSL if you have not already: open PowerShell as Administrator and run `wsl --install`
2. Install Claude Code inside WSL following the [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
3. Navigate to your project folder and run `claude`

Claude Code on the web (claude.ai/code) and Claude Code in VS Code or JetBrains IDEs work on Windows natively without WSL. If you use one of those, run the installer from Git Bash (Option A) to set up the ESF files, then use Claude Code from your IDE or browser.

---

## Who This Is For

- Writers, researchers, and journalists working with AI drafting tools
- Designers using generative AI in their creative process
- Developers using AI coding assistants
- Consultants producing client deliverables with AI support
- Context engineers and prompt developers building AI configurations
- Anyone who needs to answer: "Is this actually my work?"

ESF Companion is a craft standard for directed AI use. It originated in an education context, where the stakes of cognitive drift are visible in student work. The same risks apply to any practitioner doing serious AI-assisted work: a context engineer whose system prompt gradually reflects model defaults rather than design intent, a researcher whose argument shifts to accommodate AI framing, a designer whose concept drifts toward AI aesthetic defaults. The mechanism is the same problem in different contexts. The framework addresses all of them.

---

## What This Is

Three stages. Five practices.

**Before AI enters your project:**

- **Position Statement:** Write your direction: your stance, what matters most, what you will not compromise on. This is the gate. AI does not see your project until this exists.

**While working with AI:**

- **Records of Resistance:** Each time you reject or revise an AI suggestion, write what you changed and why. One file per decision.
- **AI Use Log:** Track what AI contributed: tool used, what you asked, what it produced, what you kept, what you changed.
- **Five Questions:** At every decision point: Can I defend this? Is this mine? Did I verify? Would I teach this? Is my disclosure honest?

**Before you submit:**

- **Five Questions:** Run the final check. If any answer is no, stop and fix it.
- **Disclosure:** State honestly what AI contributed and what you contributed. Match detail to audience and stakes.

---

## Just want to start with one thing?

Download `templates/position-statement.md`, fill it in before your next AI session, and stop there. That single step changes the dynamic. Add the other practices when they feel useful.

---

## Understanding ESF

New to the framework?

- **[Essentials](docs/essentials.md).** The three core practices in under two minutes
- **[What Is ESF?](docs/what-is-esf.md).** How the framework works, where it came from, and why it is tool-agnostic

---

## FAQ

**Do I need Claude Code?** No. ESF Companion works with any AI tool. Claude Code gives you the richest experience (drift detection, session memory, skills). Claude.ai, ChatGPT, and Gemini get the core process via the companion prompt. Claude.ai Projects adds persistent context without the paste workflow.

**Can I use this with existing work?** Yes. Run the installer inside your existing project directory. It adds ESF files without touching your work. See [Using ESF with Existing Work](docs/existing-work.md).

**Does the installer create a new folder?** It asks if you want one. If you say yes, it creates the folder and installs inside it. If you are already in a project directory, it installs there.

**What is the difference between the companion prompts?** Three options in `esf/toolkit/prompts/` after install (or `prompts/` in the GitHub source for Path 1): `quick-start.md` is a single-paste document (fill in your info, paste the whole thing as your first message; fastest to get started). `companion.md` is a fill-in-your-information template for returning users who have already set up their context. `esf-companion.md` is the full system prompt if you want to configure the AI separately from your context.

---

## The Process

```
1. INQUIRE     Understand the problem. Ask yourself what you know, what
               you don't, and what you're assuming. No AI.
       ↓
2. POSITION    Write your Position Statement: your stance, what
               matters most, what you will not compromise on. No AI.
       ↓
3. EXPLORE     Bring AI in to challenge your position. It surfaces
               alternatives, asks questions, pushes on blind spots.
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
├── .claude/                            ← Claude Code configuration
│   ├── agents/esf-companion.md         ← AI companion identity
│   ├── skills/                         ← Onboarding, project workflow, git, verify, update, cognitive
│   └── reference/esf-guide.md          ← Framework reference
├── CLAUDE.md                           ← Ambient activation block
└── esf/
    ├── companion-state.md              ← Your identity and active contexts
    ├── companion-notes.md              ← Corrections the Companion applies every session
    ├── toolkit/                        ← The Companion's own files
    │   ├── prompts/                    ← Paste-anywhere system prompts
    │   ├── templates/                  ← Blank templates for each practice
    │   ├── WORKFLOW.md                 ← Process diagram
    │   └── START_HERE.md               ← First-read overview
    └── [your-context]/
        ├── briefs/                     ← Project briefs
        ├── position-statements/        ← Your direction (write this first)
        ├── records-of-resistance/      ← Your decisions about AI output
        ├── ai-use-logs/                ← What AI contributed
        └── logs/                       ← Session logs
```

---

## Adapting to Your Domain

The templates use generic language. Adapt them:

| Domain | Position Statement becomes | Records of Resistance track |
|--------|---------------------------|----------------------------|
| Writing | "My argument is X, structured as Y" | Rejected phrasings, restructured sections, removed AI framings |
| Design | "My concept is X, constrained by Y" | Rejected compositions, overridden style suggestions, revised layouts |
| Code | "My architecture is X, optimized for Y" | Rejected implementations, rewritten algorithms, overridden patterns |
| Prompt/context engineering | "Design Intent: this AI must do X, must never do Y, optimized for Z" | Rejected model-suggested patterns, pushed-back constraint softening, corrected behavioral drift |
| Research | "My hypothesis is X, grounded in Y" | Rejected interpretations, revised analyses, challenged claims |
| Consulting | "My recommendation is X, based on Y" | Rejected framings, revised conclusions, removed unsupported claims |

### Prompt and Context Engineering

For practitioners building system prompts, context windows, or AI configurations, the Position Statement is a **Design Intent**: what behavior this AI must exhibit, what the hard constraints are, and what would indicate failure.

The five-phase process applies directly:

1. **Inquire.** Define the problem the AI needs to solve. What behavior are you designing for?
2. **Design Intent.** Write your constraints and goals before iterating with the model. This is the gate. The model does not shape your intent before you record it.
3. **Explore.** Test initial approaches against your Design Intent. Surface alternatives. Challenge your assumptions about what the model can do.
4. **Make.** Iterate. Log every moment you pushed back on a model-suggested pattern, softened constraint, or direction you did not choose. These are Design Decisions: the prompt engineering equivalent of Records of Resistance.
5. **Behavioral Audit.** Before shipping: can you explain every constraint? Does the model's behavior match your original Design Intent? Did you consciously choose each element, or did some arrive by suggestion?

The Companion detects prompt engineering projects from context (brief mentions a system prompt, context window, or model configuration) and adjusts its vocabulary accordingly. The mechanism does not change.

---

## Using ESF in any folder or tool

The Companion works in any folder structure, on any AI tool, with no required install. For a full breakdown of what works at each setup level, including how drift detection works without Claude Code and what the onboarding steps require, see [Portability: What Works Where](docs/portability.md).

---

## Adopting ESF for Your Institution

If you teach at a university, college, or training program, see [Adopting ESF for Your Institution](docs/institutional-adoption.md) for a step-by-step customization guide covering agent configuration, project minimums, student distribution, and assessment approaches.

---

## Roadmap

The ESF Companion is actively developed. See [ROADMAP.md](ROADMAP.md) for the full product vision, research foundation (30+ sources), and version plan.

For the complete walkthrough, see [WALKTHROUGH.md](WALKTHROUGH.md).

---

## License

ESF Companion is released under a dual license:

- **Content** (framework, documentation, templates, prompts, examples, sample projects, course materials, skill definitions) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT). You may share and adapt the material for any purpose, including commercial use, as long as you give appropriate credit.
- **Code** (installer scripts, test harness, GitHub Actions, plugin manifests, web assets) is licensed under the [MIT License](LICENSE-CODE).

See [LICENSE](LICENSE) for the full scope of each license and how to determine which applies to a given file. For academic citation, see [CITATION.cff](CITATION.cff).

---

*ESF Companion*
*Nathan Madrid*
*Content: CC BY 4.0  |  Code: MIT*
