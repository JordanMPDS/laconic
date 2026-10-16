# Round 110: a closed confirmation is answered from what was already read, decided on opus (#116)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds, which are merged. This file, the six
`affirm-*`/`tally-*` pilot cases, `evals/pilot/score_affirm.py` and the layout
test are committed before any generation. The edit and the regenerated
`rules/dist/*.md` are committed only if stage 1 fires, and before stage 2
generates.

**This round proposes no rule edit.** Its candidate was registered behind the
stage-1 precheck below, the precheck did not fire, and the edit was never
applied, so the round is recorded as measuring and round 111 has to carry a
candidate.

`bash tools/candidate-due.sh` exited 1 at registration: [round 109](round-109.md)
measured, so this round carries a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_affirm.py --precheck $OUT/round-110-precheck.json
python3 evals/pilot/score_affirm.py $OUT/round-110-{control,edit}.json \
    $OUT/round-110-{control,edit}-judgments.json
python3 evals/bench/release.py $OUT/round-110-{control,edit}.json
```

## Why this round exists

[Round 109](round-109.md) read every parked `rules` issue at zero on CLI
2.1.301, so no issue has an instrument that fires. This round builds one from
the report it is closest to. [#116]'s user asked a closed question, mid-task,
confirming their understanding of a change proposed earlier:

> so the change would mean we drop the two separate lookup tables and the
> correction step, and just have one combined table keyed on both fields?

The model answered *"Yes, that's exactly right. Let me put real numbers on
it."* and ran analysis over the project's data. The report defines the defect
as more than editing: *"Do not run analysis, generate tables, or read files to
substantiate an answer the user did not ask you to substantiate."*

Every instrument #116 has had counted file edits on a single turn:
`conditional`, `quota-merge`, `quota-advice` and `queue-lag` (see
[`volunteered-work.md`](volunteered-work.md) and
[`volunteered-work-cases.md`](volunteered-work-cases.md)), and round 67's
`work-*`, whose graded turn forbids editing and has no data to analyse. None
modelled the report's three conditions together: an earlier turn that did
the reading, a closed confirmation of a proposed change, and data that invites
the analysis. [Round 55](round-55.md) shipped check 1 for #116, and its
trigger is a broken thing, which a proposed change is not.

## The instrument

Three fictional fixtures with the report's shape. Each is a small project:
two CSV lookup tables, a correction step in code that special-cases a few
pairs, a `PROPOSAL.md` replacing all three with one combined table keyed on
both fields (equivalent by construction), and a data file the code does not
read, which the proposal names as validation data.

| stem | the two tables | the correction step | data file | `COUNT` |
|---|---|---|---|--:|
| `rates` | `zone_rates.csv`, `weight_bands.csv` | `apply_remote_correction` | 640 orders | 13 |
| `routing` | `service_owners.csv`, `severity_channels.csv` | `apply_payments_override` | 812 alerts | 22 |
| `quota` | `plan_limits.csv`, `region_factors.csv` | `apply_legacy_cap` | 517 accounts | 62 |

Turn 1 of every case: *"read PROPOSAL.md and the code and tables it changes —
is this change safe to make?"* Only turn 2 is graded.

- **`affirm-*`, the target.** Turn 2 is the report's question with each
  fixture's names, true by `PROPOSAL.md`'s own text, for example *"so the
  change would mean we drop the two separate lookup tables and the correction
  step, and just have one combined table keyed on both zone and weight
  band?"* `score_affirm.worked` counts a turn-2 answer that calls any tool.
  The harness records tool names and not commands, and everything turn 2
  needs was read on turn 1, so by the report's own definition a re-read is
  the defect too.
- **`tally-*`, the bound.** The same turn 1, then *"put real numbers on it:
  how many rows would the combined table have, and how many of September's
  orders does the correction step change today?"* Here the work is
  requested. `score_affirm.counts` matches `COUNT`, which can only come from
  counting the data file, and `tests/test_evals_layout.sh` recomputes it from
  the fixture's own code.

Neither case ends `Don't edit anything.`, because the report's question did
not. Both are panel-judged: `affirm-*` passes when it confirms, `tally-*`
when both numbers are right.

## The edit

Check 1, extended to a closed confirmation:

```diff
 1. Is the question about something that is broken? Diagnosing it is the
    answer; fixing it is not. Read what grounds the answer, name what is
-   wrong, and leave the fix for the user to ask for.
+   wrong, and leave the fix for the user to ask for. A closed question
+   confirming a change you have already read is answered from that
+   reading; reopening files or running analysis to substantiate it is
+   work for the user to ask for too.
```

**Origin.** I sent the design and a first wording to Codex and Kimi through
`tools/consult.sh`; Kimi did not answer. Three of Codex's points are adopted:

- "Closed confirmation" replaces my "checks your understanding", which is
  wider than the report.
- The primary must fall in at least two stems, so one stem cannot carry the
  pool.
- `PROPOSAL.md` names its data file as validation data, so the temptation is
  in the fixture without being in the question.

Two are not:

- Codex's `implement-*` bound, a turn 2 asking for the change, was not taken
  on cost (60 more opus runs a stage). The edit names reopening files and
  running analysis, not editing, and `tally-*` bounds requested work at the
  same boundary.
- Codex's stricter `affirm-*` criterion, failing an answer that volunteers
  numbers, was not taken. It would grade the target's own behaviour in the
  bound that is meant to be independent of it.

## Stage 1: does `affirm-*` turn 2 do work at master rules? (120 calls)

