#!/usr/bin/env python3
"""Round 101: does #46's design essay come back with ponytail co-active, on opus?

    python3 evals/pilot/score_ponytail.py <snap>...
    python3 evals/pilot/score_ponytail.py --selftest

Round 98's instrument, `session-alerting` and `design-alerting` cold, with a
second arm beside `laconic` in the same interleaved pass: `laconic-ponytail`,
the live slice plus ponytail's `full` SessionStart text. #46 was reported with
both plugins at `full`, and no earlier arm carried the second one.

The screen is round 98's, graded turns over `OVER` prose words, read on the
ponytail arm's session cell. `laconic`'s two cells are the in-pass control and
the void condition: either over `CONTROL_MAX` per 20 means the window moved,
and the round reads nothing. Exactly one ponytail session run over is the
registered top-up to `TOPUP_REPS`, where the bar becomes `TOPUP_AT`.

Three labels are printed beside the verdict and decide nothing on their own;
they are registered here so that what each sends next is fixed in advance:

- `cold-fires`: the ponytail cold cell clears the same bar, so the SessionStart
  text alone is enough and the session scaffold is not needed.
- `smoldering`: a null whose ponytail session median is at least `SMOLDER`x
  laconic's at permutation p < `ALPHA`, two-sided, on log prose words.
- `code-balloon`: ponytail session graded turns carrying a fenced block reach
  `BALLOON_AT` per 20 while laconic's stay at `CONTROL_MAX`. Prose words cannot
  see a schema, and ponytail says "Code first".
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
SESSION, COLD = "session-alerting", "design-alerting"
OVER, FIRE_AT, CONTROL_MAX = 600, 2, 1
TOPUP_REPS, TOPUP_AT = 40, 4
SMOLDER, ALPHA, SEED = 1.5, 0.05, 101
BALLOON_AT = 5
H2 = re.compile(r"^##\s", re.M)
FENCE = re.compile(r"^```", re.M)


def load(paths):
    """Usable runs on MODEL in the two arms and two cells, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            key = (r.get("arm"), r.get("case"), r.get("rep"))
            if (key in seen or r.get("arm") not in ARMS or r.get("model") != MODEL
                    or r.get("case") not in (SESSION, COLD)):
                continue
            seen.add(key)
            out.append(r)
    return out


def scaled(per20, n):
    return per20 * max(n, 20) // 20


def score(runs):
    """Return (verdict, labels). Verdict: fires, top-up, null or void."""
    cell = {(a, c): [r for r in runs if r["arm"] == a and r["case"] == c]
            for a in ARMS for c in (SESSION, COLD)}
    over = {k: sum(words(r) > OVER for r in v) for k, v in cell.items()}
    fenced = {k: sum(bool(FENCE.search(r.get("text") or "")) for r in v)
              for k, v in cell.items()}
    for (a, c), v in cell.items():
        w = [words(r) for r in v]
        h2 = [len(H2.findall(r.get("text") or "")) for r in v]
        print("%-16s %-16s n=%2d  median %6.1f  max %5d  over %d: %2d  "
              "fenced %2d  H2 median %.1f"
              % (a, c, len(w), metrics.median(w), max(w, default=0), OVER,
                 over[a, c], fenced[a, c], metrics.median(h2)))

    pt_s = cell["laconic-ponytail", SESSION]
    bar = TOPUP_AT if len(pt_s) >= TOPUP_REPS else FIRE_AT
    if any(over["laconic", c] > scaled(CONTROL_MAX, len(cell["laconic", c]))
           for c in (SESSION, COLD)):
        verdict = "void"
    elif over["laconic-ponytail", SESSION] >= bar:
        verdict = "fires"
    elif over["laconic-ponytail", SESSION] == 1 and len(pt_s) < TOPUP_REPS:
        verdict = "top-up"
    else:
        verdict = "null"

    labels = []
    if over["laconic-ponytail", COLD] >= bar:
        labels.append("cold-fires")
    lw = [math.log(max(words(r), 1)) for r in cell["laconic", SESSION]]
    pw = [math.log(max(words(r), 1)) for r in pt_s]
    ratio = p = None
    if lw and pw:
        ratio = math.exp(metrics.median(pw) - metrics.median(lw))
        p = metrics.permutation(lw, pw, SEED, resamples=20000,
                                stat=metrics.median)
        print("\nsession median ratio ponytail/laconic %.3f, permutation p %.4f "
              "(two-sided, log prose words, seed %d)" % (ratio, p, SEED))
    if verdict == "null" and ratio and ratio >= SMOLDER and p < ALPHA:
        labels.append("smoldering")
    if (fenced["laconic-ponytail", SESSION] >= scaled(BALLOON_AT, len(pt_s))
            and fenced["laconic", SESSION]
            <= scaled(CONTROL_MAX, len(cell["laconic", SESSION]))):
        labels.append("code-balloon")
    print("ponytail session over %d: %d/%d against a bar of %d: %s%s"
          % (OVER, over["laconic-ponytail", SESSION], len(pt_s), bar,
             verdict.upper(), "".join(" [%s]" % l for l in labels)))
    return verdict, labels


def selftest():
    def run(arm, case, rep, graded, code=False):
        text = " ".join(["word"] * graded) + ("\n```\nx\n```" if code else "")
        return {"ok": True, "arm": arm, "model": MODEL, "case": case,
                "rep": rep, "text": text}

    def design(pt_s, pt_c=0, lac_s=0, lac_c=0, reps=20, pt_words=200, code=0):
        out = []
        for arm, case, n_over in (("laconic", SESSION, lac_s), ("laconic", COLD, lac_c),
                                  ("laconic-ponytail", SESSION, pt_s),
                                  ("laconic-ponytail", COLD, pt_c)):
            base = pt_words if arm == "laconic-ponytail" and case == SESSION else 200
            out += [run(arm, case, i, 700 if i < n_over else base + 3 * i,
                        code=arm == "laconic-ponytail" and case == SESSION and i < code)
                    for i in range(reps)]
        return out
    assert score(design(2)) == ("fires", [])
    assert score(design(2, lac_s=1, lac_c=1))[0] == "fires"
    assert score(design(5, lac_s=2))[0] == "void"
    assert score(design(5, lac_c=2))[0] == "void"
    assert score(design(1)) == ("top-up", [])
    assert score(design(0)) == ("null", [])
    assert score(design(3, reps=40))[0] == "null"
    assert score(design(4, lac_s=2, reps=40))[0] == "fires"
    assert score(design(3, pt_c=3)) == ("fires", ["cold-fires"])
    assert score(design(0, pt_words=400)) == ("null", ["smoldering"])
    assert score(design(0, code=5)) == ("null", ["code-balloon"])
    assert score(design(0, code=4)) == ("null", [])
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if not argv:
        sys.exit(__doc__)
    score(load(argv))


if __name__ == "__main__":
    main(sys.argv[1:])
