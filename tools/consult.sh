#!/usr/bin/env bash
# Ask the delegate targets one question and print what they say.
#
# `delegate` is built to produce a diff: every invocation wants --branch and
# --spec, creates a worktree, and leaves a branch behind. That is the wrong
# shape for "here is the issue I am about to work, what am I missing" — the
# answer is prose, there is nothing to review, and a branch per question is
# litter. So this asks the same models directly, and none of them can edit
# anything: codex runs in a read-only sandbox, deepseek with only the read
# tools, and kimi with no tools at all (#457).
#
#   bash tools/consult.sh "why might this hypothesis not replicate?"
#   bash tools/consult.sh < question.md
#   CONSULT_TARGETS=deepseek bash tools/consult.sh "..."   # just one
#
# **It never fails the caller.** An unattended loop must not stop because a
# third-party CLI was down, so a target that is unconfigured, broken or slow is
# reported by name in the output and the run still exits 0. Silence would be
# worse than failure here: the reader has to be able to tell "nobody had a
# concern" from "nobody was asked".
#
# The launch details below mirror ~/.local/bin/delegate, which stays the source
# of truth for credentials and endpoints. Mirroring is a drift risk and the
# selftest guards it: if delegate is installed and its constants have moved,
# the selftest fails rather than this script quietly asking the wrong endpoint.
set -uo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
KEYS=${DELEGATE_KEYS:-$HOME/.config/delegate/keys.env}
KIMI_CONFIG="$HOME/.kimi-code/config.toml"
DEEPSEEK_BASE_URL="https://api.deepseek.com/anthropic"
DEEPSEEK_MODEL_DEFAULT="deepseek-v4-pro"
KIMI_MODEL_DEFAULT="kimi-code/kimi-for-coding"
# The judge's agent file, reused rather than copied: it is kimi's default
# system prompt with `tools: []`, which is exactly what a feeler needs.
KIMI_AGENT="$REPO/evals/bench/kimi-judge.md"
TIMEOUT=${CONSULT_TIMEOUT:-240}
# A feeler is meant to be read by a model that still has an issue to work. Three
# unbounded essays would spend the context the round needs, so each answer is
# truncated and the truncation is stated rather than hidden.
MAX_BYTES=${CONSULT_MAX_BYTES:-6000}

# --- availability, each with the reason it is unavailable -------------------
# Named reasons, not a boolean: "kimi did not answer" and "kimi was never asked
# because its key is a placeholder" call for different responses from a reader.
why_unavailable() { # <target> -> reason on stdout, empty when available
  case "$1" in
    codex)
      command -v codex >/dev/null || { echo "the codex binary is not on PATH"; return; }
      ;;
    deepseek)
      command -v claude >/dev/null || { echo "the claude binary is not on PATH"; return; }
      [ -f "$KEYS" ] || { echo "no keys file at $KEYS"; return; }
      # shellcheck disable=SC1090
      [ -n "$( . "$KEYS" 2>/dev/null; printf '%s' "${DEEPSEEK_API_KEY:-}" )" ] \
        || { echo "DEEPSEEK_API_KEY is unset in $KEYS"; return; }
      ;;
    kimi)
      command -v kimi >/dev/null || { echo "the kimi binary is not on PATH"; return; }
      [ -f "$KIMI_CONFIG" ] || { echo "no config at $KIMI_CONFIG"; return; }
      # The subscription, not the Moonshot API key: kimi-code/* bills the flat
      # Kimi Code plan that `kimi login` sets up, which is what delegate checks.
      grep -qF '[providers."managed:kimi-code"]' "$KIMI_CONFIG" 2>/dev/null \
        || { echo "no Kimi Code subscription in $KIMI_CONFIG (run: kimi login)"; return; }
      ;;
    *) echo "unknown target" ;;
  esac
}

