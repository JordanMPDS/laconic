#!/usr/bin/env python3
"""Turn the committed snapshots into markdown tables, and enforce gates.

Runs entirely offline: no network, no third-party packages. Exits non-zero
when a gate fails, so a rules regression fails a command instead of waiting
for somebody to notice a number moved.
"""
import argparse
import json
import math
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
import judge as bench_judge  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"
ARM_ORDER = ["baseline", "terse-control", "word-compression",
             "concise-style", "laconic"]
# A ratio of small integers is not evidence: floor/sonnet laconic (26 words,
# 0 auxiliary verbs) and code-fidelity/haiku baseline (49 words, ~1 auxiliary
# verb) both clear a *rate* floor trivially - one short correct answer with
# no auxiliary in it is terse English, not a degraded ratio. What actually
# protects the comparison is an absolute floor on how many article/auxiliary
# words the baseline had to begin with: below ABS_COUNT_FLOOR that case/model
# has too little raw material for "below 70% of baseline" to mean anything,
# regardless of what the rate says. RATE_FLOOR is kept as a cheap secondary
# sanity check, but ABS_COUNT_FLOOR is the one doing the real work.
RATE_FLOOR = 0.02
ABS_COUNT_FLOOR = 5

# Where a case's trap criteria came from, which decides what its verdicts may
# be used for. Published as a column so a reader cannot mistake a
# rule-adherence row for evidence about answer quality - two cases (decision,
# floor) were read that way once already and the claim had to be retracted.
GRADINGS = ("quality", "safety", "rule-adherence")
UNKNOWN_GRADING = "unclassified"


# The two gradings whose verdicts reach a fatal counter: quality_fails and
# safety_fails, and nothing else. A rule-adherence case is judged and displayed
# and may not be optimized against, so its verdicts decide nothing; an
# unclassified one has no criteria provenance to decide with.
JUDGE_GATE_GRADINGS = ("quality", "safety")


def _expect(case, cases_dir=None):
    """A case's expect.json, or {} if it has none.

    cases_dir exists for judge.py, which runs against evals/holdout as well as
    evals/cases and would otherwise read every holdout case as unclassified.
    """
    p = (Path(cases_dir) if cases_dir else CASES) / case / "expect.json"
    return json.loads(p.read_text()) if p.exists() else {}


def case_grading(case, cases_dir=None):
    """A case with no grading field is reported as unclassified, never
    silently promoted to quality."""
    g = _expect(case, cases_dir).get("grading")
    return g if g in GRADINGS else UNKNOWN_GRADING


def case_saturated_models(case, cases_dir=None):
    """Models whose cell a case's expect.json marks as unable to signal a rule
    edit. Two mechanisms qualify, and each entry names which one it is:

    - **Stuck at fail.** The cell fails under every rules revision tested, so
      its verdicts are a constant plus sampling noise. destructive/haiku is the
      motivating cell: 30 of 30 across six gradings, criterion verified against
      PostgreSQL 16 in #18.
    - **Stuck at a coin flip.** The cell's own master-rules rate is near 50%,
      where a binomial's variance is largest, so its per-round count swings
      several counts under no treatment. ordered-steps/haiku is that cell, at
      29 of 60 (#78). The measured-rate screen handles its own rise but not the
      round-wide total it feeds, and that total is what decides whether the
      fatal check runs at all.

    A saturated cell stays generated, judged and displayed; it leaves only the
    fatal judge-verdict counters, where at small reps a stray flip is
    indistinguishable from an edit effect (#45)."""
    d = _expect(case, cases_dir).get("saturated_models")
    return d if isinstance(d, dict) else {}


def feeds_judge_gate(case, model, cases_dir=None):
    """Can this cell's verdict reject a round?

    Only quality_fails and safety_fails read judgments at all, and both filter
    on the case's grading and skip saturated cells - so `conditional`,
    `decision`, `floor` and `ordered-steps`/haiku are graded every round and
    cannot move any gate. That is 35 of the 220 judge calls a round buys at
    n=5. judge.py skips them by default and _judge_fail_cells
    below reads it too, so the filter and the gate cannot come apart.

    What is given up by skipping them is disclosure, not scoring: those
    verdicts are how a round sees whether the rules were obeyed on the cases
    that grade adherence to them. A hypothesis that names one of those cases
    must judge them - see --judge-all.
    """
    return (case_grading(case, cases_dir) in JUDGE_GATE_GRADINGS
            and model not in case_saturated_models(case, cases_dir))


_median = metrics.median


# The noise floor is the published dispersion, not a fresh invention: 260 is
# the median per-cell output-token stdev over the laconic arm's sonnet cells
# in the committed baseline snapshot (evals/snapshots/loop/round-01-n10.json,
# 14 cells at n=10 reps), and 0.35 is the preference judge's measured flip
# rate on 2026-08-01. A move smaller than the instrument's own noise is not an
# improvement, and a loop that treats it as one churns forever.
#
# This was 175 until the laconic arm was regenerated under current rules on
# 2026-08-04, and 209 until the #45 n=10 regeneration added the three
# high-dispersion design-question cases on 2026-08-06. The floor tracks
# whatever the published snapshot disperses at, so it rose both times and the
# gate is stricter than it was.
NOISE = {"stdev": 260, "flip_rate_max": 0.35, "alpha": 0.05}

# Each rejects on its own, whatever the target metric did. Compression bought
# by dropping a never-cut item is not a cheaper answer, it is a different and
# worse one.
#
# safety_fails was missing until 2026-08-04, and the gap was not theoretical.
# destructive/haiku failed 3 of 5, then 4 of 5, then 5 of 5 across rounds 01,
# 03 and 04 - the model names the sessions cascade and calls it "safe" - and no
# gate saw any of it. never_cut_failures is a substring check, so a response
# that names the thing and then characterises it as harmless passes it; and
# destructive is graded safety, so quality_fails skipped it by construction. An
# edit could have doubled that cell's failure rate and the round would still
# have printed "never-cut held, quality held".
FATAL = (("never_cut_failures", "never-cut"),
         ("quality_fails", "quality"),
         ("safety_fails", "safety"),
         ("violations_total", "readability"))

# The non-token metrics a hypothesis may name. They are counts of rare events,
# not distributions, so the token gate's sign-test-plus-median-shift does not
# transfer: with 7 violations spread over three case/model cells, a sign test
# across cells cannot reach alpha however large the improvement is, and a
# token-stdev floor is meaningless for a count.
#
# The first four are FATAL as well - each rejects a round on its own. one_turn
# is a target only, and deliberately: the fatal four are harm counters, and not
# opening a file is not harm. On floor, decision, code-fidelity and
# ordered-steps there is nothing to open and one turn is the only possible
# behaviour. The harm it predicts is already covered by quality_fails, which is
# fatal; what this counter adds is resolution, not coverage.
COUNT_TARGETS = ("never_cut_failures", "quality_fails", "safety_fails",
                 "violations_total", "one_turn")

# Between-round overdispersion on one_turn, pooled from two estimates computed
# on opposite sides of the same contrast (#46). Seven independent generations of
# byte-identical licence rules give chi-square 18.16 on 6 df; three batches of
# byte-identical master rules on the three #88 cases give 8.97 on 2 df. Pooled,
# 27.13 on 8 df.
#
# The binomial split _count_p assumes is therefore optimistic by about the
# square root of this, the same shape of error #103 documents for
# violations_total - and, by coincidence of two unrelated mechanisms, almost the
# same size. Unlike #103's clustering, no within-round resample recovers this:
# the extra variance is BETWEEN rounds, and a bootstrap over responses inside
# one round cannot see it.
#
# The real fix is design, not statistics. Generating both sides of a comparison
# in one interleaved batch removes the between-batch component outright, and
# resolved a contrast at 40 runs a side that the archive could not resolve at
# any n (evals/results/loop/interleaved-batch.md). report.py cannot tell whether
# two snapshots were interleaved, so it applies the inflation regardless and
# prints the same test at phi = 1 beside it. A round that did interleave should
# say so in its round doc and may cite that uninflated figure.
ONE_TURN_PHI = 3.39


# A measured rate below this many runs does not clear anything. At n = 10 the
# interval is wide enough to cover almost any count, which would turn the screen
# off rather than sharpen it - and a single n = 10 draw is the defect this
# exists to correct, so accepting one as the correction would be circular.
CELL_RATE_MIN_RUNS = 30
CELL_RATES = ROOT / "evals" / "snapshots" / "loop" / "cell-rates.json"

# A cell with at least this many runs on BOTH sides is compared as a rate, with
# a test, rather than as one count against another (#133). Below it, nothing
# changes: the count comparison and the measured-rate screen above stand.
#
# The bar is where the test has enough power to be worth having. With the
# control cell at 0, the smallest treatment count that reaches alpha = 0.05
# one-sided is:
#
#     n per side   5    10    15    20    25    30    40
#     detects     80%   40%   27%   25%   20%   17%   12%   of the cell
#
# At five or ten runs a side the test would clear four fifths of a cell failing
# outright, which is not a sharper gate but a broken one - so those rounds keep
# the rule they were scored under. At twenty it detects a quarter of a cell,
# which is a regression worth the name. Round 25 is the first round the loop
# has run at 25 reps a side, and it is the first round this can act on: the
# re-score in evals/results/loop/count-vs-rate.md moves no stored verdict.
CELL_TEST_MIN_RUNS = 20

# A scoped output_tokens cell whose baseline is shorter than this does not vote
# in the sign test. The test counts votes, so a cell that cannot express the
# effect still casts one, and two such cells rejected rounds 11 and 14 outright
# while every other cell fell and the median shift grew.
#
# Set from the measured gap, not tuned: every cell that has ever moved outside
# its own noise has a baseline median of at least 1486 tokens
# (design-audit-log/haiku), and every cell that never has is at most 978
# (design-alerting/haiku). No cell sits between. The mechanism is why: this
# target measures compression of design answers, and a 600-to-1000-token answer
# has a few hundred tokens of headroom, which is the size of its own dispersion.
#
# It governs only the scoped sign test. No fatal counter reads it, dropped cells
# are named in the verdict, the six-cell floor applies to what remains, and the
# cells are still generated, judged and tabulated.
# See evals/results/loop/token-scope.md.
TOKEN_CELL_MIN_BASELINE = 1200

# How many runs a reading stratum needs before a cell's median may be taken
# from it (#131). Two, because that is what the floor's stdev needs, and the
# rule this governs asks only whether a stratum EXISTS, not whether it is
# powered: a cell votes inside the grounded stratum when both rounds have one,
# inside the unread stratum when neither does, and not at all when the reading
# rate crossed between the two.
#
# Not raised to a powered number, because raising it does not make the estimate
# better - it refiles cells. At three, a cell that read 4 of 10 is classed
# "unread" and its four grounded answers are dropped from a comparison of
# unread ones, which is a worse statistic than a noisy median. Bootstrapped
# over the round-25 and round-26 control cells, the sampling error of a median
# taken from two grounded runs is 455 to 526 tokens against a floor of 679 to
# 767 built from the same cells, so a two-run median sits inside the dispersion
# the floor already tolerates. See evals/results/loop/stratified-tokens.md.
GROUNDED_MIN_RUNS = 2


def _binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p). Exact; n here is a handful of events."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _fisher_upper_tail(k1, n1, k2, n2):
    """One-sided Fisher exact: P(treatment >= k1) at the observed margins.

    k1 of n1 is the round's cell, k2 of n2 the side it is compared against.
    Hypergeometric, summed from the observed count up, so it answers "could a
    cell this size draw this many failures by chance" rather than the
    two-sided question, which would spend half its alpha on an improvement.
    """
    def lf(n):
        return math.lgamma(n + 1)

    def hyp(a, b, c, d):
        return math.exp(lf(a + b) + lf(c + d) + lf(a + c) + lf(b + d)
                        - lf(a) - lf(b) - lf(c) - lf(d) - lf(a + b + c + d))
    total = 0.0
    for i in range(k1, min(n1, k1 + k2) + 1):
        j, k = n1 - i, (k1 + k2) - i
        l = n2 - k
        if j < 0 or k < 0 or l < 0:
            continue
        total += hyp(i, j, k, l)
    return min(1.0, total)


def _sample_covers(cur_count, cur_runs, prev_count, prev_runs, alpha):
    """Is this cell's rise inside the sampling noise of the two draws (#133)?

    The fatal counters ask whether one count exceeds another. That question
    has no answer when both sides are draws from the same cell: round 25 lost
    quality on four cells whose pooled rates were 39 of 199 against 81 of 394,
    Fisher p = 0.83, and two of the four had a control count of 0, which any
    single failure exceeds. A count is not evidence; a rate with an interval
    is.

    So where both sides have enough runs to estimate a rate - CELL_TEST_MIN_RUNS,
    which is about power, not about ceremony - ask whether the treatment cell
    is higher than the control cell at the same alpha the rest of the gate
    uses. Where either side is short, this returns False and the cell is scored
    exactly as it was before, which is why no stored round moves.

    This is the same correction _rate_covers makes against a separately
    measured master-rules rate, applied to the case where the comparison's own
    control side is large enough to supply the rate.
    """
    if cur_runs < CELL_TEST_MIN_RUNS or prev_runs < CELL_TEST_MIN_RUNS:
        return False
    return _fisher_upper_tail(cur_count, cur_runs,
                              prev_count, prev_runs) >= alpha


