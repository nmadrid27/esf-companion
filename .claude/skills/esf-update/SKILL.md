---
name: esf-update
description: Check for ESF Companion updates and install the latest version.
---

<!--
MANAGED FILE — do not edit directly.
Changes made here will be overwritten on the next /esf-update run.
To customize Companion behavior, edit companion-notes.md instead.
To report a bug or suggest a change: https://github.com/nmadrid27/esf-companion
-->

# ESF Update

Check whether a newer version of the ESF Companion is available and offer to install it.

## Steps

1. Read the local version from `.claude/esf-version`.
2. Fetch the latest release tag from the GitHub API:
   ```
   curl -fsSL https://api.github.com/repos/nmadrid27/esf-companion/tags
   ```
   Parse the response and pick the highest semver tag matching the `companion-vX.Y.Z` pattern (the dedicated namespace for Companion releases; older `vX.Y.Z` manuscript tags and `cowork-vX.Y.Z` plugin tags are intentionally excluded). Use version-sort, not lexicographic-sort: `companion-v0.10.0` must beat `companion-v0.9.0`. Store it as `LATEST_TAG` (e.g., `companion-v0.7.0`).

   If the API call fails (rate limit, network error, malformed response, or no matching tags returned), tell the user:
   > "Could not resolve the latest companion-vX.Y.Z release tag from GitHub. Aborting update. Try again later, or run the installer manually with --force --source <path> against a local clone."
   Stop. Do not fall back to `main`.

3. Fetch the remote version from `https://raw.githubusercontent.com/nmadrid27/esf-companion/<LATEST_TAG>/.claude/esf-version`. If that fetch fails, abort with the same message.
4. Compare the two versions.
   - If the remote version is higher, tell the user: "ESF Companion update available (local: v[local], latest: v[remote])." Then ask: "Want me to run the installer to update? This will refresh skills, templates, and reference files. Your workspace state file and project folders are preserved."
   - If versions match, tell the user: "Your Companion is up to date (v[local])."
5. If the user confirms the update, run:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/<LATEST_TAG>/install.sh | bash -s -- --force --platform claude
   ```
   The `<LATEST_TAG>` is the tag resolved in step 2 (e.g., `companion-v0.7.0`). The `--force` flag skips interactive prompts unnecessary during an update. The `--platform claude` flag ensures the full Claude Code install path runs.
6. After the installer completes, re-read `.claude/esf-version` and confirm the update succeeded.
