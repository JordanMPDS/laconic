#!/usr/bin/env python3
"""Round 58's target: does a 300-word slice do what the 1,055-word one does?
Extended for round 59, which asks which part of the 750-word gap carries it.

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

## Round 59

Round 59 ablates one block from the shipped slice per arm rather than replacing
the whole file, so its effects are several times smaller than round 58's and
the per-cell median is too blunt an instrument for them. Three things changed
here, none of which moves a number round 58 published:

- **The comparison arms are read off the snapshot** instead of a constant, so
  a round adds an arm by generating it. `laconic` is always the control.
- **`--words-cases` widens the prose-words scope.** Round 58 registered three
  `design-*` cells and scored the contract cells as exploratory; round 59
  registers all six in advance. The default is round 58's scope, so its
  published sign test still reproduces.
- **A blocked log-words test is the round 59 primary**, and the per-cell median
  table stays as the robustness display. Reducing each cell to one median
  throws away the reps that a 165-word ablation needs: with six cells the exact
  two-sided sign test bottoms out at p = 0.03125, which cannot clear a
  Bonferroni correction for two contrasts, so a sign test cannot be the primary
  of a round that has more than one arm to compare.
- **The primary blocks on the case, and the reading stratum comes back as a
  secondary.** `grounded()` is `num_turns > 1`, which is what the run did under
  its own treatment, so blocking on it conditions on a post-treatment variable
  and is not identified by the assignment. Round 58 made the stratified block
  its primary; round 59 reports the total effect - length as it comes out,
  reading included - because that is the quantity shipping the slice would
  change. Both blocks are printed and #131's concern is answered by the
  reading-rate guardrail, which is the endpoint built for it.
- **The primary is also printed per shard**, as a diagnostic. It is readable
  only because every shard now runs every case; see `shards()`.

## Issue #278: the guardrail had two verdicts and needed three

The reading-rate test ran in rounds 58 and 59 and returned INFERIOR on three of
four arms, none of which fell significantly on its own. The cause was neither
the margin nor the reps: `ok = lower > MARGIN` collapsed "the design ruled this
arm out" and "the design could not resolve this arm" into one verdict, and at
these reps almost every arm lands in the second. A one-sided non-inferiority
test has three outcomes and this file now reports all three - `non-inferior`
when the lower bound clears the margin, `HARMED` when the upper bound falls
below it, `inconclusive` in between.

`MARGIN` does not move. It was registered before generation, and widening it
afterwards so that results pass is the thing pre-registration exists to
prevent. Reprinting rounds 58 and 59 under the corrected verdict turns all
three INFERIOR results into `inconclusive` and changes no other number.

`HARMED` is not toothless. At n = 120 against a control at 37.5% it fires on
any arm below about 13%, which is what [#264]'s hazard - an arm that buys its
compression by not opening a file - looks like when it actually happens.

The reading line also prints each arm's own interval, because "reads between
20% and 34% against a control at 37.5%" is what the data support and what a
reader wants; and the **null resolution**, the margin an arm that fell by
nothing could have cleared at the reps actually run. The registered margin and
the reps were never checked against each other, which is how a 15-point margin
came to be registered for a design whose best case resolves 10.
`--null-resolution N RATE` runs that check before a round buys any generation.

What an `inconclusive` guardrail blocks is a registration decision and this
file does not make it. The verdict is evidence; the disposition belongs to the
round.

*Origin: the three-way form is `codex`'s on `bash tools/consult.sh`. My own
proposal fired `HARMED` whenever the difference interval excluded zero, which
is not mutually exclusive with clearing the margin - a precise 10-point fall
would have been both - and which would have labelled both round 59 arms HARMED
at upper bounds of -0.9 and -0.05 points, firing more often than the test it
replaced. `codex` computed those bounds and I confirmed them before adopting
the correction. `codex` also drew the line above between the scorer's verdict
and the round's disposition, and warned that a number printed after a round
cannot stop a bad margin being registered before one, which is what the
`--null-resolution` flag is for. `deepseek` and `kimi` did not answer.*

*Origin: the blocked log-words estimand and the six-cell sign-test arithmetic
came from the `codex` delegate target on `bash tools/consult.sh` before round
59 was registered, as did the post-treatment objection to blocking on the
reading stratum. `kimi` supplied the per-shard reading and the argument for
giving every shard every case. Both were adopted before any generation;
`deepseek` did not answer either time.*

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#278]: https://github.com/JordanMPDS/laconic/issues/278
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
from subagent import fisher_exact  # noqa: E402

SEED = 58
FULL_ARM = "laconic"
READING_CASES = ["design-cache", "design-realtime", "design-upload"]
CONTRACT_CASES = ["destructive", "code-fidelity", "badnews"]
#: Round 58's registered prose-words scope, and the default so its published
#: numbers reproduce. Round 59 passes all six cases.
WORDS_CASES = list(READING_CASES)
#: Resamples for the blocked log-words test. Enough to resolve p to ~0.002,
#: which is finer than any threshold the round reads.
BLOCK_RESAMPLES = 20000

#: Registered before generation in round 58, and not moved since - see the
#: #278 section above. An arm is non-inferior on reading rate when the lower
#: bound of its difference against `laconic` clears this, harmed when the upper
#: bound falls below it, and unresolved by the design in between.
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


def comparison_arms(runs):
    """Every arm in the snapshot except the control, in a stable order.

    Read off the data rather than hardcoded, so a round that adds an arm does
    not also have to edit this file - which is how a scorer ends up silently
    omitting the arm the round was bought for.
    """
    return sorted({r["arm"] for r in runs} - {FULL_ARM})


def shards(runs):
    """[(generator, its runs)] - one entry per process that wrote into the
    round, in a stable order.

    Round 59 gives every shard every case (`run.py --rep-offset`), so a
    per-shard read of the primary is a genuine robustness check rather than a
    restatement of which cases that process happened to own. Both delegate
    targets asked for it: an effect carried by one process is indistinguishable
    from a wall-clock or CLI-release artefact, and the pooled number alone
    cannot show that.
    """
    by = {}
    for r in runs:
        by.setdefault(r.get("generator") or "unstamped", []).append(r)
    return sorted(by.items())


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


def _wilson_upper(k, n, z=1.645):
    """One-sided upper bound on a proportion, by symmetry with the lower bound
    on the failures. Same z, so the two composed give a 90% interval."""
    if not n:
        return 1.0
    return 1 - _wilson_lower(n - k, n, z)


def _diff_upper(k1, n1, k2, n2):
    """Upper bound on p1 - p2, Newcombe's construction mirrored."""
    if not n1 or not n2:
        return 1.0
    p1, p2 = k1 / n1, k2 / n2
    u1 = _wilson_upper(k1, n1)
    l2 = _wilson_lower(k2, n2)
    return (p1 - p2) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def reading_verdict(k, n, full_k, full_n):
    """(verdict, lower, upper) - the three outcomes of the non-inferiority
    test, kept distinct. See the #278 section at the top of this file.

    The three are mutually exclusive and exhaustive because lower <= upper: a
    margin cannot sit below the lower bound and above the upper bound at once.
    """
    lower = _diff_lower(k, n, full_k, full_n)
    upper = _diff_upper(k, n, full_k, full_n)
    if lower > MARGIN:
        return "non-inferior", lower, upper
    if upper < MARGIN:
        return "HARMED", lower, upper
    return "inconclusive", lower, upper


