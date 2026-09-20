"""What a judged floor does and does not buy [#136]'s over-length detector.

    python3 evals/results/loop/judged-ceiling/ceiling.py
    python3 evals/results/loop/judged-ceiling/ceiling.py --demo

[`../judged-floor-136.md`](../judged-floor-136.md) established the floor and
falsified the reason 11 of 30 hand-read hits were excused. It named the one
thing left: *"A detector firing at, say, twice its case's judged floor is one
hand-labelled draw away from being measurable, and this document does not claim
the draw."* This script is what was computed instead of claiming it.

Four tables, each answering one question about that sentence, and none of them
costs a generation, a judge call or a label:

1. **The ratio shape is two detectors.** `K x floor` sets the surplus a
   response may carry to `(K-1) x floor`, and the floors on the thirteen closed
   cases span 12 to 64 words for the same trap. So a fixed `K` convicts 60
   surplus words on one case and acquits them on another.
2. **The floor-derived cutoff does not move precision on the labels that
   exist.** Re-scoring the 30 committed labels under every shape leaves strict
   precision where the global 80 left it.
3. **Most of what a floor-derived cutoff adds is unlabelled and shorter.** The
   cutoff sits below 80 on ten of the thirteen cases, so it admits hits nobody
   has read, and they are shorter than the ones that were.
4. **The harm is not verbatim cross-turn reuse either.** [#136] reports an
   argument re-derived inside a session; every prior turn is stored on nine of
   the thirteen cases, and the graded turn shares almost no phrasing with them.

Nothing here is imported by `evals/bench/metrics.py` and nothing has a
`POLICY_RANK` entry, for the same reason `../closed-question/detector.py` does
not: a detector this imprecise may not name a rule.
"""
import collections
import glob
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "judged-floor"))
sys.path.insert(0, os.path.join(HERE, "..", "closed-question"))
sys.path.insert(0, os.path.join(ROOT, "evals", "bench"))
import floor as floorlib  # noqa: E402
import sweep  # noqa: E402
import detector  # noqa: E402

LABELS = os.path.join(HERE, "..", "closed-question", "labels.json")

# The shapes a floor-derived cutoff can take. Reported as curves rather than as
# a choice: `../closed-question-136.md` printed the whole 20-to-200 threshold
# curve rather than resting on [#136]'s 80, and picking one point here after
# seeing the rates is the tuning that document avoided.
RATIOS = (1.5, 2.0, 2.5, 3.0)
SURPLUSES = (20, 40, 60, 80)

# The nine closed cases whose runs carry the model's own earlier turns.
# `confirm-*` is cold by construction and `quota-merge` is one turn, so four of
# the thirteen have no transcript for a cross-turn check to read.
FENCE = re.compile(r"```.*?```", re.S)
TICK = re.compile(r"`[^`]*`")
WORD = re.compile(r"[a-z0-9']+")
NGRAM = 6


def floors():
    """Per closed case: the judged floor, in prose words."""
    rows, _ = floorlib.load()
    fl = floorlib.floors(floorlib.per_text(rows))
    return {c: fl[c]["strict"][0] for c in sweep.closed_cases()
            if fl.get(c) and fl[c]["strict"]}


def fires_ratio(words, fl, k):
    return words > k * fl


def fires_surplus(words, fl, m):
    return words - fl > m


def archive():
    """Every stored response on the closed cases, de-duplicated by text."""
    return sweep.load_archive(sweep.closed_cases())


# --- table 1: the ratio shape is two detectors ------------------------------

def two_detectors(fl, rows):
    """What surplus each shape tolerates, and what each one fires on.

    The ratio's allowance is `(K-1) x floor`, so it is a per-case constant that
    nobody chose. `confirm-rollback` may carry 64 surplus words at K=2 and
    `recall-index` may carry 12.
    """
    lac = [r for r in rows if r["arm"] == "laconic"]
    out = []
    for case in sorted(fl):
        f = fl[case]
        runs = [r for r in lac if r["case"] == case]
        n = len(runs)
        rate = lambda pred: ("%d/%d" % (sum(1 for r in runs if pred(r)), n)) if n else "-"
        out.append((case, f, f, rate(lambda r: fires_ratio(r["words"], f, 2.0)),
                    rate(lambda r: fires_surplus(r["words"], f, 40))))
    return out


