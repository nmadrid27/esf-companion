#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the Codex plugin (platforms/codex) from the Claude Code sources.

The Claude Code tree (.claude/skills, .claude/agents, .claude/reference, and the
ambient block in install.sh) is the single source of truth. This script copies it
into a Codex plugin and rewrites the few Claude-only constructs. Every rewrite
must match exactly once; a miss means the source drifted, so the build fails
instead of shipping a skill that points at nothing.

    python3 scripts/build-codex-plugin.py          # write platforms/codex
    python3 scripts/build-codex-plugin.py --check  # exit 1 if it is stale
"""
import argparse
import filecmp
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "platforms" / "codex"
SKILLS = ["esf-cognitive", "esf-defense-pack", "esf-git", "esf-onboarding",
          "esf-project", "esf-status", "esf-verify"]
REFERENCES = ["esf-guide.md", "disclosure-protocol.md", "evolution-protocol.md"]
BANNER = ("<!--\nGENERATED FILE: do not edit directly.\n"
          "Source: .claude/ in https://github.com/nmadrid27/esf-companion, "
          "rebuilt by scripts/build-codex-plugin.py.\n"
          "To customize Companion behavior, edit companion-notes.md instead.\n-->")
CARD = ("present a numbered-choice card in chat (Codex has no selection-card tool) "
        "and wait for the user's reply")
SKILL_RE = "|".join(SKILLS)


def sub(text, pattern, repl, name, count=1, flags=0):
    new, n = re.subn(pattern, repl, text, flags=flags)
    if n < count:
        sys.exit(f"build-codex-plugin: rewrite '{name}' matched {n}x, expected >= {count}; source drifted")
    return new


def common(text, where):
    text = sub(text, r"<!--\nMANAGED FILE.*?-->", BANNER, f"{where} banner", flags=re.S)
    text = re.sub(rf"(?<![\w/.-])/({SKILL_RE})\b", r"$\1", text)
    return text


def skill_md(name, text):
    text = common(text, name)
    # Frontmatter: Codex reads name and description only.
    text = re.sub(r"^(allowed-tools|disable-model-invocation):.*\n", "", text, flags=re.M)
    text = text.replace("`.claude/reference/", "`references/")
    text = text.replace("writes inside `.claude/`", "writes inside the plugin directory")
    text = text.replace("No `.claude/` file mutation is needed", "No plugin file mutation is needed")
    text = text.replace("Do not edit `.claude/agents/esf-companion.md` for personalization or session state",
                        "Do not edit `references/companion.md` for personalization or session state")
    text = text.replace("Do not edit reference files (`references/`): those are read-only",
                        "Do not edit the plugin's reference files: they are read-only")
    if name == "esf-project":
        text = sub(text, r"call `AskUserQuestion`", CARD, "esf-project card", count=2)
        text = sub(text, r"Use the Glob tool to look for", "Use file search (`rg --files` or `find`) to look for", "esf-project glob")
        text = sub(text, r"silently use the Edit or Write tool to", "silently write with the shell or `apply_patch` to", "esf-project write")
        text = sub(text, r"Do not use Bash to probe fallback locations\.", "Do not probe locations beyond the lookup order.", "esf-project probe")
        text = sub(text, r"- `references/esf-guide\.md`", "- `references/esf-guide.md`", "esf-project refs")
    if name == "esf-status":
        text = sub(text, r"## Update check \(read-only\)\n.*?(?=## Step 1)", "", "esf-status update check", flags=re.S)
    if name == "esf-defense-pack":
        text = sub(text, r"\.claude/skills/esf-defense-pack/bin/",
                   "<skill-dir>/bin/", "defense-pack bin", count=2)
        text = sub(text, r"(\n# [^\n]+\n)", r"\1\n> `<skill-dir>` is the directory that contains this SKILL.md. Run the "
                   "scripts with `python3` using that absolute path.\n", "defense-pack note", flags=0)
    if name == "esf-status":
        text = text.replace(".claude/skills/esf-defense-pack/bin/aggregate.py",
                            "python3 <defense-pack-skill-dir>/bin/aggregate.py")
    if name == "esf-onboarding":
        text = sub(text, r"\| Agent \+ skills \(full experience\) \| Yes \| No \| No \| Partial \|",
                   "| Agent + skills (full experience) | Yes | No | No | Yes (plugin) |", "onboarding table")
    return text


def persona(text):
    text = common(text, "persona")
    text = re.sub(r"^model:.*\n", "", text, flags=re.M)
    text = sub(text, r"\*\*1\. Version check\.\*\*.*?\n\n", "**1. Version check.** Skipped on Codex: the plugin updates through "
               "`codex plugin marketplace upgrade`.\n\n", "persona version check", flags=re.S)
    text = text.replace("`.claude/`", "the plugin directory")
    text = text.replace("`.claude/reference/", "`references/")
    text = sub(text, r"- `/esf-update`: check and apply Companion updates\n", "", "persona esf-update line")
    text = text.replace("the same format used for ★ Insight sharing throughout Claude Code", "the ★ insight format")
    text = re.sub(r"call `AskUserQuestion`", CARD, text)
    text = sub(text, r"Do not use Bash to probe for alternates\.", "Do not probe locations beyond the lookup order.", "persona probe")
    return text


def ambient():
    src = (ROOT / "install.sh").read_text()
    m = re.search(r"<< 'ESF_AMBIENT_EOF'\n(.*?)\nESF_AMBIENT_EOF", src, re.S)
    if not m:
        sys.exit("build-codex-plugin: ambient block not found in install.sh")
    block = m.group(1).replace("`.claude/agents/esf-companion.md`",
                               "the `esf-project` skill (`references/companion.md`)")
    block = re.sub(r"call `AskUserQuestion`", CARD, block)
    return re.sub(rf"(?<![\w/.-])/({SKILL_RE})\b", r"$\1", block) + "\n"


def build(out):
    version = (ROOT / ".claude" / "esf-version").read_text().strip().removeprefix("companion-v")
    (out / ".codex-plugin").mkdir(parents=True)
    (out / ".codex-plugin" / "plugin.json").write_text(json.dumps({
        "name": "esf-companion",
        "version": version,
        "description": "ESF Companion: a toolkit for AI-assisted work that keeps the user the author of their own thinking.",
        "author": {"name": "Nathan Madrid"},
        "homepage": "https://github.com/nmadrid27/esf-companion",
        "license": "MIT",
        "skills": "./skills/",
        "interface": {
            "displayName": "ESF Companion",
            "shortDescription": "Stay the author of your own thinking while working with AI.",
            "developerName": "Nathan Madrid",
            "category": "Education",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": ["Set up ESF for this project.", "Show my ESF project status.",
                              "Help me start my project."],
        },
    }, indent=2) + "\n")
    for name in SKILLS:
        src, dst = ROOT / ".claude" / "skills" / name, out / "skills" / name
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "MANIFEST.txt"))
        (dst / "SKILL.md").write_text(skill_md(name, (src / "SKILL.md").read_text()))
    refs = out / "skills" / "esf-project" / "references"
    refs.mkdir(exist_ok=True)
    for r in REFERENCES:
        (refs / r).write_text(common((ROOT / ".claude" / "reference" / r).read_text(), r))
    (refs / "companion.md").write_text(persona((ROOT / ".claude" / "agents" / "esf-companion.md").read_text()))
    (out / "ambient-block.md").write_text(ambient())


def same(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(same(a / d, b / d) for d in cmp.common_dirs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "codex"
        fresh.mkdir()
        build(fresh)
        if args.check:
            if OUT.is_dir() and same(fresh, OUT):
                return
            sys.exit("platforms/codex is stale: run python3 scripts/build-codex-plugin.py")
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.copytree(fresh, OUT)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
