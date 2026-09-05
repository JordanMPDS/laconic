# Round 48: the same clause, in the one channel that reaches the turn where it fails

**Registration. Nothing below the results line has been computed.** This file,
the edit and the instrument stamp are committed in the same commit, before any
generation, following [round 38](round-38.md), the
[register pilot](register-inheritance-136.md) and [round 47](round-47.md).

## The edit is not in `rules/laconic.md`

It is the one line the plugin sends at every `UserPromptSubmit`, in all three
places that line lives:

```diff
-LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.
+LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words. Would this be the same answer if this were the session's first turn? Earlier turns set the subject, never the length.
```

`hooks/laconic.sh:204`, `hooks/laconic.ps1:233` and `evals/bench/run.py`'s
`REMINDER` constant, which `tests/test_bench.py` already pins to the hook's text
so the harness cannot measure a line the product does not send.

**The appended sentence is round 40's and round 47's third pre-send check, byte
for byte.** Same words, twice rejected out of the rules slice. The only variable
this round changes is which channel carries them:

| round | text | channel | instrument | verdict |
|---|---|---|---|---|
| [40](round-40.md) | the clause | `rules/laconic.md` slice | `deep-*`, `recall-*`, `drift-service` | reject, p = 0.4531 |
| [47](round-47.md) | the clause, byte-identical | `rules/laconic.md` slice | `register-*` against `deep-*` | reject, p = 0.9815 |
| 48 | the clause, byte-identical | `UserPromptSubmit` reminder | `register-*` against `deep-*` | — |

Round 47 changed the instrument and held the channel. This round holds the
instrument — the same pair, the same scorer, the same seed — and changes the
channel.

## Why the channel, and why this is not a fifth sentence in the rules file

[Round 47](round-47.md) names it as the next thing to try and is the evidence
for it:

> Under the shipped wiring turn 5 receives the slice once, thousands of tokens
> and four of its own answers ago, plus a one-line reminder that names the level
> and nothing else. The one channel that actually reaches the turn where the
> failure happens has never been edited.

Five rule attempts have now been made at the over-length cluster and all five are
nulls: four bounded a licence with another sentence, and round 47 added a step to
the checklist instead. Every one of them was delivered the same way — inside a
1,800-word slice sent once, on turn 1.

The reminder is the opposite kind of channel. It is 14 words, it is the only
laconic text on the current turn, and it arrives immediately before the prompt it
governs. Adding this sentence more than doubles it, which is a different
treatment rather than a fifth repetition of the same one.

