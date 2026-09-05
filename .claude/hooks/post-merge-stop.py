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

**The stop is only half a loop, so it says which half is missing.**
`tools/loop.sh` exports `LACONIC_LOOP_SUPERVISOR=1` into the `claude` it
spawns; without it, nothing is going to start the next issue and the stop
leaves the session idle rather than working. That is not hypothetical. On
2026-09-04 the backlog was being driven by Claude Code's built-in `/loop`,
which stays alive by calling `ScheduleWakeup` as the last action of a turn.
This hook ends the turn first, so the `/loop` iteration that merged PR #231
never scheduled its successor, and the loop sat dead for five and a half hours
with nothing in the transcript distinguishing that from working. Every
successful iteration ends in a merge, so under `/loop` the first one is fatal.

**A command that mentions a merged pull request has not merged one.** This
hook sees the whole Bash command text, quoted heredocs and JSON payloads
included, and there is no reliable way to tell an executed `gh pr merge` from a
quoted one by reading the string. On 2026-09-05 it fired twice within twenty
minutes on commands that merged nothing: a `gh pr create` whose body quoted a
timeline of earlier merges, and a test payload carrying a merge command inside
a JSON string. Under `tools/loop.sh` a false stop ends an iteration mid-work.
So the question it asks GitHub is not "is this pull request merged" but "was it
merged just now" — see `MERGE_WINDOW` and `is_fresh`.

**Do not detect the merge from `gh` output.** `gh pr merge` writes its "✓
Squashed and merged pull request #N" confirmation only when stderr is a
terminal. Under an agent's shell tool it is not, and the command prints
nothing whatsoever — the first version of this hook matched that wording and
so never fired even once. The tool payload carries no exit status either
(`stdout`, `stderr`, `interrupted`, `isImage`, `noOutputExpected`), so the
merge has to be confirmed by asking GitHub.

