"""Regenerate every number in `../closing-recap-305.md`.

    python3 evals/results/loop/closing-recap/sweep.py

Reads every committed snapshot, de-duplicates responses by text hash - snapshots
carry arms forward, so a run can appear in several files and counting it twice
would inflate whichever arm was carried most - and prints three tables:

1. the rate by arm and threshold, over all responses;
2. the rate by arm over *structurally eligible* responses only, which is the
   denominator that makes a near-zero figure readable;
3. the hand-labelled precision, read back from `labels.json`.

It buys no generation. That is the point: the finding that killed this round
cost nothing, where rounds 67, 68 and 69 each bought several hundred runs to
refute a candidate.
"""
import collections
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "evals", "bench"))
import detector  # noqa: E402
import metrics  # noqa: E402

ARMS = ("laconic", "baseline", "terse-control", "concise-style",
        "word-compression")


def load_archive():
    seen, rows = set(), []
    pattern = os.path.join(ROOT, "evals", "snapshots", "**", "*.json")
    for f in sorted(glob.glob(pattern, recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        runs = d.get("runs")
        if not isinstance(runs, list):
            continue
        for r in runs:
            if not isinstance(r, dict) or not r.get("ok") or not r.get("text"):
                continue
            h = hashlib.sha1(r["text"].encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            rows.append({"arm": r.get("arm"), "case": r.get("case"),
                         "model": r.get("model"), "text": r["text"], "sha1": h})
    return rows


def main():
    rows = load_archive()
    print("unique responses in the archive: %d\n" % len(rows))

    print("## Rate by arm and threshold, over all responses\n")
    print("%-6s %-7s | %s" % ("ovlp", "no-ref",
                              "  ".join("%-17s" % a for a in ARMS)))
    for noref in (True, False):
        for ov in (0.25, 0.30, 0.35, 0.40, 0.50):
            hit, tot = collections.Counter(), collections.Counter()
            for r in rows:
                if r["arm"] not in ARMS:
                    continue
                tot[r["arm"]] += 1
                if detector.closing_recap(r["text"], overlap=ov,
                                          require_no_new_referents=noref):
                    hit[r["arm"]] += 1
            print("%-6.2f %-7s | %s" % (ov, noref, "  ".join(
                "%-17s" % ("%d/%d %5.2f%%" % (
                    hit[a], tot[a], 100 * hit[a] / tot[a] if tot[a] else 0))
                for a in ARMS)))

    print("\n## Rate over structurally eligible responses only\n")
    print("%-18s %8s %10s %10s %10s %14s"
          % ("arm", "n", "med words", "eligible", "elig rate", "hit|eligible"))
    for a in ARMS:
        n = e = h = 0
        words = []
        for r in rows:
            if r["arm"] != a:
                continue
            n += 1
            prose, _ = metrics.split_text(r["text"])
            words.append(len(metrics.WORD.findall(prose)))
            if detector.eligible(r["text"]):
                e += 1
                if detector.closing_recap(r["text"], overlap=0.25):
                    h += 1
        if not n:
            continue
        print("%-18s %8d %10.1f %10d %9.2f%% %14s" % (
            a, n, metrics.median(words), e, 100 * e / n,
            "%d (%.1f%%)" % (h, 100 * h / e) if e else "-"))

    path = os.path.join(HERE, "labels.json")
    if not os.path.exists(path):
        return
    labels = json.load(open(path))
    print("\n## Hand-labelled precision\n")
    print("%-10s %6s %6s %9s" % ("sample", "n", "true", "precision"))
    shapes = collections.Counter()
    for name, entries in sorted(labels["samples"].items()):
        true = sum(1 for e in entries if e["verdict"] == "recap")
        print("%-10s %6d %6d %8.0f%%"
              % (name, len(entries), true, 100 * true / len(entries)))
        for e in entries:
            if e["verdict"] != "recap":
                shapes[e["shape"]] += 1
    total = sum(len(v) for v in labels["samples"].values())
    true = sum(1 for v in labels["samples"].values() for e in v
               if e["verdict"] == "recap")
    print("%-10s %6d %6d %8.0f%%" % ("pooled", total, true, 100 * true / total))
    print("\nfalse-positive shapes:")
    for shape, n in shapes.most_common():
        print("  %-28s %3d" % (shape, n))


if __name__ == "__main__":
    main()
