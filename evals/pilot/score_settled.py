#!/usr/bin/env python3
"""Round 71's target: does a worked *true-premise* closed question stop haiku
re-deriving grounds the user already has?

    python3 evals/pilot/score_settled.py --control <snap>... --edit <snap>...
    python3 evals/pilot/score_settled.py --selftest

`true-premise-136.md` built the instrument and measured the harm: on the three
`settled-*` cells a bare confirmation is the complete answer, and haiku under
master rules answers at a median of 98 prose words with **34 of 45 above 80**.
Sonnet reads 0 of 45, so this round is haiku-only on the target and says so.

**Three cells cannot reach alpha on a sign test**, which is what every other
round in this cluster combines with. Two-sided exact at 3 of 3 is p = 0.25, so
a sweep requirement is a falsifier here and not a test. The primary is instead
a **stratified one-sided permutation**: the statistic is the mean over cells of
(edit median - control median), and the side label is permuted *within each
cell*, so cell composition is held fixed and no single fixture can carry the
round by being long. The three per-cell permutations are the resolution and are
printed beside it. That split is DeepSeek's correction from `tools/consult.sh`
and is registered in `../results/loop/round-71.md`.

**The falsifier is correctness on the twin, not length on the twin.** The
`unsettled-*` cases state a false premise, so a complete answer is a denial
plus the record's version, and 25 correct words there is the edit working
rather than failing - Kimi's correction, and the reason no length bar is
registered on the twins. What is registered is that neither the **deny rate**
nor the **correction rate** may fall, pooled over the six twin cells, at
one-sided Fisher p < 0.05. Both are run on haiku *and* sonnet, because sonnet
is where the rules bite hardest and an under-answering regression would show
there first.

`CORRECTION` reads 180 of 180 twin responses under master rules, so it is a
*fall* detector at a ceiling ([#94]): it can register a regression and cannot
register an improvement, and it has no measured false-positive rate because the
shape it screens for - a denial carrying no correction - does not occur under
master rules. It requires the record's *mechanism*, not merely a contradiction:
the 14-day prune, the manual promotion, the per-line rounding.

[#131] stratification and [#209] mixture apply unchanged: a cell whose reading
rate crossed between the two sides does not vote, and a cell holding mutating
runs does not vote. Both are reported whether or not they are zero.
"""
import argparse
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_premise import load, verdict, wilson  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

SEED = 71
RESAMPLES = 200000
STEMS = ("retention", "failover", "rounding")
TARGET = tuple(("settled-%s" % s, "haiku") for s in STEMS)
TWINS = tuple(("unsettled-%s" % s, m)
              for s in STEMS for m in ("haiku", "sonnet"))
CAPS = (40, 80)

#: The record's own mechanism, per case. A denial that contradicts the user and
#: supplies none of this is the under-answering regression the falsifier exists
#: to catch, so naming the true table or the true number is not enough on its
#: own - the answer has to carry why.
CORRECTION = {
    "retention": re.compile(
        r"(14[\s-]*day|fourteen[\s-]*day|prune_events_raw"
        r"|deleted after 14|gone after 14)", re.I),
    "failover": re.compile(
        r"(manual|promote\.sh|on-?call|report[\s-]?only)", re.I),
    "rounding": re.compile(
        r"(line_tax|at the line|per[\s-]line|per invoice line"
        r"|one cent|1 cent|a cent)", re.I),
}


def corrects(run):
    """True when a twin response carries the record's mechanism."""
    stem = (run.get("case") or "").split("-", 1)[-1]
    pat = CORRECTION.get(stem)
    return bool(pat and pat.search(run.get("text") or ""))


def cell(runs, case, model):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == model
          and r.get("arm") == "laconic"]
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "deny": sum(1 for r in rs if verdict(r.get("text")) == "deny"),
        "confirm": sum(1 for r in rs if verdict(r.get("text")) == "confirm"),
        "corrects": sum(1 for r in rs if corrects(r)),
        "words": [words(r) for r in rs],
    }


def votes(a, b):
    """(votes, crossed, mixed) for one cell's two sides."""
    ra = a["grounded"] / a["n"] if a["n"] else 0.0
    rb = b["grounded"] / b["n"] if b["n"] else 0.0
    crossed = ra != rb
    mixed = bool(a["edits"] or b["edits"])
    return (bool(a["n"] and b["n"] and not crossed and not mixed),
            crossed, mixed)


