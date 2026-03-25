# ESF Community Toolkit

A lightweight, domain-agnostic version of the Epistemic Stewardship Framework for anyone who works with AI and wants to stay in control of the result.

No institution, course, or program required. If you use AI to write, research, design, code, or create, this toolkit gives you a repeatable process for keeping the work genuinely yours.

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

Pick the path that fits you best. They all get you to the same place.

### Download and use the templates (no install needed)

The simplest way to start. No terminal, no coding, no special tools.

1. Click the green **Code** button at the top of this page, then **Download ZIP**
2. Unzip the folder and open `templates/`
3. Copy `position-statement.md` into your project folder and fill it in before opening any AI tool

That is all you need to get started. See the **[Getting Started guide](docs/getting-started.md)** for a full step-by-step walkthrough.

```
templates/
├── position-statement.md      ← Fill out before each AI session
├── record-of-resistance.md    ← One per decision to reject/revise AI output
├── ai-use-log.md              ← One per project or document
├── five-questions-checklist.md ← Run at each review point
└── disclosure-statement.md    ← Add to finished deliverables
```

### Use with any AI tool (ChatGPT, Gemini, Claude, etc.)

Open `prompts/esf-companion.md`, copy the contents, and paste it at the start of a new conversation with your AI tool. It works with ChatGPT, Gemini, Claude.ai, or any tool that accepts text input. The AI will follow the ESF process and ask for your Position Statement before helping with project work.

### Use with Claude Cowork (no terminal needed)

If you use the Claude desktop app, [Cowork](https://claude.com/product/cowork) can work directly with the ESF templates on your computer — no terminal required.

1. Download and unzip the toolkit (see above)
2. Open Claude Desktop and start a Cowork session
3. Point Claude to your toolkit folder — it can read your local files directly, including the companion prompt and all templates

That is it. Claude will read the ESF companion prompt on its own, check for your Position Statement, and guide you through the full workflow — exploring, building, logging AI contributions, and recording moments of resistance. No copying or pasting required.

Available on Pro, Max, Team, and Enterprise plans.

### Use the installer (for terminal users)

If you are comfortable with the command line and want a ready-made project structure with git:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

The script creates a directory, initializes git, drops in the templates, and gives you a clean starting point.

### Use with Claude Code

The installer also sets up a `.claude/` configuration that teaches Claude Code the ESF process. When you start a session, Claude checks for a Position Statement before assisting with project work.


**Already mid-project?** If you have existing work and want ESF to work with it instead of starting fresh, see [Using ESF with Existing Work](docs/existing-work.md).
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

## Relationship to the Full ESF

This community toolkit is a simplified, portable version of the [Epistemic Stewardship Framework](https://github.com/nmadrid27/esf-companion). For the ideas behind the toolkit, read [What Is ESF?](docs/what-is-esf.md). The full ESF repository adds:

- A two-level architecture (faculty content production and user epistemic development)
- Detailed implementation guides for academic institutions
- Curriculum integration patterns
- Complete scholarly grounding and literature review (35 sources)
- Onboarding agents and project workflow skills

If you work in higher education, the full framework and its academic toolkits may be a better fit. This community toolkit is for everyone else, or for academics who want the practices without the institutional scaffolding.

---

*Epistemic Stewardship Framework — Community Edition*
*Nathan Madrid*
*Licensed under CC BY 4.0*