def _rate_covers(rate, count, runs, alpha):
    """Is `count` failures in `runs` an ordinary draw from a cell at `rate`?

    The fatal counters compare a round's per-cell count against the baseline's
    count for that cell, and the baseline is one n = 10 draw. For a cell that
    fails at 8% under master rules that draw is 0 about 43% of the time, so
    "0 -> 1" is the gate reporting a coin flip as a regression. destructive
    /haiku rejected round 10 that way, and its failing responses drop `sessions`
    exactly as the master-rules failures do, with no design-question licence in
    the file at all (2 of 25, against 7 of 60 with it, Fisher p = 1.00).

    So where a cell has a rate measured under master rules at adequate n, ask
    the question the gate was always trying to ask: is this round's count
    higher than that rate predicts? One-sided, at the same alpha. A real
    regression still rejects - 5 of 10 against an 8% rate is p = 0.0007 - and a
    lottery draw no longer does.

    This never invents a rate. A cell with no measurement, or one measured on
    too few runs, keeps the baseline-draw comparison unchanged.
    """
    if not rate or runs <= 0:
        return False
    n, k = rate.get("runs", 0), rate.get("failures", 0)
    if n < CELL_RATE_MIN_RUNS:
        return False
    p = k / n
    upper_tail = 1.0 - _binom_cdf(count - 1, runs, p) if count > 0 else 1.0
    return upper_tail >= alpha


def load_cell_rates(path=None):
    """Measured per-cell failure rates, keyed by metric then "case/model"."""
    path = Path(path) if path else CELL_RATES
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return {metric: {tuple(cell.split("/", 1)): v for cell, v in cells.items()}
            for metric, cells in raw.items() if metric != "metadata"}


def _exposure(src, target):
    """How many treatment responses gave this metric a chance to move.

    Every count target but one is exposed on every response the round produced.
    one_turn is not: it is summed only over cases that have a fixture to open,
    so its denominator has to match its numerator or the rate is wrong by the
    share of fixture-less cases in the scope.
    """
    if target == "one_turn":
        return src.get("one_turn_n_runs", 0)
    return src.get("n_runs", 0)


def _count_p(prev_count, cur_count, prev_runs, cur_runs):
    """One-sided p for "the rate fell", comparing two counts of rare events.

    Conditional on the total number of events, the split between the rounds is
    binomial, so this is exact rather than a normal approximation over counts
    too small to justify one. Exposure is read from each round's own usable-run
    count instead of assumed equal, so a round that generated fewer responses
    cannot look clean merely by having had fewer chances to fail.
    """
    total = prev_count + cur_count
    if total == 0:
        return None
    denom = prev_runs + cur_runs
    q = (cur_runs / denom) if denom else 0.5
    return _binom_cdf(cur_count, total, q)


def _inflated_count_p(prev_count, cur_count, prev_runs, cur_runs, phi):
    """`_count_p` with the variance multiplied by phi.

    The exact binomial split `_count_p` computes is right when each event is an
    independent per-run Bernoulli AND the underlying rate is the same quantity
    on both sides. For one_turn the second half fails: the rate drifts between
    batches at fixed rules text (#46), so two rounds differ by more than
    sampling before any edit is applied.

    There is no exact conditional test for that, so this is a normal
    approximation on the same one-sided question - did the rate fall - with the
    standard error scaled by sqrt(phi). Returns None when nothing was counted
    on either side, matching `_count_p`, so callers need no extra branch.
    """
    total = prev_count + cur_count
    if total == 0 or prev_runs <= 0 or cur_runs <= 0:
        return None
    p_prev = prev_count / prev_runs
    p_cur = cur_count / cur_runs
    pooled = total / (prev_runs + cur_runs)
    var = phi * pooled * (1 - pooled) * (1 / prev_runs + 1 / cur_runs)
    if var <= 0:
        return None
    z = (p_cur - p_prev) / math.sqrt(var)
    # One-sided, in the direction the gate cares about: small p means the
    # current round's rate is lower than the previous round's.
    return 0.5 * math.erfc(-z / math.sqrt(2))


CLUSTER_BOOTSTRAP_DRAWS = 20000
CLUSTER_BOOTSTRAP_SEED = 103


def _cluster_count_p(prev_runs, cur_runs, draws=CLUSTER_BOOTSTRAP_DRAWS):
    """One-sided p for "the count fell", for a count whose events cluster.

    `_count_p` is exact conditional on each event being an independent per-run
    Bernoulli, which is what `never_cut_failures`, `quality_fails` and
    `safety_fails` are: a run either fails the case or it does not.

    `violations_total` is not that shape (#103). One response can carry seven
    violations, and they arrive together - a response that reaches for an arrow
    reaches for several. On the -v4 baseline's 440 laconic responses the
    per-response counts have mean 0.359 and variance 1.085, a ratio of 3.0
    where binomial assumes 1, so the binomial p is optimistic by about the
    square root of that. Rounds 16 and 17 read 0.029 and 0.016 under
    `_count_p`; pooled and bootstrapped they are 0.042.

    Resamples whole responses within each cell, which keeps a heavy response
    intact instead of spreading its violations over the round, and returns the
    share of resamples in which the round did not beat the baseline. Seeded, so
    a stored round re-scores to the same number every time.

    Both arguments map a cell to its per-response counts. Cells present on one
    side only are ignored: a cell with no baseline cannot say the count fell.
    """
    cells = [c for c in prev_runs if c in cur_runs and prev_runs[c] and cur_runs[c]]
    if not cells:
        return None
    if sum(sum(prev_runs[c]) for c in cells) == 0 and \
            sum(sum(cur_runs[c]) for c in cells) == 0:
        return None
    rng = random.Random(CLUSTER_BOOTSTRAP_SEED)
    worse = 0
    for _ in range(draws):
        prev_tot = cur_tot = 0
        for c in cells:
            pv, cv = prev_runs[c], cur_runs[c]
            for _ in range(len(pv)):
                prev_tot += pv[rng.randrange(len(pv))]
            for _ in range(len(cv)):
                cur_tot += cv[rng.randrange(len(cv))]
        if cur_tot >= prev_tot:
            worse += 1
    return worse / draws


def _rate_count_p(rates, cells, count, runs):
    """One-sided p for "the rate fell", against the measured rates, or None.

    `_count_p` compares a round's count against the previous round's, and the
    previous round is one n = 10 draw per cell. That is the defect #66 was filed
    about, and #66 fixed it for the fatal screen and not for the target: round
    16 read its scoped sonnet cells 5 -> 2 against the baseline draw, which
    looks like a clear improvement, and 2 of 30 against the measured 22 of 120
    is p = 0.165 (#96).

    Returns None unless every cell in the scope has a measured rate, so a round
    whose scope is not fully measured is scored exactly as it was before this
    existed and no stored verdict moves.

    Conditional on the total, the split between the measured runs and this
    round's is binomial - the same exact test `_count_p` uses, with the
    baseline draw replaced by the pooled measurement behind it.
    """
    if not rates or not cells:
        return None
    have = [rates[c] for c in cells if c in rates]
    if len(have) != len(cells):
        return None
    m_fail = sum(r["failures"] for r in have)
    m_runs = sum(r["runs"] for r in have)
    total = m_fail + count
    if total == 0 or not (m_runs + runs):
        return None
    return _binom_cdf(count, total, runs / (m_runs + runs))


def _scope_composition(rates, cells, runs_by_cell):
    """Which cells a scoped count target is actually going to report on.

    Round 16 registered a threshold over six cells spanning 0% to 100%. Three
    haiku cells held 26 of the 31.8 failures the scope expected, so the target
    was 82% a haiku measurement wearing a scope's name, and sonnet could have
    gone to zero and moved the total by 5 of 60. That table existed before the
    round and was not printed, so the threshold was registered without it (#96).
    """
    rows = []
    for c in cells:
        r = rates.get(c) if rates else None
        if not r or not r["runs"]:
            return []
        n = runs_by_cell.get(c, 0)
        rows.append((c, r["failures"] / r["runs"], n * r["failures"] / r["runs"]))
    rows.sort(key=lambda x: -x[1])
    return rows


def _judge_fail_cells(judg, grading):
    """Laconic judge failures of one grading, per (case, model) cell.

    Cells marked saturated in their case's expect.json are skipped: their
    verdicts cannot move with a rule edit, so counting them would hand the
    fatal gates a lottery ticket per round instead of a signal."""
    out = Counter()
    for j in judg or []:
        if (j.get("arm") == "laconic" and j.get("verdict") == "fail"
                and case_grading(j["case"]) == grading
                and feeds_judge_gate(j["case"], j.get("model"))):
            out[(j["case"], j["model"])] += 1
    return out


def _judge_fails(judg, grading, keep, ok_model=None):
    """Round or scoped total of the above."""
    ok_model = ok_model or (lambda m: True)
    return sum(n for c, n in _judge_fail_cells(judg, grading).items()
               if keep(c[0]) and ok_model(c[1]))


# Whether an answer hands a decision back to the user instead of resolving it:
# any line that is a question. Deliberately the same expression the covariate
# was measured with, in design-quality-covariate.md - re-tuning a detector
# after seeing what it found is how a disclosure becomes a story.
ASKS_BACK = re.compile(r"^[^\n]*\?\s*$", re.M)


def _quality_strata(judg, runs):
    """quality verdicts split on whether the answer handed a decision back.

    Round 15 is why this exists. Its round-wide quality count over the five
    design cases was 61 of 100 either way, Fisher p = 1.000, and the gate read
    exactly that. Split on this covariate the same 200 responses hold two real
    effects in opposite directions - answers that ask went 16 of 27 to 10 of 33
    (p = 0.036) while answers that resolve went 45 of 73 to 51 of 67 - and the
    edit shifted responses into the worse group. The counter was flat because
    the two cancelled, not because nothing moved, and the round was accepted at
    step 7 and killed by the holdout.

    Disclosure only. The covariate was found after the round it explains, by
    looking at responses whose verdicts were already known, so using it to
    reject anything would be the exact mistake pre-registration exists to
    prevent. It is reported so a cancelling pair is visible in the verdict
    rather than needing somebody to go looking for it (#88).
    """
    text = {(r["case"], r["arm"], r["model"], r["rep"]): r.get("text", "")
            for r in runs}
    out = {"asks": {"fails": 0, "n": 0}, "resolves": {"fails": 0, "n": 0}}
    for j in judg or []:
        if j.get("arm") != "laconic" or case_grading(j["case"]) != "quality":
            continue
        if j.get("verdict") == "not_exercised" and \
                j.get("reason") in bench_judge.INFRA_REASONS:
            continue
        body = text.get((j["case"], j["arm"], j["model"], j["rep"]))
        if body is None:
            continue
        s = out["asks"] if ASKS_BACK.search(body) else out["resolves"]
        s["n"] += 1
        s["fails"] += (j.get("verdict") == "fail")
    return out


def _strata_line(prev, cur):
    """The disclosure line, or None when either round lacks the block.

    Named "disclosure" in its own text because the loop's reason lines are read
    as gate output, and this one may never be read that way.
    """
    a, b = prev.get("quality_strata"), cur.get("quality_strata")
    if not a or not b:
        return None
    moved = {}
    for k in ("asks", "resolves"):
        if not a[k]["n"] or not b[k]["n"]:
            return None
        moved[k] = (b[k]["fails"] / b[k]["n"]) - (a[k]["fails"] / a[k]["n"])
    parts = ", ".join(
        "%s %d of %d -> %d of %d"
        % (label, a[k]["fails"], a[k]["n"], b[k]["fails"], b[k]["n"])
        for k, label in (("asks", "answers that hand a decision back"),
                         ("resolves", "answers that resolve it")))
    tail = ""
    if moved["asks"] * moved["resolves"] < 0:
        worse = "asks" if moved["asks"] > 0 else "resolves"
        tail = ("; the two strata moved in OPPOSITE directions, which a flat "
                "quality count hides - the %s stratum got worse"
                % ("hands-back" if worse == "asks" else "resolves"))
    return "quality strata (disclosure, not a gate): %s%s" % (parts, tail)


def _sum_forms(dicts):
    """Add up arrow_forms blocks. Keys fixed so an empty round still reports."""
    out = {"chain": 0, "mapping": 0}
    for d in dicts:
        for k in out:
            out[k] += d.get(k, 0)
    return out


def _arrow_form_line(prev, cur):
    """The chain-versus-mapping disclosure, or None when either round lacks it.

    violations_total is one number over two forms that have never moved
    together. Round 18 read 158 -> 129, a fall of 21%, over chains at -42% and
    mappings at +25%; rounds 16 and 17 did the same thing with an edit nowhere
    near the arrow rule. A round targeting one form cannot currently tell
    whether it moved it or traded it for the other.

    Disclosure, never a gate, for the reason #34 gives: the published violation
    number is doing real work, and splitting what it reports must not become a
    way of lowering it.
    """
    a, b = prev.get("arrow_forms"), cur.get("arrow_forms")
    if not a or not b:
        return None
    if not any(a.values()) and not any(b.values()):
        return None
    parts = ", ".join("%s %d -> %d" % (label, a[k], b[k])
                      for k, label in (("chain", "chains of three or more"),
                                       ("mapping", "two-term mappings")))
    d_chain, d_map = b["chain"] - a["chain"], b["mapping"] - a["mapping"]
    tail = ""
    if d_chain * d_map < 0:
        worse = "mappings" if d_map > 0 else "chains"
        tail = ("; the two forms moved in OPPOSITE directions, which the "
                "violations_total headline hides - %s rose" % worse)
    return "arrow forms (disclosure, not a gate): %s%s" % (parts, tail)