ask_one() { # <target> <question> <outfile>
  local target=$1 q=$2 out=$3 scratch
  scratch=$(mktemp -d) || return 1
  case "$target" in
    codex)
      # Read-only sandbox: a feeler has no business editing anything. It runs at
      # the repository root rather than in a scratch directory for two reasons —
      # codex refuses a directory that is not a git repository ("Not inside a
      # trusted directory"), and a model that can read the code gives a better
      # answer than one reasoning from the question alone.
      ( timeout "$TIMEOUT" codex exec --skip-git-repo-check -C "$REPO" \
          -s read-only "$q" ) > "$out" 2>"$out.err" < /dev/null
      ;;
    deepseek)
      # env -u ANTHROPIC_API_KEY for delegate's reason: in -p mode a stray key
      # is always used and would bill Anthropic credits instead of DeepSeek.
      # At the repository root for codex's second reason, so it is confined by
      # flags rather than by its cwd (#457). Left alone, a -p session takes the
      # operator's settings: auto mode, Edit and Write allowed, every MCP
      # server, and every hook, one of which writes .remember/ into the cwd.
      # --tools leaves only the read tools, --strict-mcp-config loads no
      # server, and safe mode fires no hook, as in every run.py generation.
      # shellcheck disable=SC1090
      ( . "$KEYS" 2>/dev/null
        cd "$REPO" || exit 1
        timeout "$TIMEOUT" env -u ANTHROPIC_API_KEY \
          "ANTHROPIC_BASE_URL=$DEEPSEEK_BASE_URL" \
          "ANTHROPIC_AUTH_TOKEN=${DEEPSEEK_API_KEY:-}" \
          "ANTHROPIC_MODEL=${CONSULT_DEEPSEEK_MODEL:-$DEEPSEEK_MODEL_DEFAULT}" \
          CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1 CLAUDE_CODE_SAFE_MODE=1 \
          claude -p "$q" --tools "Read,Grep,Glob" --strict-mcp-config ) \
        > "$out" 2>"$out.err" < /dev/null
      ;;
    kimi)
      # A scratch cwd is not a boundary: kimi's default profile has a shell, and
      # as a judge it used it to read files outside its scratch dir (#411).
      ( cd "$scratch" \
        && timeout "$TIMEOUT" kimi -p "$q" \
             -m "${CONSULT_KIMI_MODEL:-$KIMI_MODEL_DEFAULT}" \
             --agent-file "$KIMI_AGENT" ) \
        > "$out" 2>"$out.err" < /dev/null
      ;;
  esac
  local status=$?
  rm -rf "$scratch"
  return $status
}

# --- selftest ---------------------------------------------------------------
# Drives the script against stub binaries. The bug it exists to catch is the
# one that makes a feeler worthless without looking broken: a target that is
# skipped or times out and says nothing about it, so the caller reads an empty
# section as "no concerns raised".
if [ "${1:-}" = "--selftest" ]; then
  tmp=$(mktemp -d) || exit 1
  trap 'rm -rf "$tmp"' EXIT
  mkdir -p "$tmp/stub" "$tmp/cfg"
  for b in codex kimi claude; do
    cat > "$tmp/stub/$b" <<STUB
#!/usr/bin/env bash
[ -n "\${STUB_HANG:-}" ] && sleep 30
echo "$b saw: \$* safe=\${CLAUDE_CODE_SAFE_MODE:-}"
STUB
    chmod +x "$tmp/stub/$b"
  done
  printf 'DEEPSEEK_API_KEY=stub-key\n' > "$tmp/cfg/keys.env"
  printf '[providers."managed:kimi-code"]\napi_key = ""\n' > "$tmp/kimi.toml"

  failed=0 total=0
  check() { # name, expected-grep, actual
    total=$((total + 1))
    if printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted /%s/ in:\n%s\n' "$1" "$2" "$3"
  }

  export PATH="$tmp/stub:$PATH" DELEGATE_KEYS="$tmp/cfg/keys.env"
  unset CLAUDE_CODE_SAFE_MODE  # so the safe-mode check sees the script's own
  export HOME="$tmp"  # so KIMI_CONFIG resolves under the sandbox
  mkdir -p "$tmp/.kimi-code" && cp "$tmp/kimi.toml" "$tmp/.kimi-code/config.toml"

  out=$(bash "$0" "what am I missing?" 2>&1)
  check "every configured target is asked" 'codex saw' "$out"
  check "deepseek is asked through the claude binary" 'claude saw' "$out"
  check "kimi is asked" 'kimi saw' "$out"
  check "the question reaches the target" 'what am I missing\?' "$out"
  check "each answer is attributed" '^## deepseek' "$out"
  # #457: a feeler reads and never edits. Each target's confinement has to reach
  # the binary, because the operator's own settings are what apply otherwise.
  check "deepseek gets only the read tools" 'claude saw: .*--tools Read,Grep,Glob( |$)' "$out"
  check "deepseek loads no MCP server" 'claude saw: .*--strict-mcp-config' "$out"
  check "deepseek runs no hook" 'claude saw: .* safe=1$' "$out"
  check "kimi runs with the no-tools agent file" \
    "kimi saw: .*--agent-file $KIMI_AGENT( |\$)" "$out"
  check "the kimi agent file exists and lists no tools" '^tools: \[\]$' \
    "$(cat "$KIMI_AGENT" 2>/dev/null)"

  # A config without the subscription must be named, not silently dropped: a
  # reader has to tell "no concerns" from "never asked".
  printf 'api_key = "stub"\n' > "$tmp/.kimi-code/config.toml"
  out=$(bash "$0" "q" 2>&1)
  check "a missing subscription is reported by name" 'no Kimi Code subscription' "$out"
  check "a skipped target is still listed" '^## kimi' "$out"
  cp "$tmp/kimi.toml" "$tmp/.kimi-code/config.toml"

  # An absent credential is a skip with a reason, never a crash.
  out=$(DELEGATE_KEYS="$tmp/nonexistent" bash "$0" "q" 2>&1)
  check "a missing keys file is named" 'no keys file' "$out"

  # The loop must survive a hung third party.
  out=$(STUB_HANG=1 CONSULT_TIMEOUT=1 bash "$0" "q" 2>&1)
  check "a hung target is reported, not waited on" 'did not answer' "$out"
  bash "$0" "q" >/dev/null 2>&1
  check "a run with every target failing still exits 0" '^0$' \
    "$(STUB_HANG=1 CONSULT_TIMEOUT=1 bash "$0" "q" >/dev/null 2>&1; echo $?)"

  out=$(CONSULT_TARGETS=deepseek bash "$0" "q" 2>&1)
  check "CONSULT_TARGETS narrows the fan-out" '^## deepseek' "$out"
  total=$((total + 1))
  if printf '%s' "$out" | grep -q '^## codex'; then
    failed=$((failed + 1)); echo "FAIL CONSULT_TARGETS still asked codex"
  fi

  # Long answers are truncated so a feeler cannot eat the round's context.
  cat > "$tmp/stub/claude" <<'STUB'
