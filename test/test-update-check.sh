#!/usr/bin/env bash
# Hermetic tests for esf-update-check.sh. No network (ESF_UPDATE_LATEST seam).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$HERE/../.claude/hooks/esf-update-check.sh"
PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); }
bad()  { FAIL=$((FAIL+1)); echo "FAIL: $1"; }
check(){ if eval "$2"; then ok; else bad "$1"; fi; }

newtmp() { mktemp -d "${TMPDIR:-/tmp}/esfupd.XXXXXX"; }

# --- resolve: prints local + latest, validates injected tag ---
T=$(newtmp); echo "companion-v0.9.1" > "$T/esf-version"
out=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
      ESF_UPDATE_LATEST="companion-v0.10.0" bash "$HELPER" resolve)
check "resolve prints local"  '[[ "$out" == *"local=companion-v0.9.1"* ]]'
check "resolve prints latest" '[[ "$out" == *"latest=companion-v0.10.0"* ]]'

# --- invalid injected tag is rejected (no latest emitted) ---
out=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
      ESF_UPDATE_LATEST="cowork-v1.0.0" bash "$HELPER" resolve)
check "invalid latter rejected" '[[ "$out" != *"latest=cowork"* ]]'

# --- exit code is always 0 (fail-open) ---
ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/nope" bash "$HELPER" resolve >/dev/null 2>&1
check "resolve exits 0 even with missing version file" '[ $? -eq 0 ]'

rm -rf "$T"

# --- refresh writes latest_tag + last_checked, no network ---
T=$(newtmp); echo "companion-v0.9.1" > "$T/esf-version"
ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
  ESF_UPDATE_LATEST="companion-v0.10.0" bash "$HELPER" refresh
check "refresh wrote latest_tag" 'grep -q "^latest_tag=companion-v0.10.0$" "$T/cache"'
check "refresh wrote last_checked" 'grep -q "^last_checked=[0-9][0-9]*$" "$T/cache"'

# --- refresh preserves an existing last_notified ---
printf 'last_notified=companion-v0.9.1\n' >> "$T/cache"
ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
  ESF_UPDATE_LATEST="companion-v0.11.0" bash "$HELPER" refresh
# last_checked is recent now, so a second refresh is throttled; force by zeroing it:
sed -i.bak 's/^last_checked=.*/last_checked=0/' "$T/cache"; rm -f "$T/cache.bak"
ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
  ESF_UPDATE_LATEST="companion-v0.11.0" bash "$HELPER" refresh
check "refresh preserved last_notified" 'grep -q "^last_notified=companion-v0.9.1$" "$T/cache"'

# --- throttle: recent last_checked means no rewrite ---
T2=$(newtmp); printf 'latest_tag=companion-v0.9.1\nlast_checked=%s\n' "$(date +%s)" > "$T2/cache"
ESF_UPDATE_CACHE="$T2/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" \
  ESF_UPDATE_LATEST="companion-v0.10.0" bash "$HELPER" refresh
check "throttle: latest_tag unchanged when recent" 'grep -q "^latest_tag=companion-v0.9.1$" "$T2/cache"'
rm -rf "$T" "$T2"

# --- status: nudges when latest newer + not notified; silent on repeat ---
T=$(newtmp); echo "companion-v0.9.1" > "$T/esf-version"
printf 'latest_tag=companion-v0.10.0\nlast_checked=%s\n' "$(date +%s)" > "$T/cache"
err=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" bash "$HELPER" status 2>&1 1>/dev/null)
check "status nudges" '[[ "$err" == *"update available: companion-v0.9.1 -> companion-v0.10.0"* ]]'
check "status set last_notified" 'grep -q "^last_notified=companion-v0.10.0$" "$T/cache"'
err=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" bash "$HELPER" status 2>&1 1>/dev/null)
check "status silent on repeat" '[ -z "$err" ]'

# --- downgrade guard: local newer than latest -> silent ---
T=$(newtmp); echo "companion-v0.11.0" > "$T/esf-version"
printf 'latest_tag=companion-v0.10.0\n' > "$T/cache"
err=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" bash "$HELPER" status 2>&1 1>/dev/null)
check "no downgrade nudge" '[ -z "$err" ]'

# --- non-matching local tag -> silent (never nag on odd state) ---
T=$(newtmp); echo "companion-v0.11.0-dev" > "$T/esf-version"
printf 'latest_tag=companion-v0.10.0\n' > "$T/cache"
err=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" bash "$HELPER" status 2>&1 1>/dev/null)
check "non-matching local silent" '[ -z "$err" ]'

# --- status-readonly nudges but does NOT write last_notified ---
T=$(newtmp); echo "companion-v0.9.1" > "$T/esf-version"
printf 'latest_tag=companion-v0.10.0\n' > "$T/cache"
err=$(ESF_UPDATE_CACHE="$T/cache" ESF_UPDATE_VERSION_FILE="$T/esf-version" bash "$HELPER" status-readonly 2>&1 1>/dev/null)
check "readonly nudges" '[[ "$err" == *"update available"* ]]'
check "readonly did not write last_notified" '! grep -q "^last_notified=" "$T/cache"'
rm -rf "$T"

echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