def certifiable_fall(n, full_k, full_n):
    """The largest observed fall in reading rate that still clears MARGIN at
    these reps, as a difference in proportions, or None if nothing does.

    This is the check #278 says nobody ran: the margin and the reps were never
    compared, and at n = 120 against a control near a third a 15-point margin
    certifies only arms that fall by less than 5 points. A margin whose name
    says it tolerates 15 and whose design tolerates 5 is not describing
    itself, and the gap is invisible unless it is printed.

    Not a power calculation - it assumes the observed control rate rather than
    a true effect and a target power, neither of which any round registers,
    and it is conditional on that rate, since a rate near 0 or 1 resolves much
    finer. It is an exact search over the counts rather than an approximation,
    which costs n calls and is free at any n a round can afford.
    """
    if not full_n or not n:
        return None
    for k in range(n + 1):
        if _diff_lower(k, n, full_k, full_n) > MARGIN:
            fall = k / n - full_k / full_n
            # A positive answer means the smallest clearing count is above the
            # control's own: the design cannot certify the margin even for an
            # arm that fell by nothing, which is a different failure and gets
            # its own value rather than a misleading negative one.
            return fall if fall <= 0 else None
    return None


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


def blocked_log_words(runs, arm, cases, seed=SEED, strata=False):
    """Mean difference in log prose words against the control, blocked on the
    case, with a permutation p-value.

    Each block contributes the difference of its two arm means and every block
    weighs the same, so one wide cell cannot carry the contrast. Labels are
    permuted inside the block, which is the null the design supports: the case
    is fixed before the round and the arm is what was assigned within it.

    **`strata=True` additionally blocks on the reading stratum, and that is a
    secondary and not the primary (#275).** `grounded()` reads `num_turns`,
    which is the run's own behaviour under the treatment: an arm can change
    whether a response opens a file, and conditioning on a post-treatment
    variable is not identified by the randomisation. Round 58 registered the
    stratified block as its primary and round 59 demotes it, because the
    quantity the product needs is the total effect of shipping the slice -
    length as it actually comes out, reading included. An arm that bought its
    compression by not reading is caught by the reading-rate guardrail, which
    is the endpoint built for it, rather than conditioned away here.
    """
    blocks = []
    for case in cases:
        for stratum in ((True, False) if strata else (None,)):
            rows_ = [r for r in runs
                     if r["case"] == case
                     and (stratum is None or grounded(r) is stratum)
                     and r["arm"] in (arm, FULL_ARM)]
            a = [math.log(max(prose_words(r), 1)) for r in rows_ if r["arm"] == arm]
            b = [math.log(max(prose_words(r), 1)) for r in rows_
                 if r["arm"] == FULL_ARM]
            if a and b:
                blocks.append((a, b))
    if not blocks:
        return None
    obs = sum(sum(a) / len(a) - sum(b) / len(b) for a, b in blocks) / len(blocks)
    rnd = random.Random(seed)
    hits = 0
    for _ in range(BLOCK_RESAMPLES):
        total = 0.0
        for a, b in blocks:
            pool = a + b
            rnd.shuffle(pool)
            total += sum(pool[:len(a)]) / len(a) - sum(pool[len(a):]) / len(b)
        if abs(total / len(blocks)) >= abs(obs) - 1e-12:
            hits += 1
    return obs, math.exp(obs), (hits + 1) / (BLOCK_RESAMPLES + 1), len(blocks)


