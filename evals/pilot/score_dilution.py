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

*Origin: the blocked log-words estimand and the six-cell sign-test arithmetic
came from the `codex` delegate target on `bash tools/consult.sh` before round
59 was registered, as did the post-treatment objection to blocking on the
reading stratum. `kimi` supplied the per-shard reading and the argument for
giving every shard every case. Both were adopted before any generation;
`deepseek` did not answer either time.*

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#270]: https://github.com/JordanMPDS/laconic/issues/270
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
    out("reading rate, %s cells, grounded = num_turns > 1" % len(READING_CASES))
    out("  %-18s %3d/%-3d  %5.1f%%" % (FULL_ARM, full_k, full_n,
                                       100 * full_k / full_n if full_n else 0))
    verdicts = {}
    for arm in arms:
        k, n = reading(runs, arm)
        lower = _diff_lower(k, n, full_k, full_n)
        p = fisher_exact(k, n - k, full_k, full_n - full_k)
        ok = lower > MARGIN
        verdicts[arm] = {"reading_non_inferior": ok}
        out("  %-18s %3d/%-3d  %5.1f%%  diff %+5.1f pts, lower bound %+5.1f, "
            "margin %+5.1f -> %s (Fisher p = %.4f)"
            % (arm, k, n, 100 * k / n if n else 0,
               100 * ((k / n if n else 0) - (full_k / full_n if full_n else 0)),
               100 * lower, 100 * MARGIN,
               "non-inferior" if ok else "INFERIOR", p))

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
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.snapshots:
        ap.error("give at least one snapshot, or --selftest")
    runs, versions = load(args.snapshots)
    print("%d usable runs, CLI %s\n" % (len(runs), ", ".join(versions)))
    report(runs, Path(args.cases_dir),
           words_cases=[c for c in args.words_cases.split(",") if c])
    return 0


if __name__ == "__main__":
    sys.exit(main())
