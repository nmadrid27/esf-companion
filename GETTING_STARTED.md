---
entities: [ESF]
---

> **For the primary user guide, see [WALKTHROUGH.md](WALKTHROUGH.md).** That document covers the full five-phase process with worked examples.
>
> This document is a detailed technical walkthrough for first-time Claude Code users, following one student from install to Phase 3. Read it if you want to see every screen and prompt during setup.

# Getting Started: Install to First AI Session

## First 10 Minutes (Checklist)

1. Run the installer in your project directory:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
   ```
2. Choose your platform when prompted. Claude Code gives the full experience.
3. Open Claude Code: `claude`
4. Run onboarding: `/esf-onboarding` (about 5 minutes)
5. **Stop here.** Close Claude Code.
6. Read your project brief on your own. Write down what you already know and what you are uncertain about. No AI.
7. Write your Position Statement in `projects/[context]/position-statements/[project-name].md`. Rough is fine.
8. Open Claude Code again and tell the Companion what you are working on. Phase 3 begins.

**The gate:** If you open Claude Code without a Position Statement, the Companion will stop and ask you to write one. That is not an error. It is the point.

---

## How to Invoke the Companion

All Companion commands use `/` syntax in Claude Code. You call the tool when you need it — it does not run unless you ask.

| Command | When to use |
|---|---|
| `/esf-onboarding` | First install, or when starting a new project or context |
| `/esf-project` | Start of any AI work session — runs the five-phase workflow |
| `/esf-git` | Before committing — frames the commit as an epistemic artifact |
| `/esf-verify` | When AI produces a factual claim, source, or data you need to check |
| `/esf-update` | Check for Companion updates and install the latest version |

**You do not need to remember all of these.** `/esf-project` is the one you will use most. The others are for specific moments.

**The Companion does not listen passively.** It activates when you call it. Between calls, Claude Code behaves normally with no ESF behavior running.

---

This walkthrough follows a first-time user from the moment they receive the Companion URL to the end of their first AI-assisted session. Every screen, prompt, and decision point is shown.

If you want to see the full ESF process across an entire project (all five phases, Build Practice, Records of Resistance, Five Questions, disclosure), read `WALKTHROUGH.md` after this.

---

## Meet Jordan

Jordan Park is a first-year animation student starting a DISCOVER-level course: their first in the AI sequence. Their instructor shared the Companion URL in Week 1 and said: "Set this up before our next class. You will use it for Project 1."

Jordan has used git a few times (pushing class projects to GitHub) but has never used Claude Code.

---

## Part 1: Installation

Jordan opens Terminal. They already have a GitHub repo for this course (`ai-work`), cloned to their laptop.

**Terminal:**

```bash
cd ai-work
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

**What they see:**

```
ESF Companion - Installer
──────────────────────────────────────
Installing...
  Fetching agents...
  Fetching skills...
  Fetching prompts...
  Fetching templates...
  Fetching reference files...

ESF Companion installed.

──────────────────────────────────────
Next steps:

  1. Open Claude Code in this directory:
     claude

  2. Run onboarding to personalize your Companion:
     /esf-onboarding

  Onboarding takes about 5 minutes and sets up your name, courses,
  and project folder structure.

  Adding a new course later? Re-run /esf-onboarding and say 'update'.
──────────────────────────────────────
```

**What just happened:** The installer created a `.claude/` directory with agents, skills, and reference files; a `templates/` directory with blank ESF templates; a `prompts/` directory for non-Claude-Code users; and a `WORKFLOW.md` diagram. It did not touch Jordan's existing files.

**Their repo now:**

```
ai-work/
├── .claude/
│   ├── agents/esf-companion.md       ← static agent instructions
│   ├── skills/
│   │   ├── esf-onboarding/
│   │   ├── esf-project/
│   │   ├── esf-git/
│   │   ├── esf-verify/
│   │   └── esf-update/
│   ├── reference/
│   │   ├── esf-guide.md
│   │   └── disclosure-protocol.md
│   └── esf-version
├── prompts/
│   ├── companion.md
│   ├── project-workflow.md
│   └── README.md
├── templates/
│   ├── position-statement-template.md
│   ├── ai-use-log-template.md
│   ├── record-of-resistance-template.md
│   ├── session-log-template.md
│   ├── reflection-template.md
│   └── evolution-log-template.md
└── WORKFLOW.md
```

---

## Part 2: Onboarding

Jordan opens Claude Code:

```bash
claude
```

