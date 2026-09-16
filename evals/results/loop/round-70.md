# Round 70: the licence, moved into the check it is supposed to be bounded by

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are why this round has the scope and
the power it has. This file, the edit, the regenerated `rules/dist/*.md` and
the scorer are committed in one commit before any generation, following
[round 38](round-38.md) through [round 69](round-69.md).

`bash tools/candidate-due.sh` exits 1: [round 69](round-69.md) was the one
measuring round the cap allows, so this round carries a candidate. Round 69's
own closing instruction is where it is pointed — *"round 70 should not aim a
rule edit at this ... round 70's candidate belongs on a different `rules`
issue."* This is that issue.

## The edit

`rules/laconic.md`, the opening checks and the length-scaling paragraph. The
licence sentence **moves** out of the paragraph and into check 2:

```diff
-2. What is the smallest set of claims that fully answers this?
+2. What is the smallest set of claims that fully answers this? A report,
+   walkthrough, comparison or explanation the user asked for needs more of
+   them, and none of them twice.
 3. Is anything here something the user did not ask for?

 **Length scales to the request, at every level.** A yes/no question gets a word
-or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets full detail. Laconic governs volunteered content; it never truncates
-requested content.
+or a line. Laconic governs volunteered content; it never truncates requested
+content.
```

`rules_cksum` on the `full` slice goes **594915793 to 3641437234**. The edit
sits above every level marker, so it reaches `lite`, `full` and `ultra`
alike, which is where the sentence it moves already sat.

**This is one edit, and it is a relocation rather than a rewording.** That
distinction is the whole reason to run it, and this cluster's own instrument
lessons are what draw it:

> 1. **Bounding a licence in prose has failed four times** — rounds 07, 08, 09
>    and 29. **Relocating one worked, once, in round 10.**

and the loop skill states the same thing as a rule:

> **Where a rule lives outranks what it says about where it lives.** When a new
> licence bleeds into content it should not reach, move it rather than write
> its limits into it. ... Round 10 moved the same licence into `level: full`,
> **wrote no precedence sentence at all**, and the cell returned to 2 while the
> token effect grew.

So this edit writes no precedence sentence. It does not say that check 2
outranks the licence, or that the checks run inside requested content — both of
which have been tried, in rounds 29 and 49, in those words. It puts the licence
**inside** check 2, where it inherits the check's limits without being told
them, and leaves nothing standing alone after the checks for a reader to take
as an exemption from them.

## Why this round exists

