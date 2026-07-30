#!/usr/bin/env bash
# laconic — emit the active rule set for Claude Code hooks.
# Usage: laconic.sh start|subagent|remind
#   start, subagent  print the rule slice for the active level
#   remind           persist any "/laconic <level>" on stdin, print one line
# Prints nothing at all unless a valid level is active.
set -uo pipefail

MODE="${1:-}"
case "$MODE" in
  start|subagent|remind) ;;
  *) exit 0 ;;   # unknown or missing mode: do nothing rather than guess
esac

CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
FLAG="$CONFIG_DIR/.laconic-level"
RULES="$(cd "$(dirname "$0")/.." && pwd)/rules/laconic.md"

# On UserPromptSubmit the hook payload arrives on stdin as JSON. Grep it rather
# than requiring jq, which is not present on many target machines. The match is
# anchored to the "prompt" field's opening quote so only a prompt that STARTS
# with the slash command switches the level: prose like "does /laconic off
# actually work?" must not flip it, and must never re-enable the mode after the
# user set off. "status" is absent from the alternation so it cannot be stored.
if [ "$MODE" = "remind" ]; then
  payload=$(cat)
  switch=$(printf '%s' "$payload" \
    | grep -oE '"prompt"[[:space:]]*:[[:space:]]*"[[:space:]]*/laconic +(lite|full|ultra|off)("|[[:space:]])' \
    | grep -oE '(lite|full|ultra|off)' \
    | tail -1) || switch=""
  # This write precedes the read-path symlink check below, so it needs its own
  # guard: without it, /laconic ultra against a symlinked flag would write
  # through the link into an attacker-chosen file.
  if [ -n "${switch:-}" ] && [ ! -L "$FLAG" ]; then
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    { printf '%s' "$switch" > "$FLAG"; } 2>/dev/null || true
  fi
fi

# Never read through a symlinked flag. The whitelist below already stops foreign
# bytes from reaching stdout; this check's real job is the write guard above.
# Do not delete it as redundant.
[ -L "$FLAG" ] && exit 0

if [ ! -f "$FLAG" ]; then
  # Opt-in only: with no flag and no configured default, do nothing.
  [ -n "${LACONIC_DEFAULT:-}" ] || exit 0
  # Validate before persisting. An unvalidated typo (LACONIC_DEFAULT=fulll)
  # would create a flag file the whitelist rejects forever, and because the file
  # now exists it would never be re-seeded — a silent, permanent brick.
  case "$LACONIC_DEFAULT" in
    lite|full|ultra|off) ;;
    *) exit 0 ;;
  esac
  mkdir -p "$CONFIG_DIR" 2>/dev/null || true
  { printf '%s' "$LACONIC_DEFAULT" > "$FLAG"; } 2>/dev/null || exit 0
fi

# Cap the read and strip everything outside [a-z] so malformed contents cannot
# reach the terminal or the model. The whitelist below is the real gate.
LEVEL=$(head -c 16 "$FLAG" 2>/dev/null | tr -cd 'a-z')
case "$LEVEL" in
  lite)  RANK=1 ;;
  full)  RANK=2 ;;
  ultra) RANK=3 ;;
  *)     exit 0 ;;
esac

if [ "$MODE" = "remind" ]; then
  printf 'LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.\n' "$LEVEL"
  exit 0
fi

[ -f "$RULES" ] || exit 0

# Print the shared block (rank 0) plus every block up to the active level.
awk -v want="$RANK" '
  BEGIN                    { rank = 0 }
  /^<!-- level:lite -->$/  { rank = 1; next }
  /^<!-- level:full -->$/  { rank = 2; next }
  /^<!-- level:ultra -->$/ { rank = 3; next }
  rank <= want
' "$RULES"
