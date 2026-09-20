"""Regenerate every number in `../closed-question-136.md`.

    python3 evals/results/loop/closed-question/sweep.py

Reads every committed snapshot, de-duplicates responses by text hash - snapshots
carry arms forward, so a run can appear in several files and counting it twice
would inflate whichever arm was carried most - and prints five tables:

1. which cases in `evals/cases/` carry a closed confirmation question at all,
   under both settings, because the population is discovered rather than listed;
2. the fire rate by arm, over the runs on those cases;
3. the whole threshold curve from 20 to 200 prose words, so the conclusion does
   not rest on [#136]'s 80;
4. the per-case laconic rate, which is where the spread lives;
5. the direction the response takes on the premise - accepted, denied, or
   neither - which is the diagnosis, and the hand-labelled precision read back
   from `labels.json`.

It buys no generation. Every figure comes off `text` and `num_turns` on runs
already stored, the way `../closing-recap/sweep.py` does.
"""
import collections
import glob
import hashlib
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "evals", "bench"))
import detector  # noqa: E402

CASES = os.path.join(ROOT, "evals", "cases")
ARMS = ("laconic", "baseline", "terse-control", "concise-style",
        "word-compression")
CURVE = (20, 30, 40, 60, 80, 100, 120, 160, 200)

# The response's direction on the premise the question asserts. Opening word
# only: a response that accepts and then qualifies opens with the acceptance,
# which is what [#136] describes and what the suite's traps mostly forbid.
import re  # noqa: E402
ACCEPTS = re.compile(
    r"^\W{0,3}(yes|correct|right|that'?s right|exactly|true|confirmed|agreed)\b", re.I)
DENIES = re.compile(
    r"^\W{0,3}(no|nope|not quite|not exactly|partly|partially|almost|mostly"
    r"|sort of|yes and no|half)\b", re.I)


def closed_cases():
    """The cases whose graded turn is a closed confirmation question."""
    out = {}
    for name in sorted(os.listdir(CASES)):
        path = os.path.join(CASES, name, "prompt.md")
        if not os.path.exists(path):
            continue
        prompt = open(path).read()
        settings = [s for s in ("literal", "widened")
                    if detector.closed_question(prompt, s)]
        if settings:
            out[name] = (detector.graded_turn(prompt), settings)
    return out


