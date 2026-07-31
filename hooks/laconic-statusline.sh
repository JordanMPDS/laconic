#!/usr/bin/env bash
# laconic — optional statusline badge. The SessionStart hook installs and
# refreshes a copy of this file at a stable path, so point settings.json there
# rather than into the plugin, whose path carries a version:
#   "statusLine": { "type": "command",
#                   "command": "bash \"$HOME/.claude/laconic-statusline.sh\"" }
# Do not reference it through ${CLAUDE_PLUGIN_ROOT}: Claude Code resolves that
# variable for plugin hooks only, and a statusLine command containing it raises
# an error that is logged and swallowed, so the badge silently renders nothing.
GLOBAL_FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level"
PROJECT_FLAG="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/.laconic-level"

# Same resolution and hardening as the hook: project flag first, never
# dereference a symlinked flag, never echo bytes that failed the whitelist. The
# order has to match laconic.sh exactly — a badge that names a level the session
# is not running is worse than no badge, because the error is invisible.
FLAG=""
for candidate in "$PROJECT_FLAG" "$GLOBAL_FLAG"; do
  [ -L "$candidate" ] && exit 0
  if [ -f "$candidate" ]; then FLAG="$candidate"; break; fi
done
[ -n "$FLAG" ] || exit 0

MODE=$(head -c 16 "$FLAG" 2>/dev/null | tr -cd 'a-z')
case "$MODE" in
  lite|full|ultra) ;;
  *) exit 0 ;;
esac

COLOR=108
[ "$MODE" = "ultra" ] && COLOR=173

if [ "$MODE" = "full" ]; then
  printf '\033[38;5;%sm[LACONIC]\033[0m' "$COLOR"
else
  printf '\033[38;5;%sm[LACONIC:%s]\033[0m' "$COLOR" "$(printf '%s' "$MODE" | tr '[:lower:]' '[:upper:]')"
fi