**Round 47's own caveat is the argument against, and it is registered here as
the reason this round can fail.** Round 47's clause did not move turn 1 either,
where the whole slice had just been sent and legibility is at its maximum. If the
sentence is simply inert, moving it to a better channel changes nothing, and this
round is what establishes that. See [Turn 1](#turn-1-is-an-internal-negative-control-by-construction-and-that-is-a-limit-not-a-feature)
below for why the harness cannot settle it directly.

## The registered hypothesis

> Appending the persistence clause to the `UserPromptSubmit` reminder should
> **reduce prose words on turn 5 of `register-index`, `register-metric` and
> `register-rollback`**, laconic arm, sonnet, `--turn-delivery plugin`.

**Endpoint:** prose words on turn 5 by `metrics.score`, laconic arm, sonnet, 30
runs a side, two-sided permutation of the side label over per-run counts at
200,000 resamples, seed 60. Identical to round 47's endpoint, deliberately, so
the two rounds are comparable line for line.

**Falsifier, registered in advance: `register-*` not separating from its control
at p < 0.05, or separating upward.**

**`deep-*` is the registered specificity control**, generated in the same
interleaved batch. The registered readings are round 47's, unchanged:

1. **`register-*` falls and `deep-*` does not.** The licence expires when the
   clause is delivered on the turn it governs, and the channel was the problem.
2. **Both fall by similar proportions.** A general compression edit to the
   reminder, not a persistence clause. It would then have to be judged as an
   ordinary length edit, against the round-wide fatal counters.
3. **Neither moves.** The clause is inert wherever it is put, and the over-length
   cluster's sixth null is a null about the text rather than about delivery.

The arbiter for 1 against 2 is the difference of differences, registered **on log
words**, because the effect being removed is stated as a ratio: register over
deep is 1.914 in round 47's control and 2.018 pooled over four generations of it.
Both come out of `score_persistence.py`, which imports its word measure from
`score_register.py` so the scorers cannot drift on what a word is.

## The harm check is fatal, and it is larger here than in round 47

**Registered: prose words summed over turns 2 to 4 on `register-*`, laconic arm.
A fall significant at p < 0.05 rejects the edit whatever the primary does.**

Those three turns ask, in as many words, for a complete assessment, the whole
argument step by step, and a table with the evidence for each row. The ruleset
promises them full detail — *"Laconic governs volunteered content; it never
truncates requested content"* — and the pilot measured laconic honouring that at
704 words against 77.5 on the plain form, a 9.1x response to the request, which
round 47 replicated at 8.8x.

**This round's prior of harm is higher than round 47's, and that is the whole
point of running it.** Round 47's clause reached turns 2 to 4 the way it reached
turn 5: once, on turn 1, behind everything else. This one is prepended to every
single one of those turns, immediately before the request it might suppress. A
reminder that asks "would this be the same answer on the first turn?" arriving
directly above *"give me the complete assessment, every phase written out in
full"* is exactly the trade [#60] warned about:

> this is the kind of edit that could trade one failure mode for the opposite one.

The instrument that makes the effect visible is the same one that makes the harm
visible. An edit that buys turn 5 by truncating turns 2 to 4 is rejected, and on
this design it cannot hide.

**Free second harm check:** `date_trunc` on the `index` stem, the pair's one
`never_cut` keyword, on the graded turn of all four groups. The other two stems
carry none, so it covers a third of the batch and is stated as such. Round 47
read 39/40 on master rules, the one miss included.

## Turn 1 is an internal negative control by construction, and that is a limit, not a feature

Under `--turn-delivery plugin` the harness sends the reminder on turns 2 and
later only; turn 1 gets the slice alone. So **this edit cannot reach turn 1 in
the instrument**, and a turn-1 movement in the results would be batch noise or a
broken harness rather than an effect. It is reported for that reason.

**In the shipped product turn 1 does receive it**, because `SessionStart` and
`UserPromptSubmit` both fire before the first prompt. The instrument is
one reminder short of the product on exactly one turn, and it has been for every
round since 40. Correcting that would change the instrument in the same round as
the treatment, which is the mistake round 47 exists to avoid, so it is recorded
here as a limit and filed rather than fixed: this round measures the reminder as
a *later-turn* channel, and says nothing about what the added sentence does to a
first answer.

That is also the honest reading of the caveat round 47 left. It asked for turn 1
to stay in scope, and it does, but as a null control rather than as the test of
whether the sentence is inert. What can be said either way is bounded, and it is
bounded before the numbers are in.

## The instrument stamp `rules_cksum` cannot supply

Both sides of this round carry **the same `rules_cksum`**, by construction:
`rules/laconic.md` is byte-identical on the branch and on master. The treatment
is invisible to every guard the harness has, which would leave two snapshots
whose metadata cannot say which one holds the edit.

`run.py` now stamps `reminder_cksum` into a new snapshot's metadata, and
`score_persistence.py` prints both checksums and warns only when *both* agree.
That is the [#69] guard's reasoning applied to the line [#69] did not cover. It
is a metadata field only: it changes nothing about what is sent to the model, and
the resume-refusal half of the `rules_cksum` guard is deliberately not built,
because it needs harness-driving test machinery that does not exist and the
detection this buys is enough for a round whose two sides live in two fixed
trees. **Operational rule for this round: a shard is resumed from the tree that
started it, and the scorer's header is checked before the numbers are read.**

## Delivery: `plugin`, and there is no choice about it

Both sides run `--turn-delivery plugin`. Under `repeat` there is no reminder at
all — the whole slice is re-appended every turn — so the channel this round edits
does not exist in that mode, and `run.py`'s docstring already refuses the
comparison for the older reason:

> a persistence clause of the kind [#60] asks for cannot be tested under
> `repeat` at all, because `repeat` already over-delivers persistence.

## Two trees, generated simultaneously

Round 38's design, unchanged. The edit side runs from this branch and the control
side from a `master` worktree writing back into this tree, launched together, so
era and CLI release cancel between the sides instead of confounding them —
[round 37](round-37.md) measured a syntactic behaviour moving 4.7x in five days
at byte-identical rules.

Here the two trees are load-bearing in a second way: `REMINDER` is resolved at
import, so the two revisions cannot share an invocation any more than two rules
revisions can.

```sh
git worktree add /tmp/laconic-control master
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --cases "deep-$stem,register-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 6 \
    --snapshot "evals/snapshots/loop/round-48-edit-$stem.json" &
done
for stem in index metric rollback; do
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --models sonnet --reps 10 --cases "deep-$stem,register-$stem" \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 6 \
    --snapshot "<abs>/evals/snapshots/loop/round-48-control-$stem.json") &
done
```

Six cases across two revisions, ten reps, five turns each: 120 runs and **600
calls**, the same size as round 47 and the pilot. The baseline arm is not bought:
it carries no rules, so `call_turns` sends it no reminder at all and the edit
cannot reach it. The pilot already measured it flat on these same six prompts
(p = 0.9135).

The shard boundary is the stem, so both families of every contrast are generated
inside one process, interleaved; the split is across contrasts, never inside one.
`--concurrency 6` is declared on all six per [#120], because six invocations
really are in flight. Shards are merged per side with `evals/bench/merge.py` and
scored by `python3 evals/pilot/score_persistence.py <control> <edit>`.

## What this round does not buy, yet

**No judging, and no round-wide arm, until the scoped target passes.** The
skill's standing order is to buy in sequence and stop at the first step that
fails, which is what saved round 40 and round 47 their 220-generation arms.

**An accept here is more expensive than a rules accept, and that is registered
too.** This edit ships in `hooks/laconic.sh` and `hooks/laconic.ps1`, so it
reaches every turn of every session at every level, including the single-turn
sessions this instrument does not cover. If the primary clears and the harm check
holds, the round-wide laconic arm and its judgments are the next purchase, and no
hook change ships without them.

**Nothing is promoted.** The pair stays in `evals/pilot`, so `cases_cksum` does
not move and no fatal counter gains an unseeded cell.

## Power, stated before the numbers

The pilot separated 31.0 from 52.0 at 30 runs a side on this exact endpoint at
p < 0.00001, and round 47 reproduced the gap at 29.0 against 55.5. This round is
sized identically and is powered to see that effect removed — the same 21 to 26
words in the other direction. It is not powered for a 5-word shift, so a null
here is a null on a large effect. `deep-*` at 28 to 31 words is close to the
floor of what these prompts produce, so a specificity control that "does not
move" is partly a floor and is read as such.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136

<!-- RESULTS BELOW THIS LINE -->

## Result: the falsifier fired, and the channel was not the problem either

Sonnet, 10 reps a side, **120 runs, 0 failed**, every run five turns. Generated
2026-09-05 from `evals/pilot` at `cases_cksum` 1852778470 — the pilot's value and
round 47's, unchanged. Both sides carry `rules_cksum` 136269960, as registered;
the contrast is `reminder_cksum`, `None` on the control against **3208985445** on
the edit. Six shards declaring `--concurrency 6`; the timestamps reconstruct to 3
in flight, so the declaration is conservative rather than false.

### Primary: rejected

| family | n | control | edit | ratio | p |
|---|--:|--:|--:|--:|--:|
| **`register-*`** | 30 | **59.5** | **54.5** | **0.916** | **0.6595** |
| `deep-*` | 30 | 28.5 | 20.5 | 0.719 | 0.4366 |

**The falsifier was "not separating at p < 0.05, or separating upward", and the
first clause fired.** The registered target does not separate. The interaction
reads p = 0.9926 on raw words and a ratio of ratios of 1.050 at p = 0.7714 on log
words, the registered arbiter, so **registered reading 3 obtains**: neither family
moves, and there is no effect anywhere to attribute.

What movement the point estimates show goes the wrong way for the hypothesis.
`deep-*`, the specificity control, falls further than the target — 0.719 against
0.916 — so the scale-free statement the clause was supposed to drive toward 1.0
goes up rather than down:

| | `deep-*` | `register-*` | ratio | p |
|---|--:|--:|--:|--:|
| control | 28.5 | 59.5 | **2.088** | 5e-06 |
| edit | 20.5 | 54.5 | **2.659** | 5e-06 |

Neither side of that comparison is significant on its own, so this is a direction
rather than a finding. It is reported because the registered prediction was the
opposite direction, and a null that also points the wrong way is weaker evidence
for the edit than a null that points the right way and misses.

### Turn 1 behaved as the negative control it was registered to be

| family | turn | control | edit | p |
|---|--:|--:|--:|--:|
| `deep-*` | 1 | 124.5 | 125.5 | 0.6572 |
| `deep-*` | 2 | 15.0 | 20.0 | 0.0364 |
| `deep-*` | 3 | 34.0 | 27.5 | 0.3743 |
| `deep-*` | 4 | 27.0 | 21.5 | 0.4940 |
| `deep-*` | 5 | 28.5 | 20.5 | 0.4366 |
| `register-*` | 1 | 125.0 | 138.0 | 0.2113 |
| `register-*` | 2 | 199.0 | 165.5 | 0.6248 |
| `register-*` | 3 | 148.0 | 170.5 | 0.6491 |
| `register-*` | 4 | 245.0 | 218.0 | 0.4680 |
| `register-*` | 5 | 59.5 | 54.5 | 0.6595 |

The edit cannot reach turn 1 in this instrument, and turn 1 does not move on
either family. That is the harness confirming it delivered the treatment where it
said it would and nowhere else, which is the one thing this table was registered
to check.

**Two cells in the exploratory tables fall under 0.05 and neither survives being
counted.** `deep-*` turn 2 moves *up* at p = 0.0364 here, and `deep`/`index` moves
*down* at p = 0.0181 in the by-stem table. Sixteen uncorrected cells across the
two tables, two under 0.05 in opposite directions, both on the specificity
control rather than the target: that is what chance produces. Bonferroni over the
six stem cells asks for 0.0083 and neither reaches it.

### The harm check passes

| family | control | edit | p |
|---|--:|--:|--:|
| `register-*` turns 2-4 | 656.0 | 605.0 | 0.5260 |
| `deep-*` turns 2-4 | 79.0 | 73.5 | 0.9976 |

Registered as fatal, with a prior of harm this round explicitly called higher
than round 47's: this sentence is prepended to turns 2 to 4 themselves,
immediately above requests for a complete assessment, the whole argument step by
step, and a table of evidence. It does not suppress them. The trade [#60] warns
about did not happen — and, as in round 47, that is the same null as everything
else, because a clause that changes nothing cannot truncate a requested full form
either.

**Never-cut keyword, `date_trunc` on the `index` stem, graded turn: 40 of 40**,
both sides, all four groups. Round 47 read 39/40.

### The carry-forward replicates a third time, in the channel that was supposed to remove it

The control side is a third independent measurement of the
[register pilot](register-inheritance-136.md), after round 47's.

| | pilot | round 47 control | round 48 control |
|---|--:|--:|--:|
| `deep-*` turn 5 | 31.0 | 29.0 | 28.5 |
| `register-*` turn 5 | 52.0 | 55.5 | 59.5 |
| `deep-*` turns 2-4 | 77.5 | 72.0 | 79.0 |
| `register-*` turns 2-4 | 704.0 | 630.5 | 656.0 |
| ratio | 1.677 | 1.914 | **2.088** |

Round 48's control does not differ from round 47's on either family — `deep-*` at
p = 1.0000 and `register-*` at p = 0.6037. Pooling both sides of this round, 60
runs a family, the carry-forward reads **26.0 against 58.0, a ratio of 2.231 at
p < 0.0001**.

The length licence holds a third time as well: laconic writes **8.3 times** as
much across turns 2 to 4 when the full form is asked for as when the same three
questions are asked plainly, against round 47's 8.8 and the pilot's 9.1. The
edit side reads 8.2, so the clause does not touch that either.

## Verdict: reject, and the edit is reverted in full

Per the stop-at-the-first-failing-step order, the round-wide laconic arm and its
judgments were not bought. `hooks/laconic.sh`, `hooks/laconic.ps1` and `run.py`'s
`REMINDER` return to the one-line reminder, byte-identical to `origin/master`.

## What this settles

**The channel was the last untested variable in the over-length cluster, and it
is not the carrier.** Five rule attempts had put this text, and texts like it,
into the 1,800-word slice sent once on turn 1. The standing objection was that
the slice is thousands of tokens and four answers away from the turn where the
failure happens, so a null there might be a delivery failure rather than a
finding about the text. This round moved the identical sentence into the one
channel that arrives immediately before the prompt it governs, more than doubling
a 14-word line, and got the sixth null.

**So the cluster's nulls are about the sentence, not about where it was put.**
Round 47 established that the clause does not work when the register exists;
round 48 establishes that it does not work when delivered on the turn it governs.
Together they close [#60]'s proposal B: a self-directed pre-send question does not
shorten a laconic answer, at any depth, through either channel the product has.

**What remains standing is the mechanism, now measured three times.** A laconic
session whose prior answers ran long under an explicit licence answers the
identical closed question with roughly twice the words, at 1.677, 1.914 and 2.088
across three independent batches and 2.231 pooled over this round's 120 runs. It
is the most reproducible effect in the loop, and nothing written into the rules or
the reminder has moved it.

**What this round does not say.** It measures the reminder as a *later-turn*
channel only. Turn 1 receives the reminder in the shipped product and cannot in
this harness, as registered above, so nothing here bounds what the added sentence
would do to a first answer. That gap is the instrument's, it predates this round,
and it stays filed rather than fixed.

**The next thing to try is not a sixth sentence.** Six nulls through two channels
is a negative result about the intervention class: instructing the model to check
its own length does not change its length. An intervention that changes what the
model *sees* — the licence's own wording in [#150], which is the clause the
register is inherited through — is a different class and is where the cluster's
remaining value is.
