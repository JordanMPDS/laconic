#!/usr/bin/env python3
"""Round 136: a feasibility question gets the verdict and what decides it (#113).

    python3 evals/pilot/score_feasible_edit.py words <control.json> <edit.json>
    python3 evals/pilot/score_feasible_edit.py longer <control.json> <edit.json>
    python3 evals/pilot/score_feasible_edit.py readability <control.json> <edit.json>
    python3 evals/pilot/score_feasible_edit.py nevercut <control.json> <edit.json>
    python3 evals/pilot/score_feasible_edit.py bounds <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_feasible_edit.py holdout <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_feasible_edit.py --selftest

Round 131 found #113's feasibility question answered at about its reference's
size inside the co-authoring session and at about twice that cold:
`coldfeasible-*` on opus ran medians of 195, 170 and 210 prose words against
references of 82, 65 and 60, with bold labels no session answer carried. Round
136 adds one `level: full` bullet for the shape and reads it here.

**Primary, `words`:** prose words fall on `TARGET`, the three cold cells on
opus, by `score_findings_length`'s statistic, a one-sided stratified
permutation of the side label within each cell on median log words, seed
`SEED`; **and** the factor it prints, exp of the mean log ratio, is
`MIN_FALL` or under. The references are round 131's, frozen in
`score_feasible.py`, and their ratio is disclosed.

**Bound, `longer`:** prose words may not rise on `KEEP`, three cases on other
fixtures whose question is feasibility- or decision-shaped and whose right
answer is conditional, the same statistic with the sides swapped.
**Bound, `readability`:** the share of `TARGET` answers with no `metrics.score`
violation may not fall, pooled, one-sided Fisher.
**Bound, `nevercut`:** on every `BOUNDS` cell whose case lists never-cut
keywords, the share carrying all of them may not fall, one-sided Fisher.
**Bounds, `bounds`:** the panel pass rate may not fall on any `BOUNDS` cell,
each one-sided Fisher at alpha 0.05, uncorrected per `AGENTS.md`, nor on the
`SESSION` cells pooled, whose traps grade the session's last question.
**Holdout, `holdout`:** `score_findings_length.holdout`, unchanged.
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "bench"))
import metrics  # noqa: E402
import score_feasible as sf  # noqa: E402
import score_findings_length as sfl  # noqa: E402
from score_choice import fall  # noqa: E402
from score_compression import words  # noqa: E402
from score_relay import never_cut  # noqa: E402
from score_settled import stratified  # noqa: E402

SEED = 136
MIN_FALL = 0.80
TARGET = tuple(("coldfeasible-" + s, "opus") for s in sf.STEMS)
SONNET = tuple(("coldfeasible-" + s, "sonnet") for s in sf.STEMS)
KEEP = tuple(("keep-" + s, "opus") for s in ("cdc", "disk", "checkout"))
WALK = ("walkthrough", "opus")
SESSION = tuple(("feasible-" + s, "opus") for s in sf.STEMS)
BOUNDS = TARGET + SONNET + KEEP + (WALK,)


def logs(rs):
    return [math.log(max(words(r), 1)) for r in rs]


def primary(control, edit, resamples=sfl.RESAMPLES):
    print("## Primary: prose words fall on coldfeasible-*/opus, one-sided")
    pairs = []
    for c in TARGET:
        cr, er = control.get(c, []), edit.get(c, [])
        pairs.append((logs(cr), logs(er)))
        print("   %-26s control n=%2d median %5.0f  edit n=%2d median %5.0f"
              % ("/".join(c), len(cr), sfl.median([words(r) for r in cr]),
                 len(er), sfl.median([words(r) for r in er])))
    if any(not a or not b for a, b in pairs):
        print("   a cell is empty on one side: the primary is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples)
    factor = math.exp(obs)
    ok = p < sfl.ALPHA and factor <= MIN_FALL
    print("   mean log ratio %.3f (factor %.3f, needs <= %.2f)  one-sided"
          " p = %.5f  %s" % (obs, factor, MIN_FALL, p,
                             "PASSES" if ok else "fails"))
    return ok


def disclose(control, edit):
    print("## Disclosed, deciding nothing: the cold cells against round 131's"
          " references")
    print("   %-26s %5s %8s %6s %6s %6s %6s" % (
        "cell", "side", "median", "ratio", "bolds", "heads", "offers"))
    for c in TARGET + SONNET:
        ref = sf.REF_WORDS[(sf.stem_of(c[0]), sf.ASKED[0])]
        for name, side in (("ctrl", control), ("edit", edit)):
            rs = side.get(c, [])
            w = [words(r) for r in rs]
            sh = [sf.shape(r) for r in rs]
            print("   %-26s %5s %8.1f %6.2f %6.1f %6.1f %6d" % (
                "/".join(c), name, sfl.median(w), sfl.median(w) / ref,
                sfl.median([b for _, b in sh]), sfl.median([a for a, _ in sh]),
                sum(bool(sf.offers(r)) for r in rs)))
    print("## Disclosed: prose words, median, on the other cells")
    for c in KEEP + (WALK,):
        print("   %-26s control %6.1f  edit %6.1f" % (
            "/".join(c), sfl.median([words(r) for r in control.get(c, [])]),
            sfl.median([words(r) for r in edit.get(c, [])])))
    for c in SESSION:
        for idx in sf.ASKED:
            per = [sfl.median([words(r["turns"][idx]) for r in side.get(c, [])
                               if len(r.get("turns") or []) > idx])
                   for side in (control, edit)]
            print("   %-26s turn %d  control %6.1f  edit %6.1f"
                  % ("/".join(c), idx + 1, *per))


def longer(control, edit, resamples=sfl.RESAMPLES):
    print("## Bound (fatal): prose words may not rise on keep-*/opus")
    pairs = [(logs(edit.get(c, [])), logs(control.get(c, []))) for c in KEEP]
    if any(not a or not b for a, b in pairs):
        print("   a cell is empty on one side: the bound is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples)
    fired = p < sfl.ALPHA
    print("   mean log ratio %.3f (factor %.3f)  one-sided p = %.5f  %s"
          % (-obs, math.exp(-obs), p, "FIRES" if fired else "holds"))
    return not fired


def readability(control, edit):
    print("## Bound (fatal): answers with no readability violation, "
          "coldfeasible-*/opus")
    t = [0, 0, 0, 0]
    for c in TARGET:
        a = [metrics.score(r.get("text") or "") for r in control.get(c, [])]
        b = [metrics.score(r.get("text") or "") for r in edit.get(c, [])]
        ca = sum(not x["violations"] for x in a)
        cb = sum(not x["violations"] for x in b)
        t = [t[0] + ca, t[1] + len(a), t[2] + cb, t[3] + len(b)]
        print("   %-26s clean control %2d/%-2d edit %2d/%-2d"
              % ("/".join(c), ca, len(a), cb, len(b)))
    return not fall("pooled", *t)


def nevercut(control, edit):
    print("## Bound (fatal): answers keeping every never-cut keyword")
    fired = False
    for cell in BOUNDS:
        kw = never_cut(cell[0])
        if not kw:
            continue
        a, b = control.get(cell, []), edit.get(cell, [])
        keep = lambda rs: sum(  # noqa: E731
            not metrics.never_cut_missing(r.get("text") or "", kw) for r in rs)
        fired |= fall("/".join(cell), keep(a), len(a), keep(b), len(b))
    return not fired


def bounds(c, e):
    print("## Bounds (fatal): the pass rate may not fall, per cell")
    fired = False
    for cell in BOUNDS:
        fired |= fall("/".join(cell), *sfl.passes(c, [cell]),
                      *sfl.passes(e, [cell]))
    fired |= fall("feasible-*/opus pooled", *sfl.passes(c, SESSION),
                  *sfl.passes(e, SESSION))
    print("## %s" % ("bounds hold" if not fired else "reject"))
    return not fired


def selftest():
    from collections import Counter

    def snap(cells, lengths):
        return {c: [{"text": "Word " * n} for n in lengths] for c in cells}

    long_ = snap(TARGET, [190 + i for i in range(20)])
    short = snap(TARGET, [110 + i for i in range(20)])
    near = snap(TARGET, [175 + i for i in range(20)])
    assert primary(long_, short, resamples=2000)
    assert not primary(long_, long_, resamples=2000)
    # Significant, but not by the margin the round registered.
    assert not primary(long_, near, resamples=2000)
    assert not primary(long_, {}, resamples=2000)
    assert longer(snap(KEEP, [80] * 10), snap(KEEP, [80] * 10), resamples=2000)
    assert not longer(snap(KEEP, [80 + i for i in range(10)]),
                      snap(KEEP, [140 + i for i in range(10)]), resamples=2000)
    clean = snap(TARGET, [60] * 10)
    arrows = {c: [{"text": "It reads the file -> then it fails. " * 3}] * 10
              for c in TARGET}
    assert readability(clean, clean)
    assert not readability(clean, arrows)
    full = {c: Counter({"pass": 10}) for c in BOUNDS + SESSION}
    assert bounds(full, full)
    worse = dict(full)
    worse[KEEP[1]] = Counter({"pass": 4, "fail": 6})
    assert not bounds(full, worse)
    # Five sessions a stem: no stem can fire alone, and the pooled test can.
    ctrl, sess = dict(full), dict(full)
    for c in SESSION:
        ctrl[c], sess[c] = Counter({"pass": 5}), Counter({"pass": 2, "fail": 3})
    assert not bounds(ctrl, sess)
    assert len(BOUNDS) == 10 and len(set(BOUNDS)) == 10
    print("selftest: ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if len(argv) == 3 and argv[0] in ("words", "longer", "readability",
                                      "nevercut"):
        (cm, c), (em, e) = sfl.runs(argv[1]), sfl.runs(argv[2])
        for name, m in (("control", cm), ("edit", em)):
            print("%-8s rules_cksum %s  cli %s" % (
                name, m.get("rules_cksum"), m.get("claude_cli_version")))
        if cm.get("rules_cksum") == em.get("rules_cksum"):
            print("!! both sides share rules_cksum: this is not a contrast")
            return 1
        if argv[0] == "words":
            ok = primary(c, e)
            disclose(c, e)
            return 0 if ok else 1
        fn = {"longer": longer, "readability": readability,
              "nevercut": nevercut}[argv[0]]
        return 0 if fn(c, e) else 1
    if len(argv) == 3 and argv[0] in ("bounds", "holdout"):
        fn = bounds if argv[0] == "bounds" else sfl.holdout
        return 0 if fn(sfl.tally(argv[1]), sfl.tally(argv[2])) else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
