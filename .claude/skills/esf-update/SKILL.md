---
name: esf-update
description: Check for ESF Companion updates and install the latest version.
---

# ESF Update

Check whether a newer version of the ESF Companion is available and offer to install it.

## Steps

1. Read the local version from `.claude/esf-version`.
2. Fetch the remote version from `https://raw.githubusercontent.com/nmadrid27/esf-companion/main/.claude/esf-version`. If the fetch fails (offline, timeout, error), tell the user you could not reach GitHub and suggest they try again later. Stop.
3. Compare the two versions.
   - If the remote version is higher, tell the user: "ESF toolkit update available (local: v[local], latest: v[remote])." Then ask: "Want me to run the installer to update? This will refresh skills, templates, and reference files. Your companion state file and project folders are preserved."
   - If versions match, tell the user: "Your toolkit is up to date (v[local])."
4. If the user confirms the update, run:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nmadrid27/esf-companion/main/install.sh | bash
   ```
5. After the installer completes, re-read `.claude/esf-version` and confirm the update succeeded.
