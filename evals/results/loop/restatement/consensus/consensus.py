#!/usr/bin/env python3
"""Does adjudication raise the `restates` label ceiling, or is the construct unlabellable?

    python3 evals/results/loop/restatement/consensus/consensus.py

[#155]'s remaining half. `labeller_drift.py` measured one labeller twice, months
apart, at Cohen kappa 0.584 against `unread_asks`'s 0.902, and computed the
ceiling that noise puts under any detector: 78.3% precision, because a detector
is scored against one label set and a second set drawn the same way is the best
it could read. The issue's two remaining routes were "two labellers with
adjudication" and "a deterministic positive condition"; this measures the first.

WHY SIX PASSES AND NOT TWO. A pair can only be compared as a 2x2 table, and at
n=60 that table's kappa carries a bootstrap interval wide enough to contain both
the reading and the bar. Six independent passes over the same 60 responses give
each response a VOTE COUNT in 0..6, and the quantity the decision needs falls
straight out of it without a second experiment:

    Two disjoint triples, each adjudicated by majority, disagree on a response
    if and only if that response's six votes split 2, 3 or 4 true.

A response at 0, 1, 5 or 6 votes agrees across every way of splitting six
labellers into two triples, because a triple holding at most one of the minority
votes still reaches the same majority. So the adjudicated ceiling is set
entirely by the contested band, which is read off 360 votes rather than
estimated from one 2x2 table.

THE CORRELATION PROBLEM, AND THE ONE SIGNATURE THAT SEPARATES IT. All six
labellers are the same model under the same criterion, so their errors need not
be independent, and a majority vote over correlated errors buys less than the
arithmetic suggests. The unanimity rate cannot test this - item difficulty is
not uniform, so shared difficulty and shared misreading both inflate it. What
separates them is the shape of the contested band: a response at exactly 3 votes
whose six labellers split cleanly into two internally-unanimous triples is two
systematic readings meeting, while a response at 3 votes that splits every which
way is one genuinely ambiguous item. Both are counted below.

Reads only committed files and costs no calls.
"""
import itertools
import json
import random
import sys
from math import comb, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1 = HERE.parent
B2 = HERE.parent.parent / "restatement-b2"
PASSES = sorted(HERE.glob("pass-*.json"))

# Pre-registered bars, written before any pass was labelled. See consensus.md.
# Both are on point estimates with a Wilson bound rather than on a cluster
# bootstrap interval, and part A is why: at four source cases that interval
# spans [0.18, 1.00] on a reading of 0.584 and cannot sit on one side of any
# bar worth setting. A bar an instrument cannot fire is not a bar.
BAR_KAPPA = 0.80          # level: the adjudicated ceiling, in kappa
BAR_SPLITPROOF = 85.0     # mechanism: share of responses invariant to the split
BAR_SPLITPROOF_LO = 75.0  # ... and its Wilson lower bound
BAR_REFERENCE = 0.902     # what `unread_asks` reached, and why 0.80 is the bar
BOOTSTRAP = 20000


def load(path):
    return json.loads(Path(path).read_text())["labels"]


def key_cases(path):
    return {k["id"]: k["case"] for k in json.loads(Path(path).read_text())}


def kappa(ids, a, b):
    n = len(ids)
    if not n:
        return float("nan"), float("nan")
    po = sum(1 for i in ids if a[i] == b[i]) / n
    pa, pb = sum(a[i] for i in ids) / n, sum(b[i] for i in ids) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def wilson(k, n, z=1.96):
    if not n:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100.0 * (c - h), 100.0 * (c + h)


def item_bootstrap(ids, stat, reps=BOOTSTRAP, seed=156):
    """Resample items. Too narrow - the items cluster by case - but it is the
    interval a reader would compute by default, so both are printed."""
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        v = stat([ids[rng.randrange(len(ids))] for _ in ids])
        if v == v:
            out.append(v)
    out.sort()
    if len(out) < reps // 2:
        return float("nan"), float("nan")
    return out[int(0.025 * len(out))], out[int(0.975 * len(out))]


