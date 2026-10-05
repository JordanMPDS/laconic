#!/usr/bin/env python3
"""Whether a round's registered pre-mortem called how the round would end (#26).

`candidate-defects-26.md` made #26 decidable on one question: can the loop's own
author call a weak idea in advance? Every candidate round since 71 registers a
pre-mortem before generating anything. This scores them against `labels.json`.

    python3 evals/results/loop/candidate-defects/premortem.py            # score
    python3 evals/results/loop/candidate-defects/premortem.py --label    # panel
    python3 evals/results/loop/candidate-defects/premortem.py --selftest

The predicted class is not read by a person who knows the results. `--label`
gives each round's registration-time document, cut at `## Results`, to a blind
panel - sonnet, opus and kimi through `judge.py`'s own helpers, each in a fresh
temporary directory - and keeps the majority, as `judge.py` does. The
registration commit lives only on the round's pull request, because the loop
squash-merges, so a missing object is fetched from `refs/pull/<PR>/head`.

`premortems.json` records a checksum of each pre-mortem section at registration,
and the selftest fails if the same section in today's round document differs: a
pre-mortem edited after its result would no longer be a prediction.
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor
from math import comb

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROUNDS = HERE.parent
DATA = HERE / "premortems.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import classify  # noqa: E402

PANEL = ("sonnet", "opus", "kimi")
PREDICTED = ("idea-defect", "noise-floor", "failed-gate", "unscored", "none")
IDEA = "idea-defect"
SPLIT = "split"
ALPHA = 0.05
SECTION = "## Pre-mortem, registered"

PROMPT = """You are reading the registration of one round of a benchmark loop that tests edits to a rules file for an AI assistant. The document below was written and committed before any data for the round was generated. It contains a section headed "## Pre-mortem, registered", in which the round's author predicted how the round would most likely fail.

Classify the single failure that the pre-mortem names as LIKELIEST into exactly one of these classes. Use the rest of the document only to work out what the pre-mortem's terms refer to (for example, what "bar 2", "the bound" or "the precheck" is).

- idea-defect: the pre-mortem expects the primary target's point estimate to move AGAINST the registered direction (the edit makes the targeted behaviour worse), or expects a registered check to show that the mechanism the edit relies on does not operate.
- noise-floor: the pre-mortem expects the primary's point estimate to move WITH the registered direction, or barely at all, and not separate: too small an effect, too noisy, underpowered, under a registered magnitude bar, or failing to replicate.
- failed-gate: the pre-mortem expects the primary to pass and a different registered bar, bound, guard or fatal counter (quality, length, coverage, spillover, holdout, safety) to reject the round.
- unscored: the pre-mortem expects a stage registered before the primary, such as a fire-rate precheck or an assay requiring the control to show the behaviour, to fail, so that the primary is never meaningfully scored.
- none: the pre-mortem names no failure, predicts that the round will pass, or names several failures without indicating which is likeliest.

If the pre-mortem ranks several failures, classify the one it ranks likeliest.

Reply with one JSON object and nothing else:
{"predicted": "<class>", "quote": "<the sentence from the pre-mortem that names it, copied exactly>", "reason": "<one sentence>"}

