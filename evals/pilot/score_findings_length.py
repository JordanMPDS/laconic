#!/usr/bin/env python3
"""Round 125: the findings below the decider get one sentence each (#113).

    python3 evals/pilot/score_findings_length.py words <control.json> <edit.json>
    python3 evals/pilot/score_findings_length.py bounds <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_findings_length.py holdout <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_findings_length.py --selftest

Round 111 shipped "say which one decides it and rank the rest under it" for a
list of findings. On opus at v0.3.10 the ranked remainder is most of the
answer: `verdict-experiment` runs 445 prose words over 7 to 14 list items. The
edit appends "one sentence each" to that sentence.

**Primary, `words`:** prose words fall on the three `verdict-*` cells on opus.
A one-sided stratified permutation of the side label within each cell, whose
statistic is the mean over cells of (median log edit words - median log
control words), so each cell counts once and `verdict-experiment`'s length
cannot carry the other two. `score_settled.stratified` on logged words, seed
`SEED`, alpha `ALPHA`. Words are `score_compression.words`, the loop's prose
counter, which counts list items and drops fenced and inline code. Total
whitespace words and list items print beside it and decide nothing.

**Bounds, `bounds`:** the panel pass rate may not fall in any `BOUNDS` cell,
each one-sided Fisher at `ALPHA`, uncorrected, per `AGENTS.md`. Per cell
rather than pooled, so a collapse on the cell round 111 was shipped to fix
cannot hide in a pool. A `not_exercised` verdict is left out of n.

**Holdout, `holdout`:** no reserved case's pass rate, sonnet and opus pooled,
falls at one-sided Fisher p < `ALPHA`.
"""

import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score_choice import fall  # noqa: E402
from score_compression import words  # noqa: E402
from score_settled import stratified  # noqa: E402

SEED = 125
ALPHA = 0.05
RESAMPLES = 200000
TARGET = (("verdict-experiment", "opus"), ("verdict-rollout", "opus"),
          ("verdict-schema", "opus"))
BOUNDS = TARGET + (("destructive", "opus"), ("verdict-experiment", "sonnet"),
                   ("verdict-rollout", "sonnet"), ("verdict-schema", "sonnet"))
ITEM = re.compile(r"^\s*(\d+[.)]|[-*•])\s+\S", re.M)


def median(xs):
    return statistics.median(xs) if xs else 0


def runs(path):
    snap = json.loads(Path(path).read_text())
    out = {}
    for r in snap["runs"]:
        if r.get("arm") == "laconic" and r.get("ok", True):
            out.setdefault((r["case"], r["model"]), []).append(r)
    return snap.get("metadata", {}), out


def primary(control, edit, resamples=RESAMPLES):
    pairs = []
    print("## Primary: prose words fall on verdict-*/opus, one-sided")
    for c in TARGET:
        cw = [words(r) for r in control.get(c, [])]
        ew = [words(r) for r in edit.get(c, [])]
        pairs.append(([math.log(max(w, 1)) for w in cw],
                      [math.log(max(w, 1)) for w in ew]))
        print("   %-24s control n=%2d median %5.0f  edit n=%2d median %5.0f"
              % ("/".join(c), len(cw), median(cw), len(ew), median(ew)))
    if any(not c or not e for c, e in pairs):
        print("   a cell is empty on one side: the primary is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples)
    ok = p < ALPHA
    print("   mean log ratio %.3f (factor %.3f)  one-sided p = %.5f  %s"
          % (obs, math.exp(obs), p, "PASSES" if ok else "fails"))
    return ok


def disclose(control, edit):
    print("## Disclosed, deciding nothing: medians per cell")
    for c in sorted(set(control) | set(edit)):
        row = []
        for side in (control, edit):
            rs = side.get(c, [])
            row.append("n=%2d prose %5.0f total %5.0f items %4.1f"
                       % (len(rs), median([words(r) for r in rs]),
                          median([len((r.get("text") or "").split()) for r in rs]),
                          median([len(ITEM.findall(r.get("text") or "")) for r in rs])))
        print("   %-26s control %s | edit %s" % ("/".join(c), row[0], row[1]))


def tally(path):
    js = json.loads(Path(path).read_text())["judgments"]
    out = {}
    for v in (js.values() if isinstance(js, dict) else js):
        if v.get("verdict") in ("pass", "fail"):
            out.setdefault((v["case"], v["model"]), Counter())[v["verdict"]] += 1
    return out


def passes(t, cells):
    return (sum(t.get(c, Counter())["pass"] for c in cells),
            sum(sum(t.get(c, Counter()).values()) for c in cells))


def bounds(c, e):
    print("## Bounds (fatal): the pass rate may not fall, per cell")
    fired = False
    for cell in BOUNDS:
        fired |= fall("/".join(cell), *passes(c, [cell]), *passes(e, [cell]))
    print("## %s" % ("bounds hold" if not fired else "reject"))
    return not fired


def holdout(c, e):
    print("## Holdout: no reserved case worse, sonnet and opus pooled")
    fired = False
    for case in sorted({k for k, _ in c} | {k for k, _ in e}):
        cells = [(case, "sonnet"), (case, "opus")]
        fired |= fall(case, *passes(c, cells), *passes(e, cells))
    print("## %s" % ("holdout holds" if not fired else "reject"))
    return not fired


def selftest():
    def snap(lengths):
        return {cell: [{"text": "word " * n} for n in ns]
                for cell, ns in lengths.items()}
    long_ = snap({c: [400 + i for i in range(20)] for c in TARGET})
    short = snap({c: [280 + i for i in range(20)] for c in TARGET})
    assert primary(long_, short, resamples=2000)
    assert not primary(long_, long_, resamples=2000)
    assert not primary(short, long_, resamples=2000)
    assert not primary(long_, {TARGET[0]: short[TARGET[0]]}, resamples=2000)

    def t(cells):
        return {c: Counter(v) for c, v in cells.items()}
    full = t({c: ["pass"] * 20 for c in BOUNDS})
    assert bounds(full, full)
    worse = {**full, **t({("verdict-schema", "sonnet"):
                          ["pass"] * 4 + ["fail"] * 6})}
    assert not bounds(full, worse)
    assert passes(t({TARGET[0]: ["pass", "fail"]}), [TARGET[0]]) == (1, 2)
    hold = t({("holdout-design", m): ["pass"] * 5 for m in ("sonnet", "opus")})
    assert holdout(hold, hold)
    assert not holdout(hold, t({("holdout-design", m): ["fail"] * 5
                                for m in ("sonnet", "opus")}))
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if len(argv) == 3 and argv[0] == "words":
        (cm, c), (em, e) = runs(argv[1]), runs(argv[2])
        for name, m in (("control", cm), ("edit", em)):
            print("%-8s rules_cksum %s  cli %s" % (
                name, m.get("rules_cksum"), m.get("claude_cli_version")))
        if cm.get("rules_cksum") == em.get("rules_cksum"):
            print("!! both sides share rules_cksum: this is not a contrast")
            return 1
        ok = primary(c, e)
        disclose(c, e)
        return 0 if ok else 1
    if len(argv) == 3 and argv[0] in ("bounds", "holdout"):
        fn = bounds if argv[0] == "bounds" else holdout
        return 0 if fn(tally(argv[1]), tally(argv[2])) else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
