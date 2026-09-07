#!/usr/bin/env python3
"""Round 53's target: how often does the fatal quality gate fire on nothing?

    python3 evals/pilot/score_aa.py <pool> --judgments <pool-judgments>

[Round 51](../results/loop/round-51.md) and
[round 52](../results/loop/round-52.md) both rejected on the same counter:
round-wide `quality_fails` rose, +7 and +4, on an edit whose registered target
passed. Neither rise was significant round-wide (Fisher p = 0.4516 and
p = 0.6977), and the loop's fatal counters carry no significance test by
design, so neither round could say whether it had measured harm or drawn a
card. This script asks the question those rounds could not: run the gate on
two arms that differ in nothing, and count how often it rejects.

**The pool is one interleaved batch at master rules**, 15 reps over the 28
quality-graded cases and both models. A draw partitions its reps into three
disjoint 5-rep blocks and labels them control, edit and arbitration - the three
roles a round actually uses. Nothing distinguishes the blocks but the label, so
every rejection the gate reports on one is a false positive by construction.

Five reps is the unit deliberately. It is what `judge.py` and every round since
21 buy per side, and it is below `report.CELL_TEST_MIN_RUNS`, so the [#133]
sampling screen is inactive and 22 of the 28 quality cells are scored by a bare
count comparison of one 5-run draw against another. Whether that matters is
exactly what is being measured.

**The gate is imported, never reimplemented.** `report.round_summary` and
`report.accept_verdict` are the functions `report.py --against` calls, run here
on sub-snapshots, with `cell-rates.json` loaded the same way. A second copy of
the counter would be a second thing to keep in sync, and a drift between them
would produce a null that does not describe the gate the loop actually runs.

**What this can and cannot conclude.** A high firing rate shows the gate cannot
separate an edit from nothing at 5 reps; it does not show rounds 51 and 52's
edits were harmless. Those are different claims and only the first is measured
here. The draws also come from one 15-rep batch, so they are re-partitions of a
single sample rather than 500 independent experiments: the quantity is the
gate's behaviour conditional on this batch, which is the right conditional -
sampling inside a round is what a round is exposed to - but its own uncertainty
is not 1/sqrt(draws).

[#133]: https://github.com/JordanMPDS/laconic/issues/133
"""
import argparse
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import report  # noqa: E402

SEED = 53

#: Reps per block. Five is the round unit: what every round since 21 buys per
#: side, and below report.CELL_TEST_MIN_RUNS, so the #133 screen is inactive.
BLOCK = 5

#: Blocks per draw. Three are control, edit and arbitration; --blocks 2 scores
#: a pool that can only afford the first two, and reports no arbitration.
BLOCKS = 3

#: The label report.FATAL gives quality_fails, and the prefix accept_verdict
#: builds a fatal reason from. Read off report rather than spelled out, so a
#: rename there breaks this loudly instead of silently matching nothing.
QUALITY_LABEL = dict(report.FATAL)["quality_fails"]
FATAL_PREFIX = "REJECT: %s lost" % QUALITY_LABEL

#: The target passed to accept_verdict. The fatal conditions run whatever the
#: target is, and this round reads only those, so the choice is arbitrary and
#: fixed here rather than exposed as a flag that could be tuned after the fact.
TARGET = "output_tokens"


def blocks_of(reps, rng, blocks):
    """One draw: `blocks` disjoint blocks of BLOCK reps, in a random order."""
    shuffled = list(reps)
    rng.shuffle(shuffled)
    return [sorted(shuffled[i * BLOCK:(i + 1) * BLOCK]) for i in range(blocks)]


def slice_snap(snap, keep):
    """The snapshot restricted to one block's reps."""
    return dict(snap, runs=[r for r in snap["runs"] if r["rep"] in keep])


def slice_judg(judg, keep):
    return [j for j in judg if j["rep"] in keep]


def summarize(snap, judg, keep):
    return report.round_summary(slice_snap(snap, keep), slice_judg(judg, keep))


def quality_reason(reasons):
    """The fatal quality reason from an accept_verdict, or None if it held."""
    for r in reasons:
        if r.startswith(FATAL_PREFIX):
            return r
    return None


def risen_cells(reason):
    """The case/model cells a fatal reason names as risen.

    The composition is the segment after "; cells: " and before the next
    "; ", which is where accept_verdict puts the screened-out cells.
    """
    if not reason or "; cells: " not in reason:
        return []
    tail = reason.split("; cells: ", 1)[1].split(";", 1)[0]
    return [part.strip().rsplit(" +", 1)[0] for part in tail.split(", ")]