=== DOCUMENT ===
"""


def load(path=DATA):
    return json.loads(path.read_text())


def save(data, path=DATA):
    path.write_text(json.dumps(data, indent=1, ensure_ascii=True) + "\n")


def premortem_section(text):
    """The `## Pre-mortem, registered` section, heading excluded."""
    out, inside = [], False
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            inside = line.startswith(SECTION)
            continue
        if inside:
            out.append(line)
    return "".join(out)


def cksum(text):
    return zlib.crc32(text.encode()) & 0xFFFFFFFF


def registration_doc(row):
    """The round document at its registration commit, cut at `## Results`."""
    spec = "%s:evals/results/loop/round-%d.md" % (row["registration_commit"], row["round"])
    got = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True, text=True)
    if got.returncode != 0:
        subprocess.run(["git", "fetch", "-q", "origin", "pull/%d/head" % row["pr"]],
                       cwd=ROOT, check=True)
        got = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True,
                             text=True, check=True)
    return got.stdout.split("\n## Results", 1)[0] + "\n"


def parse_vote(raw):
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return None
    if not isinstance(d, dict) or d.get("predicted") not in PREDICTED:
        return None
    return {"predicted": d["predicted"], "quote": d.get("quote", "") or "",
            "reason": d.get("reason", "") or ""}


def majority(votes):
    """Two agreeing votes decide; three decided and all different is a split;
    anything short of that is undecided (None) and `--label` retries it."""
    decided = [v["predicted"] for v in votes.values() if v]
    for c in set(decided):
        if decided.count(c) >= 2:
            return c
    return SPLIT if len(decided) == len(PANEL) else None


def label(data, claude_bin="claude", jobs=3):
    import judge  # the panel's own blind calls; imported here so scoring needs no CLI

    def one(row):
        prompt = PROMPT + registration_doc(row)
        votes = dict(row.get("votes") or {})
        for m in PANEL:
            if votes.get(m):
                continue
            res = judge._call_kimi(prompt) if m == "kimi" else \
                judge._call_blind(claude_bin, m, prompt)
            votes[m] = parse_vote(res.get("text", "")) if res.get("ok") else None
        return row["round"], votes

    todo = [r for r in data["rounds"] if majority(r.get("votes") or {}) is None]
    at = {r["round"]: r for r in data["rounds"]}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for n, votes in pool.map(one, todo):
            at[n]["votes"] = votes
            at[n]["predicted"] = majority(votes)
            save(data)
            print("round %d -> %s  (%s)" % (n, at[n]["predicted"], ", ".join(
                "%s %s" % (m, (votes.get(m) or {}).get("predicted")) for m in PANEL)),
                flush=True)


def fisher_greater(hits, predicted, actual, total):
    """One-sided Fisher exact: P(at least `hits` overlap) under the margins."""
    top = min(predicted, actual)
    return sum(comb(actual, x) * comb(total - actual, predicted - x)
               for x in range(hits, top + 1)) / comb(total, predicted)


def table(rows, says_idea):
    n = len(rows)
    actual = sum(1 for r in rows if r["outcome"] == IDEA)
    pred = sum(1 for r in rows if says_idea(r))
    hits = sum(1 for r in rows if says_idea(r) and r["outcome"] == IDEA)
    return {"n": n, "actual": actual, "predicted": pred, "hits": hits,
            "p": fisher_greater(hits, pred, actual, n)}


def joined(data, labels):
    outcome = {r["round"]: r["class"] for r in labels["rounds"]}
    return [dict(r, outcome=outcome[r["round"]]) for r in data["rounds"]]


def score(data, labels):
    rows = joined(data, labels)
    scored = [r for r in rows if r["outcome"] != "unscored"]
    readings = {
        "majority": table(scored, lambda r: r.get("predicted") == IDEA),
        "any vote": table(scored, lambda r: any(
            (v or {}).get("predicted") == IDEA for v in (r.get("votes") or {}).values())),
    }
    callable_ = any(t["p"] < ALPHA for t in readings.values())
    return rows, readings, callable_


def render(data, labels):
    rows, readings, callable_ = score(data, labels)
    out = ["Pre-mortem against outcome, rounds %d to %d (%d rounds, %d scored)"
           % (rows[0]["round"], rows[-1]["round"], len(rows),
              readings["majority"]["n"]), ""]
    for name, t in readings.items():
        out.append("  %-9s named idea-defect %2d, ended idea-defect %d, both %d: "
                   "one-sided Fisher p = %.4f" % (name, t["predicted"], t["actual"],
                                                  t["hits"], t["p"]))
    out += ["", "Verdict: %s (registered: callable if either reading p < %.2f)"
            % ("CALLABLE" if callable_ else "NOT CALLABLE", ALPHA), "",
            "Per round (panel majority; votes sonnet/opus/kimi):"]
    for r in rows:
        votes = r.get("votes") or {}
        out.append("  %3d  %-12s ended %-12s %s" % (
            r["round"], r.get("predicted") or "-", r["outcome"],
            "/".join((votes.get(m) or {}).get("predicted") or "-" for m in PANEL)))
    classes_p = PREDICTED + (SPLIT,)
    classes_o = classify.CLASSES
    out += ["", "Confusion, predicted (rows) against outcome (columns):",
            "  %-12s" % "" + "".join("%13s" % c for c in classes_o)]
    for p in classes_p:
        cells = [sum(1 for r in rows if r.get("predicted") == p and r["outcome"] == o)
                 for o in classes_o]
        if any(cells):
            out.append("  %-12s" % p + "".join("%13d" % c for c in cells))
    return "\n".join(out)


def check(data, labels, rounds_dir=ROUNDS):
    problems = []
    outcome = {r["round"] for r in labels["rounds"]}
    for r in data["rounds"]:
        n = r["round"]
        if n not in outcome:
            problems.append("round %d has no outcome label in labels.json" % n)
        doc = rounds_dir / ("round-%d.md" % n)
        if not doc.exists():
            problems.append("round %d: %s does not exist" % (n, doc.name))
        elif cksum(premortem_section(doc.read_text())) != r["premortem_cksum"]:
            problems.append("round %d: the pre-mortem in %s differs from the one "
                            "registered" % (n, doc.name))
    return problems


def selftest():
    fails = []

    def ok(cond, what):
        if not cond:
            fails.append(what)

    ok(abs(fisher_greater(2, 2, 3, 22) - 3 / 231) < 1e-12,
       "two hits from two calls among 3 of 22 is 3/231")
    ok(abs(fisher_greater(1, 1, 3, 22) - 3 / 22) < 1e-12,
       "one hit from one call cannot reach 0.05")
    ok(fisher_greater(0, 0, 3, 22) == 1.0, "no call at all reads p = 1")

    v = lambda c: {"predicted": c}
    ok(majority({"sonnet": v(IDEA), "opus": v(IDEA), "kimi": v("none")}) == IDEA,
       "two agreeing votes decide")
    ok(majority({"sonnet": v(IDEA), "opus": v("noise-floor"),
                 "kimi": v("failed-gate")}) == SPLIT, "three different votes split")
    ok(majority({"sonnet": v(IDEA), "opus": None, "kimi": v("none")}) is None,
       "a missing vote with no majority is undecided, and retried")
    ok(parse_vote('x {"predicted": "noise-floor", "quote": "q"} y')["predicted"]
       == "noise-floor" and parse_vote('{"predicted": "maybe"}') is None,
       "a vote parses only into a registered class")

    ok(premortem_section("# T\n## Pre-mortem, registered\n\nA.\n## Next\nB.\n")
       == "\nA.\n", "the section ends at the next heading")

    data, labels = load(), classify.load()
    problems = check(data, labels)
    ok(problems == [], "pre-mortems match their registration: %s" % problems)

    for f in fails:
        print("FAIL: %s" % f)
    print("%d/9 checks passed" % (9 - len(fails)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", action="store_true",
                    help="run the blind panel on every round without a majority")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    data, labels = load(), classify.load()
    problems = check(data, labels)
    if problems:
        for p in problems:
            print("error: %s" % p, file=sys.stderr)
        return 3
    if args.label:
        label(data, args.claude_bin, args.jobs)
        return 0
    undecided = [r["round"] for r in data["rounds"] if not r.get("predicted")]
    if undecided:
        print("error: rounds without a panel majority: %s; run --label" % undecided,
              file=sys.stderr)
        return 3
    print(render(data, labels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
