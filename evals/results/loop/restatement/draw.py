#!/usr/bin/env python3
"""Draw and blind a validation sample of requested-content responses (#150).

Unstratified simple random draw, so precision AND recall are both unbiased for
whatever detector is scored against it. That is the correction unread_asks had
to make: its first batch was stratified 30 detector-positive against 30
detector-negative, which leaves precision unbiased but undercounts false
negatives by the sampling ratio, and its published 80% recall was really 48%.
There is no detector yet here, so there is nothing to stratify on even if it
were a good idea.

The frame is every stored laconic response on the four requested-content cases
- walkthrough and the three verdict-* - across every snapshot in the archive.
Round 29 established that these are the cells where the harm #150 reports would
live: the user asks in the prompt for an explanation or an evaluation, and the
answers are long enough to carry a restated claim.

THE FRAME CONTAINS DUPLICATE TEXTS AND THEY ARE COLLAPSED BY DEFAULT. The
-v2/-v3/-v4 baselines are supersets built by copying round-01-n10.json, so one
generated run appears under several snapshot names: 1,780 rows hold only 1,430
distinct responses, 19.7% duplication. Drawing from the raw rows treats one
observation as several, which inflates the effective sample and correlates the
draws. Batch 1 drew no duplicates by luck; batch 2 drew two pairs.

--allow-duplicate-texts restores the raw frame, and it exists for exactly one
reason: batches 1 and 2 were drawn before this was noticed, and their committed
key.json files have to stay reproducible. Do not use it for a new draw.

usage: python3 draw.py [--n 60] [--seed 150] [--exclude <key.json> ...]
"""
import argparse
import glob
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CASES = ("walkthrough", "verdict-experiment", "verdict-rollout",
         "verdict-schema")


def frame():
    """Every usable laconic response on the four cases, with its provenance."""
    out = []
    for path in sorted(glob.glob(str(ROOT / "evals/snapshots/loop/*.json"))
                       + sorted(glob.glob(str(ROOT / "evals/snapshots/*.json")))):
        name = Path(path).stem
        if "judgment" in name or "preference" in name or name == "cell-rates":
            continue
        try:
            d = json.loads(Path(path).read_text())
        except Exception:
            continue
        runs = d.get("runs")
        if not isinstance(runs, list):
            continue
        ck = d.get("metadata", {}).get("rules_cksum")
        for r in runs:
            if (r.get("ok") and r.get("arm") == "laconic"
                    and r.get("case") in CASES and (r.get("text") or "").strip()):
                out.append({"snap": name, "case": r["case"], "model": r["model"],
                            "rep": r["rep"], "rules_cksum": ck})
    # Sorted so the draw is a function of (frame, seed) and nothing else.
    out.sort(key=lambda k: (k["snap"], k["case"], k["model"], k["rep"]))
    return out


def distinct(pool, seen_text):
    """One row per distinct response text, keeping the first in sort order.

    Deterministic because the pool is already sorted, so which copy survives is
    a function of the frame rather than of dict iteration order.
    """
    out, seen = [], set()
    for k in pool:
        t = seen_text(k)
        if t is None or t in seen:
            continue
        seen.add(t)
        out.append(k)
    return out


def text_of(k):
    for sub in ("evals/snapshots/loop", "evals/snapshots"):
        p = ROOT / sub / ("%s.json" % k["snap"])
        if p.exists():
            d = json.loads(p.read_text())
            hit = [r for r in d["runs"]
                   if r["case"] == k["case"] and r["rep"] == k["rep"]
                   and r["arm"] == "laconic" and r["model"] == k["model"]]
            if hit:
                return (hit[0].get("text") or "").strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=150)
    ap.add_argument("--prefix", default="R")
    ap.add_argument("--exclude", action="append", default=[],
                    help="a key.json whose draws must not be redrawn")
    ap.add_argument("--out", default=str(Path(__file__).parent))
    ap.add_argument("--allow-duplicate-texts", action="store_true",
                    help="draw from the raw rows, duplicates and all. Only for "
                         "reproducing batches 1 and 2, which were drawn before "
                         "the duplication was noticed")
    args = ap.parse_args()

    pool = frame()
    raw = len(pool)
    if not args.allow_duplicate_texts:
        pool = distinct(pool, text_of)
    seen = set()
    for path in args.exclude:
        for k in json.loads(Path(path).read_text()):
            seen.add((k["snap"], k["case"], k["model"], k["rep"]))
    pool = [k for k in pool
            if (k["snap"], k["case"], k["model"], k["rep"]) not in seen]
    if len(pool) < args.n:
        sys.exit("frame has %d responses, need %d" % (len(pool), args.n))

    picked = random.Random(args.seed).sample(pool, args.n)
    picked.sort(key=lambda k: (k["snap"], k["case"], k["model"], k["rep"]))
    key = [dict(id="%s%02d" % (args.prefix, i + 1), **k)
           for i, k in enumerate(picked)]

    out = Path(args.out)
    (out / "key.json").write_text(json.dumps(key, indent=1) + "\n")
    blind = []
    for k in key:
        d = json.loads((ROOT / "evals/snapshots/loop" / ("%s.json" % k["snap"])).read_text()
                       if (ROOT / "evals/snapshots/loop" / ("%s.json" % k["snap"])).exists()
                       else (ROOT / "evals/snapshots" / ("%s.json" % k["snap"])).read_text())
        hit = [r for r in d["runs"]
               if r["case"] == k["case"] and r["rep"] == k["rep"]
               and r["arm"] == "laconic" and r["model"] == k["model"]]
        if not hit:
            sys.exit("no run for %s" % k["id"])
        blind.append("\n\n===== %s | case: %s =====\n%s\n"
                     % (k["id"], k["case"], hit[0]["text"].strip()))
    (out / "blind.md").write_text("".join(blind))
    print("frame %d rows -> %d after excludes%s; drew %d at seed %d"
          % (raw, len(pool),
             "" if args.allow_duplicate_texts else " and text-deduplication",
             args.n, args.seed))
    print("wrote %s/key.json and %s/blind.md" % (out, out))


if __name__ == "__main__":
    main()
