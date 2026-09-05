#!/usr/bin/env bash
# Run the backlog loop with a genuinely empty context per issue.
#
# `/clear` is a client-side command: no hook output and no CLI flag can invoke
# it, so a session cannot clear itself. What it can do is exit. Each issue
# therefore gets its own `claude` process, and a process boundary is a real
# clear rather than an approximation of one.
#
# .claude/hooks/post-merge-stop.py ends a process the moment its pull request
# merges; this script starts the next one. Continuity lives in the repository —
# the open issues, evals/results/loop/LEDGER.md, master's log — not in a
# context window, which is why throwing the window away costs nothing.
#
# It exports LACONIC_LOOP_SUPERVISOR=1 into each `claude`, which is how the hook
# knows a restart is coming. Merging without it leaves the session idle, and the
# hook says so rather than printing the same message either way.
#
#   bash tools/loop.sh                  # run until stopped
#   LOOP_MAX=3 bash tools/loop.sh       # three issues, then exit
#   touch .claude/loop-stop             # finish the current issue, then exit
#
# LOOP_PERMISSION_MODE defaults to `auto`, the same mode an interactive session
# uses. A genuinely unattended overnight run wants `bypassPermissions`, which
# skips every permission check — set it deliberately, per run.
#
# **A failed iteration waits and retries; it does not end the loop.** The first
# version stopped on any non-zero exit, and on 2026-09-02 that cost twelve
# hours: iteration 3 exited 1 at 04:05 with "You've hit your session limit ·
# resets 6:20am", the supervisor stopped, and nothing restarted it after the
# reset two hours later. A usage limit is the most likely way an unattended run
# ends and it is transient, so it is the one failure the loop must survive.
# `run.py` and `judge.py` reached the same conclusion first: both stop only
# after eight *consecutive* failures, and both resume by key so a stop is free.
# This backs off 10 minutes, doubling to an hour, for LOOP_MAX_FAILURES
# consecutive failures — about six hours of cover — and resets the count on any
# iteration that finishes cleanly.
set -uo pipefail
cd "$(dirname "$0")/.."

# `bash tools/loop.sh --selftest` — drives this script against a stub `claude`.
# The bug it exists to catch shipped once: a usage limit ended the loop for
# good, and nothing in the log said the loop was gone rather than idle.
if [ "${1:-}" = "--selftest" ]; then
  tmp=$(mktemp -d) || exit 1
  trap 'rm -rf "$tmp"' EXIT
  mkdir -p "$tmp/stub"
  cat > "$tmp/stub/claude" <<'STUB'
#!/usr/bin/env bash
c=$(cat "$STUB_STATE" 2>/dev/null || echo 0); c=$((c + 1)); echo "$c" > "$STUB_STATE"
[ -n "${STUB_TOUCH:-}" ] && touch "$STUB_TOUCH"
if [ "$c" -le "${STUB_FAILS:-0}" ]; then
  # Set outside the expansion: an apostrophe inside ${x:-default} is a quote.
  msg=${STUB_MESSAGE:-}
  [ -z "$msg" ] && msg="You've hit your session limit · resets 6:20am (UTC)"
  echo "$msg"
  exit "${STUB_STATUS:-1}"
