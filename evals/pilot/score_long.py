#!/usr/bin/env python3
"""Round 103: does #46's design essay come back over a long design document?

    python3 evals/pilot/score_long.py <snap>...
    python3 evals/pilot/score_long.py --selftest

`session-alerting-long` is `session-alerting` byte for byte over a 2,578-word
SPEC.md of the same system instead of the 458-word one. #46 was reported in a
session over a long internal design document, with ponytail co-active at
`full`, and every earlier instrument used the short spec. Both arms of round
101 run on both cases in one interleaved pass, the short cells at half the reps
as the in-pass anchor.

The screen is round 98's, graded turns over `OVER` prose words, read on the
`laconic-ponytail` arm's long cell, which is the report's condition. Either
short cell over `CONTROL_MAX` per 20 means the window moved, and the round
reads nothing. Exactly one long ponytail run over is the registered top-up to
`TOPUP_REPS`, where the bar becomes `TOPUP_AT`.

Two labels print beside the verdict and decide nothing on their own:

- `long-fires`: the `laconic` long cell clears the same bar, so the document
  is enough without the second plugin.
- `dose`: a null whose long ponytail median is at least `DOSE`x the short
  ponytail median at permutation p < `ALPHA`, two-sided, on log prose words.
  The document lengthens the answer below the essay regime.

Turn-1 summary medians, H2 and fenced-block counts, and the rank correlation
between a run's turn-1 summary and its graded turn are printed as disclosure.
"""
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402

MODEL = "opus"
ARMS = ("laconic", "laconic-ponytail")
LONG, SHORT = "session-alerting-long", "session-alerting"
OVER, FIRE_AT, CONTROL_MAX = 600, 2, 1
TOPUP_REPS, TOPUP_AT = 40, 4
DOSE, ALPHA, SEED = 1.5, 0.05, 103
H2 = re.compile(r"^##\s", re.M)
FENCE = re.compile(r"^```", re.M)


def load(paths):
    """Usable runs on MODEL in the two arms and two cases, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            key = (r.get("arm"), r.get("case"), r.get("rep"))
            if (key in seen or r.get("arm") not in ARMS or r.get("model") != MODEL
                    or r.get("case") not in (LONG, SHORT)):
                continue
            seen.add(key)
            out.append(r)
    return out


def scaled(per20, n):
    return per20 * max(n, 20) // 20


def turn1(r):
    t = r.get("turns") or ()
    return words(t[0]) if t else None


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2
        i = j + 1
    return out


def spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def score(runs):
    """Return (verdict, labels). Verdict: fires, top-up, null or void."""
    cell = {(a, c): [r for r in runs if r["arm"] == a and r["case"] == c]
            for a in ARMS for c in (LONG, SHORT)}
    over = {k: sum(words(r) > OVER for r in v) for k, v in cell.items()}
    for (a, c), v in cell.items():
        w = [words(r) for r in v]
        t1 = [x for x in map(turn1, v) if x is not None]
        print("%-16s %-21s n=%2d  median %6.1f  max %5d  over %d: %2d  "
              "fenced %2d  H2 median %.1f  turn-1 median %6.1f"
              % (a, c, len(w), metrics.median(w), max(w, default=0), OVER,
                 over[a, c], sum(bool(FENCE.search(r.get("text") or "")) for r in v),
                 metrics.median([len(H2.findall(r.get("text") or "")) for r in v]),
                 metrics.median(t1)))

    pt_l = cell["laconic-ponytail", LONG]
    bar = TOPUP_AT if len(pt_l) >= TOPUP_REPS else FIRE_AT
    if any(over[a, SHORT] > scaled(CONTROL_MAX, len(cell[a, SHORT])) for a in ARMS):
        verdict = "void"
    elif over["laconic-ponytail", LONG] >= bar:
        verdict = "fires"
    elif over["laconic-ponytail", LONG] == 1 and len(pt_l) < TOPUP_REPS:
        verdict = "top-up"
    else:
        verdict = "null"

    labels = []
    lac_bar = TOPUP_AT if len(cell["laconic", LONG]) >= TOPUP_REPS else FIRE_AT
    if over["laconic", LONG] >= lac_bar:
        labels.append("long-fires")
    sw = [math.log(max(words(r), 1)) for r in cell["laconic-ponytail", SHORT]]
    lw = [math.log(max(words(r), 1)) for r in pt_l]
    ratio = p = None
    if sw and lw:
        ratio = math.exp(metrics.median(lw) - metrics.median(sw))
        p = metrics.permutation(sw, lw, SEED, resamples=20000, stat=metrics.median)
        print("\nponytail median ratio long/short %.3f, permutation p %.4f "
              "(two-sided, log prose words, seed %d)" % (ratio, p, SEED))
    if verdict == "null" and ratio and ratio >= DOSE and p < ALPHA:
        labels.append("dose")
    for a in ARMS:
        pairs = [(turn1(r), words(r)) for r in cell[a, LONG] if turn1(r) is not None]
        rho = spearman([x for x, _ in pairs], [y for _, y in pairs])
        if rho is not None:
            print("%s long: Spearman turn-1 summary against graded turn %.3f (n=%d)"
                  % (a, rho, len(pairs)))
    print("ponytail long over %d: %d/%d against a bar of %d: %s%s"
          % (OVER, over["laconic-ponytail", LONG], len(pt_l), bar,
             verdict.upper(), "".join(" [%s]" % l for l in labels)))
    return verdict, labels


def selftest():
    def run(arm, case, rep, graded, first=300):
        return {"ok": True, "arm": arm, "model": MODEL, "case": case, "rep": rep,
                "text": " ".join(["word"] * graded),
                "turns": [{"text": " ".join(["word"] * first)}]}

    def design(pt_l, lac_l=0, pt_s=0, lac_s=0, reps=20, long_words=200):
        out = []
        for arm, case, n_over, n in (("laconic", LONG, lac_l, reps),
                                     ("laconic-ponytail", LONG, pt_l, reps),
                                     ("laconic", SHORT, lac_s, 10),
                                     ("laconic-ponytail", SHORT, pt_s, 10)):
            base = long_words if case == LONG else 200
            out += [run(arm, case, i, 700 if i < n_over else base + 3 * i, 300 + i)
                    for i in range(n)]
        return out
    assert score(design(2)) == ("fires", [])
    assert score(design(2, lac_l=2)) == ("fires", ["long-fires"])
    assert score(design(5, pt_s=2))[0] == "void"
    assert score(design(5, lac_s=2))[0] == "void"
    assert score(design(5, lac_s=1, pt_s=1))[0] == "fires"
    assert score(design(1)) == ("top-up", [])
    assert score(design(0)) == ("null", [])
    assert score(design(3, reps=40))[0] == "null"
    assert score(design(4, reps=40))[0] == "fires"
    assert score(design(0, long_words=400)) == ("null", ["dose"])
    assert score(design(0, long_words=260)) == ("null", [])
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if not argv:
        sys.exit(__doc__)
    score(load(argv))


if __name__ == "__main__":
    main(sys.argv[1:])
