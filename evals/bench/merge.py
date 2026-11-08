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
- **Shards that disagree on safe mode**, an absent field read as the safe
  mode every snapshot below round 61 ran under. A round split by arm with the
  enforcement arms outside safe mode and the controls inside it confounds the
  mechanism with the regime (#441).
- **Shards holding multi-turn runs under two delivery modes**, decided on the
  per-run stamps rather than the declarations, so a shard with no multi-turn
  work left, which declares nothing, merges with either (#441).
- **Shards that disagree on `reminder_cksum` or `effort`**, which
  `rules_cksum` covers neither of. A shard older than the field merges with
  either, and the merged file keeps the value a shard recorded (#522).

What it recomputes rather than copies, because a merged file describes a round
no single shard saw:

- `cases_cksum`, over the union of the cases actually present. Shards that split
  22 cases into two halves legitimately carry three different checksums, so
  copying any one of them would stamp the merged file with a subset's identity.
- `max_runs_in_flight`, by the same sweep run.py stamps at write time (#120).
- `concurrency_declared`, as the maximum any shard declared and never less than
  the number of shards, so the merged file cannot claim a lower concurrency than
  the merge itself demonstrates.
- `turn_delivery`, `cli_versions` and `cli_versions_per_run`, from every
  shard's runs rather than the first shard's metadata (#441).
- `reps` and `rep_offset`, over the union of every shard's declared rep range
  and the reps its records hold, rather than the largest declaration: shards
  split by `--rep-offset` each declare one shard's size (#440).

What it reports rather than refuses: a usable run discarded because another
shard holds a different run under the same key. That is two shards started at
the same `--rep-offset`, and the merged file would otherwise read as complete
with one shard's work gone (#440). Each shard entry counts its own losses.

`metadata.shards` records where every run came from, so the merged file carries
its own provenance instead of leaving it to be reconstructed.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import concurrency  # noqa: E402
import run as R  # noqa: E402


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
        for key, absent in (("rules_cksum", None), ("laconic_level", None),
                            ("safe_mode", True)):
            if m.get(key, absent) != fm.get(key, absent):
                sys.exit(
                    "%s and %s disagree on %s (%s vs %s). These are two rounds, "
                    "not two shards of one; merging them would report a single "
                    "round generated from two different instruments."
                    % (first["__path"], s["__path"], key,
                       fm.get(key, absent), m.get(key, absent)))
        if s.get("arms") != first.get("arms"):
            sys.exit("%s and %s disagree on their arm definitions, despite equal "
                     "rules_cksum. Merging would keep only the first."
                     % (first["__path"], s["__path"]))

    # Absent on a shard older than the field rather than defaulted, because
    # nothing records what such a file ran under, so it merges with either.
    recorded = {}
    for key in ("reminder_cksum", "effort"):
        held = sorted({(s["metadata"].get(key), s["__path"]) for s in snaps
                       if s["metadata"].get(key) is not None})
        if len({v for v, _ in held}) > 1:
            sys.exit("the shards disagree on %s (%s). These are two rounds, not "
                     "two shards of one; merging them would report a single "
                     "round generated from two different instruments (#522)."
                     % (key, "; ".join("%s: %s" % (p, v) for v, p in held)))
        if held:
            recorded[key] = held[0][0]

    held = [(s["__path"], R.delivery_modes(s.get("runs", []))) for s in snaps]
    modes = sorted({m for _, v in held for m in v})
    if len(modes) > 1:
        sys.exit("the shards hold multi-turn runs under different delivery "
                 "modes (%s). One file would hold two treatments under one "
                 "label." % "; ".join("%s: %s" % (p, "/".join(v))
                                      for p, v in held if v))

    every = [(s["__path"], r) for s in snaps for r in s.get("runs", [])]
    runs = R.dedupe([r for _, r in every])
    # Count the usable records dedupe dropped for a different record under the
    # same key (#440). An identical copy is no loss: two shards carrying one
    # control arm from one source hold the same records, and so does a merge
    # that names a shard beside a file already merged from it.
    kept = {R.run_key(r.get("case"), r.get("arm"), r.get("model"), r.get("rep")): r
            for r in runs}
    discarded = {}
    for path, r in every:
        k = kept[R.run_key(r.get("case"), r.get("arm"), r.get("model"), r.get("rep"))]
        if r.get("ok") and k is not r and k != r:
            discarded[path] = discarded.get(path, 0) + 1

    cases_dir = cases_dir or fm.get("cases_dir") or str(R.CASES)
    # The design, from the shards that declare one (#285). Declared beats
    # observed because a cell whose every rep failed is present in the design
    # and absent from the runs, and dropping it would take its case out of
    # cases_cksum and out of the completeness check below - the two places a
    # reader looks to find out that it failed. A shard written before the
    # field existed has no declaration, so the merge falls back to what the
    # records show, over every record rather than the usable ones, which is
    # the closest an old file can come to naming a cell that produced nothing.
    declared = [s["metadata"].get("cells") for s in snaps]
    if all(d is not None for d in declared):
        cells = sorted({(c["case"], c["model"]) for d in declared for c in d})
    else:
        cells = sorted({(r["case"], r["model"]) for r in runs})
    cases = sorted({c for c, _ in cells})
    models = sorted({m for _, m in cells})

    out = {
        "metadata": dict(fm),
        "arms": first["arms"],
        "runs": runs,
    }
    meta = out["metadata"]
    meta.update(recorded)
    meta["generated_at"] = min(s["metadata"]["generated_at"] for s in snaps)
    meta["cases_cksum"] = R.cases_cksum(cases_dir, cases)
    meta["cases_dir"] = cases_dir
    meta["cells"] = R.cells_of(cells)
    meta["models"] = models
    ids = set()
    for s in snaps:
        ids |= R.rep_ids(s, concurrency.carried_runs(s))
    meta["reps"] = len(ids)
    meta["rep_offset"] = min(ids) if ids else 0
    if modes:
        meta["turn_delivery"] = modes[0]
    # A failed probe's "unknown" is not a release, as in run.py (#445).
    versions = sorted({r["claude_cli_version"] for r in runs
                       if r.get("claude_cli_version")
                       and r["claude_cli_version"] != "unknown"})
    if versions:
        meta["cli_versions"] = versions
    meta["cli_versions_per_run"] = all(
        s["metadata"].get("cli_versions_per_run") for s in snaps)
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
        "safe_mode": s["metadata"].get("safe_mode"),
        "turn_delivery": s["metadata"].get("turn_delivery"),
        "rep_offset": s["metadata"].get("rep_offset"),
        "reps": s["metadata"].get("reps"),
        "usable_runs": len(R.usable(s.get("runs", []))),
        "discarded_runs": discarded.get(s["__path"], 0),
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
    print("  models: %s | cases: %d | cells: %d | cases_cksum %s | reps %d"
          % (", ".join(meta["models"]), len({c["case"] for c in meta["cells"]}),
             len(meta["cells"]), meta["cases_cksum"], meta["reps"]))
    # A merged round is exactly the case #120 was filed about, so the merged
    # file says what it reconstructs to rather than waiting for the sweep.
    print("  concurrency: declared %d, timestamps reconstruct to %d in flight"
          % (meta["concurrency_declared"], meta["max_runs_in_flight"]))
    if meta["max_runs_in_flight"] > meta["concurrency_declared"]:
        print("warning: reconstructed concurrency exceeds the declaration; pass "
              "--concurrency %d to the generating run.py invocations (#120)"
              % meta["max_runs_in_flight"])
    lost = [s for s in meta["shards"] if s["discarded_runs"]]
    if lost:
        print("warning: %d usable run(s) discarded, each because another shard "
              "holds a different run under the same (case, arm, model, rep) "
              "key: %s. Shards started at the same --rep-offset generate the "
              "same keys and a merge keeps one record per key, so the merged "
              "file holds one shard's work where both were bought. Regenerate "
              "the lost shard at an offset of its own (#440)."
              % (sum(s["discarded_runs"] for s in lost),
                 "; ".join("%s lost %d" % (s["path"], s["discarded_runs"])
                           for s in lost)))
    # The shape a reader checks first, and the one the hand merge got wrong.
    # Counted over the cells the round declared rather than over the case-by-
    # model rectangle: a ragged design is complete at three cells where the
    # rectangle wants four, and reporting that as a gap every time would teach
    # a reader to ignore the line that exists to catch an under-merge (#285).
    expected = len(meta["cells"]) * meta["reps"] * len({r["arm"] for r in usable})
    if len(usable) != expected:
        print("note: %d usable run(s) against %d for the %d declared cell(s) at "
              "%d rep(s) and %d arm(s). That is a round with gaps - not an error "
              "here, but the gaps are not evenly spread unless the shards say so."
              % (len(usable), expected, len(meta["cells"]), meta["reps"],
                 len({r["arm"] for r in usable})))


if __name__ == "__main__":
    main()
