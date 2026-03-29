# ESF Companion Roadmap

What is built, what is coming next, and what is planned for later.

---

## What Is Shipped (v1 — current)

The full Claude Code experience: five-phase workflow, drift detection, Position Statement gate, Records of Resistance, AI Use Log, Disclosure Statement, session memory, cognitive techniques, progress indicator, auto-update on session start. Universal onboarding with educator path. Brief-driven guidance with frontmatter field control. Conversation-platform prompts for ChatGPT, Gemini, and other tools.

## What Is Shipped (v2)

Multi-platform support: install with a `--platform` flag targeting Claude Code, Claude.ai, ChatGPT, Gemini, or Codex CLI. Platform-specific config files included: `chatgpt-instructions.md`, `GEMINI.md`, `.codex/AGENTS.md`.

Platform migration: migrate/fresh/cancel options when switching platforms. Portable PROJECT.md generated for conversation-platform users.

Accessibility additions: checkpoint saves for mid-session pauses, thread tracking for concurrent project aspects, structured alternatives to open-ended Socratic questions.

Growth Record with development tracking across projects (companion-state.md Growth Record section, populated at project completion).

Educator course configs: `courses/` folder documented for optional course-level ESF requirement templates.

## What Is Shipped (v3)

Framework Evolution Protocol: users can propose revisions to the ESF process, document deliberate deviations, and build a personal version of ESF. Evolutions are recorded in `projects/_esf/evolution-log.md` and applied going forward. See `.claude/reference/evolution-protocol.md`.

Cohort homogenization detection: opt-in educator tool that analyzes a cohort's Position Statements for shared vocabulary, direction overlap, and concept space gaps. See `docs/cohort-analysis.md`.

## What Is Planned (still coming)

A local visual dashboard: a browser-based interface that renders your project cards, phase progress, cross-project themes, and growth arc from the same local files the CLI Companion writes. No new app. The CLI remains the primary surface; the dashboard makes your accumulated work visible at a glance.

Full conversation-platform context restoration (PROJECT.md auto-generation and paste-back workflow for initial session setup, not just session end).

---

*For the full product requirements document (research mapping, implementation spec, success metrics, version history), see below.*

---

# ESF Companion: Product Requirements Document

**Product name:** ESF Companion
**One-line description:** An extended thinking partner that helps you direct AI from a position you can defend.
**Date:** 2026-03-24
**Author:** Nathan Madrid, with Claude (AI collaboration)
**Status:** Draft, pending review

---

## Table of Contents

1. Product Overview
2. Core Loop
3. Scaffolding Modes
4. Cognitive Techniques Engine [SHIPPED]
5. Architecture
6. Brief-Driven Guidance
7. Universal Onboarding
8. Memory Architecture
9. Operational Mechanics
10. Position Statement Mechanism
11. Cognitive Friction [SHIPPED]
12. Boundaries and Accessibility
13. Research Foundation
14. Success Metrics
15. Version Roadmap

Status tags: **[SHIPPED]** fully implemented. **[PARTIAL]** partially implemented. **[ROADMAP]** future work.

Items marked [v3] are roadmap features outside current scope.

---

## 1. Product Overview [SHIPPED]

### Core Problem

AI collaboration creates two risks most users cannot detect on their own: cognitive fixation (locking onto AI outputs as defaults) and cognitive drift (gradually surrendering creative direction without noticing). Current tools treat AI as a productivity problem. ESF Companion treats it as a thinking problem.

### Core Mechanism

The user writes a Position Statement before AI enters the work. The tool calibrates scaffolding from that statement. During work, the tool monitors for drift between what the user stated and what the work is becoming. When drift is detected, the tool makes it visible and offers cognitive techniques to help the user re-engage. The user always decides whether to correct the drift or continue deliberately.

### Who It's For

Anyone who uses AI for creative or intellectual work and wants to remain the author of their own thinking. Students, faculty, professionals, independent creators. The tool adapts to the user; the user does not adapt to the tool.

### What It Replaces

Three separate toolkits (student, faculty, community) consolidated into one install, one agent, one workflow.