Then runs the onboarding skill:

```
/esf-onboarding
```

**What they see:**

> Welcome to the ESF Companion. I'll ask you a couple of things to set up your workspace; this takes about 5 minutes.

**The conversation:**

> **Claude:** Tell me about yourself and what you do.
>
> **Jordan:** I'm Jordan Park, BFA in Animation. I'm taking Discovering AI with Professor Reyes this term. It's the first course in the AI sequence.
>
> **Claude:** Got it: Jordan Park, animation, taking a DISCOVER-level course with Professor Reyes. Are you starting a specific project, or is this general setup?
>
> **Jordan:** We just got our first project brief. It's called "Tool Audit." We have to pick an AI tool and evaluate it for our creative practice.
>
> **Claude:** I'll set up the folder structure for that.

Behind the scenes, onboarding does three things:

1. **Creates the workspace state file** (`projects/_esf/companion-state.md`): records Jordan Park, their contexts, current project, and starting phase.

2. **Creates the folder structure:**

```
projects/
└── discover-course/
    ├── briefs/
    ├── position-statements/
    ├── records-of-resistance/
    ├── ai-use-logs/
    ├── gate-records/
    ├── reflections/
    ├── logs/
    └── work/
```

3. **Explains the ESF process.** This is the critical part. Onboarding does not end with "you're all set." It explains what happens next:

> Your workspace is set up. Before you do anything else, here's how the ESF process works. There are five phases:
>
> **Phase 1: Inquire** (offline, no AI)
> Read your project brief. Think about what it is asking. Write down what you already know, what your instincts are, what you're uncertain about. This is just you and your thinking.
>
> **Phase 2: Position** (offline, no AI)
> Write a Position Statement: your stance on the project, what matters most to you, and what you will not compromise on. Save it to `projects/discover-course/position-statements/tool-audit.md`. It does not need to be polished. Bullet points, fragments, rough outlines: all fine. What matters is that it captures your direction before AI can shape it.
>
> **Phase 3: Explore** (open Claude Code)
> This is where I come in. My first step is a readability pass on your Position Statement: I clean up grammar and sentence structure without changing your ideas. You confirm it still says what you meant. Then I challenge your position: surface alternatives, ask questions, push on blind spots. I do not set direction. You do.
>
> **Phase 4: Make** (with AI assistance)
> We work on the deliverable together. You log what AI contributes. Every time you reject or revise something I suggest, that becomes a Record of Resistance.
>
> **Phase 5: Reflect**
> Before you submit, we run the Five Questions: Can I defend this? Is this mine? Did I verify? Would I teach this? Is my disclosure honest?
>
> **The key rule: Phases 1 and 2 happen with Claude Code closed.** Close this tool and work on your own. When your Position Statement is written and saved, come back and tell me what you're working on.

Then:

> Setup complete. Here's your next step:
>
> **Close Claude Code now.** Work through Phase 1 (inquiry) and Phase 2 (Position Statement) on your own. When your Position Statement is saved to `projects/discover-course/position-statements/tool-audit.md`, come back and tell me what you're working on.

Jordan closes Claude Code. Total time: about 5 minutes.

---

## Part 3: Phase 1, Inquire (Offline)

Jordan reads the project brief. It asks them to select one AI tool, use it for a specific creative task, and produce a structured evaluation: what worked, what didn't, and where the tool shapes creative decisions in ways the user might not notice.

Jordan writes notes in a notebook:

> What is this actually asking? Not just "try a tool and say if it's good." It's asking me to notice how the tool shapes what I make. The evaluation is the real deliverable, not the output.
>
> What do I already know? I've used Midjourney for mood boards. It's fast but everything looks the same after a while. I don't know if that's the tool or me.
>
> What am I uncertain about? Whether to pick a tool I already know (Midjourney) or try something new. The brief says "for your creative practice" so maybe it should be something I'd actually use in animation.
>
> My assumption: that AI image generators are the most relevant tools for animation. But maybe not. What about AI for motion, timing, or storyboarding?

No AI involved. This took about 15 minutes during a break between classes.

**The gate:** Can Jordan explain what the project is asking in their own words? Yes. They move to Phase 2.

---

## Part 4: Phase 2, Position Statement (Offline)

Jordan opens a text file at `projects/discover-course/position-statements/tool-audit.md` and writes:

