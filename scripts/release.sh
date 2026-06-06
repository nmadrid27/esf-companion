#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Cut an ESF Companion release.
# Usage: scripts/release.sh companion-vX.Y.Z [--dry-run]
set -euo pipefail

TAG=""; DRY_RUN=false
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=true ;;
    companion-v*) TAG="$a" ;;
    *) TAG="${TAG:-$a}" ;;
  esac
done

VERSION_FILE=".claude/esf-version"
CHANGELOG="CHANGELOG.md"
TAG_RE='^companion-v[0-9]+\.[0-9]+\.[0-9]+$'
die() { echo "release: $1" >&2; exit 1; }

# --- Guards (each fails before any mutation) ---
printf '%s' "$TAG" | grep -qE "$TAG_RE" || die "version must match companion-vX.Y.Z (got: '${TAG}')"
[ -f "$VERSION_FILE" ] || die "$VERSION_FILE not found (run from repo root)"
[ -f "$CHANGELOG" ]    || die "$CHANGELOG not found (run from repo root)"
[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || die "must be on main"
[ -z "$(git status --porcelain)" ] || die "working tree not clean"
if git rev-parse "$TAG" >/dev/null 2>&1; then die "tag $TAG already exists locally"; fi

CURRENT="$(tr -d '[:space:]' < "$VERSION_FILE")"
TOP="$(printf '%s\n%s\n' "$CURRENT" "$TAG" | sort -V | tail -1)"
if [ "$TOP" != "$TAG" ] || [ "$TAG" = "$CURRENT" ]; then die "$TAG is not strictly newer than current $CURRENT"; fi

UNREL="$(awk '/^## \[Unreleased\]/{f=1;next} /^## \[/{f=0} f' "$CHANGELOG" | grep -v '^[[:space:]]*$' || true)"
[ -n "$UNREL" ] || die "CHANGELOG [Unreleased] is empty; nothing to release"

# Network/remote guards skipped in --dry-run so tests need no remote.
if [ "$DRY_RUN" = false ]; then
  command -v gh >/dev/null 2>&1 || die "gh CLI not found"
  git fetch origin --quiet --tags
  [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || die "local main not in sync with origin/main"
  if git ls-remote --tags origin "refs/tags/$TAG" | grep -q .; then die "tag $TAG already exists on origin"; fi
fi

DATE="$(date +%F)"
NEW_CHANGELOG="$(awk -v tag="$TAG" -v date="$DATE" '
  !done && /^## \[Unreleased\]/ { print; print ""; print "## [" tag "] - " date; done=1; next }
  { print }
' "$CHANGELOG")"
NOTES="$(printf '%s\n' "$NEW_CHANGELOG" | awk -v tag="$TAG" '
  index($0, "## [" tag "]")==1 {f=1; next} /^## \[/{f=0} f')"

if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN: $CURRENT -> $TAG (date $DATE)"
  echo "--- release notes (new CHANGELOG section) ---"
  printf '%s\n' "$NOTES"
  echo "--- would: commit, push main, annotated tag $TAG, push tag, gh release create ---"
  exit 0
fi

printf '%s\n' "$TAG" > "$VERSION_FILE"
printf '%s\n' "$NEW_CHANGELOG" > "$CHANGELOG"
git add "$VERSION_FILE" "$CHANGELOG"
git commit -m "chore(release): $TAG"
git push origin main
git tag -a "$TAG" -m "ESF Companion $TAG"
git push origin "$TAG"
printf '%s\n' "$NOTES" | gh release create "$TAG" --title "ESF Companion $TAG" --notes-file -
echo "Released $TAG"
