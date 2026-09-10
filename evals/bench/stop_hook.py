#!/usr/bin/env python3
"""The enforcement mechanism [#268] asks about: a `Stop` hook that reads the
completed turn and asks for one revision when it broke a rule already in the
model's context.

    python3 evals/bench/stop_hook.py --level full [--never-cut 401 ...] \
        [--record <path>]
    python3 evals/bench/stop_hook.py --selftest

Claude Code hands a `Stop` hook a JSON payload on stdin and reads a JSON
decision from stdout. The payload carries `last_assistant_message` verbatim, so
nothing here parses a transcript, and `stop_hook_active` is true on the firing
that follows a block, which is how "at most one rewrite" is enforced rather
than hoped for.

**This is benchmark code, not the plugin.** Nothing under `hooks/` calls it and
no `hooks/hooks.json` registers it. [#268] says the round can be bought before
the shipped bash and PowerShell paths are written, and that is deliberate: the
two-path sync burden is the cost of shipping the idea, and it should be paid
after a round says the idea is worth shipping, not before.

## What it measures with

`metrics.decisions(text, level, never_cut_keywords)` - the same level-aware set
of deterministic detectors the benchmark scores, so the hook cannot enforce a
rule the loop does not measure or measure one it does not enforce. It is
monotone in level by construction (#269), so a threshold that fires at `ultra`
and not at `full` is impossible here rather than merely untested.

## Why it quotes exactly one rule

The block reason names **one** rule line, the lowest-ranked detector that
fired, verbatim from `metrics.POLICY_RULE`. Two alternatives were considered
and rejected before the round (round 61's registration records both, and which
consulted target argued for which):

- Quoting *every* fired rule is closer to a deployed enforcement contract, but
  it makes the round unable to tell a model that generalised from one that
  satisfied the pointed instruction. With one line quoted, a residual scored
  per detector separates them: if the detectors that were present but *not*
  named also clear, the revision generalised; if only the named one clears, the
  model moved the violation rather than clearing it.
- Naming no rule at all ("you broke a rule, find it") tests whether the signal
  alone suffices. That is a different question, and a null under it is
  uninterpretable - it cannot distinguish a weak mechanism from underspecified
  feedback.

[#268]: https://github.com/JordanMPDS/laconic/issues/268
[#269]: https://github.com/JordanMPDS/laconic/issues/269
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402

# Named once so the round's reason text is a fact about this file rather than
# a description of it in a document. The second sentence is the one that keeps
# the revision from being a cosmetic substitution: a rewrite that swaps an
# arrow for a semicolon and drops the content is the failure the round is
# looking for, and asking for it not to happen is what makes a residual
# meaningful rather than tautological.
REASON = (
    'Your completed reply broke this rule, which was already in your '
    'instructions: "%s". Rewrite the reply once so it complies, keeping every '
    'piece of content the answer needs. Do not satisfy the rule by swapping '
    'punctuation or wording while leaving the problem in place.'
)


def choose(fired):
    """The one detector whose rule the block quotes.

    Lowest `POLICY_RANK` first, so the reason names a never-cut or readability
    finding ahead of a `lite` one; ties broken by name so the choice is a
    function of the finding set and not of set iteration order. A reason that
    varied between two identical responses would put noise into the treatment.
    """
    return min(sorted(fired), key=lambda n: metrics.POLICY_RANK[n])


def decide(payload, level, never_cut=()):
    """The hook's whole decision, as (stdout dict, record dict).

    Separated from I/O so the tests exercise the real thing. The record is what
    run.py stores beside the run: without the pre-revision text and the
    detectors that fired on it, "the hook prevented a failure" and "the hook
    never fired" are indistinguishable in the snapshot, and the revision
    success rate - the one number in this round that is not tautological - is
    unmeasurable.
    """
    text = payload.get("last_assistant_message") or ""
    fired = metrics.decisions(text, level, never_cut)
    record = {
        "text": text,
        "decisions": sorted(fired),
        "stop_hook_active": bool(payload.get("stop_hook_active")),
        "blocked": False,
        "named": None,
        "level": level,
        "never_cut": list(never_cut),
    }
    # The revision is allowed to be worse than what it replaced, and the hook
    # accepts it anyway. Blocking twice is a retry loop with a model on the
    # other end of it, and a hook that can build one is a hook that can spend
    # an unbounded number of the operator's calls on one response.
    if not fired or payload.get("stop_hook_active"):
        return {}, record
    named = choose(fired)
    record.update({"blocked": True, "named": named})
    return {"decision": "block",
            "reason": REASON % metrics.POLICY_RULE[named]}, record


PROBE_SENTINEL = "ENFORCED"


def probe(payload):
    """run.py's delivery probe, in the file whose delivery it probes.

    Blocks the first reply unconditionally and asks for a sentinel word. It
    deliberately ignores the detectors: the probe is asking whether the CLI runs
    a hook at all and feeds its reason back to the model, which is a question
    about the mechanism and not about any response.
    """
    if payload.get("stop_hook_active"):
        return {}
    return {"decision": "block",
            "reason": "Reply with only the word %s." % PROBE_SENTINEL}


def append_record(path, record):
    """One JSON object per line, appended.

    A `Stop` hook runs at most twice per response here, so the file holds the
    pre-revision reading and then the post-revision one, in order. Append
    rather than overwrite: the second firing is the measurement of the first
    one's effect, and a file that kept only the last line would lose the fact
    that anything was blocked.
    """
    with open(path, "a") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="full", choices=tuple(metrics.LEVEL_RANK))
    ap.add_argument("--never-cut", nargs="*", default=[],
                    help="the case's never-cut keywords, so the never-cut "
                         "detector can have an opinion at all. Absent, it "
                         "cannot fire - which is a caller's omission and not "
                         "a pass")
    ap.add_argument("--record", default=None,
                    help="path to append this firing's record to, as one JSON "
                         "object per line")
    ap.add_argument("--probe", action="store_true",
                    help="block once whatever the reply was, asking for a "
                         "sentinel the first reply could not contain. This is "
                         "run.py's delivery probe: if the sentinel comes back, "
                         "the CLI ran the hook, honoured the block and fed the "
                         "reason to the model")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.probe:
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except ValueError:
            payload = {}
        sys.stdout.write(json.dumps(probe(payload)))
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        # A hook that crashes on a payload it did not expect turns every
        # response in the arm into a failed run. Passing is the safe direction:
        # it under-reports enforcement rather than destroying the pass.
        payload = {}
    out, record = decide(payload, args.level, tuple(args.never_cut))
    if args.record:
        try:
            append_record(args.record, record)
        except OSError:
            pass
    sys.stdout.write(json.dumps(out))
    return 0


def selftest():
    fails = 0

    def check(label, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + label)
        if not cond:
            fails += 1

    clean = ("The limiter fails open when Redis is down. The incr call returns "
             "null, so the comparison is false and the request is passed on.")
    arrowed = "Rotate the key -> wait out the old TTL -> remove it."

    out, rec = decide({"last_assistant_message": clean}, "full")
    check("a clean reply is not blocked", out == {})
    check("a clean reply records no decisions", rec["decisions"] == [])
    check("a clean reply records its text", rec["text"] == clean)

    out, rec = decide({"last_assistant_message": arrowed}, "full")
    check("an arrow in prose is blocked", out.get("decision") == "block")
    check("the block names the arrow rule",
          metrics.POLICY_RULE["symbol_connectors"] in out["reason"])
    check("the record names the detector quoted",
          rec["named"] == "symbol_connectors")
    check("the record says it blocked", rec["blocked"] is True)

    out, rec = decide({"last_assistant_message": arrowed,
                       "stop_hook_active": True}, "full")
    check("a second firing never blocks, so one rewrite is the ceiling",
          out == {})
    check("the second firing still records what it saw",
          rec["decisions"] == ["symbol_connectors"] and rec["blocked"] is False)

    # The never-cut detector is per case and cannot fire without keywords.
    dropped = "Refresh happens transparently and the caller sees nothing."
    out, _ = decide({"last_assistant_message": dropped}, "full")
    check("no keywords means the never-cut detector cannot fire", out == {})
    out, rec = decide({"last_assistant_message": dropped}, "full", ("401",))
    check("a dropped never-cut keyword is blocked",
          out.get("decision") == "block" and rec["named"] == "never_cut_missing")

    # Rank decides which rule is quoted, not set order.
    both = dropped + " " + arrowed + " Let me know if you want more detail."
    fired = metrics.decisions(both, "full", ("401",))
    check("the mixed reply fires more than one detector", len(fired) > 1)
    check("the quoted rule is the lowest-ranked one that fired",
          metrics.POLICY_RANK[choose(fired)]
          == min(metrics.POLICY_RANK[n] for n in fired))
    check("choose() is a function of the finding set, not of iteration order",
          all(choose(frozenset(p)) == choose(frozenset(reversed(list(p))))
              for p in [list(fired)]))

    # Monotone in level, inherited from metrics.decisions(). A closing offer is
    # a `lite` rule, so it must not fire at a level that does not carry it -
    # and every level must be a superset of the one below it.
    offer = "That is the cause. Let me know if you want me to fix it."
    sets = [metrics.decisions(offer, lv, ()) for lv in ("lite", "full", "ultra")]
    check("the hook's finding sets are nested across the three levels",
          sets[0] <= sets[1] <= sets[2])
    for lv in ("lite", "full", "ultra"):
        out, _ = decide({"last_assistant_message": offer}, lv)
        check("a closing offer blocks at %s" % lv, out.get("decision") == "block")

    # A payload the hook did not expect must not take the run down with it.
    out, rec = decide({}, "full")
    check("an empty payload passes rather than crashing", out == {})
    check("an empty payload records an empty text", rec["text"] == "")

    check("the probe blocks a first reply", probe({}).get("decision") == "block")
    check("the probe asks for the sentinel run.py looks for",
          PROBE_SENTINEL in probe({})["reason"])
    check("the probe never blocks twice",
          probe({"stop_hook_active": True}) == {})

    import tempfile
    td = tempfile.mkdtemp()
    path = os.path.join(td, "log.jsonl")
    append_record(path, {"a": 1})
    append_record(path, {"a": 2})
    lines = [json.loads(l) for l in open(path)]
    check("records append rather than overwrite",
          [l["a"] for l in lines] == [1, 2])

    print("\n%d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
