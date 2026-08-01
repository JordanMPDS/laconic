# Blind pairwise preference — 2026-08-01

**A blind judge did not prefer laconic's answers to baseline's, and the run does
not establish the reverse either.** Against baseline the tally is laconic 37,
baseline 52, 21 ties (sign test on the 89 decided comparisons, p = 0.137). The
same judge picked the longer of the two answers in 63% of decided comparisons
(p = 0.019) and reversed its verdict on 35% of the comparisons it was shown
twice. Both of those effects are larger and better attested than the difference
between the arms, so the tally is reported as measured and no preference claim
is made from it.

This closes the gap [#22](https://github.com/JordanMPDS/laconic/issues/22)
opened: the plugin's *mechanism* was measured and its *reception* was not.
Reception is now measured. It did not come back favourable, and it did not come
back interpretable either — which the issue anticipated in writing before any
call was made.

Nothing here touches the compression or readability figures in
[`2026-07-31-benchmark.md`](2026-07-31-benchmark.md). Those come from
deterministic offline scoring with no judge in the loop.

## Run configuration

| | |
|---|---|
| Comparisons | 130 per control arm (110 forward + 20 flipped) |
| Responses | Reused from `evals/snapshots/results.json` — nothing regenerated |
| Arms compared | `laconic` vs `baseline`, and `laconic` vs `terse-control` |
| Judge | `sonnet`, one call per comparison, arm labels stripped |
| Cases | All 11, both models, 5 reps |
| Harness | `evals/bench/prefer.py` |
| Snapshots | `evals/snapshots/preferences.json`, `evals/snapshots/preferences-terse.json` |

Every comparison ran in a fresh temp directory rather than the repo, so the
judge could reach neither `rules/laconic.md` nor the arm labels in
`results.json`. A/B position comes from a checksum of `(case, model, rep)`,
never from the arm; laconic sat in position A for 46 of the 110 comparisons and
in B for 64.

## Headline: laconic vs baseline

| arm | wins |
|---|--:|
| laconic | 37 (34%) |
| baseline | 52 (47%) |
| tie | 21 (19%) |

| model | laconic | baseline | tie |
|---|--:|--:|--:|
| haiku | 21 | 24 | 10 |
| sonnet | 16 | 28 | 11 |

The direction favours baseline and the difference is not significant: 37 of 89
decided comparisons, two-sided exact binomial p = 0.137.

## The two effects that outrank it

**Length.** The judge picked the longer answer in **56 of 89** decided
comparisons — 63%, p = 0.019. laconic was the shorter answer in 65 of those 89
pairs, by construction. The bias documented in the literature is present in this
run, it is statistically stronger than the arm difference, and it runs against
the treatment. A loss no larger than the length effect is not a preference
result.

**Position.** The judge favours whichever answer it reads second:

| laconic shown as | wins | losses | ties | win rate |
|---|--:|--:|--:|--:|
| A | 13 | 28 | 5 | 32% |
| B | 24 | 24 | 16 | 50% |

Same responses, same judge, same prompt; only the side changed. Fisher's exact
on that 2×2 gives p = 0.090. Counting by position rather than by arm, the second
answer won 52 comparisons and the first won 37.

**Flips.** Of the 20 comparisons run in both orders, **7 changed verdict (35%)**,
3 of them a full reversal rather than a move across the tie boundary.

Read together: an instrument whose verdict moves on a third of re-presentations,
which prefers the longer answer at p = 0.019, reported a 37–52 split at
p = 0.137. That is not evidence about laconic.

## laconic vs terse-control: withheld

The second comparison hit the threshold the harness refuses to publish past.

**Order flip rate: 10 of 20 (50%).** `prefer.py` prints, and this document
honours, the rule that at or above 50% the judge is measuring position rather
than quality. The tally below is therefore published as instrument diagnostics
only, and **may not be cited as a preference between laconic and a plain "answer
concisely" instruction** in either direction.

| arm | wins | | laconic shown as | win rate |
|---|--:|---|---|--:|
| laconic | 42 (39%) | | A | 30% |
| terse-control | 51 (47%) | | B | 58% |
| tie | 15 (14%) | | | |

Two comparisons returned unparseable verdicts (`decision` and `fail-open`, both
sonnet) and are excluded from the tally rather than counted as ties. The
position spread here is wider than in the baseline run — 30% against 58% —
which is consistent with the 50% flip rate and is why the arm numbers say
nothing.

## Per case, against baseline

Ranked by laconic wins. Five reps × two models = 10 comparisons per case.

| case | laconic | baseline | tie |
|---|--:|--:|--:|
| `destructive` | 6 | 4 | 0 |
| `stale-cache` | 5 | 5 | 0 |
| `walkthrough` | 5 | 4 | 1 |
| `code-fidelity` | 4 | 3 | 3 |
| `conditional` | 4 | 5 | 1 |
| `decision` | 4 | 4 | 2 |
| `ordered-steps` | 4 | 2 | 4 |
| `silent-success` | 3 | 6 | 1 |
| `fail-open` | 1 | 4 | 5 |
| `floor` | 1 | 6 | 3 |
| `badnews` | 0 | 9 | 1 |

### `badnews` is the one case with a legible reason, and it is not position

laconic lost 0–9. The judge's stated reasons converge on a single missing
detail — the pass count:

> "B gives the full picture with '44 of 47 tests passed' (making the total scope
> explicit) and precise Decimal values, whereas A's '44 tests passed overall'
> leaves the total ambiguous and adds unrequested causal speculation instead of
> just offering to dig further."

