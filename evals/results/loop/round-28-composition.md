# Round 28: does the composition win convert into fewer failures?

Round 28 accepted on `unread_asks` while its round-wide `quality_fails` count
went the other way, 90 to 94. The strata disclosure showed why in outline: the
edit moved 46 answers out of the hands-back stratum, which fails at about a
third, into the resolving one, which fails at about a sixth — and the count did
not follow.

This asks the obvious next question. **Do the answers that moved fail more than
the ones already there?** If they do, the composition win is cosmetic.

Nothing here is a gate or a re-score. It is computed on the 896 judged runs
already committed with round 28; **no generation was bought**. Sonnet, the eight
`design-*` cases, the shipped v2 detector.

Reproduce with
[`round-28-composition/permute.py`](round-28-composition/permute.py).

## The reading that looked like an answer, and is wrong

Both arms carry the same `(case, model, rep)` keys, so each key can be
classified by what the two arms did, and the round-wide change decomposes
exactly:

| group | n | control fails | edit fails | delta |
|---|--:|--:|--:|--:|
| always resolved | 302 | 50 (16.6%) | 58 (19.2%) | +8 |
| switched into resolving | 88 | 30 (34.1%) | 19 (21.6%) | **−11** |
| switched into hands-back | 42 | 6 (14.3%) | 11 (26.2%) | +5 |
| always handed back | 16 | 4 (25.0%) | 6 (37.5%) | +2 |
| **total** | **448** | **90** | **94** | **+4** |

Read naively this says the composition win is real and large: the 88 answers
that stopped handing back fell from 34.1% to 21.6%, the biggest movement in the
table, and three smaller rises ate it.

**That reading is an artifact, and the table cannot support it.**

## The permutation that refutes it

Conditioning on what the control arm did selects that arm's noise. The keys
where control handed back are keys where control did badly, and the edit's run
at that key is an independent generation, so it regresses to the edit's own
mean. The signature is visible without any test: the edit's rate in the
"switched into resolving" group is **21.6%**, and the edit's marginal rate over
all 448 runs is **21.0%**. The group is not better than the edit's average; it
*is* the edit's average.

Shuffling the edit arm's runs within each case makes this exact. The shuffle
destroys every key-level correspondence while preserving every marginal — each
case's edit hands-back share and its failure rate are untouched — so any delta
that survives is an effect and any delta it reproduces is the artifact. 2000
shuffles, seed 28:

| group | observed | null mean | 95% null band | |
|---|--:|--:|:--:|---|
| always resolved | +8 | +8.1 | [+1, +15] | inside |
| switched into resolving | **−11** | **−9.7** | [−16, −4] | **inside** |
| switched into hands-back | +5 | +5.6 | [+1, +10] | inside |
| always handed back | +2 | +0.0 | [−2, +3] | inside |

**Every group is reproduced by the shuffle, the −11 most exactly of all.** There
is no key-level signal in round 28's data. The decomposition is arithmetically
true and causally empty, and any future round tempted to read strata this way
should run this shuffle first.

## What survives, and it does not favour the edit

Only the unconditional comparison is usable, and it is the one `report.py`
already prints:

| stratum | control | edit | one-sided |
|---|--:|--:|--:|
| resolves | 56/344 (16.3%) | 77/390 (19.7%) | rise p = 0.131 |
| hands back | 34/104 (32.7%) | 17/58 (29.3%) | fall p = 0.397 |

Take the 344 answers that were always going to resolve as unchanged at 16.3%,
and the 46 incoming answers must carry the remaining 21 failures — an implied
**45.7%**, worse than the 32.7% stratum they came from. Take the other extreme,
that the incoming answers keep their old 32.7%, and the stratum should hold 71
failures against the **77 observed**.

**Both bounds land on the same conclusion: there is no evidence in this round
that moving an answer out of hands-back makes it any less likely to fail.** The
observed resolving rate is at or above what you would predict if the incoming
answers simply carried their old failure rate with them.

## The answer

**The composition win is not shown to convert into fewer failures**, which is
exactly what the flat round-wide count was already saying. Round 28 buys a
behaviour — answers that never opened a file stop handing the decision back —
and this analysis finds nothing to suggest the behaviour is worth buying on
quality grounds.

Two limits on that, both real:

1. **Nothing here is significant.** The resolving stratum's rise is p = 0.131
   and the hands-back fall is p = 0.397. The round is powered for `unread_asks`,
   not for a three-point movement in a stratum rate, and a null at this power is
   weak evidence.
2. **`unread_asks` was never a quality proxy.** It was built because `one_turn`
   is a diluted proxy for a harm round 26 measured directly, and it stays
   target-only for reasons this analysis does not touch. What this adds is that
   the case for the edit rests on the behaviour itself, not on a measured
   quality gain, and the round doc should be read that way.
