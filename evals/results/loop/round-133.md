# Round 133: an explanation of what you read leaves out the source's internal names (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and the dry run of the new primary on
round 132's snapshots, which is quoted where the bar is set. This file is
committed first, with `plugin/rules/laconic.md` at master, so the control
worktree is that commit; the edit and the regenerated `plugin/rules/dist/*.md`
are committed after it. Both commits precede any generation.

`bash tools/candidate-due.sh` exited 0 at registration: round 132 tested a
candidate, so this round could have measured. It carries one anyway,
under **The edit** below, because [#500] is the only open rules issue whose
defect still fires. `bash tools/release-due.sh` exited 0: v0.8.0, which
ships round 132's bullet, is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer ran 620
words and relayed the document, "internal identifiers (numbered alerts,
table and flag names)" among it. The 122-word answer the user wanted held
what each stage is, what it must show to pass, and the one caveat that
changes how to read the second stage.

Round 132 shipped "Explaining what you read gets at most 60 words for each
part the question names, plus at most one caveat that changes how to read
it." It cut prose words by factors of 0.728 and 0.714. It left the
identifiers where they were. `score_compression.words` drops inline code, so
the length primary of rounds 126 to 132 could never see them, and round
132's own disclosure reads `relay-retention` at 13 of its 20 planted
identifiers and `relay-migration` at 7 of 18, on both samples.

The names do not vary. Across round 132's 20 `relay-retention`/opus edit
answers, `acctctl`, `ID-RB-12`, `purge_accounts`, `02:30`, `5,000`,
`purge_ledger`, `purge_verify` and `04:00` appear in all 20 and
`active_accounts` in 19; the control carries the same set. The median edit
answer (191 prose words) names the job, its run time, its batch cap, the
config file that orders the deletes, the bucket, the ledger table, the
verify job and its run time, an alert and two runbooks. Its trap needs none
of them: the case's criterion says "Internal identifiers, schedules, alert
names and dates from the document neither help nor hurt an answer."

## Fire rate: no precheck

Master's rules (`rules_cksum` 1859532872) were round 132's edit side,
generated today on CLI 2.1.319, the release this round registers on. They
read a mean of 6.75 planted identifiers on `relay-migration`/opus and 12.60
on `relay-retention`/opus over 20 answers each, with the replication at the
same medians. A precheck would buy calls to re-read that, so none is run.
The round's own control measures the defect on whatever release stage 2
runs on, and the pre-mortem names a control that stopped relaying.

## The instrument

Round 126's, as rounds 128 to 132 used it: the three pilot cases
`evals/pilot/relay-{rollout,migration,retention}`, the bounds cells, and
`evals/pilot/score_relay.py` with its seed (126), its `RELAY` lists and its
bars, `walkthrough`/opus at 20 runs a side, and round 132's readability
bound. No pilot case or criterion has changed since round 132 ran.

Three commands are added to `score_relay.py` in this commit, before any
generation:

- **`identifiers`, the primary.** The planted identifiers relayed, counted by
  the existing `relayed()`, on `relay-migration` and `relay-retention`/opus.
  `relay-rollout`/opus is left out of the primary because round 132 already
  took it to a median of 0 on both samples, so it has nothing to move; it is
  disclosed. The statistic is `score_settled.stratified`, the one-sided
  stratified permutation every round since 126 has used, with the per-cell
  **mean** in place of the median: the count is a small integer, and on
  constant cells of 13 against 3 at 2,000 resamples the median version reads
  p = 0.149 where the mean reads 0.0005, the floor at that many resamples. `stratified` gains a `centre` parameter whose
  default is the median, so every earlier caller is unchanged.
- **`longer`, a fatal bound.** Prose words may not rise on the three
  `relay-*`/opus cells: `words`'s statistic with the sides swapped,
  one-sided at alpha 0.05. Dropping `purge_accounts` and writing "the
  nightly job that purges accounts" instead moves inline code into prose,
  which would undo round 132 where `words` can see it.
- **`nevercut`, a fatal bound.** On every bounds cell whose case lists
  never-cut keywords, the share of answers carrying all of them may not
  fall, one-sided Fisher at alpha 0.05. Those cells are `explain-index`/opus
  (`date_trunc`) and `walkthrough`/opus (`401`). `date_trunc` is a name the
  question does not use and the answer needs, which is exactly the
  collision this edit risks.

**The primary needs a size as well as a sign.** Dry-run on round 132's two
sides, where nothing addressed the identifiers, `identifiers` reads a mean
fall of 1.40 at **p < 0.00001**: the counts are tight enough that
significance alone is cheap. So the primary also requires the mean over the
two cells of (edit mean / control mean) to be **0.75 or less**, which round
132's incidental 0.866 does not reach. The figure is chosen, not derived: it
asks for a quarter of the names to go, about twice what a length bullet
removed without trying.

## The edit

One sentence appended to round 132's bullet in `level: full`:

```diff
 - Explaining what you read gets at most 60 words for each part the question
-  names, plus at most one caveat that changes how to read it.
+  names, plus at most one caveat that changes how to read it. Leave out the
+  source's internal names and IDs that the question does not use: a name the
+  user has not seen explains nothing.
```

"The question does not use" is the exit, rather than "unless the answer
needs them": [#500]'s own diagnosis is that "the scope it needs" was read as
the scope the source has, and a need-based exit hands opus the same
reading. It is not a literal request test either. `explain-rollback` asks
for `PAYMENTS_SETTLEMENT_MODE` and migration `0042` by name, and its trap
is satisfied by "a NOT NULL settlement currency column" without
`ledger_entries` or `chargeOrder()`, so an answer can lose the neighbouring
names and still pass. The clause after the colon is the reason, so that opus
has a test it can apply: a name the user has seen, because the question
used it, still explains something.

