#!/usr/bin/env python3
"""Why the loop's candidate rounds were rejected, counted by class.

Issue #26 deferred multi-agent candidate generation with a revisit condition:

    Revisit when the ledger shows several consecutive rounds rejected at step 7
    for a failed hypothesis rather than a failed gate. That is the signal that
    idea quality has become the constraint.

Nobody had ever computed that. This script does, from `labels.json` — one label
per candidate round since 38, each keyed on a named fact printed in that round's
own results section rather than on a reading of its prose.

    python3 evals/results/loop/candidate-defects/classify.py
    python3 evals/results/loop/candidate-defects/classify.py --selftest

It is an arithmetic tool over a hand-built file, and the split is deliberate.
Deciding whether a point estimate moved against its registered direction needs a
reader; counting the result does not, and a count nobody can re-run is a claim
rather than a measurement. So the judgement is committed, with a verbatim quote
per round, and everything downstream of it is computed here.

Two integrity checks run every time, and they are not equally strict:

- **Evidence, fatal.** Each label's `evidence` string must still appear
  verbatim in its round document. A round document edited under this file fails
  here rather than leaving a label pointing at text that no longer exists.
- **Coverage, a warning.** Every round document carrying a `## The edit`
  heading at or above the scope's first round should have a label, and the
  unlabelled ones are named on stderr. It cannot be fatal: a round commits its
  registration — `## The edit` included — *before* it generates anything, so
  between that commit and the round's result there is a candidate round no
  reader could label. Failing there would make this file block the loop it
  audits. The warning is the same shape as `run.py`'s `no runs to carry`: a
  signal to act on rather than a stop.
"""

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROUNDS = HERE.parent
LABELS = HERE / "labels.json"

CLASSES = ("idea-defect", "noise-floor", "failed-gate", "accept")

# The two rejection classes #26's rationale contrasts. Its condition sentence
# says "failed hypothesis rather than failed gate", which is a two-way split;
# its rationale says "weak ideas rather than landing inside the noise floor",
# which is a three-way one. The rationale is the authoritative half, because it
# is the sentence that says what the machinery would buy.
WEAK_IDEA = "idea-defect"
NOISE = "noise-floor"


def load(path=LABELS):
    return json.loads(path.read_text())


def candidate_rounds(rounds_dir=ROUNDS, first=38):
    """Round numbers at or above `first` whose document carries `## The edit`.

    The same signal `tools/candidate-due.sh` reads, and for the same reason: a
    round declares its own kind in the document it commits before generating.
    """
    out = []
    for f in rounds_dir.glob("round-*.md"):
        m = re.fullmatch(r"round-(\d+)\.md", f.name)
        if not m:
            continue
        n = int(m.group(1))
        if n < first:
            continue
        if re.search(r"^## The edit", f.read_text(), re.M | re.I):
            out.append(n)
    return sorted(out)


def check_coverage(data, rounds_dir=ROUNDS):
    """Candidate rounds in scope with no label. A warning, never fatal."""
    labelled = {r["round"] for r in data["rounds"]}
    return [n for n in candidate_rounds(rounds_dir, data["scope"]["first_round"])
            if n not in labelled]


def check(data, rounds_dir=ROUNDS):
    """Evidence and class names. Returns a list of problems, empty when clean."""
    problems = []
    labelled = {r["round"]: r for r in data["rounds"]}

    for n, row in sorted(labelled.items()):
        if row["class"] not in CLASSES:
            problems.append(f"round {n}: unknown class {row['class']!r}")
        doc = rounds_dir / f"round-{n}.md"
        if not doc.exists():
            problems.append(f"round {n}: {doc.name} does not exist")
            continue
        if row["evidence"] not in doc.read_text():
            problems.append(
                f"round {n}: evidence string no longer appears in {doc.name}")
    return problems


def longest_run(labels, cls):
    """Longest run of consecutive *rejections* in class `cls`.

    Accepts do not break a run and do not extend one: #26's condition is about
    what the loop rejects for, and a round that shipped is not a rejection at
    all. Instrument rounds are absent from the labels entirely, so the sequence
    here is the sequence of candidate rounds in round order.
    """
    best = run = 0
    for row in labels:
        if row["class"] == "accept":
            continue
        run = run + 1 if row["class"] == cls else 0
        best = max(best, run)
    return best


def trailing_run(labels, cls):
    """Run of class `cls` at the end of the sequence, accepts skipped."""
    run = 0
    for row in reversed(labels):
        if row["class"] == "accept":
            continue
        if row["class"] != cls:
            break
        run += 1
    return run


