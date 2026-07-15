# 0001: Briefing convention installed

**Status:** accepted (2026-07-12)

This repo uses a briefing-book convention: a SessionStart standup (`.claude/hooks/standup.py`) that composes the session-state file, backlog, git state, and newest ADRs into one block, plus an append-only audit trail (`.claude/hooks/audit_log.py`). Both are engine-in-code with project settings in `briefing.config.json` and `audit.config.json`. These are maintainer-only dev hooks; they are not part of the distributed product and never reach end users.
