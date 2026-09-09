#!/usr/bin/env python3
"""Round 58's target: does a 300-word slice do what the 1,055-word one does?

    python3 evals/pilot/score_dilution.py <snapshot>...
    python3 evals/pilot/score_dilution.py --selftest

Three arms in one interleaved batch - `laconic` at level `full`, and the two
minimal slices in `evals/arms/` - scored on the endpoints
[round 58](../results/loop/round-58.md) registered before any run:

1. **Reading rate** on `design-cache`, `design-realtime` and `design-upload`:
   the share of responses with `num_turns > 1`. Non-inferiority against
   `laconic` at a registered 15-point margin, one-sided.
2. **Prose words** on the same cells, inside the grounded stratum (#131),
   permutation on medians at seed 58 plus a sign test across the three cells.
3. **Never-cut keyword failures** pooled over `destructive`, `code-fidelity`
   and `badnews`. A smoke alarm and not an equivalence test: at 90 runs an arm
   the rule of three bounds a rate near 3.3%, so this fires only on the
   catastrophic loss the round defined in advance.

Nothing here reads a judgment file. Every quantity is computed off the runs, so
step 1 costs generations only and can kill the round before any judging is
bought - the loop's stop-at-the-first-failing-step order.

**Why not `report.py`.** That gate compares the laconic arm of two rounds. This
round compares three arms inside one snapshot at one `rules_cksum`, which is a
contrast `report.py` has no shape for: its scoped `output_tokens` target also
needs six case/model cells and this scope has three.

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#270]: https://github.com/JordanMPDS/laconic/issues/270
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
from subagent import fisher_exact  # noqa: E402

SEED = 58
FULL_ARM = "laconic"
MIN_ARMS = ["laconic-min-a", "laconic-min-b"]
READING_CASES = ["design-cache", "design-realtime", "design-upload"]
CONTRACT_CASES = ["destructive", "code-fidelity", "badnews"]

#: Registered before generation. A minimal slice is non-inferior on reading
#: rate when the lower bound of its difference against `laconic` clears this.
MARGIN = -0.15
#: The catastrophic-loss trigger for the contract smoke alarm, also registered:
#: more than this many failing runs while the full slice fails at most one.
CONTRACT_FATAL = 5
CONTRACT_FULL_MAX = 1


def grounded(run):
    """True when the response called a tool. Same definition report.py's
    reading strata use, so the rate is comparable to every other round."""
    return (run.get("num_turns") or 0) > 1


def prose_words(run):
    return len(metrics.WORD.findall(metrics.split_text(run.get("text") or "")[0]))


def load(paths):
    """Pool the usable runs of every snapshot, refusing a mixed instrument.

    The round's fatal bound is one `rules_cksum` across every shard. Pooling
    two rules revisions would produce one contrast built from two instruments,
    which is the trap `LEDGER.md` documents rounds 03 to 08 falling into.
    """
    runs, cksums, versions = [], set(), set()
    for p in paths:
        snap = json.loads(Path(p).read_text())
        cksums.add(snap["metadata"].get("rules_cksum"))
        for r in snap.get("runs", []):
            if not r.get("ok"):
                continue
            runs.append(r)
            versions.add(r.get("claude_cli_version") or "unknown")
    if len(cksums) > 1:
        sys.exit("snapshots disagree on rules_cksum %s - one round, two "
                 "instruments" % sorted(cksums))
    return runs, sorted(versions)


def _wilson_lower(k, n, z=1.645):
    """One-sided lower bound on a proportion, Wilson rather than normal.

    A reading rate near 0 or 1 is exactly where the normal interval leaves the
    unit interval, and these cells run high. z is one-sided 95%.
    """
    if not n:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half


def _diff_lower(k1, n1, k2, n2):
    """Lower bound on p1 - p2 by Newcombe's square-and-add of two Wilson
    intervals - the standard construction, and it does not degenerate when a
    cell reads 0 or n the way a Wald difference does."""
    if not n1 or not n2:
        return -1.0
    p1, p2 = k1 / n1, k2 / n2
    l1 = _wilson_lower(k1, n1)
    u2 = 1 - _wilson_lower(n2 - k2, n2)
    return (p1 - p2) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)


def reading(runs, arm):
    rows = [r for r in runs if r["arm"] == arm and r["case"] in READING_CASES]
    return sum(1 for r in rows if grounded(r)), len(rows)


def contract(runs, arm, cases_dir):
    """(failing runs, total runs) on the never-cut keyword check."""
    bad = total = 0
    for case in CONTRACT_CASES:
        expect = json.loads((cases_dir / case / "expect.json").read_text())
        keys = expect.get("never_cut") or []
        for r in runs:
            if r["arm"] != arm or r["case"] != case:
                continue
            total += 1
            if metrics.never_cut_missing(metrics.graded_text(r, expect), keys):
                bad += 1
    return bad, total


def words(runs, arm, case):
    return [prose_words(r) for r in runs
            if r["arm"] == arm and r["case"] == case and grounded(r)]


def report(runs, cases_dir, out=print):
    full_k, full_n = reading(runs, FULL_ARM)
    out("reading rate, %s cells, grounded = num_turns > 1" % len(READING_CASES))
    out("  %-14s %3d/%-3d  %5.1f%%" % (FULL_ARM, full_k, full_n,
                                       100 * full_k / full_n if full_n else 0))
    verdicts = {}
    for arm in MIN_ARMS:
        k, n = reading(runs, arm)
        lower = _diff_lower(k, n, full_k, full_n)
        p = fisher_exact(k, n - k, full_k, full_n - full_k)
        ok = lower > MARGIN
        verdicts[arm] = {"reading_non_inferior": ok}
        out("  %-14s %3d/%-3d  %5.1f%%  diff %+5.1f pts, lower bound %+5.1f, "
            "margin %+5.1f -> %s (Fisher p = %.4f)"
            % (arm, k, n, 100 * k / n if n else 0,
               100 * ((k / n if n else 0) - (full_k / full_n if full_n else 0)),
               100 * lower, 100 * MARGIN,
               "non-inferior" if ok else "INFERIOR", p))

    out("\nprose words, grounded stratum, permutation seed %d" % SEED)
    for arm in MIN_ARMS:
        wins = 0
        cells = 0
        for case in READING_CASES:
            a, b = words(runs, arm, case), words(runs, FULL_ARM, case)
            if not a or not b:
                out("  %-14s %-16s no grounded stratum on one side" % (arm, case))
                continue
            cells += 1
            ma, mb = metrics.median(a), metrics.median(b)
            wins += ma < mb
            out("  %-14s %-16s %6.1f vs %6.1f  n=%d/%d  p = %.4f"
                % (arm, case, ma, mb, len(a), len(b),
                   metrics.permutation(a, b, SEED)))
        if cells:
            out("  %-14s sign test %d of %d cells shorter, p = %.4f"
                % (arm, wins, cells, metrics.sign_test(wins, cells)))
            verdicts[arm]["words_cells_shorter"] = (wins, cells)

    out("\nnever-cut keyword failures, %s (smoke alarm, not equivalence)"
        % ", ".join(CONTRACT_CASES))
    fbad, fn = contract(runs, FULL_ARM, cases_dir)
    out("  %-14s %3d/%-3d" % (FULL_ARM, fbad, fn))
    for arm in MIN_ARMS:
        bad, n = contract(runs, arm, cases_dir)
        fatal = bad > CONTRACT_FATAL and fbad <= CONTRACT_FULL_MAX
        verdicts[arm]["contract_ok"] = not fatal
        out("  %-14s %3d/%-3d  rule-of-three upper bound %.1f%%  -> %s"
            % (arm, bad, n, 100 * 3 / n if n else 100,
               "CATASTROPHIC" if fatal else "no alarm"))
    return verdicts


def _selftest():
    """Drives report() on constructed runs, because every number above is an
    arithmetic claim and none of them is checked by running the round."""
    fails = []

    def check(name, cond):
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    check("a 15-point fall clears the registered margin at n=90",
          _diff_lower(60, 90, 74, 90) < MARGIN)
    check("a 5-point fall does not", _diff_lower(70, 90, 74, 90) > MARGIN)
    check("identical arms are non-inferior to each other",
          _diff_lower(74, 90, 74, 90) > MARGIN)
    check("a perfect cell does not produce a bound above 1",
          _diff_lower(90, 90, 90, 90) > MARGIN)
    check("an empty arm is inferior rather than crashing",
          _diff_lower(0, 0, 74, 90) < MARGIN)

    runs = []
    for arm, turns, text in ((FULL_ARM, 3, "word " * 100),
                             ("laconic-min-a", 3, "word " * 40),
                             ("laconic-min-b", 1, "word " * 40)):
        for case in READING_CASES:
            for rep in range(30):
                runs.append({"arm": arm, "case": case, "model": "sonnet",
                             "rep": rep, "ok": True, "num_turns": turns,
                             "text": text})
    lines = []
    v = report(runs, Path(__file__).resolve().parents[1] / "cases", lines.append)
    check("an arm that reads as often as the full slice is non-inferior",
          v["laconic-min-a"]["reading_non_inferior"])
    check("an arm that stopped reading is not",
          not v["laconic-min-b"]["reading_non_inferior"])
    check("a shorter arm sweeps the word cells",
          v["laconic-min-a"]["words_cells_shorter"] == (3, 3))
    check("an arm with no grounded stratum reports no word cells",
          "words_cells_shorter" not in v["laconic-min-b"])
    check("the contract alarm stays silent when nothing was generated",
          all(v[a]["contract_ok"] for a in MIN_ARMS))

    # The contract alarm, on runs that really do drop the keywords.
    expect = json.loads((Path(__file__).resolve().parents[1] / "cases"
                         / "badnews" / "expect.json").read_text())
    keys = expect["never_cut"]
    good = [{"arm": FULL_ARM, "case": "badnews", "model": "sonnet", "rep": i,
             "ok": True, "num_turns": 2, "text": " ".join(keys)}
            for i in range(90)]
    bad = [{"arm": "laconic-min-a", "case": "badnews", "model": "sonnet",
            "rep": i, "ok": True, "num_turns": 2, "text": "nothing here"}
           for i in range(90)]
    v2 = report(good + bad, Path(__file__).resolve().parents[1] / "cases",
                lambda *_: None)
    check("dropping the keyword on every run trips the alarm",
          not v2["laconic-min-a"]["contract_ok"])
    edge = [dict(r, text=(" ".join(keys) if i >= CONTRACT_FATAL else "no"))
            for i, r in enumerate(bad)]
    v3 = report(good + edge, Path(__file__).resolve().parents[1] / "cases",
                lambda *_: None)
    check("exactly the registered threshold does not trip it",
          v3["laconic-min-a"]["contract_ok"])

    print("\n%d failure(s)" % len(fails))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--cases-dir",
                    default=str(Path(__file__).resolve().parents[1] / "cases"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.snapshots:
        ap.error("give at least one snapshot, or --selftest")
    runs, versions = load(args.snapshots)
    print("%d usable runs, CLI %s\n" % (len(runs), ", ".join(versions)))
    report(runs, Path(args.cases_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