#!/usr/bin/env bash
head -c 20000 /dev/zero | tr '\0' 'x'
STUB
  chmod +x "$tmp/stub/claude"
  out=$(CONSULT_TARGETS=deepseek CONSULT_MAX_BYTES=100 bash "$0" "q" 2>&1)
  check "a long answer is truncated and says so" 'truncated at 100 bytes' "$out"

  # The drift guard: delegate owns the endpoints, this script mirrors them.
  d=$(command -v delegate || true)
  if [ -n "$d" ]; then
    for pair in "DEEPSEEK_BASE_URL=$DEEPSEEK_BASE_URL" \
                "DEEPSEEK_MODEL_DEFAULT=$DEEPSEEK_MODEL_DEFAULT" \
                "KIMI_MODEL_DEFAULT=$KIMI_MODEL_DEFAULT"; do
      total=$((total + 1))
      grep -qF "${pair%%=*}=\"${pair#*=}\"" "$d" \
        || { failed=$((failed + 1))
             echo "FAIL delegate no longer defines $pair — this script has drifted" ; }
    done
  else
    echo "note: delegate not installed, endpoint drift not checked"
  fi

  [ "$failed" -eq 0 ] && echo "consult.sh selftest: $total/$total passed" \
                      || echo "consult.sh selftest: $failed of $total failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

# --- run --------------------------------------------------------------------
question=${1:-}
[ -n "$question" ] || question=$(cat)
if [ -z "${question//[[:space:]]/}" ]; then
  echo "consult.sh: no question given (argument or stdin)" >&2
  exit 2
fi

targets=${CONSULT_TARGETS:-codex deepseek kimi}
work=$(mktemp -d) || exit 1
trap 'rm -rf "$work"' EXIT

for t in $targets; do
  reason=$(why_unavailable "$t")
  if [ -n "$reason" ]; then
    printf 'SKIPPED: %s\n' "$reason" > "$work/$t"
    continue
  fi
  ( ask_one "$t" "$question" "$work/$t.raw" \
      && mv "$work/$t.raw" "$work/$t" \
      || { printf 'NOANSWER: did not answer within %ss, or exited non-zero\n' \
             "$TIMEOUT" > "$work/$t"
           # The reason is on stderr, which is where these CLIs put their
           # refusals, and it is the whole value of a failed feeler.
           for ev in "$work/$t.raw.err" "$work/$t.raw"; do
             [ -s "$ev" ] && { head -c 500 "$ev" >> "$work/$t"; break; }
           done; } ) &
done
wait

echo "# Consultation"
echo
echo "Asked: $question"
echo
answered=0
for t in $targets; do
  echo "## $t"
  echo
  if [ ! -f "$work/$t" ]; then
    echo "_No output file — the target never ran._"
  elif head -1 "$work/$t" | grep -q '^SKIPPED: '; then
    echo "_Not asked: $(sed -n '1s/^SKIPPED: //p' "$work/$t")._"
  elif head -1 "$work/$t" | grep -q '^NOANSWER: '; then
    echo "_Asked but silent: $(sed -n '1s/^NOANSWER: //p' "$work/$t")._"
    tail -n +2 "$work/$t" | sed 's/^/    /'
  else
    answered=$((answered + 1))
    size=$(wc -c < "$work/$t")
    head -c "$MAX_BYTES" "$work/$t"
    [ "$size" -gt "$MAX_BYTES" ] \
      && printf '\n\n_[truncated at %s bytes of %s]_\n' "$MAX_BYTES" "$size"
  fi
  echo
done
echo "---"
echo "$answered of $(set -- $targets; echo $#) targets answered."
exit 0
