# Round 107: check 3 asks about this message, not the conversation (#384)

**Registration. Nothing below the results line has been computed**, except the
single-turn figures quoted from round 106, which is merged. This file, the
three `carry-*` cases and their three `depend-*` bounds,
`evals/pilot/score_carry.py` and the layout tests are committed before any
generation. The edit and the regenerated
`rules/dist/*.md` are committed only if stage 1 fires, and before stage 2
generates.

`bash tools/candidate-due.sh` exited 0 at registration (round 106 carried a
candidate), and `bash tools/release-due.sh` exited 0. This round carries a
rule edit anyway, under **The edit** below, because the maintainer asked for
the next rule item in the backlog.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_carry.py --precheck $OUT/round-107-precheck.json
python3 evals/pilot/score_carry.py $OUT/round-107-{control,edit}.json \
    $OUT/round-107-{control,edit}-judgments.json
python3 evals/bench/release.py $OUT/round-107-{control,edit}.json
```

## Why this round exists

Every other open `rules` issue ends on a screen that no longer fires, so
[#384] is the backlog's only reproducing item. Rounds 105 and 106 took its
first suggested direction, and v0.3.6 ships it. This round takes the second.
The report's last paragraph, 24% of the answer, was a topic the user had
raised a turn earlier and did not ask about here. The model's own reasoning
flagged the paragraph under check 3 and kept it, because it was on topic for
the earlier turn. The issue's direction: *"Run check 3 against the current
question only. Being on-topic for something the user raised earlier is not
the same as being asked."*

No case in this repository can see that, because `choose-*` is single-turn.

## The instrument

Three two-turn pilot cases, `carry-{index,metric,rollback}`, over the `deep-*`
fixtures by symlink. Turn 1 asks for the fix. Turn 2 is `choose-*`'s either/or
about the cause, byte for byte without its opening clause, and only turn 2 is
graded, on `choose-*`'s trap.

| case | turn 1 | the topic turn 2 should not bring back |
|---|---|---|
| `carry-index` | is the index on the ticket the right fix? | the expression index, the range rewrite, the ticket's index |
| `carry-metric` | what should we do instead of shipping on this readout? | run to the sample size, or a higher-frequency proxy outcome |
| `carry-rollback` | what has to change so this can't happen again? | the action items: expand and contract, the release job, unknown modes |

`score_carry.CARRY` matches the fix by name per stem. On round 106's
single-turn `choose-*` answers it reads 0 of 80 on `index`, 0 of 80 on
`rollback`, and 16 of 80 on `metric`, where opus volunteers a correction of
the fixture's sample-size figure and mentions running to it. That baseline is
why stage 1 generates `choose-*` beside `carry-*`.

Check 1 already says the fix is left "for the user to ask for". In `carry-*`
the user has asked for it, one turn earlier, which is exactly the case the
issue describes.

`depend-*` is the bound on the other side: `carry-*`'s turn 1, then an
either/or that refers back to it, so a good answer has to use the earlier
turn.

| case | turn 2 | the record's answer |
|---|---|---|
| `depend-index` | would that index make it fast, or would the query still scan the table? | still scan: the ticket's index cannot serve the wrapped predicate |
| `depend-metric` | would two more weeks of traffic be enough, or would it still be too small? | still too small: about 1,850 a side against about 34,000 |
| `depend-rollback` | would the first action item alone have let the 14:21 revert work, or would checkouts still have failed? | it would have worked: either change alone was a short incident |

## Stage 1: does the carry fire on opus? (90 generation calls)

Master rules (v0.3.6), the laconic arm, opus, 10 reps per case,
`--turn-delivery plugin`, four shards:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
A='carry-index:opus,carry-metric:opus,carry-rollback:opus'
C='choose-index:opus,choose-metric:opus,choose-rollback:opus'
for cells in "$A" "$C"; do for off in 0 5; do
  python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $off \
    --cases-dir evals/pilot --cells "$cells" --turn-delivery plugin \
    --concurrency 4 --snapshot $OUT/round-107-precheck-${cells%%-*}-$off.json &
done; done
wait
python3 evals/bench/merge.py $OUT/round-107-precheck-*-{0,5}.json --out $OUT/round-107-precheck.json
python3 evals/pilot/score_carry.py --precheck $OUT/round-107-precheck.json
```

