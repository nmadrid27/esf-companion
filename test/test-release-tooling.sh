#!/usr/bin/env bash
# Hermetic tests for the release tooling. No network, no real push.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
DRIFT="$REPO/scripts/release-drift.sh"
RELEASE="$REPO/scripts/release.sh"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); }
bad() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }
check(){ if eval "$2"; then ok; else bad "$1"; fi; }

# A throwaway git repo with deterministic identity.
mkrepo() {
  local d; d=$(mktemp -d "${TMPDIR:-/tmp}/esfrel.XXXXXX")
  git -C "$d" init -q
  git -C "$d" config user.email t@t; git -C "$d" config user.name t
  git -C "$d" commit -q --allow-empty -m "init"
  echo "$d"
}

# --- drift: 2 commits after a tag ---
D=$(mkrepo)
git -C "$D" tag -a companion-v0.1.0 -m x
git -C "$D" commit -q --allow-empty -m "feat: a"
git -C "$D" commit -q --allow-empty -m "fix: b"
out=$(cd "$D" && bash "$DRIFT")
check "drift=2 after two commits" '[[ "$(printf "%s" "$out" | head -1)" == "drift=2" ]]'
check "drift lists a commit" '[[ "$out" == *"feat: a"* ]]'

# --- drift=0 at the tag ---
out=$(cd "$D" && ESF_RELEASE_REF=companion-v0.1.0 bash "$DRIFT")
check "drift=0 at tag" '[[ "$(printf "%s" "$out" | head -1)" == "drift=0" ]]'

# --- no tags: reports all-history without error ---
D2=$(mkrepo)
out=$(cd "$D2" && bash "$DRIFT"); rc=$?
check "no-tags exits 0" '[ "$rc" -eq 0 ]'
check "no-tags reports drift" '[[ "$(printf "%s" "$out" | head -1)" == drift=* ]]'
rm -rf "$D" "$D2"

# Build a repo that looks like the real one for release.sh (--dry-run only).
mkrelrepo() {  # $1 = current version, $2 = unreleased-has-content (yes/no)
  local d; d=$(mktemp -d "${TMPDIR:-/tmp}/esfrelr.XXXXXX")
  git -C "$d" init -q -b main
  git -C "$d" config user.email t@t; git -C "$d" config user.name t
  mkdir -p "$d/.claude"; printf '%s\n' "$1" > "$d/.claude/esf-version"
  if [ "$2" = "yes" ]; then
    printf '# Changelog\n\n## [Unreleased]\n\n### Added\n- a new thing\n\n## [%s] - 2026-01-01\n- old\n' "$1" > "$d/CHANGELOG.md"
  else
    printf '# Changelog\n\n## [Unreleased]\n\n## [%s] - 2026-01-01\n- old\n' "$1" > "$d/CHANGELOG.md"
  fi
  git -C "$d" add -A; git -C "$d" commit -q -m "init"
  echo "$d"
}
run_rel() { ( cd "$1" && shift && bash "$RELEASE" "$@" ); }  # $1=repo, rest=args

# --- rejects malformed version ---
D=$(mkrelrepo companion-v0.10.0 yes)
run_rel "$D" not-a-tag --dry-run >/dev/null 2>&1
check "rejects malformed version" '[ $? -ne 0 ]'

# --- rejects non-newer version ---
run_rel "$D" companion-v0.9.0 --dry-run >/dev/null 2>&1
check "rejects older version" '[ $? -ne 0 ]'

# --- rejects empty [Unreleased] ---
D2=$(mkrelrepo companion-v0.10.0 no)
run_rel "$D2" companion-v0.11.0 --dry-run >/dev/null 2>&1
check "rejects empty Unreleased" '[ $? -ne 0 ]'

# --- valid --dry-run: no writes, correct preview ---
out=$(run_rel "$D" companion-v0.11.0 --dry-run 2>&1); rc=$?
check "dry-run exits 0" '[ "$rc" -eq 0 ]'
check "dry-run previews new version" '[[ "$out" == *"companion-v0.10.0 -> companion-v0.11.0"* ]]'
check "dry-run shows the new section content" '[[ "$out" == *"a new thing"* ]]'
check "dry-run made no commit" '[ "$(git -C "$D" rev-list --count HEAD)" -eq 1 ]'
check "dry-run did not touch esf-version" '[ "$(cat "$D/.claude/esf-version")" = "companion-v0.10.0" ]'
rm -rf "$D" "$D2"

echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