def draw(snap, judg, reps, rng, rates, blocks):
    """One control/edit[/arbitration] draw, scored by the real gate.

    With three blocks the gate is run twice on the same pair, once bare and
    once with the third block offered as the replication, so the two rates
    describe the same draws rather than two different sets of them.
    """
    picked = blocks_of(reps, rng, blocks)
    prev, cur = (summarize(snap, judg, picked[0]),
                 summarize(snap, judg, picked[1]))
    _, bare = report.accept_verdict(prev, cur, TARGET, cell_rates=rates)
    stood = None
    if blocks > 2:
        _, after = report.accept_verdict(
            prev, cur, TARGET, cell_rates=rates,
            arbitration=summarize(snap, judg, picked[2]))
        stood = quality_reason(after)
    return {
        "delta": cur["quality_fails"] - prev["quality_fails"],
        "control": prev["quality_fails"],
        "edit": cur["quality_fails"],
        "fired": quality_reason(bare),
        "stood": stood,
    }


def pct(n, d):
    return 0.0 if not d else 100.0 * n / d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pool")
    ap.add_argument("--judgments", required=True)
    ap.add_argument("--draws", type=int, default=500)
    ap.add_argument("--blocks", type=int, default=BLOCKS,
                    help="disjoint 5-rep blocks per draw: 3 scores the "
                         "arbitration too, 2 scores only the bare gate")
    ap.add_argument("--cell-rates", default=None)
    args = ap.parse_args()

    snap = json.loads(Path(args.pool).read_text())
    raw = json.loads(Path(args.judgments).read_text())
    judg = raw["judgments"] if isinstance(raw, dict) else raw
    rates = report.load_cell_rates(args.cell_rates)

    reps = sorted({r["rep"] for r in snap["runs"]})
    if len(reps) < BLOCK * args.blocks:
        sys.exit("pool holds %d reps; a draw of %d blocks needs %d"
                 % (len(reps), args.blocks, BLOCK * args.blocks))

    rng = random.Random(SEED)
    draws = [draw(snap, judg, reps, rng, rates, args.blocks)
             for _ in range(args.draws)]

    fired = [d for d in draws if d["fired"]]
    stood = [d for d in draws if d["stood"]]
    deltas = [d["delta"] for d in draws]
    rises = [x for x in deltas if x > 0]

    print("pool: %d runs, %d reps, %d quality-graded cases, rules_cksum %s"
          % (len(snap["runs"]), len(reps),
             len({r["case"] for r in snap["runs"]}),
             snap.get("metadata", {}).get("rules_cksum")))
    print("draws: %d, seed %d, %d blocks of %d reps\n"
          % (len(draws), SEED, args.blocks, BLOCK))

    print("the gate on nothing")
    print("  fatal quality loss reported      %4d / %d  (%.1f%%)"
          % (len(fired), len(draws), pct(len(fired), len(draws))))
    if args.blocks > 2:
        print("  still standing after arbitration %4d / %d  (%.1f%%)"
              % (len(stood), len(draws), pct(len(stood), len(draws))))
        print("  cleared by the replication       %4d / %d  (%.1f%% of fired)"
              % (len(fired) - len(stood), len(fired),
                 pct(len(fired) - len(stood), len(fired))))
    else:
        print("  arbitration not scored: --blocks 2")

    print("\nquality_fails difference, edit block minus control block")
    print("  median %+.1f, mean %+.2f, range %+d to %+d"
          % (statistics.median(deltas), statistics.fmean(deltas),
             min(deltas), max(deltas)))
    print("  rose in %d of %d draws (%.1f%%)"
          % (len(rises), len(draws), pct(len(rises), len(draws))))
    for observed, label in ((7, "round 51"), (4, "round 52")):
        n = sum(1 for x in deltas if x >= observed)
        print("  >= %+d (%s's rise): %d of %d (%.1f%%)"
              % (observed, label, n, len(draws), pct(n, len(draws))))

    print("\ncells the null names as risen, most frequent first")
    counts = Counter(c for d in fired for c in risen_cells(d["fired"]))
    for cell, n in counts.most_common(12):
        print("  %-28s %4d / %d  (%.1f%%)"
              % (cell, n, len(draws), pct(n, len(draws))))

    print("\nrisen cells per firing draw: median %.1f, max %d"
          % (statistics.median([len(risen_cells(d["fired"])) for d in fired])
             if fired else 0.0,
             max([len(risen_cells(d["fired"])) for d in fired], default=0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