**Registered pass condition: at least 10 of the 30 `carry-*` turn-2 answers
carry turn 1's topic, at least 3 in every stem, and `carry-*` carries it more
often than `choose-*`, pooled one-sided Fisher, p < 0.05.** The last clause is
what makes the carry the earlier turn's: without it, a fix volunteered on the
single-turn question would buy a round about conversational scope.

**If it does not fire**, the edit is not committed, stage 2 is not generated,
this document records the precheck, and the round is recorded as measuring.

## The edit, committed only if stage 1 fires

Check 3, in the preamble every level carries:

```diff
-3. Is anything here something the user did not ask for?
+3. Is anything here something the current question did not ask for? Being
+   on topic for an earlier turn is not being asked.
```

`rules_cksum` is stamped into each snapshot at generation.

**Hypothesis.** Editing check 3 to ask what the current question did not ask
for should move the rate at which `carry-*` turn 2 carries turn 1's topic, opus,
down.

## Stage 2: the edit on opus, only if stage 1 fires (960 generation calls)

Two trees generating simultaneously: control from a worktree at this branch's
registration commit (master rules), edit from this branch with the edit
committed. Laconic, opus, `--turn-delivery plugin`: `carry-*` at 20 reps,
`depend-*` at 10, and the five-turn `deepsubset-*` and `deep-*` at 10, so 150
runs a side in two shards a side of 270 and 210 calls.

```sh
D='deep-index:opus,deep-metric:opus,deep-rollback:opus'
S='deepsubset-gateway:opus,deepsubset-ledger:opus,deepsubset-scheduler:opus'
P='depend-index:opus,depend-metric:opus,depend-rollback:opus'
for side in control edit; do for off in 0 10; do
  cells="$A,$P,$D"; [ $off = 10 ] && cells="$A,$S"
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$cells" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-107-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-107-$side-shard{0,10}.json --out $OUT/round-107-$side.json
python3 evals/bench/judge.py --results $OUT/round-107-$side.json --cases-dir evals/pilot \
    --out $OUT/round-107-$side-judgments.json
```

`deepsubset-*` carries rep keys 10 to 19 because it shares a shard's offset;
the keys are labels and nothing reads them as an order.

### The bars

1. **Primary: the carry rate on `carry-*` turn 2 falls**, opus, pooled over
   the three stems, one-sided Fisher, alpha 0.05.