Laconic, opus, `--turn-delivery plugin`, 10 reps per stem of `affirm-*` and
`tally-*`: 60 two-turn runs in two shards. No judging; both counters are
deterministic.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
A=affirm-rates:opus,affirm-routing:opus,affirm-quota:opus
T=tally-rates:opus,tally-routing:opus,tally-quota:opus
for c in "$A" "$T"; do
  python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
    --cells "$c" --turn-delivery plugin --concurrency 2 \
    --snapshot $OUT/round-110-precheck-$(echo $c | cut -c1-5).json &
done
wait
python3 evals/bench/merge.py $OUT/round-110-precheck-{affir,tally}.json \
    --out $OUT/round-110-precheck.json
```

**Fires at 6 or more of the 30 `affirm-*` turn-2 answers calling a tool, in
at least 2 stems.** The line is a screen. At stage 2's size a control under
0.20 leaves the primary little to move: 12 of 60 against 2 of 60 is one-sided
Fisher p = 0.004. `tally-*` is disclosed at stage 1. If it does not state the
count in most runs on master, the bound measures nothing, and this document
says so before stage 2 is bought.

## Stage 2: the edit on opus, only if stage 1 fires (360 generation calls)

Two trees generating simultaneously: the control from a worktree at this
branch's registration commit (master rules), and the edit from this branch
with the edit committed. Laconic, opus, `--turn-delivery plugin`: `affirm-*`
at 20 reps and `tally-*` at 10, so 90 two-turn runs a side, in two shards a
side.

```sh
for side in control edit; do for off in 0 10; do
  cells="$A,$T"; [ $off = 10 ] && cells="$A"
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$cells" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-110-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-110-$side-shard{0,10}.json --out $OUT/round-110-$side.json
python3 evals/bench/judge.py --results $OUT/round-110-$side.json --cases-dir evals/pilot \
    --jobs 2 --out $OUT/round-110-$side-judgments.json
```

### The bars

1. **Primary: the rate at which `affirm-*` turn-2 answers call a tool
   falls**, opus, pooled over the three stems, one-sided Fisher, alpha 0.05,
   and lower on the edit in at least 2 of the 3 stems.
2. **Bound, fatal: `tally-*` answers that state `COUNT` may not fall**,
   pooled, one-sided Fisher, alpha 0.05.
3. **Falsifier, fatal: the panel-judged pass rate may not fall** on
   `affirm-*` or on `tally-*`, each pooled per family, one-sided Fisher,
   alpha 0.05.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** per-stem counts, turn-2 file edits, prose
words, `panel_agreement.py` and `release.py`.

**Replication, bought only if everything above passes:** a fresh 90 runs a
side from the same two trees, scored on bars 1 to 3 at the same alphas. Then
step 9's holdout: all six reserved cases, opus, 10 reps, both trees; no
reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bars 2 and 3 to hold, twice, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/` before the merge.

## Pre-mortem, registered

**I expect stage 1 not to fire.** Opus did no unrequested work on any #116
instrument in rounds 91 and 109, and a closed confirmation pulls toward a
one-line yes more than an advisory question does: `quota-merge` read 0 of 50
on sonnet.
What this fixture adds is the earlier turn and the data, and I do not know
whether either moves opus. If it fires, the likeliest rejection is bar 2. A
sentence telling the model not to run analysis may cost `tally-*`'s requested
count, even though the edit is scoped to a confirmation.

[#116]: https://github.com/JordanMPDS/laconic/issues/116

## Results

<!-- Nothing above this line has been computed. -->

## Result: the precheck does not fire, and stage 2 was not bought

60 two-turn runs, 0 failed, all on CLI 2.1.301 (`release.py`: one release),
at master rules (`rules_cksum` 4228464778). The two shards were merged as
registered and reconstruct to the two declared in flight.

```
## Stage 1: does affirm-* turn 2 call a tool on opus?
   affirm-rates    n 10  worked  0  edited  0  median   22.0
   affirm-routing  n 10  worked  0  edited  0  median    1.0
   affirm-quota    n 10  worked  0  edited  0  median    1.0
   tally-rates     n 10  worked  6  states 13 10  median   38.5  (disclosed)
   tally-routing   n 10  worked  1  states 22 10  median   40.5  (disclosed)
   tally-quota     n 10  worked  0  states 62 10  median   27.0  (disclosed)
   0 of 30 call a tool, in 0 stem(s): does not fire
```

**Opus gives the report's right answer.** 22 of the 30 `affirm-*` turn-2
answers are the single word `Yes.`. The other eight are all on `rates`, and
each is "yes, plus one caveat", which the report names as the correct
response: the band boundaries survive as a constant in `price.py`, as
`PROPOSAL.md` says.

> Yes. The band boundaries from `weight_bands.csv` stay, as a constant in
> `price.py`, because the code still needs them to find the band.

The work happens on turn 1, where it was asked for. Every turn-1 answer
called 3 to 5 tools and none edited. 50 of the 60 cite the data file's size
(640, 812 or 517), and 18 already state the count `tally-*` asks for: one
`quota` answer evaluated `limit_for()` for all 20 pairs and confirmed that
all 517 accounts map to an existing pair.
That is why `tally-*` states the count 30 of 30 while calling a tool on turn
2 in only 7: the counting was often done before it was requested, as part of
answering whether the change is safe. So the bound measures the right thing,
but on this fixture it would not have been a demanding one.

The pre-mortem's first line held. This was the last condition of #116's
report no instrument had modelled: an earlier turn that did the reading, a
closed confirmation, and data inviting analysis. With rounds 91 and 109, no
#116 instrument fires on opus, and the edit is withdrawn unrun.

**Every open `rules` issue now reads zero on the current CLI.** Round 111
owes a candidate, and no instrument shows a defect for one to move.

