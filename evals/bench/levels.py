#!/usr/bin/env python3
"""Cross-level comparison: lite against full against ultra.

The plugin ships three levels and the four-arm benchmark measures one. This
answers the structural claim the rule text makes - that the levels are
cumulative and distinct - by asking whether the answer gets shorter across
them, and whether the never-cut contract survives at every level.

One snapshot per level, not one snapshot with a level column: run.py keys a run
by (case, arm, model, rep) with the level in the metadata, so two levels in one
file would collide on the key, and the rules-checksum guard would reject the
second level's payload anyway.

Length is measured in words of the response text, with output tokens reported
second. Output tokens count the model's tool turns as well as its answer, and
on this run that dominates: destructive/sonnet moves 1150 -> 3268 median output
tokens between lite and full while its answer stays 215 -> 204 words. For a
comparison between arms at one level that noise is common to every arm; for a
comparison between levels it is the confound, so the user-visible length leads.

Runs entirely offline against those snapshots - no network, no third-party
packages.
"""
import argparse
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import report as bench_report  # noqa: E402
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LEVELS = ("lite", "full", "ultra")
METRICS = (("words", "words of response text"),
           ("output_tokens", "output tokens (includes tool turns)"))


def _median(xs, default=0):
    return statistics.median(xs) if xs else default


def ladder(values):
    """Verdict for one sequence of per-level values, in LEVELS order.

    A tie is reported as its own verdict rather than folded into either of the
    others: two levels that produce the same length are the "cumulative and
    distinct" claim failing quietly, which is a different finding from a
    reversal and must not be reported as one. None (a level with no data)
    makes the sequence unjudgeable rather than passing on the rest.
    """
    if len(values) < 2 or any(v is None for v in values):
        return "incomplete"
    pairs = list(zip(values, values[1:]))
    if any(a == b for a, b in pairs):
        return "flat"
    return "monotonic" if all(a > b for a, b in pairs) else "broken"


def sign_test(k, n):
    """Two-sided exact binomial p for k successes in n at p=0.5.

    The per-case directions are what decide whether a level boundary does
    anything, and 11 of 22 has to be reported as the coin flip it is rather
    than as a direction. Exact rather than normal-approximated: n is 22.
    """
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1))
    return min(1.0, 2 * tail / 2 ** n)


def level_view(path):
    """(aggregate, usable runs, metadata) for one level's snapshot, or None."""
    snap = bench_run.load_snapshot(path)
    if snap is None:
        return None
    return (bench_report.aggregate(snap), bench_run.usable(snap["runs"]),
            snap["metadata"])


def cell_values(views, levels, metric):
    """{(case, model): {level: median}} - one median per cell per level."""
    out = defaultdict(dict)
    for lv in levels:
        buckets = defaultdict(list)
        for r in views[lv][1]:
            v = (metrics.score(r.get("text", ""))["words"] if metric == "words"
                 else r.get("output_tokens", 0))
            buckets[(r["case"], r["model"])].append(v)
        for key, vals in buckets.items():
            out[key][lv] = _median(vals)
    return out


def pooled(views, level, model, metric):
    """Every response in one level/model bucket, not one median per case."""
    return [metrics.score(r.get("text", ""))["words"] if metric == "words"
            else r.get("output_tokens", 0)
            for r in views[level][1] if r["model"] == model]


def _models(views):
    return sorted(set(r["model"] for _, runs, _ in views.values() for r in runs))