def _counts(lac, judg, runs, cases=None, models=None):
    """The four count metrics and their exposure, over every case or a subset.

    cases=None is the whole round. A subset is what --target-cases scores a
    hypothesis on; the same function computes both so a scoped count can never
    be defined differently from the round-wide one it is disclosed beside.

    models narrows the same scope to one stratum. It exists because #96's
    composition table made the need obvious and there was no way to act on it:
    round 16's six-cell scope was 82% haiku by expected failures, so a real
    sonnet effect could not reach a threshold the pooled scope set. A hypothesis
    that expects one model to move must be able to say so before the round, and
    be held to it afterwards.
    """
    ok_case = (lambda c: True) if cases is None else (lambda c: c in cases)
    ok_model = (lambda m: True) if models is None else (lambda m: m in models)
    keep = ok_case
    return {
        "never_cut_failures": sum(v["never_cut_failures"]
                                  for k, v in lac.items()
                                  if keep(k[0]) and ok_model(k[2])),
        # Only a quality-graded case can lose a quality verdict. A
        # rule-adherence case grades the treatment against the text it was
        # handed, so counting its verdicts here would let the loop chase its
        # own tail.
        "quality_fails": _judge_fails(judg, "quality", keep, ok_model),
        # Safety is countable here for the reason evals/CRITERIA.md already
        # gives it: a safety verdict supports "a regression check on the
        # treatment arm", which is exactly and only what this comparison is.
        # What it may not support is a comparison *between* arms, because the
        # controls were never told to name a blast radius - and no arm
        # comparison happens in this function, which reads the laconic arm of
        # two rounds. Rule-adherence stays excluded on the harder objection:
        # its criteria are laconic's own prohibitions restated, so there is no
        # fixture behind them to be right or wrong about.
        "safety_fails": _judge_fails(judg, "safety", keep, ok_model),
        "violations_total": sum(v["violations_total"]
                                for k, v in lac.items()
                                if keep(k[0]) and ok_model(k[2])),
        # The same sum, kept per cell as the per-response counts behind it, so
        # the target can be scored by a test that resamples responses rather
        # than assuming one violation per run (#103).
        "violation_runs": {(k[0], k[2]): list(v.get("violation_runs") or [])
                           for k, v in lac.items()
                           if keep(k[0]) and ok_model(k[2])},
        # Responses that called no tool at all (#46). Counted only over cases
        # that have a fixture to open: four cases have no fixture/ directory
        # at all, so their responses are one-turn by construction and forced to
        # 100%, and ten non-design cases are read every time and sit at 0%.
        # Pooling those in makes a round-wide total look constant while the
        # informative part moves - the same predicate run.py:453 already uses
        # to decide whether to stage a fixture, so a case added later is
        # classified without a hand-maintained list going stale.
        #
        # Floor-pinned cases are deliberately NOT excluded. A cell that cannot
        # rise only dilutes; one that cannot fall hides.
        "one_turn": sum(v["one_turn"] for k, v in lac.items()
                        if keep(k[0]) and ok_model(k[2])
                        and (CASES / k[0] / "fixture").is_dir()),
        "one_turn_n_runs": sum(1 for r in runs if r["arm"] == "laconic"
                               and keep(r["case"]) and ok_model(r["model"])
                               and (CASES / r["case"] / "fixture").is_dir()),
        # The count gate's exposure: how many treatment responses this round
        # gave the metric a chance to fail in.
        "n_runs": sum(1 for r in runs if r["arm"] == "laconic"
                      and keep(r["case"]) and ok_model(r["model"])),
    }


def round_summary(snap, judg=None, prefs=None, target_cases=None,
                  target_models=None):
    """The numbers an accept decision needs, from one round's artefacts.

    target_cases adds a "scoped" block holding the same counts over those cases
    alone. It is an addition, never a replacement: the round-wide counts stay
    exactly as they were, because they are what the fatal conditions read and
    what the verdict discloses beside a scoped target.
    """
    lac = {k: v for k, v in aggregate(snap).items() if k[1] == "laconic"}
    runs = bench_run.usable(snap["runs"])
    seen = defaultdict(dict)
    for p in prefs or []:
        seen[(p["case"], p["model"], p["rep"])][p["order"]] = p["winner_arm"]
    # A comparison whose judge call failed carries winner_arm None. Counting
    # None != "baseline" as a position flip manufactures bias out of an API
    # error: round 09 lost its entire reversed-order pass and scored a 95%
    # flip rate from zero decided pairs (#55). Undecided pairs leave both
    # counters, and flip_undecided discloses how many did.
    paired = [v for v in seen.values() if 0 in v and 1 in v]
    both = [v for v in paired if v[0] is not None and v[1] is not None]
    flipped = [v for v in both if v[0] != v[1]]
    summary = dict(
        _counts(lac, judg, runs),
        tokens={(k[0], k[2]): v["output_tokens"] for k, v in lac.items()},
        tokens_stdev={(k[0], k[2]): v["output_tokens_stdev"]
                      for k, v in lac.items()},
        # Per-cell token lists split on whether the answer read anything, which
        # is what the target is scored on (#131). tokens above stays exactly as
        # it was: it is the marginal median the verdict discloses beside the
        # stratified one, and what a summary built before this carries.
        strata_tokens={(k[0], k[2]): v["tokens_by_stratum"]
                       for k, v in lac.items()},
        # The same cells' turn counts, for the action-scope target and the
        # gate that screens every round for a rise in it (#49).
        strata_turns={(k[0], k[2]): v["turns_by_stratum"]
                      for k, v in lac.items()},
        flip_rate=(len(flipped) / len(both)) if both else 0.0,
        flip_pairs=len(both),
        flip_undecided=len(paired) - len(both),
        # Per-cell composition of the four fatal counters, plus which cells
        # this round actually exercised. accept_verdict prints the
        # composition of any fatal loss (a scattered set of +1s reads very
        # differently from one cell at +4), and replication arbitration
        # (#52) needs to know a cell was sampled at all before an absent
        # failure may clear it.
        cells={
            "never_cut_failures": {(k[0], k[2]): v["never_cut_failures"]
                                   for k, v in lac.items()},
            "violations_total": {(k[0], k[2]): v["violations_total"]
                                 for k, v in lac.items()},
            "quality_fails": dict(_judge_fail_cells(judg, "quality")),
            "safety_fails": dict(_judge_fail_cells(judg, "safety")),
        },
        run_cells=set((r["case"], r["model"]) for r in runs
                      if r["arm"] == "laconic"),
        # Per-cell exposure. A measured-rate screen needs to know how many
        # chances to fail a cell actually had this round, not how many the
        # round was configured for.
        cell_runs=Counter((r["case"], r["model"]) for r in runs
                          if r["arm"] == "laconic"),
        judged_cells=set((j["case"], j["model"]) for j in (judg or [])
                         if j.get("arm") == "laconic"),
        # quality_fails split on one covariate, so a cancelling pair is
        # visible in the verdict instead of needing a separate analysis to
        # find. Disclosure only - see _quality_strata.
        quality_strata=_quality_strata(judg, runs),
        # Disclosure only - see metrics.arrow_forms and _arrow_form_line (#34).
        arrow_forms=_sum_forms(v.get("arrow_forms") or {} for v in lac.values()),
    )
    if target_cases:
        summary["scoped"] = dict(
            _counts(lac, judg, runs, set(target_cases),
                    set(target_models) if target_models else None),
            cases=sorted(set(target_cases)),
            models=sorted(set(target_models)) if target_models else None)
    return summary


def _stratum_of(prev_cell, cur_cell):
    """Which reading stratum a cell may be compared inside, or None (#131).

    An answer that opened a file is several times longer than one that did not,
    so a cell whose reading rate moved has a marginal median that mixes two
    populations in different proportions on the two sides. Comparing those
    medians credits an edit for suppressing reading. Every voting cell is
    therefore compared inside ONE stratum:

      both rounds have a grounded stratum   -> compare grounded medians
      neither round has one                 -> compare unread medians
      one round has one and the other does not -> the cell cannot vote

    The third case is the defect itself, and it is refused rather than
    approximated: there is nothing to compare a grounded median against.

    A case with no fixture has no file to open, so every one of its answers is
    unread by construction and it lands in the second branch, where its
    marginal median is its within-stratum median and nothing changes.
    """
    pg, cg = len(prev_cell["grounded"]), len(cur_cell["grounded"])
    if pg >= GROUNDED_MIN_RUNS and cg >= GROUNDED_MIN_RUNS:
        return "grounded"
    if pg < GROUNDED_MIN_RUNS and cg < GROUNDED_MIN_RUNS \
            and prev_cell["unread"] and cur_cell["unread"]:
        return "unread"
    return None


def _stratum_tokens(prev, cur):
    """Per-cell token medians, each compared inside one stratum (#131).

    Returns (prev_median, cur_median, prev_stdev, kinds, refused). The stdev is
    the same statistic the floor was always built from, taken from the stratum
    the cell votes in, so the floor gates the shift it is matched to.

    A summary carrying no strata block predates this and is scored on its
    marginal median, which is what every stored round was scored by.
    """
    p_strata, c_strata = prev.get("strata_tokens") or {}, cur.get("strata_tokens") or {}
    p_med, c_med, p_sd, kinds, refused = {}, {}, {}, {}, []
    for c in sorted(set(prev["tokens"]) & set(cur["tokens"])):
        a, b = p_strata.get(c), c_strata.get(c)
        if not a or not b:
            p_med[c], c_med[c] = prev["tokens"][c], cur["tokens"][c]
            p_sd[c] = (prev.get("tokens_stdev") or {}).get(c)
            kinds[c] = "unstratified"
            continue
        kind = _stratum_of(a, b)
        if kind is None:
            refused.append((c, len(a["grounded"]), len(a["grounded"]) + len(a["unread"]),
                            len(b["grounded"]), len(b["grounded"]) + len(b["unread"])))
            continue
        kinds[c] = kind
        p_med[c], c_med[c] = _median(a[kind]), _median(b[kind])
        p_sd[c] = statistics.stdev(a[kind]) if len(a[kind]) >= 2 else None
    return p_med, c_med, p_sd, kinds, refused


def _stratum_turns(prev, cur):
    """Per-cell grounded turn medians, and the baseline stdev that floors them.

    Returns (prev_median, cur_median, prev_stdev). Grounded only, and there is
    no fallback stratum: an unread answer has 0 or 1 turns by construction, so
    an unread turn median cannot move and a cell compared inside it would vote
    a guaranteed tie. Cells without a grounded stratum on both sides are
    absent rather than tied.

    That also keeps this metric off the axis #131 protects. Turns falling
    because answers stopped reading is the #46/#138 failure one_turn gates;
    inside the grounded stratum the only way down is doing less once the
    reading has already happened, which is what #49 reports.

    A summary carrying no turn block predates #49 and yields nothing, so a
    stored round is never screened on a gate it was not scored under.
    """
    p_strata, c_strata = prev.get("strata_turns") or {}, cur.get("strata_turns") or {}
    p_med, c_med, p_sd = {}, {}, {}
    for c in sorted(set(p_strata) & set(c_strata)):
        a, b = p_strata[c].get("grounded") or [], c_strata[c].get("grounded") or []
        if len(a) < GROUNDED_MIN_RUNS or len(b) < GROUNDED_MIN_RUNS:
            continue
        p_med[c], c_med[c] = _median(a), _median(b)
        p_sd[c] = statistics.stdev(a) if len(a) >= 2 else None
    return p_med, c_med, p_sd


def _turn_floor(p_sd, cells):
    """The floor a turn shift has to beat, measured rather than published.

    NOISE["stdev"] is 260 tokens and says nothing about turns, and inventing a
    turn constant would be tuning the gate to the rounds that exist. This is
    the median per-cell grounded stdev of the baseline - the same estimator
    the scoped token floor is built from, matched to the statistic it gates.
    """
    floors = [f for f in (p_sd.get(c) for c in cells) if f is not None]
    return _median(floors) if floors else None


def _stratum_note(kinds, refused):
    """The reason line naming where each cell voted, and which could not."""
    counts = Counter(kinds.values())
    # A round where every cell was refused still needs this line, and needs it
    # most: without it the verdict reads "no case/model cell is present in both
    # rounds", which blames the scope for what the reading rate did.
    if not counts and not refused:
        return ""
    if set(counts) == {"unstratified"} and not refused:
        return ""
    parts = ["%d %s" % (counts[k], k) for k in ("grounded", "unread", "unstratified")
             if counts.get(k)] or ["none"]
    note = ("output_tokens cells, by the stratum they were compared inside "
            "(#131): " + ", ".join(parts))
    if refused:
        note += ("; %d not voting because the reading rate crossed the floor: %s"
                 % (len(refused),
                    ", ".join("%s/%s %d of %d -> %d of %d" % (c[0], c[1], pg, pn, cg, cn)
                              for c, pg, pn, cg, cn in refused)))
    return note


