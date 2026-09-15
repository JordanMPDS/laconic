#!/usr/bin/env python3
"""Round 64's target: does a worked closed question shorten a closed answer?

    python3 evals/pilot/score_closed.py <control-confirm> <edit-confirm> \
        [<control-open> <edit-open>]

[#136] reports the rule "A yes/no question gets a word or a line" failing to
fire: an eight-word `correct?` question answered in ~400 words. `confirm-index`,
`confirm-metric` and `confirm-rollback` are the only scored cells whose graded
question has that shape, and laconic spends 72 to 82 median words on them.
Round 64 adds the file's first worked *closed* question and scores the fall.

**Per cell, then a sign test — never a pooled median.** The three cells sit at
different levels, so a pooled median lets one fixture decide the round. Each
cell gets its own two-sided permutation of the side label over per-run counts;
the three directions are combined by `metrics.sign_test`. The pooled figure is
printed as disclosure and decides nothing. That split is `codex`'s correction
from `tools/consult.sh` and is registered in `../results/loop/round-64.md`.

**[#131] stratification.** Words are compared inside one reading stratum. These
cells read their fixture on the graded turn in 60 of 60 runs of round 42, so
both sides are expected fully grounded; a cell whose reading rate crosses is
reported and does not vote, because an answer that stopped opening the file is
several times shorter for a reason that is not compression.

**[#209] mixture.** Every case here ends `Don't edit anything.`, so a mutating
run would mean the cell mixes work products with prose and must not score. The
count is reported whether or not it is zero.

The optional second pair is the discriminant: `fail-open`, `silent-success` and
`stale-cache`, open diagnostic questions of the same single-turn shape. They
answer whether the mechanism is closed questions specifically or a general
compression effect of a longer file.
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

SEED = 64
TARGET = ("confirm-index", "confirm-metric", "confirm-rollback")
DISCRIMINANT = ("fail-open", "silent-success", "stale-cache")


def cell(runs, case):
    rs = [r for r in bench_run.usable(runs) if r.get("case") == case]
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "words": [words(r) for r in rs],
    }


def compare(control_runs, edit_runs, cases, resamples=200000):
    """One row per cell: medians, reading rates, and a permutation p."""
    out = []
    for case in cases:
        c, e = cell(control_runs, case), cell(edit_runs, case)
        c_rate = c["grounded"] / c["n"] if c["n"] else 0.0
        e_rate = e["grounded"] / e["n"] if e["n"] else 0.0
        # A cell whose reading rate crossed has nothing to compare: the two
        # sides are not the same stratum. Zero tolerance is right here only
        # because these cells read in 60 of 60 archived runs; a cell that
        # genuinely varies would need the stratum split instead.
        crossed = c_rate != e_rate
        mixed = bool(c["edits"] or e["edits"])
        votes = not (crossed or mixed)
        out.append({
            "case": case,
            "control": c,
            "edit": e,
            "crossed": crossed,
            "mixed": mixed,
            "votes": votes,
            "median_control": metrics.median(c["words"]),
            "median_edit": metrics.median(e["words"]),
            "p": metrics.permutation(c["words"], e["words"], SEED, resamples,
                                     stat=statistics.median) if votes else None,
        })
    return out


def combine(rows):
    """(fell, voting, sign-test p) over the cells that voted."""
    voting = [r for r in rows if r["votes"]]
    fell = sum(1 for r in voting if r["median_edit"] < r["median_control"])
    return fell, len(voting), metrics.sign_test(fell, len(voting))


def fmt_p(p):
    if p is None:
        return "-"
    return "< 0.00001" if p < 1e-5 else "%.5f" % p


def table(control_runs, edit_runs, cases, label, resamples):
    rows = compare(control_runs, edit_runs, cases, resamples)
    print("%s\n" % label)
    print("  %-16s %-18s %-18s %-11s %-13s %s"
          % ("cell", "control median", "edit median", "p", "read c/e", "edits"))
    for r in rows:
        note = " (crossed)" if r["crossed"] else (" (mixed)" if r["mixed"] else "")
        print("  %-16s %-18s %-18s %-11s %-13s %d"
              % (r["case"],
                 "%.1f (n=%d)" % (r["median_control"], r["control"]["n"]),
                 "%.1f (n=%d)" % (r["median_edit"], r["edit"]["n"]),
                 fmt_p(r["p"]) + note,
                 "%d/%d %d/%d" % (r["control"]["grounded"], r["control"]["n"],
                                  r["edit"]["grounded"], r["edit"]["n"]),
                 r["control"]["edits"] + r["edit"]["edits"]))
    fell, voting, p = combine(rows)
    print("\n  %d of %d voting cells fell, two-sided sign test p = %s"
          % (fell, voting, fmt_p(p)))
    pooled_c = [w for r in rows for w in r["control"]["words"]]
    pooled_e = [w for r in rows for w in r["edit"]["words"]]
    print("  pooled median %.1f to %.1f (disclosure only, decides nothing)\n"
          % (metrics.median(pooled_c), metrics.median(pooled_e)))
    return rows, fell, voting, p


def main(argv):
    if len(argv) not in (2, 4):
        sys.exit(__doc__)
    resamples = 200000

    def runs(path):
        return json.loads(Path(path).read_text())["runs"]

    rows, fell, voting, p = table(runs(argv[0]), runs(argv[1]), TARGET,
                                  "TARGET  %s against %s"
                                  % (Path(argv[1]).name, Path(argv[0]).name),
                                  resamples)
    rose = [r for r in rows if r["votes"] and r["p"] is not None
            and r["p"] < 0.05 and r["median_edit"] > r["median_control"]]

    if len(argv) == 4:
        table(runs(argv[2]), runs(argv[3]), DISCRIMINANT,
              "DISCRIMINANT  %s against %s"
              % (Path(argv[3]).name, Path(argv[2]).name), resamples)

    # The registered falsifier: fewer than 3 of 3 cells falling, or any cell
    # separating upward. Three cells is the smallest scope a sign test can
    # speak for, so the primary requires a clean sweep and said so in advance.
    reasons = []
    if voting < len(TARGET):
        reasons.append("%d of %d target cells voted" % (voting, len(TARGET)))
    if fell < len(TARGET):
        reasons.append("%d of %d cells fell, the registered bar is %d"
                       % (fell, voting, len(TARGET)))
    for r in rose:
        reasons.append("%s separated upward (p = %s)" % (r["case"], fmt_p(r["p"])))
    if reasons:
        print("PRIMARY REJECTED: %s" % "; ".join(reasons))
        return 1
    print("PRIMARY PASSES the registered falsifier (sign test p = %s)" % fmt_p(p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
