# Does a licensed-long stretch carry forward? The register pilot for #136

**Registration. Nothing below the results line has been computed.** This file
and the case pair it describes are committed in the same commit, before any
generation, following [round 38](round-38.md) and [rounds 44 to 46](round-46.md).

## The gap this is for

Four issues in the over-length cluster are stuck on one sentence, and three of
them say it in nearly the same words. [#136]'s last comment:

> The open part is no longer the diagnosis. It is the gap between your session
> and the instrument, and the two candidates for it are both case-authoring
> problems rather than rule problems:
>
> - **The harness's earlier turns are not yours.** You describe the turn before
>   the failure as "a real explanation with a table", which was the correct
>   response. The `deep-*` turns are short analysis answers about a one-page
>   fixture. A register can only be inherited from a register that was set.
> - **A real session interleaves work with questions.**

[#113] and [#60] name the same two. [`over-length-cluster.md`](over-length-cluster.md)
holds them. Nothing has tested either.

This is the first candidate. It is the cheaper of the two and it does not touch
`CRITERIA.md`'s `Don't edit anything.` clause, which the second one has to
remove and which [#116]'s line is separately entangled with — that cell's edit
rate is [not stable across dates](conditional-homology-116.md).

**Why the first candidate is worth a batch.** [#60] describes the mechanism
exactly, and it is a mechanism about `rules/laconic.md`'s own text rather than
about the model:

> Earlier turns in the same session had legitimately long outputs: an
> explicitly requested review report, and a walkthrough of several decisions
> the user asked to go through one at a time. **Both were correct at that
> length** — requested content is never truncated, and that rule worked. But
> nothing resets the calibration afterward.

The ruleset says so in as many words: *"Length scales to the request, at every
level … A report, walkthrough, comparison, or explanation the user asked for
gets full detail."* So the reported failure is the rule licensing length on one
turn and the licence not expiring on the next. `deep-*` cannot produce it,
because nothing in `deep-*` asks for a licensed-long deliverable. Its turns 2
to 4 are short analysis questions; one of the three begins `walk me through`,
which is the closest the scored suite comes.

## The instrument: one clause of difference

`evals/pilot/register-{index,metric,rollback}` is `evals/cases/deep-*` with

- **turn 1 byte-identical**,
- **turn 5 byte-identical**, and the same `trap`, `never_cut` and `grading`,
- **the same fixture**, by symlink rather than by copy,
- **turns 2 to 4 asking deep's three questions verbatim**, each with an added
  clause requesting the full form.

`deep-rollback` turn 2 against `register-rollback` turn 2, in full:

    how bad was the customer impact here? Don't edit anything.

    how bad was the customer impact here? Give me the complete assessment,
    every phase of the window written out in full, not a summary. Don't edit
    anything.

That is the whole manipulation. Subject matter, fixture, turn count, turn order
and the graded question are all held; the only thing that varies is the register
the model's own four prior answers were written in. `tests/test_evals_layout.sh`
holds the pair to that contract, so a later edit to one side fails the suite
rather than silently turning this into a comparison of two different questions.

The `deep-*` cases are symlinked into `evals/pilot` because `run.py` takes one
`--cases-dir` and the two families have to be generated in one interleaved pass
— [round 37](round-37.md) measured a syntactic behaviour moving 4.7x in five
days at byte-identical rules, so a sequential window is the exposure to avoid.
A symlink cannot drift from the case the scored suite ships.

Nothing joins `evals/cases/`, so `cases_cksum` does not move for any future
round and no fatal counter gains an unseeded cell.

## Hypothesis, registered

> A laconic session whose four prior answers were written at a length the rules
> licensed answers the identical closed question with **more words** than one
> whose prior answers were short.

Endpoint: prose words on turn 5 by `metrics.score`, laconic arm, sonnet,
`register-*` against `deep-*`, 30 runs a side, two-sided permutation of the
family label over per-run counts at 200,000 resamples, seed 136.

**Falsifier, registered in advance: `register-*` not separating from `deep-*` on
the laconic arm at p < 0.05, or separating downward.** Either says the first
candidate is not the gap, and the cluster's remaining candidate is the second
one.

**The baseline arm is the control, and it is what makes the result readable.**
`register-*` is a new case, so a turn-5 rise on the laconic arm alone has two
readings: the register carrying forward, or the new case simply drawing longer
answers from anybody. Round 42's lesson exactly. Registered reading: the effect
is credited to the rules only if the laconic rise exceeds the baseline rise,
tested as the difference of differences by permuting the arm label inside each
family.

Three readings are possible and all three are informative:

1. **Laconic rises and baseline does not.** The licence does not expire, the
   cluster has its instrument, and [#60]'s persistence clause becomes testable
   for the first time.
2. **Both arms rise by similar proportions.** The case is longer for everyone
   and this measures the case, not the rules. The pair does not promote.
3. **Flat and flat.** The first candidate is answered negatively and
   [#136]'s remaining gap is the second one — a session that interleaves work
   with questions — which is a more expensive instrument and now the only one
   left.

**Registered manipulation check, and it is dual-purpose.** Words summed over
turns 2 to 4 must be higher on `register-*` than on `deep-*` on the laconic arm.
If they are not, the manipulation did not land and nothing downstream is
interpretable — **and it is itself a finding**, because the ruleset promises
those three turns full detail. Laconic under-delivering on an explicitly
requested report is the never-cut failure `rules/laconic.md` says it will not
commit.

**Registered harm check, free:** `date_trunc` on the `index` stem, which is the
one `never_cut` keyword in the pair. The other two stems carry none, so the
check covers a third of the batch and is stated as such rather than implied.

## What this round does not buy

**No judging.** [Round 43](round-43.md) graded `deep-*` at 120 of 120 across
both arms at every depth, a ceiling at which per [#94] a fall registers and a
rise cannot. The primary question here is length, and a quality verdict on the
register family is the follow-up an effect would earn, not a prerequisite for
seeing one.

**No rule edit is proposed from this**, whichever way it comes out. This is an
instrument, and [#60]'s persistence clause stays untested until there is a case
that can score it.

## The command

Three shards, one per stem, launched together and declaring each other:

```sh
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 10 \
    --cases "deep-$stem,register-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 3 \
    --snapshot "evals/snapshots/loop/register-136-$stem.json" &
done
python3 evals/bench/merge.py evals/snapshots/loop/register-136-*.json \
  --out evals/snapshots/loop/register-136.json
```

Six cases, two arms, ten reps: 120 runs and **600 calls**, because every case
here is five turns. The shard boundary is the stem, so both families and both
arms of every contrast are generated inside one process, interleaved — the
split is across contrasts, never inside one. `--concurrency 3` is declared on
all three per [#120]. `--turn-delivery plugin` because this is a claim about the
product and the cluster's whole multi-turn instrument reverses under `repeat`
— see [`turn-delivery.md`](turn-delivery.md).

Scored by `python3 evals/pilot/score_register.py`.

## Power, stated before the numbers

Round 42 separated the arms on these same `deep-*` cells at 30 runs a side with
a paired median gap of 181 words, and its per-cell medians were 210.5 against
30.5. This pilot is sized the same way and is powered for an effect of that
order: a laconic turn-5 median moving from about 30 words to about 60 is
comfortably inside what 30 a side resolves on a permutation over per-run counts.
It is **not** powered for a 5-word shift, and a null here is a null on a large
effect rather than on any effect. Round 46's lesson applies in the other
direction from where it was learned: size against what the control actually
reads, and this control has been read three times.

<!-- RESULTS BELOW THIS LINE -->

## Result: the falsifier did not fire, and the registered arbiter is unusable

Sonnet, 10 reps a side, **120 runs, 0 failed**, every run five turns. Generated
2026-09-05 from `evals/pilot` at `rules_cksum` 136269960, `cases_cksum`
1852778470, `--turn-delivery plugin`, three shards declaring `--concurrency 3`
and reconstructing to three in flight.

### The manipulation landed, and it is a finding in its own right

Prose words summed over turns 2 to 4, per run:

| arm | `deep-*` | `register-*` | p |
|---|--:|--:|--:|
| baseline | 924.5 | 2446.0 | < 0.00001 |
| laconic | **77.5** | **704.0** | < 0.00001 |

**Laconic honours the length licence, and it is the sharpest measurement of that
anywhere in the archive.** Asked for the full form it writes **9.1 times** as
much as when asked the same three questions plainly. Whatever else the ruleset
does, "Length scales to the request" is not decorative.

Two things about that row are worth having on the record, neither registered:

- **On `deep-*` laconic spends 77.5 words across all three middle turns**, one
  of which begins `walk me through`, against baseline's 924.5 — a ratio of
  0.084. That is the scored suite's own multi-turn family, and a walkthrough
  answered in about 26 words is close to the [#46] failure mode inverted.
- **Even when the request is explicit, laconic delivers 0.29 of baseline.**
  704 words against 2446, on prompts asking in as many words for a complete
  assessment, the whole argument step by step, and a table with the evidence
  for each row.

### Primary: prose words on the graded turn

| arm | n | `deep-*` | `register-*` | ratio | p |
|---|--:|--:|--:|--:|--:|
| baseline | 30 | 185.5 | 190.5 | 1.027 | 0.9135 |
| **laconic** | 30 | **31.0** | **52.0** | **1.677** | **< 0.00001** |

Means move the same way and no further: laconic 30.5 to 50.6, baseline 195.2 to
**193.9**, which is a fall.

**The falsifier did not fire.** It was "not separating at p < 0.05, or
separating upward", and the laconic arm separates upward at p < 0.00001.

**Every stem agrees, and the control's stems agree in the other direction:**

| stem | laconic | p | baseline | p |
|---|--:|--:|--:|--:|
| `index` | 31.0 to **59.0** | 0.0001 | 176.5 to 180.5 | 0.9588 |
| `metric` | 44.0 to **57.0** | < 0.00001 | 234.0 to 234.0 | 0.4067 |
| `rollback` | 20.0 to **28.5** | 0.0002 | 176.0 to **150.0** | 0.0830 |

Three of three on the treatment arm, each significant on its own. Zero of three
on the control, and the one that moves most moves **down**.

### The registered interaction test failed, and the reason is my own design error

The registration made the arm contrast the arbiter: *"the effect is credited to
the rules only if the laconic rise exceeds the baseline rise, tested as the
difference of differences by permuting the arm label inside each family."*

    interaction on absolute words, as registered:  p = 0.4899

**It does not clear, and it is not evidence against the result — it is a broken
test, and round 42 already wrote down why.** Its instrument note:

> Permuting arm labels within a cell builds each group as a 50/50 mixture of
> two well-separated modes, and a median lands in whichever mode draws more
> than half the values, so the statistic has enormous variance. Reducing to the
> within-cell difference first removes the mixture. **A median under a
> permutation that creates bimodality is broken rather than conservative.**

That is this exact defect. Shuffling the arm label mixes a group whose mean is
195 with one whose mean is 30, so the null distribution of the difference of
differences is dominated by which arm happens to draw the long answers, and a
20-word effect on the short arm cannot be seen through it. Round 42 removed the
mixture by reducing to a within-cell difference first; here the two families are
different cases, so there is no run-level pairing to reduce to.

**Unregistered and post-hoc**, the same permutation on log words — where the
statistic is a ratio of ratios and the arms are on comparable scales — reads a
ratio of ratios of **1.782 at p = 0.0844**. Closer, still not clearing, and it
is post-hoc, so it is reported and not leaned on. `score_register.py` prints it
beside the registered one, so both are reproducible from the snapshot rather
than recomputed by hand.

**What rules out the "it is just a longer case" reading is the control's own
null, not the interaction.** Registered reading 2 was "both arms rise by similar
proportions". The baseline arm does not rise at all: p = 0.9135 pooled, a mean
that falls, zero of three stems rising and one falling at p = 0.083 — on the
same six prompts, in the same interleaved batch, at ten times the answer length
where a rise would be easiest to see. Reading 1 obtains.

**Recording the error as an error.** The registration should have specified the
interaction on the log scale, or specified no interaction at all and rested on
the two within-arm tests. Round 42 had already published the lesson and this
registration reproduced the mistake anyway. The primary endpoint, its falsifier
and the control were all registered correctly and all three are unambiguous, so
nothing about the finding turns on the broken arbiter — but a registration is
worth nothing if its failures are quietly reread, so the failed test stays in
the table above.

### The scale-free statement of the finding

| | `deep-*` | `register-*` |
|---|--:|--:|
| laconic median / baseline median, turn 5 | **0.167** | **0.273** |

**After four answers written at a length the rules licensed, the rule binds
about 1.6 times less hard on the turn that follows** — on a question that is
byte-identical, in a session of identical depth, against a fixture that has not
changed.

### Harm check: passes

`date_trunc` present on the graded turn, `index` stem, the pair's one
`never_cut` keyword: **10/10 in all four groups.** The other two stems carry no
keyword, so the check covers a third of the batch, as the registration said.

## What this establishes, and what it does not

**[#136]'s mechanism reproduces on the instrument for the first time.** The
cluster has spent five rounds on this family and every one of them measured
depth. This measures what [#60] actually described — the licence not expiring —
and it is the first thing in the archive that makes laconic go **up**.

**[#60]'s persistence clause is now testable.** Its proposal B was parked in
2026-08-08 with "no view yet … it is hard to instrument: the benchmark runs one
prompt per session, so nothing in it can exhibit the multi-turn drift you
describe." That is no longer true. A clause telling the model that a turn where
length was correct does not license the next one has a cell to move: laconic on
`register-*` turn 5, with `deep-*` as the case control and the baseline arm as
the era control.

**The magnitude gap is not closed and is the honest limit.** [#136] reports
about 400 words; this reads 52. The mechanism reproduces at roughly an eighth of
the reported size, so it is a mechanism finding and not a reproduction of the
report. The cluster's second candidate — a session that interleaves work with
questions — is untouched and remains the candidate for the rest.

**Nothing was judged.** Whether the extra 21 words carry anything is unmeasured
here. [Round 43](round-43.md) graded `deep-*` at 120 of 120 across both arms, so
the follow-up an effect earns is a judged batch on `register-*`; a rise from a
ceiling that high is what [#94] says a cell like this can show.

**One batch, one date, three stems, ten reps.** The within-arm contrasts are
generated in one interleaved pass so era cancels between them, which is what
[round 37](round-37.md) requires; nothing here replicates across days.

**No rule edit is proposed, as registered.** The pair stays in `evals/pilot`.
Promoting it to `evals/cases/` would move `cases_cksum` for every future round
and needs a seeded baseline, and the case for doing that is a rule edit that
wants to be scored on it — which is [#60]'s next unit, not this one.


[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136
