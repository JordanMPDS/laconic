#!/usr/bin/env python3
"""#146: what a FATAL unread_asks would reject when nothing changed.

The archive null published in `../unread-asks.md` measures false ACCEPTS: how
often a pair of rounds at identical rules text shows the counter FALLING at
alpha. Making the counter fatal asks the opposite question - how often it RISES
far enough to reject a round whose rules text did not change - and a fatal
counter that fires on noise costs a round every time it does.

Every pair scored here is a null pair by construction: same `rules_cksum`, same
set of case/model cells. Any rejection is therefore a false one. Stored
snapshots only, no model calls.

Four candidate rules are scored, because "make it fatal" is not one design:

  bare        the round-wide count rose at all. This is what adding the key to
              report.FATAL today would do, since the counter has no per-cell
              block for the screens to read.
  per-cell    any cell rose, screened by _sample_covers exactly as the four
              fatal counters are (#133).
  screened    the round-wide count rose AND the rise reaches alpha on the
              conditional exposure, the shape violations_total uses (#103).
  both        per-cell and screened together.

The four existing fatal counters are scored on the same pairs, as the reference
the loop already lives with.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import report  # noqa: E402
import detector_v2  # noqa: E402

SNAP = ROOT / "evals" / "snapshots" / "loop"
CASES = ROOT / "evals" / "cases"
ALPHA = report.NOISE["alpha"]

EXCLUDE = {
    "round-01-n10", "round-01-n10-v2", "round-01-n10-v3",
    "round-21", "round-22",
    "round-25-arbitration", "round-10-replication",
}
V1 = report.ASKS_BACK
DETECTORS = {"v1": lambda t: bool(V1.search(t)), "v2": detector_v2.asks_back}


def load(model=None):
    """Per-round cells: unread exposure and hands-back count, both detectors."""
    out = []
    for p in sorted(SNAP.glob("round-*.json")):
        name = p.stem
        if name.endswith(("-judgments", "-preferences")) or name in EXCLUDE:
            continue
        if "holdout" in name:
            continue
        d = json.loads(p.read_text())
        if "runs" not in d:
            continue
        cells = defaultdict(lambda: {"runs": 0, "unread": 0, "v1": 0, "v2": 0})
        for r in d["runs"]:
            if r.get("arm") != "laconic" or not r.get("ok"):
                continue
            if model and r.get("model") != model:
                continue
            if not (CASES / r["case"] / "fixture").is_dir():
                continue
            c = (r["case"], r["model"])
            cells[c]["runs"] += 1
            if r.get("num_turns") != 1:
                continue
            cells[c]["unread"] += 1
            for k, fn in DETECTORS.items():
                cells[c][k] += bool(fn(r.get("text", "")))
        if not cells:
            continue
        jp = SNAP / (name + "-judgments.json")
        judg = json.loads(jp.read_text())["judgments"] if jp.exists() else None
        out.append({"name": name, "cksum": d["metadata"].get("rules_cksum"),
                    "date": d["metadata"].get("generated_at", "")[:10],
                    "cells": dict(cells), "path": p, "judgments": judg})
    return out


def null_pairs(rounds):
    """Ordered pairs at identical rules text, cell coverage AND reps.

    Equal reps is not fastidiousness. These rules compare counts, so a round
    with more runs than the one it is scored against rises on arithmetic; the
    loop already requires a round to match its baseline's reps for exactly that
    reason, and a null that ignores it measures sample size instead of noise.
    """
    groups = defaultdict(list)
    for r in rounds:
        key = (r["cksum"],
               frozenset((c, v["runs"]) for c, v in r["cells"].items()))
        groups[key].append(r)
    pairs = []
    for rs in groups.values():
        for a in rs:
            for b in rs:
                if a is not b:
                    pairs.append((a, b))
    return pairs


def totals(r, det):
    return (sum(c[det] for c in r["cells"].values()),
            sum(c["unread"] for c in r["cells"].values()))


def rules_fired(prev, cur, det):
    """Which candidate fatal rules reject this null pair."""
    a, ea = totals(prev, det)
    b, eb = totals(cur, det)
    bare = b > a
    risen = [k for k in cur["cells"]
             if cur["cells"][k][det] > prev["cells"].get(k, {}).get(det, 0)]
    per_cell = [
        k for k in risen
        if not report._sample_covers(cur["cells"][k][det],
                                     cur["cells"][k]["unread"],
                                     prev["cells"][k][det],
                                     prev["cells"][k]["unread"], ALPHA)]
    # _count_p is the one-sided FALL, so the rise is the mirrored call.
    p_rise = report._count_p(b, a, eb, ea)
    screened = bare and p_rise is not None and p_rise < ALPHA
    return {"bare": bare, "per-cell": bool(per_cell),
            "screened": screened, "both": bool(per_cell) and screened}


def existing_fatal(prev, cur, cell_rates):
    """Do the four counters the loop already treats as fatal reject this pair?"""
    if prev["judgments"] is None or cur["judgments"] is None:
        return None
    sp = report.round_summary(json.loads(prev["path"].read_text()),
                              prev["judgments"])
    sc = report.round_summary(json.loads(cur["path"].read_text()),
                              cur["judgments"])
    _, why = report.accept_verdict(sp, sc, "output_tokens",
                                   cell_rates=cell_rates)
    return [r for r in why if r.startswith("REJECT: ")
            and " lost (" in r]


def report_rates(label, rounds):
    pairs = null_pairs(rounds)
    print("\n=== %s: %d null pairs over %d rounds ==="
          % (label, len(pairs), len(rounds)))
    for det in DETECTORS:
        fired = defaultdict(list)
        for prev, cur in pairs:
            for rule, hit in rules_fired(prev, cur, det).items():
                if hit:
                    fired[rule].append((prev["name"], cur["name"]))
        print("  %s" % det)
        for rule in ("bare", "per-cell", "screened", "both"):
            n = len(fired[rule])
            print("    %-9s %3d of %3d  %5.1f%%"
                  % (rule, n, len(pairs), 100 * n / len(pairs) if pairs else 0))
        for prev, cur in fired["screened"]:
            print("      screened rejection: %s -> %s" % (prev, cur))
    return pairs


# The contrasts the loop has already ruled on, at equal reps. A false-rejection
# rate says what a rule costs on noise; these say what it would have done to
# rounds whose verdicts are already published.
CONTRASTS = [
    ("round 26, the licence now in master", "round-26-control",
     "round-26-licence", "accepted"),
    ("round 26 step 8, three cases", "round-26-step8-control",
     "round-26-step8-licence", "accepted"),
    ("round 25, the same licence", "round-25-control", "round-25-licence",
     "rejected on quality"),
    ("round 27's edit", "round-27-control", "round-27-edit",
     "rejected on tokens"),
    ("round 23's edit", "round-23-matched-master", "round-23-matched-edit",
     "rejected on tokens"),
    ("round 20's text against round 19", "round-19", "round-20",
     "rejected on quality"),
]


def consequences(rounds):
    by = {r["name"]: r for r in rounds}
    print("\n=== what the screened rule would have done to judged rounds ===")
    for label, prev, cur, verdict in CONTRASTS:
        if prev not in by or cur not in by:
            print("  %-38s (snapshots missing)" % label)
            continue
        a, ea = totals(by[prev], "v2")
        b, eb = totals(by[cur], "v2")
        p_rise = report._count_p(b, a, eb, ea)   # the mirrored call is the rise
        fires = b > a and p_rise is not None and p_rise < ALPHA
        print("  %-38s %2d/%-3d -> %2d/%-3d  rise p = %-9.3g %s (loop: %s)"
              % (label, a, ea, b, eb, p_rise,
                 "REJECTS" if fires else "silent", verdict))


if __name__ == "__main__":
    rates = report.load_cell_rates()
    for label, model in (("round-wide, both models", None), ("sonnet only", "sonnet")):
        pairs = report_rates(label, load(model))
        if model:
            continue
        hits = 0
        scored = 0
        for prev, cur in pairs:
            got = existing_fatal(prev, cur, rates)
            if got is None:
                continue
            scored += 1
            hits += bool(got)
        print("  reference: the four existing fatal counters reject %d of %d "
              "scoreable null pairs (%.1f%%), before arbitration"
              % (hits, scored, 100 * hits / scored if scored else 0))
        consequences(load("sonnet"))
