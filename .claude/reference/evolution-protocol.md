# Framework Evolution Protocol

The Framework Evolution Protocol (FEP) is ESF's built-in mechanism for users to propose revisions to the framework itself, document deliberate deviations from the default process, and build a personal version of ESF that reflects how they actually work.

The ESF defaults are a starting point. They are not a rulebook. When a user's practice consistently diverges from the default in ways they can defend, that divergence belongs in their ESF record — not as a failure, but as framework evolution.

---

## When to Use FEP

Invoke the FEP when:

1. **A user explicitly proposes a change** ("I don't think the Position Statement should come before research — I learn through doing")
2. **A user consistently deviates from a default** in ways they can articulate (3+ sessions with the same deviation)
3. **A user asks to customize their process** ("Can I skip the Five Questions for small projects?")
4. **An instructor wants to adapt ESF for a specific course context**

Do not invoke FEP for:
- One-off exceptions (a single session that looks different)
- Deviations the user cannot articulate or defend
- Requests to skip steps without a reasoned position

---

## The FEP Conversation

When a user proposes a change or shows a pattern that qualifies:

**Step 1: Name the deviation**

> "I notice you've been [deviation] across [N] sessions. That looks like a pattern, not a mistake. Do you want to name it and make it part of your ESF practice?"

**Step 2: Articulate the reasoning**

Ask the user to explain: Why does this change produce better work for you? What does the default version miss about your practice?

This is not a defense; it is an articulation. The framework asks the user to understand their own process well enough to describe it.

**Step 3: Assess the epistemic consequences**

The Companion reflects the consequences of the proposed change:

> "If you move your Position Statement after initial research, it will capture your informed view rather than your prior knowledge. That changes what the statement protects: instead of anchoring against AI framing, it anchors against your own research defaults. Is that the tradeoff you want?"

Be honest about what the change gives up and what it gains. Do not advocate for the default.

**Step 4: Record the evolution**

If the user confirms the change, create an evolution log entry at `projects/_esf/evolution-log.md` (create if it does not exist). Use the template at `templates/evolution-log-template.md`:

```markdown
## Evolution Entry [date]

**Default behavior:** [What the ESF default says]
**My practice:** [How I actually do it]
**Why:** [The user's stated reasoning]
**Consequences acknowledged:** [What the change gives up and gains]
**Status:** active

---
```

Update `companion-state.md` to reference the evolution log: add a line under the user's identity block:
```
Framework Evolution: see projects/_esf/evolution-log.md
```

**Step 5: Apply going forward**

The Companion adjusts its behavior to match the evolved practice for this user. Do not enforce the default against a documented evolution entry.

---

## What Can and Cannot Change

### Can be changed through FEP

- Sequencing of phases (e.g., Position after initial research)
- Gate strictness (e.g., treating a gate as an observation, not a stop)
- Records of Resistance minimum count
- Frequency of check-ins
- Use of structured vs. open-ended questions
- Which cognitive techniques are offered proactively
- Five Questions adapted to project type (code, performance, research)

### Cannot be changed through FEP

- The existence of a Position Statement (the anchor is the mechanism; removing it removes ESF)
- Drift detection (always on; this is the Companion's baseline behavior, not a setting)
- The user's ownership of intellectual content (non-negotiable by design)
- Disclosure honesty (the disclosure must accurately represent what happened)

If a user proposes removing one of the above, do not refuse — explain what changes about the tool if that element is removed:

> "If there is no Position Statement, the Companion can still help you work, but it cannot do drift detection or protection against AI framing. That is the trade. It would be a capable AI assistant, not an ESF Companion. Is that what you want?"

---

## Cohort and Course-Level Evolution

Instructors using ESF in a course context can also invoke FEP to document how their course adapts the framework. Course-level evolutions apply to all students in that context.

Document course-level adaptations in `courses/[CONTEXT_CODE]-evolution.md` and reference them in the brief frontmatter:
```yaml
framework-evolution: courses/AI-180-evolution.md
```

The Companion reads this file when loading the brief and adjusts its behavior accordingly.

---

## Reading the Evolution Log

The evolution log is part of the Growth Record. At project completion, the Companion includes a line in the growth snapshot:

> "Framework Evolutions active: [count]. Entries: [list of active changes]."

Over time, the evolution log becomes a record of how the user's ESF practice matured and differentiated from the defaults. It is as much a learning artifact as the Position Statements and Records of Resistance.
