# Releasing the ESF Companion

Installs resolve to the latest `companion-vX.Y.Z` **tag**, not `main`. Work merged
to `main` does not reach anyone until a release is cut.

## Check for unreleased work

```bash
bash scripts/release-drift.sh
```

Prints `drift=N` and the commits since the latest tag. CI also runs this on every
push to `main` (and weekly) and keeps a single "Release pending" issue (label
`release`) open until you release; it self-closes when drift returns to 0.

## Cut a release

```bash
scripts/release.sh companion-vX.Y.Z --dry-run   # preview first
scripts/release.sh companion-vX.Y.Z             # then for real
```

The script guards (on `main`, clean tree, synced with origin, version strictly
newer, tag not taken, `[Unreleased]` non-empty), then bumps `.claude/esf-version`,
dates the CHANGELOG `[Unreleased]` section (adding a fresh empty one), commits,
pushes, creates the annotated tag, and publishes the GitHub release from that
section.

Version convention: minor bump for new features, patch for fixes.

After releasing, users get it via `/esf-update` (or it is nudged at session start
on installs that have the update-check hook).

## If a release half-completes

`release.sh` does the irreversible steps last (push main, then tag, then GitHub
release). If it pushes the version-bump commit but fails before tagging (e.g. a
network blip), `.claude/esf-version` is already at the new tag, so re-running
`release.sh` refuses with "not strictly newer." Finish by hand from the pushed
bump commit:

```bash
TAG=companion-vX.Y.Z
git tag -a "$TAG" -m "ESF Companion $TAG"
git push origin "$TAG"
awk -v t="$TAG" 'index($0,"## ["t"]")==1{f=1;next} /^## \[/{f=0} f' CHANGELOG.md \
  | gh release create "$TAG" --title "ESF Companion $TAG" --notes-file -
```
