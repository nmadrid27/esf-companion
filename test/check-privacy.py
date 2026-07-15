#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""ESF Companion privacy guard.

This is a PUBLIC repo. Personal, institutional, and third-party identifiers
must not appear in it. This scanner blocks the known classes that have leaked
before so they cannot creep back in.

Modes:
    check-privacy.py [--tree]      scan every tracked text file (CI mode)
    check-privacy.py --file PATH   scan a single file (dev-hook mode)

Exit 0 when clean; exit 1 when a forbidden identifier is found (findings on
stderr, one `path:line: [label] text` per hit).

Patterns are Python regex, matched case-insensitively. To allow a legitimate
future use (e.g. a real citation of someone named "Snyder"), add its path to
ALLOWLIST or tighten the specific pattern below. Keep this list in sync with
the memory note `repo-public-scrub-identifiers`.

Maintainer tooling: install.sh fetches shipped files by explicit name, so this
never reaches end users.
"""
import re
import subprocess
import sys

# (label, pattern, flags). Word boundaries via \b are honored by Python's re on
# every platform (unlike BSD vs GNU grep), which is why this is Python and not a
# shell one-liner. Most patterns are case-insensitive; the home-path pattern is
# case-SENSITIVE on purpose so it matches real lowercase macOS usernames
# (/Users/nathanmadrid) but NOT documentation placeholders (/Users/YourName).
PATTERNS = [
    ("SCAD institution", r"\bscad\b", re.IGNORECASE),
    ("scad.edu address", r"@scad\.edu", re.IGNORECASE),
    ("maintainer home path", r"/Users/[a-z]|-Users-[a-z]", 0),
    ("private repo ref", r"\bai-os\b", re.IGNORECASE),
    ("student name (Anderson)", r"lily anderson|anderson-lily", re.IGNORECASE),
    ("student name (Snyder)", r"\bsnyder\b|snyder[_-]cj", re.IGNORECASE),
    ("SCAD course code", r"\bAI[ _-]?(180|201)\b", re.IGNORECASE),
]

# Files that necessarily contain the patterns (the guard itself). Repo-relative.
ALLOWLIST = {
    "test/check-privacy.py",
    ".claude/hooks/dev-privacy-guard.sh",
    ".github/workflows/privacy-scan.yml",
}

COMPILED = [(label, re.compile(pat, flags)) for label, pat, flags in PATTERNS]


def scan_file(path):
    """Return a list of (lineno, label, text) findings for one file."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeDecodeError):
        return []  # unreadable or binary: nothing to scan
    hits = []
    for n, line in enumerate(lines, 1):
        for label, rx in COMPILED:
            if rx.search(line):
                hits.append((n, label, line.rstrip("\n")))
    return hits


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=False
    )
    return [p for p in out.stdout.splitlines() if p and p not in ALLOWLIST]


def main(argv):
    if len(argv) >= 2 and argv[1] == "--file":
        if len(argv) < 3:
            return 0
        target = argv[2]
        # The hook passes an absolute path; ALLOWLIST is repo-relative. Treat the
        # file as allow-listed if it equals or ends with any allowlist entry.
        allowed = any(target == a or target.endswith("/" + a) for a in ALLOWLIST)
        files = [] if allowed else [target]
    else:  # --tree / default
        files = tracked_files()

    findings = []
    for path in files:
        for lineno, label, text in scan_file(path):
            findings.append((path, lineno, label, text))

    if findings:
        sys.stderr.write(
            "Privacy guard: forbidden identifier(s) found "
            "(this is a PUBLIC repo):\n"
        )
        for path, lineno, label, text in findings:
            sys.stderr.write(f"  {path}:{lineno}: [{label}] {text.strip()[:120]}\n")
        sys.stderr.write(
            "\nRemove or generalize the identifier. If it is a legitimate use, "
            "add the path to ALLOWLIST in test/check-privacy.py.\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
