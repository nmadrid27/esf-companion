# ESF Companion: Walkthrough

A process reference and 10-minute worked example. For first steps after installing, see [START_HERE.md](START_HERE.md).

---

## What Is This?

The ESF Companion is a thinking partner for anyone who works with AI. It does one thing: keeps your creative direction yours while AI extends what you can do.

You write a Position Statement before AI enters your work. The Companion watches for drift between what you said and where the work is heading. When it sees a gap, it asks you about it. You decide what to do. The Companion never decides for you.

**Who it is for:** Students, professionals, educators, independent creators. Anyone using AI for creative or intellectual work who wants to stay the author.

**What it is not:** It is not a usage monitor. It is not grading software. It does not restrict how you use AI. It makes your AI use intentional rather than habitual.

---

## Install

One command:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

The installer asks what AI tool you use (Claude Code, ChatGPT, or other) and sets up accordingly.

**What got installed:**
- An agent that knows the ESF process (`.claude/agents/esf-companion.md`)
- Skills for onboarding, project workflow, and verification (`.claude/skills/`)
- Templates for Position Statements, Records of Resistance, and AI Use Logs (`templates/`)
- A visual process diagram (`WORKFLOW.md`)

You are ready. Open your AI tool and run `/esf-onboarding` to set up your profile.

---

## Your First Project (10-minute walkthrough)

This walks you through the full process using a simple example.

### Step 1: Tell the Companion what you are working on

Open Claude Code in your repo directory and say:

> "I want to redesign my portfolio website using AI tools."

The Companion creates a project folder and asks a few questions: what are the deliverables, when is it due, what are the AI boundaries? If you have a project brief from an instructor, drop it into `projects/portfolio-redesign/briefs/` instead.

### Step 2: Write your Position Statement

The Companion asks you three questions:

1. **What are you making?** "A portfolio site that reflects my design practice, not a template."
2. **What matters most?** "The visual identity has to feel handcrafted. The site should look like me, not like every other AI-generated portfolio."
3. **What will you not compromise?** "AI will not choose my typography or color palette. Those are mine."

The Companion structures your answers into a Position Statement and reads it back: "Does this sound like you? Change anything that does not match what you meant."

You confirm. This is now your anchor. Everything the Companion does from here references it.

### Step 3: Start working with AI

Ask the Companion for help:

> "I need layout ideas for my project page. Each project has a hero image, a description, and process shots."

The Companion helps: suggests approaches, generates alternatives, answers questions. Normal AI assistance.

### Step 4: See drift detection

After a few exchanges, suppose the Companion notices something:

> "Your Position Statement says the site should feel handcrafted. The layout we have been developing uses a grid system that looks like a standard template. Is that intentional, or did we drift?"

You have three choices:
- **Correct the drift:** "You are right. Let me rethink the grid."
- **Update your position:** "Actually, I have decided a clean grid IS part of my aesthetic. Let me update my Position Statement."
- **Continue deliberately:** "I know it looks templated right now. I am adding hand-drawn elements in the next pass."

All three are valid. The point is you made the decision consciously.

### Step 5: Capture a Record of Resistance

The Companion suggests a color palette. You reject it:

> "No, those colors are too safe. My work is bolder than that."

The Companion prompts:

> "That is a Record of Resistance. Want to capture it? Three things: what AI produced, why you rejected it, what you did instead."

You say: "AI suggested muted pastels. I rejected them because my brand is high-contrast and saturated. I chose my existing palette: black, white, and electric blue."

The Companion saves it. This documents your editorial judgment.

### Step 6: End the session

The Companion generates an AI Use Log draft:

> "Here is what happened this session. What you asked, what you kept, what you revised, what you rejected. Review it and confirm."

You review, make a small correction, confirm. The Companion saves the log and updates your PROJECT.md:

```
# Project: Portfolio Redesign
Phase: Make
Position: Handcrafted portfolio site. Typography and color are mine.
RoR: 1 of 0 minimum documented
Last session: 2026-03-24. Layout exploration. Rejected AI color palette.
Next: Add hand-drawn elements to grid. Start project page template.
```

Next time you open the Companion, it picks up right here.

---

## The Full Process

Five phases. The first two happen offline (without AI). The last three happen with the Companion.

### Phase 1: Inquire (offline, no AI)

Read your project brief or define your project. Ask yourself: what do I already know? What are my instincts? What am I uncertain about? Write this down in whatever form works for you.

### Phase 2: Position (offline, no AI)

Write your Position Statement. Three elements:
- **Your stance:** What are you making? What is your creative direction?
- **What matters most:** What qualities are non-negotiable?
- **What you will not compromise:** The line AI will not cross.

Save it to `projects/[name]/position-statements/`. It does not need to be polished. Rough is fine.

