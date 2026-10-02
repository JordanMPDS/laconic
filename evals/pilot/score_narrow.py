#!/usr/bin/env python3
"""Round 92: #305's narrowing follow-up, decided on opus.

    python3 evals/pilot/score_narrow.py precheck <snap>...
    python3 evals/pilot/score_narrow.py compare --control <snap>... --edit <snap>... \
        [--control-judgments <j>] [--edit-judgments <j>]
    python3 evals/pilot/score_narrow.py --selftest

`narrow-*` asks `settled-*`'s one-word question as turn 2, after a turn 1 that
requested a full inventory of the same record. Round 91 read `settled-*` cold
on opus at 30 of 30 answering `Yes.`; the question here is whether the prior
inventory inflates the same answer, which is the shape #305 was reported in.

**precheck** reads master rules only. It fires when at least `FIRE_AT` of the
graded turns run over `OVER` prose words, round 91's threshold on the same
question.

**compare** is stage 2, bought only if the precheck fires. The primary is the
difference of differences on log prose words of the graded turn, edit minus
control on `narrow` minus the same on `settled`, by `metrics`'s aligned-residual
permutation. Below 1 as a ratio of ratios is the registered direction. Two
fatal bounds: turn 1's inventory, which the user asked for, may not get shorter
(one-sided permutation on mean log words), and the panel's pass rate on the `narrow`
graded turn may not fall (one-sided Fisher).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_structure import fisher_one_sided_fall  # noqa: E402

MODEL = "opus"
STEMS = ("failover", "retention", "rounding")
FAMILIES = ("settled", "narrow")
OVER, FIRE_AT = 80, 9
ALPHA = 0.05
SEED = 92


def load(paths):
    """Usable laconic runs on MODEL in the two families, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            fam, _, stem = r.get("case", "").partition("-")
            key = (r.get("case"), r.get("model"), r.get("arm"), r.get("rep"))
            if (key in seen or r.get("arm") != "laconic" or r.get("model") != MODEL
                    or fam not in FAMILIES or stem not in STEMS):
                continue
            seen.add(key)
            out.append(r)
    return out


def family(r):
    return r["case"].split("-", 1)[0]


def turn1_words(r):
    return words(r["turns"][0]) if r.get("turns") else None


def precheck(runs):
    narrow = [r for r in runs if family(r) == "narrow"]
    over = sum(words(r) > OVER for r in narrow)
    print("narrow-* graded turn on %s, master rules: %d runs" % (MODEL, len(narrow)))
    for stem in STEMS:
        cell = [words(r) for r in narrow if r["case"] == "narrow-" + stem]
        t1 = [turn1_words(r) for r in narrow if r["case"] == "narrow-" + stem]
        print("  %-10s n=%2d  graded median %6.1f  over %d: %2d   turn-1 median %6.1f"
              % (stem, len(cell), metrics.median(cell), OVER,
                 sum(w > OVER for w in cell), metrics.median([w for w in t1 if w is not None])))
    fired = over >= FIRE_AT
    print("\nover %d prose words: %d/%d, fires at >= %d: %s"
          % (OVER, over, len(narrow), FIRE_AT, "FIRES" if fired else "does not fire"))
    return fired


def verdicts(path):
    """{(case, rep): verdict} for laconic on MODEL from a judgments file."""
    if not path:
        return {}
    out = {}
    for j in json.loads(Path(path).read_text())["judgments"]:
        if j.get("arm") == "laconic" and j.get("model") == MODEL:
            out[(j["case"], j["rep"])] = j.get("verdict")
    return out