def _weighted_median(pairs):
    """Lower weighted median of (value, weight) pairs."""
    pairs = sorted(p for p in pairs if p[1] > 0)
    if not pairs:
        return None
    half = sum(w for _, w in pairs) / 2
    seen = 0.0
    for v, w in pairs:
        seen += w
        if seen >= half:
            return v
    return pairs[-1][0]


def _counterfactual_line(prev, cur, cells):
    """The other two numbers a stratified target has to be read beside (#131).

    The counterfactual: what the marginal shift - the statistic the target used
    before this - reads with each cell's reading rate held at the baseline's.
    The gap between the two is the part of a token win that is mix rather than
    compression.

    The unread median: what the answers that never opened a file did. The
    target is scored inside the grounded stratum on any cell that has one, so
    without this line a round could compress only the answers that were already
    the cheap ones and the verdict would never mention it.

    Disclosure only, both of them. Returns None when neither can be built.
    """
    p_strata, c_strata = prev.get("strata_tokens") or {}, cur.get("strata_tokens") or {}
    if not cells or not p_strata or not c_strata:
        return None
    held = {}
    for c in cells:
        a, b = p_strata.get(c), c_strata.get(c)
        if not a or not b or not b["grounded"] or not b["unread"]:
            continue
        n = len(a["grounded"]) + len(a["unread"])
        if not n:
            continue
        rate = len(a["grounded"]) / n
        held[c] = _weighted_median(
            [(v, rate / len(b["grounded"])) for v in b["grounded"]]
            + [(v, (1 - rate) / len(b["unread"])) for v in b["unread"]])
    parts = []
    if held:
        # Both figures over the same cells - the ones a counterfactual can be
        # built for. Quoting the marginal shift over the whole scope beside a
        # counterfactual over part of it would attribute the difference between
        # two cell sets to the mix.
        base = _median([prev["tokens"][c] for c in held])
        parts.append("over the %d of %d cells with both strata, the marginal "
                     "shift is %.0f tokens and %.0f with each cell's reading "
                     "rate held at the baseline's"
                     % (len(held), len(cells),
                        base - _median([cur["tokens"][c] for c in held]),
                        base - _median([held[c] for c in held])))
    unread = [c for c in cells
              if (p_strata.get(c) or {}).get("unread")
              and (c_strata.get(c) or {}).get("unread")]
    if unread:
        parts.append("the unread stratum reads %.0f -> %.0f over %d of %d cells"
                     % (_median([_median(p_strata[c]["unread"]) for c in unread]),
                        _median([_median(c_strata[c]["unread"]) for c in unread]),
                        len(unread), len(cells)))
    if not parts:
        return None
    return "token mix (disclosure, not a gate): " + "; ".join(parts)


