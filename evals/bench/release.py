#!/usr/bin/env python3
"""Which claude releases generated a snapshot, and were the arms balanced?

A round is bought from the `claude` CLI, and the CLI ships several times a day.
Round 57 ran for fourteen hours and the binary advanced three patch releases
underneath it, which is not an unusual round and not an unusual week. So a
snapshot spanning a release is the normal case rather than the exceptional one,
and the question worth asking is not "did it span" but "does the span
confound anything".

Two failures, and they are different:

- **The labels are wrong.** Until #272 `run.py` read `claude --version` once at
  startup and copied the answer onto every run, so a pass that outlived a
  release recorded the release it started on. `claude` is a symlink into a
  versioned payload and an upgrade re-points it, so the next generation ran the
  new binary under the old label. 540 of round 57's 1,440 runs name a release
  they did not run on, and the round stratified on exactly that field. A
  snapshot whose metadata does not say `cli_versions_per_run` holds
  per-invocation labels and may not be stratified on at all.
- **The arms are imbalanced.** Simultaneity equalises the calendar across arms;
  it does not equalise the instrument, and it stops equalising even the calendar
  once the arms drift apart in pace, which they do because a usage limit hits
  the slowest arm hardest. Round 57's three arms split 225/246, 276/204 and
  254/226 across their boundary, so the release is correlated with the arm and a
  pooled contrast is confounded by it.

The second is what this tool tests. Every group is checked against the pooled
rest on every release, two-sided Fisher exact, Bonferroni corrected over the
tests performed - exact rather than chi-square because a release that shipped
mid-pass can leave a group with a handful of runs on one side.

A group is one arm of one snapshot. That covers both shapes a round comes in:
several arms inside one file, and one arm per file, which is what a round
comparing two rules texts is forced into because `rules_cksum` is resolved once
per invocation.

    python3 evals/bench/release.py                        # sweep the archive
    python3 evals/bench/release.py a.json b.json c.json    # one round's arms
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "evals" / "snapshots"

sys.path.insert(0, str(Path(__file__).resolve().parent))
# The same two-sided exact test the subagent report uses. Imported rather than
# copied: a second implementation is a second thing to keep correct.
from subagent import fisher_exact  # noqa: E402

ALPHA = 0.05


def version(run):
    """The release stamp, normalised: `2.1.263 (Claude Code)` is `2.1.263`."""
    v = run.get("claude_cli_version")
    return v.split()[0] if isinstance(v, str) and v.strip() else None


def per_run_stamped(snap):
    """True when every run in the file carries the release that produced it."""
    return bool((snap.get("metadata") or {}).get("cli_versions_per_run"))


def groups(snap, label):
    """{(label, arm): {release: n}} over the runs that produced text."""
    out = defaultdict(lambda: defaultdict(int))
    for r in snap.get("runs", []):
        if not isinstance(r, dict) or not r.get("ok"):
            continue
        v = version(r)
        if v is None:
            continue
        out[(label, r.get("arm") or "-")][v] += 1
    return out


def imbalance(counts):
    """[(group, release, k, n, p, significant)] for every group-release cell.

    Each cell is one group's share of one release against the pooled share of
    every other group, so a group that is over-represented on a release names
    itself. Corrected over `groups * (releases - 1)` rather than over the rows
    printed: a group's shares sum to its whole, so across two releases both of
    its rows are one test read from either side and reporting them as two would
    pay for the same comparison twice. That is not a detail. Round 57's split
    over two releases reads p = 0.0095 for its most skewed arm, which clears a
    correction over 3 tests and does not clear one over 6, so counting the
    printed rows would have let the round that motivated this tool through.
    """
    releases = sorted({v for c in counts.values() for v in c})
    if len(releases) < 2 or len(counts) < 2:
        return []
    tests = len(counts) * (len(releases) - 1)
    rows = []
    for g in sorted(counts):
        n = sum(counts[g].values())
        for v in releases:
            k = counts[g].get(v, 0)
            other_k = sum(c.get(v, 0) for gg, c in counts.items() if gg != g)
            other_n = sum(sum(c.values()) for gg, c in counts.items() if gg != g)
            p = fisher_exact(k, n - k, other_k, other_n - other_k)
            rows.append((g, v, k, n, p, p * tests < ALPHA))
    return rows


def audit(paths):
    """(counts, per_snapshot) for the snapshots that hold usable runs."""
    counts, meta = {}, []
    for p in paths:
        try:
            snap = json.loads(Path(p).read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(snap, dict) or not isinstance(snap.get("runs"), list):
            continue
        rel = os.path.relpath(p, str(ROOT))
        g = groups(snap, rel)
        if not g:
            continue
        counts.update(g)
        seen = sorted({v for c in g.values() for v in c})
        meta.append({"path": rel, "releases": seen,
                     "per_run": per_run_stamped(snap),
                     "n": sum(sum(c.values()) for c in g.values())})
    return counts, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("snapshots", nargs="*",
                    help="snapshot files; default every file under evals/snapshots")
    ap.add_argument("--warn", action="store_true",
                    help="report and exit 0 even when a span is unreadable or "
                         "the arms are imbalanced across it")
    args = ap.parse_args()

    paths = args.snapshots or sorted(
        glob.glob(str(SNAPSHOTS / "**" / "*.json"), recursive=True))
    counts, meta = audit(paths)

    print("%-52s %5s  %-9s %s" % ("snapshot", "runs", "stamps", "releases"))
    unreadable = []
    for m in meta:
        spans = len(m["releases"]) > 1
        # A file that never spanned a release cannot be mislabelled by the
        # per-invocation stamp, whatever its metadata says, so it is not
        # reported as a problem - the stamp it holds is the one that ran.
        if spans and not m["per_run"]:
            unreadable.append(m)
        print("%-52s %5d  %-9s %s%s"
              % (m["path"], m["n"], "per-run" if m["per_run"] else "per-pass",
                 ", ".join(m["releases"]),
                 "   <- labels unreadable" if spans and not m["per_run"] else ""))

    # Only when the caller named the files. Balance is a question about the arms
    # of one round, and the sweep holds every round the archive has: pooling
    # them into one contingency table asks whether round 12 is over-represented
    # on a release that shipped after it, which is arithmetic about nothing.
    rows = imbalance(counts) if args.snapshots else []
    bad = [r for r in rows if r[5]]
    if rows:
        print("\n%-52s %-9s %14s %10s" % ("group", "release", "share", "p"))
        for (path, arm), v, k, n, p, sig in rows:
            print("%-52s %-9s %5d/%-5d %4.1f%% %10.4f%s"
                  % ("%s [%s]" % (path, arm), v, k, n, 100.0 * k / n, p,
                     "  <- imbalanced" if sig else ""))

    if unreadable:
        print("\n%d snapshot(s) span more than one claude release and were "
              "stamped once per pass rather than once per run, so which release "
              "produced which run is not recoverable from the file. Do not "
              "stratify on claude_cli_version in them (#272)." % len(unreadable))
    if bad:
        print("\n%d group-release cell(s) are imbalanced at Bonferroni-corrected "
              "alpha %.2f. The release is correlated with the arm, so a pooled "
              "contrast across these groups is confounded by the instrument and "
              "has to be stratified." % (len(bad), ALPHA))
    if not unreadable and not bad:
        print("\nno unreadable span, and no arm is imbalanced across a release")
    return 0 if (args.warn or not (unreadable or bad)) else 1


if __name__ == "__main__":
    sys.exit(main())
