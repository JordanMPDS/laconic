#!/usr/bin/env python3
"""Round 99: does dropping "Cut content, not words." from the reminder stop #353?

    python3 evals/pilot/score_reminder.py precheck <snapshot> <judgments>
    python3 evals/pilot/score_reminder.py compare <control> <control-judgments> \
        <edit> <edit-judgments>
    python3 evals/pilot/score_reminder.py --selftest

`precheck` is stage 1: panel fails on the sonnet index family at master rules,
against the threshold registered in `round-99.md`. `compare` is stage 2: the
primary (one-sided Fisher on those fails, edit lower), the guard-word bound
(`score_settled.stratified`, one-sided for a rise) and the `recall-metric`
bound. A judgment counts only as `pass` or `fail`; anything else is not a
verdict and is left out of n.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
from score_compression import words  # noqa: E402
from score_settled import fisher_le, fmt_p, stratified  # noqa: E402

SEED = 99
ALPHA = 0.05
FIRES_AT = 12  # of 60 sonnet index-family verdicts
INDEX = ("recall-index", "wide-index", "deep-index")
METRIC = ("recall-metric",)
GUARDS = ("recall-rollback", "wide-rollback", "wide-metric", "deep-rollback",
          "deep-metric", "drift-service")


def load_runs(path):
    return [r for r in json.loads(Path(path).read_text())["runs"]
            if r.get("ok") and r.get("arm") == "laconic"]


def load_verdicts(path):
    return [j for j in json.loads(Path(path).read_text())["judgments"]
            if j.get("arm") == "laconic"]


def fails(verdicts, cases, model="sonnet"):
    """(fails, n) over the named cases on one model."""
    vs = [j for j in verdicts if j["case"] in cases and j["model"] == model
          and j.get("verdict") in ("pass", "fail")]
    return sum(j["verdict"] == "fail" for j in vs), len(vs)


def precheck(verdicts):
    k, n = fails(verdicts, INDEX)
    lines = ["%-14s %s" % (c, "%d/%d" % fails(verdicts, (c,))) for c in INDEX]
    lines.append("%-14s %d/%d  fires at >= %d: %s"
                 % ("sonnet index", k, n, FIRES_AT,
                    "FIRES" if k >= FIRES_AT else "does not fire"))
    lines.append("%-14s %d/%d  (opus, disclosed)" % (("opus index",)
                                                    + fails(verdicts, INDEX, "opus")))
    lines.append("%-14s %d/%d  (disclosed)" % (("recall-metric",)
                                              + fails(verdicts, METRIC)))
    return k >= FIRES_AT, lines


def guard_pairs(control, edit):
    pairs = []
    for model in ("sonnet", "opus"):
        for case in GUARDS:
            pick = lambda rs: [words(r) for r in rs
                               if r["case"] == case and r["model"] == model]
            pairs.append((pick(control), pick(edit)))
    return pairs


def compare(control_runs, control_v, edit_runs, edit_v, resamples=200000):
    """Returns (accept, lines)."""
    ck, cn = fails(control_v, INDEX)
    ek, en = fails(edit_v, INDEX)
    p1 = fisher_le(ek, en - ek, ck, cn - ck)
    primary = ek * cn < ck * en and p1 < ALPHA

    # stratified() tests the second side for a fall, so swapping the sides
    # tests the edit for a rise; its statistic is then control minus edit
    drop, p2 = stratified([(e, c) for c, e in guard_pairs(control_runs, edit_runs)],
                          seed=SEED, resamples=resamples)
    shift = None if drop is None else -drop
    guard = p2 is None or p2 >= ALPHA

    mck, mcn = fails(control_v, METRIC)
    mek, men = fails(edit_v, METRIC)
    # a rise in edit fails is a fall in edit passes
    p3 = fisher_le(men - mek, mek, mcn - mck, mck)
    metric = p3 >= ALPHA

    lines = [
        "primary   index fails  control %d/%d  edit %d/%d  one-sided p %s  %s"
        % (ck, cn, ek, en, fmt_p(p1), "PASS" if primary else "fail"),
        "bound     guard words  mean change %s  one-sided p %s  %s"
        % ("n/a" if shift is None else "%+.1f" % shift,
           "n/a" if p2 is None else fmt_p(p2), "holds" if guard else "BROKEN"),
        "bound     recall-metric fails  control %d/%d  edit %d/%d  p %s  %s"
        % (mck, mcn, mek, men, fmt_p(p3), "holds" if metric else "BROKEN"),
    ]
    accept = primary and guard and metric
    lines.append("verdict: %s" % ("ACCEPT" if accept else "REJECT"))
    return accept, lines


def selftest():
    def v(case, verdict, model="sonnet"):
        return {"arm": "laconic", "case": case, "model": model, "verdict": verdict}

    def r(case, n, model="sonnet"):
        return {"arm": "laconic", "case": case, "model": model, "ok": True,
                "text": "word " * n}

    fired = [v("recall-index", "fail")] * 12 + [v("wide-index", "pass")] * 48
    assert precheck(fired)[0]
    assert not precheck(fired[1:] + [v("deep-index", "pass")])[0]
    assert fails([v("recall-index", "not_exercised")], INDEX) == (0, 0)
    assert fails([v("recall-index", "fail", "opus")], INDEX) == (0, 0)

    guards = [r(c, 50, m) for c in GUARDS for m in ("sonnet", "opus")] * 5
    longer = [r(c, 80, m) for c in GUARDS for m in ("sonnet", "opus")] * 5
    cv = [v("recall-index", "fail")] * 30 + [v("recall-index", "pass")] * 60
    ev = [v("recall-index", "fail")] * 5 + [v("recall-index", "pass")] * 85
    assert compare(guards, cv, guards, ev, resamples=999)[0]
    assert not compare(guards, cv, longer, ev, resamples=999)[0], "guard rise must reject"
    assert not compare(guards, cv, guards, cv, resamples=999)[0], "no fall must reject"
    mv = [v("recall-metric", "fail")] * 10 + [v("recall-metric", "pass")] * 5
    assert not compare(guards, cv + [v("recall-metric", "pass")] * 15,
                       guards, ev + mv, resamples=999)[0], "metric rise must reject"
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if argv[:1] == ["precheck"] and len(argv) == 3:
        ok, lines = precheck(load_verdicts(argv[2]))
        runs = load_runs(argv[1])
        lines.append("sonnet index graded-turn median words %.1f"
                     % metrics.median([words(r) for r in runs
                                       if r["case"] in INDEX
                                       and r["model"] == "sonnet"] or [0]))
        print("\n".join(lines))
        return
    if argv[:1] == ["compare"] and len(argv) == 5:
        ok, lines = compare(load_runs(argv[1]), load_verdicts(argv[2]),
                            load_runs(argv[3]), load_verdicts(argv[4]))
        print("\n".join(lines))
        sys.exit(0 if ok else 1)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
