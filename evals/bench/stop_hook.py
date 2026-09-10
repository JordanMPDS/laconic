#!/usr/bin/env python3
"""The enforcement mechanism [#268] asks about: a `Stop` hook that reads the
completed turn and asks for one revision when it broke a rule already in the
model's context.

    python3 evals/bench/stop_hook.py --level full [--never-cut 401 ...] \
        [--reason-mode named|reminder] [--record <path>]
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

## Why there are now two reason modes (#283, round 62)

The second alternative is no longer hypothetical. Round 61 answered its own
question - the named block clears the violation - so a null under the unnamed
one is no longer the uninterpretable thing that argument was about, and the
comparison became buyable on the same cells. `--reason-mode reminder` is that
variant: the same sentence with the quoted rule taken out, and nothing else
changed.

It is a shipping question rather than a curiosity. Both modes need the
detectors. Only `named` additionally needs `metrics.POLICY_RULE`, the
detector-to-rule-text table, which the shipped hook would have to carry down
both the bash and the PowerShell path and keep in step with
`rules/laconic.md`. If a sentence works as well as the table, the shipped
mechanism is materially smaller and has one fewer thing that can drift.

## Why both reasons end by asking for no commentary

Round 61's one residual was not a surviving violation. The response rewrote the
offending line correctly and then prepended `Found it - "No refresh token ->
throws" used an arrow. Rewritten:`, and the detector fired on the arrow inside
that quotation - on commentary the block reason itself caused. A reason that
does not name the rule invites exactly that narration, so the artefact would
load the `reminder` arm differentially and could manufacture a difference out
of nothing. The clause is in both reasons for that reason, and it is `codex`'s
on `tools/consult.sh`; `kimi` argued instead for keeping round 61's text
byte-identical and classifying the residuals after the fact. The cost of the
choice taken is that round 62's `named` arm is an internal replication of round
61 rather than a reuse of its number, which the round document says.

[#268]: https://github.com/JordanMPDS/laconic/issues/268
[#269]: https://github.com/JordanMPDS/laconic/issues/269
[#283]: https://github.com/JordanMPDS/laconic/issues/283
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402

# Named once so the round's reason text is a fact about this file rather than
# a description of it in a document. The two modes share every sentence but the
# first, and that is the whole point: #283 asks whether the block has to quote
# the rule, so the arms must differ in rule specificity and in nothing else.
#
# `%s` in the `named` reason is the one quoted `metrics.POLICY_RULE` line. The
# `reminder` reason takes no substitution and deliberately does not say "find
# it" either - an extra instruction is a second difference, and it is the one
# most likely to provoke the narration the last sentence exists to stop.
#
# Sentence by sentence, and each is load-bearing:
#   1. what happened, with or without the rule quoted - the treatment.
#   2. rewrite once, keeping the content - a rewrite that complies by deleting
#      the answer is the failure the never-cut detector is watching for.
#   3. no cosmetic substitution - swapping an arrow for a semicolon and losing
#      the content is what makes a residual tautological rather than meaningful.
#   4. no commentary - round 61's only residual was the model quoting its own
#      offending line back inside a "Found it - ... Rewritten:" preamble, and
#      the detector fired on the quotation. Without this, that artefact loads
#      the unnamed arm differentially and manufactures the round's own effect.
_TAIL = (
    'Rewrite the reply once so it complies, keeping every piece of content the '
    'answer needs. Do not satisfy the rule by swapping punctuation or wording '
    'while leaving the problem in place. Reply with only the rewritten answer '
    'and no commentary.'
)

REASONS = {
    "named": 'Your completed reply broke this rule, which was already in your '
             'instructions: "%s". ' + _TAIL,
    "reminder": 'Your completed reply broke one of the rules that was already '
                'in your instructions. ' + _TAIL,
}

# Round 61's arm, kept as a name rather than a default spelled in three places.
DEFAULT_REASON_MODE = "named"


def choose(fired):
    """The one detector whose rule the block quotes.

    Lowest `POLICY_RANK` first, so the reason names a never-cut or readability
    finding ahead of a `lite` one; ties broken by name so the choice is a
    function of the finding set and not of set iteration order. A reason that
    varied between two identical responses would put noise into the treatment.
    """
    return min(sorted(fired), key=lambda n: metrics.POLICY_RANK[n])


def decide(payload, level, never_cut=(), mode=DEFAULT_REASON_MODE):
    """The hook's whole decision, as (stdout dict, record dict).

    Separated from I/O so the tests exercise the real thing. The record is what
    run.py stores beside the run: without the pre-revision text and the
    detectors that fired on it, "the hook prevented a failure" and "the hook
    never fired" are indistinguishable in the snapshot, and the revision
    success rate - the one number in this round that is not tautological - is
    unmeasurable.

    `named` is recorded in **both** modes, and it is the target detector rather
    than a transcript of the reason: under `reminder` the rule is chosen and
    then not quoted. Without it, "did the model clear the violation the hook
    was actually reacting to?" is unanswerable in the arm that most needs
    asking, because a response with two findings could clear either one
    (`codex` on `tools/consult.sh`, #283).
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
        "reason_mode": mode,
    }
    # The revision is allowed to be worse than what it replaced, and the hook
    # accepts it anyway. Blocking twice is a retry loop with a model on the
    # other end of it, and a hook that can build one is a hook that can spend
    # an unbounded number of the operator's calls on one response.
    if not fired or payload.get("stop_hook_active"):
        return {}, record
    named = choose(fired)
    record.update({"blocked": True, "named": named})
    reason = REASONS[mode]
    return {"decision": "block",
            "reason": reason % metrics.POLICY_RULE[named]
                      if "%s" in reason else reason}, record


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
    ap.add_argument("--reason-mode", default=DEFAULT_REASON_MODE,
                    choices=tuple(REASONS),
                    help="whether the block quotes the rule that fired. "
                         "'named' is round 61's arm; 'reminder' is #283's, the "
                         "same sentence with the quotation taken out and "
                         "nothing else changed. The choice is recorded on "
                         "every firing, because a snapshot that does not say "
                         "which reason a response got cannot be reanalysed")
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
    out, record = decide(payload, args.level, tuple(args.never_cut),
                         args.reason_mode)
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
    check("the record says which reason it gave, so a snapshot can be "
          "reanalysed without knowing how it was launched",
          rec["reason_mode"] == "named")

    # #283's arm. The two reasons must differ in rule specificity and in
    # nothing else, because that is the whole contrast the round buys.
    rout, rrec = decide({"last_assistant_message": arrowed}, "full",
                        mode="reminder")
    check("the reminder reason blocks on the same finding",
          rout.get("decision") == "block")
    check("the reminder reason quotes no rule at all",
          metrics.POLICY_RULE["symbol_connectors"] not in rout["reason"])
    check("no POLICY_RULE line leaks into the reminder reason, not just the "
          "one that fired",
          not any(r and r in rout["reason"]
                  for r in metrics.POLICY_RULE.values()))
    check("the reminder record still names the target detector, so clearance "
          "of the finding the hook reacted to stays measurable",
          rrec["named"] == "symbol_connectors")
    check("the reminder record says which reason it gave",
          rrec["reason_mode"] == "reminder")
    check("the two reasons differ only in their first sentence",
          out["reason"].split(". ", 1)[1] == rout["reason"].split(". ", 1)[1])
    check("both reasons end by asking for no commentary, which is what keeps "
          "round 61's narration artefact from loading one arm",
          all(r.endswith("Reply with only the rewritten answer and no "
                         "commentary.") for r in REASONS.values()))
    check("the reminder reason takes no substitution",
          "%s" not in REASONS["reminder"])
    check("only the named reason takes one", "%s" in REASONS["named"])
    check("neither reason tells the model to go looking, which would be a "
          "second difference between the arms",
          not any("find it" in r.lower() for r in REASONS.values()))

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
    check("a pass records its reason mode too, so an unfired response is not "
          "a hole in the arm's record", rec["reason_mode"] == "named")

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
