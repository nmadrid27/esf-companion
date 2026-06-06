#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Report unreleased commits on the current ref since the latest companion-v* tag.
# Prints "drift=<N>" then the commit list. Fail-open: always exits 0.
# Used by the release-drift workflow and runnable locally.
set -u
REF="${ESF_RELEASE_REF:-HEAD}"

latest=$(git tag -l 'companion-v*' 2>/dev/null | sort -V | tail -1)
if [ -z "$latest" ]; then
  n=$(git rev-list --count "$REF" 2>/dev/null || echo 0)
  echo "drift=$n"
  echo "(no prior companion-v* release)"
  git log --oneline "$REF" 2>/dev/null | head -50 || true
  exit 0
fi

n=$(git rev-list --count "${latest}..${REF}" 2>/dev/null || echo 0)
echo "drift=$n"
if [ "${n:-0}" -gt 0 ] 2>/dev/null; then
  echo "since ${latest}:"
  git log --oneline "${latest}..${REF}" 2>/dev/null || true
fi
exit 0