def stratified(pairs, seed=SEED, resamples=RESAMPLES):
    """One-sided stratified permutation of the side label within each cell.

    `pairs` is [(control_words, edit_words), ...], one entry per voting cell.
    The statistic is the mean over cells of (edit median - control median), so
    every cell contributes equally however many runs it holds, and a cell that
    is simply longer than the others cannot carry the round. Returns
    (statistic, p) where p is P(statistic <= observed) under the null, or
    (None, None) when no cell votes.
    """
    pairs = [(list(c), list(e)) for c, e in pairs if c and e]
    if not pairs:
        return (None, None)

    def stat(ps):
        return sum(metrics.median(e) - metrics.median(c)
                   for c, e in ps) / len(ps)

    obs = stat(pairs)
    rng = random.Random(seed)
    hits = 0
    for _ in range(resamples):
        shuffled = []
        for c, e in pairs:
            pool = c + e
            rng.shuffle(pool)
            shuffled.append((pool[:len(c)], pool[len(c):]))
        if stat(shuffled) <= obs + 1e-9:
            hits += 1
    return (obs, (hits + 1) / (resamples + 1))


def fisher_le(a, b, c, d):
    """One-sided Fisher exact: P(edit successes <= a) given the margins.

    a/b are the edit side's successes and failures, c/d the control's. This is
    the fall test both twin rates are registered against.
    """
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    total = comb(n1 + n2, k)
    if not total:
        return 1.0
    lo = max(0, k - n2)
    return sum(comb(n1, x) * comb(n2, k - x)
               for x in range(lo, a + 1)) / total


def fmt_p(p):
    if p is None:
        return "-"
    return "< 0.00001" if p < 1e-5 else "%.5f" % p


def target(control, edit):
    """The primary and its per-cell resolution, over the three settled cells."""
    rows, pairs = [], []
    for case, model in TARGET:
        a, b = cell(control, case, model), cell(edit, case, model)
        ok, crossed, mixed = votes(a, b)
        rows.append({
            "cell": "%s/%s" % (case, model), "a": a, "b": b,
            "votes": ok, "crossed": crossed, "mixed": mixed,
            "median_a": metrics.median(a["words"]),
            "median_b": metrics.median(b["words"]),
            "p2": metrics.permutation(a["words"], b["words"], SEED, RESAMPLES,
                                      stat=statistics.median) if ok else None,
        })
        if ok:
            pairs.append((a["words"], b["words"]))
    stat, p = stratified(pairs)
    return rows, stat, p


def twins(control, edit):
    """The falsifier: deny and correction rates over the six twin cells."""
    rows = []
    tot = {"deny_a": 0, "deny_b": 0, "corr_a": 0, "corr_b": 0,
           "n_a": 0, "n_b": 0}
    for case, model in TWINS:
        a, b = cell(control, case, model), cell(edit, case, model)
        rows.append({"cell": "%s/%s" % (case, model), "a": a, "b": b,
                     "median_a": metrics.median(a["words"]),
                     "median_b": metrics.median(b["words"])})
        tot["deny_a"] += a["deny"]; tot["deny_b"] += b["deny"]
        tot["corr_a"] += a["corrects"]; tot["corr_b"] += b["corrects"]
        tot["n_a"] += a["n"]; tot["n_b"] += b["n"]
    tot["deny_p"] = fisher_le(tot["deny_b"], tot["n_b"] - tot["deny_b"],
                              tot["deny_a"], tot["n_a"] - tot["deny_a"])
    tot["corr_p"] = fisher_le(tot["corr_b"], tot["n_b"] - tot["corr_b"],
                              tot["corr_a"], tot["n_a"] - tot["corr_a"])
    return rows, tot


def decide(rows, p, tot):
    """The registered verdict, as (passed, reasons) over already-scored rows.

    Four conditions, all registered in `../results/loop/round-71.md` before
    any generation. The consistency requirement is separate from the
    permutation deliberately: a stratified permutation *can* be carried by one
    cell that separates hugely while the other two sit still, and on three
    cells that is not a result this round will accept.
    """
    voting = [r for r in rows if r["votes"]]
    fell = [r for r in voting if r["median_b"] < r["median_a"]]
    rose_sig = [r["cell"] for r in voting
                if r["median_b"] > r["median_a"] and (r["p2"] or 1) < 0.05]
    reasons = []
    if p is None or p >= 0.05:
        reasons.append("stratified permutation p = %s" % fmt_p(p))
    if len(voting) != len(TARGET) or len(fell) != len(TARGET):
        reasons.append("%d of %d cells fell, %d voted"
                       % (len(fell), len(TARGET), len(voting)))
    if rose_sig:
        reasons.append("rose at p < 0.05: %s" % ", ".join(rose_sig))
    if tot["deny_p"] < 0.05:
        reasons.append("twin deny rate fell, p = %s" % fmt_p(tot["deny_p"]))
    if tot["corr_p"] < 0.05:
        reasons.append("twin correction rate fell, p = %s"
                       % fmt_p(tot["corr_p"]))
    return (not reasons), reasons