fi
echo "supervisor=${LACONIC_LOOP_SUPERVISOR:-unset}"
echo "did work (call $c)"
STUB
  chmod +x "$tmp/stub/claude"
  export PATH="$tmp/stub:$PATH" LOOP_STOP_FILE="$tmp/stop"
  export LOOP_RETRY_GAP=1 LOOP_RETRY_CAP=1 LOOP_GAP=1

  failed=0
  check() { # name, expected-grep, actual
    if printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted /%s/ in:\n%s\n' "$1" "$2" "$3"
  }

  out=$(STUB_STATE=$tmp/a STUB_FAILS=2 LOOP_MAX=1 bash "$0" 2>&1)
  check "a limit retries, then the iteration runs" 'retrying in 1s \(2/8\)' "$out"
  check "a retry is not counted as an iteration" 'did work \(call 3\)' "$out"
  # Paired with .claude/hooks/post-merge-stop.py, which reads this name to tell
  # a supervised stop from the loop quietly dying. Drift breaks the message.
  check "the supervisor marker reaches claude" 'supervisor=1' "$out"

  out=$(STUB_STATE=$tmp/b STUB_FAILS=99 LOOP_MAX_FAILURES=3 bash "$0" 2>&1)
  check "consecutive failures stop the loop" '3 consecutive failures, stopping' "$out"
  check "a limit is named as one" 'usage limit \(resets' "$out"

  out=$(STUB_STATE=$tmp/c STUB_FAILS=99 STUB_STATUS=3 \
    STUB_MESSAGE='TypeError: broke' LOOP_MAX_FAILURES=1 bash "$0" 2>&1)
  check "a real error is named by exit code" 'exit 3 — 1 consecutive' "$out"

  out=$(STUB_STATE=$tmp/d STUB_TOUCH=$tmp/stop bash "$0" 2>&1)
  check "the stop file ends the loop" 'stop present, stopping' "$out"
  [ -e "$tmp/stop" ] && { failed=$((failed + 1)); echo "FAIL stop file left behind"; }

  [ "$failed" -eq 0 ] && echo "loop.sh selftest: 7/7 passed" || echo "loop.sh selftest: $failed failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

STOP_FILE=${LOOP_STOP_FILE:-.claude/loop-stop}
MAX=${LOOP_MAX:-0}
MAX_FAILURES=${LOOP_MAX_FAILURES:-8}
RETRY_GAP=${LOOP_RETRY_GAP:-600}
RETRY_CAP=${LOOP_RETRY_CAP:-3600}

PROMPT='Work the laconic backlog: pick the highest-value open issue and take it
end to end — design, implement, test, a round document if it is a loop round,
branch, pull request, wait for CI, merge. Do exactly one issue, then stop; the
next one gets its own process and its own empty context. Never ask permission
and never offer next steps.'

transcript=$(mktemp)
trap 'rm -f "$transcript"' EXIT

rm -f "$STOP_FILE"
n=0
failures=0
backoff=$RETRY_GAP
while :; do
  if [ -e "$STOP_FILE" ]; then
    echo "loop: $STOP_FILE present, stopping"
    rm -f "$STOP_FILE"
    break
  fi
  if [ "$MAX" -gt 0 ] && [ "$n" -ge "$MAX" ]; then
    echo "loop: reached LOOP_MAX=$MAX, stopping"
    break
  fi

  printf '\n=== loop iteration %d — %s ===\n' "$((n + 1))" "$(date -Is)"

  LACONIC_LOOP_SUPERVISOR=1 \
  claude -p "$PROMPT" --permission-mode "${LOOP_PERMISSION_MODE:-auto}" \
    2>&1 | tee "$transcript"
  status=${PIPESTATUS[0]}

  if [ "$status" -eq 0 ]; then
    n=$((n + 1))
    failures=0
    backoff=$RETRY_GAP
    sleep "${LOOP_GAP:-10}"
    continue
  fi

  failures=$((failures + 1))
  # Worth distinguishing in the log: a limit is expected and self-clearing,
  # anything else is a bug someone has to read.
  if grep -qiE 'usage limit|session limit|rate limit' "$transcript"; then
    reason="usage limit ($(grep -oiE 'resets[^)]*\)?' "$transcript" | head -1))"
  else
    reason="exit $status"
  fi

  if [ "$failures" -ge "$MAX_FAILURES" ]; then
    echo "loop: $reason — $failures consecutive failures, stopping"
    break
  fi
  echo "loop: $reason — retrying in ${backoff}s ($failures/$MAX_FAILURES)"
  sleep "$backoff"
  backoff=$((backoff * 2))
  [ "$backoff" -gt "$RETRY_CAP" ] && backoff=$RETRY_CAP
done
