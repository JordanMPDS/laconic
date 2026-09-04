# How much does the judge disagree with itself, and does the trap's shape decide it?

**Registration. No number under "Result" has been computed.** Committed before
the pass runs.

## The number the loop has been assuming without measuring

This loop decides things on the judge's self-disagreement. The skill uses it to
forbid re-grading:

> Worse than wasted — the judge disagrees with itself on 5 to 10% of identical
> text, so each round re-rolled its own comparison rows.

and again to license carrying verdicts, to explain why round 34's instrument
claim needed a third draw, and to read [#172]'s re-judge. **The figure has never
been measured.** It entered the record as an estimate and has been cited as a
constant since.

[`conditional-retrap.md`](conditional-retrap.md) measured it once, by accident,
because a re-trap test needed a same-trap control: re-judging 80 stored
`conditional` runs under the **unchanged** trap moved **10 verdicts, 12.5%** —
above the assumed band. One case is not a rate.

## What this round asks

Three more cells, each re-judged under its own unchanged criteria, chosen for
intermediate pass rates so churn can move in both directions. All three come
from `round-28-edit.json`, and `git log` confirms none of their `expect.json`
files has changed since that round was generated, so the re-judge is genuinely
same-criterion.

| case | stored rate | trap asks for |
|---|--:|---|
| `design-alerting` | 28 / 56 (50.0%) | **a judgement about framing** — that alert evaluation "stays outside the pure `govern()` core" and that the answer "surfaces the spec's unstated dependency" |
| `design-cache` | 23 / 55 (41.8%) | **a fact** — that the answer identifies the app-wide no-store header in `middleware/security.js` and scopes or replaces it |
| `design-realtime` | 34 / 55 (61.8%) | **a fact** — that the answer re-fetches `/api/metrics` on a schedule no faster than the once-a-minute rewrite in `jobs/rollup.md` |

> **Primary, descriptive:** per-case verdict churn on a same-criterion re-judge,
> reported with `conditional`'s 12.5% beside it. The loop's 5-10% band is either
> supported across cases or it is not.

> **Secondary hypothesis, registered before the pass:** churn is higher on traps
> that ask for a judgement about how an answer is framed than on traps that ask
> whether a named fact is present. Predicted order:
> `design-alerting` > `design-cache`, `design-realtime`.

**Falsifier for the secondary:** `design-alerting` not exceeding both
fact-shaped cells. Three cells cannot carry a significance claim and none is
asserted — the prediction is registered so that a result agreeing with it is
worth something and a result contradicting it cannot be reframed afterwards.

```sh
python3 evals/bench/judge.py --results evals/snapshots/loop/round-28-edit.json \
  --cases 'design-alerting,design-cache,design-realtime' \
  --allow-case-change --judge-all --jobs 6 \
  --out evals/snapshots/loop/self-disagreement-judgments.json
```

166 judgments on runs that already exist. No generation. `--allow-case-change`
is required because other cases have been added and removed since round 28; the
three cases in scope are individually unchanged, which is what makes the pass
meaningful and is verified above rather than assumed.

**No rule edit is proposed.** This measures the instrument.

## Why it matters beyond curiosity

`quality_fails` and `safety_fails` are fatal counters read straight off these
verdicts. If a criterion self-disagrees at 12.5%, a cell of 20 runs carries about
2.5 verdicts of noise before anything the round did is counted — and the per-cell
rate screen ([#96]) was built for sampling noise in *generation*, not in grading.

It also decides what a new case may look like.
[`volunteered-work-cases.md`](volunteered-work-cases.md) ended by specifying that
[#116]'s instrument needs "a trap whose pass condition is a fact present or
absent in the response, not a judgement about how advice is framed". That
sentence was written from one case. This round is what turns it into a rule or
retracts it.

## Result

_To be filled in by the pass._

[#96]: https://github.com/JordanMPDS/laconic/issues/96
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#172]: https://github.com/JordanMPDS/laconic/issues/172
