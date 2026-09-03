#!/usr/bin/env python3
"""Merge the shard snapshots of one sharded round into a single snapshot.

A round generated at N-way concurrency writes N files, because each process
owns its own file and nothing races on a write. Every consumer downstream -
judge.py, report.py, prefer.py - takes one `--results` path, so the shards have
to become one file before the round can be scored.

Until now that merge happened by hand, and `evals/results/loop/concurrency-audit.md`
says so about ten committed snapshots. Doing it by hand is how the first
`opus-model-set.json` came out holding 100 of 660 runs: a silent under-merge
looks exactly like a round that was never finished, and the number it reports is
wrong rather than absent. This is the same union the maintainer was doing,
except it checks the things a hand merge cannot be relied on to check.

What it refuses:

- **Shards generated from different rules.** `rules_cksum` is the guard the
  whole harness is built around; merging across it would produce one round from
  two instruments, which is the exact failure run.py's resume guard exists to
  prevent.
- **Shards at different levels.** `laconic_level` picks which slice of the rules
  the treatment arm carries, so two levels in one file is two treatments.
- **Shards whose arm definitions differ.** Equal `rules_cksum` makes this
  near-impossible, but the check is one comparison and the alternative is a
  merged file whose `arms` block describes only whichever shard was read first.

What it recomputes rather than copies, because a merged file describes a round
no single shard saw:

- `cases_cksum`, over the union of the cases actually present. Shards that split
  22 cases into two halves legitimately carry three different checksums, so
  copying any one of them would stamp the merged file with a subset's identity.
- `max_runs_in_flight`, by the same sweep run.py stamps at write time (#120).
- `concurrency_declared`, as the maximum any shard declared and never less than
  the number of shards, so the merged file cannot claim a lower concurrency than
  the merge itself demonstrates.

`metadata.shards` records where every run came from, so the merged file carries
its own provenance instead of leaving it to be reconstructed.
"""
import argparse
import json
import sys
from pathlib import Path

import concurrency
import run as R


def merge(paths, cases_dir=None):
    snaps = []
    for p in paths:
        s = R.load_snapshot(p)
        if s is None:
            sys.exit("no snapshot at %s" % p)
        s["__path"] = str(p)
        snaps.append(s)

    first = snaps[0]
    fm = first["metadata"]
    for s in snaps[1:]:
        m = s["metadata"]
        for key in ("rules_cksum", "laconic_level"):
            if m.get(key) != fm.get(key):
                sys.exit(
                    "%s and %s disagree on %s (%s vs %s). These are two rounds, "
                    "not two shards of one; merging them would report a single "
                    "round generated from two different instruments."
                    % (first["__path"], s["__path"], key,
                       fm.get(key), m.get(key)))
        if s.get("arms") != first.get("arms"):
            sys.exit("%s and %s disagree on their arm definitions, despite equal "
                     "rules_cksum. Merging would keep only the first."
                     % (first["__path"], s["__path"]))

    runs = R.dedupe([r for s in snaps for r in s.get("runs", [])])

    cases_dir = cases_dir or fm.get("cases_dir") or str(R.CASES)
    cases = sorted({r["case"] for r in runs})
    models = sorted({r["model"] for r in runs})

    out = {
        "metadata": dict(fm),
        "arms": first["arms"],
        "runs": runs,
    }
    meta = out["metadata"]
    meta["generated_at"] = min(s["metadata"]["generated_at"] for s in snaps)
    meta["cases_cksum"] = R.cases_cksum(cases_dir, cases)
    meta["cases_dir"] = cases_dir
    meta["models"] = models
    meta["reps"] = max(s["metadata"].get("reps") or 0 for s in snaps)
    meta["concurrency_declared"] = max(
        [concurrency.declared(s) for s in snaps] + [len(snaps)])
    # Carried runs belong to the pass that generated them, so they are dropped
    # from the sweep here for the same reason run.py drops them at write time:
    # charging a carry source's regime to the carrying round is the specific
    # misreading carried_runs() exists to prevent.
    meta["max_runs_in_flight"] = concurrency.snapshot_max_in_flight(
        runs, concurrency.carried_runs(out))
    meta["shards"] = [{
        "shard": Path(s["__path"]).stem,
        "path": s["__path"],
        "generated_at": s["metadata"]["generated_at"],
        "claude_cli_version": s["metadata"].get("claude_cli_version"),
        "cases_cksum": s["metadata"].get("cases_cksum"),
        "models": s["metadata"].get("models"),
        # A round that is resumed after an outage finishes at whatever commit
        # the checkout is on by then, which is not the one the top-level stamp
        # inherits from the first shard. rules_cksum and cases_cksum are
        # checked equal above, so the span cannot have moved the instrument -
        # but a reader comparing rounds should see it rather than deduce it.
        "git_commit": s["metadata"].get("git_commit"),
        "usable_runs": len(R.usable(s.get("runs", []))),
    } for s in snaps]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shards", nargs="+", help="the shard snapshots to merge")
    ap.add_argument("--out", required=True, help="the merged snapshot to write")
    ap.add_argument("--cases-dir", default=None,
                    help="where the cases live; defaults to the first shard's "
                         "recorded cases_dir, so a merge normally needs no flag")
    args = ap.parse_args()

    if Path(args.out) in {Path(p) for p in args.shards}:
        sys.exit("--out %s is also an input; merging a file into itself would "
                 "read a partial merge as a shard" % args.out)

    snap = merge(args.shards, args.cases_dir)
    R.save_snapshot(args.out, snap)

    runs = snap["runs"]
    usable = R.usable(runs)
    meta = snap["metadata"]
    print("wrote %s: %d usable run(s) of %d record(s), from %d shard(s)"
          % (args.out, len(usable), len(runs), len(meta["shards"])))
    print("  models: %s | cases: %d | cases_cksum %s | reps %d"
          % (", ".join(meta["models"]), len({r["case"] for r in runs}),
             meta["cases_cksum"], meta["reps"]))
    # A merged round is exactly the case #120 was filed about, so the merged
    # file says what it reconstructs to rather than waiting for the sweep.
    print("  concurrency: declared %d, timestamps reconstruct to %d in flight"
          % (meta["concurrency_declared"], meta["max_runs_in_flight"]))
    if meta["max_runs_in_flight"] > meta["concurrency_declared"]:
        print("warning: reconstructed concurrency exceeds the declaration; pass "
              "--concurrency %d to the generating run.py invocations (#120)"
              % meta["max_runs_in_flight"])
    # The shape a reader checks first, and the one the hand merge got wrong.
    expected = len({r["case"] for r in runs}) * len(meta["models"]) * meta["reps"] \
        * len({r["arm"] for r in usable})
    if len(usable) != expected:
        print("note: %d usable run(s) against %d for a full case x model x arm x "
              "rep grid. That is a round with gaps - not an error here, but the "
              "gaps are not evenly spread unless the shards say so."
              % (len(usable), expected))


if __name__ == "__main__":
    main()
