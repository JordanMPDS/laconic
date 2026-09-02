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

**Do not detect the merge from `gh` output.** `gh pr merge` writes its "✓
Squashed and merged pull request #N" confirmation only when stderr is a
terminal. Under an agent's shell tool it is not, and the command prints
nothing whatsoever — the first version of this hook matched that wording and
so never fired even once. The tool payload carries no exit status either
(`stdout`, `stderr`, `interrupted`, `isImage`, `noOutputExpected`), so the
merge has to be confirmed by asking GitHub.

Reads the PostToolUse payload on stdin.
"""

import json
import re
import subprocess
import sys

# `#123`, `123`, or a trailing `/123` from a full PR URL.
PR_NUM = re.compile(r"(?:^|/)#?(\d+)$")

# Only used when stderr *is* a terminal, which is the interactive case.
MERGED_TEXT = re.compile(r"merged pull request", re.I)


def pr_number(command):
    """The PR `gh pr merge` was pointed at, or None for 'the current branch'."""
    tail = command.split("gh pr merge", 1)[1] if "gh pr merge" in command else ""
    for token in tail.split():
        if token.startswith("-"):
            continue
        if token in {"|", "&&", "||", ";", "2>&1"}:
            break
        match = PR_NUM.search(token)
        return match.group(1) if match else None
    return None


def is_merged(number):
    """Ask GitHub. The only reliable signal available to this hook."""
    argv = ["gh", "pr", "view"]
    if number:
        argv.append(number)
    argv += ["--json", "state", "--jq", ".state"]
    try:
        done = subprocess.run(
            argv, capture_output=True, text=True, timeout=20, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0 and done.stdout.strip() == "MERGED"


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

    # `--auto` queues the merge behind required checks. Nothing has landed, and
    # asking GitHub would just say OPEN, but skip the call and be explicit.
    if re.search(r"(?<!\S)--auto(?!\S)", command):
        return 0

    output = f"{response.get('stdout', '')}\n{response.get('stderr', '')}"
    if not MERGED_TEXT.search(output) and not is_merged(pr_number(command)):
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
    nothing in the transcript says so. That is not hypothetical — it is how
    the first version of this file shipped, matching `gh` output that a
    non-TTY shell never produces. So these drive `main()` itself, with GitHub
    stubbed, rather than re-checking a copy of its conditions.
    """
    import io

    # (command, stdout, interrupted, merged-per-github, should fire)
    cases = [
        # The real case: gh prints nothing at all under a non-TTY shell.
        ("gh pr merge 193 --squash --delete-branch", "", False, True, True),
        ("gh pr merge 193 -s --delete-branch 2>&1 | tail -4", "", False, True, True),
        ("gh pr merge --squash", "", False, True, True),
        ("gh pr merge https://github.com/o/r/pull/12 -s", "", False, True, True),
        ("gh pr merge 7 --squash", "", False, False, False),   # merge refused
        ("gh pr merge 5 --auto -s", "", False, True, False),   # queued, not merged
        ("gh pr merge 9 -s", "", True, True, False),           # interrupted
        ("git status", "", False, True, False),
        ("gh pr view 3", "MERGED", False, True, False),
        # A terminal did print the confirmation: fire without asking GitHub.
        ("gh pr merge 8 -s", "✓ Squashed and merged pull request #8",
         False, False, True),
    ]

    numbers = [
        ("gh pr merge 193 --squash", "193"),
        ("gh pr merge #193 --squash", "193"),
        ("gh pr merge https://github.com/o/r/pull/12 -s", "12"),
        ("gh pr merge --squash --delete-branch", None),
        ("gh pr merge -s 42", "42"),
    ]

    def run(payload):
        """Feed one payload through main(), returning whether it emitted."""
        stdin_was, stdout_was = sys.stdin, sys.stdout
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        try:
            main()
            return sys.stdout.getvalue().strip() != ""
        finally:
            sys.stdin, sys.stdout = stdin_was, stdout_was

    real_is_merged = is_merged
    failed = 0
    try:
        for command, stdout, interrupted, merged, want in cases:
            globals()["is_merged"] = lambda _n, m=merged: m
            got = run(json.dumps({
                "tool_input": {"command": command},
                "tool_response": {"stdout": stdout, "stderr": "",
                                  "interrupted": interrupted},
            }))
            if got != want:
                failed += 1
                print(f"FAIL want={want} got={got}: {command!r}")

        globals()["is_merged"] = lambda _n: True
        if run("not json"):
            failed += 1
            print("FAIL malformed payload fired")
    finally:
        globals()["is_merged"] = real_is_merged

    for command, want in numbers:
        got = pr_number(command)
        if got != want:
            failed += 1
            print(f"FAIL pr_number want={want!r} got={got!r}: {command!r}")

    total = len(cases) + len(numbers) + 1
    print(f"{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
