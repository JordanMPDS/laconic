#!/usr/bin/env python3
"""Round 63: does hoisting the reading instruction out of the pre-action
check's conditional buy back the reading it costs? ([#264])

Round 56 bought 0.95 power on `quality_fails` for `design-*`/sonnet and found
nothing: 68/318 against 66/313, 95% CI [-6.7, +6.1]. Its registered secondary
fired instead - the share of runs that opened no file rose 35.0% to 42.8%,
+7.8 points, p = 0.0258 - and splitting the same verdicts by whether the run
read showed why both are true at once. Inside each reading stratum the check
changed nothing; what it changed was how much mass landed in each, and the
strata differ by 28.0 points, so the shift implies a quality cost near +2.2
points that no round this loop can afford to resolve.

So this round scores the mechanism directly, on three arms generated in one
interleaved pass:

    laconic-precheck-off    the two-item list the file carried before round 55
    laconic                 the check as it ships
    laconic-precheck-read   the check with the reading instruction hoisted out
                            of the broken-thing conditional

**The primary is the reading rate, and calling it a surrogate for quality
would be a claim this round cannot make.** `codex` put the distinction on
tools/consult.sh and it is adopted here: the estimand is the arm's own rate of
answering a design question without opening the fixture, which on this case
family is the documented mechanism of failure ([#88],
`design-discrimination.md` - no response that failed to resolve the fixture has
ever passed). It is a necessary-process endpoint, not a proven causal
conversion: the 28-point stratum gap is measured on a post-treatment split and
is not identified by the randomisation. A result here supports "the rewording
reduces the known mechanism of design-case failure", never "the rewording
improves quality".

**Two gates, in a fixed sequence, and the order is what keeps a null
readable.** Both delegate targets asked for this independently.

1. *Assay.* `laconic` against `laconic-precheck-off`. Does the check cost
   reading in this round's own window at all? Round 31 measured a three-day-old
   control at 31 where the simultaneous one read 46 on the same quantity, so a
   cross-round reference is not evidence here and the positive control is
   generated beside the arms it certifies. If this does not fire the round is
   **assay-inconclusive**: it says nothing about the rewording and nothing
   ships.
2. *Recovery.* `laconic-precheck-read` against `laconic`, tested only if the
   assay fired. `codex` supplied the rule that a failed assay must not be read
   as evidence the check is harmless.

Testing them in sequence rather than side by side is what makes one alpha
cover both.

**The test is Mantel-Haenszel stratified by case, registered before
generation.** The cells run from 27% to 80% unread in round 56's own table and
two more sit at a structural floor of zero, so a pooled 2x2 throws away the
blocking the design already has. Simulated at round 56's per-cell rates,
stratifying lifts power from 0.72 to 0.78 at 40 reps and from 0.83 to 0.88 at
53. A within-case permutation of the arm labels is printed beside it as the
exact check on the normal approximation, which is the null the design supports
- the case is fixed before the round, the arm is assigned within it.

**Two cells of round 56's eight are excluded in advance and the criterion is
mechanical**: `design-alerting` and `design-audit-log` read 0/40 unread on both
sides, a structural floor that contributes exactly zero to a stratified
contrast while costing a quarter of the generations. Reallocating those reps to
the six cells where the endpoint has variance buys 0.09 of power at constant
cost. Named here, before the round, and the round reports what it gives up: if
those cells are off the floor in this window they were informative and were not
bought.

**The guardrails are on cost, because the edit's risk is that it buys reading
by writing more or by reading where there is nothing to read.** Both targets
named the second one and neither was in the design that went to them.

- Prose length, `-read` against `laconic`, blocked on the case. Reported
  **all-runs and additionally blocked on the reading stratum**, in that order.
  `codex`: conditioning on "opened a file" conditions on the mechanism the arm
  changes, so the stratified figure is a diagnostic and the all-runs figure is
  the guardrail. Same estimator round 59 and 60 used, imported rather than
  re-implemented.
- Turns per run, all runs, per arm.
- **The sentinel**: the four cases in `evals/cases/` that ship no fixture
  directory - `code-fidelity`, `decision`, `floor`, `ordered-steps`. Across
  1,509 archived laconic/sonnet runs of those cases the tool count is zero and
  `num_turns` is 1 in 1,506 of them, so any reading there is gratuitous by
  construction and the floor needs no model. This is where an unconditional
  "read what grounds the answer" would show up, and `design-*` cannot see it.

*Origin: `codex` supplied the necessary-process framing, the assay-inconclusive
verdict, the all-runs length guardrail and the observation that the round is
scoped to design cases while the rule ships globally. `kimi` supplied the
outcome table the two gates produce, the fixed-sequence ordering, and the
demand that the stage-2 trigger be written down rather than left to reading.
Both, independently, asked for the over-reading sentinel. `deepseek` was asked
and did not answer.*

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#264]: https://github.com/JordanMPDS/laconic/issues/264
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_dilution as sd  # noqa: E402

#: The six `design-*` cells whose reading rate had variance in round 56.
#: `design-alerting` and `design-audit-log` read 0/40 on both sides and are
#: excluded in advance - see the module docstring.
DESIGN_CASES = ["design-cache", "design-rate-limit", "design-realtime",
                "design-retry", "design-search", "design-upload"]
#: The two round 56 cells this round does not buy, named so the round can say
#: what it gave up rather than leaving a reader to diff the case list.
FLOOR_CASES = ["design-alerting", "design-audit-log"]
#: Every case in evals/cases/ with no fixture/ directory. Nothing to read, so
#: any tool call is gratuitous.
SENTINEL_CASES = ["code-fidelity", "decision", "floor", "ordered-steps"]

OFF_ARM = "laconic-precheck-off"
SHIP_ARM = "laconic"
READ_ARM = "laconic-precheck-read"

#: One-sided 95%. Both gates are directional: the check is claimed to raise
#: unread and the rewording to lower it, and a rise in unread under the
#: rewording is a failure rather than a finding.
Z_ONE_SIDED = 1.6449
#: Exact permutations of the arm label within each case. Enough to resolve p to
#: ~0.0001, far finer than the 0.05 either gate reads.
PERMUTATIONS = 20000
SEED = 63
#: Non-inferiority margin on prose length, as a ratio. `-read` may not run more
#: than 10% longer than the shipped arm. Registered rather than derived: round
#: 59 measured 1.119x for deleting 209 words and calls 1.10x its detection
#: floor, so a margin below that would certify nothing this design can resolve.
LENGTH_MARGIN = 1.10


def unread(run):
    """The complement of score_dilution.grounded, so the two cannot drift."""
    return not sd.grounded(run)


def rates(runs, arm, cases):
    """(unread, total) for one arm over the named cases."""
    rows = [r for r in runs if r["arm"] == arm and r["case"] in cases]
    return sum(1 for r in rows if unread(r)), len(rows)


def _tables(runs, arm, ref, cases):
    """[(a, b, c, d)] per case: unread/read for `arm` then for `ref`."""
    out = []
    for case in cases:
        a, n1 = rates(runs, arm, [case])
        c, n2 = rates(runs, ref, [case])
        if n1 and n2:
            out.append((a, n1 - a, c, n2 - c))
    return out


def mantel_haenszel(tables):
    """(z, p one-sided) for `arm` carrying more unread than `ref`.

    Positive z means the first arm of each table reads less. The variance is
    the hypergeometric one per stratum, which is what makes a cell pinned at
    zero contribute nothing instead of contributing noise.
    """
    num = var = 0.0
    for (a, b, c, d) in tables:
        n = a + b + c + d
        if n < 2:
            continue
        num += a - (a + b) * (a + c) / n
        var += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if var <= 0:
        return 0.0, 1.0
    z = num / math.sqrt(var)
    return z, 0.5 * math.erfc(z / math.sqrt(2))


def permutation(runs, arm, ref, cases, seed=SEED, draws=PERMUTATIONS):
    """One-sided p for the same contrast, permuting the arm label inside each
    case. Exact under the design's null and free of any normal approximation.

    The statistic is the summed within-case difference in unread counts, which
    is monotone in the MH numerator at fixed margins, so the two answer the
    same question and a disagreement is a warning about the approximation
    rather than about the finding.
    """
    blocks = []
    for case in cases:
        a = [unread(r) for r in runs if r["arm"] == arm and r["case"] == case]
        b = [unread(r) for r in runs if r["arm"] == ref and r["case"] == case]
        if a and b:
            blocks.append((a, b))
    if not blocks:
        return None
    obs = sum(sum(a) / len(a) - sum(b) / len(b) for a, b in blocks) / len(blocks)
    rnd = random.Random(seed)
    hits = 0
    for _ in range(draws):
        total = 0.0
        for a, b in blocks:
            pool = a + b
            rnd.shuffle(pool)
            total += sum(pool[:len(a)]) / len(a) - sum(pool[len(a):]) / len(b)
        if total / len(blocks) >= obs - 1e-12:
            hits += 1
    return obs, (hits + 1) / (draws + 1)


def contrast_line(runs, arm, ref, cases, label, out):
    """One gate, printed whole: rates, difference with a two-sided interval,
    the MH test and the permutation beside it."""
    k1, n1 = rates(runs, arm, cases)
    k2, n2 = rates(runs, ref, cases)
    tabs = _tables(runs, arm, ref, cases)
    z, p = mantel_haenszel(tabs)
    perm = permutation(runs, arm, ref, cases)
    lo = sd._diff_lower(k1, n1, k2, n2)
    hi = sd._diff_upper(k1, n1, k2, n2)
    out("%s: %s %d/%d (%.1f%%) against %s %d/%d (%.1f%%)"
        % (label, arm, k1, n1, 100 * k1 / n1 if n1 else 0.0,
           ref, k2, n2, 100 * k2 / n2 if n2 else 0.0))
    out("  difference %+.1f pts, 90%% CI [%+.1f, %+.1f]"
        % (100 * ((k1 / n1 if n1 else 0) - (k2 / n2 if n2 else 0)),
           100 * lo, 100 * hi))
    out("  Mantel-Haenszel z = %+.3f, one-sided p = %.4f (%d strata)"
        % (z, p, len(tabs)))
    if perm:
        out("  within-case permutation: mean block difference %+.3f, "
            "one-sided p = %.4f" % (perm[0], perm[1]))
    return z, p


def per_cell(runs, arms, cases, out):
    out("")
    out("per-cell unread counts (disclosure, no second alpha rides on them):")
    width = max(len(c) for c in cases)
    out("  %-*s  %s" % (width, "cell", "  ".join("%-22s" % a for a in arms)))
    for case in cases:
        cells = []
        for arm in arms:
            k, n = rates(runs, arm, [case])
            cells.append("%-22s" % ("%d/%d (%.0f%%)"
                                    % (k, n, 100 * k / n if n else 0.0)))
        out("  %-*s  %s" % (width, case, "  ".join(cells)))


def per_shard(runs, arm, ref, cases, out):
    """The gate again inside each generating process. An effect carried by one
    shard is indistinguishable from a wall-clock or CLI-release artefact."""
    out("")
    out("%s against %s, per shard (diagnostic):" % (arm, ref))
    for gen, rows in sd.shards(runs):
        k1, n1 = rates(rows, arm, cases)
        k2, n2 = rates(rows, ref, cases)
        if not n1 or not n2:
            continue
        z, p = mantel_haenszel(_tables(rows, arm, ref, cases))
        out("  %-26s %d/%d (%.1f%%) against %d/%d (%.1f%%)  z = %+.2f  p = %.3f"
            % (gen[:26], k1, n1, 100 * k1 / n1, k2, n2, 100 * k2 / n2, z, p))


def length(runs, arm, ref, cases, out, note=""):
    """The prose-length guardrail, all-runs then blocked on the stratum."""
    for strata, name in ((False, "all runs"), (True, "blocked on the reading "
                                                     "stratum (#131)")):
        got = sd.blocked_log_words(runs, arm, cases, strata=strata, ref=ref)
        if not got:
            out("  %-38s no comparable block" % name)
            continue
        obs, ratio, p, blocks = got
        verdict = ("over margin" if ratio > LENGTH_MARGIN else "within margin")
        out("  %-38s %.3fx, p = %.4f, %d blocks - %s"
            % (name, ratio, p, blocks, verdict))
    if note:
        out("  %s" % note)


def turns(runs, arms, cases, out):
    out("")
    out("median turns per run, all runs (disclosure):")
    for arm in arms:
        vals = sorted((r.get("num_turns") or 0) for r in runs
                      if r["arm"] == arm and r["case"] in cases)
        if vals:
            out("  %-24s %d runs, median %d, mean %.2f"
                % (arm, len(vals), vals[len(vals) // 2],
                   sum(vals) / len(vals)))


def sentinel(runs, arms, out):
    """Reading where there is nothing to read. Any tool call is gratuitous."""
    present = [c for c in SENTINEL_CASES
               if any(r["case"] == c for r in runs)]
    if not present:
        out("")
        out("sentinel: no runs of %s in this snapshot - not bought"
            % ", ".join(SENTINEL_CASES))
        return
    out("")
    out("sentinel, the %d case(s) with no fixture to open: %s"
        % (len(present), ", ".join(present)))
    for arm in arms:
        rows = [r for r in runs if r["arm"] == arm and r["case"] in present]
        if not rows:
            continue
        read = sum(1 for r in rows if sd.grounded(r))
        tools = sum(len(r.get("tools") or []) for r in rows)
        out("  %-24s %d/%d runs opened something (%.1f%%), %d tool calls"
            % (arm, read, len(rows), 100 * read / len(rows), tools))
    out("")
    out("sentinel prose length, %s against %s:" % (READ_ARM, SHIP_ARM))
    length(runs, READ_ARM, SHIP_ARM, present, out,
           note="four cells, below the six a scoped sign test needs - "
                "disclosure, not a gate")


def report(runs, out=print):
    arms = [a for a in (OFF_ARM, SHIP_ARM, READ_ARM)
            if any(r["arm"] == a for r in runs)]
    cases = [c for c in DESIGN_CASES if any(r["case"] == c for r in runs)]
    out("arms present: %s" % ", ".join(arms))
    out("design cells scored: %s" % ", ".join(cases))
    floor_seen = [c for c in FLOOR_CASES if any(r["case"] == c for r in runs)]
    if floor_seen:
        out("NOTE: %s present in the snapshot and excluded by the "
            "registration" % ", ".join(floor_seen))
    out("")

    out("=== gate 1, the assay: does the check cost reading in this window ===")
    fired = False
    if OFF_ARM in arms and SHIP_ARM in arms:
        z, p = contrast_line(runs, SHIP_ARM, OFF_ARM, cases,
                             "unread rate", out)
        fired = p < 0.05 and z > 0
        out("  gate 1 %s" % ("FIRES - the assay is sensitive"
                             if fired else
                             "does not fire - ASSAY-INCONCLUSIVE, and the "
                             "round says nothing about the rewording"))
    else:
        out("  both arms not present - not scored")

    out("")
    out("=== gate 2, recovery: does the rewording buy the reading back ===")
    if not fired:
        out("  not tested: gate 1 did not fire, and the sequence is registered")
    elif READ_ARM in arms and SHIP_ARM in arms:
        z2, _ = contrast_line(runs, READ_ARM, SHIP_ARM, cases,
                               "unread rate", out)
        # The direction is reversed here: the rewording is claimed to lower
        # unread, so the gate reads the other tail of the same statistic.
        # contrast_line already printed p for the rise; this is p for the fall.
        p_recovery = 0.5 * math.erfc(-z2 / math.sqrt(2))
        out("  one-sided p in the direction of recovery = %.4f" % p_recovery)
        out("  gate 2 %s" % ("FIRES - the rewording recovers reading"
                             if p_recovery < 0.05 else "does not fire"))
    else:
        out("  both arms not present - not scored")

    per_cell(runs, arms, cases, out)
    if OFF_ARM in arms and SHIP_ARM in arms:
        per_shard(runs, SHIP_ARM, OFF_ARM, cases, out)
    if READ_ARM in arms and SHIP_ARM in arms:
        per_shard(runs, READ_ARM, SHIP_ARM, cases, out)

    out("")
    out("=== guardrail: prose length, %s against %s, margin %.2fx ==="
        % (READ_ARM, SHIP_ARM, LENGTH_MARGIN))
    if READ_ARM in arms and SHIP_ARM in arms:
        length(runs, READ_ARM, SHIP_ARM, cases, out)
    out("")
    out("what the check itself bought, %s against %s (context, not a gate):"
        % (SHIP_ARM, OFF_ARM))
    if OFF_ARM in arms and SHIP_ARM in arms:
        length(runs, SHIP_ARM, OFF_ARM, cases, out)

    turns(runs, arms, cases, out)
    sentinel(runs, arms, out)


def _selftest():
    fails = []

    def check(name, ok):
        print("%-4s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            fails.append(name)

    check("unread is exactly the complement of grounded",
          unread({"num_turns": 1}) and not unread({"num_turns": 4})
          and unread({}) and not sd.grounded({"num_turns": 1}))

    # A stratum with no variance contributes nothing rather than noise, which
    # is the whole reason the two floor cells are droppable at no cost.
    z_floor, _ = mantel_haenszel([(0, 40, 0, 40)])
    check("a cell pinned at zero contributes nothing to MH", z_floor == 0.0)

    # Identical arms must not fire; a large uniform shift must.
    flat = [(10, 30, 10, 30)] * 6
    z_flat, p_flat = mantel_haenszel(flat)
    check("MH is null on identical arms", abs(z_flat) < 1e-9 and p_flat > 0.4)
    shifted = [(20, 20, 10, 30)] * 6
    z_shift, p_shift = mantel_haenszel(shifted)
    check("MH fires on a uniform shift", z_shift > 3 and p_shift < 0.001)

    # Direction: the first arm of the table is the one claimed to read less.
    z_rev, _ = mantel_haenszel([(10, 30, 20, 20)] * 6)
    check("MH sign follows the arm order", z_rev < 0 and abs(z_rev + z_shift) < 1e-9)

    # Stratification has to beat pooling on the shape this round has, or the
    # registration's power claim is wrong about its own test.
    mixed = [(0, 40, 0, 40), (32, 8, 32, 8), (21, 19, 17, 23),
             (15, 25, 11, 29), (17, 23, 11, 29), (23, 17, 18, 22),
             (29, 11, 23, 17)]
    z_mixed, _ = mantel_haenszel(mixed)
    pooled_a = sum(t[0] for t in mixed)
    pooled_b = sum(t[2] for t in mixed)
    pooled_n = sum(t[0] + t[1] for t in mixed)
    z_pooled, _ = mantel_haenszel([(pooled_a, pooled_n - pooled_a,
                                    pooled_b, pooled_n - pooled_b)])
    check("stratifying beats pooling at round 56's per-cell rates",
          z_mixed > z_pooled)

    # The permutation agrees with MH in sign and roughly in size on data built
    # to have an effect, and returns a usable p on data built to have none.
    runs = []
    rnd = random.Random(1)
    for case in DESIGN_CASES:
        for rep in range(40):
            for arm, rate in ((SHIP_ARM, 0.55), (READ_ARM, 0.30)):
                runs.append({"arm": arm, "case": case, "model": "sonnet",
                             "rep": rep, "ok": True, "text": "word " * 50,
                             "num_turns": 1 if rnd.random() < rate else 4,
                             "generator": "g1"})
    obs, p_perm = permutation(runs, READ_ARM, SHIP_ARM, DESIGN_CASES, draws=2000)
    z_r, _ = mantel_haenszel(_tables(runs, READ_ARM, SHIP_ARM, DESIGN_CASES))
    check("permutation and MH agree in sign on a built effect",
          obs < 0 and z_r < 0)
    check("permutation gives a large p in the wrong direction", p_perm > 0.9)
    obs2, p_perm2 = permutation(runs, SHIP_ARM, READ_ARM, DESIGN_CASES,
                                draws=2000)
    check("permutation fires in the right direction", obs2 > 0 and p_perm2 < 0.01)

    # rates() must not silently score a case the round did not name.
    k, n = rates(runs, SHIP_ARM, DESIGN_CASES)
    check("rates counts every named cell once", n == 40 * len(DESIGN_CASES))
    k2, n2 = rates(runs, SHIP_ARM, ["design-cache"])
    check("rates scopes to the cells it is given", n2 == 40)

    # The whole report must run on a snapshot missing an arm and on one
    # missing the sentinel, because that is what stage 1 hands it.
    lines = []
    report(runs, out=lines.append)
    text = "\n".join(lines)
    check("report survives a snapshot with no positive-control arm",
          "both arms not present" in text)
    check("a missing assay arm leaves gate 2 untested",
          "not tested: gate 1 did not fire" in text)
    check("report names the sentinel it did not get",
          "not bought" in text)

    full = runs + [{"arm": a, "case": c, "model": "sonnet", "rep": i,
                    "ok": True, "text": "word " * 20, "num_turns": 1,
                    "generator": "g1"}
                   for a in (OFF_ARM, SHIP_ARM, READ_ARM)
                   for c in SENTINEL_CASES for i in range(10)]
    for case in DESIGN_CASES:
        for rep in range(40):
            full.append({"arm": OFF_ARM, "case": case, "model": "sonnet",
                         "rep": rep, "ok": True, "text": "word " * 50,
                         "num_turns": 1 if rnd.random() < 0.30 else 4,
                         "generator": "g1"})
    lines = []
    report(full, out=lines.append)
    text = "\n".join(lines)
    check("a fired assay lets gate 2 be tested",
          "gate 1 FIRES" in text and "not tested" not in text)
    check("the sentinel reports a reading rate per arm",
          "runs opened something" in text)
    check("the sentinel names its cases", "no fixture to open" in text)
    check("the length guardrail prints both scopes",
          "all runs" in text and "reading stratum" in text)
    check("a snapshot without the floor cells says nothing about them",
          "excluded by the registration" not in text)

    print("")
    print("%d failure(s)" % len(fails))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.snapshots:
        return ap.error("give at least one snapshot, or --selftest")
    runs, versions = sd.load(args.snapshots)
    print("%d usable runs, CLI release(s): %s" % (len(runs), ", ".join(versions)))
    print("")
    report(runs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
