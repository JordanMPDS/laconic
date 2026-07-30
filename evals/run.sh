#!/usr/bin/env bash
# Two-arm eval runner. For each case, ask the same question with and without the
# laconic rules, and write both answers side by side for human review.
#
#   ./evals/run.sh [level] [case-glob]     e.g. ./evals/run.sh ultra destructive
#
# `claude plugin eval` is the eventual home for this; it is gated behind early
# access, so this stands in. Graded by reading, against evals/CRITERIA.md.
set -uo pipefail

LEVEL="${1:-full}"
GLOB="${2:-*}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/evals/scratch/$LEVEL"

case "$LEVEL" in
  lite|full|ultra) ;;
  *) printf 'usage: run.sh [lite|full|ultra] [case-glob]\n' >&2; exit 2 ;;
esac

command -v claude >/dev/null || { printf 'claude CLI not on PATH\n' >&2; exit 2; }

# Build the treatment arm's system prompt from the real hook, so the eval tests
# what ships rather than a copy that can drift.
tmp_cfg=$(mktemp -d)
printf '%s' "$LEVEL" > "$tmp_cfg/.laconic-level"
RULES=$(CLAUDE_CONFIG_DIR="$tmp_cfg" bash "$ROOT/hooks/laconic.sh" start </dev/null)
rm -rf "$tmp_cfg"
[ -n "$RULES" ] || { printf 'hook produced no rules for level %s\n' "$LEVEL" >&2; exit 1; }
RULES_CKSUM=$(printf '%s' "$RULES" | cksum | cut -d' ' -f1)

# Both arms run under CLAUDE_CODE_SAFE_MODE=1 (the env-var form of --safe-mode)
# so neither inherits the developer's own ~/.claude/CLAUDE.md or hooks —
# otherwise the "without" arm is not a control, and the "with" arm could get
# rules twice. Safe mode stops hooks from running, not environment variables,
# so LACONIC_DEFAULT is unset explicitly rather than left to safe mode to
# cover. Unlike pointing CLAUDE_CONFIG_DIR at a fresh temp dir, safe mode
# leaves auth (OAuth/keychain) working: credentials live in the real config
# dir, so a temp dir with no CLAUDE.md but also no credentials makes both arms
# fail with "Not logged in" instead of running.
export CLAUDE_CODE_SAFE_MODE=1
unset LACONIC_DEFAULT

mkdir -p "$OUT"
matched=0
for dir in "$ROOT"/evals/cases/$GLOB/; do
  [ -f "$dir/prompt.md" ] || continue
  matched=$((matched + 1))
  name=$(basename "$dir")
  prompt=$(cat "$dir/prompt.md")
  printf 'running %s (%s)...\n' "$name" "$LEVEL"

  # Run from a scratch dir, not the laconic repo: with tools on and cwd here,
  # the model discovers it's the laconic plugin repo and answers the meta-
  # situation instead of the question. (Disabling tools outright via
  # --tools "" was tried and made this worse: the model still emitted literal
  # tool-call markup as text instead of prose.) Stage the case's fixture into
  # that dir so the hypothetical is real — without it the model has nothing
  # to inspect, stalls asking for the project, and the case's trap never
  # fires.
  case_scratch=$(mktemp -d)
  [ -d "$dir/fixture" ] && cp -R "$dir/fixture/." "$case_scratch/"

  # Keep each arm's stdout as pure model prose: a rate-limit or auth error on
  # stderr must not get folded in and word-counted as if it were the answer.
  without=$(cd "$case_scratch" && printf '%s' "$prompt" | claude -p --model haiku 2>/dev/null); without_rc=$?
  [ "$without_rc" -eq 0 ] || without="ARM FAILED (rc=$without_rc)"
  with=$(cd "$case_scratch" && printf '%s' "$prompt" | claude -p --model haiku --append-system-prompt "$RULES" 2>/dev/null); with_rc=$?
  [ "$with_rc" -eq 0 ] || with="ARM FAILED (rc=$with_rc)"
  rm -rf "$case_scratch"

  {
    printf '# %s @ %s\n\n' "$name" "$LEVEL"
    printf 'Model: haiku\n'
    printf 'Run (UTC): %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'Rules checksum: %s\n\n' "$RULES_CKSUM"
    printf '## Prompt\n\n%s\n\n' "$prompt"
    printf '## Arm: without rules (%s words)\n\n%s\n\n' "$(printf '%s' "$without" | wc -w | tr -d ' ')" "$without"
    printf '## Arm: with rules (%s words)\n\n%s\n\n' "$(printf '%s' "$with" | wc -w | tr -d ' ')" "$with"
    printf '## Verdict\n\nTerseness: PASS/FAIL\nIntegrity: PASS/FAIL\nCase trap: PASS/FAIL\nNotes:\n'
  } > "$OUT/$name.md"
done

if [ "$matched" -eq 0 ]; then
  printf 'no cases matched: %s\n' "$GLOB" >&2
  exit 1
fi

printf '\nwrote %s\nGrade against evals/CRITERIA.md.\n' "$OUT"
