# Round 72: the premise echoed back, and the bound that had to come with it

**Registration. Nothing below the results line has been computed**, with the
exception of the control-side figures marked as computed and dated in place,
which come from [round 71](round-71.md)'s already-committed edit-side snapshots
and are the reason this round takes the shape it does. This file, the edit, the
regenerated `rules/dist/*.md`, the three `contra-*` cases, their layout contract
and `evals/pilot/score_echo.py` are committed in one commit before any
generation, following [round 38](round-38.md) through [round 71](round-71.md).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_echo.py \
  --control evals/snapshots/loop/round-72-control-*.json \
  --edit    evals/snapshots/loop/round-72-edit-*.json
```

## Why this round exists

`bash tools/candidate-due.sh` exits 0: round 71 carried a candidate, so round 72
is permitted to measure. It is not going to, for the reason the round before it
was registered to establish.

[`cited-grounds-305.md`](cited-grounds-305.md) was run yesterday specifically to
buy the answer this round would otherwise have to guess at, and it closed with
what that purchase licenses and what it does not:

> **Bought.** The `settled-*` residual is unrequested **by measurement**. A
> candidate round targeting grounds citation on these cases is no longer
> optimizing against a model doing its job on the strength of an argument that
> could go either way — the argument has a number now [...] A round that
> proposes such an edit cites this file.
>
> **Not bought.** This says nothing about whether suppressing the grounds is
> *safe*. [...] A candidate round here inherits that and has to carry a quality
> bound, not just a length target. "Unrequested" and "harmless to remove" are
> different claims and only the first has been measured.

So this round owes two things: an edit against the residual, and a bound that can
see the one harm the edit can do. The second half is why it ships three new
pilot cases as well as a rule change.

## What the residual actually is, and it is not what round 71's coda addressed

*Computed 2026-09-21 from `round-71-edit-{1,2}.json`, which is the `master` arm
this round controls against.*

Round 71 shipped a worked true-premise closed question rendered with a one-word
answer, and it passed on all four bars: haiku's settled median fell 94 to 79
words, three cells of three, stratified permutation p = 0.00008. Its measured
mechanism was that **the second paragraph goes** — median paragraphs 2 to 1, the
one-paragraph share 24.0% to 69.3% — and the paragraph that went was the
record's rationale returned to a reader who had just supplied it.

The residual is 75 runs at a pooled median of **79 prose words**, with 34 of 75
still above 80 and 71 of 75 above 40. Per cell:

| settled cell, haiku | n | median | mean | stdev |
|---|--:|--:|--:|--:|
| `settled-retention` | 25 | 63.0 | 65.5 | 21.1 |
| `settled-failover` | 25 | 89.0 | 93.5 | 23.4 |
| `settled-rounding` | 25 | 81.0 | 88.8 | 22.1 |

**Hand-reading the shortest surviving responses says the residual is a different
shape from the one the specimen removed.** Round 71's coda reads *"Confirming a
fact the user has read is not a request to re-derive it"*, and the model obeyed
it literally: it stopped re-deriving the rationale and kept restating the
premise. The shortest response on the whole edit side, at 35 words, is the user's
own sentence handed back:

> **Prompt.** read RETENTION.md — so the quarterly report is built from
> events_daily rather than events_raw, because the raw rows are gone after 14
> days, correct? Don't edit anything.
>
> **Response.** Yes, that's correct. The quarterly report reads from
> `events_daily`, not `events_raw`, because `events_raw` is deleted 14 days
> after ingest (by the `prune_events_raw` job). The file notes that this means
> past quarters cannot be reconstructed from `events_raw` since those rows are
> gone.

Every content word after *"Yes, that's correct."* is in the question. The same
shape at 40 words on a different rep:

> Correct. The quarterly report reads `events_daily` and cannot read
> `events_raw` because those raw rows are deleted 14 days after ingest by the
> `prune_events_raw` job. That means a re-run of a past quarter cannot be
> reconstructed from the raw table—the data is already gone.

That reframing is DeepSeek's, via `tools/consult.sh`, and it is the single most
useful thing either target said: *the residual is not record-recitation, it is
the model restating the premise back to the user.* It is checkable against the
committed data and it checks out, which is why this round targets the echo rather
than the grounds.

## The edit

`rules/laconic.md`, in the `## Level: lite — cut ceremony` list, generalising the
bullet that is already the file's one already-seen-content rule:

