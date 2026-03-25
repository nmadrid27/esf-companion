# Adopting ESF for Your Institution

If you teach at a university, college, or training program and want students to use ESF in your courses, the ESF Companion is a starting point you can customize. Fork this repository or fork this repository and make the following changes.

## 1. Add your course context to the agent

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

## 2. Set minimums for Records of Resistance

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

## 3. Add your project briefs

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

## 4. Customize the disclosure protocol

The generic disclosure template has three tiers (short, standard, detailed). For a course, you may want to specify which tier is required and where it goes:

- Add a line to your syllabus: "All AI-assisted work must include a Standard Form disclosure statement."
- Edit `templates/disclosure-statement.md` to include your course-specific fields (course code, project number, submission date).

## 5. Set up student distribution

Two options:

**Option A: Give students the install command.** Point them to your fork:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR-ORG/YOUR-FORK/main/install.sh | bash
```

Update the `TOOLKIT_BASE` URL at the top of `install.sh` to point to your fork.

**Option B: Provide a pre-configured repo template.** Create a GitHub template repository with the toolkit already installed and your course context pre-loaded. Students click "Use this template" and get a ready-to-use project repo.

## 6. Decide what you assess

ESF artifacts are process documentation, not deliverables. Decide which ones count toward grades:

| Artifact | Common approaches |
|----------|-------------------|
| Position Statement | Completion grade (did they write one before AI entry?) |
| Records of Resistance | Minimum count per project; quality assessed by specificity of reasoning |
| AI Use Log | Completion and honesty; compare against visible AI patterns in the work |
| Five Questions | Spot-check at submission; ask students to defend a randomly selected answer |
| Disclosure | Required for submission; accuracy assessed against AI Use Log |

## Example: What a Customized Toolkit Looks Like

The full ESF repository includes a [ESF Companion](https://github.com/nmadrid27/esf-companion) which shows what a fully customized version looks like. It adds:

- Course-specific onboarding (`/esf-onboarding` skill)
- Per-course project folder structure
- Session memory across conversations
- Automated Five Questions checkpoints
- Portfolio accumulation across a multi-course sequence

You do not need all of that. Start with the community toolkit, add your course context and minimums, and expand as needed.

---

*[Back to Community Toolkit](../README.md)*