2. **Falsifier, fatal: panel-judged pass rate may not fall** on `carry-*`,
   `depend-*`, `deepsubset-*` and `deep-*`, each pooled per family, one-sided
   Fisher, alpha 0.05. `depend-*` asks an either/or that refers back to turn
   1, so the primary cannot be bought by never mentioning an earlier turn.
   `deepsubset-*` ends in a narrowing follow-up ("what is left at
   the SPEC level to finish X?") whose answer is built from what earlier turns
   listed, and `deep-*` in a wrong-premise confirmation that needs the earlier
   diagnosis. They are where scoping check 3 to the current question could
   cost an answer the context it depends on.
3. **Bound, fatal: `date_trunc`** kept on `deep-index`'s graded turn.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** per-stem carry counts; `carry-*` turn-2
prose words; `panel_agreement.py`; `release.py`.

**Replication, bought only if everything above passes:** a fresh 150 runs a
side from the same two trees, scored on bars 1 to 3 at the same alphas. Then
step 9's holdout: all six reserved cases, opus, 10 reps, both trees; no
reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bars 2 and 3 to hold, twice, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/` before the merge.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**. v0.3.6 already tells
an either/or answer to leave its evidence out, and an answer that short may
have no room for a second topic; round 106's edit side put 16 of 60 at 20
words or fewer. If it fires, the likeliest failure is **bar 2 on
`depend-*`**: "the current question" read as licence to answer a question
about the earlier turn as if the earlier turn had not happened.

## What this round cannot establish

- **Opus only.** The edit ships to every model; sonnet and haiku have no runs
  on this instrument.
- **One kind of earlier topic.** Turn 1 asks for the fix in every stem, so
  the carried topic is one the user asked about. The report's was a second
  claim in a sentence asked about a turn earlier, raised rather than asked,
  and these fixtures have no sentence of that shape. Both reviewers below
  preferred that shape; the edit's wording covers both.
- **What the detector cannot tell apart.** `CARRY` matches the fix by name,
  so a passing mention and a carried paragraph count alike. The results
  quote what the matches are.

## Where the ideas came from

The edit is [#384]'s second suggested direction. Through `tools/consult.sh`,
Kimi supplied its final wording ("the current question", "an earlier turn"),
and Kimi and Codex both supplied the `depend-*` bound, Codex as a referent
carried from turn 1 and Kimi as a turn 2 that needs turn 1 to be answered.
Both also preferred a turn 1 that only raises the carried topic; that was not
taken, for the reason under **What this round cannot establish**. Codex's
alternative wording, which keeps earlier context "only when the current
question depends on it", was not taken: Kimi argued the carve-out belongs in
the bounds, and `depend-*` is that bound. DeepSeek did not answer within the
timeout.

[#384]: https://github.com/JordanMPDS/laconic/issues/384
[#388]: https://github.com/JordanMPDS/laconic/issues/388

## Results

<!-- Nothing above this line has been computed. -->

### Stage 1: it does not fire

60 runs, 0 failed, at master rules (`rules_cksum` 3105749900, v0.3.6), every
run on CLI 2.1.300, `cases_cksum` 3741594717 over the six cells.

| stem | `carry-*` carries turn 1's topic | median turn-2 words | `choose-*` carries it | median words |
|---|--:|--:|--:|--:|
| `index` | 0/10 | 3.0 | 0/10 | 41.0 |
| `metric` | 0/10 | 6.0 | 1/10 | 16.5 |
| `rollback` | 0/10 | 54.5 | 0/10 | 33.0 |

**0 of 30 against a fire line of 10.** The edit is not committed, stage 2 is
not bought, and the round is recorded as measuring.

On `index` and `metric`, turn 2 is the option and nothing else in all 20 runs:
"In the query itself." and "Because control had only four purchases." After
an earlier turn, the either/or answer is shorter than the single-turn one, not
longer.

**Disclosed, deciding nothing: on `rollback`, opus carries a different
earlier topic, its own.** Every turn-1 answer volunteers that the fixture's
migration cannot have run as written: `ALTER TABLE ... ADD COLUMN
settlement_currency char(3) NOT NULL` with no default fails on a table that
already has rows. In 9 of 10 `carry-rollback` turn-2 answers that objection
comes back, four of them flagged as such ("As I noted earlier, ..."), against
0 of 10 single-turn `choose-rollback` answers (one-sided Fisher p = 0.00006).
Nine of the ten attribute the `NOT NULL` column to the write-up ("according to
the report") rather than stating it, and one declines both options ("Neither
fits the evidence"). The objection is correct Postgres behaviour, so these turns carry
an earlier claim that bears on the answer's premise, which the never-cut
uncertainty item protects. It is not [#384]'s shape, a topic on which the
current question does not depend, and the registered detector does not count
it.

## Result: the precheck does not fire, and stage 2 was not bought

**Withdrawn unrun, `unscored`.** On opus at v0.3.6, an either/or asked after a
turn about the fix does not bring the fix back: 0 of 30. [#384]'s second
direction has no defect to move on this instrument, so no further edit on it
should be registered until a case shows a carried topic the current question
does not depend on. The instrument stays in `evals/pilot`.

The pre-mortem's first guess was right, and for the reason it gave: v0.3.6's
either/or answers are three to six words on two stems.

The `rollback` turns found something else. `deep-rollback`'s fixture states
an impossible migration, and opus says so whenever it is asked about the
remedy. Every case built on that fixture, including the scored `deep-rollback`,
`recall-rollback` and `wide-rollback`, grades against a record that a careful
reader disputes. That is [#388].
