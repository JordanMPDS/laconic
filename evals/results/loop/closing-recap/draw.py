"""Draw the hand-labelling samples, reproducibly.

    python3 evals/results/loop/closing-recap/draw.py loose   # overlap 0.25, no referent gate
    python3 evals/results/loop/closing-recap/draw.py strict   # overlap 0.40, referent gate on

Prints each drawn hit as its opening and closing paragraph, which is what a
labeller reads. The draw is seeded, and the archive iteration order is fixed by
`sweep.load_archive`, so re-running reproduces `labels.json` entry for entry -
`labels.json` stores the sha1 of each response so a drift in either is caught
rather than silently relabelled.

The sample size is 30 on the setting whose rate the write-up quotes and 20 on
the stricter one, following the [#155] convention: 30 hits drawn at random from
the archive and hand-read is what `metrics.closing_offers` cleared at 30/30 and
what the restatement detector failed at 55.3%.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "bench"))
import detector  # noqa: E402
import metrics  # noqa: E402
import sweep  # noqa: E402

SEED = 71
SETTINGS = {
    "loose": {"overlap": 0.25, "require_no_new_referents": False, "k": 30},
    "strict": {"overlap": 0.40, "require_no_new_referents": True, "k": 20},
}


def draw(name):
    cfg = dict(SETTINGS[name])
    k = cfg.pop("k")
    hits = []
    for r in sweep.load_archive():
        last = detector.closing_recap(r["text"], **cfg)
        if not last:
            continue
        _, src = metrics.split_text(r["text"])
        paras = metrics._paragraph_prose(src)
        hits.append({"sha1": r["sha1"], "arm": r["arm"], "case": r["case"],
                     "model": r["model"], "opening": paras[0], "closing": last})
    total = len(hits)
    random.Random(SEED).shuffle(hits)
    return total, hits[:k]


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "loose"
    total, sample = draw(name)
    print("# %s: %d hits in the archive, %d drawn at seed %d\n"
          % (name, total, len(sample), SEED))
    for i, h in enumerate(sample, 1):
        print("===== %s %d  [%s / %s / %s]  %s" %
              (name, i, h["arm"], h["case"], h["model"], h["sha1"][:12]))
        print("OPENING: %s" % h["opening"][:400])
        print("CLOSING: %s\n" % h["closing"][:400])
    if "--json" in sys.argv:
        json.dump(sample, open("/dev/stdout", "w"), indent=2)
