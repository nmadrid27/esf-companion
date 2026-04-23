#!/usr/bin/env bash
# ESF Companion status line for Claude Code
# Shows: cwd, model, context %, git branch, ESF context/phase, rate limits
#
# Note: uses ASCII separators only. macOS ships Bash 3.2, which has a bug
# where multibyte UTF-8 characters (e.g. U+00B7 middle dot) corrupt the
# preceding variable content in double-quoted string assignments.

# Exit silently if this project has been moved or ESF was uninstalled.
[ -f ".claude/esf-version" ] || exit 0

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
cwd="${cwd/#$HOME/~}"

model=$(echo "$input" | jq -r '.model.display_name // ""')

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

branch=$(git -C "${cwd/#\~/$HOME}" --no-optional-locks branch --show-current 2>/dev/null)

session_name=$(echo "$input" | jq -r '.session_name // empty')

five_hour=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_day=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

parts=()

[ -n "$cwd" ]      && parts+=("$cwd")
[ -n "$model" ]    && parts+=("$model")
[ -n "$used_pct" ] && parts+=("ctx:$(printf '%.0f' "$used_pct")%")
[ -n "$branch" ]   && parts+=("[$branch]")

# ESF Companion: read context + phase from companion-state.md.
# Check esf/ first (current), then context/ and projects/_esf/ (legacy).
base_dir="${cwd/#\~/$HOME}"
companion_state=""
for candidate in \
    "$base_dir/esf/companion-state.md" \
    "$base_dir/context/companion-state.md" \
    "$base_dir/projects/_esf/companion-state.md"; do
    if [ -f "$candidate" ]; then
        companion_state="$candidate"
        break
    fi
done

if [ -n "$companion_state" ]; then
    esf_context=$(grep "^\- \*\*Context:\*\*" "$companion_state" | sed 's/.*\*\*Context:\*\* //')
    esf_phase=$(grep "^\- \*\*Phase:\*\*" "$companion_state" | sed 's/.*\*\*Phase:\*\* //')
    if [ -n "$esf_context" ] && [ "$esf_context" != "not set" ]; then
        esf_str="ESF:${esf_context}"
        [ -n "$esf_phase" ] && [ "$esf_phase" != "not set" ] && esf_str="${esf_str}:${esf_phase}"
    else
        esf_str="ESF:active"
    fi
    parts+=("$esf_str")
fi

[ -n "$session_name" ] && parts+=('"'"$session_name"'"')

rate_parts=()
[ -n "$five_hour" ] && rate_parts+=("5h:$(printf '%.0f' "$five_hour")%")
[ -n "$seven_day" ] && rate_parts+=("7d:$(printf '%.0f' "$seven_day")%")
[ ${#rate_parts[@]} -gt 0 ] && parts+=("${rate_parts[*]}")

(IFS=' | '; printf '%s' "${parts[*]}")
