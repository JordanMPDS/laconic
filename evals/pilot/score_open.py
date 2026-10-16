#!/usr/bin/env python3
"""Round 108: does an answer carry an open question it was not asked? (#384)

    python3 evals/pilot/score_open.py --precheck <master.json>
    python3 evals/pilot/score_open.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json>]
    python3 evals/pilot/score_open.py --selftest

[#384]'s answer named the option, then inferred a cause inside it that nobody
had asked about and attached a caveat: *"That's inferred, because we haven't
seen the colleague's connector configuration."* The report suspects the
never-cut uncertainty item licensed it. Each `open-*` fixture settles an
either/or and leaves the mechanism inside the winning option unestablished;
`open-*` asks only the either/or. `OPEN` matches the open question in the
answer, as a cause inferred inside the option or as a note that it is unknown.

**Stage 1, `--precheck`:** at master rules, opus, the defect fires when at
least `FIRE_K` of the `open-*` answers carry the open question, at least
`FIRE_STEM_K` in every stem.

**Primary:** the rate at which `open-*` answers carry the open question
falls, opus, pooled one-sided Fisher, alpha 0.05.

**Fatal bounds**, one-sided Fisher for a fall, uncorrected:
- panel-judged pass rate on `open-*`, `unsettled-*` and `keep-*`, pooled per
  family. `unsettled-*` asks an either/or about the open mechanism itself, so
  the uncertainty is the answer. `keep-*` asks whether a remedy would work,
  and it works only if the open mechanism is the one the remedy assumes.
- `HEDGE`, an answer saying the record leaves the question open or making its
  advice conditional on it, on `unsettled-*` and `keep-*`, pooled per family.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
import score_choice  # noqa: E402
from score_choice import MODEL, fall, load  # noqa: E402
from score_compression import words  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

STEMS = ("cdc", "disk", "checkout")
FAMILIES = ("open", "unsettled", "keep")
FIRE_K = 10
FIRE_STEM_K = 3

#: A cause inside the winning option, which the user did not ask about and
#: the record does not establish. None of these words is in the fixtures.
INFER = {
    "cdc": re.compile(
        r"(ordering key|parallel|concurren|\bretr(y|ies|ied|ying)\b|batch"
        r"|in[\s-]flight|buffer|back[\s-]?pressure|partition)", re.I),
    "disk": re.compile(
        r"(replication slot|pg_replication_slots|\bslots?\b|archiv|wal_keep"
        r"|max_wal_size|checkpoint|standby|\breplicas?\b|logical decoding)",
        re.I),
    "checkout": re.compile(
        r"(provider'?s (side|end)|their (side|end)|network|\begress\b|\bNAT\b"
        r"|\bDNS\b|\bTLS\b|handshake|connection (setup|pool|reuse)"
        r"|keep[\s-]?alive|rate[\s-]?limit|throttl)", re.I),
}

#: The open question named as open: the fixture's own sentence about what was
#: not collected, run or answered, carried into an answer that did not need it.
#: Registered narrower; widened after the precheck's first sample, which it
#: under-read on `disk` (see round-108.md), and before any sample it decides.
WHY_NOT_SAID = (r"|\b(doesn't|does not|don't|do not|can't|cannot) (yet )?"
                r"(say|tell|show|explain) why")
UNKNOWN = {
    "cdc": re.compile(
        r"(sink settings|(were|was|weren't|wasn't|not) (been )?collected"
        r"|why (wal2queue|the connector) (is )?(hand|deliver|send|publish)"
        + WHY_NOT_SAID + ")", re.I),
    "disk": re.compile(
        r"(nothing (else )?(past|beyond|after)|beyond (that|the|this) `?du"
        r"|off shift|\b(nobody|no one|no-one) (has )?(run|ran|looked|checked)"
        r"|(not|n't) (yet )?(been )?(run|checked|diagnosed)"
        r"|why (postgres|the server|the database|the wal|wal|it)\b[^.]{0,30}"
        r"(keep|kept|hold|retain|pil|accumul|grow)" + WHY_NOT_SAID + ")", re.I),
    "checkout": re.compile(
        r"(support ticket|finer spans|(hasn't|has not|not yet) answered"
        r"|status page" + WHY_NOT_SAID + ")", re.I),
}

#: The record leaves it open, or the advice is conditional on it.
HEDGE = re.compile(
    r"(not established|isn't established|not (yet )?known|\bunknown\b"
    r"|\b(doesn't|does not|don't|do not|can't|cannot) (yet )?(say|establish"
    r"|settle|tell|show|distinguish|know|determine|confirm|break|answer)"
    r"|no way to tell|(not|n't) (yet )?(been )?(collected|checked|run"
    r"|confirmed|pulled|looked)|nothing past|unclear|undetermined"
    r"|(hasn't|has not|not yet) answered|unconfirmed|unverified|only if"
    r"|depends on|(check|confirm|verify|look|find out|establish)[^.]{0,60}"
    r"\bfirst\b|until (you|we)|before (you|we|dropping|turning|moving"
    r"|switching))", re.I)


def stem_of(run):
    return (run.get("case") or "").split("-", 1)[-1]


def infers(run):
    pat = INFER.get(stem_of(run))
    return bool(pat and pat.search(run.get("text") or ""))


def opens(run):
    pat = UNKNOWN.get(stem_of(run))
    return infers(run) or bool(pat and pat.search(run.get("text") or ""))


def hedges(run):
    return bool(HEDGE.search(run.get("text") or ""))


def cell(runs, case):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == MODEL
          and r.get("arm") == "laconic"]
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "open": sum(1 for r in rs if opens(r)),
        "infer": sum(1 for r in rs if infers(r)),
        "hedge": sum(1 for r in rs if hedges(r)),
        "words": [words(r) for r in rs],
    }


def precheck(runs):
    print("## Stage 1: does an open question carry into open-* on %s?" % MODEL)
    k = n = 0
    every_stem = True
    for stem in STEMS:
        c = cell(runs, "open-" + stem)
        k, n = k + c["open"], n + c["n"]
        every_stem &= c["open"] >= FIRE_STEM_K
        print("   open-%-9s n %2d  carries %2d (infers %2d)  median %6.1f"
              "  read %2d" % (stem, c["n"], c["open"], c["infer"],
                              metrics.median(c["words"]), c["grounded"]))
    for fam in FAMILIES[1:]:
        for stem in STEMS:
            c = cell(runs, "%s-%s" % (fam, stem))
            if c["n"]:
                print("   %-15s n %2d  hedges %2d  median %6.1f  (disclosed)"
                      % ("%s-%s" % (fam, stem), c["n"], c["hedge"],
                         metrics.median(c["words"])))
    fires = k >= FIRE_K and every_stem
    print("   %d of %d carry it, %s stem at %d or more: %s" % (
        k, n, "every" if every_stem else "not every", FIRE_STEM_K,
        "fires, stage 2 is bought" if fires else "does not fire"))
    return fires


def pooled(control, edit, fam, key):
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a, b = cell(control, fam + "-" + stem), cell(edit, fam + "-" + stem)
        t = [t[0] + a[key], t[1] + a["n"], t[2] + b[key], t[3] + b["n"]]
        print("   %-15s control %2d/%-2d median %6.1f  edit %2d/%-2d median"
              " %6.1f  edits %d/%d" % (
                  fam + "-" + stem, a[key], a["n"], metrics.median(a["words"]),
                  b[key], b["n"], metrics.median(b["words"]),
                  a["edits"], b["edits"]))
    return t


def primary(control, edit):
    print("## Primary: open-* carries the open question, %s, pooled, one-sided"
          % MODEL)
    return fall("pooled", *pooled(control, edit, "open", "open"))


def hedge_bound(control, edit):
    print("## Bound (fatal): the answer says the record leaves it open")
    fired = False
    for fam in FAMILIES[1:]:
        fired |= fall(fam + "-* pooled", *pooled(control, edit, fam, "hedge"))
    return fired


def quality(cj, ej):
    print("## Bound (fatal): panel-judged pass rate, per family")
    saved = score_choice.FAMILIES
    score_choice.FAMILIES = FAMILIES
    try:
        a, b = score_choice.verdicts(cj), score_choice.verdicts(ej)
    finally:
        score_choice.FAMILIES = saved
    fired = False
    for fam in FAMILIES:
        fired |= fall(fam + "-*", a[fam][0], a[fam][1], b[fam][0], b[fam][1])
    return fired


def main(argv):
    if argv[:1] == ["--precheck"] and len(argv) == 2:
        return 0 if precheck(load(argv[1])) else 1
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    control, edit = load(argv[0]), load(argv[1])
    ok = primary(control, edit)
    fired = hedge_bound(control, edit)
    if len(argv) == 4:
        fired |= quality(argv[2], argv[3])
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    for case, text in (
            ("open-cdc", "At the publish step. It is likely retries without an "
             "ordering key, though that is inferred."),
            ("open-cdc", "When wal2queue publishes. Its sink settings weren't "
             "collected, so why it is late is open."),
            ("open-disk", "The WAL, probably held by an inactive replication "
             "slot."),
            ("open-disk", "The WAL. Nothing past the du has been run yet."),
            ("open-disk", "Postgres's WAL. The note doesn't say why WAL is "
             "piling up. No one has run anything beyond that `du`."),
            ("open-disk", "Postgres's WAL. The document doesn't say why the "
             "WAL is being kept, and nothing beyond that `du` was run."),
            ("open-checkout", "The provider call. The delay could be on their "
             "side or in our network path."),
            ("open-checkout", "The call to the card provider; the support "
             "ticket is still unanswered.")):
        assert opens({"case": case, "text": text}), text
    for case, text in (
            ("open-cdc", "When wal2queue publishes to the topic. The "
             "subscription only copies publish_time, so its write order "
             "cannot invert lsn against publish_time."),
            ("open-disk", "Postgres's WAL. pg_wal grew 401G in nine days; the "
             "application's logs are on the app hosts."),
            ("open-checkout", "The call to the card provider: payments.authorize "
             "takes 2,740 ms while the database spans are unchanged.")):
        assert not opens({"case": case, "text": text}), text
    assert infers({"case": "open-disk", "text": "check pg_replication_slots"})
    assert not infers({"case": "open-disk", "text": "Nothing past du was run."})
    for text in ("The record doesn't say which.", "Not established yet.",
                 "LATENCY.md can't answer that.",
                 "Only if a slot is holding it; check pg_replication_slots "
                 "first.", "The sink settings weren't collected."):
        assert hedges({"text": text}), text
    for text in ("Retries. Turn them off.", "Yes, drop the slot.",
                 "It is the provider's side."):
        assert not hedges({"text": text}), text

    def run(carry, rep):
        return {"ok": True, "case": "open-disk", "model": MODEL,
                "arm": "laconic", "rep": rep, "num_turns": 3, "tools": ["Read"],
                "text": "The WAL, likely a replication slot." if carry
                else "The WAL."}
    hi = [run(True, i) for i in range(20)]
    lo = [run(i < 4, i) for i in range(20)]
    assert cell(hi, "open-disk")["open"] == 20
    assert cell(lo, "open-disk")["open"] == 4
    assert fall("selftest", 20, 20, 4, 20)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
