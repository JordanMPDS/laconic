#!/usr/bin/env python3
"""Turn the committed snapshots into markdown tables, and enforce gates.

Runs entirely offline: no network, no third-party packages. Exits non-zero
when a gate fails, so a rules regression fails a command instead of waiting
for somebody to notice a number moved.
"""
import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
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
ARM_ORDER = ["baseline", "terse-control", "word-compression", "laconic"]
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


def _median(xs, default=0):
    return statistics.median(xs) if xs else default


# The noise floor is the published dispersion, not a fresh invention: 209 is
# laconic's output-token stdev on sonnet in the committed benchmark snapshot,
# and 0.35 is the preference judge's measured flip rate on 2026-08-01. A move
# smaller than the instrument's own noise is not an improvement, and a loop that
# treats it as one churns forever.
#
# This was 175 until the laconic arm was regenerated under current rules on
# 2026-08-04. The floor tracks whatever the published snapshot disperses at, so
# it rose with it and the gate is stricter than it was.
NOISE = {"stdev": 209, "flip_rate_max": 0.35, "alpha": 0.05}

# Each rejects on its own, whatever the target metric did. Compression bought
# by dropping a never-cut item is not a cheaper answer, it is a different and
# worse one.
FATAL = (("never_cut_failures", "never-cut"),
         ("quality_fails", "quality"),
         ("violations_total", "readability"))

# The three fatal counters are also the only non-token metrics a hypothesis may
# name. They are counts of rare events, not distributions, so the token gate's
# sign-test-plus-median-shift does not transfer: with 7 violations spread over
# three case/model cells, a sign test across cells cannot reach alpha however
# large the improvement is, and a token-stdev floor is meaningless for a count.
COUNT_TARGETS = ("never_cut_failures", "quality_fails", "violations_total")


def _binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p). Exact; n here is a handful of events."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


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


def round_summary(snap, judg=None, prefs=None):
    """The four numbers an accept decision needs, from one round's artefacts."""
    lac = {k: v for k, v in aggregate(snap).items() if k[1] == "laconic"}
    seen = defaultdict(dict)
    for p in prefs or []:
        seen[(p["case"], p["model"], p["rep"])][p["order"]] = p["winner_arm"]
    both = [v for v in seen.values() if 0 in v and 1 in v]
    flipped = [v for v in both if v[0] != v[1]]
    return {
        "never_cut_failures": sum(v["never_cut_failures"] for v in lac.values()),
        # Only a quality-graded case can lose a quality verdict. A
        # rule-adherence case grades the treatment against the text it was
        # handed, so counting its verdicts here would let the loop chase its
        # own tail.
        "quality_fails": sum(1 for j in (judg or [])
                             if j.get("arm") == "laconic" and j.get("verdict") == "fail"
                             and case_grading(j["case"]) == "quality"),
        "violations_total": sum(v["violations_total"] for v in lac.values()),
        "tokens": {(k[0], k[2]): v["output_tokens"] for k, v in lac.items()},
        "flip_rate": (len(flipped) / len(both)) if both else 0.0,
        # The count gate's exposure: how many treatment responses this round
        # gave the metric a chance to fail in.
        "n_runs": sum(1 for r in bench_run.usable(snap["runs"])
                      if r["arm"] == "laconic"),
    }


def accept_verdict(prev, cur, target, noise=None):
    """(verdict, reasons) for one round against the round before it.

    Fatal conditions reject alone. For output_tokens the target has to beat the
    noise floor on both estimators - a sign test across the case/model cells and
    a median shift larger than the published stdev - because either one alone
    accepts moves the benchmark cannot distinguish from sampling. For a count
    target it has to clear an exact conditional binomial test at the same alpha.

    An unrecognized target rejects. Falling through to the fatal conditions
    alone would return "accept" for any round that merely failed to regress,
    which reads as a confirmed hypothesis and is not one.

    Preference is disclosed and never decisive: the judge that produces it
    favours the longer answer 63% of the time and laconic is the short arm, so
    it may not reject an edit that passed every deterministic gate.
    """
    noise = noise or NOISE
    reasons = []
    fatal = False
    for key, label in FATAL:
        if cur[key] > prev[key]:
            reasons.append("REJECT: %s lost (%d -> %d)" % (label, prev[key], cur[key]))
            fatal = True

    if target == "output_tokens":
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
        a, b = prev[target], cur[target]
        p = _count_p(a, b, prev.get("n_runs", 0), cur.get("n_runs", 0))
        if p is None:
            reasons.append("REJECT: %s was already 0 before the edit, so this "
                           "round cannot show it falling" % target)
            fatal = True
        elif p >= noise["alpha"]:
            reasons.append("REJECT: %s %d -> %d, p = %.3f" % (target, a, b, p))
            fatal = True
        else:
            reasons.append("%s %d -> %d, p = %.3f" % (target, a, b, p))
    else:
        reasons.append("REJECT: unknown target %r (expected output_tokens or one "
                       "of %s)" % (target, ", ".join(COUNT_TARGETS)))
        fatal = True

    if cur["flip_rate"] >= noise["flip_rate_max"]:
        reasons.append("preference not citable: flip rate %.0f%% is at or above the "
                       "%.0f%% ceiling"
                       % (100 * cur["flip_rate"], 100 * noise["flip_rate_max"]))
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


def render(snap, judg, threshold):
    agg = aggregate(snap)
    arms, models = _arms_present(agg), _models_present(agg)
    meta = snap["metadata"]
    excluded = len([r for r in snap["runs"] if not r.get("ok")])

    out = []
    out.append("_Generated: %s · CLI: %s · commit: %s_" %
               (meta.get("generated_at"), meta.get("claude_cli_version"),
                meta.get("git_commit")))
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
    ap.add_argument("--against-judgments",
                    help="the previous round's judgments; required with --against")
    ap.add_argument("--preferences",
                    help="preference snapshot, for the flip-rate disclosure")
    args = ap.parse_args()

    CASES = Path(args.cases_dir)

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
        prefs = (bench_run.load_snapshot(args.preferences) or {}).get("comparisons", []) \
            if args.preferences else []
        verdict, reasons = accept_verdict(
            round_summary(prev_snap, prev_judg),
            round_summary(snap, judg["judgments"], prefs),
            args.target)
        print("verdict: %s (target %s, against %s)"
              % (verdict, args.target, args.against))
        for r in reasons:
            print("  %s" % r)
        sys.exit(0 if verdict == "accept" else 1)

    md = render(snap, judg, args.threshold)
    if args.markdown:
        Path(args.markdown).write_text(md)
        print("wrote %s" % args.markdown)
    else:
        print(md)

    if not args.no_gate and gate_failures(aggregate(snap), args.threshold):
        sys.exit(1)


if __name__ == "__main__":
    main()