def headroom(runs, label):
    out = []
    pooled = []
    for case, model in TARGET:
        c = cell(runs, case, model)
        pooled += c["words"]
        out.append((("%s/%s" % (case, model)), c["n"],
                    {k: sum(1 for w in c["words"] if w > k) for k in CAPS},
                    metrics.median(c["words"])))
    out.append(("pooled %s" % label, len(pooled),
                {k: sum(1 for w in pooled if w > k) for k in CAPS},
                metrics.median(pooled)))
    return out


def report(control, edit):
    rows, stat, p = target(control, edit)
    print("# Round 71: the true-premise worked question\n")
    print("## Target: prose words, three settled cells, haiku\n")
    print("| cell | n ctl | n edit | control median | edit median "
          "| two-sided p | votes |")
    print("|---|--:|--:|--:|--:|--:|---|")
    for r in rows:
        why = "yes" if r["votes"] else (
            "no (reading crossed)" if r["crossed"] else "no (mixed)")
        print("| `%s` | %d | %d | %.1f | %.1f | %s | %s |"
              % (r["cell"], r["a"]["n"], r["b"]["n"], r["median_a"],
                 r["median_b"], fmt_p(r["p2"]), why))
    fell = sum(1 for r in rows if r["votes"] and r["median_b"] < r["median_a"])
    voting = sum(1 for r in rows if r["votes"])
    rose_sig = [r["cell"] for r in rows
                if r["votes"] and r["median_b"] > r["median_a"]
                and (r["p2"] or 1) < 0.05]
    print("\n**Stratified one-sided permutation: statistic %s words, "
          "p = %s** over %d voting cells."
          % ("%.2f" % stat if stat is not None else "-", fmt_p(p), voting))
    print("Cells falling: %d of %d. Rising at p < 0.05: %s."
          % (fell, voting, ", ".join(rose_sig) if rose_sig else "none"))

    print("\n## Headroom, disclosure\n")
    for label, runs in (("control", control), ("edit", edit)):
        print("### %s\n" % label)
        print("| cell | n | > 40 | > 80 | median |")
        print("|---|--:|--:|--:|--:|")
        for name, n, caps, med in headroom(runs, label):
            lo, hi = wilson(caps[80], n)
            print("| %s | %d | %d (%.1f%%) | %d (%.1f%%) [%.1f, %.1f] | %.1f |"
                  % (name, n, caps[40], 100.0 * caps[40] / n if n else 0.0,
                     caps[80], 100.0 * caps[80] / n if n else 0.0,
                     100 * lo, 100 * hi, med))
        print()

    trows, tot = twins(control, edit)
    print("## Falsifier: the unsettled twins, both models\n")
    print("| cell | n ctl | n edit | deny ctl | deny edit | corrects ctl "
          "| corrects edit | median ctl | median edit |")
    print("|---|--:|--:|--:|--:|--:|--:|--:|--:|")
    for r in trows:
        print("| `%s` | %d | %d | %d | %d | %d | %d | %.1f | %.1f |"
              % (r["cell"], r["a"]["n"], r["b"]["n"], r["a"]["deny"],
                 r["b"]["deny"], r["a"]["corrects"], r["b"]["corrects"],
                 r["median_a"], r["median_b"]))
    print("\n**Pooled deny %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s.**"
          % (tot["deny_a"], tot["n_a"], tot["deny_b"], tot["n_b"],
             fmt_p(tot["deny_p"])))
    print("**Pooled correction %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s.**"
          % (tot["corr_a"], tot["n_a"], tot["corr_b"], tot["n_b"],
             fmt_p(tot["corr_p"])))

    passed, reasons = decide(rows, p, tot)
    print("\n**Registered verdict: %s**%s"
          % ("PASS" if passed else "FAIL",
             "" if passed else " — " + "; ".join(reasons)))
    return 0 if passed else 1