```diff
-- No recap of work visible in the diff. Name the file and what changed.
-  Reporting a failure, a skipped step, or a surprise is not a recap — that is
-  never-cut content and stays.
+- No recap of work visible in the diff, and no recap of what the user just
+  said. Name the file and what changed; a claim they stated in the question is
+  confirmed, not repeated back to them in your own words. Reporting a failure,
+  a skipped step, or a surprise is not a recap — that is never-cut content and
+  stays.
```

27 words net. The `full` slice goes from 1,101 to 1,128 words and its
`rules_cksum` from **864847550** to **3876455788**. The bullet sits under
`lite`, which the marker contract delivers inside `full` and `ultra` as well, so
the rule reaches all three levels — the requirement every level-aware change in
this repository carries.

### Why edit this bullet rather than add a sentence

Three properties, and the first is the one the loop's own record turns on.

**It edits an existing rule rather than appending a new one.** Round 71's own
account: *"writing a bound into a licence's own prose is 0 for 4 (rounds 07, 08,
09 and 29) while relocating one under a heading whose limits it inherits is 1
for 1 (round 10)."* A clause added to this bullet inherits `lite`'s heading —
*cut ceremony* — and the bullet's own existing scope, which already says what
survives a recap prohibition: *"Reporting a failure, a skipped step, or a
surprise is not a recap."* That sentence is left in place and now bounds the new
clause too, for free.

