#!/usr/bin/env python3
"""Turn the committed snapshots into markdown tables, and enforce gates.

Runs entirely offline: no network, no third-party packages. Exits non-zero
when a gate fails, so a rules regression fails a command instead of waiting
for somebody to notice a number moved.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"
ARM_ORDER = ["baseline", "terse-control", "word-compression", "laconic"]
# Rate gates are ratios of small integers on short answers. Below this floor the
# baseline itself carries too few articles or auxiliaries for the ratio to mean
# anything, and gating on it would produce flaky failures rather than findings.
RATE_FLOOR = 0.02


def _median(xs, default=0):
    return statistics.median(xs) if xs else default


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
        agg[key] = {
            "n": len(runs),
            "output_tokens": _median([r.get("output_tokens", 0) for r in runs]),
            "cost": _median([r.get("total_cost_usd", 0.0) for r in runs], 0.0),
            "duration_ms": _median([r.get("duration_ms", 0) for r in runs]),
            "violations": _median([s["violations"] for s in scored]),
            "article_rate": _median([s["article_rate"] for s in scored], 0.0),
            "aux_verb_rate": _median([s["aux_verb_rate"] for s in scored], 0.0),
            "never_cut_failures": sum(
                1 for r in runs
                if metrics.never_cut_missing(r.get("text", ""), never_cut)
            ),
            "spans": [sp for s in scored for sp in s["spans"]][:5],
        }
    return agg


def gate_failures(agg, threshold):
    out = []
    for (case, arm, model), v in sorted(agg.items()):
        if arm != "laconic":
            continue
        base = agg.get((case, "baseline", model))
        if v["violations"] > 0:
            out.append("%s/%s: %.1f readability violation(s) %s"
                       % (case, model, v["violations"], v["spans"]))
        if v["never_cut_failures"] > 0:
            out.append("%s/%s: %d never-cut failure(s)"
                       % (case, model, v["never_cut_failures"]))
        if base:
            if (base["article_rate"] >= RATE_FLOOR
                    and v["article_rate"] < threshold * base["article_rate"]):
                out.append("%s/%s: article rate %.3f below %.0f%% of baseline %.3f"
                           % (case, model, v["article_rate"], threshold * 100,
                              base["article_rate"]))
            if (base["aux_verb_rate"] >= RATE_FLOOR
                    and v["aux_verb_rate"] < threshold * base["aux_verb_rate"]):
                out.append("%s/%s: aux verb rate %.3f below %.0f%% of baseline %.3f"
                           % (case, model, v["aux_verb_rate"], threshold * 100,
                              base["aux_verb_rate"]))
    return out


def _arms_present(agg):
    return [a for a in ARM_ORDER if any(k[1] == a for k in agg)]


def _models_present(agg):
    return sorted(set(k[2] for k in agg))


def _by_arm_model(agg, field, arms, models, fmt="%s"):
    rows = ["| arm | " + " | ".join(models) + " |",
            "|---|" + "|".join("--:" for _ in models) + "|"]
    for arm in arms:
        cells = []
        for m in models:
            vals = [v[field] for k, v in agg.items() if k[1] == arm and k[2] == m]
            cells.append(fmt % _median(vals) if vals else "-")
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

    out.append("### Output tokens (median)\n")
    out.append(_by_arm_model(agg, "output_tokens", arms, models, "%.0f") + "\n")

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
    out.append("### Article rate\n")
    out.append(_by_arm_model(agg, "article_rate", arms, models, "%.3f") + "\n")
    out.append("### Auxiliary-verb rate\n")
    out.append(_by_arm_model(agg, "aux_verb_rate", arms, models, "%.3f") + "\n")
    out.append("### Cost per call, USD (median)\n")
    out.append(_by_arm_model(agg, "cost", arms, models, "%.4f") + "\n")
    out.append("### Duration, ms (median)\n")
    out.append(_by_arm_model(agg, "duration_ms", arms, models, "%.0f") + "\n")

    nc = defaultdict(int)
    for (case, arm, model), v in agg.items():
        nc[arm] += v["never_cut_failures"]
    out.append("### Never-cut failures (total across cases)\n")
    out.append("| arm | failures |\n|---|--:|")
    for arm in arms:
        out.append("| %s | %d |" % (arm, nc[arm]))
    out.append("")

    # judge.py records a failed judge *call* (subprocess/parse failure) as
    # verdict "not_exercised", reason "judge call failed". That is an
    # infrastructure failure, not a real "the trap never fired" result, and
    # folding it into not_exercised would misreport the benchmark - a run of
    # judge outages would look identical to a run of well-behaved responses
    # that just never tripped their traps. Count it separately.
    verdicts = defaultdict(lambda: defaultdict(int))
    judge_failed = defaultdict(int)
    for j in judg.get("judgments", []):
        key = (j["case"], j["arm"])
        if j.get("verdict") == "not_exercised" and j.get("reason") == "judge call failed":
            judge_failed[key] += 1
        else:
            verdicts[key][j["verdict"]] += 1
    verdict_keys = set(verdicts) | set(judge_failed)
    if verdict_keys:
        out.append("### Trap verdicts by case\n")
        out.append("| case | arm | pass | fail | not_exercised | judge_failed |\n"
                   "|---|---|--:|--:|--:|--:|")
        for (case, arm) in sorted(verdict_keys):
            v = verdicts[(case, arm)]
            out.append("| %s | %s | %d | %d | %d | %d |"
                       % (case, arm, v["pass"], v["fail"], v["not_exercised"],
                          judge_failed[(case, arm)]))
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
    return "\n".join(out) + "\n"


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--judgments", default=str(JUDGMENTS))
    ap.add_argument("--threshold", type=float, default=0.70)
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--markdown")
    args = ap.parse_args()

    snap = bench_run.load_snapshot(args.results)
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

    judg = _load_judgments(args.judgments)

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
