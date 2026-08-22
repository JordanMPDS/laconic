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
import levels as bench_levels  # noqa: E402

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


def case_grading(case):
    """A case with no grading field is reported as unclassified, never
    silently promoted to quality."""
    p = CASES / case / "expect.json"
    if not p.exists():
        return UNKNOWN_GRADING
    g = json.loads(p.read_text()).get("grading")
    return g if g in GRADINGS else UNKNOWN_GRADING


def case_saturated_models(case):
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
    p = CASES / case / "expect.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text()).get("saturated_models")
    return d if isinstance(d, dict) else {}


def _median(xs, default=0):
    return statistics.median(xs) if xs else default


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

# The four fatal counters are also the only non-token metrics a hypothesis may
# name. They are counts of rare events, not distributions, so the token gate's
# sign-test-plus-median-shift does not transfer: with 7 violations spread over
# three case/model cells, a sign test across cells cannot reach alpha however
# large the improvement is, and a token-stdev floor is meaningless for a count.
COUNT_TARGETS = ("never_cut_failures", "quality_fails", "safety_fails",
                 "violations_total")


# A measured rate below this many runs does not clear anything. At n = 10 the
# interval is wide enough to cover almost any count, which would turn the screen
# off rather than sharpen it - and a single n = 10 draw is the defect this
# exists to correct, so accepting one as the correction would be circular.
CELL_RATE_MIN_RUNS = 30
CELL_RATES = ROOT / "evals" / "snapshots" / "loop" / "cell-rates.json"

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


def _binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p). Exact; n here is a handful of events."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


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
                and j.get("model") not in case_saturated_models(j["case"])):
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
        if risen and cell_rates:
            rates = cell_rates.get(key) or {}
            cur_runs = (cur.get("cell_runs") or {})
            covered_by_rate = [
                c for c in risen
                if _rate_covers(rates.get(c), cur_cells.get(c, 0),
                                cur_runs.get(c, 0), noise["alpha"])]
            risen = [c for c in risen if c not in covered_by_rate]
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
        if not risen and covered_by_rate:
            reasons.append("%s rise (%d -> %d) is within the measured rate%s"
                           % (label, prev[key], cur[key], comp))
            continue
        if risen and arbitration:
            covered = (arbitration.get("run_cells")
                       if key in ("never_cut_failures", "violations_total")
                       else arbitration.get("judged_cells")) or set()
            arb_cells = (arbitration.get("cells") or {}).get(key, {})
            cleared = [c for c in risen
                       if c in covered
                       and arb_cells.get(c, 0) <= prev_cells.get(c, 0)]
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

    if target_cases and not (prev.get("scoped") and cur.get("scoped")):
        # Scoring a scoped hypothesis against round-wide counts would silently
        # answer a different question than the one the hypothesis asked.
        reasons.append("REJECT: --target-cases needs both rounds summarized with "
                       "the same scope")
        return "reject", reasons

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
        cells = sorted(c for c in set(prev["tokens"]) & set(cur["tokens"])
                       if c[0] in wanted)
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
                       if prev["tokens"][c] < TOKEN_CELL_MIN_BASELINE)
        if short and len(cells) - len(short) >= 6:
            cells = [c for c in cells if c not in set(short)]
            dropped = ("; %d cell(s) below the %d-token floor and not voting: %s"
                       % (len(short), TOKEN_CELL_MIN_BASELINE,
                          ", ".join("%s/%s %d" % (c[0], c[1], prev["tokens"][c])
                                    for c in short)))
        elif short:
            dropped = ("; %d cell(s) are below the %d-token floor and voted "
                       "anyway: dropping them would leave %d cells, under the "
                       "six a sign test needs to reach alpha. Name more cases "
                       "in the scope" % (len(short), TOKEN_CELL_MIN_BASELINE,
                                         len(cells) - len(short)))
        else:
            dropped = ""
        floors = [f for f in (prev.get("tokens_stdev", {}).get(c)
                              for c in cells)
                  if f is not None]
        if len(cells) < 6:
            p_all = bench_levels.sign_test(len(cells), len(cells)) if cells else 1.0
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
            improved = sum(1 for c in cells if cur["tokens"][c] < prev["tokens"][c])
            p = bench_levels.sign_test(improved, len(cells))
            shift = (_median([prev["tokens"][c] for c in cells])
                     - _median([cur["tokens"][c] for c in cells]))
            wide_cells = sorted(set(prev["tokens"]) & set(cur["tokens"]))
            wide_improved = sum(1 for c in wide_cells
                                if cur["tokens"][c] < prev["tokens"][c])
            wide_p = (bench_levels.sign_test(wide_improved, len(wide_cells))
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
        cells = sorted(set(prev["tokens"]) & set(cur["tokens"]))
        improved = sum(1 for c in cells if cur["tokens"][c] < prev["tokens"][c])
        p = bench_levels.sign_test(improved, len(cells)) if cells else 1.0
        shift = (_median([prev["tokens"][c] for c in cells])
                 - _median([cur["tokens"][c] for c in cells])) if cells else 0
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
            p = _count_p(a, b, src_prev.get("n_runs", 0),
                         src_cur.get("n_runs", 0))
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
        reasons.append("REJECT: unknown target %r (expected output_tokens or one "
                       "of %s)" % (target, ", ".join(COUNT_TARGETS)))
        fatal = True

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
                         "output_tokens, or one of " + ", ".join(COUNT_TARGETS))
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
