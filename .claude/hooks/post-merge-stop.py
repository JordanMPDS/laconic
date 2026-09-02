#!/usr/bin/env python3
"""PostToolUse/Bash hook: end the turn as soon as a pull request merges.

`/clear` is a client-side command. No hook output field can invoke it — the
recognised fields are `continue`, `stopReason`, `suppressOutput`,
`systemMessage`, `decision`, `reason` and `hookSpecificOutput`, and none of
them touches the conversation history. The only real way to start the next
issue on an empty context is to end the process and start another one.

This hook supplies the "end" half. Under `tools/loop.sh` that stop is what
makes the supervisor spawn a fresh `claude`, which is a true clear. Run
interactively it just stops cleanly at the right moment, and you type `/clear`
yourself.

Reads the PostToolUse payload on stdin: `.tool_input.command` and
`.tool_response.{stdout,stderr,interrupted}`.
"""

import json
import re
import sys

# `gh pr merge` prints its confirmation to stderr, so a command that redirects
# with `2>&1 | tail -n` leaves only the last line — usually the branch
# deletion. Accept either marker. "will be automatically merged" (`--auto`)
# matches neither, which is correct: nothing has merged yet.
MERGED = re.compile(r"merged pull request|deleted branch", re.I)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if "gh pr merge" not in command:
        return 0

    response = payload.get("tool_response", {})
    if response.get("interrupted"):
        return 0

    output = f"{response.get('stdout', '')}\n{response.get('stderr', '')}"
    if not MERGED.search(output):
        return 0

    json.dump(
        {
            "continue": False,
            "stopReason": (
                "Pull request merged. Stopping so the next issue starts on an "
                "empty context — tools/loop.sh restarts from here, or run "
                "/clear and carry on."
            ),
            "systemMessage": (
                "Merged. Context stop: state lives in the open issues, "
                "evals/results/loop/LEDGER.md and master's log, not in this "
                "window."
            ),
        },
        sys.stdout,
    )
    return 0


def selftest() -> int:
    """`python3 .claude/hooks/post-merge-stop.py --selftest`

    A hook that stops firing fails silently: the loop simply never clears, and
    nothing in the transcript says so. These cases pin the `gh` output wording
    the detection depends on.
    """

    def fires(command, stdout="", stderr="", interrupted=False):
        return bool(
            "gh pr merge" in command
            and not interrupted
            and MERGED.search(f"{stdout}\n{stderr}")
        )

    cases = [
        # (should fire, command, stdout, stderr, interrupted)
        (True, "gh pr merge 192 --squash --delete-branch", "",
         "✓ Squashed and merged pull request #192 (fix)\n"
         "✓ Deleted branch fix-192", False),
        (True, "gh pr merge 3 --merge", "",
         "✓ Merged pull request #3 (title)", False),
        # `2>&1 | tail -1` keeps only the branch line.
        (True, "gh pr merge 178 --squash --delete-branch 2>&1|tail -1",
         "✓ Deleted branch feat-178", "", False),
        # --auto queues; nothing has merged.
        (False, "gh pr merge 5 --auto --squash", "",
         "✓ Pull request #5 will be automatically merged when all "
         "requirements are met", False),
        (False, "gh pr merge 7 --squash", "",
         "X Pull request #7 is not mergeable", False),
        (False, "gh pr merge 9 --squash",
         "✓ Squashed and merged pull request #9", "", True),
        (False, "git status", "clean", "", False),
        (False, "gh pr view 3", "MERGED pull request", "", False),
    ]

    failed = 0
    for want, command, stdout, stderr, interrupted in cases:
        got = fires(command, stdout, stderr, interrupted)
        if got != want:
            failed += 1
            print(f"FAIL want={want} got={got}: {command!r}")
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
