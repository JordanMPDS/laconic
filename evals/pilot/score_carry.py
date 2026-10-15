#!/usr/bin/env python3
"""Round 107: does an answer carry an earlier turn's topic it was not asked? (#384)

    python3 evals/pilot/score_carry.py --precheck <master.json>
    python3 evals/pilot/score_carry.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json>]
    python3 evals/pilot/score_carry.py --selftest

[#384]'s answer ended with a paragraph on a topic the user had raised a turn
earlier, which the model's own reasoning flagged as not asked for and kept.
`carry-*` asks for the fix in turn 1 and then `choose-*`'s either/or about the
cause in turn 2, byte for byte without its opening clause. Only turn 2 is
scored. `CARRY` matches turn 1's topic, the fix, in turn 2's answer.

**Stage 1, `--precheck`:** at master rules, opus, the defect fires when at
least `FIRE_K` of the `carry-*` turn-2 answers carry turn 1's topic, at least
`FIRE_STEM_K` in every stem, and `carry-*` carries it more often than the
single-turn `choose-*` generated beside it (pooled one-sided Fisher), so the
carry is the earlier turn's and not a fix volunteered anyway.

**Primary:** the carry rate on `carry-*` turn 2 falls, opus, pooled one-sided
Fisher, alpha 0.05.

**Fatal bounds**, one-sided Fisher for a fall, uncorrected: panel-judged pass
rate on `carry-*`, `depend-*`, `deepsubset-*` and `deep-*`, pooled per family.
`depend-*` is `carry-*`'s turn 1 followed by an either/or that refers back to
it, so a good answer has to use the earlier turn; `deepsubset-*` ends in a
narrowing follow-up whose answer is built from earlier turns, and `deep-*` in
a wrong-premise confirmation that needs the earlier diagnosis. They are where
scoping check 3 to the current question could cost an answer the context it
needs. Plus `date_trunc` kept on `deep-index`.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_choice import MODEL, ALPHA, STEMS, fall, load  # noqa: E402
from score_compression import words  # noqa: E402
from score_structure import fisher_one_sided_fall  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

FAMILIES = ("carry", "depend", "deepsubset", "deep")
FIRE_K = 10
FIRE_STEM_K = 3

#: Turn 1's topic, the fix, per stem. Each names the fix itself rather than
#: the cause turn 2 asks about, so an answer to turn 2 has no need of it.
CARRY = {
    "index": re.compile(
        r"(events_created_at_idx|events_day_tenant_idx|CREATE INDEX|half-open"
        r"|expression index|index (on|over) the expression|composite"
        r"|rewrit\w* the (predicate|query|where)|ticket's (proposed )?index"
        r"|index on the ticket)", re.I),
    "metric": re.compile(
        r"(proxy|payment step|higher-frequency|run (it )?to the [^.]{0,20}sample"
        r"|keep running|run (it )?longer)", re.I),
    "rollback": re.compile(
        r"(expand|contract|action item|same release|release job"
        r"|rollback window|treat\w* (an )?unknown|instead of throw)", re.I),
}


def carries(run):
    stem = (run.get("case") or "").split("-", 1)[-1]
    pat = CARRY.get(stem)
    return bool(pat and pat.search(run.get("text") or ""))


def cell(runs, case):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == MODEL
          and r.get("arm") == "laconic"]
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "carry": sum(1 for r in rs if carries(r)),
        "words": [words(r) for r in rs],
    }


def precheck(runs):
    print("## Stage 1: does an earlier turn's topic carry into turn 2 on %s?"
          % MODEL)
    t = [0, 0, 0, 0]
    every_stem = True
    for stem in STEMS:
        a, b = cell(runs, "carry-" + stem), cell(runs, "choose-" + stem)
        t = [t[0] + a["carry"], t[1] + a["n"], t[2] + b["carry"], t[3] + b["n"]]
        every_stem &= a["carry"] >= FIRE_STEM_K
        print("   carry-%-8s n %2d  carries %2d  median %6.1f  |  choose-%-8s"
              " n %2d  carries %2d  median %6.1f" % (
                  stem, a["n"], a["carry"], metrics.median(a["words"]), stem,
                  b["n"], b["carry"], metrics.median(b["words"])))
    # A rise in carry over choose is choose falling below carry.
    p = fisher_one_sided_fall(t[0], t[1], t[2], t[3]) if t[1] and t[3] else 1.0
    fires = t[0] >= FIRE_K and every_stem and p < ALPHA
    print("   carry %d/%d, %s stem at %d or more; above choose %d/%d, one-sided"
          " p = %.4f: %s" % (t[0], t[1], "every" if every_stem else "not every",
                             FIRE_STEM_K, t[2], t[3], p,
                             "fires, stage 2 is bought" if fires
                             else "does not fire"))
    return fires


def primary(control, edit):
    print("## Primary: carry-* turn 2 carries turn 1's topic, %s, pooled,"
          " one-sided" % MODEL)
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a, b = cell(control, "carry-" + stem), cell(edit, "carry-" + stem)
        t = [t[0] + a["carry"], t[1] + a["n"], t[2] + b["carry"], t[3] + b["n"]]
        print("   carry-%-8s control %2d/%-2d median %6.1f  edit %2d/%-2d median"
              " %6.1f  edits %d/%d" % (
                  stem, a["carry"], a["n"], metrics.median(a["words"]),
                  b["carry"], b["n"], metrics.median(b["words"]),
                  a["edits"], b["edits"]))
    return fall("pooled", *t)


def verdicts(path):
    out = defaultdict(lambda: [0, 0])
    for j in json.loads(Path(path).read_text())["judgments"]:
        fam = j["case"].split("-", 1)[0]
        if (fam in FAMILIES and j.get("model") == MODEL
                and j["verdict"] != "not_exercised"):
            out[fam][0] += j["verdict"] == "pass"
            out[fam][1] += 1
    return out


def quality(cj, ej):
    print("## Bound (fatal): panel-judged pass rate, per family")
    a, b = verdicts(cj), verdicts(ej)
    fired = False
    for fam in FAMILIES:
        fired |= fall(fam + "-*", a[fam][0], a[fam][1], b[fam][0], b[fam][1])
    return fired


def kept(control, edit):
    print("## Bound (fatal): date_trunc kept on deep-index")
    out = []
    for runs in (control, edit):
        rs = [r for r in bench_run.usable(runs) if r.get("case") == "deep-index"
              and r.get("model") == MODEL and r.get("arm") == "laconic"]
        out += [sum(1 for r in rs if not metrics.never_cut_missing(
            r.get("text") or "", ["date_trunc"])), len(rs)]
    return fall("deep-index", *out)


def main(argv):
    if argv[:1] == ["--precheck"] and len(argv) == 2:
        return 0 if precheck(load(argv[1])) else 1
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    control, edit = load(argv[0]), load(argv[1])
    ok = primary(control, edit)
    fired = kept(control, edit)
    if len(argv) == 4:
        fired |= quality(argv[2], argv[3])
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    assert carries({"case": "carry-index",
                    "text": "The query. Build events_day_tenant_idx as above."})
    assert carries({"case": "carry-metric",
                    "text": "Four purchases; a proxy outcome would resolve it."})
    assert carries({"case": "carry-rollback",
                    "text": "The NOT NULL column. Hence expand and contract."})
    for case, text in (
            ("carry-index", "The query itself: a sequential scan, because "
             "date_trunc wraps created_at, and events_tenant_id_idx is skipped."),
            ("carry-metric", "Because control had only four purchases; the "
             "arms are balanced on device mix."),
            ("carry-rollback", "On the NOT NULL column. Migration 0042 had run "
             "at 14:05 with no default.")):
        assert not carries({"case": case, "text": text}), text

    def run(case, carry, rep):
        return {"ok": True, "case": case, "model": MODEL, "arm": "laconic",
                "rep": rep, "num_turns": 3, "tools": ["Read"],
                "text": "The query. See events_day_tenant_idx." if carry
                else "The query."}
    hi = [run("carry-index", True, i) for i in range(20)]
    lo = [run("carry-index", i < 4, i) for i in range(20)]
    assert fall("selftest", 20, 20, 4, 20)
    assert cell(hi, "carry-index")["carry"] == 20
    assert cell(lo, "carry-index")["carry"] == 4
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
