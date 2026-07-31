#!/usr/bin/env bash
# laconic — emit the active rule set for Claude Code hooks.
# Usage: laconic.sh start|subagent|remind
#   start, subagent  print the rule slice for the active level
#   remind           persist any "/laconic <level> [project]" on stdin, print one line
# Prints nothing at all unless a valid level is active.
set -uo pipefail

MODE="${1:-}"
case "$MODE" in
  start|subagent|remind) ;;
  *) exit 0 ;;   # unknown or missing mode: do nothing rather than guess
esac

CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
GLOBAL_FLAG="$CONFIG_DIR/.laconic-level"

# The project flag lets one repository run a different level from the machine
# default. CLAUDE_PROJECT_DIR is what Claude Code exports to hooks; $PWD is the
# fallback because Claude Code spawns hooks from the project root anyway, and it
# is what the test suite and a hand-run invocation both see.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PROJECT_CONFIG_DIR="$PROJECT_DIR/.claude"
PROJECT_FLAG="$PROJECT_CONFIG_DIR/.laconic-level"

RULES="$(cd "$(dirname "$0")/.." && pwd)/rules/laconic.md"

# On UserPromptSubmit the hook payload arrives on stdin as JSON. Grep it rather
# than requiring jq, which is not present on many target machines. The match is
# anchored to the "prompt" field's opening quote so only a prompt that STARTS
# with the slash command switches the level: prose like "does /laconic off
# actually work?" must not flip it, and must never re-enable the mode after the
# user set off. "status" is absent from the alternation so it cannot be stored.
if [ "$MODE" = "remind" ]; then
  payload=$(cat)
  # Keep the whole matched span, not just the level: the optional " project"
  # suffix that selects the scope is only visible here.
  match=$(printf '%s' "$payload" \
    | grep -oE '"prompt"[[:space:]]*:[[:space:]]*"[[:space:]]*/laconic +(lite|full|ultra|off)( +project)?("|[[:space:]])' \
    | tail -1) || match=""
  switch=$(printf '%s' "$match" \
    | grep -oE '(lite|full|ultra|off)' \
    | tail -1) || switch=""
  # "project" contains none of the level words, so the extraction above is
  # unaffected by the suffix and this stays a plain substring test.
  target="$GLOBAL_FLAG"
  target_dir="$CONFIG_DIR"
  case "$match" in
    *" project"*) target="$PROJECT_FLAG"; target_dir="$PROJECT_CONFIG_DIR" ;;
  esac
  # This write precedes the read-path symlink check below, so it needs its own
  # guard: without it, /laconic ultra against a symlinked flag would write
  # through the link into an attacker-chosen file.
  if [ -n "${switch:-}" ] && [ ! -L "$target" ]; then
    mkdir -p "$target_dir" 2>/dev/null || true
    { printf '%s' "$switch" > "$target"; } 2>/dev/null || true
  fi
fi

# Resolve which flag is in force. The project flag wins so a repository can run
# a different level from the machine default, including "off".
#
# Never read through a symlinked flag. The whitelist below already stops foreign
# bytes from reaching stdout; this check's real job is the write guard above.
# Do not delete it as redundant. A symlink at either path fails closed and
# silences the plugin rather than falling through to the other one — the
# conservative direction, and the same behavior a symlinked flag had before the
# project path existed.
FLAG=""
for candidate in "$PROJECT_FLAG" "$GLOBAL_FLAG"; do
  [ -L "$candidate" ] && exit 0
  if [ -f "$candidate" ]; then FLAG="$candidate"; break; fi
done

if [ -z "$FLAG" ]; then
  # Opt-in only: with no flag and no configured default, do nothing.
  [ -n "${LACONIC_DEFAULT:-}" ] || exit 0
  # Validate before persisting. An unvalidated typo (LACONIC_DEFAULT=fulll)
  # would create a flag file the whitelist rejects forever, and because the file
  # now exists it would never be re-seeded — a silent, permanent brick.
  case "$LACONIC_DEFAULT" in
    lite|full|ultra|off) ;;
    *) exit 0 ;;
  esac
  # Seeds the machine flag only. LACONIC_DEFAULT is a per-machine preference,
  # and writing it into whichever repository happens to be open would put a file
  # in the user's working tree that they never asked for.
  mkdir -p "$CONFIG_DIR" 2>/dev/null || true
  { printf '%s' "$LACONIC_DEFAULT" > "$GLOBAL_FLAG"; } 2>/dev/null || exit 0
  FLAG="$GLOBAL_FLAG"
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
