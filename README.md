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
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-community-toolkit/main/install.sh | bash
```

The script creates a directory, initializes git, drops in the templates, and gives you a clean starting point.

### Use with Claude Code

The installer also sets up a `.claude/` configuration that teaches Claude Code the ESF process. When you start a session, Claude checks for a Position Statement before assisting with project work.

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

If you teach at a university, college, or training program and want students to use ESF in your courses, the community toolkit is a starting point you can customize. Fork this repository or copy the `community-toolkit/` directory and make the following changes.

### 1. Add your course context to the agent

Edit `.claude/agents/esf-companion.md` to include your course information. Add a section after the Identity block:

```markdown
## Course Context

- **Institution:** [Your institution name]
- **Course:** [Course code and title]
- **Instructor:** [Your name]
- **AI Policy:** [Your course's AI use policy, or link to it]

## Project Structure

Students in this course complete the following projects:
- **Project 1:** [Title and brief description]
- **Project 2:** [Title and brief description]

Each project requires a Position Statement before AI engagement
and a minimum of [N] Records of Resistance.
```

This gives Claude Code (or any AI tool using the companion prompt) the context to guide students within your specific course structure.

### 2. Set minimums for Records of Resistance

The generic templates leave minimums open. For a course, you should set them. Edit the agent file and the companion prompt to enforce your requirements:

```markdown
## ESF Requirements for This Course

| Project | Position Statement | Records of Resistance (minimum) | AI Use Log |
|---------|--------------------|---------------------------------|------------|
| P1      | Required           | 1                               | Required   |
| P2      | Required           | 3                               | Required   |
| Final   | Required           | 5                               | Required   |
```

Scale minimums to project complexity. A short exercise needs fewer Records of Resistance than a capstone project.

### 3. Add your project briefs

Drop your assignment briefs into a `briefs/` directory. Reference them in the agent so the AI has context when students ask about project requirements:

```
your-course-toolkit/
├── briefs/
│   ├── project-1-brief.md
│   └── project-2-brief.md
├── templates/
│   └── [ESF templates, unchanged or adapted]
└── .claude/
    └── agents/
        └── esf-companion.md   ← References your briefs
```

In the agent file, add:

```markdown
## Project Briefs

Read the brief in `briefs/` for the student's current project before assisting.
Use the brief to check whether the student's Position Statement addresses
the assignment's requirements.
```

### 4. Customize the disclosure protocol

The generic disclosure template has three tiers (short, standard, detailed). For a course, you may want to specify which tier is required and where it goes:

- Add a line to your syllabus: "All AI-assisted work must include a Standard Form disclosure statement."
- Edit `templates/disclosure-statement.md` to include your course-specific fields (course code, project number, submission date).

### 5. Set up student distribution

Two options:

**Option A: Give students the install command.** Point them to your fork:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR-ORG/YOUR-FORK/main/community-toolkit/install.sh | bash
```

Update the `TOOLKIT_BASE` URL at the top of `install.sh` to point to your fork.

**Option B: Provide a pre-configured repo template.** Create a GitHub template repository with the toolkit already installed and your course context pre-loaded. Students click "Use this template" and get a ready-to-use project repo.

### 6. Decide what you assess

ESF artifacts are process documentation, not deliverables. Decide which ones count toward grades:

| Artifact | Common approaches |
|----------|-------------------|
| Position Statement | Completion grade (did they write one before AI entry?) |
| Records of Resistance | Minimum count per project; quality assessed by specificity of reasoning |
| AI Use Log | Completion and honesty; compare against visible AI patterns in the work |
| Five Questions | Spot-check at submission; ask students to defend a randomly selected answer |
| Disclosure | Required for submission; accuracy assessed against AI Use Log |

### Example: What a Customized Toolkit Looks Like

The full ESF repository includes a [student toolkit](https://github.com/nmadrid27/Epistemic-Stewardship-Framework-ESF-/tree/main/student-toolkit) and [faculty toolkit](https://github.com/nmadrid27/Epistemic-Stewardship-Framework-ESF-/tree/main/faculty-toolkit) that show what a fully customized institutional version looks like. They add:

- Course-specific onboarding (`/esf-onboarding` skill)
- Per-course project folder structure
- Session memory across conversations
- Automated Five Questions checkpoints
- Portfolio accumulation across a multi-course sequence

You do not need all of that. Start with the community toolkit, add your course context and minimums, and expand as needed.

---

## Relationship to the Full ESF

This community toolkit is a simplified, portable version of the [Epistemic Stewardship Framework](https://github.com/nmadrid27/Epistemic-Stewardship-Framework-ESF-). For the ideas behind the toolkit, read [What Is ESF?](docs/what-is-esf.md). The full ESF repository adds:

- A two-level architecture (faculty content production and student epistemic development)
- Detailed implementation guides for academic institutions
- Curriculum integration patterns
- Complete scholarly grounding and literature review (35 sources)
- Faculty and student toolkits with onboarding agents

If you work in higher education, the full framework and its academic toolkits may be a better fit. This community toolkit is for everyone else, or for academics who want the practices without the institutional scaffolding.

---

*Epistemic Stewardship Framework — Community Edition*
*Nathan Madrid*
*Licensed under CC BY 4.0*
