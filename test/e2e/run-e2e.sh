#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion end-to-end test harness.
#
# Runs each scenario in scenarios/ against a fresh install of the plugin
# from the local repo checkout. Scenarios assert against the transcript
# returned by `claude -p` and the workspace filesystem state after.
#
# Usage: bash test/e2e/run-e2e.sh
#
# Exit 0: all scenarios pass.
# Exit 1: one or more scenarios fail.

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
E2E_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_BASE="/tmp/esf-e2e"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if ! command -v claude >/dev/null 2>&1; then
  echo -e "${RED}Error:${NC} 'claude' CLI not found on PATH."
  echo "Install Claude Code (https://claude.com/claude-code) to run end-to-end tests."
  exit 1
fi

mkdir -p "$TMP_BASE"

echo ""
echo -e "${CYAN}ESF Companion end-to-end tests${NC}"
echo "────────────────────────────────────────────────────────────"
echo "Repo:       $REPO_ROOT"
echo "Workspace:  $TMP_BASE"
echo "Claude CLI: $(claude --version 2>&1 | head -1 || echo "unknown")"

TOTAL=0
PASSED=0
FAILED_SCENARIOS=()

for scenario in "$E2E_DIR/scenarios/"*.sh; do
  [ -f "$scenario" ] || continue
  name=$(basename "$scenario" .sh)
  workspace="$TMP_BASE/$name"

  echo ""
  echo -e "${CYAN}─── Scenario: $name ───${NC}"

  rm -rf "$workspace"
  mkdir -p "$workspace"

  TOTAL=$((TOTAL + 1))
  if bash "$scenario" "$workspace" "$REPO_ROOT"; then
    echo -e "  ${GREEN}PASS${NC}: $name"
    PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}FAIL${NC}: $name"
    echo -e "  ${YELLOW}Workspace preserved at:${NC} $workspace"
    FAILED_SCENARIOS+=("$name")
  fi
done

echo ""
echo "────────────────────────────────────────────────────────────"
if [ "$TOTAL" -eq 0 ]; then
  echo -e "${YELLOW}No scenarios found in $E2E_DIR/scenarios/${NC}"
  exit 1
fi

echo "Results: $PASSED / $TOTAL passed"

if [ ${#FAILED_SCENARIOS[@]} -gt 0 ]; then
  echo -e "${RED}Failed scenarios:${NC}"
  for s in "${FAILED_SCENARIOS[@]}"; do
    echo "  - $s"
  done
  echo "────────────────────────────────────────────────────────────"
  exit 1
fi

echo -e "${GREEN}All scenarios passed.${NC}"
echo "────────────────────────────────────────────────────────────"
