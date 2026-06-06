#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# ESF Companion update check. Single source of truth for update detection.
# Shared by the SessionStart hook, /esf-update, and /esf-status.
# Fail-open: always exits 0. ASCII only. Portable (bash 3.2, no jq/flock/setsid).
set -u

CACHE="${ESF_UPDATE_CACHE:-$HOME/.claude/.esf-update-check}"
VERSION_FILE="${ESF_UPDATE_VERSION_FILE:-.claude/esf-version}"
THROTTLE_SECONDS=86400
TAG_RE='^companion-v[0-9]+\.[0-9]+\.[0-9]+$'
TAGS_API="https://api.github.com/repos/nmadrid27/esf-companion/tags?per_page=100"

_valid_tag() { printf '%s' "${1:-}" | grep -qE "$TAG_RE"; }

_read_local_tag() {
  if [ -f "$VERSION_FILE" ]; then tr -d '[:space:]' < "$VERSION_FILE"; else echo "none"; fi
}

# _newer A B -> exit 0 if B is strictly newer than A (version-sort)
_newer() {
  [ "$1" = "$2" ] && return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -1)" = "$2" ]
}

_cache_get() {  # _cache_get key  -> prints value or returns 1
  [ -f "$CACHE" ] || return 1
  local line; line=$(grep -E "^$1=" "$CACHE" 2>/dev/null | head -1) || return 1
  [ -n "$line" ] || return 1
  printf '%s' "${line#*=}"
}

_cache_set() {  # _cache_set key=val [key=val ...]  (atomic merge: keep other keys)
  local tmp; tmp=$(mktemp "${CACHE}.XXXXXX" 2>/dev/null) || { mkdir -p "$(dirname "$CACHE")"; tmp=$(mktemp "${CACHE}.XXXXXX") || return 1; }
  [ -f "$CACHE" ] && cat "$CACHE" >> "$tmp" 2>/dev/null
  local kv key
  for kv in "$@"; do
    key="${kv%%=*}"
    grep -vE "^${key}=" "$tmp" > "${tmp}.n" 2>/dev/null || true
    mv "${tmp}.n" "$tmp" 2>/dev/null || true
    echo "$kv" >> "$tmp"
  done
  mkdir -p "$(dirname "$CACHE")"
  mv "$tmp" "$CACHE" 2>/dev/null || rm -f "$tmp"
}

_resolve_latest() {  # prints a validated latest tag, or returns 1
  if [ -n "${ESF_UPDATE_LATEST:-}" ]; then
    _valid_tag "$ESF_UPDATE_LATEST" && { printf '%s' "$ESF_UPDATE_LATEST"; return 0; }
    return 1
  fi
  local resp tag
  resp=$(curl -fsSL --max-time 6 --connect-timeout 3 "$TAGS_API" 2>/dev/null) || return 1
  tag=$(printf '%s' "$resp" | grep -oE 'companion-v[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
  _valid_tag "$tag" && { printf '%s' "$tag"; return 0; }
  return 1
}

cmd_resolve() {
  local local_tag latest
  local_tag="$(_read_local_tag)"
  echo "local=$local_tag"
  latest="$(_resolve_latest)" && echo "latest=$latest"
}

cmd_refresh() {
  local last_checked now latest
  now=$(date +%s)
  last_checked="$(_cache_get last_checked 2>/dev/null || echo 0)"
  case "$last_checked" in (*[!0-9]*|'') last_checked=0 ;; esac
  if [ -f "$CACHE" ] && [ $((now - last_checked)) -lt "$THROTTLE_SECONDS" ]; then
    return 0
  fi
  latest="$(_resolve_latest)" || return 0   # fail-open: leave cache untouched
  _cache_set "latest_tag=$latest" "last_checked=$now"
}

cmd_status() {  # $1: "readonly" to skip the last_notified write
  local local_tag latest notified
  local_tag="$(_read_local_tag)"
  _valid_tag "$local_tag" || return 0          # none / dev / suffixed -> never nudge
  latest="$(_cache_get latest_tag)" || return 0
  _valid_tag "$latest" || return 0
  _newer "$local_tag" "$latest" || return 0    # strict-above only; no downgrade nudge
  notified="$(_cache_get last_notified 2>/dev/null || echo '')"
  [ "$notified" = "$latest" ] && return 0
  printf '\nESF Companion update available: %s -> %s. Run /esf-update to see what changed and install.\n\n' \
    "$local_tag" "$latest" >&2
  [ "${1:-}" = "readonly" ] || _cache_set "last_notified=$latest"
}

cmd_changelog() {  # $1=OLD $2=NEW
  local old="$1" new="$2" text
  if [ -n "${ESF_UPDATE_CHANGELOG_FILE:-}" ]; then
    text="$(cat "$ESF_UPDATE_CHANGELOG_FILE" 2>/dev/null)" || return 0
  else
    _valid_tag "$new" || return 0
    text="$(curl -fsSL --max-time 6 --connect-timeout 3 \
      "https://raw.githubusercontent.com/nmadrid27/esf-companion/$new/CHANGELOG.md" 2>/dev/null)" || return 0
  fi
  # Print each '## [companion-vX.Y.Z]' section whose version is in (old, new].
  printf '%s\n' "$text" | awk -v old="$old" -v new="$new" '
    function vget(line,   v) { v=line; sub(/^## \[/,"",v); sub(/\].*/,"",v); return v }
    function inrange(v,   arr) {
      if (v !~ /^companion-v[0-9]+\.[0-9]+\.[0-9]+$/) return 0
      # v > old  AND  v <= new, via external sort -V comparisons
      cmd1="printf \x27%s\\n%s\\n\x27 \x27" old "\x27 \x27" v "\x27 | sort -V | tail -1"
      cmd1 | getline top1; close(cmd1)
      cmd2="printf \x27%s\\n%s\\n\x27 \x27" v "\x27 \x27" new "\x27 | sort -V | tail -1"
      cmd2 | getline top2; close(cmd2)
      return (top1==v && v!=old) && (top2==new || v==new)
    }
    /^## \[/ { keep = inrange(vget($0)) }
    keep { print }
  '
}

main() {
  case "${1:-status}" in
    status)          cmd_status ;;
    status-readonly) cmd_status readonly ;;
    resolve)         cmd_resolve ;;
    refresh)         cmd_refresh ;;
    changelog)       cmd_changelog "${2:-}" "${3:-}" ;;
    *) : ;;
  esac
  return 0
}

# Source-safe: only run when executed directly.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then main "$@"; fi
exit 0
