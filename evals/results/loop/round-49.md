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