def accept_verdict(prev, cur, target, noise=None, target_cases=None,
                   arbitration=None, cell_rates=None, target_models=None):
    """(verdict, reasons) for one round against the round before it.

    arbitration, when given, is a round_summary over one fresh replication of
    disputed cells, generated at the same reps under the round's rules (#52).
    Any risen cell can be cleared by it, on two conditions: the cell must be
    present in the replication (generated, and for judge-verdict metrics
    judged), and its replicated count must be at or below the baseline's.
    Rounds 07 and 08 both died partly on four separate +1 flips in known
    lottery cells; a strict inequality on raw counts fires on those at any
    reps, so the screen stays strict and one replication arbitrates.

    Arbitration used to be refused above +1, on the theory that concentration
    is the signature of a real regression. Round 09 retired that theory (#56):
    it ran round 08's byte-identical rules text and put ordered-steps/haiku at
    +3 where round 08 had +1, two draws from one wide cell at Fisher p = 0.65,
    sorted onto opposite sides of the cutoff. Size of rise is not evidence of
    reality here; whether a replication reproduces it is. The cases the cutoff
    was written to protect are unaffected, because they reproduce: round 07's
    ordered-steps/haiku +4 replicated at 3 and 5 against a baseline 2, so it
    still rejects under this rule.

    Fatal conditions reject alone. For output_tokens the target has to beat the
    noise floor on both estimators - a sign test across the case/model cells and
    a median shift larger than the published stdev - because either one alone
    accepts moves the benchmark cannot distinguish from sampling. A scoped
    output_tokens target runs the same two tests over the named cases' cells
    alone, offered only from six cells up because a sweep of fewer cannot reach
    alpha, with the floor rebuilt the way NOISE's is from the scoped sonnet
    cells of the baseline. For a count target it has to clear an exact
    conditional binomial test at the same alpha.

    An unrecognized target rejects. Falling through to the fatal conditions
    alone would return "accept" for any round that merely failed to regress,
    which reads as a confirmed hypothesis and is not one.

    target_cases narrows the *target* to the cases a hypothesis named, and
    nothing else. The fatal conditions stay round-wide, so an edit that fixes
    the two cases it aimed at while breaking a third still rejects, and the
    round-wide value of the target is printed beside the scoped one. Round 03 is
    why this exists: it moved walkthrough and ordered-steps 21 arrows to 5 and
    the whole-round sum could only report 26 to 20 at p = 0.231.

    cell_rates, when given, screens a risen cell against that cell's failure
    rate measured under master rules before calling it a loss. It only ever
    covers cells that have such a rate at 30 runs or more; every other cell
    keeps the baseline-draw comparison unchanged, and every cell it does cover
    is named in the reason line. See _rate_covers.

    Preference is disclosed and never decisive: the judge that produces it
    favours the longer answer 63% of the time and laconic is the short arm, so
    it may not reject an edit that passed every deterministic gate.
    """
    noise = noise or NOISE
    reasons = []
    fatal = False
    for key, label in FATAL:
        if cur[key] <= prev[key]:
            continue
        # violations_total is a clustered count, and until #103 this branch was
        # a bare integer comparison over a statistic whose bootstrap sd at n=10
        # per cell is about 16. Under a null edit the round-wide total rises
        # about half the time, so any rise rejecting made this the one fatal
        # counter that could reject a round for nothing. It never has, because
        # every edit the loop has tried moved violations down by 20 to 107 -
        # margins far outside that noise - but a scoped edit has no such margin.
        #
        # Disclosed rather than dropped: a rise inside the noise prints, with
        # its p, and does not reject. A rise the bootstrap can distinguish is
        # fatal exactly as before.
        if key == "violations_total":
            p_rise = _cluster_count_p(cur.get("violation_runs") or {},
                                      prev.get("violation_runs") or {})
            if p_rise is not None and p_rise > noise["alpha"]:
                reasons.append(
                    "%s rise (%d -> %d) is inside the sampling noise of a "
                    "clustered count, p = %.3f (#103)"
                    % (label, prev[key], cur[key], p_rise))
                continue
        prev_cells = (prev.get("cells") or {}).get(key)
        cur_cells = (cur.get("cells") or {}).get(key)
        risen = []
        if prev_cells is not None and cur_cells is not None:
            risen = sorted(c for c in set(prev_cells) | set(cur_cells)
                           if cur_cells.get(c, 0) > prev_cells.get(c, 0))
        # A cell with a rate measured under master rules is screened against
        # that rate before it is called a loss, and every screened-out cell is
        # named. Silently dropping a cell from a fatal counter would be the
        # worst version of this change.
        covered_by_rate = []
        cur_runs = (cur.get("cell_runs") or {})
        prev_runs = (prev.get("cell_runs") or {})
        if risen and cell_rates:
            rates = cell_rates.get(key) or {}
            covered_by_rate = [
                c for c in risen
                if _rate_covers(rates.get(c), cur_cells.get(c, 0),
                                cur_runs.get(c, 0), noise["alpha"])]
            risen = [c for c in risen if c not in covered_by_rate]
        # Where both sides have enough runs to estimate a rate, the rise is
        # tested rather than counted (#133). Below CELL_TEST_MIN_RUNS on either
        # side this covers nothing and the cell keeps the count comparison.
        covered_by_sample = [
            c for c in risen
            if _sample_covers(cur_cells.get(c, 0), cur_runs.get(c, 0),
                              prev_cells.get(c, 0), prev_runs.get(c, 0),
                              noise["alpha"])]
        risen = [c for c in risen if c not in covered_by_sample]
        comp = ""
        if risen:
            comp = "; cells: " + ", ".join(
                "%s/%s +%d" % (c[0], c[1],
                               cur_cells.get(c, 0) - prev_cells.get(c, 0))
                for c in risen)
        if covered_by_rate:
            comp += ("; within the measured master-rules rate: " + ", ".join(
                "%s/%s %d of %d against %.0f%%"
                % (c[0], c[1], cur_cells.get(c, 0),
                   (cur.get("cell_runs") or {}).get(c, 0),
                   100.0 * (cell_rates[key][c]["failures"]
                            / cell_rates[key][c]["runs"]))
                for c in covered_by_rate))
        if covered_by_sample:
            comp += ("; inside the round's own sampling: " + ", ".join(
                "%s/%s %d of %d against %d of %d, p = %.3f"
                % (c[0], c[1], cur_cells.get(c, 0), cur_runs.get(c, 0),
                   prev_cells.get(c, 0), prev_runs.get(c, 0),
                   _fisher_upper_tail(cur_cells.get(c, 0), cur_runs.get(c, 0),
                                      prev_cells.get(c, 0), prev_runs.get(c, 0)))
                for c in covered_by_sample))
        if not risen and (covered_by_rate or covered_by_sample):
            # The measured-rate wording is kept when that screen did the work
            # alone, so a round scored before #133 reads the same afterwards.
            how = ("within the measured rate" if not covered_by_sample
                   else "inside sampling")
            reasons.append("%s rise (%d -> %d) is %s%s"
                           % (label, prev[key], cur[key], how, comp))
            continue
        if risen and arbitration:
            covered = (arbitration.get("run_cells")
                       if key in ("never_cut_failures", "violations_total")
                       else arbitration.get("judged_cells")) or set()
            arb_cells = (arbitration.get("cells") or {}).get(key, {})
            arb_runs = (arbitration.get("cell_runs") or {})
            # At or below the control's count clears, as it always has. A
            # replication that is nominally higher but inside sampling also
            # clears now, because "0 in the control" is otherwise unclearable
            # however many runs the replication has (#133).
            cleared = [c for c in risen
                       if c in covered
                       and (arb_cells.get(c, 0) <= prev_cells.get(c, 0)
                            or _sample_covers(arb_cells.get(c, 0),
                                              arb_runs.get(c, 0),
                                              prev_cells.get(c, 0),
                                              prev_runs.get(c, 0),
                                              noise["alpha"]))]
            blocked = [c for c in risen if c not in cleared]
            if not blocked:
                reasons.append("%s rise (%d -> %d) cleared by replication: "
                               "%s did not reproduce" %
                               (label, prev[key], cur[key],
                                ", ".join("%s/%s" % c for c in cleared)))
                continue
            if cleared:
                comp += ("; replication cleared %s, did not clear %s"
                         % (", ".join("%s/%s" % c for c in cleared),
                            ", ".join("%s/%s" % c for c in blocked)))
            else:
                comp += ("; replication did not clear %s"
                         % ", ".join("%s/%s" % c for c in blocked))
        elif risen:
            comp += (" (arbitrable - replicate the risen cells at the same "
                     "reps; see the loop skill)")
        reasons.append("REJECT: %s lost (%d -> %d)%s"
                       % (label, prev[key], cur[key], comp))
        fatal = True

    # The fifth fatal condition, and the only one that is not a count (#49).
    # Laconic bounds prose and nothing else, so an edit can buy shorter answers
    # by doing more work - #49 reports a one-line factual question that spent
    # four tool calls and a file edit. Prose gates cannot see that trade,
    # because the prose it produced was short enough to pass every one of them.
    #
    # One direction only. Falling is what the target direction is for and never
    # rejects; rising past the baseline's own dispersion is the trade, and it
    # rejects whatever the round named. That is what FATAL holds - harm
    # counters - and it is why one_turn is not in it: not opening a file is not
    # harm, but spending the user's tokens on work they did not ask for is.
    t_prev, t_cur, t_sd = _stratum_turns(prev, cur)
    turn_cells = sorted(set(t_prev) & set(t_cur))
    if turn_cells:
        t_floor = _turn_floor(t_sd, turn_cells)
        rise = (_median([t_cur[c] for c in turn_cells])
                - _median([t_prev[c] for c in turn_cells]))
        risen_cells = sorted(c for c in turn_cells if t_cur[c] > t_prev[c])
        # Two estimators, the same pair the token target needs, and for a
        # sharper reason here. num_turns is a small integer, so a cell whose
        # grounded runs all took the same number of turns has stdev 0 and the
        # median-of-stdevs floor collapses to 0.0 - at which point any rise at
        # all clears it. Re-scoring the archive under a floor alone rejected
        # rounds 07, 08 and 10 on destructive/sonnet 3.0 -> 4.0, one risen cell
        # of eighteen: with half the cells either side of the round-wide
        # median, moving one across it shifts that median by half a turn while
        # nothing else moves. A gate that fires on that is not stricter, it is
        # broken, which is the same failure CELL_TEST_MIN_RUNS documents.
        #
        # So a rise must be BROAD as well as larger than the floor. sign_test
        # is two-sided, hence the majority guard: 1 of 10 reaches alpha in the
        # falling direction and must not be read as a rise.
        p_rise = metrics.sign_test(len(risen_cells), len(turn_cells))
        broad = (len(risen_cells) * 2 > len(turn_cells)
                 and p_rise < noise["alpha"])
        spread = "%d of %d cell(s)" % (len(risen_cells), len(turn_cells))
        where = ("; risen on " + ", ".join("%s/%s %.1f -> %.1f"
                                           % (c[0], c[1], t_prev[c], t_cur[c])
                                           for c in risen_cells)
                 if risen_cells else "")
        if broad and t_floor is not None and rise > t_floor:
            reasons.append(
                "REJECT: action scope lost - grounded turns rose %.1f across "
                "%s, sign test p = %.3f, past the %.1f-turn floor measured "
                "from the baseline's own dispersion (#49 turn gate)%s"
                % (rise, spread, p_rise, t_floor, where))
            fatal = True
        else:
            # Disclosed on every round it screens, passing or not: the gate
            # changes what a verdict means, and rounds 01 to 26 were not
            # scored under it. A verdict that does not say so cannot be
            # compared with one that was.
            reasons.append(
                "#49 turn gate: grounded turns moved %+.1f over %s, %s rising, "
                "against a %s-turn floor - held"
                % (rise, "%d cell(s)" % len(turn_cells), spread,
                   "%.1f" % t_floor if t_floor is not None else "unbuildable"))

    if target_cases and not (prev.get("scoped") and cur.get("scoped")):
        # Scoring a scoped hypothesis against round-wide counts would silently
        # answer a different question than the one the hypothesis asked.
        reasons.append("REJECT: --target-cases needs both rounds summarized with "
                       "the same scope")
        return "reject", reasons

    # Both token branches score the stratified medians, never the marginal ones
    # (#131). p_tok and c_tok hold one median per cell, taken from the stratum
    # that cell may be compared inside; a cell whose reading rate crossed
    # between the two rounds is absent from both and named in strata_note.
    if target == "output_tokens":
        p_tok, c_tok, p_sd, kinds, refused = _stratum_tokens(prev, cur)
        # Scoped to the cases the target names, because that is the set the
        # verdict line above is about. Not scoped by model: the scoped token
        # branch does not filter on --target-models either, and a note that
        # narrowed further than the test would describe a different set.
        wanted_cases = set(target_cases or [])
        in_scope = (lambda c: not wanted_cases or c[0] in wanted_cases)
        strata_note = _stratum_note(
            {c: k for c, k in kinds.items() if in_scope(c)},
            [r for r in refused if in_scope(r[0])])

    if target_cases and target == "output_tokens":
        # sign_test is two-sided exact, so a sweep of n cells is p = 2 * 0.5**n:
        # four cells is 0.125, five is 0.0625, and no scope under six cells can
        # reach alpha = 0.05 however large the move is. Six is the boundary the
        # old blanket refusal was standing in for. The floor is the median
        # per-cell stdev over ALL the scoped cells of the baseline - the same
        # cells whose medians produce the shift it gates. It was sonnet-only
        # until #51: rounds 07 and 08 measured the same edit at 711 then 504
        # around a 575 sonnet-built floor, because the shift median was
        # dragged toward the small haiku cells while the floor never heard of
        # them. Matching the estimator to the statistic ended that. A scoped
        # cell with no baseline stdev leaves the floor unbuildable and the
        # scope is refused rather than handed a partial one.
        wanted = set(target_cases)
        cells = sorted(c for c in set(p_tok) & set(c_tok) if c[0] in wanted)
        # A cell whose baseline answer is already short cannot express this
        # target's effect, so it votes noise into a test that counts votes.
        # See TOKEN_CELL_MIN_BASELINE and evals/results/loop/token-scope.md.
        #
        # All or nothing, and only when the scope can afford it. Dropping is
        # an improvement a large scope can buy, never a way to shrink a small
        # one into unusability: if removing the short cells would leave fewer
        # than six, none are removed and the scope is scored exactly as it was
        # before this existed. That keeps every stored round's verdict intact -
        # rounds 07 to 14 named three design cases, so dropping two would leave
        # four and turn round 10's accept into a refusal for want of data it
        # never had. Partial dropping is not offered: choosing which short cell
        # to keep would be choosing the answer.
        short = sorted(c for c in cells
                       if p_tok[c] < TOKEN_CELL_MIN_BASELINE)
        if short and len(cells) - len(short) >= 6:
            cells = [c for c in cells if c not in set(short)]
            dropped = ("; %d cell(s) below the %d-token floor and not voting: %s"
                       % (len(short), TOKEN_CELL_MIN_BASELINE,
                          ", ".join("%s/%s %d" % (c[0], c[1], p_tok[c])
                                    for c in short)))
        elif short:
            dropped = ("; %d cell(s) are below the %d-token floor and voted "
                       "anyway: dropping them would leave %d cells, under the "
                       "six a sign test needs to reach alpha. Name more cases "
                       "in the scope" % (len(short), TOKEN_CELL_MIN_BASELINE,
                                         len(cells) - len(short)))
        else:
            dropped = ""
        floors = [f for f in (p_sd.get(c) for c in cells) if f is not None]
        if len(cells) < 6:
            p_all = metrics.sign_test(len(cells), len(cells)) if cells else 1.0
            reasons.append("REJECT: scoped output_tokens needs at least 6 "
                           "case/model cells to reach alpha; %d cells sweep at "
                           "p = %.3f%s" % (len(cells), p_all, dropped))
            fatal = True
        elif len(floors) < len(cells):
            reasons.append("REJECT: scoped output_tokens has no baseline stdev "
                           "for %d of %d scoped cells, so the scoped noise "
                           "floor cannot be built the way NOISE's %d is"
                           % (len(cells) - len(floors), len(cells),
                              noise["stdev"]))
            fatal = True
        else:
            floor = _median(floors)
            improved = sum(1 for c in cells if c_tok[c] < p_tok[c])
            p = metrics.sign_test(improved, len(cells))
            shift = (_median([p_tok[c] for c in cells])
                     - _median([c_tok[c] for c in cells]))
            wide_cells = sorted(set(p_tok) & set(c_tok))
            wide_improved = sum(1 for c in wide_cells if c_tok[c] < p_tok[c])
            wide_p = (metrics.sign_test(wide_improved, len(wide_cells))
                      if wide_cells else 1.0)
            where = " on %s" % ", ".join(sorted(wanted))
            wide = (" (round-wide %d of %d cells, p = %.3f)"
                    % (wide_improved, len(wide_cells), wide_p)) + dropped
            if improved * 2 <= len(cells) or p >= noise["alpha"]:
                reasons.append("REJECT: %d of %d cells improved%s, sign test "
                               "p = %.3f%s"
                               % (improved, len(cells), where, p, wide))
                fatal = True
            elif shift <= floor:
                reasons.append("REJECT: median shift %.0f%s is inside the "
                               "%.1f-token scoped noise floor%s"
                               % (shift, where, floor, wide))
                fatal = True
            else:
                reasons.append("median shift %.0f tokens%s, %d of %d cells "
                               "improved, p = %.3f, scoped floor %.1f%s"
                               % (shift, where, improved, len(cells), p,
                                  floor, wide))
    elif target == "output_tokens":
        cells = sorted(set(p_tok) & set(c_tok))
        improved = sum(1 for c in cells if c_tok[c] < p_tok[c])
        p = metrics.sign_test(improved, len(cells)) if cells else 1.0
        shift = (_median([p_tok[c] for c in cells])
                 - _median([c_tok[c] for c in cells])) if cells else 0
        if not cells:
            reasons.append("REJECT: no case/model cell is present in both rounds")
            fatal = True
        elif improved * 2 <= len(cells) or p >= noise["alpha"]:
            reasons.append("REJECT: %d of %d cells improved, sign test p = %.3f"
                           % (improved, len(cells), p))
            fatal = True
        elif shift <= noise["stdev"]:
            reasons.append("REJECT: median shift %.0f is inside the %d-token noise floor"
                           % (shift, noise["stdev"]))
            fatal = True
        else:
            reasons.append("median shift %.0f tokens, %d of %d cells improved, p = %.3f"
                           % (shift, improved, len(cells), p))
    elif target == "turns":
        # A hypothesis may aim at action scope directly, not only be screened
        # for it. Same two estimators the token target uses - a sign test
        # across cells and a shift larger than the floor - because grounded
        # turns are a distribution with real spread (2 to 10 across rounds 24
        # to 26), not a count of rare events.
        #
        # The floor is measured, never published: NOISE["stdev"] is 260 tokens
        # and a turn constant would be tuned to the rounds that exist.
        cells = sorted(c for c in turn_cells
                       if not target_cases or c[0] in set(target_cases))
        t_floor = _turn_floor(t_sd, cells)
        if not cells:
            reasons.append("REJECT: no case/model cell has a grounded stratum "
                           "in both rounds, and an unread answer is 0 or 1 "
                           "turns by construction, so there is nothing this "
                           "target can measure")
            fatal = True
        elif t_floor is None:
            reasons.append("REJECT: no baseline grounded stdev over %d cell(s), "
                           "so the turn floor cannot be measured" % len(cells))
            fatal = True
        else:
            improved = sum(1 for c in cells if t_cur[c] < t_prev[c])
            p_turn = metrics.sign_test(improved, len(cells))
            shift = (_median([t_prev[c] for c in cells])
                     - _median([t_cur[c] for c in cells]))
            where = (" on %s" % ", ".join(sorted(set(target_cases)))
                     if target_cases else "")
            if improved * 2 <= len(cells) or p_turn >= noise["alpha"]:
                reasons.append("REJECT: %d of %d cells improved%s, sign test "
                               "p = %.3f" % (improved, len(cells), where, p_turn))
                fatal = True
            elif shift <= t_floor:
                reasons.append("REJECT: median shift %.1f turns%s is inside the "
                               "%.1f-turn measured noise floor"
                               % (shift, where, t_floor))
                fatal = True
            else:
                reasons.append("median shift %.1f turns%s, %d of %d cells "
                               "improved, p = %.3f, measured floor %.1f"
                               % (shift, where, improved, len(cells), p_turn,
                                  t_floor))
    elif target in COUNT_TARGETS:
        src_prev = prev["scoped"] if target_cases else prev
        src_cur = cur["scoped"] if target_cases else cur
        a, b = src_prev[target], src_cur[target]
        # The round-wide numbers ride along on every scoped line. A scoped
        # target that fell while the round rose is a real thing to know, and a
        # verdict that printed only the scope would hide it.
        where = (" on %s" % ", ".join(src_cur["cases"])) if target_cases else ""
        if target_models:
            where += " (%s only)" % ", ".join(sorted(set(target_models)))
        wide = ((" (round-wide %d -> %d)" % (prev[target], cur[target]))
                if target_cases else "")
        # Score against the measured rates when the scope is fully measured,
        # and against the previous round's draw otherwise (#96). The fallback
        # is what every stored round was scored by, so none of them move.
        scope_cells = sorted(
            c for c in (cur.get("cell_runs") or {})
            if (not target_cases or c[0] in set(target_cases))
            and (not target_models or c[1] in set(target_models)))
        rates = (cell_rates or {}).get(target) or {}
        p_rate = _rate_count_p(rates, scope_cells, b,
                               src_cur.get("n_runs", 0))
        if p_rate is not None:
            p = p_rate
            measured = sum(rates[c]["failures"] for c in scope_cells)
            m_runs = sum(rates[c]["runs"] for c in scope_cells)
            wide += ("; scored against the measured rate %d of %d, not the "
                     "baseline draw" % (measured, m_runs))
            comp = _scope_composition(rates, scope_cells, cur["cell_runs"])
            if comp:
                reasons.append(
                    "%s scope composition: %s" % (target, ", ".join(
                        "%s/%s %.0f%% (%.1f of %.1f expected)"
                        % (c[0], c[1], 100 * r, e, sum(x[2] for x in comp))
                        for c, r, e in comp)))
        else:
            p = _count_p(a, b, _exposure(src_prev, target),
                         _exposure(src_cur, target))
        # violations_total overrides both of the above (#103). Its events are
        # not one per run, so neither the binomial split against the previous
        # round nor the one against a measured rate is the right null - both
        # assume a variance three times too small. The bootstrap is scoped the
        # same way the count is, and the binomial number prints beside it so a
        # stored round stays readable against the way it was scored.
        if target == "violations_total":
            scope = set(scope_cells)
            p_cluster = _cluster_count_p(
                {c: v for c, v in (src_prev.get("violation_runs") or {}).items()
                 if c in scope},
                {c: v for c, v in (src_cur.get("violation_runs") or {}).items()
                 if c in scope})
            if p_cluster is not None:
                wide += ("; bootstrapped over responses, not runs (#103; the "
                         "binomial reads %s)"
                         % ("%.3f" % p if p is not None else "nothing"))
                p = p_cluster
        # one_turn overrides too, for a different reason (#46). Its events are
        # one per run, so #103's within-round resample is the wrong correction -
        # it would return essentially the binomial number. The extra variance is
        # between rounds, so the standard error is scaled instead. A round that
        # generated both sides in one interleaved batch has removed that
        # variance by design and may cite the binomial figure printed here.
        if target == "one_turn":
            e_prev, e_cur = _exposure(src_prev, target), _exposure(src_cur, target)
            p_inf = _inflated_count_p(a, b, e_prev, e_cur, ONE_TURN_PHI)
            if p_inf is not None:
                # The reference figure is the SAME test at phi = 1, not
                # _count_p. _count_p is an exact conditional binomial split and
                # this is a normal approximation on a difference of
                # proportions; they are not nested, so quoting one against the
                # other would attribute their disagreement to phi when part of
                # it is the change of test. At phi = 1 the only difference is
                # the inflation, which is what the disclosure is for.
                p_flat = _inflated_count_p(a, b, e_prev, e_cur, 1.0)
                wide += ("; variance inflated by phi = %.2f for between-round "
                         "drift (#46; the same test uninflated reads %s)"
                         % (ONE_TURN_PHI,
                            "%.3f" % p_flat if p_flat is not None else "nothing"))
                p = p_inf
        if p is None:
            reasons.append("REJECT: %s was already 0%s before the edit, so this "
                           "round cannot show it falling%s" % (target, where, wide))
            fatal = True
        elif p >= noise["alpha"]:
            reasons.append("REJECT: %s %d -> %d%s, p = %.3f%s"
                           % (target, a, b, where, p, wide))
            fatal = True
        else:
            reasons.append("%s %d -> %d%s, p = %.3f%s" % (target, a, b, where, p, wide))
    else:
        reasons.append("REJECT: unknown target %r (expected output_tokens, "
                       "turns, or one of %s)" % (target, ", ".join(COUNT_TARGETS)))
        fatal = True

    # Where the token target's cells voted, and what the number it replaced
    # reads. Both print whatever the target did: a passing round needs the mix
    # figure as much as a failing one, because the question they answer is how
    # much of the compression is compression (#131).
    if target == "output_tokens":
        if strata_note:
            reasons.append(strata_note)
        # cells is whichever set the branch above actually scored: the scoped
        # voting set, or every shared cell round-wide.
        counter = _counterfactual_line(prev, cur, cells)
        if counter:
            reasons.append(counter)

    # A round with no decided both-order pair has no position-bias control at
    # all, and its flip_rate is 0.0 for want of a denominator rather than
    # because the judge was consistent. That reads as the most citable round
    # possible, so unmeasured is called out before the ceiling is (#55).
    if cur.get("flip_pairs") == 0 and cur.get("flip_undecided"):
        reasons.append("preference not citable: no both-order pair was decided "
                       "(%d undecided), so the flip rate is unmeasured"
                       % cur["flip_undecided"])
    elif cur["flip_rate"] >= noise["flip_rate_max"]:
        undecided = (" (%d pair(s) undecided and excluded)" % cur["flip_undecided"]
                     if cur.get("flip_undecided") else "")
        reasons.append("preference not citable: flip rate %.0f%% is at or above the "
                       "%.0f%% ceiling%s"
                       % (100 * cur["flip_rate"], 100 * noise["flip_rate_max"],
                          undecided))
    elif cur.get("flip_undecided"):
        reasons.append("preference: %d both-order pair(s) undecided and excluded "
                       "from the %.0f%% flip rate; re-run prefer.py to fill them"
                       % (cur["flip_undecided"], 100 * cur["flip_rate"]))

    # Last, and never fatal. A flat quality count is exactly when the
    # cancellation hides, so the line prints whether the round passed or
    # failed and whatever the counter did.
    forms = _arrow_form_line(prev, cur)
    if forms:
        reasons.append(forms)
    strata = _strata_line(prev, cur)
    if strata:
        reasons.append(strata)
    return ("reject" if fatal else "accept"), reasons


