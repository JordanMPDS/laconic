# Round 49: the licence's own wording, on the instrument that can see the register

**Registration. Nothing below the results line has been computed.** This file,
the edit and the regenerated `rules/dist/*.md` are committed in the same commit,
before any generation, following [round 38](round-38.md), the
[register pilot](register-inheritance-136.md), [round 47](round-47.md) and
[round 48](round-48.md).

## The edit is round 29's, byte for byte

`rules/laconic.md:12-15`, the length-scaling paragraph:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets full detail. Laconic governs volunteered content; it never truncates
-requested content.
+gets the claims it needs, each made once: both checks above run inside
+requested content. Laconic governs volunteered content; it never truncates
+requested content, and it never licenses restating a claim the answer has
+already made.
```

**The checksum proves the text is identical to round 29's.** This branch's
laconic slice reads `rules_cksum` **3990961107**, which is the value in round
29's [`LEDGER.md`](LEDGER.md) row. The only variable this round changes is the
instrument the text is scored on:

| round | text | instrument | endpoint | verdict |
|---|---|---|---|---|
| [29](round-29.md) | the licence edit | `walkthrough` + three `verdict-*`, both models | `output_tokens`, 8 cells | reject, sign test p = 1.000 |
| 49 | the licence edit, byte-identical | `register-*` against `deep-*`, sonnet | turn-5 prose words | — |

That is round 47's design applied to a different text: round 47 held the text
and changed the instrument, round 48 held the instrument and changed the
channel, and both were readable because exactly one thing moved.

## Why this round exists

[Round 48](round-48.md) closed [#60]'s proposal B and said what was left:

> **The next thing to try is not a sixth sentence.** Six nulls through two
> channels is a negative result about the intervention class: instructing the
> model to check its own length does not change its length. An intervention that
> changes what the model *sees* — the licence's own wording in [#150], which is
> the clause the register is inherited through — is a different class and is
> where the cluster's remaining value is.

The clause is the one the register pilot's `register-*` cases invoke by name.
`expect.json` on all three says so:

> Turns 2 to 4 ask deep-index's three questions verbatim and add an explicit
> request for the full form — a complete checklist, the whole argument step by
> step, a table with the evidence for each row — which rules/laconic.md licenses
> at length ("a report, walkthrough, comparison, or explanation the user asked
> for gets full detail").

So the sentence this round edits is the sentence that produces the treatment the
pilot measured. Six rule and reminder attempts have tried to make a licensed
register expire by adding a second sentence telling the model to check itself.
None has touched the licence.

## Why round 29's null is not this round's answer

Round 29 ran this exact text and read a flat null — 3 of 7 voting cells improved,
sign test p = 1.000. Its own verdict names the reason, and the reason is the
instrument rather than the text:

> **The scope was also chosen badly, and that is the round's most useful
> finding**: this round's own control gives a 298-token floor on a 1684-token
> median, a 17.7% bar, against the 17.2% harm [#150] measured — an edit that
> removed every restated word would land 8 tokens short. More reps cannot fix
> it, since the floor is a per-cell stdev rather than a standard error.

An edit that worked perfectly could not have passed that gate. The register
instrument has the opposite property: the effect it resolves is a **2x**
difference in words on a turn where nothing was requested, measured three times
in three independent batches at 1.677, 1.914 and 2.088, and pooled at 2.231
(p < 0.0001) over round 48's 120 runs. It is the most reproducible effect in the
loop. A 21-to-26-word removal on it separates at p < 0.00001; round 29's gate
needed 18% off a 1,684-token median.

Round 29's own closing line was "the next move on [#150] is a metric, not
another rule edit." Two metrics were then built and both parked — `restates` at
55.3% out-of-sample precision and deletability at 51.2%
([`deletability.md`](deletability.md)). The metric that did arrive is the
register pair, and this is the first round to point it at the text it measures.

## The registered hypothesis

> Replacing the licence's "gets full detail" with "gets the claims it needs, each
> made once" should **reduce prose words on turn 5 of `register-index`,
> `register-metric` and `register-rollback`**, laconic arm, sonnet,
> `--turn-delivery plugin`.

**Endpoint:** prose words on turn 5 by `metrics.score`, laconic arm, sonnet, 30
runs a side, two-sided permutation of the side label over per-run counts at
200,000 resamples, seed 60. Identical to rounds 47 and 48, deliberately, so the
three rounds are comparable line for line.

**Falsifier, registered in advance: `register-*` not separating from its control
at p < 0.05, or separating upward.**

**`deep-*` is the registered specificity control**, generated in the same
interleaved batch. Its turns 2 to 4 ask the same three questions without asking
for the full form, so the licence has much less to bite on there — but `deep-*`
turn 3 opens `walk me through`, which is a never-cut item, so this control is
not inert by construction and a movement on it is informative rather than
impossible.

Three readings, registered:

1. **`register-*` falls and `deep-*` does not.** The licence's wording is what
   the register is inherited through, and the cluster has its first positive
   result after six nulls.
2. **Both fall by similar proportions.** A general compression edit, not a
   licence edit. It would then have to be judged as an ordinary length edit
   against the round-wide fatal counters, and the scale-free carry-forward
   statement is untouched.
3. **Neither moves.** The seventh null, and the first one about a text that
   changes what the model sees rather than what it is told to check.

The arbiter for 1 against 2 is the difference of differences, registered **on log
words**, because the effect being removed is stated as a ratio. Both come out of
`score_persistence.py`, unchanged.

## The harm check is different from rounds 47 and 48, and the change is registered here

Rounds 47 and 48 registered *any* significant fall in `register-*` words over
turns 2 to 4 as fatal. That was right for those rounds: they added a
self-directed pre-send question, which has no business touching the turns where
the user asked for the full form, so a fall there could only be the trade [#60]
warns about.

**It is the wrong check for this round, and keeping it would reject the edit for
working.** This round edits the licence itself, and [#150]'s claim is that a
requested report carries removable redundancy — 230 words of 1,335, about 17%,
audited by hand in the report that opened the issue. The mechanism by which this
edit could move turn 5 at all runs *through* turns 2 to 4: a licensed stretch
written more tightly is a tighter register to inherit. A significance test on
those turns therefore cannot separate the intended effect from the harm.

So the fatal check becomes a bound, and it is stated before the numbers:

- **Fatal: `register-*` words over turns 2 to 4 falling below 60% of the
  control's median** — a fall of more than 40%. [#150] measured 17% removable;
  a fall past 40% is removing content the user asked for, and this round has no
  content check on those three turns fine enough to tell the two apart. The
  three prior batches put the licence's delivery at 704, 630.5 and 656 words, so
  the bound is roughly 390 words.
- **Fatal: the licence ceasing to deliver, measured scale-free** as
  `register-*` over `deep-*` on turns 2 to 4 falling below **5.0x**. Three prior
  measurements read 9.1, 8.8 and 8.2, so 5.0 is well outside anything the
  instrument has produced, and a licence that no longer separates a request for
  the full form from the plain question has been destroyed rather than tightened.
- **Fatal: any loss on the never-cut keyword** `date_trunc` on the graded turn.
  Round 47 read 39/40 and round 48 read 40/40. It covers the `index` stem only —
  the other two stems carry no `never_cut` keyword — so it speaks for a third of
  the batch and is reported as such.

The significance test rounds 47 and 48 registered is still computed and printed,
as disclosure rather than as a gate.

**What no check here can see.** Whether the words removed from turns 2 to 4 are
the restated ones is exactly the question the `restates` and deletability
detectors failed to answer at 55.3% and 51.2% precision. This round measures
that content survives at all, not that the right content went. If the primary
passes, that is what stage 2's judging is for.

## Delivery: `plugin`, and there is no choice about it

Both sides run `--turn-delivery plugin`, as in rounds 47 and 48. Under `repeat`
the whole slice is re-appended every turn, so the licence is re-asserted at full
strength on the graded turn and the register question cannot be asked at all.

## Two trees, generated simultaneously

Round 38's design, unchanged. The edit side runs from this branch and the control
side from a `master` worktree writing back into this tree, launched together, so
era and CLI release cancel between the sides instead of confounding them —
[round 37](round-37.md) measured a syntactic behaviour moving 4.7x in five days
at byte-identical rules.

```sh
git worktree add /tmp/laconic-control master
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --cases "deep-$stem,register-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 6 \
    --snapshot "evals/snapshots/loop/round-49-edit-$stem.json" &
