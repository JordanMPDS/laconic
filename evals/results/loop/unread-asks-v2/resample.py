#!/usr/bin/env python3
"""Regenerate the blinded sample the detector validation was labelled from.

key.json records which response each id came from; this rebuilds the blind
file from the committed snapshots so the labels can be re-checked. The seed
and snapshot list are recorded here rather than in prose so a re-run is exact.
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "evals" / "bench"))

key = json.load(open(Path(__file__).parent / "key.json"))
snaps = {}
for k in key:
    snaps.setdefault(k["snap"], None)
for name in snaps:
    snaps[name] = json.load(open(ROOT / ("evals/snapshots/loop/%s.json" % name)))

out = []
for k in key:
    runs = snaps[k["snap"]]["runs"]
    hit = [r for r in runs if r["case"] == k["case"] and r["rep"] == k["rep"]
           and r["arm"] == "laconic" and r["model"] == "sonnet"]
    if not hit:
        sys.exit("no run for %s in %s" % (k["id"], k["snap"]))
    out.append("\n\n===== %s | case: %s =====\n%s\n"
               % (k["id"], k["case"], hit[0]["text"].strip()))
dest = Path(__file__).parent / "blind.md"
dest.write_text("".join(out))
print("wrote %s (%d responses)" % (dest, len(out)))
