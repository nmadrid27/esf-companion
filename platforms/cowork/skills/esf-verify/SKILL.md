---
name: esf-verify
description: >
  Use this skill when AI has produced factual claims, cited sources, or presented data
  that the user should check before incorporating. Triggers for "/esf-verify", "let's
  verify that", "check those claims", "I want to verify what you said", or when the
  esf-project skill flags verification moments during Phase 3 (Explore) or Phase 4 (Make).
version: 0.1.0
---

# ESF Verify: Checking What AI Told You

## Purpose

Verification is the user's job, not AI's. Your role is to surface specific claims clearly, help the user locate original sources, and log results. Do not verify claims for the user — that defeats the purpose.

---

## Step 1: Surface the Claims

Present the claims that need checking from the last AI response. Frame it clearly:

> "I made these factual claims in that last response. Before you use any of them, pick the ones that matter to your project and check them."

List each claim as a numbered item with a priority and a suggested verification method:

| # | Claim | Priority | How to check |
|---|-------|----------|-------------|
| 1 | [specific claim] | High — shapes your argument | Search for the source, check the original |
| 2 | [specific claim] | Low — background detail | Quick web search to confirm |

Let the user decide which claims to check. Not everything needs verification. **High-weight claims** — those that shape creative direction or support the Position Statement — matter most.

---

## Step 2: Walk Through Each Claim

For each claim the user chooses to verify:

1. **State the claim clearly.** Repeat it verbatim so there is no ambiguity about what is being checked.
2. **Help the user locate the source.** Offer search terms, likely databases, or the original publication if known. Do not locate it for them.
3. **Ask the user to read and judge.** "Does the source say what I said it says?"
4. **Record the result:** confirmed / partially accurate / inaccurate / source not found.

---

## Step 3: Log the Results

After verification, help the user fill in the AI Use Log's Verification table:

```
| Claim or source | Checked? | How | Result |
|---|---|---|---|
| [claim] | Yes | [method] | [confirmed / inaccurate / not found] |
```

The log lives at `projects/[context]/ai-use-logs/[project-name]-ai-use-log.md`. If it does not exist yet, create it automatically with this template header:

```markdown
---
type: ai-use-log
project: [project name]
created: [today's date]
---

# AI Use Log — [Project Name]

## Verification Log

| Claim or source | Checked? | How | Result |
|---|---|---|---|
```

Then append the verification results below the table header.

---

## What Not to Do

- Do not verify claims yourself — the user builds the habit by doing it.
- Do not present verification as busywork. High-weight claims that shape creative direction or the Position Statement are worth the time.
- Do not skip plausible-sounding claims. Fluent AI output is not a quality signal.
- Do not fabricate verification results.
- Do not mark a claim as verified without the user actually checking it.
