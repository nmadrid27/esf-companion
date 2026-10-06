---
name: esf-status
description: Show an on-demand ESF project gap snapshot (present/missing artifacts, RoR minimum, scaffolding-aware) by running the Defense Pack aggregator in scan-only mode. Use when the user asks for project status, what's missing, or a gap check.
---

<!--
GENERATED FILE: do not edit directly.
Source: .claude/ in https://github.com/nmadrid27/esf-companion, rebuilt by scripts/build-codex-plugin.py.
To customize Companion behavior, edit companion-notes.md instead.
-->

Show the current ESF project's gap snapshot. Run the aggregator in scan-only mode and relay its report. Do not fabricate; relay what the scan returns.

## Step 1: Run the scan

The aggregator owns workspace resolution, so run it first and let it tell you whether a workspace exists. From the current directory:

```
python3 <defense-pack-skill-dir>/bin/aggregate.py . --scan-only
```

This prints a JSON snapshot.

## Step 2: Check for a workspace

If the JSON output contains `"error": "no_workspace"` (or the command otherwise fails to run, e.g. no Python, missing skill), tell the user: "No ESF workspace found here. Run $esf-onboarding to set one up." and stop. Do not invent a report.

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