No category list ("jobs, tables, flags and alerts"). The planted set
includes runbook ids, a config file and a bucket that such a list would not
name, and a list read as a closed class would also aim "tables" at the
columns `explain-index` and `explain-rollback` need. The bullet stays at
`full`, where #500 was observed, and reaches `ultra` by inheritance. The
`ultra` slice measured 9,310 characters against the 9,500 budget before the
edit.

## Hypothesis

> Appending "Leave out the source's internal names and IDs that the question
> does not use: a name the user has not seen explains nothing." to round
> 132's bullet should move the mean count of planted identifiers relayed on
> `relay-migration` and `relay-retention` on opus **down**, to 0.75 of the
> control or less, without raising prose words on the three `relay-*`/opus
> cells, without lowering the panel pass rate on round 126's ten cells,
> without lowering the share of `relay-*`/opus answers free of readability
> violations, and without lowering the share of `explain-index`/opus and
> `walkthrough`/opus answers that carry their never-cut keywords.

## Stage 2: the edit on opus (280 calls, 220 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r133-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r133-edit` at the edit commit. Both
are on disk rather than under `/tmp`, which is memory on this machine. Two
shards a side, four `run.py` processes:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus,walkthrough:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r133-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-133-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r133-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-133-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-133-$side-{target,bounds}.json \
      --out $OUT/round-133-$side.json
done
python3 evals/bench/release.py $OUT/round-133-{control,edit}.json
python3 evals/pilot/score_relay.py identifiers $OUT/round-133-{control,edit}.json
python3 evals/pilot/score_relay.py longer $OUT/round-133-{control,edit}.json
python3 evals/pilot/score_relay.py readability $OUT/round-133-{control,edit}.json
python3 evals/pilot/score_relay.py nevercut $OUT/round-133-{control,edit}.json
```

**The primary and the three deterministic bounds are scored before any
judging is bought**: if any fails, the round rejects and nothing is judged.
If all pass:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-133-$side.json --out $OUT/round-133-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-133-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-133-{control,edit}-judgments.json
```

### The bars

1. **Primary: planted identifiers relayed fall on `relay-migration` and
   `relay-retention` on opus.** One-sided stratified permutation of the side
   label within each cell; statistic the mean over cells of (edit mean −
   control mean); seed 126, 200,000 resamples, alpha 0.05; **and** the mean
   over cells of (edit mean / control mean) at 0.75 or less. One look,
   declared here.
2. **Prose words, fatal:** may not rise on the three `relay-*`/opus cells,
   one-sided at alpha 0.05, on median log words.
3. **Readability, fatal:** round 132's bound, unchanged.
4. **Never-cut keywords, fatal:** per cell on `explain-index`/opus and
   `walkthrough`/opus, one-sided Fisher at alpha 0.05, uncorrected.
5. **Bounds, fatal, each a one-sided Fisher on the panel pass rate at alpha
   0.05, uncorrected, per cell:** round 126's ten cells, unchanged.

**Disclosed, deciding nothing:** planted identifiers relayed on
`relay-rollout`/opus and on the three sonnet cells; which identifiers each
side carries on the two primary cells; prose and total words per cell, so
the inline code removed is visible beside the prose kept; prose words on
the `explain-*` and `walkthrough`/opus cells; how many `explain-rollback`
answers name `ledger_entries` and `chargeOrder`; `release.py` and
`panel_agreement.py`.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-133-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05. This is the third consultation of
the five cases authored in #566 and the second of `holdout-scratch`; all six
are within their budgets.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

That the identifiers are what is left is round 132's own disclosure. I put
this design to the delegate targets through `tools/consult.sh`. Codex and
DeepSeek did not answer within 240 seconds; Kimi answered. Adopted from
Kimi: **dropping the category list** I had drafted ("such as its jobs,
tables, flags and alerts"), on the grounds that a list reads as a closed
class, misses the runbooks, config file and bucket in the planted set, and
aims "tables" at the columns the `explain-*` answers need; and **keeping the
prose-words bound rather than a total-words one**, since total words fall
the moment inline code goes and so cannot see a name traded for a phrase.
Not adopted: Kimi's exit "unless the answer needs them", for the reason
under **The edit**, and its trailing "describe them in plain terms
instead", which asks for the substitution the prose bound exists to catch.
The size requirement on the primary and the never-cut bound are mine.

## Pre-mortem, registered

The likeliest rejection is the third class, on bound 2: opus drops the
backticked names and keeps every mechanism they labelled, so "`purge_verify`
checks the night's results at 04:00 UTC" becomes "a verification job checks
each night's results", the primary passes and prose words rise. The second
likeliest is the second class: opus reads the names in the median answer as
part of what the parts are, keeps most of them, and the count falls by less
than a quarter, as round 132's length bullet moved it by an eighth. A third
class on bound 4 or on `explain-rollback` is possible if opus reads
`date_trunc` or `ledger_entries` as an internal name; `date_trunc` is a
Postgres function rather than the source's own name, so I expect it to
survive. The times and the batch cap are planted but are not names, so even
a clean edit leaves `relay-retention` near 3 rather than 0. A control that
stopped relaying would leave the primary nothing to move. I give the count
moving against the direction little weight.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#500]: https://github.com/JordanMPDS/laconic/issues/500