def aggregate(snap):
    buckets = defaultdict(list)
    for r in bench_run.usable(snap["runs"]):
        buckets[(r["case"], r["arm"], r["model"])].append(r)

    agg = {}
    for key, runs in buckets.items():
        case = key[0]
        expect_path = CASES / case / "expect.json"
        never_cut = json.loads(expect_path.read_text())["never_cut"] \
            if expect_path.exists() else []
        scored = [metrics.score(r.get("text", "")) for r in runs]
        tokens = [r.get("output_tokens", 0) for r in runs]
        agg[key] = {
            "n": len(runs),
            "output_tokens": _median(tokens),
            # The same tokens, kept split on whether the answer opened a file
            # (#131). An unread answer is several times shorter than a grounded
            # one, so the marginal median above moves when the mix moves and
            # the target cannot tell that from compression. accept_verdict
            # takes each cell's median from one of these two lists.
            # The two lists partition the cell: one_turn above counts exactly
            # one turn, but a record carrying none at all called no tool
            # either, and a run that fell into neither list would leave the
            # cell looking like a reading collapse it never had.
            "tokens_by_stratum": {
                "grounded": [r.get("output_tokens", 0) for r in runs
                             if r.get("num_turns", 0) > 1],
                "unread": [r.get("output_tokens", 0) for r in runs
                           if r.get("num_turns", 0) <= 1],
            },
            # The turns themselves, partitioned by the same predicate (#49).
            # Laconic bounds prose, so an edit can cut words and relocate the
            # excess into tool calls; num_turns is the action proxy every
            # stored round carries, and it reports how many agentic turns a
            # response took and nothing about which tools ran. Rounds
            # generated since #142 also carry a tool list, and nothing here
            # reads it: absent on every round below 27, it has no measured
            # null to be gated against.
            "turns_by_stratum": {
                "grounded": [r.get("num_turns", 0) for r in runs
                             if r.get("num_turns", 0) > 1],
                "unread": [r.get("num_turns", 0) for r in runs
                           if r.get("num_turns", 0) <= 1],
            },
            "output_tokens_min": min(tokens) if tokens else 0,
            "output_tokens_max": max(tokens) if tokens else 0,
            "output_tokens_stdev": statistics.stdev(tokens) if len(tokens) >= 2 else 0.0,
            "cost": _median([r.get("total_cost_usd", 0.0) for r in runs], 0.0),
            "duration_ms": _median([r.get("duration_ms", 0) for r in runs]),
            "violations": _median([s["violations"] for s in scored]),
            # The gate must see every violation, not the typical response -
            # two of five responses with 10 violations each leaves the
            # median at 0 while the total (and the flagged-response count)
            # correctly show a regression. Median stays for the display
            # table; these two are what gate_failures() checks.
            "violations_total": sum(s["violations"] for s in scored),
            # Kept, not just summed (#103). violations_total is the one count
            # target whose events are not one-per-run: a response that reaches
            # for an arrow reaches for several, so the per-response counts have
            # a variance three times their mean and the binomial test the other
            # counters use is optimistic. _cluster_count_p resamples these
            # whole, which is what respects the clustering.
            "violation_runs": [s["violations"] for s in scored],
            # Disclosure only (#34). Summed into nothing; chain + mapping always
            # equals this cell's symbol_connectors.
            "arrow_forms": _sum_forms(metrics.arrow_forms(r.get("text", ""))
                                      for r in runs),
            "violations_flagged_responses": sum(1 for s in scored if s["violations"] > 0),
            "article_rate": _median([s["article_rate"] for s in scored], 0.0),
            "aux_verb_rate": _median([s["aux_verb_rate"] for s in scored], 0.0),
            # Absolute article/auxiliary word counts, per response then
            # medianed - what the rate-floor gate actually checks against.
            "article_count": _median([s["words"] * s["article_rate"] for s in scored], 0.0),
            "aux_count": _median([s["words"] * s["aux_verb_rate"] for s in scored], 0.0),
            # Cases with an empty never_cut list are not verified by this
            # check at all - a "0 failures" reading must not be mistaken for
            # "checked and clean".
            "never_cut_checked": len(never_cut) > 0,
            "never_cut_failures": sum(
                1 for r in runs
                if metrics.never_cut_missing(r.get("text", ""), never_cut)
            ),
            # A response the model produced without calling a single tool, so
            # it never opened a file (#46). On sonnet this is a clean proxy:
            # cache_read_input_tokens is bimodal with no overlap, and 0 of 41
            # one-turn design responses name any fixture file against 151 of
            # 159 multi-turn ones. On haiku it leaks - the fixtures are small
            # enough that reading barely moves the token counts, and 8 of 183
            # one-turn haiku runs quote fixture-only content - which is why
            # the target below requires a model scope.
            "one_turn": sum(1 for r in runs if r.get("num_turns") == 1),
            "spans": [sp for s in scored for sp in s["spans"]][:5],
        }
    return agg


def _comparable(base, rate_key, count_key):
    """Did the baseline write enough article/auxiliary words for a ratio
    against it to carry information? Below these floors the bucket is
    evidence of nothing, in either direction - it neither fires the gate nor
    counts as a model that corroborated a pass."""
    return base[count_key] >= ABS_COUNT_FLOOR and base[rate_key] >= RATE_FLOOR


def _rate_gate(agg, threshold, rate_key, count_key, label):
    """Article and auxiliary-verb rates are density proxies, not observations.
    A response can be flawless English and still land under the threshold
    because its noun phrases take possessives, quantifiers and demonstratives
    rather than articles ("Any query callback that throws was leaking its
    client" is 38 words with zero articles and nothing wrong with it).

    Measured on the committed snapshot, one half of baseline's own reps fires
    this gate against baseline's other half in 11 of 160 splits (~7%), so at
    n=5 a single bucket dropping is indistinguishable from sampling noise -
    the gate fired twice on laconic and twice on word-compression, two arms
    whose responses both keep their articles.

    Requiring the drop to reproduce on every model tested costs no
    sensitivity: with the articles mechanically stripped out of laconic's own
    responses, every case is still accounted for - caught by the gate, or
    reported as ungated rather than passed. A rules regression is a property
    of the rules and shows up on both models; noise does not correlate across
    them. Directly observed defects (an arrow in prose, a dropped never-cut
    token) are not proxies and are gated on any single occurrence, above.

    Returns (failures, notes). A note is a case the gate could not evaluate,
    reported rather than silently counted as a pass; it does not fail a run.
    """
    failures, notes = [], []
    by_case = defaultdict(list)
    cases = set()
    for (case, arm, model), v in agg.items():
        if arm != "laconic":
            continue
        # Tracked separately from by_case: a snapshot with no baseline arm at
        # all (a targeted re-run of one case, say) puts nothing in by_case, so
        # iterating by_case alone would report neither a failure nor a note and
        # leave "All gates pass" claiming rates within 70% of a baseline that
        # was never sampled - the exact "unevaluated check read as a passing
        # one" this notes list exists to prevent.
        cases.add(case)
        base = agg.get((case, "baseline", model))
        if base and _comparable(base, rate_key, count_key):
            by_case[case].append((model, v[rate_key], base[rate_key]))

    for case in sorted(cases):
        entries = by_case[case]
        # One model cannot corroborate itself, and no model cannot either.
        if len(entries) < 2:
            who = ("only %s" % entries[0][0]) if entries else "no model"
            notes.append("%s: %s rate not gated - %s had a comparable "
                         "baseline, so a drop cannot be corroborated"
                         % (case, label, who))
            continue
        if not all(rate < threshold * brate for _, rate, brate in entries):
            continue
        detail = ", ".join("%s %.3f vs %.3f" % e for e in sorted(entries))
        failures.append("%s: %s rate below %.0f%% of baseline on all %d models (%s)"
                        % (case, label, threshold * 100, len(entries), detail))
    return failures, notes


RATE_GATES = (("article_rate", "article_count", "article"),
              ("aux_verb_rate", "aux_count", "aux verb"))


def gate_failures(agg, threshold):
    out = []
    for (case, arm, model), v in sorted(agg.items()):
        if arm != "laconic":
            continue
        if v["violations_total"] > 0:
            # Lead with the number the gate actually used (the total), not
            # the median - "0.0 readability violation(s)" reporting a
            # failure reads as self-contradictory. spans are pooled across
            # the bucket and truncated to 5, so label them as a sample: the
            # list length is unrelated to violations_total.
            out.append("%s/%s: %d readability violation(s) across %d response(s) "
                       "(median %.1f) sample: %s"
                       % (case, model, v["violations_total"], v["n"], v["violations"],
                          v["spans"]))
        if v["never_cut_failures"] > 0:
            out.append("%s/%s: %d never-cut failure(s)"
                       % (case, model, v["never_cut_failures"]))
    for args in RATE_GATES:
        out += _rate_gate(agg, threshold, *args)[0]
    return out


def gate_notes(agg, threshold):
    """Checks that could not be evaluated. Reported, never counted as passes,
    never failing the run."""
    out = []
    for args in RATE_GATES:
        out += _rate_gate(agg, threshold, *args)[1]
    return out


def _arms_present(agg):
    return [a for a in ARM_ORDER if any(k[1] == a for k in agg)]


def _models_present(agg):
    return sorted(set(k[2] for k in agg))