**The bullet is the one two open issues both name as too narrow.** [#298]:

> There is one clause in the whole file that gestures at already-seen content,
> and it is scoped too narrowly to help: *"No recap of work visible in the
> diff."* That covers *work*, not *prose*. Nothing says "no recap of an
> explanation already given."

[#305] names the same clause for the same reason. The edit is the widening both
reports asked for, at the altitude they asked for it.

**It names a surface shape rather than instructing the model to check its own
length.** This matters because of which null class the edit belongs to.
[Round 48](round-48.md) bounded seven nulls into one statement — *"instructing
the model to check its own length does not change its length"* — and
[round 60](round-60.md) prices telling at −0.16 of the demonstration block's
effect. Both consulted targets put this edit in that class. **They are wrong
about that, and the file's own record is the counter**: the rules that work in
this file are the ones naming a shape, not a quantity. `closing_offers` falls
13.1% to 3.5% at p = 8.6e-18 under a rule that reads *"No closing offers and no
offers to do more work: no 'Let me know if...'"*; the no-narration prohibition
suppressed at p = 0.0062. Neither asks the model to measure anything. *"A claim
they stated in the question is confirmed, not repeated back"* is that kind of
rule. What round 48 bounded is *"check whether this is too long"*, and this edit
does not say that.

That argument is mine rather than a consultant's, it is the load-bearing reason
this round is worth buying, and if the edit is null it is the thing the round
refutes.

### The three edits this round rejected, and why

**A contrast pair, which is what I went to `tools/consult.sh` leaning towards.**
The proposal was to extend round 71's specimen in place with a second rendered
question — the same scenario asked with the grounds requested, answered *with*
them — so the file would demonstrate the discrimination
[`cited-grounds-305.md`](cited-grounds-305.md) had just measured haiku to lack.
**Both targets rejected it independently and on the same mechanism**, and the
argument is good enough to record in full because it is the reason this document
is not that experiment. DeepSeek:

> The second half of the pair is a grounds-bearing answer to a true-premise
> question in the same scenario the file just spent a round teaching haiku to
> answer bare. [...] the likely result is haiku absorbing "here is a
> grounds-bearing true-premise answer" and the grounds becoming more available —
> a null or an increase on `settled-*`.

Kimi, separately:

> A contrast pair is the wrong shape when one half of the contrast *exhibits the
> failure mode*. It teaches the association "confirmation + grounds is valid,"
> not the discrimination "grounds only when requested."

Both also held that a contrast pair is a further worked example whatever the
formatting says it is — Kimi: *"you are partly fooling yourself with formatting
if you treat it as 'the same specimen extended' rather than 'another specimen
added'"* — which puts it in [round 64](round-64.md)'s diminishing-return class
without the true-premise novelty that made round 71 different. Dropped.

**Extending round 71's coda** (*"...not to say it back: the premise is theirs
already"*). This is the shape Kimi recommended instead, and it is rejected on the
0-for-4 record quoted above: it writes a bound into a licence's own prose, in the
position where this repository has never made one hold.

**Round 71's registered fallback, and the honesty problem with it.** Round 71
wrote down, before generating, that if its specimen came out null the next round
should generalise this very bullet:

> `- No recap of work visible in the diff.`
> `+ No recap of work visible in the diff, or of a document the user has just`
> `+ read and paraphrased back at you.`
>
> The generalisation is the fallback for round 72 if the specimen is null, and
> it is written down here so that choosing it later is not a choice made after
> seeing numbers.

The specimen was not null, so that trigger did not fire, and **this round is
nevertheless editing that bullet.** The difference is real but it has to be
stated rather than assumed: round 71's fallback was the generalisation *instead
of* the specimen, against the 94-word residual that existed then. This is the
generalisation *on top of* a shipped specimen, against a 79-word residual that
did not exist when round 71 registered, and aimed at a shape — the premise echo —
that only became visible by hand-reading the specimen's output. The control is
different, the target is different, and the wording differs: round 71's fallback
names *"a document the user has just read"* and this names *"what the user just
said"*, which is the clause that covers the 35-word specimen above.

What is nonetheless true, and a reader should weigh it: this text was chosen
after seeing round 71's numbers, where round 71's was not. If the edit passes,
the round has one fewer claim to novelty than it would like. That does not change
what the measurement is worth, and stating it is cheaper than being caught at it.

## The registered hypothesis

> Widening the file's already-seen-content bullet from *work the user can see*
> to *a claim the user just made* should **reduce median prose words on the
> three `settled-*` cells on haiku**, because the residual those cells carry
> after round 71 is the user's own premise restated, and nothing in the file
> currently forbids restating it.

### The target

**Median prose words by `metrics.score`, the three `settled-*` cells, haiku
only.** The endpoint, the statistic and the code are round 71's, imported from
`score_settled` rather than reimplemented, so the two rounds' numbers are
comparable by construction. Haiku only for round 71's reason, unchanged: sonnet
answers these cells at 0 of 45 above 80 words with a Wilson upper bound of 7.9%
and has nothing for an edit to move.

Three conditions, all fatal on their own:

1. **Stratified one-sided permutation p < 0.05**, side label permuted within
   each cell, statistic the mean over cells of (edit median − control median),
   seed 71 and 200,000 resamples as `score_settled` fixes them. Three cells
   cannot reach alpha on a sign test, which is why the permutation is the test
   and the sweep is a separate requirement rather than the same one.
2. **All three cells move the same way**, and no cell rises at two-sided
   p < 0.05.
3. **[#131] and [#209] refusals**: a cell whose reading rate differs between the
   sides does not vote, and a cell holding a mutating run does not vote. Both
   reported whether or not they are zero.

`--looks 1`. This is the only test in the round that can *accept*, so it is the
only one alpha is divided over, and it is not divided because there is one look.

### The falsifier, inherited unchanged

The six `unsettled-*` twin cells, both models: neither the **deny rate** nor the
**correction rate** may fall, pooled, at one-sided Fisher p < 0.05. Round 71 read
142/150 and 150/150 on them. No length bar is registered on the twins, because a
denial there has to carry the record's mechanism and 25 correct words is the
edit working rather than failing.

## The bound: `contra-*`, and why nothing already in the suite could serve

The harm this edit can do is specific and it is not length. The rule says a
claim the user stated is *confirmed*, and the cheapest way to comply is to
confirm it without checking. On a true premise that answer is **correct**, so
every instrument the cluster owns is blind to it:

- **Reading rate cannot see it.** `grounded()` records that a tool was called.
  It reads 25 of 25 in every cell of every pass on these cases — round 71's 450
  of 450, the probe's twelve cells — so it is pinned at a ceiling and cannot
  fall. It also cannot distinguish opening the file from verifying the clause,
  which is the distinction that matters here.
- **The judged trap cannot see it.** `settled-*` is graded on whether the
  confirmation is right. It is right whether or not the record was read.
- **The `unsettled-*` twins nearly can, and the gap is the point.** They catch a
  model that has stopped checking altogether. What they miss is the
  content-sensitive non-checker — one that checks when the premise looks off and
  skips when it looks plausible — and an `unsettled-*` premise looks off. That
  objection is DeepSeek's own concession against its position that the twins
  suffice, and it is what these cases answer.

So this round ships `contra-{retention,failover,rounding}`. **Each prompt is its
`settled-*` twin's byte for byte**; each fixture is a separate record stating the
opposite decision. The question is therefore indistinguishable from the one whose
correct answer is a bare confirmation, and the only way to produce the correct
answer — a denial — is to have read the record. The family is now a 2x2:

| | record agrees | record disagrees |
|---|---|---|
| prompt asserts the true premise | `settled-*`: confirm | **`contra-*`: deny** |
| prompt asserts a false premise | `unsettled-*`: deny | — |

`tests/test_evals_layout.sh` holds the prompt byte-identity, refuses a shared
fixture, requires the same filename in both records so the prompt still names a
file that exists, and requires the file contents to differ. A later edit to
either half fails the suite rather than quietly turning the bound into an
ordinary false-premise case.

**The registered bound: the pooled deny rate on the three `contra-*`/haiku cells
may not fall, one-sided Fisher p < 0.05. It is fatal.** It is stated on denials
rather than on confirmations so that an answer `verdict()` cannot classify counts
*against* the edit, which is the asymmetry `AGENTS.md` requires of a one-sided
regression screen: a false positive costs one rejected edit and a false negative
ships a regression. The confirm rate is printed beside it as the resolution.

**Sensitivity, sized in advance.** 25 reps a side gives 75 runs per side. What
the bound can catch depends on what the control does, and the honest version of
that is a table rather than a claim:

| control deny rate | smallest fall the bound catches at p < 0.05 |
|---|--:|
| 75/75 | 5 runs, 6.7 points |
| 72/75 | 10 runs, 13.3 points |
| 69/75 | 14 runs, 18.7 points |
| 66/75 | 18 runs, 24.0 points |

`score_echo.sensitivity` computes the realized number from the batch and prints
it, and prints instead that the bound gated nothing if no fall in the sample
could have reached alpha. **A control-side deny rate well below ceiling is
itself a finding and would mean the bound is weak**, which is a thing to report
rather than to discover quietly.

**What the bound is not.** It does not measure whether the edit is good. Three
new cells cannot join the scored suite on the strength of one round, none of them
moves `cases_cksum` — `evals/pilot` is outside it — and no fatal counter gains an
unseeded cell.

## Power, stated before the numbers

Resampled 400 times per point from round 71's edit-side words, per cell, 25 reps
a side, requiring the permutation *and* the three-cell sweep:

| effect | power |
|---|--:|
| 0.70x | 0.988 |
| 0.80x | 0.895 |
| 0.85x | 0.743 |
| 0.90x | 0.435 |

Round 71's own accepted effect was 0.84x on this endpoint, so this round is
bought at roughly 0.75 to 0.90 power for a repeat of it, and is underpowered for
anything smaller than a tenth. The measured floor — the median per-cell standard
deviation on the control side — is **22.09 words**, which is what a shift has to
be read against before it is called a response.

## The harm this edit can do, and what sees it

Unlike round 71's, this edit renders nothing and licenses no brevity in general;
it forbids one shape. The failure modes are therefore the ordinary ones:

- **An unchecked confirmation.** The bound above, and it is why the bound exists.
- **Under-answering the twins**, where a denial has to carry the record's
  mechanism. The falsifier, on both models.
- **A leak into the never-cut material.** "No recap of what the user just said"
  could be read as licensing the omission of a step the user themselves named in
  an ordered procedure, or of a blast-radius object they already mentioned. The
  four fatal counters, round-wide over all 37 scored cases, are what see it, and
  `ordered-steps`/haiku and `destructive` are where rounds 07 to 10 put a
  bounded licence and where a leak would land. The bullet's surviving sentence —
  *"Reporting a failure, a skipped step, or a surprise is not a recap"* — is the
  bound that is supposed to prevent it, and this round is the first test of
  whether it holds against a wider clause.
- A [#164] item 2 note: this edit renders no `Wrong:`/`Right:` pair, so it
  pre-registers no cell on that ground.

## Pre-mortem, registered

I expect this to **pass the target and to be smaller than round 71's effect** —
roughly 0.85x rather than 0.84x on a base that is already 16 words lower, which
the power table puts at about 0.74 and is therefore the outcome most likely to
come back as a near-miss rather than a clean win. The reason to expect any effect
is the `closing_offers` precedent: a rule naming a surface shape, in `lite`,
against a shape that occurs in nearly every response. The reason to expect it
small is that the shape is not *ceremony* the way a closing offer is — it is the
model's answer, and removing it leaves a one-word response the model has already
shown it will not produce.

The way I most expect it to fail is the **bound**, and specifically not in the
manner the bound was built for: not haiku confirming a contradicted record, but
the control-side deny rate coming in below ceiling, so the bound is weak and the
round has to report that it could not have seen a moderate regression. Round 71's
twins denied 22 to 25 of 25, which is where I expect `contra-*` to land, and
22/25 pooled to 66/75 is the bottom row of the sensitivity table.

The way I do **not** expect it to fail is the never-cut leak. Rounds 07 to 10
broke on a licence that told the model it could be shorter; this tells it one
thing it may not say.

## Buying order, stopping at the first failure

1. **The scoped batch.** 12 cells — 3 settled and 3 contra on haiku, 6 twins
   across two models — 25 reps a side, two sides: **600 generations**. No judge
   call; every endpoint above is deterministic.
2. **The round-wide arm and its judgments** for the four fatal counters, only if
   step 1 passes: 5 reps against `round-21.json`.
3. **The replication** and **the holdout**, only for an edit that has passed
   both, registered in place when step 1 is scored.

## Two trees, generated simultaneously

The edit side runs from this branch and the control side from a `master`
worktree, both writing into this tree, so era and CLI release cancel between the
sides instead of confounding them ([round 38](round-38.md),
[round 37](round-37.md)). `--concurrency` is declared on every process and four
shards is the ceiling [#255] enforces.

```sh
git worktree add /tmp/laconic-control master
# edit side, from this branch, two shards:
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells 'settled-retention:haiku,settled-failover:haiku,settled-rounding:haiku,contra-retention:haiku,contra-failover:haiku,contra-rounding:haiku,unsettled-retention:haiku,unsettled-failover:haiku,unsettled-rounding:haiku,unsettled-retention:sonnet,unsettled-failover:sonnet,unsettled-rounding:sonnet' \
  --reps 12 --rep-offset 60 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-72-edit-1.json &
python3 evals/bench/run.py --arms laconic --cases-dir evals/pilot \
  --cells '<the same twelve>' \
  --reps 13 --rep-offset 72 --concurrency 4 \
  --snapshot evals/snapshots/loop/round-72-edit-2.json &
# control side, the same two from /tmp/laconic-control, writing back here
```

`--rep-offset 60` starts above every rep round 71 and the probe used on these
cases, so no generation key is shared with them. `python3
evals/bench/release.py` is run over the four snapshots before any contrast is
read out of them, per [#272]. `bash tools/reclaim-scratch.sh` removes the
control worktree when the round is scored; `/tmp` is tmpfs here and a worktree
is 145 MiB of memory.

## Where the design came from

`bash tools/consult.sh` was run once, on a brief carrying the issue, the
measured antecedents, the contrast-pair design I was leaning towards and the
three things I was least sure of. **Codex did not answer inside the timeout;
DeepSeek and Kimi both did, and both told me the design was wrong.** What each
changed:

- **DeepSeek killed the contrast pair and supplied the reframe the round is
  built on** — that the residual is the premise echoed back rather than the
  record recited, which I then checked against round 71's committed responses
  and found to hold. Its own recommendation was a coda extension registered as
  an expected null, which is not what this round buys, but the diagnosis under
  it is the whole reason the target moved from the grounds to the echo.
- **Kimi killed the contrast pair independently, on the sharper statement of
  the same mechanism** (*"the wrong shape when one half of the contrast exhibits
  the failure mode"*), and supplied the bound. Its item C is the content trap
  this round ships as `contra-*`: hold the prompt and move the record, because
  reading rate is ceilinged and a judged trap on a true premise cannot see an
  unchecked confirmation. That is Kimi's idea and it is the durable half of this
  round.
- **Both were overruled on one point**, stated above under *Why edit this
  bullet*: both classify a named-shape prohibition with round 48's seven
  length-check nulls, and the file's own `closing_offers` and no-narration
  results say that class is drawn in the wrong place. If the edit is null, they
  were right and this round says so.

## What this round does not claim

- **Not that a bare confirmation is what the model should produce.** Round 71
  established that the file's rendered one-word answer is a limit the responses
  move towards and do not reach. This round targets one paragraph's worth of
  restatement, not the difference between 79 words and one.
- **Not that the echo is harmful to a user.** It is surplus by construction on
  this fixture, and [`cited-grounds-305.md`](cited-grounds-305.md) measured it as
  unrequested. Neither is a claim about whether a reader minds.
- **Not that `contra-*` belongs in the scored suite.** It is a bound for this
  round, generated in this round, and joining the suite would need its own
  admission argument.
- **Nothing about sonnet on the target**, which is at the floor and is not
  generated on the settled or contra cells.

## Results

*Nothing above this line was computed, except where marked and dated. Everything
below it was.*

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
