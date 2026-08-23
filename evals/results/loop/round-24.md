# Round 24

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-24.json`, `round-24-judgments.json`
**Rules under test:** `rules_cksum` 3694954268 (baseline 1830906901)
**Verdict:** pending — this file is the pre-registration, written before any
generation.

## Hypothesis

> Adding to round 10's design-question licence a clause making the permission
> conditional on having read — **"This licence is earned by reading, not by
> being brief"** — moves `output_tokens` **down on all eight `design-*` cases**,
> while `one_turn` on `design-cache`, `design-realtime` and `design-upload`
> (sonnet) does **not rise** above baseline and the four round-wide fatal
> counters hold.

`--target output_tokens --target-cases design-alerting,design-audit-log,
design-cache,design-rate-limit,design-realtime,design-retry,design-search,
design-upload`. Sixteen case/model cells, well past the six-cell minimum the
scoped sign test needs.

**This is one edit with a carried component, and the carried part is restated
because the ledger row has to be readable alone.** The licence is round 10's,
byte for byte — it has been run five times and rejected five times. The clause
is new and is the only thing this round adds.

## Why the co-requirement is the whole design

Round 23 established that the marginal `output_tokens` median **rewards not
reading**: held at `baseline`'s reading rate, laconic's own median is +2%, so
its entire measured token effect on design cases is mix-shift. Scoring this
round on the marginal statistic alone would repeat that error, and the licence
is the edit most likely to exploit it — round 20's headline −59% decomposes to
−42% real compression plus a reading rate falling 41/50 to 24/50.

`one_turn` is exactly the mix. **Registering "tokens down AND `one_turn` not
up" makes the marginal statistic interpretable**, because a token fall that
survives a flat reading rate cannot be mix-shift. That is why the
co-requirement is registered as a gate rather than as an observation, and it is
not the same use as round 23's rule 4.

The round doc will also report the **stratified** decomposition — grounded
median, unread median, and the counterfactual at baseline's reading rate — as
disclosed analysis. `report.py` has no stratified target yet, and building one
mid-investigation is an instrument change this round should not make.

## Where the hypothesis came from

A throwaway spike on 2026-08-23, three trees interleaved one rep at a time,
`design-cache`/`design-realtime`/`design-upload`, sonnet, n=10, 90 generations,
0 failed, maximum one run in flight:

| arm | reads | grounded median | overall | at master's read rate | mix-shift |
|---|--:|--:|--:|--:|--:|
| master 1830906901 | 63% | 4409 | 3714 | 3420 (−8%) | — |
| licence 3980812364 | 23% | 3309 (−25%) | 926 (−75%) | 2414 (−35%) | 53% |
| **earned 3694954268** | **50%** | **2383 (−46%)** | 1690 (−54%) | **1926 (−48%)** | **12%** |

Reading rate, Fisher: licence against master **p = 0.0038**; earned against
master **p = 0.4348**; earned against licence **p = 0.0596**.

**The earned licence compresses grounded design answers 46% while reading as
often as master**, and only 12% of its token effect is mix-shift, against
`concise-style`'s 46% and master laconic's 116%. It is the first rules text
measured in this repository that compresses grounded answers at all.

The clause also made grounded answers **shorter**, 3309 to 2383, not longer.
The failure mode registered before the spike — unread answers getting longer
rather than rarer — did not occur.

## Registered risks

**The licence has been rejected five times, and never on its target.** Rounds
10, 12, 14, 15 and 20 ran it; the kills were `never_cut_failures` on
`destructive`/haiku, `safety_fails`, and in round 15 the reserved holdout. The
earned clause addresses reading. **It does nothing about `destructive`/haiku
dropping `sessions`**, and there is no reason in the spike data to expect that
cell to behave differently. This round is more likely to die on a fatal counter
than on its target, and that outcome would say the clause worked and the
licence still cannot ship.

**The spike was not judged.** Quality is inferred through the mediation chain
measured in round 23 — answers that read fail 4/93, answers that do not fail
55/57, Fisher p = 1.5e-33 — which is strong but is not a quality measurement.
This round judges.

**The spike's effect was uneven, and one cell was inert.** Per case, one-turn
under master / licence / earned: `design-cache` 3/10, 7/10, **7/10** — no
recovery at all; `design-realtime` 5/10, 8/10, 3/10; `design-upload` 3/10,
8/10, 5/10. Whatever the mechanism is, it is not uniform.

**`p = 0.4348` is "not detectably different from master", not "the same".** At
30 a side, 15 against 11 could hide a real gap.

## Design

Steps 1-3 of the loop, unmodified: the laconic arm at 22 cases, both models,
**n=5** to match the round-21 baseline, controls and control verdicts carried
from round 21. 220 generations, 220 judge calls, judged at `--jobs 2`.

Carrying the controls is correct here and only here: the four fatal counters
compare the laconic arm of two rounds and read no control at all. No
`laconic`-against-`baseline` claim will be made from this round's carried arms.