def render(views, levels):
    out = []
    models = _models(views)

    out.append("### Runs per level\n")
    out.append("| level | runs | failed | rules cksum | generated |\n|---|--:|--:|---|---|")
    for lv in levels:
        agg, runs, meta = views[lv]
        n = sum(v["n"] for v in agg.values())
        out.append("| %s | %d | %d | %s | %s |"
                   % (lv, n, len(runs) - n, meta.get("rules_cksum"),
                      meta.get("generated_at")))
    out.append("")

    for metric, label in METRICS:
        cells = cell_values(views, levels, metric)
        out.append("### Length by level: %s\n" % label)
        # Two estimators, because the four-arm run already showed the Haiku
        # compression sign depending on which one is used. Publishing one of
        # them would be picking the flattering answer.
        for est in ("median of per-case medians", "flat median over responses"):
            out.append("%s:\n" % est)
            out.append("| level | " + " | ".join(models) + " |")
            out.append("|---|" + "|".join("--:" for _ in models) + "|")
            series = defaultdict(list)
            for lv in levels:
                row = []
                for m in models:
                    if est.startswith("median of"):
                        vals = [c[lv] for (case, mm), c in cells.items()
                                if mm == m and lv in c]
                    else:
                        vals = pooled(views, lv, m, metric)
                    val = _median(vals) if vals else None
                    series[m].append(val)
                    row.append("%.0f" % val if val is not None else "-")
                out.append("| %s | %s |" % (lv, " | ".join(row)))
            out.append("")
            out.append("Ladder: %s\n" % ", ".join(
                "%s **%s**" % (m, ladder(series[m])) for m in models))

        # Per-case, because ultra's fallback makes the aggregate misleading on
        # its own: on a case whose honest answer does not fit in a line, ultra
        # is supposed to answer at full, so a flat cell there is the rule
        # working rather than failing.
        out.append("Per case:\n")
        out.append("| case | model | " + " | ".join(levels) + " | ladder |")
        out.append("|---|---|" + "|".join("--:" for _ in levels) + "|---|")
        for (case, model) in sorted(cells):
            vals = [cells[(case, model)].get(lv) for lv in levels]
            shown = ["%.0f" % v if v is not None else "-" for v in vals]
            out.append("| %s | %s | %s | %s |"
                       % (case, model, " | ".join(shown), ladder(vals)))
        out.append("")

        # The direction counts are the actual test. A ladder verdict on an
        # aggregate can be carried by two cells out of twenty-two.
        out.append("Direction, per case and model:\n")
        out.append("| boundary | shorter | of | two-sided sign test |\n|---|--:|--:|--:|")
        for a, b in zip(levels, levels[1:]):
            pairs = [(c[a], c[b]) for c in cells.values() if a in c and b in c]
            k = sum(1 for x, y in pairs if y < x)
            out.append("| %s to %s | %d | %d | p = %.2f |"
                       % (a, b, k, len(pairs), sign_test(k, len(pairs))))
        out.append("")

    # The never-cut contract sits above the first level marker, so every level
    # carries it verbatim. ultra is where a dropped safety clause is most
    # likely and had no measurement at all before this run.
    out.append("### Never-cut failures by level\n")
    out.append("| level | checked | unchecked | failures | where |\n|---|--:|--:|--:|---|")
    for lv in levels:
        agg = views[lv][0]
        checked = sum(v["n"] for v in agg.values() if v["never_cut_checked"])
        unchecked = sum(v["n"] for v in agg.values() if not v["never_cut_checked"])
        fails = sum(v["never_cut_failures"] for v in agg.values())
        where = ", ".join("%s/%s x%d" % (k[0], k[2], v["never_cut_failures"])
                          for k, v in sorted(agg.items())
                          if v["never_cut_failures"]) or "-"
        out.append("| %s | %d | %d | %d | %s |" % (lv, checked, unchecked, fails, where))
    out.append("")

    out.append("### Readability violations by level (total)\n")
    out.append("| level | " + " | ".join(models) + " | where |")
    out.append("|---|" + "|".join("--:" for _ in models) + "|---|")
    for lv in levels:
        agg = views[lv][0]
        cells_ = ["%d" % sum(v["violations_total"] for k, v in agg.items() if k[2] == m)
                  for m in models]
        where = ", ".join("%s/%s x%d" % (k[0], k[2], v["violations_total"])
                          for k, v in sorted(agg.items())
                          if v["violations_total"]) or "-"
        out.append("| %s | %s | %s |" % (lv, " | ".join(cells_), where))
    out.append("")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-dir", default=str(ROOT / "evals" / "snapshots"))
    ap.add_argument("--prefix", default="levels-")
    ap.add_argument("--markdown")
    args = ap.parse_args()

    views, missing = {}, []
    for lv in LEVELS:
        path = Path(args.snapshot_dir) / ("%s%s.json" % (args.prefix, lv))
        view = level_view(str(path))
        if view is None or not view[0]:
            missing.append(lv)
        else:
            views[lv] = view
    if not views:
        sys.exit("no level snapshots under %s - run run.py --level first" % args.snapshot_dir)

    levels = [lv for lv in LEVELS if lv in views]
    md = render(views, levels)
    # A level that never ran must be named. Silently rendering a two-level
    # table under a heading that promises three is the same defect class as a
    # gate that skips a check and reports a pass.
    if missing:
        md += "\n**Levels with no usable snapshot: %s.** Every table above " \
              "covers the rest only.\n" % ", ".join(missing)

    if args.markdown:
        Path(args.markdown).write_text(md)
        print("wrote %s" % args.markdown)
    else:
        print(md)


if __name__ == "__main__":
    main()