def selftest():
    r = lambda case, text, n=2: {  # noqa: E731
        "case": case, "text": text, "num_turns": n, "tools": ["Read"],
        "ok": True, "model": "haiku", "arm": "laconic"}
    assert corrects(r("unsettled-retention",
                      "No. The raw rows are gone after 14 days."))
    assert corrects(r("unsettled-retention",
                      "Not quite - `prune_events_raw` deletes them."))
    assert not corrects(r("unsettled-retention",
                          "No, that is backwards."))
    assert corrects(r("unsettled-failover", "No - promotion is manual."))
    assert corrects(r("unsettled-failover",
                      "That is wrong; the on-call runs promote.sh."))
    assert not corrects(r("unsettled-failover", "No."))
    assert corrects(r("unsettled-rounding", "No, tax rounds at the line."))
    assert corrects(r("unsettled-rounding",
                      "Incorrect - `line_tax` rounds per line."))
    assert not corrects(r("unsettled-rounding", "That is the opposite."))
    # A settled case is never passed to `corrects`, but an unknown stem must
    # read False rather than raise, because a snapshot can hold a case this
    # round did not ask for.
    assert not corrects(r("walkthrough", "anything at all"))

    # The stratified permutation: a clean separation in every cell reaches
    # alpha, and identical sides do not.
    lo = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    hi = [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    stat, p = stratified([(hi, lo)] * 3, resamples=2000)
    assert stat is not None and stat < 0 and p < 0.05, (stat, p)
    stat, p = stratified([(hi, hi)] * 3, resamples=2000)
    assert p > 0.05, (stat, p)
    # Cells are weighted equally however many runs they hold, so a cell with
    # ten times the reps cannot outvote a small one on n alone.
    stat_small, _ = stratified([(hi, lo), (hi, hi)], resamples=2000)
    stat_big, _ = stratified([(hi * 10, lo * 10), (hi, hi)], resamples=2000)
    assert abs(stat_small - stat_big) < 1e-9, (stat_small, stat_big)
    # Nothing to compare is not a p-value.
    assert stratified([]) == (None, None)

    # `decide`: the permutation alone does not accept. One cell separating
    # hugely while the others sit still clears the permutation and is still
    # rejected by the consistency requirement, which is why both are
    # registered.
    clean = {"deny_p": 1.0, "corr_p": 1.0}
    row = lambda c, a, b, p2=0.5: {  # noqa: E731
        "cell": c, "votes": True, "median_a": a, "median_b": b, "p2": p2}
    swept = [row("a", 100, 60), row("b", 100, 70), row("c", 100, 80)]
    assert decide(swept, 0.01, clean)[0]
    assert not decide(swept, 0.20, clean)[0]
    one_cell = [row("a", 100, 20), row("b", 100, 100), row("c", 100, 100)]
    assert not decide(one_cell, 0.001, clean)[0]
    rising = [row("a", 100, 60), row("b", 100, 70), row("c", 100, 140, 0.01)]
    assert not decide(rising, 0.01, clean)[0]
    assert not decide(swept, 0.01, {"deny_p": 0.01, "corr_p": 1.0})[0]
    assert not decide(swept, 0.01, {"deny_p": 1.0, "corr_p": 0.01})[0]
    # A cell that did not vote is not a cell that fell.
    short = [row("a", 100, 60), row("b", 100, 70),
             dict(row("c", 100, 80), votes=False)]
    assert not decide(short, 0.01, clean)[0]

    # Fisher: the fall test fires on a real fall and not on a rise.
    assert fisher_le(60, 15, 75, 0) < 0.05
    assert fisher_le(75, 0, 75, 0) == 1.0
    assert fisher_le(75, 0, 60, 15) > 0.5

    # A mixed cell and a crossed cell both refuse to vote.
    a = {"n": 5, "edits": 0, "grounded": 5}
    assert votes(a, dict(a))[0]
    assert not votes(a, dict(a, grounded=4))[0]
    assert not votes(a, dict(a, edits=1))[0]
    print("selftest: ok")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--control", nargs="*", default=[])
    ap.add_argument("--edit", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.control or not args.edit:
        ap.error("--control and --edit each need at least one snapshot")
    return report(load(args.control), load(args.edit))


if __name__ == "__main__":
    sys.exit(main())
