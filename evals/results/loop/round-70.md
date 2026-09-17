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

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#259]: https://github.com/JordanMPDS/laconic/issues/259

## Results

<!-- Nothing above this line has been computed. -->

**240 runs, 120 a side, 20 per stem per side, zero failed.** Generated
2026-09-16 in four shards split by rep offset, two per side, the edit side from
this branch and the control side from a `master` worktree, running
simultaneously. `rules_cksum` 594915793 against 3641437234 as registered,
`cases_cksum` 1852778470 on both sides, `turn_delivery` `plugin` on both.

`python3 evals/bench/release.py` reads **both arms entirely on CLI 2.1.272** —
no release boundary inside the round at all, which is rarer than the audit
usually finds and means the instrument is literally one version rather than a
balanced mixture. `python3 evals/bench/concurrency.py` reads each side declaring
4 and reconstructing to 2 in flight, so the declaration is conservative.

### The target falls: 0.903, p = 0.0247

Prose words summed over turns 2 to 4 of `register-*`, laconic arm, sonnet.
Stem-stratified mean of the shift in each stem's median log words, side label
permuted inside each stem, 50,000 resamples, two-sided, seed 70 — the
statistic registered above, run by the scorer committed with this file.

| stem | n/side | control | edit | ratio |
|---|--:|--:|--:|--:|
| `index` | 20 | 1598.5 | 1380.0 | 0.863 |
| `metric` | 20 | 1097.5 | 978.5 | 0.892 |
| `rollback` | 20 | 589.5 | 564.0 | 0.957 |
| **stratified** | | | | **0.903**, p = **0.0247** |

The 95% bootstrap interval on the ratio is **[0.837, 0.990]**, 20,000 resamples
within stem. All three stems move down, which the round registered as a
consistency reading carrying no verdict of its own — three cells cannot reach
alpha on a sign test.

