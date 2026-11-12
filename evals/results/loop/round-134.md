# Round 134: an explanation of what you read says what happens, not which component does it (#500)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds. This file is committed first, with
`plugin/rules/laconic.md` at master, so the control worktree is that commit;
the edit and the regenerated `plugin/rules/dist/*.md` are committed after it.
Both commits precede any generation.

`bash tools/candidate-due.sh` exited 0 at registration: round 133 tested a
candidate, so this round could have measured. It carries one anyway, under
**The edit** below, because [#500] is still the only open rules issue whose
defect fires. `bash tools/release-due.sh` exited 0: v0.8.0, which ships round
132's bullet, is tagged and current.

Decided on **opus**: [#500] was observed on Opus 5.5 at level `full`.

## Why this round exists

[#500] reports a bare "explain `<stage A>` and `<stage B>`" asked right after
the model read about 125 lines of a design document. The answer relayed the
document, internal identifiers among it. The answer the user wanted held what
each stage is, what it must show to pass, and the one caveat that changes how
to read the second stage. It did not say which component does what.

[Round 133](round-133.md) appended "Leave out the source's internal names and
IDs that the question does not use: a name the user has not seen explains
nothing." to round 132's bullet. The planted identifiers relayed on
`relay-migration` and `relay-retention`/opus fell to factors of 0.342 and
0.384 of the control (p < 0.00001 both samples), and every panel bound held,
but prose words rose by a factor of 1.032 on the replication (one-sided
p = 0.025), a fatal bound. It was the rejection round 133's own pre-mortem
ranked first: the name went and the thing it named stayed, written out. The
replication's control says "`outbox-relay` then applies those rows to
orders-v2"; round 133's stage-2 median edit answer on the same cell says "a
relay worker copies that row". On `relay-retention` the names attached to an
action survived: "Support can undo the deletion with `acctctl restore` once
the user passes the `ID-RB-12` identity check".

So the name is the label and the description is the same claim without the
label. Leaving out one invites the other. This round names both, and says
what stays in their place: what happens.

## Fire rate: no precheck

Master's rules (`rules_cksum` 1859532872) have not moved since round 133,
whose two controls read a mean of 6.60 and 7.00 planted identifiers on
`relay-migration`/opus and 12.90 and 12.75 on `relay-retention`/opus, over
20 answers each, on CLI 2.1.319. The CLI is 2.1.321 at registration. A
precheck would buy calls to re-read that, so none is run; the round's own
control measures the defect on whatever release stage 2 runs on, and the
pre-mortem names a control that stopped relaying.

## The instrument

Round 133's, unchanged, with no code edited for this round: the three pilot
cases `evals/pilot/relay-{rollout,migration,retention}`, round 126's bounds
cells, `walkthrough`/opus at 20 runs a side, and `evals/pilot/score_relay.py`
with its seed (126), its `RELAY` lists, `MIN_FALL` (0.75), and its
`identifiers`, `longer`, `readability`, `nevercut`, `bounds` and `holdout`
commands. No pilot case or criterion has changed since round 133 ran.

The primary is `identifiers` again, not prose words. The question this round
asks is whether the names can go without a description taking their place,
and the bound that rejected round 133, `longer`, is the half of that question
round 133 failed. Keeping both exactly as registered makes the two rounds
comparable on both halves.

## The edit

Round 133's sentence is replaced, not carried. Appended to round 132's
bullet in `level: full`:

```diff
 - Explaining what you read gets at most 60 words for each part the question
-  names, plus at most one caveat that changes how to read it.
+  names, plus at most one caveat that changes how to read it. Leave out the
+  source's internal names and IDs that the question does not use, and any
+  description of what they name: say what happens, not which component
+  does it.
```

- "and any description of what they name" is the change. It closes the trade
  round 133 measured: `outbox-relay` and "a relay worker" are the same claim,
  and both go.
- "say what happens, not which component does it" says what stays, so the
  subtraction cannot take the content the trap grades with it. "Each write is
  also copied to orders-v2" is what happens; "`outbox-relay` copies each
  row" and "a relay worker copies each row" are which component does it.
  "Support can restore the account during the 30 days" is what happens; "with
  `acctctl restore` once the user passes `ID-RB-12`" is which component.
- "what happens" rather than "what each part does", so the positive clause
  asks for no more than the bullet already allows, and gives opus nothing new
  to elaborate.
- "that the question does not use" stays, round 133's exit, for round 133's
  reasons: a need-based exit hands opus [#500]'s own misreading, and
  `explain-rollback` asks for `PAYMENTS_SETTLEMENT_MODE` and migration `0042`
  by name.

The bullet stays at `full`, where [#500] was observed, and reaches `ultra` by
inheritance. The hook's `ultra` output measured 9,310 characters before the
edit, against the 9,500 budget `tests/test_laconic.sh` enforces.

## Hypothesis

> Appending "Leave out the source's internal names and IDs that the question
> does not use, and any description of what they name: say what happens, not
> which component does it." to round 132's bullet should move the mean count
> of planted identifiers relayed on `relay-migration` and `relay-retention`
> on opus **down**, to 0.75 of the control or less, without raising prose
> words on the three `relay-*`/opus cells, without lowering the panel pass
> rate on round 126's ten cells, without lowering the share of
> `relay-*`/opus answers free of readability violations, and without
> lowering the share of `explain-index`/opus and `walkthrough`/opus answers
> that carry their never-cut keywords.

## Stage 2: the edit on opus (280 calls, 220 opus)

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r134-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r134-edit` at the edit commit. Both
are on disk rather than under `/tmp`, which is memory on this machine. Two
shards a side, four `run.py` processes:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='relay-*:opus,walkthrough:opus'
B='relay-*:sonnet,explain-index:opus,explain-metric:opus,explain-rollback:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r134-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-134-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r134-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-134-$side-bounds.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-134-$side-{target,bounds}.json \
      --out $OUT/round-134-$side.json
done
python3 evals/bench/release.py $OUT/round-134-{control,edit}.json
python3 evals/pilot/score_relay.py identifiers $OUT/round-134-{control,edit}.json
python3 evals/pilot/score_relay.py longer $OUT/round-134-{control,edit}.json
python3 evals/pilot/score_relay.py readability $OUT/round-134-{control,edit}.json
python3 evals/pilot/score_relay.py nevercut $OUT/round-134-{control,edit}.json
```

**The primary and the three deterministic bounds are scored before any
judging is bought**: if any fails, the round rejects and nothing is judged.
If all pass:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-134-$side.json --out $OUT/round-134-$side-judgments.json
done
python3 evals/pilot/score_relay.py bounds $OUT/round-134-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-134-{control,edit}-judgments.json
```

### The bars

Round 133's, unchanged.

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
answers name `ledger_entries` and `chargeOrder`; how many `relay-retention`
answers mention the audit tombstone and the verification step, which its
trap lists under the hard purge and which this edit could strip as
"which component"; `release.py` and `panel_agreement.py`.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard, into `round-134-rep-*`), scored on the
same bars. **Then step 9's holdout:** all six reserved cases, sonnet and
opus, 5 reps, both trees, judged, scored with `score_relay.py holdout`: no
reserved case worse at one-sided p < 0.05. Round 133 rejected before its
holdout, so this is the third consultation of the five cases authored in
#566 and the second of `holdout-scratch`; all six are within their budgets.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md` and
`plugin/rules/dist/` are reverted before the merge.

## Origin

That the description replaces the name is round 133's own result, and its
pre-mortem's first-ranked rejection. I put a draft to the delegate targets
through `tools/consult.sh`: "Say what each part does, not which of the
source's components does it: a name the question does not use explains
nothing." Codex did not answer within 240 seconds and DeepSeek exited on an
unrecognised model id; Kimi answered. Adopted from Kimi: **keeping round
133's scope phrase "internal names and IDs"**, since "components" may read
as services and jobs and leave the flags, tables and runbook ids in place,
and **a purely subtractive clause naming the description**, which Kimi wrote
as "don't swap in a plain-words description of what they label either", on
the grounds that "say what each part does" asks for more description, which
is the bound round 133 failed. Kimi's named risk, that the subtraction strips
an outcome the trap grades, is why the positive clause stays, cut to "say what
happens, not which component does it" from my draft and from Kimi's own
suggested softening ("the outcome it produces still belongs in the answer").
Not adopted: Kimi's "a name the user hasn't seen explains nothing" reason
clause, for the character budget; the positive clause carries a test opus can
apply in its place.

## Pre-mortem, registered

The likeliest rejection is the third class on bound 2 again: "say what
happens" is still a description, and opus writes "each write is also copied
to orders-v2 in commit order" where the control wrote "`outbox-relay` then
applies those rows", so prose words rise by a few percent as they did in
round 133's replication. The second likeliest is the second class on
`relay-retention`: the times and the batch cap are planted but are not names,
and `acctctl restore` reads as what happens, so that cell stays near half its
control and the mean factor misses 0.75 if `relay-migration` does not go to
zero again. A third class on bound 5 is possible on `relay-retention`, if
opus drops the tombstone and the verification step as "which component" and a
panel reads the purge as under-explained; the disclosure counts them. I give
the count moving against the direction little weight, and a control that
stopped relaying would leave the primary nothing to move.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

[#500]: https://github.com/JordanMPDS/laconic/issues/500