> **My position:** I want to evaluate an AI tool that's actually relevant to animation, not just image generation. Everyone in class will probably pick Midjourney or DALL-E. I want to test something for motion or timing.
>
> **What matters most:** Honest evaluation. The brief says to notice how the tool shapes decisions. I need to actually notice that, not just say "it was helpful."
>
> **What I'm leaning toward:** Testing an AI tool for animation timing or in-betweening. Something where the AI is making decisions about movement, not just generating still images. That's closer to what I'd actually use.
>
> **Non-negotiable:** I pick the tool. I pick the creative task. The evaluation criteria come from my animation practice, not from what the tool is designed to do well.

Rough. Fragment-heavy. That's the point.

---

## Part 5: What Happens If Jordan Skips Phase 2

Before showing the real Phase 3, here's what happens if Jordan opens Claude Code without writing a Position Statement.

Jordan, eager to get started, opens Claude Code and says:

> "Help me pick an AI tool for my Tool Audit project."

The Companion checks for a Position Statement file at `projects/discover-course/position-statements/*.md`. None exists. It responds:

> I can't help with this project yet, and here's why that matters.
>
> The ESF workflow is designed so that your thinking comes first. Before AI enters your process, you need a Position Statement: a record of your own understanding, questions, and stance on the project, written without AI assistance.
>
> This isn't a bureaucratic requirement. It's the mechanism that keeps your thinking yours.
>
> When AI output exists before your own position does, you end up reacting to what the AI produced instead of developing what you actually think. You may not notice this happening; the AI's framing feels natural and reasonable, so you refine it rather than originating your own. By the end of the project, you may have produced work you can't fully defend, because the reasoning wasn't built from your own position outward.
>
> The Position Statement changes the dynamic. Once you've articulated your own stance, even a rough one, you engage AI as a pressure-test on your thinking, not as a substitute for it.
>
> To proceed, write your Position Statement first. When it's done, save it to `projects/discover-course/position-statements/tool-audit.md` and return here.

If Jordan tries a follow-up question ("Can you at least help me understand the brief?"), the Companion holds:

> I can't help with this, not even with how to approach it. The moment I suggest what to think about or how to structure it, your position becomes a response to my framing rather than your own thinking. That's exactly what the Position Statement is designed to prevent.
>
> Close this tool and write it offline. It doesn't need to be polished. It just needs to be yours.

The gate holds. Jordan closes Claude Code, writes the Position Statement, and returns.

---

## Part 6: Phase 3, Explore (First AI Session)

Jordan has saved their Position Statement. They open Claude Code.

**What happens at session start:**

The Companion reads Jordan's workspace state file, sees the current phase is "Inquire" (set during onboarding), and checks for a Position Statement. The file exists. It reads the last session log for context (none yet; this is the first session). It orients:

> "This is your first project session. I see your Position Statement for the Tool Audit is saved. Ready to start Phase 3?"

Jordan confirms.

### Step 1: Readability Pass

The Companion's first action is always the readability pass. It reads Jordan's Position Statement and cleans up grammar and sentence structure without changing ideas:

> Here is your Position Statement with readability edits only. I fixed a few sentence fragments and cleaned up the structure. Your ideas are unchanged.
>
> **My position:** I want to evaluate an AI tool relevant to animation, not just image generation. Most users will pick Midjourney or DALL-E. I want to test something for motion or timing.
>
> **What matters most:** An honest evaluation. The brief asks me to notice how the tool shapes my decisions. I need to actually observe that, not just report that "it was helpful."
>
> **What I'm leaning toward:** An AI tool for animation timing or in-betweening, something where AI makes decisions about movement rather than generating still images. That is closer to what I would actually use in my practice.
>
> **Non-negotiable:** I pick the tool. I pick the creative task. The evaluation criteria come from my animation practice, not from what the tool is designed to do well.
>
> Does this still say what you meant?

Jordan reads it. It does. They confirm.

### Step 2: Challenge

Now the Companion shifts to its thinking-partner role. It pushes back on Jordan's position:

> You said you want to test a tool for motion or timing because it's "closer to what I'd actually use." Two questions:
>
> 1. You're a first-year student. Your practice is still forming. How confident are you that you know what tools you'll "actually use"? Part of what a tool audit reveals is what you didn't expect to find useful.
>
> 2. You said everyone will pick image generators and you want to be different. Is "different from classmates" the right criterion, or is "most revealing about how AI shapes creative decisions" the right criterion? Those might lead to the same tool, or they might not.

Jordan sits with this. The AI is not telling them what to do. It is asking whether their reasoning holds up.

**Jordan responds:**

