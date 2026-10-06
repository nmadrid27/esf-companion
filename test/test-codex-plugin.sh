#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Codex plugin guard: platforms/codex must match what the generator builds from
# .claude/, carry no Claude-only constructs, and install via install.sh.
# Usage: bash test/test-codex-plugin.sh
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
fail=0
check() { if "$@" >/dev/null 2>&1; then echo "PASS: $DESC"; else echo "FAIL: $DESC"; fail=1; fi; }

DESC="platforms/codex is current"; check python3 scripts/build-codex-plugin.py --check
DESC="manifest version matches .claude/esf-version"
check python3 - <<'PY'
import json
v = open(".claude/esf-version").read().strip().removeprefix("companion-v")
assert json.load(open("platforms/codex/.codex-plugin/plugin.json"))["version"] == v
PY
DESC="marketplace points at platforms/codex"
check grep -q '"./platforms/codex"' .agents/plugins/marketplace.json
DESC="no Claude-only tool or hook references in shipped text"
check bash -c "! grep -rn -E 'AskUserQuestion|CLAUDE\.md|hooks/|esf-update' platforms/codex --include=*.md"
DESC="every skill has a SKILL.md"
check bash -c 'for s in esf-cognitive esf-defense-pack esf-git esf-onboarding esf-project esf-status esf-verify; do test -f platforms/codex/skills/$s/SKILL.md || exit 1; done'

DESC="session hook emits valid additionalContext JSON"
check bash -c "d=\$(mktemp -d) && mkdir \$d/esf && printf -- '- **Project name:** p\\n- **Context:** C\\n' > \$d/esf/companion-state.md && cd \$d && bash '$ROOT/platforms/codex/hooks/esf-session-status.sh' | python3 -c 'import json,sys; assert \"ESF Companion active\" in json.load(sys.stdin)[\"hookSpecificOutput\"][\"additionalContext\"]'"
DESC="manifest wires hooks/hooks.json"
check grep -q '"hooks": "./hooks/hooks.json"' platforms/codex/.codex-plugin/plugin.json

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
( cd "$tmp" && git init -q && bash "$ROOT/install.sh" --force --platform codex --source "$ROOT" )
DESC="codex install writes the AGENTS.md ambient block once"
check bash -c "cd '$tmp' && bash '$ROOT/install.sh' --force --platform codex --source '$ROOT' && [ \$(grep -c 'ESF Companion (Always On)' AGENTS.md) = 1 ]"
DESC="codex install leaves no .claude/ or .codex/"
check bash -c "cd '$tmp' && [ ! -d .claude ] && [ ! -d .codex ]"
exit $fail
