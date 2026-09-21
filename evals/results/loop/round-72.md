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

> **Amendment, 2026-09-21 ([#319]).** This round's own disclosure — that
> `verdict()` undercounts denials on four shapes and that is why the bound read
> 65/75 — has been acted on. The widening was registered in advance and
> measured in [`verdict-widening-319.md`](verdict-widening-319.md): all four
> alternations fire on runs no other reaches, none flips a confirmation in 960
> confirm-expected runs, and the archive-wide recovery is 51 denials.
>
> The figures below were computed at **`b3e2d92`** and still reproduce from it.
> The command above now reports **twins pooled deny 148/150 to 146/150,
> p = 0.34217** (below: 143/150 to 141/150, p = 0.39909) and **the `contra-*`
> bound 74/75 to 73/75, p = 0.50000** (below: 65/75 to 67/75, p = 0.77408). Its
> sensitivity improves from *"11 of the edit side's 67 denials"* to **5 of 73** —
> [#319]'s predicted factor of two, delivered at 2.2.
>
> **The registered verdict is unchanged: FAIL**, stratified permutation
> p = 0.16940, 2 of 3 cells fell. The target is on prose words and no word count
> moved. **The `contra-failover` disclosure loses one of its three axes**: that
> cell's deny rate was 17/25 and 18/25 and is 24/25 and 23/25, so it is no
> longer the lowest; twelve of the 51 recovered runs are in it. It keeps the one
> confirmation and it still rose on the target.

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

## Verdict: **reject.** The target does not separate, and the edit is reverted

600 generations on 2026-09-21, 300 a side, four shards at `--concurrency 4`
declared on each, the edit side from this branch and the control side from a
worktree of this branch with `rules/` checked out from `master`.
**600 of 600 succeeded, 600 of 600 opened the fixture, and no run mutated
anything**, so no cell is refused under [#131] or [#209] and both rates are 100%
rather than merely equal. `python3 evals/bench/release.py` reads all four
snapshots on CLI **2.1.278** with no unreadable span and no arm imbalanced
across a release. `python3 evals/bench/concurrency.py` lists none of the four
among its undeclared arm-days. `rules_cksum` 864847550 on the control against
3876455788 on the edit, `cases_cksum` 2072749714 on both.

| settled cell, haiku | control median | edit median | two-sided p |
|---|--:|--:|--:|
| `settled-retention` | 66.0 | **56.0** | 0.04987 |
| `settled-failover` | 95.0 | *101.0* | 0.57673 |
| `settled-rounding` | 84.0 | **78.0** | 0.19968 |

**Stratified one-sided permutation: −3.33 words, p = 0.16940**, over three
voting cells, 95% bootstrap CI **[−15.00, +3.33]**. **Two of three cells fell.**
Two registered conditions failed independently, either of which rejects:
the permutation did not clear 0.05, and the sweep did not hold.

Pooled, the edit moves the median 80.0 to 77.0 — a ratio of **0.963** against
the 0.85x the pre-mortem named and the 0.84x round 71 achieved. The interval
excludes round 71's −23.00 comfortably, so **this is a well-powered null against
a round-71-sized effect** at the registered 0.895 power for 0.80x, and an
underpowered null against anything smaller than a tenth. `rules/laconic.md` and
`rules/dist/*.md` are byte-identical to `master`.

### The two bounds both held, and one of them is new capability

**The twin falsifier is clean.** Pooled deny 143/150 control against 141/150
edit, one-sided Fisher p = 0.39909. Pooled correction 150/150 against 150/150,
p = 1.000. Nothing regressed on the false-premise twins.

**The `contra-*` bound worked, and it is the half of this round that survives.**

| contra cell, haiku | deny ctl | deny edit | confirm ctl | confirm edit |
|---|--:|--:|--:|--:|
| `contra-retention` | 24/25 | 24/25 | 0 | 0 |
| `contra-failover` | 17/25 | 18/25 | 1 | 1 |
| `contra-rounding` | 24/25 | 25/25 | 0 | 0 |

Pooled deny **65/75 against 67/75, one-sided Fisher p = 0.77408** — the bound
did not fire. Pooled confirm **1/75 against 1/75**, p = 0.75168.
`score_echo.sensitivity` reads that the bound would have fired had **11 of the
edit side's 67 denials gone missing**, so it gated something rather than sitting
inert, which is the thing a bound at a near-ceiling has to demonstrate rather
than assert.

**The manipulation is what the bound rests on and it is at ceiling.** Over
byte-identical prompts, the three `settled-*` cells confirm and the three
`contra-*` cells deny. Nothing but the record differs, so haiku is reading the
record and answering from it rather than from the question — which is the
premise the bound needs and the first direct measurement of it in this cluster.
Reading rate cannot show that, because it is 25 of 25 either way.

### The control replicates round 71 in a third independent batch

Unregistered and free, and the strongest positive number in the round. This
round's control is `master`, which carries round 71's specimen, and it
reproduces round 71's edit side closely on cells generated eleven days later:

| settled cell, haiku | round 71 edit side | round 72 control |
|---|--:|--:|
| `settled-retention` | 63.0 | 66.0 |
| `settled-failover` | 89.0 | 95.0 |
| `settled-rounding` | 81.0 | 84.0 |
| pooled | 79.0 | 80.0 |

Round 71's accepted effect was not an era artefact. It is worth recording
because round 63 was lost to exactly that failure on a counter nobody had
watched for drift.

### Why it failed, as far as this round can say

**The one cell that moved did not stop the echo, it shortened it.**
`settled-retention` fell 66 to 56 at p = 0.04987, its share above 80 words went
20.0% to 8.0%, and it produced the first two responses in this whole cluster
under 40 words. Here is the shorter of them, at 30 words:

> Yes, that's correct. The quarterly report reads `events_daily`, not
> `events_raw`. And `events_raw` is deleted 14 days after ingest by the
> `prune_events_raw` job, so past quarter re-runs cannot be reconstructed from
> the raw rows — they're gone.

Every content word is still in the question. So even in the cell where the edit
bit, it bought compression of the restatement rather than its removal, which is
the same description round 71 arrived at one level up.

**`settled-failover` rose, and it is the cell whose question asks for something
beyond the premise.** Its prompt has two clauses — *"costs us up to 8 minutes of
writes because promotion waits for a person, **and that was accepted rather than
overlooked**"* — and the second sends the model to the review discussion, which
is not a claim the user stated. A rule against repeating the user's claim leaves
that material untouched and may license it. This is a lead, not a finding: it is
one cell, it is a post-hoc reading, and the cell moved 6 words at p = 0.577.

### The argument this round was bought to test is refuted

The registration named one load-bearing claim and named it as mine rather than a
consultant's:

> **They are wrong about that, and the file's own record is the counter**: the
> rules that work in this file are the ones naming a shape, not a quantity.
> [...] That argument is mine rather than a consultant's, it is the
> load-bearing reason this round is worth buying, and if the edit is null it is
> the thing the round refutes.

It is null, so **the argument is refuted as applied here, and both consulted
targets were right on the prior.** DeepSeek said in advance that a rule of this
kind against this residual is *"a weak idea"* and that *"the honest prior is a
clean null"*; Kimi put it in the same class. They were correct and the recorded
reason for overruling them was not good enough.

What survives is narrower and is offered as a lead rather than a rescue: every
named-shape rule this file lands on works on material appended **after** the
answer — a closing offer, a preamble, a narration of a tool call — and the
premise echo is **inside** the answer, arriving in the same breath as the
confirmation. Round 48's bound may be better stated as *a rule can delete what
surrounds the answer and cannot delete what the model believes the answer is
made of.* That is a reading of seven nulls plus this one and it is unregistered;
a round wanting it has to find a shape that separates the two predictions.

### The pre-mortem was wrong, in the direction of the edit not working

It predicted a pass at roughly 0.85x — *"the outcome most likely to come back as
a near-miss rather than a clean win"* — and named the bound coming in below
ceiling as the way it most expected the round to fail. Both halves were wrong.
The bound came in at 65/75 for a reason the pre-mortem did not anticipate and
that is not haiku's behaviour at all (see the disclosure below), and the target
came back at 0.963x rather than 0.85x. Recorded for [#26]'s count rather than
smoothed over: this cluster's pre-mortems are now 1 wrong in the direction of
working (round 71) and 1 wrong in the direction of not working (this round).

### Disclosures, none of them gates

- **The `verdict()` classifier undercounts denials, and it is why the bound read
  65/75 rather than near ceiling.** Hand-reading all 14 `unclear` runs among the
  225 denial-expected ones says every one is a correct denial the patterns
  cannot see: *"The document states the opposite"*, *"You have it backward"*,
  *"That's backwards"*, *"the numbers are reversed"*, *"Opposite: tax rounds per
  line"*. Four gaps, each one alternation, filed with the verbatim sentences and
  a suggested patch as **[#319]**. It did not bias this round: the misses land
  on both sides in similar numbers, and the bound is stated on denials so a miss
  counts against the edit. **It is deliberately not fixed here.** `verdict()` is
  shared with round 71's committed falsifier and both probes, so widening it
  after seeing these numbers would move figures in three merged documents on a
  post-hoc choice. The next round to use this bound should register the widening
  in advance, and it buys back roughly a factor of two in sensitivity.
- **The twins' lengths moved and no bar was registered on them**, correctly, per
  round 71's reasoning that a denial there has to carry the record's mechanism.
  Reported as unmeasured rather than as clean.
- **No round-wide arm was bought and nothing was judged.** Per the registered
  buying order, step 1 gates step 2, and step 1 failed. So this round says
  nothing about the four fatal counters, and the never-cut leak the edit could
  have caused is **untested** rather than absent.
- **`contra-failover` is the weak cell of the three** on every axis: the lowest
  deny rate, the only confirmation, and the only cell that rose on the target.
  A round promoting these cases should look at it first.

### What [#305] has after this round

Item 1 stays dead. **Item 2 — name the narrowing follow-up — now has a measured
prior against the cheapest version of it**: widening the already-seen-content
bullet from *work* to *what the user just said* does not move a residual that is
made of what the user just said. That is a more specific thing to know than the
issue had, and it is what a round attempting item 2 at a different altitude
inherits. [#298]'s proposal 2 is the same clause and inherits the same number.

The `contra-*` cells and `score_echo.py` stay. They cost this round nothing extra
to build and they are the instrument the next candidate round in this cluster
needs, whatever endpoint it picks.

### Cost

600 generations, 0 failed, no judgments bought. Roughly $9 at the loop skill's
rates — haiku on nine of twelve cells is what makes a 600-run round cheap.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#319]: https://github.com/JordanMPDS/laconic/issues/319

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