[#150] reports the paragraph read as a length exemption rather than a scope
allowance:

> "Gets full detail" plus "never truncates requested content" is readable as:
> once the user asks for a report, the two checks at lines 9-10 no longer bind.
> That is how I read it.

The report is a field one and it carries its own audit: a requested document of
1,335 prose words, of which **230 words — 17.2% — restate claims the document
had already made**. An aside making the same point as a table further down the
page; a sentence that follows trivially from the table above it; a chart note
re-explaining labels already printed on the chart.

**The issue has been scored twice and neither round scored it on that.**

| round | text | endpoint | why it could not settle the issue |
|---|---|---|---|
| [29](round-29.md) | the licence edit | `output_tokens`, 8 cells | the scoped floor is **17.7%** against a 17.2% harm: an edit removing every restated word lands 8 tokens short, and reps cannot shrink a per-cell standard deviation |
| [49](round-49.md) | the same text, byte-identical | `register-*` turn 5 prose words | it measured the *carry-forward*, whose 0.44 elasticity made the 10.1% the edit bought upstream worth about **three words** on the turn being graded |

Round 49's own reading is the opening this round takes:

> **The licensed turns are the only place in this round where a point estimate
> moves in the predicted direction.** A 10.1% fall on `register-*` turns 2 to 4
> is close to the 17% [#150] audited by hand, and the licence's delivery falls
> with it, from 9.40x to 7.58x. Neither is significant and neither is claimed.
> What matters is that the graded turn did not follow.

The graded turn was round 49's target and the licensed stretch was its harm
bound. This round swaps them: **the licensed stretch is the target**, because
it is the only place in this repository where `rules/laconic.md` licenses
length explicitly and where the harm [#150] describes can therefore occur.

## The instrument is rounds 47 to 49's, unchanged

`evals/pilot/register-{index,metric,rollback}` and its `deep-*` twin. Turns 2
to 4 of the `register-*` family ask `deep-*`'s three questions verbatim with an
explicit request for the full form appended — *a complete checklist, every
check written out in full, not a summary*; *the whole argument, step by step,
in full*; *the full assessment as a table — every failure mode, its mitigation,
and what you would monitor*. `deep-*` asks the same three questions plainly.

`cases_cksum` over the six cases computes **1852778470**, which is the value
rounds 47, 48 and 49 each recorded. The instrument has not moved, so this
round's control is directly comparable to three stored ones, and those three
agree with each other on every quantity.

**Nothing joins `evals/cases/`**, so no fatal counter gains an unseeded cell and
`cases_cksum` does not move for any future round.

## Registered endpoints

**Target: prose words summed over turns 2 to 4 of `register-*`, laconic arm,
sonnet. Registered direction: down.** Scored by
`evals/pilot/score_claims.py`, committed with this file.

**The statistic is stem-stratified, and that is what makes the round
affordable.** The three stems sit at 879.5, 689.0 and 324.5 median words on
round 49's control (computed 2026-09-16 from `round-49-control.json`, n = 10
per stem), so pooling them puts most of the variance into which stem a draw
came from. The registered statistic is the **mean over stems of the shift in
that stem's median log words**, with the side label permuted inside each stem,
50,000 resamples, two-sided, seed 70. Exponentiating it gives the factor the
edit multiplied a typical response by, with each stem weighted equally rather
than by its own level.

That is [round 42](round-42.md)'s mixture lesson applied inside this family,
and round 69 measured what ignoring it costs: an unstratified permutation on an
instrument whose groups sit far apart builds a null **1.9x wider than the
sampling distribution of the statistic it tests**. Here, at the same 30 runs a
side, the pooled test carries **0.24** power against [#150]'s harm size where
the stratified one carries **0.90**.

### Bound 1, fatal: fixture-token coverage over turns 2 to 4 must not fall

**Fewer words is bought trivially by saying less, and that failure would score
as a triumph.** So the target does not stand alone. Coverage counts how many of
the fixture's own tokens the licensed stretch names — a pass condition that is
a token present in the response, which is `evals/CRITERIA.md`'s admission rule
for never-cut keywords applied to the whole fixture rather than to one keyword.

**The token list is mechanical, not hand-picked.** It is every number, clock
time and backticked identifier in the fixture, minus anything the prompt
already contains, minus single-character matches; matching consumes the longest
token first, so `41.2` inside `41,199,388` is not credited twice. A hand-picked
list is a list picked after reading responses. This one is a function of the
fixture, and `cases_cksum` covers the fixture, so it cannot drift from the
round that registered it. `python3 evals/pilot/score_claims.py --tokens` prints
it; it is 37 tokens on `index`, 24 on `metric` and 30 on `rollback`.

Same statistic as the target, **one-sided down**. Computed on round 49's
control, the coverage medians are 13.5 of 37, 13.0 of 24 and 20.5 of 30.

**What makes this bound sensitive rather than decorative** is the `deep-*`
family beside it. Computed 2026-09-16 from `register-136.json`, laconic arm,
median tokens covered over turns 2 to 4:

| stem | of | `deep-*` | `register-*` |
|---|--:|--:|--:|
| `index` | 37 | 3.0 | 15.0 |
| `metric` | 24 | 6.5 | 14.0 |
| `rollback` | 30 | 3.5 | 22.5 |

Asked the same three questions without the full-form request, the laconic arm
names a fifth to a half of what it names when the full form is asked for. So
the measure separates a delivered report from an undelivered one by a factor of
two to five, and a fall of that kind cannot hide inside it.

### Bound 2, fatal: the licence still fires

Round 49's bound, carried forward verbatim. Median `register-*` words over
turns 2 to 4 divided by median `deep-*` words over the same turns must stay at
or above **5.0**. Round 49's control reads 12.93, 6.02 and 6.76 by stem. A
licence that stops discriminating between an explicit request for the full form
and the plain question has been removed rather than relocated, whatever the
coverage count says.

### Bound 3, fatal: the never-cut keyword survives

`date_trunc` on the graded turn of the `index` stem, the pair's one `never_cut`
keyword. Any loss rejects. It covers a third of the batch, and this round says
so rather than implying otherwise, as round 49 did.

## The registered decision rule, written before any generation

1. **The target falls at p < 0.05 and all three bounds hold.** The relocation
   removes words from a requested report without removing claims from it, which
   is [#150]'s harm and the first thing in this cluster's history to reject an
   edit's alternative reading rather than the edit. **Accept**, subject to
   step 8's replication and step 9's holdout, and the round proceeds to the
   round-wide fatal counters before anything ships.
2. **The target falls and a bound fails.** **Reject**, and the round reports
   which cheap win was taken. This is the outcome the bounds exist to name, and
   a fall bought by dropping the fixture's own facts is worse than a null.
3. **The target is null.** **Reject**, edit reverted in full. Relocation joins
   rewording as an intervention class that does not move this quantity, and the
   round reports the interval on the ratio so the next reader knows what it
   bounds rather than what it excludes. Taken with rounds 29 and 49, that would
   be three intervention classes on one paragraph, and the honest conclusion is
   that [#150] needs the judged redundancy verdict [#155] specifies rather than
   another edit to the paragraph.
4. **The target rises.** **Reject.** The relocation made the licence read as a
   larger licence, which is a real and publishable failure of the move-it-don't-
   bound-it rule at the one place that rule has previously won.

**Nothing is judged unless branch 1 fires**, per the standing order to stop at
the first step that fails and round 68's discipline: a quality verdict bought
against a null primary answers no question the round asked.

## Power, stated before the numbers

Computed 2026-09-16 by resampling `round-49-control.json`'s 30 stored
`register-*` laconic runs at master rules, per stem, 200 trials of the
registered permutation, alpha 0.05:

| true ratio | n = 10/stem | n = 15/stem | **n = 20/stem** | n = 30/stem |
|---|--:|--:|--:|--:|
| 1.00 | 0.04 | 0.05 | **0.05** | 0.06 |
| 0.90 | 0.47 | 0.53 | **0.77** | 0.81 |
| 0.85 | 0.79 | 0.91 | **0.98** | 0.99 |
| 0.83 | 0.90 | 0.97 | **0.98** | 1.00 |
| 0.80 | 0.97 | 0.99 | **0.99** | 1.00 |

0.83 is [#150]'s audited harm — 17.2% of the words restating claims already
made. **20 reps per stem per side carries 0.98 there and 0.77 at 0.90**, which
is the size round 49's edit actually delivered on this quantity (0.919 when its
two committed snapshots are re-scored by this round's scorer, p = 0.3055). So
the round is powered both for the harm as reported and for the movement the
only comparable edit produced.

The same figures under the **pooled** permutation round 49 used, over 30 runs a
side: 0.24 at a 0.83 ratio, 0.21 at 0.85 and 0.35 at 0.80. The stratification
buys more than doubling the round would.

## The command

Four shards, two per side, split by rep offset rather than by case so every
shard covers every cell:

```sh
# edit side, from this branch
for off in 0 10; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --rep-offset $off --cases 'register-*,deep-*' --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 4 \
    --snapshot "evals/snapshots/loop/round-70-edit-$off.json" &
done
# control side, from a worktree at master, writing back here
git worktree add /tmp/laconic-r70-control master
for off in 0 10; do
  (cd /tmp/laconic-r70-control && python3 evals/bench/run.py --arms laconic \
    --models sonnet --reps 10 --rep-offset $off --cases 'register-*,deep-*' \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 4 \
    --snapshot "$REPO/evals/snapshots/loop/round-70-control-$off.json") &
done
```

Six cases, one arm, one model, 20 reps a side: **240 runs and 1,200 CLI calls**,
because every case here is five turns. Four shards is the ceiling `run.py`
enforces and this round sits on it; `--concurrency 4` is declared on all four
per [#120], and each shard interleaves both families and all three stems, so
the simultaneity [round 38](round-38.md) requires holds inside each shard
rather than only in aggregate.

`--turn-delivery plugin` because every claim here is about the product, and
because `repeat` re-asserts the whole slice every turn and would make an edit to
the checks a different treatment on every turn of the run.

Sonnet only: rounds 47, 48 and 49 and the register pilot are all sonnet, and a
haiku arm would be a second contrast with no stored comparison to register
against.

Scored by:

```sh
python3 evals/pilot/score_claims.py \
  evals/snapshots/loop/round-70-control.json \
  evals/snapshots/loop/round-70-edit.json
```

after `evals/bench/merge.py` unions each side's two shards.

## What this round cannot establish

- **It does not measure restatement.** The target is prose words and the bound
  is fixture-token coverage; neither reads whether a sentence repeats one
  above it. What the pair can say is that a report got *shorter* without
  getting *thinner*, which is [#150]'s harm removed if restatement is what the
  words were, and is a compression win with no measured cost if it is not.
  [#155]'s detector is parked at 55.3% precision and may not be promoted inside
  a round. A judged redundancy verdict remains the thing that would close this,
  and it is a separate unit.
- **The benchmark's restatement population may not be [#150]'s.**
  Hand-labelling under [#155] put restatement at 62.5% on haiku against 25.0%
  on sonnet, and the field report is a large model writing a document. This
  round is sonnet, in chat, on a five-turn synthetic fixture. `kimi` raised
  exactly this through `tools/consult.sh` and it is recorded here rather than
  discovered afterwards: a fall here is a fall on this instrument, and the
  claim it licenses is about a requested report in a session, not about a
  1,335-word document.
- **Three stems cannot reach alpha on a sign test** — the minimum two-sided p
  over three cells is 0.25 — so the per-stem table is a consistency reading and
  carries no verdict, as in rounds 67, 68 and 69. The verdict is the stratified
  statistic's.
- **The round-wide fatal counters are not bought unless branch 1 fires.** An
  accept here is an accept on the scoped target only, and the standing order
  sends it to the round-wide laconic arm next.
- **A null bounds the effect rather than excluding one.** At 20 reps per stem
  the round is underpowered below about a 0.90 ratio, and the interval on the
  ratio is reported with the result.

## What was consulted

`bash tools/consult.sh` was run on the design before anything was committed.
`codex` and `deepseek` were both unavailable — codex timed out and deepseek's
model id is not in this CLI's catalogue — and `kimi` answered.

Two things it said are adopted. The first is the construct-validity caution
above, stated as a limit rather than argued away. The second killed a different
design outright: this round nearly registered the **opposite** failure of the
same paragraph — the laconic arm delivering 0.084 of the unruled arm's words on
a turn that begins *"walk me through"* — and `kimi`'s objection was that a ratio
against a verbose control is not evidence of truncation without a completeness
measure, so a null could hide in what a walkthrough "needed".

**That objection was then tested rather than accepted, at no generation cost,
and it decided the question.** The turn it is cleanest on is `register-rollback`
turn 2, which asks for *"the complete assessment, every phase of the window
written out in full, not a summary"* about an incident whose fixture states the
window as nine timestamped rows and three error rates. Scoring those twelve
facts over `register-136.json`'s committed runs, laconic arm against baseline
arm, ten runs each:

| arm | timeline facts named, of 12 | median prose words |
|---|---|--:|
| laconic | 10, 10, 10, 11, 11, 11, 11, 12, 12, 12 | 142.0 |
| baseline | 12 in all ten runs | 631.0 |

The fact laconic drops is `13:58` in seven runs of ten — the release rollout
starting, four minutes before the window the question asks about. **The terse
arm delivers a median 11 of the 12 facts in 22% of the words**, so the 0.084
ratio is the unruled arm padding rather than the ruled arm truncating, and the
under-delivery design is refuted before it was registered.

That twelve-fact list was written by hand for this check and is not the token
list the bound above uses; it is quoted here as the premise check it was, and
the mechanical measure reads the same direction less sharply, at 22.5 of 30
against 26.5.

[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155

## Results

<!-- Nothing above this line has been computed. -->
