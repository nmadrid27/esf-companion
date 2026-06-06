---
name: esf-update
description: Check for ESF Companion updates and install the latest version.
---

<!--
MANAGED FILE: do not edit directly.
Changes made here will be overwritten on the next /esf-update run.
To customize Companion behavior, edit companion-notes.md instead.
To report a bug or suggest a change: https://github.com/nmadrid27/esf-companion
-->

# ESF Update

Check whether a newer version of the ESF Companion is available and offer to install it.

## Steps

1. Resolve versions with the shared helper (single source of truth):
   ```bash
   bash .claude/hooks/esf-update-check.sh resolve
   ```
   It prints `local=<tag>` and (if reachable) `latest=<tag>`. If no `latest=` line is printed, tell the user: "Could not resolve the latest companion-vX.Y.Z release from GitHub. Aborting update. Try again later, or run the installer manually with --force --source <path>." Stop. Do not fall back to `main`.
2. Compare with version-sort (the helper already validated the tags). If `latest` is not strictly newer than `local`, tell the user: "Your Companion is up to date (`<local>`)." and stop.
3. If `latest` is newer, capture `OLD=<local>` and tell the user: "ESF Companion update available (local: `<local>`, latest: `<latest>`)." Ask: "Want me to update? This refreshes skills, templates, and reference files. Your workspace state and project folders are preserved."
4. On confirmation, re-validate `<latest>` matches `^companion-v[0-9]+\.[0-9]+\.[0-9]+$` (never interpolate an unvalidated tag), then run:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/<latest>/install.sh | bash -s -- --force --platform claude
   ```
5. After the installer completes, read `NEW` from `.claude/esf-version` and show what changed:
   ```bash
   bash .claude/hooks/esf-update-check.sh changelog <OLD> <NEW>
   ```
   Print the output under a "What changed" heading. If it prints nothing, say: "Updated to `<NEW>`. Could not load the changelog; see https://github.com/nmadrid27/esf-companion/blob/main/CHANGELOG.md."
6. Refresh the cache so the session-start nudge does not re-fire for the just-installed version:
   ```bash
   ESF_UPDATE_LATEST="<NEW>" bash .claude/hooks/esf-update-check.sh refresh
   ```
   (Equivalently, the next session's refresh self-corrects within 24h.)