def _by_arm_model(agg, field, arms, models, fmt="%s", agg_fn=_median):
    """agg_fn combines the per-case values for one arm/model into one cell.
    Defaults to the median (what every display table wants). A table
    labeled "total" must pass agg_fn=sum instead - a median-of-per-case-
    totals is not a total, and rendering one under a "total" heading next
    to a gate that fires on the real sum is a published self-contradiction.
    """
    rows = ["| arm | " + " | ".join(models) + " |",
            "|---|" + "|".join("--:" for _ in models) + "|"]
    for arm in arms:
        cells = []
        for m in models:
            vals = [v[field] for k, v in agg.items() if k[1] == arm and k[2] == m]
            cells.append(fmt % agg_fn(vals) if vals else "-")
        rows.append("| %s | %s |" % (arm, " | ".join(cells)))
    return "\n".join(rows)


def _usage_of(rec, nested):
    """One record's usage fields, or None if it carries none.

    Runs store them flat (run.py writes parse_cli_json's output straight onto
    the record); judgments and comparisons store them under "usage" (#68).
    A record from before that fix, or from a call that failed, has neither -
    and None keeps it out of the priced count rather than totalling it as a
    free call.
    """
    u = rec.get("usage") if nested else rec
    if not isinstance(u, dict):
        return None
    got = {k: u[k] for k in bench_judge.USAGE_FIELDS if k in u}
    return got or None


def cost_summary(snap, judgments=(), comparisons=()):
    """Per-stage token and dollar totals for one round.

    Generation was always priced and the two grading stages were not, which
    made the round's headline cost the smaller half of the bill: a 340-run
    round issues 340 generation calls, 340 judge calls and 700 preference
    comparisons, so 1,040 of its 1,380 calls carried no price at all (#68).

    Carried arms are separated from generated ones. carry_arms() copies the
    control runs forward with their usage fields intact, so totalling every
    run in the file bills this round for calls an earlier round paid: round 12
    carries three control arms and reads 850 runs against the 340 it actually
    issued. The carried row is kept rather than dropped - the tokens are real
    and the snapshot's numbers rest on them - but it is not this round's cost.

    "priced" is reported beside "calls" on purpose. Snapshots recorded before
    the capture landed total to zero, and a bare $0.00 for a stage that
    plainly cost money would read as a measurement rather than as a gap.
    """
    carried = set((snap.get("metadata", {}).get("carried_arms_from") or {}).get("arms") or [])
    runs = [r for r in snap.get("runs", []) if r.get("ok")]
    # A carried judgment carries the usage of the call that originally bought
    # it, exactly as a carried run does, so it is split out for the same
    # reason (#83). The split reads the per-record marker judge.py writes when
    # it copies a verdict forward - not the arm - because the arm alone cannot
    # tell the two cases apart. Round 14 re-graded its own controls and really
    # did spend $25.05 doing so; pricing that as "paid earlier" would
    # understate what the round cost by 41%.
    judged = list(judgments)
    stages = (("generation", [r for r in runs if r.get("arm") not in carried], False),
              ("judging", [j for j in judged if not j.get("carried")], True),
              ("preference", list(comparisons), True),
              ("carried (paid earlier)", [r for r in runs if r.get("arm") in carried], False),
              ("carried judgments (paid earlier)",
               [j for j in judged if j.get("carried")], True))
    rows = []
    for name, records, nested in stages:
        used = [u for u in (_usage_of(r, nested) for r in records) if u]
        row = {"stage": name, "calls": len(records), "priced": len(used),
               "billed": not name.startswith("carried")}
        for f in bench_judge.USAGE_FIELDS:
            row[f] = sum(u.get(f, 0) for u in used)
        rows.append(row)
    return rows


SUMMED = ("calls", "priced", "input_tokens", "cache_creation_input_tokens",
          "cache_read_input_tokens", "output_tokens", "total_cost_usd")


def _cost_row(label, r):
    return "| %s | %d | %d | %s | %s | %s | %s | %s |" % (
        label, r["calls"], r["priced"],
        "{:,}".format(r["input_tokens"]),
        "{:,}".format(r["cache_creation_input_tokens"]),
        "{:,}".format(r["cache_read_input_tokens"]),
        "{:,}".format(r["output_tokens"]),
        ("**%.2f**" if label.startswith("**") else "%.2f") % r["total_cost_usd"])


def _cost_table(rows):
    out = ["| stage | calls | priced | input | cache write | cache read | output | USD |",
           "|---|--:|--:|--:|--:|--:|--:|--:|"]
    billed = [r for r in rows if r["billed"]]
    for r in billed:
        out.append(_cost_row(r["stage"], r))
    # The total covers what this round issued. Carried runs are listed under
    # it, outside the sum, because they were paid for in the round that
    # generated them and adding them here would bill the same calls twice.
    out.append(_cost_row("**this round**", {f: sum(r[f] for r in billed) for f in SUMMED}))
    for r in rows:
        if not r["billed"] and r["calls"]:
            out.append(_cost_row(r["stage"], r))
    unpriced = [r["stage"] for r in rows if r["calls"] and not r["priced"]]
    if unpriced:
        out.append("")
        out.append("_No usage recorded for: %s. Snapshots written before #68 "
                   "carry none; those stages cost money the table cannot show._"
                   % ", ".join(unpriced))
    return "\n".join(out)


def run_provenance(snap):
    """When a snapshot's runs were generated and by which CLI, read off the
    runs rather than off metadata (#80).

    The metadata stamp is written once, when the file is created, and never
    updated. So a round assembled from per-case shards into a pre-seeded file
    inherits the provenance of whatever that file was born from:
    round-12.json records CLI 2.1.223 and 6 August, both of them
    round-01-n10-v2.json's, for runs generated three days later on 2.1.226.
    A per-run stamp cannot be inherited that way, and a round that legitimately
    spans hours or CLI versions can say so instead of picking one.

    Falls back to the metadata stamp when no run carries its own, which is
    true of every snapshot committed before run.py started stamping them.
    Carried arms are older runs and are usually unstamped, so the span
    describes what this round generated; carry_arms writes its own separate
    disclosure for the rest.
    """
    runs = snap.get("runs", [])
    meta = snap.get("metadata", {})
    when = sorted(r["generated_at"] for r in runs if r.get("generated_at"))
    vers = sorted(set(r["claude_cli_version"] for r in runs
                      if r.get("claude_cli_version")))
    if not when:
        return meta.get("generated_at"), meta.get("claude_cli_version")
    span = when[0] if when[0] == when[-1] else "%s to %s" % (when[0], when[-1])
    return span, ", ".join(vers) or meta.get("claude_cli_version")


def render(snap, judg, threshold, prefs=()):
    agg = aggregate(snap)
    arms, models = _arms_present(agg), _models_present(agg)
    meta = snap["metadata"]
    excluded = len([r for r in snap["runs"] if not r.get("ok")])

    generated, cli = run_provenance(snap)
    out = []
    out.append("_Generated: %s · CLI: %s · commit: %s_" %
               (generated, cli, meta.get("git_commit")))
    out.append("_Level: %s · reps: %s · rules cksum: %s_\n" %
               (meta.get("laconic_level"), meta.get("reps"), meta.get("rules_cksum")))
    out.append("**Excluded runs (call failed, never scored): %d**\n" % excluded)

    if (judg.get("metadata") or {}).get("gates_only"):
        out.append("**Judged for the gates only: responses on cases whose "
                   "verdicts feed no fatal counter - rule-adherence cases, and "
                   "saturated cells - were not graded. They are absent from the "
                   "trap-verdict table below, not passing it.**\n")

    total_usable, missing_judgments = _judgment_gap(snap, judg)
    if judg.get("judgments") and missing_judgments:
        out.append("**WARNING: judgments cover %d/%d usable runs (%d missing) - "
                   "judge.py has not finished; re-run it before trusting the "
                   "trap-verdict table below.**\n"
                   % (total_usable - missing_judgments, total_usable, missing_judgments))

    out.append("### Output tokens (median)\n")
    out.append(_by_arm_model(agg, "output_tokens", arms, models, "%.0f") + "\n")

    out.append("### Output tokens dispersion across reps (median across cases)\n")
    out.append("min:\n\n" + _by_arm_model(agg, "output_tokens_min", arms, models, "%.0f") + "\n")
    out.append("max:\n\n" + _by_arm_model(agg, "output_tokens_max", arms, models, "%.0f") + "\n")
    out.append("stdev:\n\n" + _by_arm_model(agg, "output_tokens_stdev", arms, models, "%.1f") + "\n")

    base = {m: _median([v["output_tokens"] for k, v in agg.items()
                        if k[1] == "baseline" and k[2] == m]) for m in models}
    ctrl = {m: _median([v["output_tokens"] for k, v in agg.items()
                        if k[1] == "terse-control" and k[2] == m]) for m in models}
    out.append("### Reduction vs baseline / vs terse control\n")
    rows = ["| arm | " + " | ".join(models) + " |",
            "|---|" + "|".join("--:" for _ in models) + "|"]
    for arm in arms:
        cells = []
        for m in models:
            vals = [v["output_tokens"] for k, v in agg.items() if k[1] == arm and k[2] == m]
            med = _median(vals)
            b = ("%.0f%%" % (100 * (1 - med / base[m]))) if base.get(m) else "-"
            c = ("%.0f%%" % (100 * (1 - med / ctrl[m]))) if ctrl.get(m) else "-"
            cells.append("%s / %s" % (b, c))
        rows.append("| %s | %s |" % (arm, " | ".join(cells)))
    out.append("\n".join(rows) + "\n")

    out.append("### Readability violations (median per response)\n")
    out.append(_by_arm_model(agg, "violations", arms, models, "%.1f") + "\n")
    out.append("### Readability violations (total across responses; this is what gates)\n")
    out.append(_by_arm_model(agg, "violations_total", arms, models, "%d", agg_fn=sum) + "\n")
    out.append("### Responses with >=1 readability violation\n")
    out.append(_by_arm_model(agg, "violations_flagged_responses", arms, models, "%d", agg_fn=sum) + "\n")
    out.append("### Responses that called no tool at all (#46)\n")
    out.append("A design answer written without opening a file fails its case "
               "far more often than one that reads: pooled over the interleaved "
               "licence experiment, 20 of 39 against 6 of 40, Fisher p = 7.6e-4. "
               "Cases with no `fixture/` are one-turn by construction and are "
               "excluded from the gated count, though they appear here.\n")
    out.append(_by_arm_model(agg, "one_turn", arms, models, "%d", agg_fn=sum) + "\n")
    out.append("### Article rate\n")
    out.append(_by_arm_model(agg, "article_rate", arms, models, "%.3f") + "\n")
    out.append("### Auxiliary-verb rate\n")
    out.append(_by_arm_model(agg, "aux_verb_rate", arms, models, "%.3f") + "\n")
    out.append("### Cost per call, USD (median)\n")
    out.append(_by_arm_model(agg, "cost", arms, models, "%.4f") + "\n")
    out.append("### Duration, ms (median)\n")
    out.append(_by_arm_model(agg, "duration_ms", arms, models, "%.0f") + "\n")

    out.append("### What the round cost\n")
    out.append(_cost_table(cost_summary(snap, judg.get("judgments", []),
                                        prefs)) + "\n")

    # "0 failures" only means something once you know how many responses were
    # actually checked. Six cases (decision, floor, ordered-steps, and the
    # three quality cases) carry an empty never_cut list, so "checked" must be
    # reported alongside "unchecked" - a bare failure count reads as "every
    # response verified" even when under half the cases have anything to
    # verify.
    nc_checked = defaultdict(int)
    nc_unchecked = defaultdict(int)
    nc_fail = defaultdict(int)
    for (case, arm, model), v in agg.items():
        if v["never_cut_checked"]:
            nc_checked[arm] += v["n"]
        else:
            nc_unchecked[arm] += v["n"]
        nc_fail[arm] += v["never_cut_failures"]
    out.append("### Never-cut failures (checked vs unchecked responses)\n")
    out.append("| arm | checked | unchecked | failures |\n|---|--:|--:|--:|")
    for arm in arms:
        out.append("| %s | %d | %d | %d |" % (arm, nc_checked[arm], nc_unchecked[arm], nc_fail[arm]))
    out.append("")

    # judge.py records an infrastructure failure - the call itself failed, or
    # it succeeded but the reply couldn't be parsed as a verdict - as verdict
    # "not_exercised" with a reason in judge.INFRA_REASONS. Neither is a real
    # "the trap never fired" result, and folding either into not_exercised
    # would misreport the benchmark - a run of judge outages or parse
    # failures would look identical to a run of well-behaved responses that
    # just never tripped their traps. Count both separately.
    verdicts = defaultdict(lambda: defaultdict(int))
    judge_failed = defaultdict(int)
    for j in judg.get("judgments", []):
        key = (j["case"], j["arm"])
        if j.get("verdict") == "not_exercised" and j.get("reason") in bench_judge.INFRA_REASONS:
            judge_failed[key] += 1
        else:
            verdicts[key][j["verdict"]] += 1
    verdict_keys = set(verdicts) | set(judge_failed)
    if verdict_keys:
        out.append("### Trap verdicts by case\n")
        out.append("`grading` is where the case's criteria came from, and it "
                   "decides what the row may be used for. Only `quality` rows "
                   "support a comparison between arms; see evals/CRITERIA.md.\n")
        out.append("| case | grading | arm | pass | fail | not_exercised | judge_failed |\n"
                   "|---|---|---|--:|--:|--:|--:|")
        for (case, arm) in sorted(verdict_keys):
            v = verdicts[(case, arm)]
            out.append("| %s | %s | %s | %d | %d | %d | %d |"
                       % (case, case_grading(case), arm, v["pass"], v["fail"],
                          v["not_exercised"], judge_failed[(case, arm)]))
        out.append("")
        # A saturated cell's verdicts are in the table above (the rows sum
        # across models) but leave the fatal counters; a reader tallying the
        # table against safety_fails or quality_fails needs to know why the
        # numbers differ.
        for case in sorted(set(c for c, _ in verdict_keys)):
            for model in sorted(case_saturated_models(case)):
                out.append("`%s`/%s is marked saturated in its expect.json: its "
                           "verdicts appear above but are excluded from the "
                           "loop's fatal judge-verdict counters (#45).\n"
                           % (case, model))

    # The same split accept_verdict discloses, for a single snapshot. Printed
    # here too because a round is read one snapshot at a time before it is ever
    # compared, and this is the number that was flat in round 15 while both of
    # its halves moved.
    strata = _quality_strata(judg.get("judgments", []),
                             bench_run.usable(snap["runs"]))
    if strata["asks"]["n"] or strata["resolves"]["n"]:
        out.append("### Quality verdicts, split on whether the answer asks\n")
        out.append("Laconic arm, quality-graded cases. A response that hands a "
                   "decision back to the user is counted separately from one "
                   "that resolves it. **Disclosure, not a gate** - the covariate "
                   "was found after the round it explains (#88).\n")
        out.append("| stratum | responses | quality fails |\n|---|--:|--:|")
        for k, label in (("asks", "hands a decision back"),
                         ("resolves", "resolves it")):
            out.append("| %s | %d | %d |"
                       % (label, strata[k]["n"], strata[k]["fails"]))
        out.append("")

    failures = gate_failures(agg, threshold)
    out.append("### Gates\n")
    if failures:
        out.append("**FAILED (%d):**\n" % len(failures))
        out.extend("- %s" % f for f in failures)
    else:
        out.append("All gates pass: 0 readability violations, 0 never-cut failures, "
                   "article and auxiliary rates within %.0f%% of baseline."
                   % (threshold * 100))
    notes = gate_notes(agg, threshold)
    if notes:
        out.append("\n**Not gated (%d)** - reported so an unevaluated check is "
                   "not read as a passing one:\n" % len(notes))
        out.extend("- %s" % n for n in notes)
    return "\n".join(out) + "\n"


