# Round 47: round 40's edit, on an instrument that can see the thing it edits

**Registration. Nothing below the results line has been computed.** This file,
the edit and the scorer are committed in the same commit, before any
generation, following [round 38](round-38.md) and
[the register pilot](register-inheritance-136.md).

## The edit, byte-identical to round 40's

`rules/laconic.md`, the pre-send checks:

```diff
-Two checks before sending:
+Three checks before sending:

 1. What is the smallest set of claims that fully answers this?
 2. Is anything here something the user did not ask for?
+3. Would this be the same answer if this were the session's first turn?
+   Earlier turns set the subject, never the length.
```

That is [round 40](round-40.md)'s edit reproduced character for character,
deliberately. **The only thing this round changes is the instrument.**

## Why re-run a rejected edit

Round 40 registered `output_tokens` on seven multi-turn sonnet cells —
`drift-service`, `deep-{metric,index,rollback}`, `recall-{metric,index,rollback}`
— and rejected: five of seven moved up, sign test p = 0.4531, median shift +7.5
tokens against a 29.3 floor. Wrong direction in the test and in the point
estimate. The edit was reverted in full.

Three days later the [register pilot](register-inheritance-136.md) established
what those seven cells are:

> `deep-*` cannot produce it, because nothing in `deep-*` asks for a
> licensed-long deliverable. Its turns 2 to 4 are short analysis questions; one
> of the three begins `walk me through`, which is the closest the scored suite
> comes.

And it measured the size of what they are missing. On `deep-*` under `plugin`
delivery, laconic spends **77.5 prose words across all three middle turns**.
There is no inherited register in those sessions to be found — the model's four
prior answers average about 26 words each.

So round 40 tested a licence-expiry clause on sessions where **no licence was
ever granted**. Its null is a null on a condition the clause does not address,
and nothing in it bears on whether the clause works where the mechanism exists.
The pilot built the cells where it does: on `register-*` the same four prior
turns run **704 words**, and the graded turn that follows them runs 52 against
`deep-*`'s 31, at p < 0.00001 with the baseline arm flat as the control.

This round is that re-test, with one variable changed.

## The registered hypothesis

> Editing the pre-send checks to add a third check that recalibrates the answer
> against the current turn alone should **reduce prose words on turn 5 of
> `register-index`, `register-metric` and `register-rollback`**, laconic arm,
> sonnet, `--turn-delivery plugin`.

**Endpoint:** prose words on turn 5 by `metrics.score`, laconic arm, sonnet, 30
runs a side, two-sided permutation of the side label over per-run counts at
200,000 resamples, seed 60.

**Falsifier, registered in advance: `register-*` not separating from its control
at p < 0.05, or separating upward.**

