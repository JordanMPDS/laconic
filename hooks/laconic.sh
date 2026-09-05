#!/usr/bin/env bash
# laconic — emit the active rule set for Claude Code hooks.
# Usage: laconic.sh start|remind|switch
#   start   print the rule slice for the active level
#   remind  persist any "/laconic <level> [project]" on stdin, print one line
#   switch  persist the same switch and acknowledge it by refusing the turn,
#           for a hook system with no per-turn injection (#16). Prints nothing
#           at all when the prompt is not a switch.
# Prints nothing at all unless a valid level is active.
#
# Output is raw text by default, which is what Claude Code consumes. Setting
# LACONIC_JSON_PATH to a dotted key path wraps that text as JSON instead, for
# hook systems that read a field rather than stdout:
#
#   LACONIC_JSON_PATH=hookSpecificOutput.additionalContext   # Gemini CLI (#13)
#
# The path is a parameter rather than a fixed shape because the platforms do not
# agree on where the field lives — Codex and Copilot nest it differently (#14,
# #15). Unset or empty means the raw path, byte for byte, so nothing about the
# Claude Code behaviour moves. Switch mode ignores it: what that mode emits is a
# fixed object with two fields rather than a rule slice at a caller's key path.
#
# There is deliberately no subagent mode. laconic exists to make a response
# pleasant and cheap for a person to read, and nobody reads a subagent's report
# — it goes to the parent model. evals/results/2026-07-31-subagent.md measured
# the path before it was cut: accuracy was unchanged in every arm (p = 1.000)
# while the injected slice raised the cost of a subagent call by 6-16%, so the
# hook was paying for a benefit with no consumer. See issue #6.
set -uo pipefail

MODE="${1:-}"
case "$MODE" in
  start|remind|switch) ;;
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
if [ "$MODE" = "remind" ] || [ "$MODE" = "switch" ]; then
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
  applied=""
  # This write precedes the read-path symlink check below, so it needs its own
  # guard: without it, /laconic ultra against a symlinked flag would write
  # through the link into an attacker-chosen file.
  if [ -n "${switch:-}" ] && [ ! -L "$target" ]; then
    mkdir -p "$target_dir" 2>/dev/null || true
    { printf '%s' "$switch" > "$target"; } 2>/dev/null || true
    # Read the flag back rather than trusting the redirect, whose status the
    # guard above deliberately discards. Only switch mode uses this, and its
    # acknowledgment is a claim that the level is on disk: a write that failed,
    # or one refused because the flag is a symlink, must not produce one.
    if [ "$(head -c 16 "$target" 2>/dev/null | tr -cd 'a-z')" = "$switch" ]; then
      applied="$switch"
    fi
  fi
fi

# switch mode ends here, before the level whitelist, because the one switch that
# most needs acknowledging is "off" — and past this point an inactive level is
# silence by design.
#
# Cursor's beforeSubmitPrompt is the only per-turn hook laconic can reach there
# and it injects nothing: it reads `continue`, and a `user_message` shown to the
# user only when the submission is blocked. So the one thing that event can do
# is refuse the /laconic turn and say what happened. That beats writing the flag
# silently — a switch nothing confirms is a weaker form of the silent no-op #2
# exists to eliminate, and under Cursor the new level genuinely does not take
# effect until the next session, which is the part a user has to be told.
#
# Anything that is not a switch prints nothing, and an empty stdout blocks
# nothing. The blast radius of this mode is exactly the prompts that begin
# "/laconic lite|full|ultra|off".
if [ "$MODE" = "switch" ]; then
  [ -n "${applied:-}" ] || exit 0
  scope=""
  case "$match" in *" project"*) scope=" for this project" ;; esac
  printf '{"continue":false,"user_message":"laconic: level set to %s%s. Cursor delivers the rules at session start, so open a new chat for it to take effect."}\n' \
    "$applied" "$scope"
  exit 0
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

# Emit on stdout: raw when LACONIC_JSON_PATH is unset or empty, otherwise the
# same bytes as a JSON string nested at that dotted path.
#
# The escaping is the failure mode raw stdout never had. The rule slice contains
# double quotes, backslashes and newlines on every level, so a wrapper that only
# handled quotes would ship malformed JSON the moment a rule mentioned `\n` or a
# quoted example. awk does it here rather than jq, which is not a dependency this
# project has, or python, which a shell hook has no business requiring.
laconic_emit() {
  if [ -z "${LACONIC_JSON_PATH:-}" ]; then
    cat
    return
  fi
  awk -v path="$LACONIC_JSON_PATH" '
    function esc(s,   out, i, c, n) {
      out = ""
      n = length(s)
      for (i = 1; i <= n; i++) {
        c = substr(s, i, 1)
        if      (c == "\\") out = out "\\\\"
        else if (c == "\"")  out = out "\\\""
        else if (c == "\b")  out = out "\\b"
        else if (c == "\f")  out = out "\\f"
        else if (c == "\n")  out = out "\\n"
        else if (c == "\r")  out = out "\\r"
        else if (c == "\t")  out = out "\\t"
        else if (c < " ")     out = out sprintf("\\u%04x", index(CTRL, c) - 1)
        else                  out = out c
      }
      return out
    }
    BEGIN {
      CTRL = ""
      for (i = 0; i < 32; i++) CTRL = CTRL sprintf("%c", i)
      body = ""
    }
    { body = body (NR > 1 ? "\n" : "") $0 }
    END {
      n = split(path, key, ".")
      pre = ""; post = ""
      for (i = 1; i <= n; i++) { pre = pre "{\"" esc(key[i]) "\":"; post = post "}" }
      printf "%s\"%s\"%s\n", pre, esc(body), post
    }
  '
}

if [ "$MODE" = "remind" ]; then
  printf 'LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.\n' "$LEVEL" | laconic_emit
  exit 0
fi

# Keep the statusline badge installed at a stable, version-free path.
#
# Claude Code reads "statusLine" from settings only — a plugin cannot register
# one, and a statusLine command referencing ${CLAUDE_PLUGIN_ROOT} is rejected
# and swallowed, so the badge would silently render nothing. Wiring it up is
# therefore always one manual edit to settings.json. What the plugin can do is
# own the script, so the user's settings point at a path that never carries a
# version and never goes stale.
#
# Only on start, only while a level is active, and never fatal: this exists to
# save the user a copy-paste, so it must not be able to break the rule slice
# below. A symlinked target is refused for the same reason the flag file is.
if [ "$MODE" = "start" ]; then
  BADGE_SRC="$(dirname "$0")/laconic-statusline.sh"
  BADGE_DST="$CONFIG_DIR/laconic-statusline.sh"
  if [ -f "$BADGE_SRC" ] && [ ! -L "$BADGE_DST" ] && ! cmp -s "$BADGE_SRC" "$BADGE_DST"; then
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    { cp "$BADGE_SRC" "$BADGE_DST"; } >/dev/null 2>&1 || true
  fi
fi

[ -f "$RULES" ] || exit 0

# Print the shared block (rank 0) plus every block up to the active level.
awk -v want="$RANK" '
  BEGIN                    { rank = 0 }
  /^<!-- level:lite -->$/  { rank = 1; next }
  /^<!-- level:full -->$/  { rank = 2; next }
  /^<!-- level:ultra -->$/ { rank = 3; next }
  rank <= want
' "$RULES" | laconic_emit
