---
description: Run a cognitive technique to break fixation or reframe your work
allowed-tools: Read, Glob
---

Offer the user a cognitive technique from the ESF Companion's Cognitive Techniques Engine. Use AskUserQuestion with preview cards to let them see what each technique involves before choosing.

## Step 1: Read the current project context

Glob for `companion-state.md` (root first, then one level deep, ignoring sample/examples/templates). If found, read it to get the current project name and phase. Use this context to frame the technique as relevant to their actual work.

## Step 2: Present techniques with preview cards

Use AskUserQuestion:

Question: "Which thinking exercise do you want to run? Each takes 5 to 10 minutes."

Options:

- **Lateral thinking** — preview: "Reverse your core constraint. The central limit of your project becomes your starting point instead. What opens up when the thing you've been working around becomes the thing you're working toward? Good for: feeling stuck in one approach, same direction across multiple sessions."

- **Perspective shift** — preview: "Adopt the position of someone who would never approach this your way. What would they say is missing, wrong, or misframed? You don't have to agree with them — you're trying on the view. Good for: your work and Position Statement are converging too neatly, you haven't been challenged recently."

- **Analogical reasoning** — preview: "Map your project onto an unrelated domain — a biological system, a piece of music, a recipe, a sport. What structural insight transfers back? Usually surfaces a hidden assumption you've been carrying. Good for: narrow framing, feeling like there's only one way to approach this."

- **Constraint manipulation** — preview: "Remove your most obvious constraint and describe what opens up. Then add a constraint you haven't been using and describe what that forces. Two moves, back to back. Good for: stuck within your own parameters, options feeling limited."

## Step 3: Run the technique

After the user selects a technique, run it using the delivery format from `references/cognitive-techniques.md` in the esf-project skill.

Frame it as an invitation: "Take a few minutes with this and tell me what you see." Give the user space to respond before moving forward.

## Step 4: Connect back to the project

After the user responds, ask: "Does this change anything about your Position Statement or your current direction — or does it confirm where you're headed?"

If something shifted: offer to update the Position Statement or note it as a decision point in the session buffer.

If nothing shifted: acknowledge it — "Good. That's confirmation, not a dead end. You now know your direction holds under pressure."