def arrows_carried(runs, arm, cases):
    """(responses carrying an arrow, responses) - the round 59 manipulation
    check, not an endpoint. An arm with the arrow rule deleted that produces no
    more arrows than the control did not receive its treatment."""
    rows = [r for r in runs if r["arm"] == arm and r["case"] in cases]
    hit = sum(1 for r in rows
              if sum(metrics.arrow_forms(r.get("text") or "").values()))
    return hit, len(rows)


def report(runs, cases_dir, out=print, words_cases=None, arms=None):
    words_cases = list(words_cases or WORDS_CASES)
    arms = list(arms if arms is not None else comparison_arms(runs))
    full_k, full_n = reading(runs, FULL_ARM)
    out("reading rate, %s cells, grounded = num_turns > 1 "
        "(90%% intervals, margin %+.1f pts)" % (len(READING_CASES),
                                                100 * MARGIN))
    out("  %-18s %3d/%-3d  %5.1f%%  [%.1f, %.1f]"
        % (FULL_ARM, full_k, full_n, 100 * full_k / full_n if full_n else 0,
           100 * _wilson_lower(full_k, full_n),
           100 * _wilson_upper(full_k, full_n)))
    verdicts = {}
    for arm in arms:
        k, n = reading(runs, arm)
        verdict, lower, upper = reading_verdict(k, n, full_k, full_n)
        p = fisher_exact(k, n - k, full_k, full_n - full_k)
        verdicts[arm] = {"reading_verdict": verdict,
                         "reading_bounds": (lower, upper)}
        out("  %-18s %3d/%-3d  %5.1f%%  [%.1f, %.1f]  diff %+5.1f pts "
            "[%+.1f, %+.1f] -> %s (Fisher p = %.4f)"
            % (arm, k, n, 100 * k / n if n else 0,
               100 * _wilson_lower(k, n), 100 * _wilson_upper(k, n),
               100 * ((k / n if n else 0) - (full_k / full_n if full_n else 0)),
               100 * lower, 100 * upper, verdict, p))
    # #278: the margin and the reps were never checked against each other, so
    # the check is printed beside the result it governs rather than left to a
    # reader to run by hand.
    for n in sorted({reading(runs, arm)[1] for arm in arms}):
        fall = certifiable_fall(n, full_k, full_n)
        out("  at %d runs an arm this design certifies a %+.1f pt margin only "
            "for arms that fall by less than %s"
            % (n, 100 * MARGIN,
               "nothing at all" if fall is None else "%.1f pts" % (-100 * fall)))

    out("\nprose words, blocked on case, %d cells, permutation seed %d "
        "(THE PRIMARY)" % (len(words_cases), SEED))
    for arm in arms:
        got = blocked_log_words(runs, arm, words_cases)
        if not got:
            out("  %-18s no block with both arms in it" % arm)
            continue
        diff, ratio, p, nblocks = got
        verdicts[arm]["log_words_ratio"] = ratio
        verdicts[arm]["log_words_p"] = p
        out("  %-18s %+.4f log words, ratio %.3fx against %s, %d blocks, "
            "p = %.4f" % (arm, diff, ratio, FULL_ARM, nblocks, p))

    out("\nprose words, additionally blocked on the reading stratum "
        "(secondary: conditions on num_turns, which is post-treatment)")
    for arm in arms:
        got = blocked_log_words(runs, arm, words_cases, strata=True)
        if not got:
            out("  %-18s no block with both arms in it" % arm)
            continue
        diff, ratio, p, nblocks = got
        verdicts[arm]["log_words_ratio_stratified"] = ratio
        verdicts[arm]["log_words_p_stratified"] = p
        out("  %-18s %+.4f log words, ratio %.3fx against %s, %d blocks, "
            "p = %.4f" % (arm, diff, ratio, FULL_ARM, nblocks, p))

    out("\nthe primary per shard (diagnostic, not an endpoint: a contrast "
        "carried by one process is a warning, not a finding)")
    for arm in arms:
        for shard, rows in shards(runs):
            got = blocked_log_words(rows, arm, words_cases)
            out("  %-18s %-26s %s"
                % (arm, shard,
                   "no block with both arms in it" if not got else
                   "ratio %.3fx, %d blocks, p = %.4f" % (got[1], got[3], got[2])))

    out("\nprose words per cell, grounded stratum, permutation seed %d "
        "(robustness, not the primary)" % SEED)
    for arm in arms:
        wins = 0
        cells = 0
        for case in words_cases:
            a, b = words(runs, arm, case), words(runs, FULL_ARM, case)
            if not a or not b:
                out("  %-18s %-16s no grounded stratum on one side" % (arm, case))
                continue
            cells += 1
            ma, mb = metrics.median(a), metrics.median(b)
            wins += ma < mb
            out("  %-18s %-16s %6.1f vs %6.1f  n=%d/%d  p = %.4f"
                % (arm, case, ma, mb, len(a), len(b),
                   metrics.permutation(a, b, SEED)))
        if cells:
            out("  %-18s sign test %d of %d cells shorter, p = %.4f"
                % (arm, wins, cells, metrics.sign_test(wins, cells)))
            verdicts[arm]["words_cells_shorter"] = (wins, cells)

    out("\nnever-cut keyword failures, %s (smoke alarm, not equivalence)"
        % ", ".join(CONTRACT_CASES))
    fbad, fn = contract(runs, FULL_ARM, cases_dir)
    out("  %-18s %3d/%-3d" % (FULL_ARM, fbad, fn))
    for arm in arms:
        bad, n = contract(runs, arm, cases_dir)
        fatal = bad > CONTRACT_FATAL and fbad <= CONTRACT_FULL_MAX
        verdicts[arm]["contract_ok"] = not fatal
        out("  %-18s %3d/%-3d  rule-of-three upper bound %.1f%%  -> %s"
            % (arm, bad, n, 100 * 3 / n if n else 100,
               "CATASTROPHIC" if fatal else "no alarm"))

    out("\nresponses carrying an arrow (manipulation check, not an endpoint)")
    ak, an = arrows_carried(runs, FULL_ARM, words_cases)
    out("  %-18s %3d/%-3d" % (FULL_ARM, ak, an))
    for arm in arms:
        k, n = arrows_carried(runs, arm, words_cases)
        verdicts[arm]["arrows"] = (k, n)
        out("  %-18s %3d/%-3d  (Fisher p = %.4f)"
            % (arm, k, n, fisher_exact(k, n - k, ak, an - ak)))
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

    # #278. The three verdicts have to partition the outcomes, and the two
    # rounds that have run this test have to come out of it saying what the
    # data actually support. Every count below is read off an immutable
    # snapshot, so these are regression checks and not illustrations.
    check("the three verdicts are exclusive and exhaustive over every count",
          all(sum(reading_verdict(k, 120, 45, 120)[0] == v
                  for v in ("non-inferior", "HARMED", "inconclusive")) == 1
              for k in range(121)))
    check("bounds never cross, so no count can be both",
          all(reading_verdict(k, 120, 45, 120)[1]
              <= reading_verdict(k, 120, 45, 120)[2] for k in range(121)))
    check("round 58's laconic-min-a was never ruled against, only unresolved",
          reading_verdict(23, 90, 30, 90)[0] == "inconclusive")
    check("round 59's abl-shown likewise",
          reading_verdict(32, 120, 45, 120)[0] == "inconclusive")
    check("round 59's abl-arrow likewise",
          reading_verdict(33, 120, 45, 120)[0] == "inconclusive")
    check("round 58's laconic-min-b is still certified non-inferior",
          reading_verdict(37, 90, 30, 90)[0] == "non-inferior")
    # The rule I proposed before consulting - HARMED whenever the interval
    # excludes zero - would have taken both round 59 arms, whose upper bounds
    # are -0.9 and -0.05 points. It has to stay excluded.
    check("an arm whose interval excludes zero is not harmed on that alone",
          _diff_upper(32, 120, 45, 120) < 0
          and reading_verdict(32, 120, 45, 120)[0] != "HARMED")
    check("#264's hazard, an arm that stopped reading, is HARMED",
          reading_verdict(0, 120, 45, 120)[0] == "HARMED")
    check("and so is one that reads a third as often",
          reading_verdict(10, 120, 45, 120)[0] == "HARMED")
    check("an arm that reads more than the control is never harmed",
          reading_verdict(90, 120, 45, 120)[0] == "non-inferior")
    check("a 15-point margin at n=120 certifies only a 5-point fall",
          abs(-100 * certifiable_fall(120, 45, 120) - 5.0) < 0.05)
    check("the fall it names is the smallest one that really clears",
          _diff_lower(39, 120, 45, 120) > MARGIN
          and _diff_lower(38, 120, 45, 120) < MARGIN)
    check("quadrupling the reps buys a wider tolerance",
          -certifiable_fall(480, 180, 480) > -certifiable_fall(120, 45, 120))
    check("a design too small to certify even a zero fall says so",
          certifiable_fall(4, 2, 4) is None)
    check("it does not divide by zero on an arm with no runs",
          certifiable_fall(0, 45, 120) is None
          and certifiable_fall(120, 0, 0) is None)

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
          v["laconic-min-a"]["reading_verdict"] == "non-inferior")
    check("an arm that stopped reading is reported harmed, not unresolved",
          v["laconic-min-b"]["reading_verdict"] == "HARMED")
    check("the report prints the margin-against-reps check beside the verdict",
          any("this design certifies" in ln for ln in lines))
    check("a shorter arm sweeps the word cells",
          v["laconic-min-a"]["words_cells_shorter"] == (3, 3))
    check("an arm with no grounded stratum reports no word cells",
          "words_cells_shorter" not in v["laconic-min-b"])
    check("the contract alarm stays silent when nothing was generated",
          all(v[a]["contract_ok"] for a in ("laconic-min-a", "laconic-min-b")))
    check("the comparison arms are discovered from the runs",
          comparison_arms(runs) == ["laconic-min-a", "laconic-min-b"])

    # #275's primary. The per-cell median cannot see an effect this small, so
    # the blocked test has to, and a scorer that reported an effect on runs
    # with none would be worse than no scorer.
    check("the blocked test recovers a known ratio",
          abs(blocked_log_words(runs, "laconic-min-a", READING_CASES)[1]
              - 0.4) < 0.01)
    check("and calls it significant",
          blocked_log_words(runs, "laconic-min-a", READING_CASES)[2] < 0.01)
    import random as _r
    _rnd = _r.Random(1)
    null = [dict(r, text="word " * _rnd.randint(80, 120))
            for r in runs if r["arm"] in (FULL_ARM, "laconic-min-a")]
    _null = blocked_log_words(null, "laconic-min-a", READING_CASES)
    check("two arms drawn from one distribution do not separate",
          _null[2] > 0.05 and 0.9 < _null[1] < 1.1)
    check("the blocked test refuses a scope it has no block for",
          blocked_log_words(runs, "laconic-min-a", ["no-such-case"]) is None)

    # Blocking is the point: an arm that is shorter inside every stratum but
    # reads far less often has a *higher* marginal mean, which is #131's trap.
    # The blocked estimand must report the within-stratum truth.
    simpson = []
    for arm, rate, short, long_ in ((FULL_ARM, 0.9, 100, 200),
                                    ("laconic-min-a", 0.1, 80, 160)):
        for case in READING_CASES:
            for rep in range(60):
                deep = rep < rate * 60
                simpson.append({"arm": arm, "case": case, "model": "sonnet",
                                "rep": rep, "ok": True,
                                "num_turns": 3 if deep else 1,
                                "text": "word " * (long_ if deep else short)})
    check("blocking survives a Simpson reversal the marginal median would miss",
          blocked_log_words(simpson, "laconic-min-a", READING_CASES,
                            strata=True)[1] < 0.85)

    # The two blocks answer different questions and this is the fixture where
    # they disagree: an arm 1.2x longer inside *both* strata, which reads so
    # much less often that its answers are shorter as they actually come out.
    # The primary must report the total effect (0.69x) and the secondary the
    # within-stratum one (1.20x). A scorer that silently reported the second as
    # the first would say a shipped slice compresses when it lengthens every
    # answer it is compared against at equal reading.
    both = []
    for arm, rate, short, long_ in ((FULL_ARM, 0.9, 100, 200),
                                    ("laconic-min-a", 0.1, 120, 240)):
        for case in READING_CASES:
            for rep in range(60):
                deep = rep < rate * 60
                both.append({"arm": arm, "case": case, "model": "sonnet",
                             "rep": rep, "ok": True,
                             "num_turns": 3 if deep else 1,
                             "text": "word " * (long_ if deep else short)})
    check("the primary reports the total effect, reading included",
          abs(blocked_log_words(both, "laconic-min-a", READING_CASES)[1]
              - 0.689) < 0.01)
    check("the secondary reports the within-stratum effect, which is the "
          "other direction",
          abs(blocked_log_words(both, "laconic-min-a", READING_CASES,
                                strata=True)[1] - 1.2) < 0.01)
    check("the primary blocks per case and the secondary per case and stratum",
          (blocked_log_words(both, "laconic-min-a", READING_CASES)[3],
           blocked_log_words(both, "laconic-min-a", READING_CASES,
                             strata=True)[3]) == (3, 6))

    check("shards are split on the generator that wrote each run",
          [k for k, _ in shards([{"generator": "b"}, {"generator": "a"},
                                 {"generator": "b"}])] == ["a", "b"])
    check("a run with no generator stamp is still assigned a shard",
          shards([{"case": "x"}])[0][0] == "unstamped")

    # The manipulation check has to count responses, not arrows, or one
    # arrow-heavy answer would read as a delivered treatment.
    arrowy = [{"arm": "laconic-abl-arrow", "case": "design-cache",
               "model": "sonnet", "rep": i, "ok": True, "num_turns": 2,
               "text": "a -> b" if i < 7 else "plain prose"} for i in range(10)]
    check("the arrow check counts responses carrying one",
          arrows_carried(arrowy, "laconic-abl-arrow", ["design-cache"]) == (7, 10))

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
    ap.add_argument("--words-cases", default=",".join(WORDS_CASES),
                    help="prose-words scope; round 58 registered three cells "
                         "and round 59 registers six")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--certifiable-fall", nargs=2, type=float,
                    metavar=("N", "CONTROL_RATE"),
                    help="check the margin against planned reps before buying "
                         "any generation: prints the largest fall the "
                         "registered margin could certify at N runs an arm "
                         "against a control reading at CONTROL_RATE. Assumes "
                         "equal reps per arm, which is how every round has "
                         "run it. See #278")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.certifiable_fall:
        n, rate = int(args.certifiable_fall[0]), args.certifiable_fall[1]
        fall = certifiable_fall(n, round(n * rate), n)
        print("at %d runs an arm and a control reading %.1f%%, the registered "
              "%+.1f pt margin certifies only arms that fall by less than %s"
              % (n, 100 * rate, 100 * MARGIN,
                 "nothing at all" if fall is None
                 else "%.1f pts" % (-100 * fall)))
        return 0
    if not args.snapshots:
        ap.error("give at least one snapshot, or --selftest")
    runs, versions = load(args.snapshots)
    print("%d usable runs, CLI %s\n" % (len(runs), ", ".join(versions)))
    report(runs, Path(args.cases_dir),
           words_cases=[c for c in args.words_cases.split(",") if c])
    return 0


if __name__ == "__main__":
    sys.exit(main())
