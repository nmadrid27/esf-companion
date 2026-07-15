#!/usr/bin/env python3
"""PostToolUse audit-trail hook (Mina briefing-book convention).

Appends one JSONL line per Edit, Write, or Bash action to
logs/audit-YYYY-MM.jsonl, tagging each with an autonomy tier from a config
rule table. Strictly non-fatal: any error is swallowed and the hook exits 0,
so it can never block a tool call.

Tier rules come from audit.config.json at the repo root (engine in code, rules
in config), so the hook installs into any repo unchanged. Unmatched actions
log as "unclassified". Spec: docs/design/briefing-book-convention.md.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

DEFAULT_RULES = [
    {"tool": "Write|Edit", "target": r"(^|/)(docs|logs|\.claude)/", "tier": "autonomous"},
    {"tool": "Bash", "target": r"\b(git\s+push|gh)\b", "tier": "propose-approve"},
]
DEFAULT_TIER = "unclassified"


def load_rules(root):
    try:
        with open(os.path.join(root, "audit.config.json")) as f:
            data = json.load(f)
        rules = data.get("rules")
        if isinstance(rules, list):
            return rules, data.get("default_tier", DEFAULT_TIER)
    except Exception:
        pass
    return DEFAULT_RULES, DEFAULT_TIER


def classify(tool, target, rules, default_tier):
    for rule in rules:
        try:
            if not re.search(rule.get("tool", ""), tool):
                continue
            tgt = rule.get("target", "")
            if tgt and not re.search(tgt, target):
                continue
            return rule.get("tier", default_tier)
        except Exception:
            continue
    return default_tier


def extract(payload):
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    if tool == "Bash":
        target = str(ti.get("command") or "")
    else:
        target = str(ti.get("file_path") or ti.get("notebook_path") or "")
    return tool, target


def build_entry(payload, rules, default_tier):
    tool, target = extract(payload)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": payload.get("session_id", ""),
        "tool": tool,
        "target": target,
        "tier": classify(tool, target, rules, default_tier),
        "cwd": payload.get("cwd", ""),
    }


def log_path(root):
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return os.path.join(root, "logs", "audit-{}.jsonl".format(month))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    try:
        root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
        rules, default_tier = load_rules(root)
        entry = build_entry(payload, rules, default_tier)
        path = log_path(root)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        return


if __name__ == "__main__":
    main()