Words rather than round 40's `output_tokens`, because that is the pilot's
registered endpoint, because [#136] is a report about prose, and because the
effect being removed is stated in words (52.0 against 31.0). Naming the same
metric as round 40 would have been the tidier story and the wrong measurement.

**`deep-*` is the registered specificity control**, generated in the same
interleaved batch, with `run.py` looping cases inside one invocation per stem.
Round 40 already used the same idea and the pilot supplies the number: `deep-*`
laconic turn 5 sits at 31 words, which is about as far down as this instrument
goes. Registered reading:

1. **`register-*` falls and `deep-*` does not.** The licence expires, and the
   clause does what [#60] proposal B asks for.
2. **Both fall by similar proportions.** This is a general compression edit, not
   a persistence clause, and the 1.68x carry-forward the pilot measured is
   untouched. The gate's round-wide counters would then be deciding an ordinary
   length edit, and it should be judged as one.
3. **Neither moves.** The clause does not work where the mechanism exists
   either, and [#60]'s proposal B is answered negatively for the first time on
   an instrument that could have seen it.

The arbiter for 1 against 2 is the difference of differences, registered **on
log words** — the pilot's finding is a ratio and the scale-free statement of it
is the register/deep ratio, 1.68 under master rules. Unlike the pilot's
interaction this one is not the broken test round 42 recorded: both groups here
are the laconic arm on the same fixture, so shuffling the side label does not
build a mixture of two modes an order of magnitude apart. The raw-words version
is printed beside it and both come out of `score_persistence.py`, so neither is
recomputed by hand.

## The harm check is fatal to the edit, and it is why this round is worth buying

**Registered: prose words summed over turns 2 to 4 on `register-*`, laconic arm.
A fall significant at p < 0.05 rejects the edit whatever the primary does.**

Those three turns ask, in as many words, for a complete assessment, the whole
argument step by step, and a table with the evidence for each row. The ruleset
promises them full detail — *"Laconic governs volunteered content; it never
truncates requested content"* — and the pilot measured laconic honouring that
promise at 704 words against 77.5 on the plain form, a 9.1x response to the
request.

A clause that tells the model to answer as though this were the session's first
turn can suppress exactly that. [#60] names the risk itself, about its other
proposal: *"this is the kind of edit that could trade one failure mode for the
opposite one."* The instrument that makes the effect visible is the same one
that makes the harm visible, and a round that measured only the primary would
ship the trade without seeing it.

**Free second harm check:** `date_trunc` on the `index` stem, the pair's one
`never_cut` keyword, on the graded turn of all four groups. The other two stems
carry none, so it covers a third of the batch and is stated as such.

## Delivery: `plugin`, and there is no choice about it

Both sides run `--turn-delivery plugin`. `run.py`'s docstring settles it:

> a persistence clause of the kind [#60] asks for cannot be tested under
> `repeat` at all, because `repeat` already over-delivers persistence.

Under `plugin` the added check reaches turn 5 the same way the licence sentence
it modifies does: once, in the turn-1 slice, behind four of the model's own
answers. That is the shipped wiring, and it is the harder test — the clause has
to survive to the turn it governs rather than being re-asserted on it.

## Two trees, generated simultaneously

`rules_cksum` resolves once at `run.py` startup, so the two revisions cannot
share an invocation. Edit side from this branch, control side from a `master`
worktree writing back into this tree, launched together, following
[round 38](round-38.md) — [round 37](round-37.md) measured a syntactic behaviour
moving 4.7x in five days at byte-identical rules, so a sequential window is the
exposure to avoid. Era and CLI release cancel between the sides instead of
confounding them.

```sh
git worktree add /tmp/laconic-control master
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --cases "deep-$stem,register-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 6 \
    --snapshot "evals/snapshots/loop/round-47-edit-$stem.json" &
done
for stem in index metric rollback; do
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --models sonnet --reps 10 --cases "deep-$stem,register-$stem" \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 6 \
    --snapshot "<abs>/evals/snapshots/loop/round-47-control-$stem.json") &
done
```

Six cases across two revisions, ten reps, five turns each: 120 runs and **600
calls**, the same size as the pilot and half what it would cost with a baseline
arm. The baseline arm is not bought, because it carries no rules and therefore
cannot move under a rules edit — the pilot already measured it flat on these
same six prompts (p = 0.9135, mean falling), which is what licenses dropping it
here.

The shard boundary is the stem, so both families of every contrast are generated
inside one process, interleaved; the split is across contrasts, never inside one.
`--concurrency 6` is declared on all six per [#120], because six invocations
really are in flight.

Scored by `python3 evals/pilot/score_persistence.py <control> <edit>`, which
imports its word measure and its tests from `score_register.py` so the two
scorers cannot drift on what a word is.

## What this round does not buy, yet

**No judging, and no round-wide arm, until the scoped target passes.** The skill's
standing order is to buy in sequence and stop at the first step that fails, which
is what saved round 40 its 220-generation arm. If the primary clears and the harm
check holds, the round-wide laconic arm and its judgments are the next purchase
and no rule change ships without them.

**Nothing is promoted.** The pair stays in `evals/pilot`, so `cases_cksum` does
not move and no fatal counter gains an unseeded cell.

## Power, stated before the numbers

The pilot separated 31.0 from 52.0 at 30 runs a side on this exact endpoint at
p < 0.00001. This round is sized identically and is powered to see the effect
being removed, which is the same 21 words in the other direction. It is not
powered for a 5-word shift, so a null here is a null on a large effect. The
floor matters as much as the ceiling: `deep-*` at 31 words is close to the
bottom of what these prompts produce, so a specificity control that "does not
move" is partly a floor and is read as such.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136

<!-- RESULTS BELOW THIS LINE -->

## Result: the falsifier fired on both of its clauses, and the edit moves nothing anywhere

Sonnet, 10 reps a side, **120 runs, 0 failed**, every run five turns. Generated
2026-09-05 from `evals/pilot` at `cases_cksum` 1852778470 — the pilot's value,
unchanged — with the control at `rules_cksum` 136269960 and the edit at
1135334847, which is the checksum the ledger records for round 40. The edit is
byte-identical to it, and the checksum is the proof rather than my word for it.
Six shards declaring `--concurrency 6`; the timestamps reconstruct to 3 in
flight, so the declaration is conservative rather than false.

### Primary: rejected

| family | n | control | edit | ratio | p |
|---|--:|--:|--:|--:|--:|
| **`register-*`** | 30 | **55.5** | **58.0** | **1.045** | **0.9815** |
| `deep-*` | 30 | 29.0 | 28.0 | 0.966 | 0.4699 |

**The falsifier was "not separating at p < 0.05, or separating upward", and both
clauses of it fired.** The registered target does not separate, and the point
estimate is in the wrong direction. Means agree: 55.5 to 55.7 on `register-*`,
28.1 to 30.6 on `deep-*`. The interaction reads p = 0.7257 on raw words and a
ratio of ratios of 0.904 at p = 0.5402 on log words, so registered reading 3
obtains — neither family moves, and there is no effect anywhere to attribute.

**The carry-forward survives the edit intact:**

| | `deep-*` | `register-*` | ratio | p |
|---|--:|--:|--:|--:|
| control | 29.0 | 55.5 | **1.914** | 5e-06 |
| edit | 28.0 | 58.0 | **2.071** | 1e-05 |

That is the finding stated as the pilot states it. The clause was supposed to
drive that ratio toward 1.0. It is 1.914 without the clause and 2.071 with it.

### The edit moves nothing on any of the ten turn positions

Registered analysis is above; this table is not registered and is the reason the
round is worth its 600 calls.

| family | turn | control | edit | p |
|---|--:|--:|--:|--:|
| `deep-*` | 1 | 137.5 | 129.0 | 0.5356 |
| `deep-*` | 2 | 13.5 | 14.0 | 0.8705 |
| `deep-*` | 3 | 28.0 | 31.0 | 0.4749 |
| `deep-*` | 4 | 20.5 | 24.0 | 0.4233 |
| `deep-*` | 5 | 29.0 | 28.0 | 0.4680 |
| `register-*` | 1 | 129.0 | 130.5 | 0.8898 |
| `register-*` | 2 | 197.5 | 188.5 | 0.6229 |
| `register-*` | 3 | 151.5 | 145.0 | 0.9957 |
| `register-*` | 4 | 251.0 | 227.0 | 0.1924 |
| `register-*` | 5 | 55.5 | 58.0 | 0.9811 |

Ten positions, two families, 120 runs, and the smallest p in the table is
0.1924. **Turn 1 is the row that matters.** It carries no inherited register at
all, and it is the turn on which the whole rule slice has just been sent, so a
third item in the pre-send checks is at its most legible there. It does not
move either, on either family.

So the failure is not the one the round was designed to find. This is not a
persistence clause that fails to persist — **it is a checklist item that does not
change the answer at any depth, including the depth at which it was just
read.** Round 40 could not distinguish those two, because it had no cell where
the register existed; this round can, and the answer is the less flattering one.

### The harm check passes, and it passes for the same reason

| family | control | edit | p |
|---|--:|--:|--:|
| `register-*` turns 2-4 | 630.5 | 613.5 | 0.4733 |
| `deep-*` turns 2-4 | 72.0 | 82.0 | 0.4112 |

Registered as fatal: a significant fall would have rejected the edit whatever
the primary did. It does not fall. The trade [#60] warns about did not happen,
which is good news and is also the same null as everything else in the round —
a clause that changes nothing cannot suppress a requested full form either.

**Never-cut keyword, `date_trunc` on the `index` stem, graded turn: 39 of 40.**
The one miss is `control`/`deep`, so it is on master rules and not on the edit.

### The pilot replicates, in an independent batch

The control side is a second, independently generated measurement of the
[register pilot](register-inheritance-136.md), and it was not registered as one —
it is simply what a control arm is.

| | pilot | round 47 control | p |
|---|--:|--:|--:|
| `deep-*` turn 5 | 31.0 | 29.0 | 0.4651 |
| `register-*` turn 5 | 52.0 | 55.5 | 0.3217 |
| `deep-*` turns 2-4 | 77.5 | 72.0 | — |
| `register-*` turns 2-4 | 704.0 | 630.5 | — |
| ratio | 1.677 | 1.914 | — |

Neither turn-5 figure differs. The pilot's own limits section said "one batch,
one date, three stems, ten reps" and that nothing in it replicated; one of those
two is now false. Pooling both sides of this round, 60 runs a family, the
carry-forward reads **28.0 against 56.5, a ratio of 2.018 at p = 5e-06**.

The length licence also holds a second time: laconic writes **8.8 times** as much
across turns 2 to 4 when the full form is asked for as when the same three
questions are asked plainly, against the pilot's 9.1.

## Verdict: reject, and the edit is reverted in full

Per the stop-at-the-first-failing-step order, the round-wide laconic arm and its
judgments were not bought. `rules/laconic.md` returns to two pre-send checks and
`rules/dist/` is regenerated from it.

## What this settles, and what it costs

**Round 40's null was not an instrument failure.** That was this round's
premise, and it is wrong. The clause reads the same on a session that spent 630
words under an explicit licence as on one that spent 72, which is the contrast
round 40 could not construct. [#60]'s proposal B is now answered negatively on
an instrument that could have seen it, which is the first time anything in the
cluster can say that.

**What is left standing is the mechanism, twice measured, with nothing that
moves it.** The carry-forward is real at 1.9x to 2.1x across four independent
generations of it. Five rule attempts have now been made at the over-length
cluster and all five are nulls, four of them bounding a licence with another
sentence and this one adding a step to the checklist instead.

**The next thing to try is not another sentence in `rules/laconic.md`, and this
round is the evidence for that.** Under the shipped wiring turn 5 receives the
slice once, thousands of tokens and four of its own answers ago, plus a
one-line reminder that names the level and nothing else. The one channel that
actually reaches the turn where the failure happens has never been edited. That
is `hooks/laconic.sh`'s `REMINDER`, mirrored in `hooks/laconic.ps1` and in
`run.py`, and moving it is a three-file change with a bash/PowerShell parity
requirement rather than a one-line rule edit — which is presumably why four
rounds went to the rules file first. The instrument to score it on now exists
and has a control measured four times.

**Turn 1 is the caveat on that recommendation.** The clause did not move turn 1
either, where delivery cannot be the explanation, so "the reminder is the
channel" is the next hypothesis and not the established reason. A round on the
reminder line has to keep turn 1 in scope for exactly that reason.
