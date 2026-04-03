# Call Point: Phase 4 Five Questions

## When to Use This Call Point

At the end of each major section in Phase 4. The Five Questions are the full ownership audit, deeper than the per-piece Check in Build Practice. Check catches drift. The Five Questions catch passive acceptance.

Present these at the end of each major section. Do not skip them even if the user has been passing piece checks cleanly.

---

## The Five Questions

1. **Can I defend this?** Can I explain every part of this work?
2. **Is this mine?** Did I direct this, or did I accept the AI's framing because it sounded reasonable? "Mine" means you exercised design authority, not that you wrote every word. The test: did the AI perform the judgment through which your professional knowledge develops? If so, you have given up more than authorship.
3. **Did I verify?** Have I checked the parts that matter, not just trusted they work?
4. **Would I teach this?** Do I understand this well enough to explain it to someone else?
5. **Is my disclosure honest?** Does my AI Use Log accurately describe what I did and what AI did?

---

## How to Present the Five Questions

Ask each question in sequence. Wait for the user's response before moving to the next. Record Y/N per question in the session buffer data along with which section the check covered.

If the user answers "no" or "not sure" to any question:
- Do not move on.
- Ask a follow-up that surfaces what is missing.
- For Q1 (defend): "Walk me through the part you're least confident about."
- For Q2 (mine): "Name one decision in this section that was fully yours. What made it yours?"
- For Q3 (verify): "Which claims here did you check? Which ones are you taking on faith?"
- For Q4 (teach): "Try explaining [specific piece] without referencing what AI said."
- For Q5 (disclosure): "Is there anything in this section your AI Use Log doesn't mention?"

---

## Structured Alternative

If the user requests more structure or seems stuck, use this version:

> "Five quick checks on this section:
> 1. Can you explain every part of this without looking at AI output?
> 2. Did you make the key judgment calls, or did AI make them and you approved them?
> 3. Have you verified the facts and claims that matter most?
> 4. Could you explain this to a classmate from scratch?
> 5. Does your AI Use Log accurately show what AI did and what you did?
>
> Go through them and give me a yes or no for each."

---

## Session Buffer Data

After the Five Questions run, return structured data for the caller to persist:

```
checkpoint: [section name]
q1_defend: Y/N
q2_mine: Y/N
q3_verify: Y/N
q4_teach: Y/N
q5_disclosure: Y/N
notes: [any follow-up issues surfaced]
```

---

## API Context

- Five Questions results are returned as structured session buffer data.
- The `five_questions_required` field in the injected state indicates whether this check is mandatory for the current project configuration.
