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
# It also exports CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0. A round drives run.py
# for hours through a background task, and print mode otherwise waits a default
# 600s for one, terminates it, and exits 0. On 2026-09-05 that killed iteration 1
# mid-pass at "Master tree at 39 of 80", left a half-generated snapshot in the
# tree, and the supervisor read the exit as clean and started the next issue. A
# truncated round reporting success is worse than a failed one, because the
# retry path above never sees it. 0 waits indefinitely.
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

# A usage limit names the time it clears: "resets 6:20am (UTC)". Backing off
# exponentially past a time we were told is waste — on 2026-09-05 a limit that
# reset at 12:00 was retried at 09:44, 10:04, 10:44, 11:44 and finally 12:44,
# so the loop idled 45 minutes after it could have run. Turn the stated time
# into a deadline and sleep to it instead. Empty output means "not parseable",
# and the caller keeps its exponential backoff.
limit_reset_epoch() { # <time> [tz] -> epoch on stdout
  local t=$1 tz=${2:-UTC} now target
  [ -n "$t" ] || return 1
  now=$(date +%s)
  target=$(TZ="$tz" date -d "$t" +%s 2>/dev/null) || return 1
  [ -n "$target" ] || return 1
  # A time that has already passed today is tomorrow's reset.
  if [ "$target" -le "$now" ]; then
    target=$(TZ="$tz" date -d "$t tomorrow" +%s 2>/dev/null) || return 1
    [ -n "$target" ] || return 1
  fi
  printf '%s' "$target"
}

# An iteration inherits whatever branch the last one left checked out. That is
# deliberate — a round too long for one iteration continues on its branch, which
# is how round 48 finished what round 48 started. But a branch whose work is
# already merged is not continuity, it is debris, and a fresh child with no
# memory of the merge re-opens a pull request for it: on 2026-09-06 iteration 8
# inherited `volunteered-check-116` after iteration 7 had merged it, and shipped
# PR #251 as a byte-identical duplicate of #250 that merged as an empty commit.
#
# So: tidy back to master only when the branch adds nothing to origin/master and
# the tree is clean. A round in flight fails both tests and is never touched.
branch_is_merged() {
  [ -z "$(git status --porcelain 2>/dev/null)" ] || return 1
  git rev-parse --verify -q origin/master >/dev/null 2>&1 || return 1
  git merge-base --is-ancestor HEAD origin/master 2>/dev/null
}

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
echo "bgceiling=${CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS:-unset}"
echo "did work (call $c)"
STUB
  chmod +x "$tmp/stub/claude"
  # LOOP_RESET_MAX_WAIT=0 refuses every deadline, so the stub's "resets 6:20am"
  # can never be slept to. Without it this selftest passes or hangs depending on
  # the hour it runs: before 6:20am UTC the reset is still ahead, and the run
  # sleeps to it for real. The cap itself is exercised deliberately below.
  export PATH="$tmp/stub:$PATH" LOOP_STOP_FILE="$tmp/stop" LOOP_TIDY=0 \
         LOOP_RESET_MAX_WAIT=0
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
  # Paired with the export below, for the same reason the marker is checked: a
  # round drives run.py for hours in a background task, and losing this lets
  # print mode kill the pass and still exit 0.
  check "the background-wait ceiling is lifted" 'bgceiling=0' "$out"

  out=$(STUB_STATE=$tmp/b STUB_FAILS=99 LOOP_MAX_FAILURES=3 bash "$0" 2>&1)
  check "consecutive failures stop the loop" '3 consecutive failures, stopping' "$out"
  check "a limit is named as one" 'usage limit \(resets' "$out"

  out=$(STUB_STATE=$tmp/c STUB_FAILS=99 STUB_STATUS=3 \
    STUB_MESSAGE='TypeError: broke' LOOP_MAX_FAILURES=1 bash "$0" 2>&1)
  check "a real error is named by exit code" 'exit 3 — 1 consecutive' "$out"

  # The deadline arithmetic, called directly: sleeping to a real reset in a
  # selftest is not something a test can afford to do.
  _now=$(date +%s)
  _later=$(TZ=UTC date -u -d "@$((_now + 3600))" +%-I:%M%P)
  _earlier=$(TZ=UTC date -u -d "@$((_now - 3600))" +%-I:%M%P)
  _t=$(limit_reset_epoch "$_later" UTC)
  check "a reset later today is a deadline within the hour" \
    "^1$" "$([ -n "$_t" ] && [ "$_t" -gt "$_now" ] && [ $((_t - _now)) -le 3660 ] && echo 1)"
  _t=$(limit_reset_epoch "$_earlier" UTC)
  check "a reset already past today rolls to tomorrow" \
    "^1$" "$([ -n "$_t" ] && [ $((_t - _now)) -gt 82000 ] && echo 1)"
  check "an unparseable reset yields nothing, so the caller backs off" \
    "^EMPTY$" "$(limit_reset_epoch "half past soon" UTC || echo EMPTY)"

  # A parseable reset beyond LOOP_RESET_MAX_WAIT must not be slept to.
  out=$(STUB_STATE=$tmp/e STUB_FAILS=99 LOOP_MAX_FAILURES=2 LOOP_RESET_MAX_WAIT=1 \
    STUB_MESSAGE="You've hit your session limit · resets 11:59pm (UTC)" bash "$0" 2>&1)
  check "a reset past the cap falls back to the backoff" 'retrying in 1s' "$out"

  # The guard that matters: a tree with work in it is never tidied away. The
  # merged case is not asserted here because CI checks out a detached merge ref,
  # so what "merged" means depends on the checkout rather than on the code.
  _probe=".loop-tidy-probe-$$"
  touch "$_probe"
  check "a dirty tree is never tidied" "^DIRTY$" \
    "$(branch_is_merged || echo DIRTY)"
  rm -f "$_probe"

  out=$(STUB_STATE=$tmp/d STUB_TOUCH=$tmp/stop bash "$0" 2>&1)
  check "the stop file ends the loop" 'stop present, stopping' "$out"
  [ -e "$tmp/stop" ] && { failed=$((failed + 1)); echo "FAIL stop file left behind"; }

  [ "$failed" -eq 0 ] && echo "loop.sh selftest: 13/13 passed" || echo "loop.sh selftest: $failed failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