If you prefer to talk through your ideas rather than write, the Companion can help you articulate your position through conversation when you open Phase 3. You answer questions in your own words; the Companion structures them.

### Phase 3: Explore (with AI)

Open the Companion. It does a readability pass on your Position Statement (same ideas, clearer sentences). Then it challenges your thinking: surfaces alternatives, asks questions, pushes on blind spots. You direct. AI responds.

### Phase 4: Make (with AI)

Build the deliverable with the Companion's help. The Companion monitors for drift against your Position Statement. When you reject AI output, document it as a Record of Resistance. The Companion tracks your count against any minimum your brief requires.

### Phase 5: Reflect

Before submitting, the Companion walks you through the Five Questions:

1. **Can I defend this?** Can I explain every part of this work?
2. **Is this mine?** Does this reflect my thinking, or did I follow AI's direction?
3. **Did I verify?** Have I checked the parts that matter?
4. **Would I teach this?** Do I understand it well enough to explain it?
5. **Is my disclosure honest?** Does my documentation accurately describe what I did and what AI did?

The Companion generates a Disclosure Statement from your session logs and Records of Resistance. You review and own it.

---

## For Different Users

### If you have an instructor brief

Drop the `.md` file into `projects/[context]/briefs/`. The Companion reads it and extracts: deliverables, AI use policy, Records of Resistance minimum, Five Questions requirement, and timeline. If your instructor set these to "required," the Companion enforces them as hard gates.

### If you are working on a personal project

Describe your project to the Companion or write your own brief. You control the ESF level: set `position-statement: required` if you want accountability, or `optional` if you want lighter guidance. The minimum viable brief is a name and a description.

### If you are an educator

Tell the Companion you want to create a brief for your students. It walks you through the fields: deliverables, AI policy, ESF requirements. It generates a `.md` file with frontmatter your students' Companions can read. Distribute it however you normally share assignments.

### If you are using ChatGPT or another conversation tool

The core process is the same. The difference: context does not persist between conversations. At the end of each session, the Companion generates a PROJECT.md summary. Save it. Paste it at the start of your next conversation. This takes 30 seconds and keeps drift detection working across sessions.

Without it, the Companion starts fresh and cannot compare your work to your original direction.

---

## Common Situations

**"I want to start a second project."**
Tell the Companion. It creates a new project folder. Each project has its own Position Statement and context. At the start of each session, the Companion asks which project you are working on.

**"My Position Statement is wrong. I need to change direction."**
Tell the Companion. It saves your current statement as v1 and helps you write a new one. The pivot is documented with your reasoning. Position Statement evolution is a feature, not a failure.

**"I want less interruption today."**
Say "less interruption today." The Companion scales back to essential drift flags only. No proactive check-ins, no friction questions. Just the baseline monitoring.

**"I am stuck."**
Tell the Companion. It offers a cognitive technique to help you break out of fixation: lateral thinking (approach the problem from an unrelated angle), perspective shift (describe the project as if explaining it to someone in a different field), constraint manipulation (add or remove a constraint and see what opens up), or analogical reasoning (find a parallel problem in a different domain and examine how it was solved). You choose whether to try one.

**"I finished my project."**
The Companion runs a close-out: it generates the final Disclosure Statement and updates your Growth Record with what you developed this project. Your next project starts fresh with a new Position Statement.

**"I want to use this after I graduate."**
Write your own briefs. The Companion works the same way with self-authored briefs as with instructor briefs. Set your own ESF level. The tool becomes a lifelong practice, not a course requirement.

---

For quick setup after install, see [START_HERE.md](START_HERE.md).
For filled examples of Position Statements, Records of Resistance, and Disclosures, see [examples/](examples/).

---

## How It Works

The ESF Companion is built on research from cognitive science, education, and AI ethics.

**Extended mind theory** (Clark & Chalmers, 1998): Your thinking can genuinely extend into tools, including AI, but only when you actively direct the tool's contributions. Passive acceptance is not extension; it is surrender. The Position Statement is how you actively direct.

**Metacognitive demands** (Tankelevitch et al., 2024): AI output is fluent and polished, which makes it harder to evaluate critically. Your brain treats smooth output as trustworthy. The Companion counteracts this by flagging fluent output that you have not examined.

**Cognitive friction** (Vendrell & Johnston, 2026): The productive struggle of working through problems is what builds understanding. AI bypasses that struggle. The Companion reintroduces friction deliberately: challenging your direction, surfacing what is missing, questioning whether the work is still yours.

**The core insight:** AI is not the problem. Unexamined AI use is the problem. The Companion makes your AI use examined.

For the full research foundation and product roadmap, see [ROADMAP.md](ROADMAP.md).
