#!/usr/bin/env python3
"""Session-standup generator (Mina briefing-book convention).

Composes existing project stores into one standup block: the top entries of
the session-state file, open backlog items, git state, and the newest ADRs.
Read-only over every source; a missing or malformed source is skipped, never
fatal, so session start is never blocked.

Modes: --print (default) markdown to stdout; --write render into the
briefing file (docs/BRIEFING.md, gitignored); --hook emit SessionStart
additionalContext JSON.

All paths come from briefing.config.json at the repo root, so this script
installs into any repo unchanged (engine in code, project in config). Spec:
docs/design/briefing-book-convention.md.
"""
import argparse
import json
import os
import re
import subprocess
from datetime import date

DEFAULTS = {
    "project": "",
    "state_file": "",
    "state_mode": "entries",
    "state_entries": 2,
    "state_head_lines": 40,
    "backlog_file": "",
    "backlog_sections": [],
    "adr_dir": "",
    "adr_count": 2,
    "briefing_file": "docs/BRIEFING.md",
    "git_commits": 3,
}


def _safe_int(cfg, key):
    try:
        return int(cfg.get(key, DEFAULTS[key]))
    except (TypeError, ValueError):
        return int(DEFAULTS[key])


def load_config(root):
    cfg = dict(DEFAULTS)
    try:
        with open(os.path.join(root, "briefing.config.json")) as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def _resolve(root, path):
    path = os.path.expanduser(path)
    return path if os.path.isabs(path) else os.path.join(root, path)


def parse_state_entries(text, limit):
    """Parse '## YYYY-MM-DD -- Title' entries with Status / NEXT ACTION bullets."""
    entries = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^## (\S+) -- (.+)$", line)
        if m:
            if current is not None:
                entries.append(current)
                if len(entries) >= limit:
                    return entries
            current = {"date": m.group(1), "title": m.group(2),
                       "status": "", "next_action": ""}
        elif current is not None:
            s = re.match(r"^- \*\*Status:\*\* (.*)$", line)
            if s:
                current["status"] = s.group(1)
            n = re.match(r"^- \*\*NEXT ACTION:\*\* (.*)$", line)
            if n:
                current["next_action"] = n.group(1)
    if current is not None and len(entries) < limit:
        entries.append(current)
    return entries


def state_block(cfg, root):
    if not cfg.get("state_file"):
        return None
    try:
        with open(_resolve(root, cfg["state_file"])) as f:
            text = f.read()
    except Exception:
        return None
    if cfg.get("state_mode", "entries") == "head":
        lines = text.splitlines()[: _safe_int(cfg, "state_head_lines")]
        return {"mode": "head", "text": "\n".join(lines)}
    return {"mode": "entries",
            "entries": parse_state_entries(text, _safe_int(cfg, "state_entries"))}


def parse_backlog(text, sections):
    """Items under each '## <section>' heading until '---' or the next '## '."""
    out = {}
    for section in sections:
        items, inblock = [], False
        for line in text.splitlines():
            if line.startswith("## "):
                inblock = line[3:].strip() == section
                continue
            if inblock and line.startswith("---"):
                inblock = False
            elif inblock and line.startswith("- ") and "(none" not in line.lower():
                items.append(re.sub(r"^- \[.\] |^- ", "", line).strip())
        out[section] = items
    return out


def git_summary(root, commit_count):
    def run(args):
        try:
            r = subprocess.run(["git", "-C", root] + args,
                               capture_output=True, text=True, timeout=10)
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    porcelain = run(["status", "--porcelain"])
    log = run(["log", f"-{commit_count}", "--format=%ad %s", "--date=short"])
    return {
        "branch": branch,
        "dirty_count": len([l for l in porcelain.splitlines() if l.strip()]),
        "commits": [l for l in log.splitlines() if l.strip()],
    }


def latest_adrs(adr_dir, count):
    if count <= 0:
        return []
    try:
        names = sorted(n for n in os.listdir(adr_dir) if n.endswith(".md"))
        return list(reversed(names[-count:]))
    except Exception:
        return []


def render_markdown(cfg, state, backlog, git, adrs):
    name = cfg.get("project") or os.path.basename(os.getcwd())
    lines = [f"# Standup: {name}",
             f"_Generated {date.today().isoformat()} by standup.py; regenerate, do not edit._",
             ""]
    if git.get("branch"):
        lines.append(f"**Git:** branch `{git['branch']}`, "
                     f"{git['dirty_count']} uncommitted change(s)")
        lines.extend(f"- {c}" for c in git.get("commits", []))
        lines.append("")
    if state and state["mode"] == "entries" and state["entries"]:
        lines.append("## Where we left off")
        for e in state["entries"]:
            lines.append(f"### {e['date']}: {e['title']}")
            if e["status"]:
                lines.append(f"- Status: {e['status']}")
            if e["next_action"]:
                lines.append(f"- **Next action:** {e['next_action']}")
        lines.append("")
    elif state and state["mode"] == "head":
        lines.append("## State file (head)")
        lines.append(state["text"])
        lines.append("")
    for section, items in (backlog or {}).items():
        if items:
            lines.append(f"## Backlog: {section} ({len(items)})")
            lines.extend(f"- {i}" for i in items)
            lines.append("")
    if adrs:
        lines.append("## Newest decisions (ADRs)")
        lines.extend(f"- {a}" for a in adrs)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def hook_json(md):
    return json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": md,
        }
    })


def compose(root):
    cfg = load_config(root)
    state = state_block(cfg, root)
    backlog = {}
    if cfg.get("backlog_file"):
        try:
            with open(_resolve(root, cfg["backlog_file"])) as f:
                backlog = parse_backlog(f.read(), cfg.get("backlog_sections", []))
        except Exception:
            backlog = {}
    git = git_summary(root, _safe_int(cfg, "git_commits"))
    adrs = latest_adrs(_resolve(root, cfg["adr_dir"]),
                       _safe_int(cfg, "adr_count")) if cfg.get("adr_dir") else []
    return render_markdown(cfg, state, backlog, git, adrs)


def main():
    parser = argparse.ArgumentParser(description="Generate the session standup.")
    parser.add_argument("--print", action="store_true",
                        help="output markdown to stdout (default)")
    parser.add_argument("--write", action="store_true",
                        help="render into the briefing file")
    parser.add_argument("--hook", action="store_true",
                        help="emit SessionStart additionalContext JSON")
    args = parser.parse_args()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    md = compose(root)
    if args.hook:
        print(hook_json(md))
    elif args.write:
        cfg = load_config(root)
        target = _resolve(root, cfg["briefing_file"])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f:
            f.write(md)
        print(f"wrote {target}")
    else:
        print(md)


if __name__ == "__main__":
    main()
