---
name: esf-verify
description: Use when AI produces factual claims, sources, or data that the user should check. Walks through verification and logs results to the AI Use Log.
---

# ESF Verify: Checking What AI Told You

## When to Use

Invoke when AI has produced factual claims, cited sources, or presented data during Phase 3 (Explore) or Phase 4 (Make). The esf-project skill flags these moments: "This includes claims about [X]. Log any you verified."

## The Verification Prompt

Present the claims that need checking:

> "I made these factual claims in that last response. Before you use any of them, pick the ones that matter to your project and check them."

List the specific claims as a numbered checklist. For each:

| Claim | Priority | How to check |
|-------|----------|-------------|
| [specific claim] | High (it shapes your argument) / Low (background detail) | Search for the source, check the original, test it yourself |

Let the user decide which claims to verify. Not everything needs checking. High-weight claims (those that shape creative direction or support the Position Statement) matter most.

## Verification Walkthrough

For each claim the user chooses to check:

1. **What did AI claim?** (state it clearly)
2. **Can you find the original source?** (help the user search, but they evaluate)
3. **Does the source say what AI said it says?** (user reads and judges)
4. **Result:** confirmed / partially accurate / inaccurate / source not found

## Logging

After verification, help the user fill in their AI Use Log's Verification table:

```
| Claim or source | Checked? | How | Result |
|---|---|---|---|
| [claim] | Yes | [method] | [confirmed/inaccurate/not found] |
```

## What Not to Do

- Do not verify claims for the user (that defeats the purpose)
- Do not present verification as busywork ("you should check everything")
- Do not skip high-weight claims because they seem plausible
- Do not fabricate verification results
