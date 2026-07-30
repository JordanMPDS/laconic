#!/usr/bin/env bash
# laconic — optional statusline badge. Opt in by adding to settings.json:
#   "statusLine": { "type": "command",
#                   "command": "bash \"$HOME/.claude/plugins/.../hooks/laconic-statusline.sh\"" }
FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level"

# Same hardening as the hook: never dereference a symlinked flag, never echo
# bytes that failed the whitelist.
[ -L "$FLAG" ] && exit 0
[ -f "$FLAG" ] || exit 0

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