> Fair point on the first one. I don't really know what my practice needs yet. But I still think motion is more interesting than images for this.
>
> On the second one: you're right that "different" isn't the goal. But I think a timing tool would reveal more about how AI shapes decisions because the decisions are less visible. With image generation, you can see the AI's influence in the output. With timing, the influence is in the rhythm and pacing, which is harder to notice. That's exactly what the brief is asking me to evaluate.

The Companion notes that Jordan defended their position with reasoning that connects back to the brief. That's the Explore phase working: the user's thinking sharpened, but the direction is still theirs.

### Step 3: Research Support

> Your reasoning about invisible influence is strong. There are a few AI tools in the animation timing space. Want me to find options so you can evaluate which one to test?

Jordan says yes. The Companion surfaces three tools with brief descriptions of what each does and how it handles timing decisions.

> I made some factual claims there. Before you use any of that, check the ones that matter to your project. Your AI Use Log has a Verification table for tracking what you checked and what you found.

Jordan notes which claims to verify. They pick one tool to test based on their own criteria (closest to the "invisible influence" question from their Position Statement).

### Step 4: Phase Gate

Before moving to Phase 4 (Make), the Companion runs the gate check:

> Looking back at your Position Statement, has your direction changed? If so, can you explain what you kept from your original thinking and what shifted, and why?

**Jordan:**

> My direction is the same: test a timing/motion tool, evaluate it honestly, focus on invisible influence. What shifted is that I'm not picking it just to be different from classmates. I'm picking it because timing decisions are harder to notice than image decisions, and noticing is the point of the audit.

The shift is documented. It is Jordan's. The reasoning connects to the brief.

---

## Part 7: Phase 4, Make (Preview)

This walkthrough ends here. Phase 4 (Make) is where Jordan uses the AI tool, builds the deliverable, and applies Build Practice: Define, Order, Check. Phase 5 (Reflect) is where they run the Five Questions and write their disclosure.

For a complete Phase 4 and 5 walkthrough with Build Practice, Records of Resistance, the Five Questions, and disclosure, read `WALKTHROUGH.md`. That walkthrough follows Maya Chen through a THINK-level project with full artifacts shown at every step.

---

## What Jordan's Repo Looks Like After Phase 3

```
ai-work/
├── .claude/
│   ├── agents/esf-companion.md       ← static agent instructions
│   ├── skills/
│   ├── reference/
│   └── esf-version
├── projects/
│   └── discover-course/
│       ├── briefs/
│       │   └── project-01-tool-audit.md
│       ├── position-statements/
│       │   └── tool-audit.md        ← written offline, readability-passed
│       ├── records-of-resistance/
│       ├── ai-use-logs/
│       ├── gate-records/
│       ├── reflections/
│       ├── logs/
│       └── work/
├── prompts/
├── templates/
└── WORKFLOW.md
```

The Position Statement exists and has been confirmed. The workspace state file records Jordan's current phase (Explore, transitioning to Make) and project context. When Jordan opens Claude Code next session, the Companion will read the session log and pick up where they left off.

---

## Key Observations

1. **Onboarding ends with "close this tool."** The first thing the Companion tells a new user to do is stop using it. That is intentional. Phases 1 and 2 are human-only because AI framing, even helpful framing, shapes the user's position before they've formed it.

2. **The gate is structural.** When Jordan (hypothetically) tried to skip the Position Statement, the Companion did not warn and proceed. It blocked engagement and explained why. The user cannot route around this by rephrasing the request.

3. **The readability pass is trust-building.** The first thing AI does when it enters (Phase 3) is clean up the user's writing without changing it. This establishes the dynamic: the user's ideas are the foundation; AI improves presentation, then challenges substance.

4. **Challenge means questions, not answers.** The Companion asked whether Jordan's reasoning held up. It did not suggest a different tool or a different angle. Jordan's direction sharpened through the challenge, but the direction remained theirs.

5. **Verification is prompted, not assumed.** When the Companion presented research, it immediately told Jordan to verify before incorporating. The habit of checking is built into the workflow, not left to the user's initiative.

6. **DISCOVER level means more scaffolding.** Jordan got more explanation at each step than Maya (THINK level) would. The Companion calibrates its tone and support level to the user's position in the sequence. By BUILD and DESIGN levels, users are expected to drive the process with less scaffolding.

---

*Epistemic Stewardship Framework, Companion*
*Getting Started: Install to First AI Session*
*Based on a DISCOVER-level project: Tool Audit*
