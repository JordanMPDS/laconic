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
    """The fatal quality reason from an accept_verdict, or None if it held.

    Two wordings reject: the per-cell one the gate has always printed, and the
    round-wide one #259 added. Both begin with the same prefix, which is built
    off report.FATAL rather than spelled out, so a rename there breaks this
    loudly instead of silently matching nothing.
    """
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


def inject(judg, keep, n, rng, concentrated=False):
    """`judg` with n passing verdicts of the edit block flipped to fail (#259).

    The power arm. A null pool cannot say what a gate detects, only what it
    reports on nothing, so the effect has to be put in by hand - and putting it
    into the verdicts rather than into the text is what keeps the gate the
    thing under test instead of the judge.

    Dispersed spreads the same total uniformly over every eligible verdict.
    Concentrated packs it into as few cells as possible, saturating one before
    it starts the next, which is the shape of a regression that ruins one case
    rather than shaving every case. The two produce the SAME round-wide total
    by construction, so wherever the two curves coincide the gate is deciding
    on the round-wide count alone and cannot see concentration at all.
    """
    pool = [j for j in judg
            if j["rep"] in keep and j.get("arm") == "laconic"
            and j.get("verdict") == "pass"
            and report.case_grading(j["case"]) == "quality"
            and report.feeds_judge_gate(j["case"], j.get("model"))]
    rng.shuffle(pool)
    if concentrated:
        cells = {}
        for j in pool:
            cells.setdefault((j["case"], j.get("model")), []).append(j)
        order = list(cells)
        rng.shuffle(order)
        pool = [j for c in order for j in cells[c]]
    flip = set(id(j) for j in pool[:n])
    return [dict(j, verdict="fail") if id(j) in flip else j for j in judg]


def draw(snap, judg, reps, rng, rates, blocks, legacy=False, n_inject=0,
         concentrated=False):
    """One control/edit[/arbitration] draw, scored by the real gate.

    With three blocks the gate is run twice on the same pair, once bare and
    once with the third block offered as the replication, so the two rates
    describe the same draws rather than two different sets of them.
    """
    picked = blocks_of(reps, rng, blocks)
    edit_judg = judg if not n_inject else inject(judg, set(picked[1]),
                                                 n_inject, rng, concentrated)
    prev, cur = (summarize(snap, judg, picked[0]),
                 summarize(snap, edit_judg, picked[1]))
    _, bare = report.accept_verdict(prev, cur, TARGET, cell_rates=rates,
                                    legacy_count_gate=legacy)
    stood = None
    if blocks > 2:
        _, after = report.accept_verdict(
            prev, cur, TARGET, cell_rates=rates, legacy_count_gate=legacy,
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


#: The injected effects bar D reports, in judgments added to the edit block.
#: +13 is the gate's own 50% mark and +20 its 80% mark, both computed from the
#: test's arithmetic before the round ran; the rest bracket them.
INJECTIONS = (0, 2, 4, 7, 10, 13, 16, 20, 25, 30)


def fire_rate(snap, judg, reps, rates, args, n, concentrated=False):
    """Share of draws the gate rejects with n failures injected."""
    rng = random.Random(SEED)
    fired = 0
    for _ in range(args.draws):
        d = draw(snap, judg, reps, rng, rates, args.blocks,
                 legacy=args.legacy_count_gate, n_inject=n,
                 concentrated=concentrated)
        fired += bool(d["fired"])
    return fired


def power(snap, judg, reps, rates, args):
    """Bar D: what the gate detects once there is something to detect.

    The dispersed arm spreads the injection over every eligible cell and is the
    one bar D put a threshold on. The concentrated arm puts the same total into
    one cell; at five reps a side no cell is condemnable, so the two arms should
    read alike, and printing them together is how that blindness is disclosed
    rather than argued.
    """
    print("pool: %d runs, %d reps; draws: %d, seed %d; gate: %s\n"
          % (len(snap["runs"]), len(reps), args.draws, SEED,
             "legacy (pre-#259)" if args.legacy_count_gate else "repriced"))
    print("detection, failures injected into the edit block")
    print("  %-10s %-22s %s" % ("injected", "dispersed", "concentrated"))
    for n in INJECTIONS:
        disp = fire_rate(snap, judg, reps, rates, args, n)
        conc = fire_rate(snap, judg, reps, rates, args, n, concentrated=True)
        print("  %-10s %4d / %d  (%5.1f%%)   %4d / %d  (%5.1f%%)"
              % ("+%d" % n, disp, args.draws, pct(disp, args.draws),
                 conc, args.draws, pct(conc, args.draws)))
    print("\n  concentrated saturates one cell before starting the next")
    print("  +13 is the gate's registered 50%% mark, +20 its 80%% mark")
    return 0


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
    ap.add_argument("--legacy-count-gate", action="store_true",
                    help="score under the pre-#259 gate, which is the one "
                         "round 53 measured at 46.2%%")
    ap.add_argument("--power", action="store_true",
                    help="bar D: the detection curve, with failures injected "
                         "into the edit block instead of a null")
    args = ap.parse_args()

    snap = json.loads(Path(args.pool).read_text())
    raw = json.loads(Path(args.judgments).read_text())
    judg = raw["judgments"] if isinstance(raw, dict) else raw
    rates = report.load_cell_rates(args.cell_rates)

    reps = sorted({r["rep"] for r in snap["runs"]})
    if len(reps) < BLOCK * args.blocks:
        sys.exit("pool holds %d reps; a draw of %d blocks needs %d"
                 % (len(reps), args.blocks, BLOCK * args.blocks))

    if args.power:
        return power(snap, judg, reps, rates, args)

    rng = random.Random(SEED)
    draws = [draw(snap, judg, reps, rng, rates, args.blocks,
                  legacy=args.legacy_count_gate)
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
