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

## Step 1: Locate the workspace

The workspace root is the directory containing `esf/companion-state.md` (or a legacy `projects/_esf/companion-state.md`). If neither resolves, tell the user: "No ESF workspace found here. Run /esf-onboarding to set one up." and stop.

## Step 2: Run the scan

Run, from the workspace root:

```
.claude/skills/esf-defense-pack/bin/aggregate.py . --scan-only
```

This prints a JSON snapshot. If the command errors (no Python, missing skill), say so plainly and stop; do not invent a report.

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
