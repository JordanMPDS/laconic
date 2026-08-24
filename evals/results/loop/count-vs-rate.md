# The fatal counters compare counts where they should compare rates

**Date:** 2026-08-24
**Issue:** [#133]
**Cost:** no generations. The re-score below runs on stored snapshots.
**Code:** `_sample_covers` and `_fisher_upper_tail` in `evals/bench/report.py`,
gated by `CELL_TEST_MIN_RUNS`.

## The defect

The four fatal counters compare a round's per-cell count against the
baseline's, and the arbitration that can clear a risen cell requires the
replicated count to be **at or below** the baseline's. Both are count
comparisons. They were written for a round scored against a stored baseline at
five or ten runs a cell, where a rise of one or two was the whole signal.

Round 25 is the first round the loop has run at 25 reps a side, and it broke
them. It lost `quality_fails` 39 to 41 on four cells, a full 200-run
replication of the treatment side cleared none of them, and the rates it was
rejected on were:

| | control | round | replication | pooled treatment | Fisher |
|---|--:|--:|--:|--:|--:|
| round-wide | 39/199 (19.6%) | 41/196 | 40/198 | 81/394 (20.6%) | **0.829** |

Two of the four cells have a control count of **0**, which any single failure
exceeds. At a true rate near 20%, a 25-run cell draws 0 about 0.4% of the time,
so a cell that draws 0 in the control is close to unclearable however many runs
the replication has.

## The fix, and why it is scoped by run count

Where **both** sides have enough runs to estimate a rate, the rise is tested —
one-sided Fisher at the same alpha the rest of the gate uses — instead of
counted. Where either side is short, nothing changes.

The bar is where the test has enough power to be worth having. With the control
cell at 0, the smallest treatment count that reaches alpha = 0.05 one-sided is:

| runs per side | 5 | 10 | 15 | 20 | 25 | 30 | 40 |
|---|--:|--:|--:|--:|--:|--:|--:|
| detects | 80% | 40% | 27% | **25%** | 20% | 17% | 12% |

At five or ten runs a side the test would clear four fifths of a cell failing
outright. That is not a sharper gate, it is a broken one, and it is why
`CELL_TEST_MIN_RUNS` is 20 rather than 0. Rounds scored at n ≤ 10 keep the rule
they were scored under.

This is the same correction `_rate_covers` already makes against a separately
measured master-rules rate ([#96]), applied to the case where the comparison's
own control side is large enough to supply the rate.

## The re-score, which is the condition for adopting it

Every stored round re-scored twice: once with `CELL_TEST_MIN_RUNS` raised out
of reach, which reproduces the pre-[#133] behaviour exactly, and once at 20.
The fatal counters are computed the same way whatever target a round named, so
this compares the fatal reason lines and isolates what the change can touch.

**23 rounds re-scored. One moved: round 25.**

| round | max runs in any cell | verdict line |
|---|--:|---|
| 01 to 06 | 5 | unchanged |
| 07 to 20 | 10 | unchanged |
| 21, 22, 24 | 5 | unchanged |
| **25** | **25** | `REJECT: quality lost (39 -> 41)` becomes `quality rise (39 -> 41) is inside sampling` |

No stored round has more than ten runs in any cell, so by construction the
change cannot reach one, and the empirical re-score confirms it. To reproduce a
round's pair of verdict lines:

```python
import json, sys
sys.path.insert(0, "evals/bench")
import report as R
L = "evals/snapshots/loop/"
def summary(stem):
    snap = json.load(open(L + stem + ".json"))
    judg = json.load(open(L + stem + "-judgments.json"))["judgments"]
    return R.round_summary(snap, judg)
prev, cur = summary("round-01-n10-v4"), summary("round-20")
for bar in (10 ** 9, 20):          # pre-#133, then #133
    R.CELL_TEST_MIN_RUNS = bar
    print(bar, [r for r in R.accept_verdict(prev, cur, "output_tokens")[1]
                if "lost (" in r or "rise (" in r])
```

**The first round this can act on is the round that motivated it.** That is
uncomfortable and is stated rather than hidden. Two things make it defensible:
the bar is set from a power table rather than from round 25's numbers, and
round 25's own verdict is **not** claimed from the re-score — a fresh round,
registered under the fixed gate, is what decides the licence.

[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#96]: https://github.com/JordanMPDS/laconic/issues/96
