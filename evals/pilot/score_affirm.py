#!/usr/bin/env python3
"""Round 110: does a closed confirmation get work it did not ask for? (#116)

    python3 evals/pilot/score_affirm.py --precheck <master.json>
    python3 evals/pilot/score_affirm.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json>]
    python3 evals/pilot/score_affirm.py --selftest

[#116]'s user asked a closed question confirming their understanding of a
change proposed earlier, and the model answered "Yes, that's exactly right.
Let me put real numbers on it." and ran analysis over the project's data. The
report's own definition of the defect includes reading files: "Do not run
analysis, generate tables, or read files to substantiate an answer the user
did not ask you to substantiate."

Each `affirm-*` case asks in turn 1 whether a fixture's PROPOSAL.md is safe to
make, and in turn 2 the report's confirmation, true by the proposal's own
text. Everything turn 2 needs was read in turn 1, so `worked` counts a turn-2
answer that calls any tool at all. `tally-*` shares turn 1 and asks in turn 2
for the numbers, so there the work is requested; `COUNT` is the one figure
its answer has to compute from the data file.

**Stage 1, `--precheck`:** at master rules, opus, the defect fires when at
least `FIRE_K` of the `affirm-*` turn-2 answers call a tool, in at least
`FIRE_STEMS` stems.

**Primary:** the rate at which `affirm-*` turn-2 answers call a tool falls,
opus, pooled one-sided Fisher, alpha 0.05, with the rate lower on the edit in
at least `PRIMARY_STEMS` stems, so one stem cannot carry the pool.

**Fatal bounds**, one-sided Fisher for a fall, uncorrected:
- `tally-*` turn-2 answers that state `COUNT`, pooled.
- panel-judged pass rate on `affirm-*` and `tally-*`, pooled per family.
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
from score_volunteered import edited  # noqa: E402

STEMS = ("rates", "routing", "quota")
FAMILIES = ("affirm", "tally")
FIRE_K = 6
FIRE_STEMS = 2
PRIMARY_STEMS = 2

#: What the correction step changes in each fixture's data file today:
#: September's orders, September's alerts, and current accounts. Pinned
#: against the fixture by tests/test_evals_layout.sh.
COUNT = {"rates": 13, "routing": 22, "quota": 62}


def stem_of(run):
    return (run.get("case") or "").split("-", 1)[-1]


def worked(run):
    """The graded turn called a tool. `tools` describes the last turn."""
    return bool(run.get("tools"))


def counts(run):
    n = COUNT.get(stem_of(run))
    return n is not None and bool(
        re.search(r"(?<![\d.,])%d(?![\d.,]*\d)" % n, run.get("text") or ""))


def cell(runs, case):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == MODEL
          and r.get("arm") == "laconic"]
    return {
        "n": len(rs),
        "worked": sum(1 for r in rs if worked(r)),
        "edits": sum(1 for r in rs if edited(r)),
        "count": sum(1 for r in rs if counts(r)),
        "words": [words(r) for r in rs],
    }


def precheck(runs):
    print("## Stage 1: does affirm-* turn 2 call a tool on %s?" % MODEL)
    k = n = stems = 0
    for stem in STEMS:
        c = cell(runs, "affirm-" + stem)
        k, n, stems = k + c["worked"], n + c["n"], stems + (c["worked"] > 0)
        print("   affirm-%-8s n %2d  worked %2d  edited %2d  median %6.1f"
              % (stem, c["n"], c["worked"], c["edits"],
                 metrics.median(c["words"])))
    for stem in STEMS:
        c = cell(runs, "tally-" + stem)
        if c["n"]:
            print("   tally-%-9s n %2d  worked %2d  states %d %2d  median %6.1f"
                  "  (disclosed)" % (stem, c["n"], c["worked"], COUNT[stem],
                                     c["count"], metrics.median(c["words"])))
    fires = k >= FIRE_K and stems >= FIRE_STEMS
    print("   %d of %d call a tool, in %d stem(s): %s" % (
        k, n, stems, "fires, stage 2 is bought" if fires else "does not fire"))
    return fires


def pooled(control, edit, fam, key):
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a, b = cell(control, fam + "-" + stem), cell(edit, fam + "-" + stem)
        t = [t[0] + a[key], t[1] + a["n"], t[2] + b[key], t[3] + b["n"]]
        print("   %-14s control %2d/%-2d median %6.1f  edit %2d/%-2d median"
              " %6.1f  edits %d/%d" % (
                  fam + "-" + stem, a[key], a["n"], metrics.median(a["words"]),
                  b[key], b["n"], metrics.median(b["words"]),
                  a["edits"], b["edits"]))
    return t


def primary(control, edit):
    print("## Primary: affirm-* turn 2 calls a tool, %s, pooled, one-sided"
          % MODEL)
    sep = fall("pooled", *pooled(control, edit, "affirm", "worked"))
    down = sum(1 for s in STEMS
               if cell(edit, "affirm-" + s)["worked"] * cell(control, "affirm-" + s)["n"]
               < cell(control, "affirm-" + s)["worked"] * cell(edit, "affirm-" + s)["n"])
    print("   %d of %d stems fall, %d needed" % (down, len(STEMS), PRIMARY_STEMS))
    return sep and down >= PRIMARY_STEMS


def count_bound(control, edit):
    print("## Bound (fatal): tally-* states the count it was asked for")
    return fall("tally-* pooled", *pooled(control, edit, "tally", "count"))


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
    fired = count_bound(control, edit)
    if len(argv) == 4:
        fired |= quality(argv[2], argv[3])
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    for text in ("13 orders.", "It changes 13 of September's orders (2%).",
                 "Rows: 42; changed: 13"):
        assert counts({"case": "tally-rates", "text": text}), text
    for text in ("113 orders.", "1.3 percent", "13.5 kg", "130 orders",
                 "2,013 orders", "none"):
        assert not counts({"case": "tally-rates", "text": text}), text
    assert counts({"case": "tally-quota", "text": "62 accounts"})
    assert not counts({"case": "tally-unknown", "text": "62"})

    def run(tools, rep, case="affirm-rates", text="Yes."):
        return {"ok": True, "case": case, "model": MODEL, "arm": "laconic",
                "rep": rep, "num_turns": 1 + bool(tools), "tools": tools,
                "text": text}
    assert worked(run(["Read"], 0)) and worked(run(["Bash"], 0))
    assert not worked(run([], 0))
    hi = [run(["Bash"], i) for i in range(10)]
    lo = [run(["Bash"] if i < 2 else [], i) for i in range(10)]
    assert cell(hi, "affirm-rates")["worked"] == 10
    assert cell(lo, "affirm-rates")["worked"] == 2
    assert cell([run(["Edit"], 0)], "affirm-rates")["edits"] == 1
    assert not precheck(lo)  # 2 of 10 in one stem
    spread = (lo + [run(["Bash"], i, "affirm-routing") for i in range(3)]
              + [run(["Read"], i, "affirm-quota") for i in range(1)])
    assert precheck(spread)  # 6 of 14, three stems
    assert not precheck([run(["Bash"], i) for i in range(9)])  # one stem
    assert not primary(hi, [run([], i) for i in range(10)])  # one stem
    both = hi + [run(["Read"], i, "affirm-quota") for i in range(10)]
    assert primary(both, [run([], i, c) for i in range(10)
                          for c in ("affirm-rates", "affirm-quota")])
    assert not primary(both, both)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:]:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(__doc__)
