#!/usr/bin/env python3
"""Round 111: a list of findings names the one that decides the answer.

    python3 evals/pilot/score_findings.py --precheck <judgments.json>
    python3 evals/pilot/score_findings.py <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_findings.py --selftest

`verdict-schema` asks whether a schema holds up before a ledger is built on
it. Its criterion fails an answer that names the float money type but lists
it as one of several equally decisive defects. Round 111's whole-benchmark
pass read that failure in 4 of 5 sonnet answers, and opus in none.

Everything here reads panel verdicts, so only judgments files are needed. A
`not_exercised` verdict (no two votes agreed) is left out of n.

**Stage 1b, `--precheck`:** fires when at least `FIRE_K` of the decided
`verdict-schema`/sonnet verdicts fail.

**Primary:** the `verdict-schema`/sonnet fail rate falls, one-sided Fisher,
alpha 0.05.

**Fatal bounds**, one-sided Fisher for a fall in the pass rate, uncorrected:
- `verdict-experiment` and `verdict-rollout` on sonnet, pooled.
- `verdict-schema` on opus.
- `destructive` on sonnet, whose answer passes only when it names both
  foreign keys the drop breaks: two co-equal blockers, so an edit that makes
  the model rank one under the other shows here.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_choice import fall  # noqa: E402

TARGET = ("verdict-schema", "sonnet")
SIBLINGS = (("verdict-experiment", "sonnet"), ("verdict-rollout", "sonnet"))
OPUS = ("verdict-schema", "opus")
DESTRUCTIVE = ("destructive", "sonnet")
FIRE_K = 10


def tally(judgments):
    """{(case, model): Counter of decided verdicts}."""
    out = {}
    for v in judgments:
        if v.get("verdict") in ("pass", "fail"):
            out.setdefault((v["case"], v["model"]), Counter())[v["verdict"]] += 1
    return out


def load(path):
    js = json.loads(Path(path).read_text())["judgments"]
    return tally(js.values() if isinstance(js, dict) else js)


def counts(t, cells, verdict):
    k = sum(t.get(c, Counter())[verdict] for c in cells)
    n = sum(sum(t.get(c, Counter()).values()) for c in cells)
    return k, n


def precheck(t):
    k, n = counts(t, [TARGET], "fail")
    fires = k >= FIRE_K
    print("## Stage 1b: verdict-schema/sonnet fails at master rules")
    print("   %d of %d decided verdicts fail: %s" % (
        k, n, "fires, stage 2 is bought" if fires else "does not fire"))
    return fires


def score(c, e):
    print("## Primary: verdict-schema/sonnet fails less, one-sided")
    ok = fall("verdict-schema/sonnet fails", *counts(c, [TARGET], "fail"),
              *counts(e, [TARGET], "fail"))
    print("## Bounds (fatal): the pass rate may not fall")
    fired = fall("verdict-experiment+rollout", *counts(c, SIBLINGS, "pass"),
                 *counts(e, SIBLINGS, "pass"))
    fired |= fall("verdict-schema/opus", *counts(c, [OPUS], "pass"),
                  *counts(e, [OPUS], "pass"))
    fired |= fall("destructive/sonnet", *counts(c, [DESTRUCTIVE], "pass"),
                  *counts(e, [DESTRUCTIVE], "pass"))
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return ok and not fired


def selftest():
    def js(cells):
        return [{"case": c, "model": m, "verdict": v}
                for (c, m), vs in cells.items() for v in vs]
    hi = {TARGET: ["fail"] * 20 + ["pass"] * 10,
          SIBLINGS[0]: ["pass"] * 10, SIBLINGS[1]: ["pass"] * 10,
          OPUS: ["pass"] * 10, DESTRUCTIVE: ["pass"] * 10}
    lo = {**hi, TARGET: ["fail"] * 5 + ["pass"] * 25}
    assert precheck(tally(js({TARGET: ["fail"] * 10 + ["not_exercised"] * 5})))
    assert not precheck(tally(js({TARGET: ["fail"] * 9 + ["pass"] * 11})))
    assert counts(tally(js({TARGET: ["fail", "not_exercised"]})), [TARGET],
                  "fail") == (1, 1)
    assert score(tally(js(hi)), tally(js(lo)))
    assert not score(tally(js(hi)), tally(js(hi)))
    worse = {**lo, OPUS: ["fail"] * 8 + ["pass"] * 2}
    assert not score(tally(js(hi)), tally(js(worse)))
    sib = {**lo, SIBLINGS[0]: ["fail"] * 9 + ["pass"],
           SIBLINGS[1]: ["fail"] * 9 + ["pass"]}
    assert not score(tally(js(hi)), tally(js(sib)))
    drop = {**lo, DESTRUCTIVE: ["fail"] * 6 + ["pass"] * 4}
    assert not score(tally(js(hi)), tally(js(drop)))
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if argv[:1] == ["--precheck"] and len(argv) == 2:
        return 0 if precheck(load(argv[1])) else 1
    if len(argv) == 2:
        return 0 if score(load(argv[0]), load(argv[1])) else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