def cluster_bootstrap(ids, cases, stat, reps=BOOTSTRAP, seed=155):
    """Resample the four source cases with replacement, not the items.

    The 60 responses come from four prompts, so they are not independent: items
    from one prompt share topic, length and the shapes a restatement can take.
    Both consult targets said to resample at the case level, and both said that
    with four clusters this returns a WIDER interval than the naive one rather
    than a narrower one. It is reported because it is the honest width.
    """
    groups = {}
    for i in ids:
        groups.setdefault(cases[i], []).append(i)
    names = sorted(groups)
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        drawn = []
        for _ in names:
            drawn.extend(groups[names[rng.randrange(len(names))]])
        v = stat(drawn)
        if v == v:  # drop NaN draws, which occur when a resample is constant
            out.append(v)
    out.sort()
    if len(out) < reps // 2:
        return float("nan"), float("nan")
    return out[int(0.025 * len(out))], out[int(0.975 * len(out))]


def fisher_two_sided(a, b, c, d):
    n, r1, c1 = a + b + c + d, a + b, a + c
    if not r1 or not (c + d) or not c1 or not (b + d):
        return 1.0
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)

    def p(k):
        return comb(r1, k) * comb(n - r1, c1 - k) / comb(n, c1)
    obs = p(a) * (1 + 1e-9)
    return min(1.0, sum(p(k) for k in range(lo, hi + 1) if p(k) <= obs))


# --- part A: what the existing two-session instrument resolves ---------------

def part_a(cases):
    committed, relabel = load(B2 / "labels.json"), load(B2 / "labels-v1-relabel.json")
    ids = sorted(set(committed) & set(relabel))
    po, k = kappa(ids, committed, relabel)
    lo, hi = cluster_bootstrap(ids, cases, lambda s: kappa(s, committed, relabel)[1])
    ilo, ihi = item_bootstrap(ids, lambda s: kappa(s, committed, relabel)[1])
    print("=== A. what the committed two-session reading actually resolves ===")
    print("  batch 2, criterion v1 twice: agreement %d/%d = %.1f%%, kappa %.3f"
          % (round(po * len(ids)), len(ids), 100 * po, k))
    print("  bootstrap 95%%, by item:  [%.3f, %.3f]   (too narrow: items cluster)"
          % (ilo, ihi))
    print("  bootstrap 95%%, by case:  [%.3f, %.3f]   (four clusters, so wide)"
          % (lo, hi))
    tt = sum(1 for i in ids if committed[i] and relabel[i])
    bf = sum(1 for i in ids if relabel[i] and not committed[i])
    af = sum(1 for i in ids if committed[i] and not relabel[i])
    pl, ph = wilson(tt, tt + bf)
    rl, rh = wilson(tt, tt + af)
    print("  oracle ceiling against the committed labels:")
    print("    precision %.1f%% (n=%d, Wilson 95%% [%.0f%%, %.0f%%])"
          % (100.0 * tt / (tt + bf), tt + bf, pl, ph))
    print("    recall    %.1f%% (n=%d, Wilson 95%% [%.0f%%, %.0f%%])"
          % (100.0 * tt / (tt + af), tt + af, rl, rh))
    print("  A bar this interval cannot sit on one side of is not a bar.")
    return ids, committed, relabel, k


# --- part B: six passes, one sitting ----------------------------------------