### Research Foundation (summary)

Grounded in Tankelevitch et al. (2024, CHI Best Paper) on metacognitive demands, Vendrell & Johnston (2026) on scaffolding critical thinking with AI, Clark & Chalmers (1998) on extended mind theory, Wu et al. (2025) on the replacement risk, and Xu et al. (2025) on metacognitive scaffolding. Full research mapping in Section 13.

---

## 2. Core Loop

One loop. Every user, every project, every session.

**Position → Work → Monitor → Surface → Decide** [SHIPPED]

1. **Position.** Before AI enters, the user writes their stance: what they are making, what matters most, what they will not compromise. This is the anchor.

2. **Work.** The user works with AI. The Companion supports the work: answering questions, generating alternatives, challenging assumptions. It is a thinking partner, not a gatekeeper.

3. **Monitor.** The Companion watches for two kinds of drift:
   - **Direction drift:** the work is moving away from the stated position.
   - **Agency drift:** the user is accepting AI output without evaluation.

4. **Surface.** When drift is detected, the Companion makes it visible. Always Socratic, never prescriptive: "Your Position Statement says X. The work is heading toward Y. Is that intentional?"
   - **Mirror mode (default):** surfaces drift, user decides. No gates. [SHIPPED]
   - **Gate mode (educator-activated via brief frontmatter):** surfaces drift and enforces hard stops at Five Questions. If the student cannot answer, the Companion redirects to the Position Statement. [SHIPPED]

5. **Decide.** The user chooses: correct the drift, update the position (deliberate pivot), or continue (acknowledged deviation). All three are valid. The point is the decision is conscious.

---

## 3. Scaffolding Modes

### Three Levels [PARTIAL]

| Level | Who gets it | How it works |
|-------|------------|-------------|
| **Guided** | New users, early-pipeline students, anyone who asks | Full phase-by-phase walkthrough. Prompts at every transition. Gate mode active if brief requires it. |
| **Supported** | Intermediate users, BUILD-level students | Check-ins at key moments. Mirror mode default, gate mode if brief requires it. |
| **Independent** | Advanced users, professionals, graduates | Minimal interruption. Surfaces only significant drift. Mirror mode always. |

### How the Level Is Determined

1. The Companion reads the Position Statement and suggests a level based on specificity and self-awareness.
2. The user confirms or overrides.
3. The Companion can push back if a user selects Independent but shows persistent unacknowledged drift.

### The Scaffolding Floor [SHIPPED]

Drift detection is always on. It is not an ESF construct. It is the Companion's baseline behavior. Even a user who opts out of all ESF constructs (no Position Statement, no Records of Resistance, no Five Questions) still gets drift flags and access to cognitive techniques.

---

## 4. Cognitive Techniques Engine [SHIPPED]

Five research-backed techniques the Companion can guide in real time:

| Technique | What the Companion does | When to offer |
|-----------|------------------------|---------------|
| **Lateral thinking** | "What if you reversed your core constraint?" | Fixation signal: same approach across 2+ sessions |
| **Analogical reasoning** | "What does this project look like if it is a biological system? A musical form?" | Narrow framing. Proactively offered once per project. |
| **Constraint manipulation** | "What opens up when you remove the most obvious constraint?" | User stuck within their own parameters. Proactively at Make phase start. |
| **Random stimulus** | "Force a connection between this arbitrary input and your project." | Agency drift: accepting AI defaults without pushing back. |
| **Perspective shift** | "Adopt the position of someone who would never approach this your way." | Proactively at Explore phase. Reactively when work and Position Statement converge too neatly. |

**Proactive cadence:** One technique per phase transition. [SHIPPED]
**Reactive triggers:** Fixation, agency drift, fluency collapse, convergence. [SHIPPED]

**Note:** The existing Phase 3 exploration modes and Phase 4 drift detection provide the foundation. The structured five-technique engine with proactive/reactive cadence is shipping this session via the esf-cognitive skill.

---

## 5. Architecture

