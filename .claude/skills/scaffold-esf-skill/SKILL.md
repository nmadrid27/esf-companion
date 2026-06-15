---
name: scaffold-esf-skill
description: Scaffold a new shipped ESF skill with correct frontmatter, the managed-file banner, cross-platform parity (.claude/skills + platforms/cowork/skills), and installer registration. Use when adding a new product skill so parity and shipping are built in from the start.
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Glob
---

<!--
MAINTAINER-ONLY dev skill. Not shipped by install.sh, not managed by /esf-update.
Edit freely. Lives only in the source repo to support skill authoring.
-->

Scaffold a new **shipped** ESF Companion skill. The point of this skill is to bake in the three things that are easy to forget and silently break the distribution: the managed-file banner, cross-platform parity, and installer registration. A new SKILL.md that is not wired into `install.sh` never reaches users.

## Inputs to gather

Ask the maintainer (or take from the invocation):
- **Skill name** (kebab-case, becomes the directory name and the `name:` field; conventionally `esf-<thing>`).
- **Description** (a trigger, not a label: say *when to use it*, with concrete trigger phrases. Model it on esf-status and esf-git).
- **Allowed tools**, if the skill restricts them (for example `Bash, Read`).
- **Invocation control**: user-only (side effects -> `disable-model-invocation: true`), Claude-only (background knowledge -> `user-invocable: false`), or both (omit both).
- **Cowork parity**: does this skill also belong in the Cowork platform? Most user-facing ESF skills do.

## Steps

1. **Create the Claude Code skill.** Write `.claude/skills/<name>/SKILL.md` with frontmatter (`name`, `description`, and any `allowed-tools` / invocation flags), followed by the managed-file banner exactly as the existing shipped skills carry it:
   ```
   <!--
   MANAGED FILE: do not edit directly.
   Changes made here will be overwritten on the next /esf-update run.
   To customize Companion behavior, edit companion-notes.md instead.
   To report a bug or suggest a change: https://github.com/nmadrid27/esf-companion
   -->
   ```
   Then a short body. Confirm `name:` exactly equals `<name>` (the directory).

2. **Create the Cowork copy if applicable.** If the skill belongs in Cowork, write `platforms/cowork/skills/<name>/SKILL.md` with parity content. Note any platform-specific wording the maintainer needs to adjust. If not applicable, say so explicitly so the omission is a decision, not an oversight.

3. **Register it in install.sh.** This is the step that actually ships the skill. `install.sh` fetches each skill by explicit name. Show the maintainer the exact lines to add, matching the existing pattern:
   ```bash
   mkdir -p .claude/skills/<name>
   curl -fsSL "$TOOLKIT_BASE/.claude/skills/<name>/SKILL.md" -o .claude/skills/<name>/SKILL.md \
     || { echo -e "${RED}Failed to fetch <name>/SKILL.md.${NC}"; exit 1; }
   ```
   Offer to apply the edit. If the skill ships supporting files under `bin/` or `render/` (like esf-defense-pack), those must instead be driven by a `MANIFEST.txt`; point the maintainer to that pattern and to `test/check-defense-pack-manifest.sh`.

4. **Surface remaining registration.** Remind the maintainer to add the new skill to any user-facing inventory that lists skills (README folder diagram, GETTING_STARTED, the Cowork plugin command set if it gets a `/` command), and to add a CHANGELOG `[Unreleased]` entry.

5. **Verify.** Run `bash test/smoke-test.sh` if the maintainer wants a pre-merge check that the installer still wires everything correctly.

## Guardrails

- Do not invent skill behavior. Scaffold structure and frontmatter; leave the substantive body for the maintainer unless they ask you to draft it.
- A skill is not shipped until install.sh fetches it. Never report the skill as done after only creating the SKILL.md.
- Keep the two platform copies in parity. If you create one, account for the other.