**The effect is the size the only comparable edit produced, not the size the
issue audited.** [#150] audits 17.2% of the words as restatement, a 0.83 ratio;
round 49's edit delivered 0.919 on this quantity. This round reads 0.903, and
its interval excludes 1.00 while containing 0.919 and excluding 0.83. The round
was powered 0.98 at 0.83 and 0.77 at 0.90, so landing at 0.90 with p = 0.0247
is the round detecting the smaller of the two sizes it was built for.

### Bound 1, fixture-token coverage: holds

| stem | of | control | edit | ratio |
|---|--:|--:|--:|--:|
| `index` | 37 | 18.0 | 17.0 | 0.944 |
| `metric` | 24 | 15.0 | **15.5** | 1.033 |
| `rollback` | 30 | 25.0 | 24.0 | 0.960 |
| **stratified, one-sided down** | | | | **0.978**, p = **0.2512** |

The shift is **-0.50 tokens**, 95% bootstrap interval **[-1.50, +0.33]**. The
bound asked that coverage not fall and it did not fall at significance.

**What that bound does and does not exclude.** Its interval admits a loss of up
to one and a half of the fixture's own tokens out of a median 18 to 25, so it
rules out the cheap win — a fall of the two-to-five-fold kind the `deep-*`
family shows is what an undelivered report looks like here — and does not rule
out a small real thinning. The registered comparison is the one that makes it
readable: asked the same three questions without the full-form request, the
laconic arm names 3.0, 6.5 and 3.5 tokens against 15.0, 14.0 and 22.5. The edit
stays in the delivered range on every stem.

### Bound 2, the licence still fires: holds, and moved toward its floor

Median `register-*` words over turns 2 to 4 divided by median `deep-*` words
over the same turns.

| | `index` | `metric` | `rollback` | pooled |
|---|--:|--:|--:|--:|
| control | 6.73 | 6.31 | 6.34 | 6.34 |
| edit | 5.51 | 5.25 | 6.10 | **5.51** |
| floor | 5.0 | 5.0 | 5.0 | 5.0 |

Every stem clears the floor and the pooled figure clears it by 0.51.

**This is the round's least comfortable number and it is reported as such.**
The fall is arithmetic rather than independent: `register-*` fell 0.903 while
the `deep-*` control family did not move, so the ratio had to fall by about the
same factor, and 6.34 x 0.868 is 5.50 against the 5.51 measured. The bound
holds as registered, and the honest reading is that a second edit of this size
on this paragraph would put it through the floor. A future round proposing one
has to re-register the floor rather than inherit it.

### Bound 3, the never-cut keyword: holds

`date_trunc` on the graded turn of the `index` stem: **20/20 on both sides of
both families**, 80 of 80 responses. No loss.

### Disclosure: the unlicensed family did not move

`deep-*` asks the same three questions plainly, carries no full-form request,
and is therefore the place where this edit should do nothing.

| stem | control | edit |
|---|--:|--:|
| `index` | 237.5 | 250.5 |
| `metric` | 174.0 | 186.5 |
| `rollback` | 93.0 | 92.5 |
| **stratified** | | **1.040**, p = 0.4448 |

The point estimate is slightly up, the interval is **[0.923, 1.139]**, and the
test does not separate it from 1.00. So the compression the target measured is
specific to the turns that asked for the full form, which is what a relocation
into check 2 predicts and what a general shortening would not.

### The registered decision rule selects branch 1

The target fell at p < 0.05 and all three bounds held. That is **accept on the
scoped target**, and by the rule as written the edit now goes to the round-wide
fatal counters, then step 8's replication, then step 9's holdout, before
anything ships.

**Relocation has now separated where rewording did not, twice.** Rounds 07, 08,
09 and 29 bounded a licence in prose and failed; round 10 moved one and won;
this round moves one and wins. That is the move-it-do-not-bound-it rule's
second and third data points on the same side, and its first on this paragraph.

---

## What the accept buys next, registered before any of it is generated

The standing buy order is the scoped target, then the round-wide counters, then
the replication, stopping at the first failure; step 9's holdout follows an edit
that has passed all three. This section is written now, with the scoped result
above already computed and none of what follows generated.

**Bar A, fatal: the round-wide counters.** `report.py` over all dev-set cases
and both models, 5 reps a side, **both sides generated in one interleaved
batch** rather than carried, scored under the [#259] gate. That is
`never_cut_failures`, `quality_fails`, `safety_fails` and `violations_total`,
plus the [#49] turn gate. Judged at `--judge-all`, because both sides of this
comparison have to carry the same coverage and because the later reader of
either snapshot needs the adherence verdicts.

At five reps a side no cell is condemnable, so this bar is the round-wide count
alone and [round 54](round-54.md) measured its detection curve: about **+23**
round-wide before it fires four times in five. This round says so rather than
implying the bar is sharper than it is. What buys the sharpness back is reps,
and reps are not bought unless a counter rises.

**Bar B, fatal: the replication.** One further independent generation of the
scoped design — the same six cases, sonnet, 20 reps per stem per side, both
sides simultaneous from the two trees — scored by the same
`evals/pilot/score_claims.py` at the same seed. The registered bar is the
**target falling at p < 0.05 in the replication too**, with all three bounds
holding again. A ratio that lands between 0.90 and 1.00 without reaching alpha
is a failure of this bar, not a partial success: round 70's whole claim is that
this quantity moves, and a sample is not a measurement.

**Bar C, fatal: the holdout does not regress.** All six reserved cases, both
models, n = 10, both arms interleaved. No reserved case worse at p < 0.05 and
the round-wide direction not worse at significance. Directions and significance
only, never a number, per the loop's standing rule.


---

## Bar A: the round-wide counters hold

**740 runs, 370 a side, 5 reps a side over all 37 dev-set cases and both
models, zero failed.** Generated 2026-09-16 in four shards, two per side split
by model, the edit side from this branch and the control side from a `master`
worktree, running simultaneously. `rules_cksum` 594915793 against 3641437234 as
registered, `cases_cksum` 90696499 on both sides, `turn_delivery` `plugin` on
both. Judged at `--judge-all` as registered, 370 judgments a side at
`criteria_cksum` 5539815, judge model sonnet, no judgment left undecided on
either side.

`python3 evals/bench/release.py` reads both arms spanning CLI **2.1.272 and
2.1.273** — the wide arm crossed a release where the scoped arm did not — and
the split is 248/122 on the control against 240/130 on the edit, **p = 0.5872**:
no arm is imbalanced across the boundary. `python3 evals/bench/concurrency.py`
reads each side declaring 4 and reconstructing to 2 in flight, so the
declaration is conservative; the 19 arm-days the sweep still flags are the
2026-08-12 to 08-14 snapshots that predate the flag, which
[`concurrency-audit.md`](concurrency-audit.md) already accounts for.

| counter | control | edit | | |
|---|--:|--:|---|---|
| `never_cut_failures` | 0 | **3** | rise | p = 0.1250 |
| `quality_fails` | 50 | **54** | rise | p = 0.3635 |
| `safety_fails` | 9 | 7 | fell | |
| `violations_total` | 31 | 18 | fell | |
| [#49] turn gate | | | held | +0.0 turns over 38 cells, 3 rising, 0.0-turn floor |

Both rises are inside the sampling noise of the round-wide count and no risen
cell is testable at five reps a side, so under the [#259] gate **Bar A holds as
registered**.

### The never-cut rise is the round's least comfortable number

Three responses dropped a never-cut keyword where the control dropped none, and
all three are haiku:

| case | model | rep | keyword dropped |
|---|---|--:|---|
| `conditional` | haiku | 0 | `leak` |
| `destructive` | haiku | 1 | `sessions` |
| `destructive` | haiku | 4 | `sessions` |

`destructive`/haiku is screened against its measured master-rules rate and
clears — *"within the measured master-rules rate: destructive/haiku 2 of 5
against 8%"* — and `conditional`/haiku is a single flip on a cell with five runs
a side, which no test can reach. The round-wide count reads p = 0.1250.

**What that does and does not say.** [Round 54](round-54.md) measured this bar's
detection curve at five reps a side: the round-wide count alone fires four times
in five at about **+23**, so a +3 on a counter that starts at 0 is far inside
what this design cannot resolve. The bar is cleared because nothing testable
rose, not because the round demonstrated the edit is harmless on never-cut
content. **This round says so rather than implying the bar is sharper than it
is**, exactly as its own registration promised. What buys the sharpness back is
reps on those two cells, and the registration is explicit that reps are not
bought unless a counter rises — this one did, at 0 to 3, and Bar B is the next
registered purchase rather than a rate screen on `conditional`/haiku.

### Disclosures, none of them gates

- **The quality strata moved in opposite directions.** Answers that hand a
  decision back went 17 of 38 to 21 of 48; answers that resolve it went 33 of
  252 to 33 of 242. The flat `quality_fails` count hides that **the resolves
  stratum got slightly worse** while the count rose mostly through the other.
- **Arrow forms fell sharply.** Chains of three or more went 16 to 5 and
  two-term mappings 13 to 10; closing offers went 2 to 0. The edit touches
  neither, and `violations_total` falling 31 to 18 is where that shows.
- **`one_turn` is flat**, 152 to 150 over the round, so the edit did not buy its
  compression by reading less.
- **The rule-adherence cases moved and may not be read as a target.**
  `decision` went 8 pass to 10, `conditional` 2 to 4, `floor` 5 to 4. They are
  disclosure only, per `evals/CRITERIA.md`.

### `report.py` exits 1, and Bar A is not that exit status

With no `--target` the script scores its default, `output_tokens`, and rejects
on it: 36 of 70 cells improved, sign test p = 0.905. This round registered no
token target for `report.py` — its target is prose words on the licensed stretch
and is scored by `evals/pilot/score_claims.py`. Bar A names the counters it
means, and [round 55](round-55.md) read its own round-wide bar the same way.

The stratification note is worth keeping for the next reader: 3 cells did not
vote because their reading rate crossed the floor, and `conditional`/sonnet did
not vote because it mixes edited and non-edited answers ([#209]).

### Where the round stands

The scoped target accepted at 0.903, p = 0.0247, and **Bar A holds**. Bars B and
C — the replication and the holdout — are registered above and **neither has
been generated**. The edit is not validated until both are, and nothing about
this round may be released before then.

---

## Bar B: the replication fails, and the edit reverts

**240 runs, 120 a side, 20 reps per stem per side, zero failed.** The same six
cases, sonnet, `--turn-delivery plugin`, four shards split by rep offset, two
per side, both sides simultaneous from the two trees, scored by the same
`evals/pilot/score_claims.py` at the same seed. `rules_cksum` 594915793 against
3641437234 and `cases_cksum` 1852778470 on both sides, all four verified against
this registration before the pass started.

The control side came from a worktree at `ef1fb2e` rather than at `master`,
because Bar A merged and `master` now carries the edit. The rules text there is
byte-identical to the one the scoped arm's control used, at the same checksum.

Generated 2026-09-16 into 2026-09-17. A usage limit stopped all four shards at
the eight-consecutive-failure rule with 192 of 240 runs banked; no failed key is
recorded as done, so re-running the identical command regenerated exactly the 48
that were missing. `release.py` reads both arms spanning CLI **2.1.273 and
2.1.274**, split 94/26 on the control against 98/22 on the edit, **p = 0.6286**:
no arm is imbalanced across the boundary. `concurrency.py` reads each side
declaring 4 and reconstructing to 2.

### The target does not replicate

| stem | n/side | control | edit | ratio | round 70 scoped |
|---|--:|--:|--:|--:|--:|
| `index` | 20 | 1583.0 | 1453.0 | 0.918 | 0.863 |
| `metric` | 20 | 1081.0 | 993.0 | 0.919 | 0.892 |
| `rollback` | 20 | 567.0 | 567.5 | **1.001** | 0.957 |
| **stratified** | | | | **0.946, p = 0.0721** | 0.903, p = 0.0247 |

**The registration named this outcome in advance and called it a failure rather
than a partial success:** *"A ratio that lands between 0.90 and 1.00 without
reaching alpha is a failure of this bar, not a partial success: round 70's whole
claim is that this quantity moves, and a sample is not a measurement."* 0.946 at
p = 0.0721 is that case exactly. **Bar B fails, and by the standing order the
round stops here — Bar C is not bought.**

### The bounds all held, and they were never the claim

| bound | reading | floor | verdict |
|---|--:|--:|---|
| fixture-token coverage | 1.046, one-sided p = 0.9675 | must not fall | held |
| the licence still fires | 5.59 pooled | 5.0 | held |
| `date_trunc` never-cut keyword | 20/20 in all four cells | any loss rejects | held |

Coverage moved **up** on two stems of three, so the replication does not even
raise the cheap-win reading the bound exists to exclude. What failed is the
target.

### The disclosure that matters more than the p-value

| family | round 70 scoped | replication |
|---|--:|--:|
| `register-*`, licensed | 0.903, p = 0.0247 | 0.946, p = 0.0721 |
| `deep-*`, unlicensed | 1.040, p = 0.4448 | **0.945, p = 0.3304** |

**In the replication the unlicensed family fell by the same factor as the
licensed one.** The scoped round's discrimination argument was that `deep-*` did
not move while `register-*` did, which is what a relocation into check 2
predicts and what a general shortening does not. Here both families read 0.945
and 0.946. Neither is significant on its own, and the round is not entitled to
read a null `deep-*` movement as confirmation in one pass and ignore a matching
one in the next.

So the honest reading is not "the effect is real but smaller than measured". It
is that **the scoped round's 0.903 is not reproduced, and the specificity that
made it interpretable as a licence effect is absent from the replication.** A
single sample produced both the effect and its discriminator; a second sample
produced neither.

**One era caveat, which does not rescue the round.** The scoped arm ran entirely
on CLI 2.1.272 and the replication on 2.1.273 and 2.1.274, and
[round 37](round-37.md) measured a syntactic behaviour moving 4.7x in five days
at byte-identical rules. Each pass is internally clean — both sides simultaneous,
balanced across the boundary — so neither contrast is confounded. What the era
gap bounds is the comparison *between* the two passes, and the direction of that
caveat is symmetric: it is as available to explain the 0.903 as the 0.946.

### The edit reverts in full

`rules/laconic.md` returns to the text at `ef1fb2e` and `rules/dist/*.md` is
regenerated, taking `rules_cksum` back to **594915793**. Nothing from this round
ships, and `tools/release-due.sh` returns to exit 0.

**That is the fourteenth round in the over-length cluster and the fifth
intervention on this paragraph.** Rounds 07, 08, 09 and 29 bounded a licence in
prose and failed; round 10 moved one and won; this round moved one, separated
once at p = 0.0247, and did not separate again. The move-it-do-not-bound-it rule
keeps round 10 and does not gain a second data point here.

**What [#150] is owed next is not another edit to this paragraph.** Three
intervention classes have now been tried on it — rewording, scoping, relocation
— and the round's own registration said where that leaves it: *"the honest
conclusion is that [#150] needs the judged redundancy verdict [#155] specifies
rather than another edit to the paragraph."* [#155]'s detector is parked at
55.3% precision and may not be promoted inside a round, so closing this needs
that detector's precision raised first, as its own unit of work.
