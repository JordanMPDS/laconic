#!/usr/bin/env python3
"""Score the #150 pilot pair: how long is the deliverable, and is it right?

The deliverable is the response on `authored-reply` and ONBOARDING.md on
`authored-file`, so a length metric that reads `text` alone measures a
one-line "wrote it" on half the pair. That is the whole point of the pilot:
every metric the loop has is a `text` metric.

    python3 evals/pilot/score_authored.py <snapshot> [judgments]
"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402

CASES = Path(__file__).resolve().parent


def deliverable(run):
    """(words in the deliverable, words in the reply) for one run."""
    reply = metrics.score(run.get("text", ""))["words"]
    expect = json.loads((CASES / run["case"] / "expect.json").read_text())
    if not expect.get("grade_artifacts"):
        return reply, reply
    wrote = sum(metrics.score(e["text"])["words"]
                for e in (run.get("artifacts") or {}).values()
                if e.get("text"))
    return wrote, reply


def main():
    snap = json.loads(Path(sys.argv[1]).read_text())
    verdicts = {}
    if len(sys.argv) > 2:
        for v in json.loads(Path(sys.argv[2]).read_text())["judgments"]:
            verdicts[(v["case"], v["arm"], v["model"], v["rep"])] = v["verdict"]

    cells = defaultdict(list)
    for r in bench_run.usable(snap["runs"]):
        key = (r["case"], r["arm"])
        wrote, reply = deliverable(r)
        cells[key].append((wrote, reply,
                           verdicts.get((r["case"], r["arm"], r["model"],
                                         r["rep"])),
                           bool(r.get("artifacts"))))

    print("| case | arm | n | deliverable words | reply words | wrote a file | trap |")
    print("|---|---|--:|--:|--:|--:|--:|")
    med = {}
    for key in sorted(cells):
        rows = cells[key]
        d = statistics.median(r[0] for r in rows)
        med[key] = d
        passes = sum(1 for r in rows if r[2] == "pass")
        graded = sum(1 for r in rows if r[2] in ("pass", "fail"))
        print("| %s | %s | %d | %.1f | %.1f | %d/%d | %s |"
              % (key[0], key[1], len(rows), d,
                 statistics.median(r[1] for r in rows),
                 sum(1 for r in rows if r[3]), len(rows),
                 ("%d/%d" % (passes, graded)) if graded else "-"))

    print()
    for case in sorted({k[0] for k in cells}):
        b, l = med.get((case, "baseline")), med.get((case, "laconic"))
        if b and l:
            print("%s: laconic / baseline = %.2f  (%.1f -> %.1f words)"
                  % (case, l / b, b, l))


if __name__ == "__main__":
    main()
