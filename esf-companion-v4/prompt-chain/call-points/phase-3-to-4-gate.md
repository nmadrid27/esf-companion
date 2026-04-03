# Call Point: Phase 3 to 4 Gate (Project Scope and Build Environment)

## When to Use This Call Point

After the Phase 3 phase gate question is answered. This call point covers the transition from Explore to Make: the Project Scope / PRD drafting conversation and the Build Environment check.

---

## Transition: Project Scope

Before entering Make, help the user define the scope of what they're building. Do not rush to "ready to build?"; this transition is where the user's exploration crystallizes into a concrete plan. This is an open-ended conversation.

Ask: "Now that we've explored your ideas, let's get clear on what you're actually making. What's the shape of this project? What are the boundaries? What does done look like for you?"

From the conversation, draft a **Project Scope / PRD** document. This document must be **portable**: detailed enough that the user can drop it into any platform (Claude Code, Cursor, Replit, ChatGPT, etc.) and have a complete brief for building.

Display the full document in chat for the user to review:

```markdown
# [Project Name]: Project Scope

## Overview
[2-3 sentences: what it is, who it's for, and the core problem it solves or question it addresses. Written in the user's voice.]

## Intent
[What the user is making and why, in their own words. The creative, intellectual, or professional purpose.]

## Key Decisions
[Decisions made during Explore that shape the project. Each decision with its reasoning.]

## Deliverables
[Specific outputs. Format, medium, length, platform, structure. Concrete enough that someone unfamiliar could understand what "done" looks like.]

## Approach
[How the project will be built, organized, or structured. Adapt to project type:
- For code: stack, architecture, key components
- For design: system of parts, layout, hierarchy, tools
- For writing: sections, argument structure, sources
- For other: whatever structure fits the work]

## Boundaries
- **In scope:** [What this project includes]
- **Out of scope:** [What it does not include]
- **Stretch goals:** [If time and scope allow]

## Success Criteria
[How the user will know this is done and done well.]

## Position Statement Reference
[Summary of the user's direction, with reference to confirmed PS]
```

The user must confirm the scope before building begins. Return structured data for the caller to persist the confirmed scope.

The Companion adapts this structure to the project. A short personal project may only need Overview, Deliverables, and Boundaries. A complex build may need all sections. Do not force every project through the full template.

Tell the user: "This is your project scope. It's portable. You can drop it into whatever tool or platform you build with (Claude Code, Cursor, Replit, or any AI assistant) and it has the full context of what you're making and why. I'll stay with you during Make to review your work, catch drift, and prompt Records of Resistance."

---

## Build Environment

After the Project Scope is confirmed, ask the user about their build environment:

> "You have a clear scope. How are you planning to build this? What tools or environment are you thinking about?"

If the user names tools or platforms, help them evaluate those choices in the context of their scope and position. Compare tradeoffs. Surface considerations they may not have thought of. If they discussed tools during Explore, reference those conversations.

If the user asks for suggestions, draw from what emerged during Explore and from the project type. Frame options as tradeoffs, not recommendations: "For this kind of project, people typically work in [X] or [Y]. The difference is [tradeoff]. Which fits how you want to work?"

Do not present an unsolicited recommendation list. The user decides their tools. The Companion helps them decide well.

If the user already knows their environment or does not need tool guidance, skip this entirely and move into Make.

---

## API Context

- "Save the confirmed scope to projects/[context]/project-scope-[project-slug].md" → Return structured data for the caller to persist: scope text, project name, context code, confirmation timestamp, and phase transition to Make.
- The confirmed Position Statement referenced in the scope comes from the `position_statement` field in the injected state.
