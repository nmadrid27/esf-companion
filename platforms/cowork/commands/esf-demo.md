---
description: Run a guided demo of ESF Companion on a sample studio project. Adds a sandbox at demo/critical-cartography/ and walks through all five phases at accelerated pace.
argument-hint: "[--reset]"
---

# /esf-demo

Run a guided demo session of ESF Companion using a pre-seeded sample studio project. The demo exercises every gate, prompt, and selection card the production skill produces, so the user experiences ESF rather than reading about it.

## Argument handling

If invoked as `/esf-demo --reset`, run the **Reset** flow below.

Otherwise, run the **Setup** flow.

## Setup

1. **Confirm intent.** If a sandbox already exists at `demo/critical-cartography/`, ask: "A demo sandbox already exists. Resume the existing demo, restart from scratch, or cancel?" Wait for the user's answer.

2. **Scaffold the sandbox.** Create the following directory structure inside the user's selected workspace folder. Use the file contents from `templates/demo-project/` in this plugin.

```
demo/critical-cartography/
├── briefs/
│   └── cartography.md
├── planning-notes.md
└── .esf-demo (manifest file: see below)
```

The `.esf-demo` manifest is a small JSON or YAML file that marks the sandbox as a demo. Write it as:

```yaml
mode: demo
project: critical-cartography
created: [today's date]
prior_companion_state: |
  [snapshot of companion-state.md before demo activation, so Reset can restore it]
```

3. **Update `companion-state.md`.** Set:
   - `current_project: critical-cartography`
   - `current_context: demo`
   - `current_phase: 2`
   - Add a top-level note: `demo_active: true`

4. **Surface the sandbox.** Use `mcp__cowork__present_files` (or print the relative path if the tool is unavailable) for the brief and planning note. Tell the user:

> "Demo sandbox is ready at `demo/critical-cartography/`. The project is a studio series about absent Indigenous place names. Read the brief and the planning note when you have a minute. To start the session, just say 'Help me start drafting the artist statement' or anything similar that asks for substantive help on this project."

5. **Hand off to the `esf-project` skill in demo mode.** Do not produce further content. The next user message will trigger the skill, which will read the `.esf-demo` manifest and apply the Demo Mode behaviors described in the skill patch.

## Reset

1. **Confirm.** "This will delete the sandbox at `demo/critical-cartography/` and restore `companion-state.md` to its pre-demo state. Confirm?"

2. **On confirm:**
   - Delete `demo/critical-cartography/` and any of its contents.
   - Read `prior_companion_state` from the `.esf-demo` manifest before deletion. If it exists, restore `companion-state.md` from that snapshot.
   - If no manifest exists or the snapshot is absent, leave `companion-state.md` untouched and tell the user: "Sandbox removed. companion-state.md was not auto-restored because no snapshot was found. Review and adjust manually if needed."

3. **Confirm completion.** "Demo sandbox cleared. Run `/esf-demo` to start a fresh demo, or carry on with your real work."

## Notes for the assistant

- Never write demo files outside `demo/critical-cartography/`.
- The `--reset` flag is the only safe path to undo the demo. If the user wants to keep the sandbox but stop the demo session, they can simply move on; the manifest will leave `demo_active: true` until they reset.
- If the user is in `silent_mode`, still run the demo. Silent mode applies to the assistant's narration, not to user-initiated explicit demo commands.