def compare(control, edit, cj=None, ej=None):
    """Print every bar; return True only if the primary passes and both bounds hold."""
    groups = {}
    for side, runs in (("control", control), ("edit", edit)):
        for fam in FAMILIES:
            groups[(side, fam)] = [words(r) for r in runs if family(r) == fam]
    for k, v in groups.items():
        print("  %-8s %-8s n=%3d  median %6.1f" % (k[0], k[1], len(v), metrics.median(v)))
    if any(not v for v in groups.values()):
        print("a group is empty: no verdict")
        return False
    logged = {k: [math.log(max(w, 1)) for w in v] for k, v in groups.items()}
    did = metrics.difference_of_differences(logged, ("control", "edit"), FAMILIES)
    p = metrics.interaction_permutation(logged, ("control", "edit"), FAMILIES, SEED)
    primary = did < 0 and p < ALPHA
    print("\nprimary: ratio of ratios %.3f, aligned-residual p = %.4f: %s"
          % (math.exp(did), p, "PASS" if primary else "fail"))

    t1 = {s: [turn1_words(r) for r in runs if family(r) == "narrow"]
          for s, runs in (("control", control), ("edit", edit))}
    mc, me = metrics.median(t1["control"]), metrics.median(t1["edit"])
    p1 = metrics.permutation([math.log(max(w, 1)) for w in t1["control"]],
                             [math.log(max(w, 1)) for w in t1["edit"]], SEED)
    p1 = None if p1 is None else (p1 / 2 if me < mc else 1 - p1 / 2)
    t1_holds = p1 is None or p1 >= ALPHA
    print("bound, turn-1 inventory words: control %.1f, edit %.1f, one-sided p = %s: %s"
          % (mc, me, "-" if p1 is None else "%.4f" % p1, "holds" if t1_holds else "FATAL"))

    q_holds = True
    vc, ve = verdicts(cj), verdicts(ej)
    if vc and ve:
        def rate(v, runs):
            got = [v.get((r["case"], r["rep"])) for r in runs if family(r) == "narrow"]
            got = [g for g in got if g in ("pass", "fail")]
            return sum(g == "pass" for g in got), len(got)
        a, n1 = rate(vc, control)
        c, n2 = rate(ve, edit)
        pq = fisher_one_sided_fall(a, n1, c, n2)
        q_holds = pq >= ALPHA
        print("bound, narrow graded-turn quality: control %d/%d, edit %d/%d, one-sided p = %.4f: %s"
              % (a, n1, c, n2, pq, "holds" if q_holds else "FATAL"))
    else:
        print("bound, quality: not read (no judgments passed)")
    return primary and t1_holds and q_holds


def selftest():
    def run(case, rep, graded, t1=300):
        text = " ".join(["word"] * graded)
        r = {"ok": True, "arm": "laconic", "model": MODEL, "case": case, "rep": rep,
             "text": text}
        if case.startswith("narrow"):
            r["turns"] = [{"text": " ".join(["word"] * t1)}, {"text": text}]
        return r
    fire = [run("narrow-" + s, i, 120 if i < 3 else 5) for s in STEMS for i in range(10)]
    assert precheck(fire)
    assert not precheck([run("narrow-" + s, i, 120 if i < 2 else 5) for s in STEMS for i in range(10)])
    ctl = ([run("settled-" + s, i, 2 + i % 2) for s in STEMS for i in range(10)]
           + [run("narrow-" + s, i, 100 + i) for s in STEMS for i in range(10)])
    good = ([run("settled-" + s, i, 2 + i % 2) for s in STEMS for i in range(10)]
            + [run("narrow-" + s, i, 10 + i) for s in STEMS for i in range(10)])
    assert compare(ctl, good)
    bad_t1 = ([run("settled-" + s, i, 2 + i % 2) for s in STEMS for i in range(10)]
              + [run("narrow-" + s, i, 10 + i, t1=100) for s in STEMS for i in range(10)])
    assert not compare(ctl, bad_t1)
    assert not compare(ctl, ctl)
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["precheck"] and len(argv) > 1:
        precheck(load(argv[1:]))
        return
    if argv[:1] == ["compare"]:
        opts, cur = {}, None
        for a in argv[1:]:
            if a.startswith("--"):
                cur = a
                opts.setdefault(cur, [])
            else:
                opts[cur].append(a)
        ok = compare(load(opts["--control"]), load(opts["--edit"]),
                     (opts.get("--control-judgments") or [None])[0],
                     (opts.get("--edit-judgments") or [None])[0])
        sys.exit(0 if ok else 1)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
