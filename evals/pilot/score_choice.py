#!/usr/bin/env python3
"""Round 105: is an either/or question answered by naming one option? (#384)

    python3 evals/pilot/score_choice.py --precheck <master.json>
    python3 evals/pilot/score_choice.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json>]
    python3 evals/pilot/score_choice.py --selftest

[#384] reports an either/or question that named both options answered in 156
words on opus, of which the first 8 were the whole answer. The rules' only
worked closed question is a confirmation, and on opus that one already works:
`settled-*` reads a median of 1 word at master rules. `choose-*` asks the
either/or shape over the `deep-*` fixtures, one option the record's answer and
the other on its own ruled-out list. `neither-*` asks over the same fixture
with both options ruled out, so a complete answer is "neither" and the cause.

**Stage 1, `--precheck`:** at master rules, opus, the defect fires when at
least `FIRE_K` of the `choose-*` runs exceed `FIRE_WORDS` prose words and at
least `FIRE_STEM_K` of each stem's do, so one fixture cannot buy the round.

**Primary:** prose words on `choose-*`, opus, as `score_settled.stratified`'s
one-sided permutation within each stem (mean over stems of edit median minus
control median), seed 105. A stem whose reading rate differs between the sides,
or that holds a mutating run, does not vote ([#131], [#209]).

**Fatal bounds**, one-sided Fisher for a fall, uncorrected:
- `neither-*` answers carrying the record's actual cause (`MECHANISM`), pooled.
  This is the bare-answer regression [#353] reports, in the either/or shape.
- panel-judged pass rate on `choose-*`, `neither-*` and `confirm-*`, pooled
  per family, when the judgments are given. `confirm-*` is the scored suite's
  wrong-premise confirmation, borrowed by symlink, where [#353]'s bare "No"
  was observed and where the edit's last sentence could spill.
- `date_trunc` kept on `confirm-index`, the one never-cut keyword these
  cells carry.
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
from score_compression import words  # noqa: E402
from score_settled import fmt_p, stratified, votes  # noqa: E402
from score_structure import fisher_one_sided_fall  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

SEED = 105
MODEL = "opus"
ALPHA = 0.05
STEMS = ("index", "metric", "rollback")
FAMILIES = ("choose", "neither", "confirm")
FIRE_WORDS = 45
FIRE_K = 10
FIRE_STEM_K = 3

#: The record's actual cause, per stem. A `neither-*` answer that rejects both
#: options and names none of this is the regression the bound exists to catch.
MECHANISM = {
    "index": re.compile(
        r"(seq(uential)?[\s-]*scan|date_trunc|full[\s-]*table[\s-]*scan)", re.I),
    "metric": re.compile(
        r"(\b(four|4)\b[^.]{0,30}purchases|purchases?[^.]{0,20}\b(four|4)\b"
        r"|few(er)? purchases|34,?000|sample size|underpowered)", re.I),
    "rollback": re.compile(
        r"(not[\s-]?null|settlement_currency|0042|migration)", re.I),
}


def names_cause(run):
    stem = (run.get("case") or "").split("-", 1)[-1]
    pat = MECHANISM.get(stem)
    return bool(pat and pat.search(run.get("text") or ""))


def cell(runs, case):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == MODEL
          and r.get("arm") == "laconic"]
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "cause": sum(1 for r in rs if names_cause(r)),
        "words": [words(r) for r in rs],
    }


def load(path):
    return json.loads(Path(path).read_text())["runs"]


def precheck(runs):
    print("## Stage 1: does #384 fire on %s at master rules?" % MODEL)
    over = total = 0
    every_stem = True
    for stem in STEMS:
        c = cell(runs, "choose-" + stem)
        k = sum(1 for w in c["words"] if w > FIRE_WORDS)
        over, total = over + k, total + c["n"]
        every_stem &= k >= FIRE_STEM_K
        print("   choose-%-8s n %2d  median %6.1f  over %d words %2d  read %2d"
              % (stem, c["n"], metrics.median(c["words"]), FIRE_WORDS, k,
                 c["grounded"]))
    for stem in STEMS:
        c = cell(runs, "neither-" + stem)
        print("   neither-%-7s n %2d  median %6.1f  names the cause %2d  "
              "(disclosed)" % (stem, c["n"], metrics.median(c["words"]),
                               c["cause"]))
    fires = over >= FIRE_K and every_stem
    print("   %d of %d over %d words, %s stem at %d or more: %s" % (
        over, total, FIRE_WORDS, "every" if every_stem else "not every",
        FIRE_STEM_K, "fires, stage 2 is bought" if fires else "does not fire"))
    return fires


def primary(control, edit):
    print("## Primary: prose words on choose-*, %s, stem-stratified, one-sided"
          % MODEL)
    pairs = []
    for stem in STEMS:
        a, b = cell(control, "choose-" + stem), cell(edit, "choose-" + stem)
        ok, crossed, mixed = votes(a, b)
        print("   choose-%-8s control %3d median %6.1f  edit %3d median %6.1f"
              "  %s" % (stem, a["n"], metrics.median(a["words"]), b["n"],
                        metrics.median(b["words"]),
                        "votes" if ok else "does not vote (%s)" % (
                            "reading rate differs" if crossed else "mutating run")))
        if ok:
            pairs.append((a["words"], b["words"]))
    stat, p = stratified(pairs, seed=SEED)
    passed = p is not None and p < ALPHA and stat < 0
    print("   mean median shift %s words, p = %s: %s" % (
        "-" if stat is None else "%+.1f" % stat, fmt_p(p),
        "passes" if passed else "does not pass"))
    return passed


def fall(name, a, n1, c, n2):
    p = fisher_one_sided_fall(a, n1, c, n2) if n1 and n2 else float("nan")
    fired = p < ALPHA
    print("   %-28s control %3d/%-3d  edit %3d/%-3d  one-sided p = %.4f  %s"
          % (name, a, n1, c, n2, p, "FIRES" if fired else "holds"))
    return fired


def mechanism(control, edit):
    print("## Bound (fatal): neither-* names the record's cause")
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a, b = cell(control, "neither-" + stem), cell(edit, "neither-" + stem)
        t = [t[0] + a["cause"], t[1] + a["n"], t[2] + b["cause"], t[3] + b["n"]]
        print("   neither-%-7s control %3d/%-3d median %6.1f  edit %3d/%-3d "
              "median %6.1f" % (stem, a["cause"], a["n"],
                                metrics.median(a["words"]), b["cause"], b["n"],
                                metrics.median(b["words"])))
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
    print("## Bound (fatal): date_trunc kept on confirm-index")
    out = []
    for runs in (control, edit):
        rs = [r for r in bench_run.usable(runs) if r.get("case") == "confirm-index"
              and r.get("model") == MODEL and r.get("arm") == "laconic"]
        out += [sum(1 for r in rs if not metrics.never_cut_missing(
            r.get("text") or "", ["date_trunc"])), len(rs)]
    return fall("confirm-index", *out)


def main(argv):
    if argv[:1] == ["--precheck"] and len(argv) == 2:
        return 0 if precheck(load(argv[1])) else 1
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    control, edit = load(argv[0]), load(argv[1])
    ok = primary(control, edit)
    fired = mechanism(control, edit)
    fired |= kept(control, edit)
    if len(argv) == 4:
        fired |= quality(argv[2], argv[3])
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    def run(case, n_words, cause=True, rep=0):
        text = " ".join(["word"] * n_words)
        if cause:
            text += " the migration"
        return {"ok": True, "case": case, "model": MODEL, "arm": "laconic",
                "rep": rep, "num_turns": 3, "tools": ["Read"], "text": text}
    long = [run("choose-%s" % s, 120, rep=i) for s in STEMS for i in range(10)]
    short = [run("choose-%s" % s, 10, rep=i) for s in STEMS for i in range(10)]
    assert sum(1 for r in long if words(r) > FIRE_WORDS) == 30
    assert names_cause({"case": "neither-rollback",
                        "text": "Neither; migration 0042 added a NOT NULL column."})
    assert names_cause({"case": "neither-metric",
                        "text": "Neither. Control had only four purchases."})
    assert not names_cause({"case": "neither-index", "text": "Neither of those."})
    stat, p = stratified([(c, e) for c, e in zip(
        [[words(r) for r in long if r["case"] == "choose-" + s] for s in STEMS],
        [[words(r) for r in short if r["case"] == "choose-" + s] for s in STEMS])],
        seed=SEED, resamples=2000)
    assert stat < 0 and p < ALPHA, (stat, p)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
