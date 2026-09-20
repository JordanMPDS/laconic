"""Draw the precision sample the labels in `labels.json` were read from.

    python3 evals/results/loop/closed-question/draw.py        # print the 30 hits
    python3 evals/results/loop/closed-question/draw.py --shas # ids only

The sample is drawn from the firing responses of the `laconic` arm at
[#136]'s own threshold, seeded so the draw is reproducible, and keyed by the
first twelve hex of the response's sha1 so a label survives a re-sweep whatever
order the snapshots are globbed in.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detector  # noqa: E402
import sweep  # noqa: E402

SEED = 136
N = 30


def sample(rows, seed=SEED, n=N, arm="laconic", limit=detector.LIMIT):
    hits = sorted((r for r in rows if r["arm"] == arm and r["words"] > limit),
                  key=lambda r: r["sha"])
    return random.Random(seed).sample(hits, min(n, len(hits)))


def main():
    rows = sweep.load_archive(sweep.closed_cases())
    hits = sample(rows)
    if "--shas" in sys.argv:
        print(json.dumps([{k: h[k] for k in ("sha", "case", "model", "words")}
                          for h in hits], indent=1))
        return
    for i, h in enumerate(hits, 1):
        print("=" * 72)
        print("#%d  %s  %s  %s  %d words" % (i, h["sha"], h["case"], h["model"], h["words"]))
        print(h["text"])


if __name__ == "__main__":
    main()
