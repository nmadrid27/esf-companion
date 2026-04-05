# ESF Companion: Sample Data

This folder contains pre-filled BUILD-level sample data for testing the Companion without running onboarding.

**Sample student:** Alex Rivera, BFA Motion Media Design, BUILD level (Creative Computing with AI)
**Sample project:** Project 2, Responsive System (reaction-diffusion system with sound input)
**Phase:** Explore (Position Statement complete, working on implementation)

---

## How to Use

Copy these files into your project repo after running the installer:

```bash
# From inside your project repo, after running install.sh:
mkdir -p projects/_esf
cp path/to/sample/projects/_esf/companion-state.md projects/_esf/companion-state.md
cp -r path/to/sample/projects/build-course projects/
```

Or install with the sample flag:

```bash
curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash -s -- --sample
```

Then open Claude Code and start working:

```bash
claude
```

Try: "I want to keep working on my responsive system. I'm in the Explore phase and need to think through my shader implementation."

The Companion will load Alex's context, check for the Position Statement (it exists), confirm the phase, and engage as a thinking partner from there.

---

## What's Included

| File | What it demonstrates |
|------|---------------------|
| **BUILD level (Creative Computing)** | **Alex Rivera, BFA Motion Media Design** |
| `projects/_esf/companion-state.md` | Sample workspace state: Alex Rivera, BUILD-level calibration, 3 RoR required, Explore phase |
| `projects/build-course/briefs/p2-responsive-system.md` | Realistic BUILD-level project brief: tool-agnostic, emergence-focused |
| `projects/build-course/position-statements/responsive-system.md` | Student-voice position statement with 3-element Design Intent |
| `projects/build-course/records-of-resistance/responsive-system-ror-01.md` | Record of Resistance: AI suggestion documented and deliberately rejected |
| `projects/build-course/records-of-resistance/responsive-system-ror-02.md` | Record of Resistance: choosing raw Canvas API over a suggested library for aesthetic and creative control reasons |
| `projects/build-course/gate-records/gate-no-remediation.md` | Gate record where Q2 ("Is this mine?") fails; student returns to Position Statement, redesigns system architecture, passes on second attempt |
| **THINK level (Creativity and AI)** | **Jamie Torres, BFA Illustration; Priya Kapoor, BFA Graphic Design; Sam Chen, BFA Photography** |
| `projects/think-course/briefs/p2-visual-essay.md` | THINK-level project brief: personal visual essay, tool-agnostic, process-focused |
| `projects/think-course/position-statements/visual-essay.md` | Non-technical position statement: identity, memory, and place in illustration |
| `projects/think-course/records-of-resistance/visual-essay-ror-01.md` | Partial acceptance: keeping an AI composition suggestion while rejecting its color palette, with documented reasoning |
| `projects/think-course/records-of-resistance/visual-essay-ror-02.md` | Source verification: catching a misattributed design history reference the AI presented confidently |
| `projects/think-course/records-of-resistance/visual-essay-ror-03.md` | Low-stakes pushback: rejecting a single wording change in an artist statement, showing RoR as habit, not heroics |
| `projects/think-course/logs/ai-use-log-sample.md` | Filled-in AI Use Log with 3 sessions: composition research, statement review, reference research |
| `projects/think-course/process/process-blog-entry.md` | Process blog entry in student voice: metacognitive reflection on how the Position Statement shaped real-time decisions |

---

## What to Test

- **Gate enforcement:** Delete the position statement file and try to start a project session. The Companion should block until it's restored.
- **Phase awareness:** The workspace state says Alex is in Explore phase. Ask about the Inquire phase artifacts; it should know they're complete.
- **AI calibration:** BUILD-level calibration means less hand-holding. Ask a vague question and notice how the Companion pushes back rather than filling in the gaps.
- **Records of Resistance:** Ask the Companion to help you review your RoR count. It should know 3 are required and 1 is complete.