def summarise(data, recent=4):
    labels = sorted(data["rounds"], key=lambda r: r["round"])
    rejections = [r for r in labels if r["class"] != "accept"]
    counts = {c: sum(1 for r in rejections if r["class"] == c)
              for c in CLASSES if c != "accept"}
    tail = rejections[-recent:]
    return {
        "first_round": data["scope"]["first_round"],
        "candidate_rounds": len(labels),
        "accepts": len(labels) - len(rejections),
        "rejections": len(rejections),
        "counts": counts,
        "longest_idea_defect_run": longest_run(labels, WEAK_IDEA),
        "trailing_idea_defect_run": trailing_run(labels, WEAK_IDEA),
        "recent": [(r["round"], r["class"]) for r in tail],
        "recent_idea_defects": sum(1 for r in tail if r["class"] == WEAK_IDEA),
        "recent_noise_floor": sum(1 for r in tail if r["class"] == NOISE),
    }


def render(data, recent=4):
    s = summarise(data, recent)
    n = s["rejections"]
    lines = [
        f"Candidate rounds from {s['first_round']}: {s['candidate_rounds']} "
        f"({s['accepts']} accept, {n} reject)",
        "",
        "Rejections by class:",
    ]
    for cls, k in s["counts"].items():
        lines.append(f"  {cls:<13} {k:>2} / {n}  ({100 * k / n:.0f}%)")
    lines += [
        "",
        f"Longest consecutive run of {WEAK_IDEA}: "
        f"{s['longest_idea_defect_run']}",
        f"Run of {WEAK_IDEA} at the end of the archive: "
        f"{s['trailing_idea_defect_run']}",
        "",
        f"Last {recent} rejections: "
        + ", ".join(f"{r} {c}" for r, c in s["recent"]),
        f"  weak ideas {s['recent_idea_defects']} of {len(s['recent'])}, "
        f"noise floor {s['recent_noise_floor']} of {len(s['recent'])}",
        "",
        "Per round:",
    ]
    for row in sorted(data["rounds"], key=lambda r: r["round"]):
        lines.append(f"  {row['round']:>3}  {row['class']:<13} "
                     f"{row['registered_primary']}")
    return "\n".join(lines)


def selftest():
    """Seven checks over the arithmetic and the evidence gate.

    Coverage is deliberately not asserted here. CI runs this selftest, and a
    round's registration commit carries `## The edit` before any result exists
    to label, so asserting coverage would fail every registration.
    """
    fails = []

    def ok(cond, what):
        if not cond:
            fails.append(what)

    mk = lambda n, c: {"round": n, "class": c, "registered_primary": "",
                       "evidence": ""}

    ok(longest_run([mk(1, "idea-defect"), mk(2, "idea-defect"),
                    mk(3, "noise-floor"), mk(4, "idea-defect")],
                   "idea-defect") == 2,
       "longest_run counts the longest run, not the last one")

    ok(longest_run([mk(1, "idea-defect"), mk(2, "accept"),
                    mk(3, "idea-defect")], "idea-defect") == 2,
       "an accept neither breaks nor extends a run of rejections")

    ok(trailing_run([mk(1, "idea-defect"), mk(2, "noise-floor")],
                    "idea-defect") == 0,
       "trailing_run is 0 when the last rejection is another class")

    ok(trailing_run([mk(1, "noise-floor"), mk(2, "idea-defect"),
                     mk(3, "idea-defect")], "idea-defect") == 2,
       "trailing_run counts back from the end")

    data = load()
    ok(check(data) == [], f"the committed labels are clean: {check(data)}")

    s = summarise(data)
    ok(s["rejections"] == sum(s["counts"].values()),
       "every rejection lands in exactly one class")

    ok(all(r["class"] in CLASSES for r in data["rounds"]),
       "every committed label names a class the criterion defines")

    for f in fails:
        print(f"FAIL: {f}")
    print(f"{7 - len(fails)}/7 checks passed")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--recent", type=int, default=4,
                    help="how many trailing rejections the summary reports on")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    data = load()
    problems = check(data)
    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        return 3

    for n in check_coverage(data):
        print(f"warning: round {n} carries '## The edit' and is not labelled; "
              f"it is outside every count below", file=sys.stderr)

    if args.json:
        print(json.dumps(summarise(data, args.recent), indent=2))
    else:
        print(render(data, args.recent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
