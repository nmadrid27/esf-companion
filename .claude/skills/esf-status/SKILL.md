---
name: esf-status
description: Show an on-demand ESF project gap snapshot (present/missing artifacts, RoR minimum, scaffolding-aware) by running the Defense Pack aggregator in scan-only mode. Use when the user asks for project status, what's missing, or a gap check.
allowed-tools: Bash, Read
---

<!--
MANAGED FILE: do not edit directly.
Changes made here will be overwritten on the next /esf-update run.
-->

Show the current ESF project's gap snapshot. Run the aggregator in scan-only mode and relay its report. Do not fabricate; relay what the scan returns.

## Update check (read-only)

Before the gap snapshot, surface any pending update without consuming the session-start nudge:

```bash
bash .claude/hooks/esf-update-check.sh status-readonly
```

If it prints an "update available" line, show that single line above the snapshot. If it prints nothing, say nothing about updates.

## Step 1: Run the scan

The aggregator owns workspace resolution, so run it first and let it tell you whether a workspace exists. From the current directory:

```
.claude/skills/esf-defense-pack/bin/aggregate.py . --scan-only
```

This prints a JSON snapshot.

## Step 2: Check for a workspace

If the JSON output contains `"error": "no_workspace"` (or the command otherwise fails to run, e.g. no Python, missing skill), tell the user: "No ESF workspace found here. Run /esf-onboarding to set one up." and stop. Do not invent a report.

Otherwise, proceed to render the snapshot.

## Step 3: Render the report

Format the snapshot as a short, plain status block. Reuse the same shape the scanner's gap_report produces:

```
[ESF gap check: <project>]
Position Statement: <status>
Records of Resistance: <N> of <M> required   (omit "of M" when no minimum)
AI Use Log: <status>
Reflection: <status>

Gaps:
- [<severity>] <message>
```

Scaffolding-aware: for Independent, omit INFO gaps; for Guided, add a one-line remediation pointer per gap. If there are no gaps, state "No gaps. Your artifact list is complete." On-demand invocation always shows output, even if `silent_mode` is set.