### One Repo, One Install [SHIPPED]

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
```

### Multi-Platform Install [SHIPPED]

The install script detects or asks the platform, then installs only what that user needs:

| Platform | What gets installed | Status |
|----------|-------------------|--------|
| **Claude Code** | `.claude/` directory (agents, skills, reference) | [SHIPPED] |
| **ChatGPT** | `chatgpt-instructions.md` (custom instructions format) | [SHIPPED] |
| **Gemini CLI** | `GEMINI.md` format | [SHIPPED] |
| **Codex CLI** | `.codex/AGENTS.md` directory | [SHIPPED] |
| **Other / Not sure** | `COMPANION.md` (universal system prompt) | [SHIPPED] |

**v1 scope:** Claude Code is the full experience. Other platforms get the `prompts/` directory (manual paste, honest about limitations). Platform-specific files for ChatGPT, Gemini, and Codex are [ROADMAP].

### Repo Structure

```
esf-companion/
├── README.md
├── ROADMAP.md                   # This PRD, versioned
├── WALKTHROUGH.md               # User-facing guide
├── CHANGELOG.md
├── CITATION.cff
├── install.sh
├── WORKFLOW.md
│
├── .claude/                     # Claude Code (v1 primary platform)
│   ├── agents/esf-companion.md
│   ├── skills/
│   │   ├── esf-onboarding/      [SHIPPED]
│   │   ├── esf-project/         [SHIPPED]
│   │   ├── esf-cognitive/       [SHIPPED]
│   │   ├── esf-git/             [SHIPPED]
│   │   ├── esf-verify/          [SHIPPED]
│   │   └── esf-update/          [SHIPPED]
│   └── reference/
│
├── prompts/                     # Non-Claude platforms (manual paste)
├── templates/
└── courses/                     # Optional course configs
```

---

## 6. Brief-Driven Guidance

### Three Paths In

| Path | User action | Companion response | Status |
|------|-----------|-------------------|----|
| **Drop a file** | Places `.md`, `.pdf`, `.docx`, or `.txt` in `projects/[name]/briefs/` | Reads frontmatter first (instant). If none, reads prose and asks clarifying questions. | [SHIPPED] |
| **Paste or describe** | Pastes text or describes project verbally | Extracts structure, generates formatted brief, asks "does this capture it?" | [PARTIAL] |
| **Build from scratch** | Says "I'm starting a new project" | Asks 5 questions: what, deliverables, AI boundaries, deadline, ESF preference. Generates and saves the brief. | [PARTIAL] |

### Three-Value Frontmatter Fields [SHIPPED]

`position-statement` and `five-questions` accept three values:

| Value | Companion behavior |
|-------|-------------------|
| `required` | Gate enforced. Companion verifies before proceeding. |
| `optional` | Companion offers but does not gate. |
| `not-required` | Companion skips entirely. |

### What the Companion Extracts

In priority order: frontmatter fields, deliverables list, AI use policy, timeline/milestones, grading criteria, ADP ceremonies, Five Questions, portfolio artifact description, toolkit repo placement.

---

## 7. Universal Onboarding

### The Flow

**Step 1: Platform.** From install flag or first question.

**Step 2: Who are you.** One open question: "Tell me about yourself and what you do." The Companion infers context without categorizing. Confirms understanding. [SHIPPED]

**Step 3: First project (optional).** "Are you starting a specific project, or is this general setup?"

**Step 4: Position Statement seed.** The Companion explains the concept but does not ask the user to write one yet. That happens when a project begins.

**Step 5: Workspace creation.** Adapted to what the Companion learned about the user.

### Onboarding does NOT: [SHIPPED]
- Ask "are you a student or faculty?"
- Ask for scaffolding level preference (determined later, from Position Statement)
- Ask the user to write a Position Statement during setup

### Addressed Gaps [PARTIAL]

| Scenario | Solution | Status |
|----------|---------|--------|
| Self-motivated student, no institutional context | Calibrating question: "Have you felt AI start driving your direction instead of you?" | [SHIPPED] |
| Educator creating briefs | Guided walkthrough generating complete briefs with all ESF chain elements | [SHIPPED] |
| Professional, confidentiality concern | Local-only assurance, `.gitignore` guidance, conversation platform trade-off named | [SHIPPED] |
| Explorer returns after weeks | No guilt, fresh start, first Position Statement gets full explanation | [SHIPPED] |
| Platform migration | Migrate/fresh/cancel options, manual import help | [SHIPPED] |
| Multiple concurrent projects | Active project selection at session start, locked context per session | [SHIPPED] |

---

## 8. Memory Architecture

### Three Layers

| Layer | What it holds | Where it lives | Persistence | Status |
|-------|-------------|---------------|-------------|--------|
| **Identity** | Name, discipline, preferences, scaffolding baseline, growth record | `projects/_esf/companion-state.md` | Permanent, updated during onboarding and at project completion | [SHIPPED] |
| **Project context** | Phase, Position Statement reference, RoR count, drift history, last session | `projects/[name]/PROJECT.md` | Per project, updated each session | [SHIPPED] |
| **Session memory** | Decisions made, techniques used, drift flagged | `projects/[name]/logs/session-YYYY-MM-DD.md` | Created each session | [SHIPPED] |

### Session Start Protocol

1. Read workspace state file
2. Ask which project (if multiple)
3. Read that project's `PROJECT.md`
4. Read most recent session log's "Next Session" section
5. Orient the user

### Conversation-Platform Users [PARTIAL]

`PROJECT.md` is the portable context object. Short enough to paste (10 to 15 lines). The Companion generates an updated version at session end for the user to save. Generation at session end is documented in esf-project but no auto-generation for initial setup exists for conversation users.

### Addressed Gaps

- Long gap between sessions: ask what changed before assuming
- Project completion: close-out protocol, archive PROJECT.md, update Growth Record
- Position Statement evolution: version the statement (v1, v2), celebrate deliberate pivots
- Forgotten context paste: ask for it, reconstruct if needed, emphasize saving
- Identity recalibration: offer every 3 completed projects

---

## 9. Operational Mechanics

### Who Does What

| Artifact | Generated by | User's role | When | Status |
|----------|-------------|-------------|------|--------|
| **Record of Resistance** | User writes, Companion prompts and pre-fills "what AI produced" | Writes the reasoning (why rejected, what instead) | Real-time, when rejection happens | [SHIPPED] |
| **AI Use Log** | Companion auto-drafts from session | Reviews, corrects, approves | End of each session | [SHIPPED] |
| **Disclosure Statement** | Companion drafts from accumulated logs and RoRs | Reviews, edits, owns | At milestones and project close | [SHIPPED] |

### Records of Resistance Detail

The Companion watches for rejection moments. When the user rejects or significantly revises AI output:

"You just rejected that suggestion. That is a Record of Resistance. Want to capture it? Three things: what AI produced, why you rejected it, what you did instead."

The Companion pre-fills "what AI produced." The user fills the reasoning. If the user declines, the Companion tracks the count and flags later if the minimum is not met.

### Disclosure Statement Detail

Generated at two points: milestone checkpoints (if brief defines milestones) and project close. The draft pulls from session logs, Records of Resistance, Position Statement, and any Position Statement revisions. The Companion flags discrepancies: "Your disclosure says you independently developed the color system, but the session log from March 15 shows AI generated the initial palette."

---

## 10. Position Statement Mechanism

### Three Reference Points [SHIPPED]

The Companion extracts:

| Reference point | What it tracks | Drift signal example |
|----------------|---------------|---------------------|
| **Direction** | Is the work heading where the user said? | User said "sound installation." Work is becoming a static visual piece. |
| **Priority** | Are the non-negotiable qualities present? | User said "intentional mapping." System uses random assignment. |
| **Boundary** | Has the stated line been crossed? | User said "AI will not redesign my gestural vocabulary." AI-generated mappings are the primary input. |

### Canonical Terminology

User-facing: "stance, what matters most, what I will not compromise."
Companion's internal extraction: "direction, priority, boundary."
Course-specific alias: "Design Intent" (AI 201).

### Key Behaviors

- **Vague statements rejected.** The Companion asks specificity questions until the statement is trackable. [SHIPPED]
- **Understanding confirmed.** The Companion reflects back its reading before work begins. [SHIPPED]
- **Readability pass offered, not assumed.** "Want me to clean up the language?" [SHIPPED]
- **Versioning for pivots.** When the user deliberately changes direction, the Companion saves v1 and creates v2 with reasoning. The disclosure references the full arc. [SHIPPED]
- **Milestone comparison.** Automatic when brief defines milestones. Offered at project midpoint otherwise. [SHIPPED]

### Conversational Drafting (accessibility) [SHIPPED]

For users who cannot write due to processing barriers, the Companion asks the three Position Statement questions aloud and drafts from their answers. The ideas are the user's. The structure is the Companion's contribution. The user confirms the meaning is preserved before proceeding. This is articulation support, not content generation.

---

## 11. Cognitive Friction [SHIPPED]

### Convergence Signals

| Signal | What it suggests |
|--------|-----------------|
| No rejections across multiple exchanges | Agency drift |
| No modifications to AI output | User not engaging critically |
| Rapid agreement ("yes," "looks good") | Metacognitive disengagement |
| Position-work alignment too perfect | Confirming rather than discovering |

### Friction Moves (Socratic)

- Challenge the direction: "What would someone who disagrees say?"
- Surface what is missing: "What is this project NOT addressing?"
- Question AI's contribution: "Explain the reasoning without referencing what AI said."
- Invert a choice: "What if you had gone the opposite direction?"
- Name the fluency risk: "This sounds finished. Walk me through the logic."

### Friction Scales with Scaffolding Level

| Level | Style |
|-------|-------|
| Guided | Explicit, with explanation of why the question matters |
| Supported | Direct, no explanation needed |
| Independent | Compressed. "Weakest point?" One-line prompts. |

### Special Cases

- **First friction ever:** one-time explanation of purpose
- **AI-free projects:** different signals (fixation, shallow observation, premature format commitment)
- **Struggling user:** 30-second minimal check instead of full friction
- **Competent but stagnant:** project-close growth question
- **Collaborative work:** friction is personal, per user's own Position Statement

**Note:** The existing Phase 3 exploration and Phase 4 drift detection provide baseline friction. The structured convergence detection and proactive cadence are shipping this session.

---

## 12. Boundaries and Accessibility

### What the Companion Does NOT Do [SHIPPED]

- **Does not originate Position Statement ideas.** Helps articulate through conversational drafting. Never drafts content.
- **Does not produce deliverables, but supports planning and build.** Reviews work in progress, surfaces drift, prompts Records of Resistance, and runs Five Questions checks. Does not generate the user's work product.
- **Does not replace the instructor.** Does not grade, set deadlines, or make exceptions.
- **Does not diagnose.** Detects drift patterns. Does not diagnose conditions.
- **Does not enforce beyond its mode.** Mirror mode surfaces. Gate mode redirects. Neither punishes.
- **Does not track or report to instructors.** The user's tool. Local files only.
- **Does not claim epistemic authority.** "Your Position Statement says X and the work shows Y." The user determines if that is a problem.

### Neurodivergent Accessibility (Universal Design)

All adaptations available to everyone. No labels. No disclosure required. Calibrated through "how do you prefer to work?"

**ADHD support:**
- Small questions instead of documents for Position Statement [SHIPPED]
- Checkpoint saves ("save where you are, pick up next time") [SHIPPED]
- Thread tracking for context-switching between project aspects [SHIPPED]
- Gentle interrupts during extended unbroken work (hyperfocus check) [SHIPPED]

**Dyslexia support:**
- Conversational drafting (talk through ideas, Companion structures) [SHIPPED]
- Brief summarization ("walk through deliverables one at a time") [SHIPPED]
- Pre-filled Records of Resistance (Companion fills "what AI produced") [SHIPPED]
- Auto-generated session logs (user reviews, does not write from scratch) [SHIPPED]

**Autism support:**
- Explicit schedule on request ("I will check in once during Make phase and once before your milestone") [SHIPPED]
- Direct expectations ("Right now I need you to answer three questions") [SHIPPED]
- Structured alternatives to open-ended Socratic questions [SHIPPED]
- "Less interruption today" scales back to essential drift flags only [SHIPPED]

**Research basis:** Zhu, Yu & Luo (2026, CHI): GenAI metacognitive scaffolding for ADHD. Kalmanovich-Cohen & Stanton (2025): 81% of neurodivergent employees mask; universal design delivers implicit support. Carik et al. (2025): neurodivergent users already use LLMs as translators. Goodman et al. (2024): AI writing scaffolding for dyslexic adults. Full citations in Section 13.

---

## 13. Research Foundation [SHIPPED]

### Core Architecture

| Design Decision | Research Basis |
|----------------|---------------|
| Position Statement before AI | Clark & Chalmers (1998): "active endorsement" condition for genuine cognitive extension |
| Drift detection as baseline | Tankelevitch et al. (2024, CHI Best Paper): metacognitive effort is not self-sustaining |
| Cognitive friction as feature | Vendrell & Johnston (2026): productive struggle stimulates deep understanding |
| Scaffolding adapts to user | Zhang & Zhang (2026): scaffolding works by maintaining authorial agency |
| Socratic over prescriptive | Degen & Asanov (2025): Socratic AI activates ownership of reasoning |
| Brief as contract | Hutchins (1995): distributed cognitive systems require active coordination |

### Drift Detection

| Feature | Research Basis |
|---------|---------------|
| Direction drift | Wadinambiarachchi et al. (2024): fixation displacement, not elimination |
| Agency drift | Wu et al. (2025): "psychological deprivation effect" from AI collaboration |
| Fluency as red flag | Tankelevitch et al. (2024): fluency undermines metacognitive vigilance |
| Convergence detection | Doshi & Hauser (2024): individually better, collectively more similar |

### Cognitive Techniques

| Feature | Research Basis |
|---------|---------------|
| Proactive cadence | Koivisto et al. (2025): proactive interventions stronger than reactive |
| Structural defixation | Wan & Kalman (2025): persona diversification restores collective diversity |
| Perspective techniques | Vendrell & Johnston (2026, P5): intellectual curiosity through alternative perspectives |

### Operational Mechanics

| Feature | Research Basis |
|---------|---------------|
| Records of Resistance | Stoyanov (2026): epistemic audit for delegated reasoning |
| AI Use Log auto-generation | Vendrell & Johnston (2026, P4): metacognitive regulation through explicit logs |
| Disclosure at milestones | Vendrell & Johnston (2026, P3): evaluation embedded throughout |
| Epistemic transparency | Weaver (2024): compliance vs. epistemic transparency distinction |

### Neurodivergent Accessibility

| Feature | Research Basis |
|---------|---------------|
| Conversational drafting | Goodman et al. (2024, LaMPost); Carik et al. (2025): LLMs as translators |
| No disclosure required | Kalmanovich-Cohen & Stanton (2025): 81% mask; universal design works |
| ADHD metacognitive scaffolding | Zhu, Yu & Luo (2026, CHI): three design directions |
| Multimodal interaction | Scoping review (2025, Disability & Rehabilitation): 32 articles on multimodal |
| Universal availability | Kalmanovich-Cohen & Stanton (2025): proactive accommodations benefit all |

### Vendrell & Johnston (2026) Six Processes → Companion Features

| Process | Feature |
|---------|---------|
| Conceptual interpretation | Position Statement |
| Inferential reasoning | Cognitive techniques (lateral, analogical) |
| Evaluative judgement | Five Questions at gates |
| Metacognitive regulation | Drift detection + session logs |
| Intellectual curiosity | Proactive techniques (perspective shift, constraint manipulation) |
| Epistemic integrity | Records of Resistance + Disclosure |

---

## 14. Success Metrics [SHIPPED]

### Individual Users

| Metric | Signal of success |
|--------|-------------------|
| Position Statement specificity over time | v1 vague, v3 precise |
| Records of Resistance quality | Early: "I didn't like it." Later: "I rejected because it contradicted my priority of X." |
| Drift flags engaged vs ignored | User responds with decisions, not dismissals |
| Scaffolding level progression | Guided → Supported → Independent over multiple projects |
| Five Questions depth | Increasingly honest and specific self-assessment |
| Cognitive technique self-initiation | User requests techniques without prompting [v2] |

### Educators

| Metric | Signal of success |
|--------|-------------------|
| Position Statements exist before AI work | 100% compliance |
| RoR minimums met with substance | Records reference Position Statement with reasoning |
| Disclosure matches session logs | Honesty verified |

### Product

| Metric | Signal of success |
|--------|-------------------|
| Completion rate (onboarding to project close) | Users finish what they start |
| Return rate (second project) | Tool becomes practice |
| Self-authored briefs | Users create own accountability structures |
| Post-graduation usage | Practice persists beyond institution |

### What We Do NOT Measure

- Output quality (the Companion judges thinking engagement, not work quality)
- Speed (awareness, not velocity)
- AI usage volume (intention, not quantity)

---

## 15. Version Roadmap

### v1: Claude Code + Applied AI Students [SHIPPED]

**Audience:** Students with instructor briefs on Claude Code.

**Shipped:**
- Five-phase workflow (esf-project skill, production-ready) [SHIPPED]
- Brief-driven guidance with frontmatter extraction [SHIPPED]
- Drift detection (direction + agency) [SHIPPED]
- Position Statement mechanism with versioning [SHIPPED]
- Session memory (PROJECT.md + session logs) [SHIPPED]
- Self-authored briefs for personal projects [SHIPPED]
- Conversational drafting for Position Statement (accessibility) [SHIPPED]
- `prompts/` directory for non-Claude platforms (manual paste, honest about limitations) [SHIPPED]

**Shipping this session:**
- Cognitive techniques engine (five techniques, proactive/reactive cadence) [SHIPPED]
- Cognitive friction as active behavior (convergence detection, friction moves) [SHIPPED]
- Records of Resistance (prompted, pre-filled) [SHIPPED]
- AI Use Log (auto-generated) [SHIPPED]
- Disclosure Statement (at milestones + close) [SHIPPED]
- Universal onboarding (no role labels, one open question) [SHIPPED]

### v2: Universal Tool + Full Conversation Platform [SHIPPED]

**Audience:** Students, professionals, graduates on Claude Code and conversation platforms.

**Shipped:**
- Multi-platform install: `--platform` flag for claude, conversation, chatgpt, gemini, codex [SHIPPED]
- Platform-specific config files: `chatgpt-instructions.md`, `GEMINI.md`, `.codex/AGENTS.md` [SHIPPED]
- Platform migration (migrate/fresh/cancel) in esf-onboarding skill [SHIPPED]
- Accessibility: checkpoint saves, thread tracking, structured Socratic alternatives [SHIPPED]
- Growth Record with development tracking (appended to companion-state.md at project close) [SHIPPED]
- Educator course configs folder documented [SHIPPED]
- Identity recalibration (every 3 projects) — offered at project completion [SHIPPED]
- Educator brief-authoring walkthrough — in esf-onboarding educator path [SHIPPED]

**Partial (deferred to dashboard):**
- Full conversation-platform context restoration for initial session setup [PARTIAL — session end generates PROJECT.md; first-session auto-generation not yet built]

### v3: Framework Evolution + Collective Features [SHIPPED]

**Audience:** Everyone, every platform.

**Shipped:**
- Framework Evolution Protocol: user-proposed ESF adaptations, recorded and applied [SHIPPED]
- Cohort homogenization detection: opt-in Position Statement analysis for educators [SHIPPED]

**Planned:**
- Local visual dashboard (browser-based project cards, phase progress, growth arc) [ROADMAP]
- Educator dashboard or progress visibility (opt-in by student) [ROADMAP]