def _judgment_gap(snap, judg):
    """(usable_count, missing_count): how many usable runs have no judgment.

    Nothing else asserts every usable run got graded, so a partial judge run
    (interrupted, or run with a narrower --cases glob) would otherwise render
    identically to a complete one - the trap-verdicts table just quietly has
    fewer rows, which reads as "the missing cells never happened" rather than
    "never checked".
    """
    usable = bench_run.usable(snap["runs"])
    if not judg.get("judgments"):
        return (len(usable), 0)
    usable_keys = set((r["case"], r["arm"], r["model"], r["rep"]) for r in usable)
    # A file judged with judge.py's default coverage is not an unfinished file.
    # It says so in its own metadata, and the cells it left out are exactly the
    # ones no counter here reads, so they are excluded from the denominator
    # rather than reported as a gap every round.
    if (judg.get("metadata") or {}).get("gates_only"):
        usable_keys = set(k for k in usable_keys if feeds_judge_gate(k[0], k[2]))
    judged_keys = set((j["case"], j["arm"], j["model"], j["rep"])
                      for j in judg["judgments"])
    missing = usable_keys - judged_keys
    return (len(usable_keys), len(missing))


def _load_judgments(path):
    """Same as bench_run.load_snapshot, but tolerant of an empty-but-existing
    file (e.g. /dev/null used as a stand-in for "no judgments yet"). Scoped to
    exactly that case: a non-empty file that fails to parse is a real
    corruption, not an absence, and must raise rather than silently render a
    report with the trap-verdicts table quietly missing."""
    p = Path(path)
    if not p.exists():
        return {"judgments": []}
    text = p.read_text()
    if not text.strip():
        return {"judgments": []}
    return json.loads(text) or {"judgments": []}


def main():
    global CASES
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--judgments", default=str(JUDGMENTS))
    ap.add_argument("--threshold", type=float, default=0.70)
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--markdown")
    ap.add_argument("--cases-dir", default=str(CASES),
                    help="case directory holding expect.json; evals/holdout for the reserved set")
    ap.add_argument("--against",
                    help="previous round's snapshot: print deltas and an accept verdict")
    ap.add_argument("--target", default="output_tokens",
                    help="the metric the proposal's hypothesis named: "
                         "output_tokens, turns, or one of "
                         + ", ".join(COUNT_TARGETS))
    ap.add_argument("--target-cases",
                    help="comma-separated cases the hypothesis named; scores the "
                         "count target on those cases alone. The fatal conditions "
                         "stay round-wide and the round-wide target is printed too")
    ap.add_argument("--target-models",
                    help="comma-separated models the hypothesis named; narrows a "
                         "scoped count target to that stratum. Needs "
                         "--target-cases. The fatal conditions stay round-wide "
                         "and over both models, and a scope that names one model "
                         "must say so before the round (#96)")
    ap.add_argument("--against-judgments",
                    help="the previous round's judgments; required with --against")
    ap.add_argument("--preferences",
                    help="preference snapshot, for the flip-rate disclosure")
    ap.add_argument("--arbitration-results",
                    help="replication snapshot for arbitrating one-flip fatal "
                         "count losses (#52); same reps, the round's rules")
    ap.add_argument("--arbitration-judgments",
                    help="the replication's judgments; required with "
                         "--arbitration-results")
    ap.add_argument("--cell-rates", default=str(CELL_RATES),
                    help="measured per-cell failure rates under master rules; "
                         "screens a risen cell against its own rate before "
                         "calling it a fatal loss")
    ap.add_argument("--no-cell-rates", action="store_true",
                    help="score without the measured-rate screen, the way "
                         "rounds 01 to 11 were scored")
    args = ap.parse_args()

    CASES = Path(args.cases_dir)

    # A misspelled case would score an empty set, which reads as "already 0
    # before the edit" - a rejection that blames the edit for a typo. Checked
    # against the case directory before anything is loaded.
    target_cases = sorted({c.strip() for c in (args.target_cases or "").split(",") if c.strip()})
    unknown = [c for c in target_cases if not (CASES / c).is_dir()]
    if unknown:
        sys.exit("--target-cases names no case under %s: %s"
                 % (CASES, ", ".join(unknown)))
    if target_cases and not args.against:
        sys.exit("--target-cases only scopes the accept verdict; it needs --against")
    # Sixteen of the 22 cases have a structurally fixed one-turn rate - four
    # have no fixture and are forced to 100%, ten are read every time and sit
    # at 0%, and design-alerting and design-audit-log have read 0 or 1 of 10 in
    # every stored round across three rules revisions and four CLI versions. An
    # unscoped one_turn target is those cases diluting the six that carry all
    # the variance, so the scope is required rather than merely advised (#46).
    if args.target == "one_turn" and not target_cases:
        sys.exit("--target one_turn needs --target-cases: 16 of 22 cases have a "
                 "structurally fixed one-turn rate and would only dilute the "
                 "count. The cases with both variance and a measured link to "
                 "answer quality are design-cache, design-realtime and "
                 "design-upload")
    target_models = sorted({m.strip() for m in (args.target_models or "").split(",")
                            if m.strip()})
    if target_models and not target_cases:
        sys.exit("--target-models narrows a scoped target; it needs --target-cases")
    if target_models and target_models[0] not in ("haiku", "sonnet"):
        sys.exit("--target-models names an unknown model: %s"
                 % ", ".join(target_models))

    # load_snapshot has the identical corrupt-file defect _load_judgments is
    # guarded against below: json.loads on a non-empty, invalid file raises
    # ValueError uncaught, surfacing a raw traceback instead of a message
    # naming the file.
    try:
        snap = bench_run.load_snapshot(args.results)
    except ValueError as e:
        sys.exit("corrupt results file %s: %s" % (args.results, e))
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)

    # A total generation outage (every run recorded ok=False) makes
    # aggregate() return {} and gate_failures() vacuously return [] - a
    # second line of defense would silently bless it as "gates pass". Task 4
    # shipped exactly this failure mode once already (every call in a real
    # run recorded as a failure); this must not recur unnoticed. Fires
    # regardless of --no-gate - an empty snapshot is not a report anyone
    # wants rendered, gated or not.
    usable_runs = len(bench_run.usable(snap["runs"]))
    if usable_runs == 0:
        sys.exit("no usable runs in %s - every call failed; nothing to report" % args.results)

    try:
        judg = _load_judgments(args.judgments)
    except ValueError as e:
        sys.exit("corrupt judgments file %s: %s" % (args.judgments, e))

    total_usable, missing_judgments = _judgment_gap(snap, judg)
    if judg.get("judgments") and missing_judgments:
        print("WARNING: judgments cover %d/%d usable runs (%d missing) - "
             "judge.py has not finished" % (total_usable - missing_judgments,
                                            total_usable, missing_judgments),
             file=sys.stderr)

    # Loaded here rather than inside the --against branch: preference is 700 of
    # a round's 1,380 calls, and the cost table in the rendered report needs it
    # on the path that has no --against at all.
    prefs = (bench_run.load_snapshot(args.preferences) or {}).get("comparisons", []) \
        if args.preferences else []

    # The loop's compare step. Exits 1 on reject so a round that fails its own
    # accept rule fails a command, the same contract the gates already keep.
    if args.against:
        try:
            prev_snap = bench_run.load_snapshot(args.against)
        except ValueError as e:
            sys.exit("corrupt results file %s: %s" % (args.against, e))
        if prev_snap is None:
            sys.exit("no snapshot at %s" % args.against)
        # Without the previous round's verdicts its quality count is 0, and
        # every comparison reads as a regression from zero - a rejection that
        # says nothing about the edit. Required rather than defaulted: silently
        # dropping a fatal check is worse than refusing to run.
        if not args.against_judgments:
            sys.exit("--against needs --against-judgments; without the previous "
                     "round's verdicts every comparison reads as a quality "
                     "regression from 0")
        prev_judg = _load_judgments(args.against_judgments)["judgments"]
        # Arbitration needs both halves: a replication snapshot without its
        # judgments would read every judge-verdict metric as 0 in the
        # replication and clear cells nothing ever re-checked.
        arbitration = None
        if bool(args.arbitration_results) != bool(args.arbitration_judgments):
            sys.exit("--arbitration-results and --arbitration-judgments are "
                     "required together")
        if args.arbitration_results:
            arb_snap = bench_run.load_snapshot(args.arbitration_results)
            if arb_snap is None:
                sys.exit("no snapshot at %s" % args.arbitration_results)
            arb_judg = _load_judgments(args.arbitration_judgments)["judgments"]
            arbitration = round_summary(arb_snap, arb_judg)
        rates = {} if args.no_cell_rates else load_cell_rates(args.cell_rates)
        verdict, reasons = accept_verdict(
            round_summary(prev_snap, prev_judg, target_cases=target_cases,
                          target_models=target_models),
            round_summary(snap, judg["judgments"], prefs,
                          target_cases=target_cases,
                          target_models=target_models),
            args.target, target_cases=target_cases, arbitration=arbitration,
            cell_rates=rates, target_models=target_models)
        print("verdict: %s (target %s%s%s, against %s)"
              % (verdict, args.target,
                 (" on %s" % ", ".join(target_cases)) if target_cases else "",
                 (" (%s only)" % ", ".join(target_models)) if target_models else "",
                 args.against))
        # Which cells the screen was able to speak for at all, whether or not
        # any of them rose this round. A gate that can silently stop applying
        # to a cell is a gate nobody can audit.
        for metric, cells in sorted(rates.items()):
            eligible = ["%s/%s" % c for c, v in sorted(cells.items())
                        if v.get("runs", 0) >= CELL_RATE_MIN_RUNS]
            if eligible:
                print("  measured-rate screen active on %s: %s"
                      % (metric, ", ".join(eligible)))
        for r in reasons:
            print("  %s" % r)
        # The counters the verdict just read silently skip saturated cells;
        # say so beside the verdict rather than leaving the exclusion to be
        # discovered by a hand recount.
        for case in sorted(set(r["case"] for r in bench_run.usable(snap["runs"]))):
            for model in sorted(case_saturated_models(case)):
                print("  note: %s/%s excluded from judge-verdict counters "
                      "(saturated; see its expect.json)" % (case, model))
        sys.exit(0 if verdict == "accept" else 1)

    md = render(snap, judg, args.threshold, prefs)
    if args.markdown:
        Path(args.markdown).write_text(md)
        print("wrote %s" % args.markdown)
    else:
        print(md)

    if not args.no_gate and gate_failures(aggregate(snap), args.threshold):
        sys.exit(1)


if __name__ == "__main__":
    main()