def part_b(ids, cases, passes):
    names = [p.stem for p in PASSES]
    votes = {i: sum(1 for p in passes if p[i]) for i in ids}
    hist = [sum(1 for i in ids if votes[i] == v) for v in range(len(passes) + 1)]

    print()
    print("=== B. six independent passes, one sitting, criterion v1 unchanged ===")
    print("  passes: %s" % ", ".join(names))
    for n, p in zip(names, passes):
        print("    %-12s true %2d/%d (%.1f%%)"
              % (n, sum(p[i] for i in ids), len(ids),
                 100.0 * sum(p[i] for i in ids) / len(ids)))

    print("  vote profile (how many of the six called a response a restatement):")
    for v, c in enumerate(hist):
        band = {0: "unanimous false", len(passes): "unanimous true"}.get(
            v, "safe" if v in (1, len(passes) - 1) else "CONTESTED")
        print("    %d/%d votes  %2d responses  (%4.1f%%)  %s"
              % (v, len(passes), c, 100.0 * c / len(ids), band))
    core = hist[0] + hist[-1]
    safe = core + hist[1] + hist[-2]
    contested = len(ids) - safe
    slo, shi = wilson(safe, len(ids))
    print("  unanimous core %d/%d (%.1f%%); split-proof band %d/%d (%.1f%%,"
          % (core, len(ids), 100.0 * core / len(ids), safe, len(ids),
             100.0 * safe / len(ids)))
    print("  Wilson 95%% [%.1f%%, %.1f%%]); contested %d/%d (%.1f%%) - and the"
          % (slo, shi, contested, len(ids), 100.0 * contested / len(ids)))
    print("  ceiling is lost only there.")

    # pairwise: what one labeller reads against another, at one sitting
    pairwise = [kappa(ids, passes[a], passes[b])
                for a, b in itertools.combinations(range(len(passes)), 2)]
    pk = sorted(k for _, k in pairwise)
    ppo = sorted(po for po, _ in pairwise)
    print()
    print("  single pass against single pass, %d pairs:" % len(pairwise))
    print("    agreement  mean %.1f%%  range %.1f%% to %.1f%%"
          % (100 * sum(ppo) / len(ppo), 100 * ppo[0], 100 * ppo[-1]))
    print("    kappa      mean %.3f   range %.3f to %.3f"
          % (sum(pk) / len(pk), pk[0], pk[-1]))

    # adjudicated: every way of splitting six labellers into two disjoint triples
    splits = [(t, tuple(x for x in range(len(passes)) if x not in t))
              for t in itertools.combinations(range(len(passes)), 3)
              if 0 in t]

    def majority(ids_, idx):
        return {i: sum(passes[j][i] for j in idx) >= 2 for i in ids_}

    adj = [kappa(ids, majority(ids, a), majority(ids, b)) for a, b in splits]
    ak = sorted(k for _, k in adj)
    apo = sorted(po for po, _ in adj)
    mean_adj = sum(ak) / len(ak)
    mean_pair = sum(pk) / len(pk)
    print()
    print("  majority-of-three against the disjoint other three, %d splits:" % len(splits))
    print("    agreement  mean %.1f%%  range %.1f%% to %.1f%%"
          % (100 * sum(apo) / len(apo), 100 * apo[0], 100 * apo[-1]))
    print("    kappa      mean %.3f   range %.3f to %.3f"
          % (mean_adj, ak[0], ak[-1]))

    def adj_minus_pair(sample):
        a = sum(kappa(sample, majority(sample, x), majority(sample, y))[1]
                for x, y in splits) / len(splits)
        p = sum(kappa(sample, passes[x], passes[y])[1]
                for x, y in itertools.combinations(range(len(passes)), 2)) / len(pairwise)
        return a - p
    dlo, dhi = cluster_bootstrap(ids, cases, adj_minus_pair, reps=2000, seed=1551)
    alo, ahi = cluster_bootstrap(
        ids, cases,
        lambda s: sum(kappa(s, majority(s, x), majority(s, y))[1]
                      for x, y in splits) / len(splits), reps=2000, seed=1552)
    print("    cluster bootstrap by case, 95%%: [%.3f, %.3f]" % (alo, ahi))
    print("  adjudication gain in kappa: %+.3f, cluster bootstrap 95%% [%+.3f, %+.3f]"
          % (mean_adj - mean_pair, dlo, dhi))

    # the correlation signature: a response the six split three-three, where the
    # three-three is itself a clean split into two internally unanimous triples.
    half = len(passes) // 2
    tied = [i for i in ids if votes[i] == half]
    clean = 0
    for i in tied:
        for a, b in splits:
            if all(passes[j][i] for j in a) and not any(passes[j][i] for j in b):
                clean += 1
                break
            if all(passes[j][i] for j in b) and not any(passes[j][i] for j in a):
                clean += 1
                break
    print()
    print("  correlation signature: %d responses split %d-%d, of which %d split"
          % (len(tied), half, half, clean))
    print("  cleanly into two internally unanimous triples. A clean split is two")
    print("  systematic readings meeting; a ragged one is a single ambiguous item.")
    if tied:
        print("  clean share %.1f%% (chance under exchangeable votes: %.1f%%)"
              % (100.0 * clean / len(tied), 100.0 * len(splits) / comb(len(passes), half) * 2))

    return (votes, mean_adj, mean_pair, (alo, ahi), (dlo, dhi),
            safe, len(ids), wilson(safe, len(ids)))


