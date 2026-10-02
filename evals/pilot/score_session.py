#!/usr/bin/env python3
"""Round 98: does #46's design essay reproduce in a session, on opus?

    python3 evals/pilot/score_session.py <snap>...
    python3 evals/pilot/score_session.py --selftest

`session-alerting` asks `design-alerting`'s prompt as turn 5, after a turn 1
that summarises the same spec and three closed questions about it. Round 91
read `design-alerting` cold on opus at 0 of 20 over 600 prose words; the
question is whether the model's own account of the spec in context, plus
several terse turns, brings back the answer #46 reported.

It fires when at least `FIRE_AT` of the `session-alerting` graded turns run
over `OVER` prose words and the cold cell, generated in the same pass, stays
at or under `COLD_MAX`. A cold cell over that means the window moved, not the
session, and the round reads nothing. Exactly one session run over is the
registered top-up: both cells extend to 40 reps and the bar becomes `TOPUP_AT`.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402

MODEL = "opus"
SESSION, COLD = "session-alerting", "design-alerting"
OVER, FIRE_AT, COLD_MAX = 600, 2, 1
TOPUP_REPS, TOPUP_AT = 40, 4


def load(paths):
    """Usable laconic runs on MODEL in the two cells, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            key = (r.get("case"), r.get("rep"))
            if (key in seen or r.get("arm") != "laconic" or r.get("model") != MODEL
                    or r.get("case") not in (SESSION, COLD)):
                continue
            seen.add(key)
            out.append(r)
    return out


def turn_words(r, i):
    return words(r["turns"][i]) if len(r.get("turns") or ()) > i else None


def score(runs):
    """'fires', 'top-up', 'null' or 'void' (the cold cell moved)."""
    sess = [r for r in runs if r["case"] == SESSION]
    cold = [r for r in runs if r["case"] == COLD]
    so, co = sum(words(r) > OVER for r in sess), sum(words(r) > OVER for r in cold)
    for name, cell, over in ((SESSION, sess, so), (COLD, cold, co)):
        w = [words(r) for r in cell]
        print("%-17s n=%2d  graded median %6.1f  max %5d  over %d: %d"
              % (name, len(w), metrics.median(w), max(w, default=0), OVER, over))
    for i in range(4):
        t = [x for x in (turn_words(r, i) for r in sess) if x is not None]
        print("  session turn %d median %6.1f  (n=%d)" % (i + 1, metrics.median(t), len(t)))
    bar = TOPUP_AT if len(sess) >= TOPUP_REPS else FIRE_AT
    if co > COLD_MAX * len(cold) // 20:
        verdict = "void"
    elif so >= bar:
        verdict = "fires"
    elif so == 1 and len(sess) < TOPUP_REPS:
        verdict = "top-up"
    else:
        verdict = "null"
    print("\nsession over %d: %d/%d against a bar of %d; cold %d/%d: %s"
          % (OVER, so, len(sess), bar, co, len(cold), verdict.upper()))
    return verdict


def selftest():
    def run(case, rep, graded):
        r = {"ok": True, "arm": "laconic", "model": MODEL, "case": case, "rep": rep,
             "text": " ".join(["word"] * graded)}
        if case == SESSION:
            r["turns"] = [{"text": "word " * 400}] + [{"text": "word " * 20}] * 3 + [{"text": r["text"]}]
        return r

    def cells(n_sess_over, n_cold_over, reps=20):
        return ([run(SESSION, i, 700 if i < n_sess_over else 200) for i in range(reps)]
                + [run(COLD, i, 700 if i < n_cold_over else 200) for i in range(reps)])
    assert score(cells(2, 0)) == "fires"
    assert score(cells(2, 1)) == "fires"
    assert score(cells(3, 2)) == "void"
    assert score(cells(1, 0)) == "top-up"
    assert score(cells(0, 0)) == "null"
    assert score(cells(3, 0, reps=40)) == "null"
    assert score(cells(4, 2, reps=40)) == "fires"
    assert score(cells(4, 3, reps=40)) == "void"
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if not argv:
        sys.exit(__doc__)
    score(load(argv))


if __name__ == "__main__":
    main(sys.argv[1:])