Reads the PostToolUse payload on stdin.
"""

import datetime
import json
import os
import re
import subprocess
import sys

# `#123`, `123`, or a trailing `/123` from a full PR URL.
PR_NUM = re.compile(r"(?:^|/)#?(\d+)$")

# Only used when stderr *is* a terminal, which is the interactive case.
MERGED_TEXT = re.compile(r"merged pull request", re.I)

# How recently a pull request must have merged for this command to be what
# merged it. A real merge is confirmed within seconds; anything older is the
# command naming a pull request rather than merging one. Symmetric, so a
# GitHub timestamp slightly ahead of the local clock still counts.
MERGE_WINDOW = 120


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


def is_fresh(stamp, now=None):
    """Did this merge happen just now, or is the command naming an old one?"""
    if not stamp:
        return False
    try:
        merged_at = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return abs((now - merged_at).total_seconds()) <= MERGE_WINDOW


def merged_just_now(number):
    """Ask GitHub. The only reliable signal available to this hook."""
    argv = ["gh", "pr", "view"]
    if number:
        argv.append(number)
    argv += ["--json", "state,mergedAt"]
    try:
        done = subprocess.run(
            argv, capture_output=True, text=True, timeout=20, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if done.returncode != 0:
        return False
    try:
        info = json.loads(done.stdout)
    except (json.JSONDecodeError, ValueError):
        return False
    return info.get("state") == "MERGED" and is_fresh(info.get("mergedAt"))


def supervised():
    """Is something going to start the next issue after this stop?"""
    return os.environ.get("LACONIC_LOOP_SUPERVISOR") == "1"


def stop_reason():
    if supervised():
        return (
            "Pull request merged. Stopping so the next issue starts on an "
            "empty context; tools/loop.sh restarts from here."
        )
    return (
        "Pull request merged, and this turn ends here. No loop supervisor is "
        "running, so nothing will start the next issue: this session is now "
        "idle, not working. Run `bash tools/loop.sh` to work the backlog "
        "unattended, or `/clear` and carry on by hand. Claude Code's built-in "
        "`/loop` cannot drive this repository — it stays alive by calling "
        "ScheduleWakeup as the last action of a turn, and this hook ends the "
        "turn first, so a `/loop` iteration that merges never schedules its "
        "successor."
    )


def system_message():
    if supervised():
        return (
            "Merged. Context stop: state lives in the open issues, "
            "evals/results/loop/LEDGER.md and master's log, not in this "
            "window."
        )
    return (
        "Merged, and the loop is now idle: no supervisor is running to start "
        "the next issue. `bash tools/loop.sh` is the driver; `/loop` cannot "
        "survive this stop."
    )


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
    if not MERGED_TEXT.search(output) and not merged_just_now(pr_number(command)):
        return 0

    json.dump(
        {
            "continue": False,
            "stopReason": stop_reason(),
            "systemMessage": system_message(),
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

    # (command, stdout, interrupted, merged-just-now-per-github, should fire)
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
        # Merged, but not by this command. Both of these stopped a turn on
        # 2026-09-05 while merging nothing: the hook reads the whole command
        # text, so a quoted merge command inside a pull request body or a JSON
        # test payload looked exactly like an executed one.
        ("gh pr create --body 'timeline: gh pr merge 230'", "", False, False, False),
        ("""echo '{"command":"gh pr merge 231"}' | python3 hook.py""",
         "", False, False, False),
    ]

    # (mergedAt, was it this command that merged it)
    freshness = [
        ("2026-09-05T02:00:00Z", True),      # five seconds ago
        ("2026-09-05T01:00:00Z", False),     # an hour ago: a mention, not a merge
        ("2026-09-05T02:00:10Z", True),      # GitHub's clock a little ahead
        ("", False),                         # never merged
        ("not a timestamp", False),
    ]

    numbers = [
        ("gh pr merge 193 --squash", "193"),
        ("gh pr merge #193 --squash", "193"),
        ("gh pr merge https://github.com/o/r/pull/12 -s", "12"),
        ("gh pr merge --squash --delete-branch", None),
        ("gh pr merge -s 42", "42"),
    ]

    def run(payload):
        """Feed one payload through main(), returning whatever it emitted."""
        stdin_was, stdout_was = sys.stdin, sys.stdout
        sys.stdin, sys.stdout = io.StringIO(payload), io.StringIO()
        try:
            main()
            return sys.stdout.getvalue().strip()
        finally:
            sys.stdin, sys.stdout = stdin_was, stdout_was

    real_merged_just_now = merged_just_now
    failed = 0
    try:
        for command, stdout, interrupted, merged, want in cases:
            globals()["merged_just_now"] = lambda _n, m=merged: m
            got = bool(run(json.dumps({
                "tool_input": {"command": command},
                "tool_response": {"stdout": stdout, "stderr": "",
                                  "interrupted": interrupted},
            })))
            if got != want:
                failed += 1
                print(f"FAIL want={want} got={got}: {command!r}")

        globals()["merged_just_now"] = lambda _n: True
        if run("not json"):
            failed += 1
            print("FAIL malformed payload fired")

        # A supervised stop is the design; an unsupervised one is the loop
        # dying, and the message is the only thing that tells them apart.
        merge = json.dumps({
            "tool_input": {"command": "gh pr merge 1 -s"},
            "tool_response": {"stdout": "", "stderr": "", "interrupted": False},
        })
        marker_was = os.environ.get("LACONIC_LOOP_SUPERVISOR")
        for marker, wanted in (("1", "tools/loop.sh restarts from here"),
                               (None, "No loop supervisor is running")):
            if marker is None:
                os.environ.pop("LACONIC_LOOP_SUPERVISOR", None)
            else:
                os.environ["LACONIC_LOOP_SUPERVISOR"] = marker
            reason = json.loads(run(merge))["stopReason"]
            if wanted not in reason:
                failed += 1
                print(f"FAIL supervisor={marker!r} wanted {wanted!r} in {reason!r}")
        if marker_was is None:
            os.environ.pop("LACONIC_LOOP_SUPERVISOR", None)
        else:
            os.environ["LACONIC_LOOP_SUPERVISOR"] = marker_was
    finally:
        globals()["merged_just_now"] = real_merged_just_now

    now = datetime.datetime(2026, 9, 5, 2, 0, 5, tzinfo=datetime.timezone.utc)
    for stamp, want in freshness:
        got = is_fresh(stamp, now=now)
        if got != want:
            failed += 1
            print(f"FAIL is_fresh want={want} got={got}: {stamp!r}")

    for command, want in numbers:
        got = pr_number(command)
        if got != want:
            failed += 1
            print(f"FAIL pr_number want={want!r} got={got!r}: {command!r}")

    total = len(cases) + len(numbers) + len(freshness) + 3
    print(f"{total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