def part_c(ids, cases, votes, passes, committed, relabel):
    """Does the committee reproduce the hand labels, or drift away from them?"""
    n = len(passes)
    cons = {i: votes[i] * 2 > n for i in ids}
    print()
    print("=== C. the committee against the two committed hand label sets ===")
    for name, other in (("committed labels", committed), ("v1 re-label", relabel)):
        po, k = kappa(ids, other, cons)
        lo, hi = cluster_bootstrap(ids, cases, lambda s: kappa(s, other, cons)[1],
                                   reps=2000, seed=1553)
        print("  consensus-of-%d against %-18s agreement %.1f%%, kappa %.3f [%.3f, %.3f]"
              % (n, name, 100 * po, k, lo, hi))
    print("  consensus true %d/%d (%.1f%%); committed %d/%d; re-label %d/%d"
          % (sum(cons.values()), len(ids), 100.0 * sum(cons.values()) / len(ids),
             sum(committed[i] for i in ids), len(ids),
             sum(relabel[i] for i in ids), len(ids)))
    return cons


def by_case(ids, cases, votes, n):
    print()
    print("=== D. where the contest sits ===")
    groups = {}
    for i in ids:
        groups.setdefault(cases[i], []).append(i)
    for c in sorted(groups):
        g = groups[c]
        cont = sum(1 for i in g if 2 <= votes[i] <= n - 2)
        print("    %-20s contested %2d of %2d (%.1f%%)"
              % (c, cont, len(g), 100.0 * cont / len(g)))
    rows = [(c, sum(1 for i in g if 2 <= votes[i] <= n - 2), len(g))
            for c, g in groups.items()]
    worst = max(rows, key=lambda r: r[1] / r[2])
    om = sum(r[1] for r in rows) - worst[1]
    on = sum(r[2] for r in rows) - worst[2]
    print("    %s against the rest: %d/%d vs %d/%d, Fisher p = %.4f"
          % (worst[0], worst[1], worst[2], om, on,
             fisher_two_sided(worst[1], worst[2] - worst[1], om, on - om)))


def main():
    cases = key_cases(B2 / "key.json")
    ids, committed, relabel, _ = part_a(cases)
    if not PASSES:
        print()
        print("No pass-*.json yet. Part A is the registration's own resolution check;")
        print("parts B to D run once the six labelling passes are committed.")
        return 0
    passes = [load(p) for p in PASSES]
    ids = sorted(set(ids) & set.intersection(*[set(p) for p in passes]))
    votes, adj, pair, aci, dci, safe, nitems, sci = part_b(ids, cases, passes)
    part_c(ids, cases, votes, passes, committed, relabel)
    by_case(ids, cases, votes, len(passes))

    print()
    print("=== THE PRE-REGISTERED VERDICT ===")
    share = 100.0 * safe / nitems
    level = adj >= BAR_KAPPA
    mech = share >= BAR_SPLITPROOF and sci[0] >= BAR_SPLITPROOF_LO
    print("  bar 1, level:     adjudicated kappa %.3f >= %.2f ........... %s"
          % (adj, BAR_KAPPA, "PASS" if level else "FAIL"))
    print("  bar 2, mechanism: split-proof %.1f%% >= %.0f%% and its Wilson"
          % (share, BAR_SPLITPROOF))
    print("                    lower bound %.1f%% >= %.0f%% ............... %s"
          % (sci[0], BAR_SPLITPROOF_LO, "PASS" if mech else "FAIL"))
    print("  disclosed, not gated: adjudication gain %+.3f kappa, cluster 95%%"
          % (adj - pair))
    print("  [%+.3f, %+.3f]; adjudicated kappa cluster 95%% [%.3f, %.3f]."
          % (dci[0], dci[1], aci[0], aci[1]))
    print("  (`unread_asks` ruled its labeller out at kappa %.3f.)" % BAR_REFERENCE)
    if level and mech:
        print("  BOTH BARS CLEAR: adjudication raises the ceiling, and a consensus")
        print("  label set is the route for #150, #298 and #305.")
    else:
        print("  A BAR FAILS: adjudication does not deliver a label set a detector")
        print("  could be scored against, and the judged-verdict route needs a")
        print("  different construct rather than a better protocol.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