STOP_FILE=${LOOP_STOP_FILE:-.claude/loop-stop}
MAX=${LOOP_MAX:-0}
MAX_FAILURES=${LOOP_MAX_FAILURES:-8}
RETRY_GAP=${LOOP_RETRY_GAP:-600}
RETRY_CAP=${LOOP_RETRY_CAP:-3600}

# "wait for CI" as one item in a list is a phrase a model can satisfy by saying
# it. On 2026-09-05 iteration 1 printed "PR #236 opened; CI running. Waiting on
# the checks before merging." and exited 0 without merging, leaving the pull
# request open and the issue unfinished — and the supervisor started the next
# issue, because a stopped-short iteration exits exactly like a finished one.
# So the wait is named as a blocking command rather than left as an intention.
PROMPT='Work the laconic backlog: pick the highest-value open issue and take it
end to end — design, implement, test, a round document if it is a loop round,
branch, pull request, then merge. Do exactly one issue, then stop; the next one
gets its own process and its own empty context. Never ask permission and never
offer next steps.

Waiting for CI is a command, not an intention. Run `gh pr checks <N> --watch`,
which blocks until every check has finished, and merge only after it returns.
Saying that you are waiting and then ending the turn does not wait: it abandons
the pull request open, and nothing downstream can tell that from a clean finish.
If the checks fail, fix them and wait again. The issue is not done until its
pull request is merged.'

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

  # LOOP_TIDY=0 for the selftest, which runs inside this very repository and has
  # no business moving its HEAD.
  if [ "${LOOP_TIDY:-1}" = 1 ]; then
    git fetch -q origin master 2>/dev/null
    if branch_is_merged && [ "$(git branch --show-current)" != master ]; then
      echo "loop: $(git branch --show-current) is already merged — returning to master"
      git checkout -q master 2>/dev/null && git merge --ff-only -q origin/master 2>/dev/null
    fi
  fi

  # `< /dev/null` because print mode reads stdin for piped input and waits on
  # it. An unattended supervisor is started from whatever stdin its caller
  # happened to have: on 2026-09-05 a restart handed the child a pipe nothing
  # wrote to, and every iteration opened with "no stdin data received in 3s,
  # proceeding without it". It proceeded, but a caller whose stdin stays open
  # is a hang rather than a warning, and the prompt is passed with -p anyway.
  LACONIC_LOOP_SUPERVISOR=1 \
  CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
  claude -p "$PROMPT" --permission-mode "${LOOP_PERMISSION_MODE:-auto}" \
    < /dev/null 2>&1 | tee "$transcript"
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
  wait_s=$backoff
  waited_to_reset=
  if grep -qiE 'usage limit|session limit|rate limit' "$transcript"; then
    reason="usage limit ($(grep -oiE 'resets[^)]*\)?' "$transcript" | head -1))"
    # Sleep to the time the limit named, rather than doubling blindly past it.
    reset_t=$(grep -oiE 'resets +[0-9]{1,2}(:[0-9]{2})? *[ap]m' "$transcript" \
      | head -1 | sed -E 's/^resets +//I; s/ +//g')
    reset_tz=$(grep -oE '\(([A-Z]{2,5})\)' "$transcript" | head -1 | tr -d '()')
    target=$(limit_reset_epoch "$reset_t" "${reset_tz:-UTC}") || target=
    if [ -n "$target" ]; then
      d=$((target + 60 - $(date +%s)))
      if [ "$d" -gt 0 ] && [ "$d" -le "${LOOP_RESET_MAX_WAIT:-21600}" ]; then
        wait_s=$d
        waited_to_reset=" — sleeping to the stated reset"
      fi
    fi
  else
    reason="exit $status"
  fi

  if [ "$failures" -ge "$MAX_FAILURES" ]; then
    echo "loop: $reason — $failures consecutive failures, stopping"
    break
  fi
  echo "loop: $reason — retrying in ${wait_s}s ($failures/$MAX_FAILURES)$waited_to_reset"
  sleep "$wait_s"
  backoff=$((backoff * 2))
  [ "$backoff" -gt "$RETRY_CAP" ] && backoff=$RETRY_CAP
done