> "B includes the pass count (44 passed) giving a fuller picture of the run and
> uses precise Decimal notation matching likely actual output, while both are
> otherwise equivalent in identifying the failures."

Both halves of that check out against the responses, counted directly rather
than taken from the judge:

- **laconic named the failures in all 10 responses**, 3 to 4 `test_*`
  identifiers each — indistinguishable from baseline's 3 to 5. The bad-news
  item held.
- **laconic gave the total in 1 of 10 responses against baseline's 6.** That is
  the difference the judge is describing.

Whether that difference is a defect is exactly what this case disagrees with the
judge about. `evals/cases/badnews/expect.json` fails a response that "buries
[the failures] under the passing count" — the case was written on the view that
leading with 44 passing tests is how a report hides three broken ones, and the
judge has just rewarded including it. Two defensible readings of the same
number: scale for the reader, or cover for the failures.

No rule change follows from one case graded by one judge that its own criteria
contradict. It is recorded here because it is the only thing in the run that is
checkable independent of the tally, and because the next revision of
`rules/laconic.md` should settle deliberately whether a denominator is context
or padding.

`floor` (1–6) has the opposite shape and no such lesson. Its ties read
"differing only in trivial stylistic presentation"; its losses are the length
effect on a question where both answers are correct and short.

## What this does and does not change

- **It does not change any published figure.** Compression, readability,
  latency, cost, and the never-cut check are computed offline by
  `evals/bench/report.py` with no judge involved.
- **It does not license a "laconic answers are nicer to read" claim**, which was
  never made, and this run supplies no basis for making one.
- **It does not establish the reverse either.** A loss at p = 0.137, from an
  instrument with a measured 63% length bias and a 35% flip rate, is not
  evidence that laconic's answers serve readers worse.
- **It surfaces one checkable disagreement**: the `badnews` denominator, above,
  where the judge and the case's own criteria want opposite things.
- **It fixes the taxonomy gap.** `evals/CRITERIA.md` now carries `preference` as
  a fourth grading class with these limits attached, so a future run cannot be
  read as an answer-quality result.

## Honesty notes

1. **A model's preference is not a reader's.** The claim this instrument can
   support is "a judge preferred X", never "readers prefer X". A human
   preference study is not in scope and is not planned.
2. **The judge is a Claude model grading Claude outputs.** Same limit as
   `judge.py`, and the same limit the answer-quality result carries.
3. **n = 20 for the flip rate**, so 35% carries a wide interval. It is enough to
   establish that verdicts move, not to pin how often.
4. **The A/B split was 46/64, not 55/55.** The checksum is deterministic, not
   balanced, and the imbalance placed laconic in the favoured second position
   more often than chance — which makes the loss no easier to dismiss, but does
   mean the headline tally is not position-neutral. The per-position table is
   the one to read.
5. **Two verdicts were unparseable** in the terse-control run and are excluded
   rather than counted. Both are recorded in the snapshot with reason
   `unparseable`.
6. **The comparison is single-judgment.** Each comparison was judged once, not
   by a panel. A three-judge majority would cost three times as much and is the
   obvious way to cut the flip rate if this is ever re-run.
7. **`terse-control` is withheld, not buried.** Its tables are above with the
   reason attached. A 50% flip rate is the harness's own refusal threshold and
   was set before the numbers came back.

## Reproduce

```bash
python3 evals/bench/prefer.py --dry-run                        # count calls, spend nothing
python3 evals/bench/prefer.py --control baseline --jobs 6
python3 evals/bench/prefer.py --control terse-control --jobs 6 \
  --out evals/snapshots/preferences-terse.json
python3 evals/bench/prefer.py --report-only                    # offline tally, no calls
```

The snapshots are committed, so `--report-only` reproduces every table in this
document without a single API call.