def print_two_detectors(fl, rows):
    print("## 1. `K x floor` tolerates a different surplus on every case")
    print()
    print("%-18s %7s %11s %12s %14s"
          % ("case", "floor", "allowance", "fires @2x", "fires @+40"))
    for case, f, allow, r2, s40 in two_detectors(fl, rows):
        print("%-18s %7d %11d %12s %14s" % (case, f, allow, r2, s40))
    print()
    spread = sorted(fl.values())
    print("The allowance at K=2 is the floor itself, so it spans %d to %d words "
          "across cases asking the same trap." % (spread[0], spread[-1]))
    print()


# --- table 2: the labels that exist -----------------------------------------

def rescore_labels(fl):
    """Every committed label, re-scored under each shape.

    The 30 labels were drawn at [#136]'s global 80 and carry three values:
    `violation`, `borderline` and `not`. Strict precision counts violations
    alone; generous counts borderlines with them, which is the pair
    `../closed-question-136.md` reports and the gap it calls the finding.
    """
    labels = json.load(open(LABELS))["labels"]
    out = []
    for name, keep in (
            [("80 words (as drawn)", lambda l: True)]
            + [("%.1fx floor" % k,
                lambda l, k=k: fires_ratio(l["words"], fl[l["case"]], k))
               for k in RATIOS]
            + [("floor +%d" % m,
                lambda l, m=m: fires_surplus(l["words"], fl[l["case"]], m))
               for m in SURPLUSES]):
        kept = [l for l in labels if keep(l)]
        c = collections.Counter(l["label"] for l in kept)
        n = len(kept)
        out.append((name, n, c["violation"], c["borderline"], c["not"],
                    c["violation"] / n if n else None,
                    (c["violation"] + c["borderline"]) / n if n else None))
    return out


def print_rescore(fl):
    print("## 2. No shape moves precision on the thirty labels that exist")
    print()
    print("%-20s %5s %6s %6s %5s %9s %9s"
          % ("cutoff", "kept", "viol", "bord", "not", "strict", "generous"))
    for name, n, v, b, no, s, g in rescore_labels(fl):
        print("%-20s %5d %6d %6d %5d %9s %9s"
              % (name, n, v, b, no,
                 "-" if s is None else "%.1f%%" % (100 * s),
                 "-" if g is None else "%.1f%%" % (100 * g)))
    print()


# --- table 3: what a floor-derived cutoff adds ------------------------------

def admitted(fl, rows):
    """Hits each shape adds below 80 words, which no label covers.

    A precision figure cannot be carried across a threshold that admits hits
    nobody read. This counts them and reports how long they are, because the
    added hits being *shorter* than the labelled ones is what decides whether
    the existing 30.0% is an optimistic or a pessimistic read of the new
    cutoff.
    """
    lac = [r for r in rows if r["arm"] == "laconic"]
    out = []
    for name, pred in ([("%.1fx floor" % k,
                         lambda r, k=k: fires_ratio(r["words"], fl[r["case"]], k))
                        for k in RATIOS]
                       + [("floor +%d" % m,
                           lambda r, m=m: fires_surplus(r["words"], fl[r["case"]], m))
                          for m in SURPLUSES]):
        hits = [r for r in lac if r["case"] in fl and pred(r)]
        below = [r for r in hits if r["words"] <= detector.LIMIT]
        out.append((name, len(hits), len(below),
                    statistics.median(r["words"] for r in below) if below else None,
                    statistics.median(r["words"] for r in hits) if hits else None))
    return out


def print_admitted(fl, rows):
    print("## 3. What each shape admits that the global 80 did not")
    print()
    print("%-20s %7s %11s %13s %11s"
          % ("cutoff", "hits", "<= 80 words", "median of new", "median all"))
    for name, n, nb, mb, ma in admitted(fl, rows):
        print("%-20s %7d %11d %13s %11s"
              % (name, n, nb, "-" if mb is None else "%.0f" % mb,
                 "-" if ma is None else "%.0f" % ma))
    print()
    cases_below = sorted(c for c, f in fl.items() if 2.0 * f < detector.LIMIT)
    print("At K=2 the cutoff sits below 80 words on %d of %d cases: %s."
          % (len(cases_below), len(fl), ", ".join("`%s`" % c for c in cases_below)))
    print()


