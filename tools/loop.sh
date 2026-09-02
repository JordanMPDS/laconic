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
#   bash tools/loop.sh                  # run until stopped
#   LOOP_MAX=3 bash tools/loop.sh       # three issues, then exit
#   touch .claude/loop-stop             # finish the current issue, then exit
#
# LOOP_PERMISSION_MODE defaults to `auto`, the same mode an interactive session
# uses. A genuinely unattended overnight run wants `bypassPermissions`, which
# skips every permission check — set it deliberately, per run.
set -uo pipefail
cd "$(dirname "$0")/.."

STOP_FILE=.claude/loop-stop
MAX=${LOOP_MAX:-0}

PROMPT='Work the laconic backlog: pick the highest-value open issue and take it
end to end — design, implement, test, a round document if it is a loop round,
branch, pull request, wait for CI, merge. Do exactly one issue, then stop; the
next one gets its own process and its own empty context. Never ask permission
and never offer next steps.'

rm -f "$STOP_FILE"
n=0
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

  n=$((n + 1))
  printf '\n=== loop iteration %d — %s ===\n' "$n" "$(date -Is)"

  claude -p "$PROMPT" --permission-mode "${LOOP_PERMISSION_MODE:-auto}"
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "loop: claude exited $status, stopping"
    break
  fi

  sleep "${LOOP_GAP:-10}"
done
