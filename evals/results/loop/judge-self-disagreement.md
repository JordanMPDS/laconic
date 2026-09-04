# How much does the judge disagree with itself, and does the trap's shape decide it?

**Registration. No number under "Result" has been computed.** Committed before
the pass runs.

## The number, and where it came from

This loop decides things on the judge's self-disagreement. The skill uses it to
forbid re-grading:

> Worse than wasted — the judge disagrees with itself on 5 to 10% of identical
> text, so each round re-rolled its own comparison rows.

and again to license carrying verdicts, to explain why round 34's instrument
claim needed a third draw, and to read [#172]'s re-judge.

**It is measured, and this round nearly published a claim that it was not.**
Round 13 re-judged round 12's 340 laconic responses under identical criteria and
[`instrument-notes.md`](instrument-notes.md) records the result: 94.7% agreement
on the laconic arm and 90.4% on the control arm. The band's two ends are those
two arms.

What that measurement is, and what it is not, is the whole point of this round.
**It is pooled over every case a round covers**, and most of them cannot churn: a
cell graded 20 of 20 has nowhere to move. So a pooled figure is an average over
cells that are structurally frozen and cells that are not, and the cells a round
is actually *decided* on are the second kind.

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

## Result: 0% to 27% between cases, and the spread is the finding

Same-criterion re-judge, paired per run:

| case | stored | re-judged | flips | churn | trap asks |
|---|--:|--:|--:|--:|---|
| `design-alerting` | 28/56 | 29/56 | 15 | **26.8%** | a judgement about framing |
| `design-realtime` | 34/55 | 36/55 | 10 | **18.2%** | a fact (named endpoint) |
| `conditional` | 46/80 | 48/80 | 10 | **12.5%** | a judgement about framing |
| `design-cache` | 23/55 | 23/55 | 0 | **0.0%** | a fact (named file) |

Pooled over the three new cells: **25 of 166, 15.1%.** No cell's *rate* moves —
every McNemar is p ≥ 0.75, so the churn is symmetric and a round's headline
number is not biased by it. What moves is which runs pass.

**This 15.1% does not contradict round 13's 5.3%, and must not be quoted as if
it did.** These three cells were chosen *because* their stored pass rates were
between 42% and 62%, which is where churn can occur at all. Round 13's figure is
pooled over a whole round, most of whose cells sit at or near a ceiling and
contribute close to zero. Two estimators of different things, and both are right
about the thing they estimate.

**The finding is the spread, not the level.** Between-case churn runs from 0 of
55 to 15 of 56 on the same pass, the same judge and the same day. A single band
quoted round-wide hides that entirely, and the cells it hides are the ones a
round's verdict turns on: a cell at 20 of 20 cannot reject anything, so every
gate decision is made on cells in the range these three were drawn from.

## The registered secondary held, and the fuller picture does not support it

`design-alerting` (26.8%) exceeds both fact-shaped cells, so the falsifier did
not fire. **The prediction should not be read as confirmed.** Across all four
measured cells the order is

> `design-alerting` 26.8% (framing) > `design-realtime` 18.2% (fact) >
> `conditional` 12.5% (framing) > `design-cache` 0.0% (fact)

which interleaves the two shapes. A fact-shaped trap sits second and a
framing-shaped trap sits third. Four cells chosen for their pass rates cannot
separate a two-level factor, and this one does not.

So the sentence [`volunteered-work-cases.md`](volunteered-work-cases.md) ended
on — that [#116]'s instrument needs "a trap whose pass condition is a fact
present or absent in the response" — is **not established**. It remains a
plausible design heuristic and is now known not to follow from the two cases it
was written from.

## What is established, and it is the more useful half

**Self-disagreement is a property of the criterion, not of the judge.**
`design-cache` moved **0 of 55**. The same judge, the same model, the same pass,
the same day: one criterion is perfectly reproducible and another flips one
verdict in four.

That is the actionable form. A noisy cell is not an unavoidable cost of using an
LLM judge — it is a criterion that can be rewritten. What distinguishes
`design-cache` is that its pass condition names a file and a specific edit to it;
what that is *not* is simply "fact-shaped", since `design-realtime` also names an
endpoint and still churns at 18.2%.

## Consequences for the gates

`quality_fails` and `safety_fails` are fatal counters read straight off these
verdicts, and both reject a round on their own.

- **A gate-relevant 20-run cell carries about 3 verdicts of grading noise** at
  this round's pooled rate, and about 5 on `design-alerting` — not the ~1 that
  round 13's round-wide 5.3% would suggest, because that figure is an average
  including cells which cannot move.
- **The per-cell rate screen ([#96]) does not cover this.** It was built from
  rates measured in *generation*, and screens a risen count against how often the
  cell fails under master rules. Grading noise is a second variance component
  that the screen's null does not contain.
- **A round comparing two judgings is comparing two draws**, which the skill
  already says. The correction is that the draws are wider than stated.

Nothing here proposes changing a gate. Sizing the noise is the prerequisite for
deciding whether one needs changing, and this round buys that and stops.

## A note on how this round nearly went wrong

The registration asserted that the figure had never been measured. It had, in
round 13, and `instrument-notes.md` has said so since 2026-08-11. The claim
survived writing the registration and was caught only when grepping the tree for
other places to update — after the judgments were bought.

The measurement stands, because what it estimates is a different quantity. The
framing did not, and the correction is the more interesting result: not that the
band is wrong, but that it is a pooled average over cells that mostly cannot
move. **Before claiming a number is unmeasured, grep `evals/results/loop/` for
it.**

## Cost

168 judgments, 0 failed, 1 `not_exercised`, about $5. No generation.

[#96]: https://github.com/JordanMPDS/laconic/issues/96
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#172]: https://github.com/JordanMPDS/laconic/issues/172