def load_archive(cases):
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
            if r.get("case") not in cases:
                continue
            h = hashlib.sha1(r["text"].encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            rows.append(dict(sha=h[:12], case=r["case"], arm=r.get("arm"),
                             model=r.get("model"), rep=r.get("rep"),
                             generated_at=r.get("generated_at"),
                             words=detector.prose_words(r["text"]),
                             text=r["text"]))
    return rows


def pct(k, n):
    return "%.1f%%" % (100.0 * k / n) if n else "-"


def main():
    cases = closed_cases()
    print("## Closed-question cases in evals/cases/\n")
    print("%-18s %-16s %s" % ("case", "settings", "graded turn"))
    for name, (turn, settings) in cases.items():
        print("%-18s %-16s %s (%d words)"
              % (name, ",".join(settings), turn, len(turn.split())))
    literal = {n for n, (_, s) in cases.items() if "literal" in s}
    print("\n%d cases, %d of them under the literal 15-word cap\n"
          % (len(cases), len(literal)))

    rows = load_archive(cases)
    print("## Fire rate by arm, %d de-duplicated responses\n" % len(rows))
    print("%-16s %6s %8s %8s %8s %10s" % ("arm", "n", "median", "p90", "max", "fires"))
    by_arm = collections.defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)
    for arm in ARMS:
        rs = by_arm.get(arm)
        if not rs:
            continue
        w = sorted(x["words"] for x in rs)
        k = sum(1 for x in rs if x["words"] > detector.LIMIT)
        print("%-16s %6d %8.1f %8d %8d %10s"
              % (arm, len(rs), statistics.median(w), w[int(0.9 * (len(w) - 1))],
                 w[-1], "%d (%s)" % (k, pct(k, len(rs)))))

    print("\n## The threshold curve, prose words\n")
    print("%8s %10s %10s" % ("cutoff", "laconic", "baseline"))
    for c in CURVE:
        lac, base = by_arm.get("laconic", []), by_arm.get("baseline", [])
        print("%8d %10s %10s"
              % (c, pct(sum(1 for x in lac if x["words"] > c), len(lac)),
                 pct(sum(1 for x in base if x["words"] > c), len(base))))

    print("\n## Per-case laconic rate at %d words\n" % detector.LIMIT)
    print("%-18s %6s %8s %10s" % ("case", "n", "median", "fires"))
    for name in cases:
        rs = [r for r in by_arm.get("laconic", []) if r["case"] == name]
        if not rs:
            continue
        k = sum(1 for r in rs if r["words"] > detector.LIMIT)
        print("%-18s %6d %8.1f %10s"
              % (name, len(rs), statistics.median([r["words"] for r in rs]),
                 "%d (%s)" % (k, pct(k, len(rs)))))

    print("\n## Direction on the premise\n")
    print("%-16s %6s %10s %10s %10s" % ("arm", "n", "accepts", "denies", "neither"))
    for arm in ARMS:
        rs = by_arm.get(arm)
        if not rs:
            continue
        a = [r for r in rs if ACCEPTS.match(r["text"].strip())]
        d = [r for r in rs if DENIES.match(r["text"].strip())]
        n = len(rs) - len(a) - len(d)
        print("%-16s %6d %10s %10s %10s"
              % (arm, len(rs), "%d (%s)" % (len(a), pct(len(a), len(rs))),
                 "%d (%s)" % (len(d), pct(len(d), len(rs))), "%d (%s)" % (n, pct(n, len(rs)))))
    acc = [r for r in by_arm.get("laconic", []) if ACCEPTS.match(r["text"].strip())]
    print("\nlaconic responses that accept the premise and fire: %d of %d"
          % (sum(1 for r in acc if r["words"] > detector.LIMIT), len(acc)))

    path = os.path.join(HERE, "labels.json")
    if os.path.exists(path):
        labels = json.load(open(path))
        rec = labels["labels"]
        counts = collections.Counter(x["label"] for x in rec)
        print("\n## Hand-labelled precision, %d hits at seed %d\n"
              % (len(rec), labels["seed"]))
        print(labels["criterion"])
        print()
        for label in ("violation", "borderline", "not"):
            print("%-12s %d" % (label, counts[label]))
        print("\nstrict precision  %s" % pct(counts["violation"], len(rec)))
        print("with borderlines  %s"
              % pct(counts["violation"] + counts["borderline"], len(rec)))
        print("\n%-28s %s" % ("shape", "n"))
        for shape, k in collections.Counter(x["shape"] for x in rec).most_common():
            print("%-28s %d" % (shape, k))
        st = labels.get("stratum")
        if st:
            sc = collections.Counter(x["label"] for x in st["labels"])
            n = len(st["labels"])
            print("\n## The premise-accepting stratum, %d hits, all of them\n" % n)
            print(st["what"])
            print()
            for label in ("violation", "borderline", "not"):
                print("%-12s %d" % (label, sc[label]))
            print("\nstrict precision  %s" % pct(sc["violation"], n))
            print("with borderlines  %s" % pct(sc["violation"] + sc["borderline"], n))
            print("haiku %d of %d" % (sum(1 for x in st["labels"] if x["model"] == "haiku"), n))

        drawn = {x["sha"] for x in rec}
        import draw  # noqa: E402
        here = {r["sha"] for r in draw.sample(rows, labels["seed"], len(rec))}
        print("\nsample reproduces from this archive: %s"
              % ("yes" if drawn == here else "NO - %d of %d match"
                 % (len(drawn & here), len(drawn))))


if __name__ == "__main__":
    main()