# --- table 4: the session-local check ---------------------------------------

def tokens(text):
    return WORD.findall(TICK.sub(" ", FENCE.sub(" ", text or "")).lower())


def reuse(graded, prior, n=NGRAM):
    """Share of the graded turn inside some n-gram it already used earlier.

    Bag-of-words overlap cannot answer this: every turn in these cases is about
    one fixture, so the vocabulary is shared by construction. A run of six
    words is not.
    """
    g, p = tokens(graded), tokens(prior)
    if len(g) < n:
        return None
    grams = {tuple(p[i:i + n]) for i in range(len(p) - n + 1)}
    hit = [False] * len(g)
    for i in range(len(g) - n + 1):
        if tuple(g[i:i + n]) in grams:
            for j in range(i, i + n):
                hit[j] = True
    return sum(hit) / len(g)


def cross_turn():
    """Every de-duplicated multi-turn run on the closed cases, by arm."""
    cases = set(sweep.closed_cases())
    seen, by_arm, by_case = set(), collections.defaultdict(list), collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "evals", "snapshots", "**", "*.json"),
                                 recursive=True)):
        try:
            doc = json.load(open(path))
        except Exception:
            continue
        for run in doc.get("runs") or []:
            if not isinstance(run, dict) or not run.get("ok") or not run.get("text"):
                continue
            if run.get("case") not in cases or not run.get("turns"):
                continue
            digest = hashlib.sha1(run["text"].encode()).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            prior = "\n".join(t.get("text") or "" for t in run["turns"][:-1])
            share = reuse(run["text"], prior)
            if share is None:
                continue
            by_arm[run.get("arm")].append(share)
            by_case[(run["case"], run.get("arm"))].append(share)
    return by_arm, by_case


def print_cross_turn():
    by_arm, by_case = cross_turn()
    print("## 4. The graded turn does not reuse the phrasing of the turns before it")
    print()
    print("%-18s %6s %8s %8s %8s %8s"
          % ("arm", "n", "median", "mean", "p90", "max"))
    for arm in sorted(by_arm):
        v = sorted(by_arm[arm])
        n = len(v)
        print("%-18s %6d %8.3f %8.3f %8.3f %8.3f"
              % (arm, n, statistics.median(v), sum(v) / n, v[min(n - 1, int(0.9 * n))], v[-1]))
    print()
    print("%-18s %-16s %6s %8s" % ("case", "arm", "n", "median"))
    for (case, arm), v in sorted(by_case.items()):
        if arm not in ("laconic", "baseline"):
            continue
        print("%-18s %-16s %6d %8.3f" % (case, arm, len(v), statistics.median(v)))
    print()


def main():
    if "--demo" in sys.argv:
        return demo()
    fl = floors()
    rows = archive()
    print_two_detectors(fl, rows)
    print_rescore(fl)
    print_admitted(fl, rows)
    print_cross_turn()


def demo():
    """The asserts that hold the two shapes apart, and the reuse measure."""
    # The ratio's allowance is the floor, so the same surplus decides differently.
    # 60 surplus words: convicted on a floor of 12, acquitted on a floor of 64.
    assert fires_ratio(12 + 60, 12, 2.0)
    assert not fires_ratio(64 + 60, 64, 2.0)
    # The surplus shape decides the same surplus the same way on both.
    assert fires_surplus(12 + 60, 12, 40) and fires_surplus(64 + 60, 64, 40)
    assert not fires_surplus(12 + 20, 12, 40) and not fires_surplus(64 + 20, 64, 40)

    # Reuse is a run of words, not a shared vocabulary.
    same_topic = "the predicate wraps the column so a plain btree cannot serve it"
    reworded = "a plain btree is not a candidate because the column sits inside a call"
    assert reuse(reworded, same_topic) == 0.0, "shared subject is not reuse"
    assert reuse(same_topic, "earlier: " + same_topic) == 1.0, "verbatim is reuse"
    # Code is not prose here either, for the reason metrics.score excludes it.
    assert reuse("```sql\nSELECT 1;\n```", "SELECT 1;") is None
    print("ceiling.demo: ok")


if __name__ == "__main__":
    main()