done
for stem in index metric rollback; do
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --models sonnet --reps 10 --cases "deep-$stem,register-$stem" \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 6 \
    --snapshot "<abs>/evals/snapshots/loop/round-49-control-$stem.json") &
done
```

Six cases across two revisions, ten reps, five turns each: 120 runs and **600
calls**, the same size as rounds 47 and 48 and the pilot. The baseline arm is not
bought: the pilot measured it flat on these same six prompts (185.5 against
190.5, p = 0.9135), and it carries no rules, so this edit cannot reach it.

The shard boundary is the stem, so both families of every contrast are generated
inside one process, interleaved; the split is across contrasts, never inside one.
`--concurrency 6` is declared on all six per [#120]. Shards are merged per side
with `evals/bench/merge.py` and scored by
`python3 evals/pilot/score_persistence.py <control> <edit>`.

**The two sides are distinguishable in their own metadata**, which is what round
48 had to add a field for: here `rules_cksum` does the work it was built for,
136269960 on the control against 3990961107 on the edit. `reminder_cksum` is
`None` on both, since the reminder is untouched.

## What this round does not buy, yet

**No judging, and no round-wide arm, until the scoped target passes.** The
skill's standing order is to buy in sequence and stop at the first step that
fails, which is what saved rounds 40, 47 and 48 their 220-generation arms. If the
primary clears and the harm bounds hold, stage 2 is the round-wide laconic arm
and its judgments, and this edit touches every level's slice, so nothing ships
without them.

**Nothing is promoted.** The pair stays in `evals/pilot`, so `cases_cksum` does
not move and no fatal counter gains an unseeded cell.

**One rule-adherence note.** `register-*` and `deep-*` grade `quality`, not
adherence, so the loop's ban on optimizing against a rule-adherence case does not
apply. What the edit is scored on is words on a turn whose question is fixed and
whose fixture answer is fixed.

## Power, stated before the numbers

The pilot separated 31.0 from 52.0 at 30 runs a side at p < 0.00001, round 47
read 29.0 against 55.5, and round 48 read 28.5 against 59.5. This round is sized
identically and is powered to see that gap removed — 21 to 31 words in the other
direction. It is not powered for a 5-word shift, so a null here is a null on a
large effect. `deep-*` at 20.5 to 31.0 words across four generations is close to
the floor of what these prompts produce, so a specificity control that "does not
move" is partly a floor and is read as such.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150

<!-- RESULTS BELOW THIS LINE -->

## Result: the falsifier fired on both clauses, and the licence is not the carrier either

Sonnet, 10 reps a side, **120 runs, 0 failed**, every run five turns. Generated
2026-09-06 from `evals/pilot` at `cases_cksum` 1852778470 — the pilot's value and
rounds 47 and 48's, unchanged. The two sides are separated by `rules_cksum`,
136269960 on the control against **3990961107** on the edit, which is round 29's
value: the text really is byte-identical. `reminder_cksum` is 1027894636 on both,
since the reminder is untouched. Six shards declaring `--concurrency 6`; the
timestamps reconstruct to 3 in flight, so the declaration is conservative rather
than false.

### Primary: rejected

| family | n | control | edit | ratio | p |
|---|--:|--:|--:|--:|--:|
| **`register-*`** | 30 | **60.5** | **62.5** | **1.033** | **0.7410** |
| `deep-*` | 30 | 29.5 | 26.5 | 0.898 | 0.7893 |

**The falsifier was "not separating at p < 0.05, or separating upward", and both
clauses fired.** The registered target does not separate, and its point estimate
moves up rather than down. The interaction reads p = 0.6780 on raw words and a
ratio of ratios of 1.109 at p = 0.5203 on log words, the registered arbiter, so
**registered reading 3 obtains**: neither family moves.

The scale-free statement the edit was supposed to drive toward 1.0 goes the other
way, as in round 48:

| | `deep-*` | `register-*` | ratio |
|---|--:|--:|--:|
| control | 29.5 | 60.5 | **2.051** |
| edit | 26.5 | 62.5 | **2.358** |

Both sides separate register from deep at p < 0.00001 on 30 runs each, so the
carry-forward is intact on the edited rules.

### By stem, all six cells

| family | stem | control | edit | p |
|---|---|--:|--:|--:|
| `register` | index | 64.5 | 64.5 | 0.9759 |
| `register` | metric | 69.5 | 75.5 | 1.0000 |
| `register` | rollback | 31.0 | 36.0 | 0.2629 |
| `deep` | index | 31.5 | 31.0 | 0.7824 |
| `deep` | metric | 32.0 | 28.0 | 0.4791 |
| `deep` | rollback | 19.5 | 15.0 | 0.8408 |

No cell reaches 0.05 in either direction. Unlike round 48 there is not even a
chance cell to discount.

### The harm checks pass, and one of them is the round's real finding

| check | control | edit | bound | verdict |
|---|--:|--:|---|---|
| `register-*` words, turns 2-4 | 658.0 | 591.5 | fatal below 394.8 | **passes** at 0.899 of control |
| licence delivery, register / deep on turns 2-4 | **9.40x** | **7.58x** | fatal below 5.0x | **passes** |
| never-cut `date_trunc`, graded turn | 10/10, 10/10 | 10/10, 10/10 | fatal on any loss | **passes**, 40/40 |

The significance test rounds 47 and 48 registered as fatal, kept here as
disclosure: `register-*` turns 2-4 p = 0.8036, `deep-*` p = 0.7708.

**The licensed turns are the only place in this round where a point estimate
moves in the predicted direction.** A 10.1% fall on `register-*` turns 2 to 4 is
close to the 17% [#150] audited by hand, and the licence's delivery falls with it,
from 9.40x to 7.58x. Neither is significant and neither is claimed. What matters
is that the graded turn did not follow, and the round can say by how much it
should have.

### Why the null is exactly what the round's own data predicts

Within a single run, the length of the licensed stretch **does** predict the
graded turn. Pooling both sides, 60 `register-*` runs:

- Spearman rho over all 60 runs: **0.647**, permutation p < 0.0001. Much of that
  is the stem, which sets both levels.
- Within stem: rho 0.482 (`index`), 0.303 (`metric`), 0.419 (`rollback`) —
  positive on all three.
- Within-stem log-log elasticity: **0.44** (r = 0.380, n = 60).

So the carry-forward is real at the level of an individual run, and it is
**inelastic**. At 0.44, the 10.1% fall this edit bought on the licensed stretch
predicts **4.5% off the graded turn** — about 3 words on a 60-word median. This
round is powered for 21 to 31 words. The primary null is not evidence that
tightening the licence does nothing to the graded turn; it is evidence that this
much tightening does far less than the instrument can see.

**And that is what closes the route rather than extending it.** Running the
arithmetic the other way, at an elasticity of 0.44:

| wanted on turn 5 | licensed stretch must fall to |
|---|---|
| 60.5 to 48.3 words (the 0.60 fatal bound) | 60% — the most this round permits |
| 60.5 to 45.4 words (0.75) | 52% |
| 60.5 to 35.3 words (the pilot's `deep-*` level) | **29%** |

Removing the carry-forward by tightening the licence means cutting the licensed
stretch to under a third of its words — a 71% cut, past this round's fatal bound
and well past anything [#150] describes as redundancy. **The effect size and the
harm bound are in direct conflict, and the elasticity is the number that puts
them there.** An edit that bought the full effect would not be a licence that had
been tightened; it would be a licence that had been removed.

### The carry-forward replicates a fourth time

The control side is a fourth independent measurement of the
[register pilot](register-inheritance-136.md).

| | pilot | round 47 control | round 48 control | round 49 control |
|---|--:|--:|--:|--:|
| `deep-*` turn 5 | 31.0 | 29.0 | 28.5 | 29.5 |
| `register-*` turn 5 | 52.0 | 55.5 | 59.5 | 60.5 |
| `deep-*` turns 2-4 | 77.5 | 72.0 | 79.0 | 70.0 |
| `register-*` turns 2-4 | 704.0 | 630.5 | 656.0 | 658.0 |
| ratio | 1.677 | 1.914 | 2.088 | **2.051** |

Round 49's control does not differ from round 48's on anything: turn 5 p = 0.8982
on `register-*` and 0.8476 on `deep-*`, turns 2-4 p = 0.9491 and 0.4670. Pooling
both sides of this round, 60 runs a family, the carry-forward reads **28.0
against 61.5, a ratio of 2.196 at p < 0.00001**.

The licence delivers **9.4 times** as much across turns 2 to 4 when the full form
is asked for as when the same three questions are asked plainly, against 8.2, 8.8
and 9.1 in the three prior batches.

## Verdict: reject, and the edit is reverted in full

Per the stop-at-the-first-failing-step order, the round-wide laconic arm and its
judgments were not bought. `rules/laconic.md` and `rules/dist/*.md` return to
master, byte-identical.

## What this settles

**Seven nulls, three intervention classes.** Rounds 40 and 47 put a self-directed
pre-send question in the rules slice, round 48 put the identical sentence in the
`UserPromptSubmit` reminder, and this round edited the licence the register is
inherited through. Nothing has moved the graded turn.

**But this null is not the same kind as the six before it**, and the difference
is worth keeping. Those six were nulls about a sentence that had no measurable
effect on anything. This one is a null with a measured mechanism attached: the
edit did move the licensed stretch, in the predicted direction, by roughly the
amount [#150] describes — and the carry-forward's 0.44 elasticity means that
movement was worth about three words on the turn being graded.

**The route is closed by arithmetic rather than by a p-value.** Any licence edit
that removes the carry-forward on this instrument has to cut the licensed stretch
to under a third, which is a licence removed rather than tightened, and which
this round's own fatal bound refuses. So the remaining moves are not further
edits to that paragraph.

**What survives, measured four times.** A laconic session whose prior answers ran
long under an explicit licence answers the identical closed question with roughly
twice the words, at 1.677, 1.914, 2.088 and 2.051, and 2.196 pooled over this
round's 120 runs. It is the loop's most reproducible effect, and nothing written
into the rules, the reminder, or the licence itself has moved it.

**What this round does not say.** The elasticity is estimated from 60 runs at one
rules revision on three stems, within stem, and it is a local slope rather than a
law: it says what a 10% shift buys, not what a 70% shift would. It is reported
because the primary null is uninterpretable without it, and because it is the
first quantitative statement the cluster has about *how* the register carries
rather than *that* it does.
