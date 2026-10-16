# Round 109: do the parked `rules` issues fire on CLI 2.1.301? (#353, #116, #113, #46)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 91, 99 and 103, which are merged. This file is
committed before any generation. No harness or scorer changes: stage 1 is
[round 99](round-99.md)'s precheck and [round 91](round-91.md)'s screen,
command for command, at today's master.

**This round proposes no rule edit.** Its candidate was registered behind the
stage-1 precheck below, the precheck did not fire, and the edit was never
applied, so the round is recorded as measuring and round 110 has to carry a
candidate.

`bash tools/candidate-due.sh` exited 0 at registration ([round 108](round-108.md)
carried a candidate), and `bash tools/release-due.sh` exited 0. This round
carries round 99's registered candidate for [#353] under **The edit** below,
behind round 99's stage-1 precheck. If the precheck does not fire, the edit is
withdrawn unrun and the round is recorded as measuring, so round 110 owes a
candidate.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_reminder.py precheck \
  $OUT/round-109-precheck-sonnet.json $OUT/round-109-precheck-sonnet-judgments.json
python3 evals/pilot/score_fire.py $OUT/round-109-fire.json $OUT/round-109-edit-service.json
python3 evals/bench/release.py $OUT/round-109-*.json
```

## Why this round exists

[#384] closed with round 108. Every other open `rules` issue is parked on a
screen that read zero, and every one of those screens ran on CLI 2.1.285 to
2.1.288. The CLI is now 2.1.301, thirteen releases later. #353 is the reason
to re-read: its failure arrived and left with a CLI release (45 of 105 sonnet
index verdicts on 2.1.282, 0 of 105 on 2.1.285 to 2.1.287), so the release is
the variable most likely to bring it back.

| issue | last read | CLI | result |
|---|---|---|--:|
| [#353] | [round 99](round-99.md) | 2.1.287 | sonnet index fails 0/60 |
| [#116] | [round 91](round-91.md) | 2.1.287 | `conditional` edits 0/20 |
| [#113] | [round 91](round-91.md) | 2.1.287 | `edit-service` turn-3 offers 0/20 |
| [#46] | [round 103](round-103.md) | 2.1.288 | `session-alerting-long` over 600 words 0/40 |

[#298] and [#264] are not re-read. #298 waits for a new case, not a new
reading. #264's screen is round 90's 600-run sonnet design panel, which costs
more than the rest of this round together.

## The edit

Round 99's arm F, unchanged: the reminder, in its three copies
(`hooks/laconic.sh`, `hooks/laconic.ps1`, `evals/bench/run.py`'s `REMINDER`).

```diff
-LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.
+LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar.
```

## Stage 1 (about 540 calls)

Master rules (`rules_cksum` 4228464778) and the shipped reminder
(`reminder_cksum` 1027894636), laconic arm, two shards at a time, in two
phases to hold memory down.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
# phase 1: #353, round 99's precheck
CASES='recall-index wide-index deep-index recall-metric'
for m in sonnet opus; do
  reps=$([ $m = sonnet ] && echo 20 || echo 5)
  cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
  python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
    --turn-delivery plugin --concurrency 2 \
    --snapshot $OUT/round-109-precheck-$m.json &
done
wait
# phase 2: round 91's screens for #116, #113 and #46
python3 evals/bench/run.py --arms laconic --concurrency 2 --reps 20 \
  --cells 'conditional:opus,design-alerting:opus' --snapshot $OUT/round-109-fire.json &
python3 evals/bench/run.py --arms laconic --concurrency 2 --reps 20 \
  --cells 'edit-service:opus' --cases-dir evals/pilot --turn-delivery plugin \
  --snapshot $OUT/round-109-edit-service.json &
wait
# judging, #353 only, one side at a time
for m in sonnet opus; do
  python3 evals/bench/judge.py --results $OUT/round-109-precheck-$m.json \
    --out $OUT/round-109-precheck-$m-judgments.json --jobs 2 \
    --cases recall-index,wide-index,deep-index,recall-metric
done
```

**#353 fires at 12 or more of the 60 sonnet index-family verdicts**, round
99's registered line. Opus and `recall-metric` are disclosed and decide
nothing. If it fires, round 99's stage 2 is bought as that document registers
it, with its three bars and its replication, under the `round-109-` prefix.

**#116, #113 and #46 fire at round 91's lines:** `conditional` runs that edit a
file at 5 or more of 20, `edit-service` turn 3 carrying a closing offer at 3 or
more of 20, and `design-alerting` answers over 600 prose words at 2 or more of
20. These decide nothing in this round. They name the issue round 110 takes if
#353 does not fire, ranked by margin over threshold as round 91 ranks them.
`score_fire.py` also prints a row for #305, which is closed and has no runs
here, and its last line still says "round 92 takes"; both are read as round
110.

## Pre-mortem, registered

**I expect nothing to fire.** Every one of these screens has read zero for two
weeks or more, and none of the thirteen releases since has a reason attached
to it that would bring a failure back. If #353 fires, the likeliest rejection
is round 99's: the primary moves with the registered direction and does not
separate, because "Make fewer claims" may carry the licence too. If anything in
phase 2 fires, my guess is #113, because a closing offer is the kind of
habit a release changes without anyone meaning to.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#384]: https://github.com/JordanMPDS/laconic/issues/384

## Results

<!-- Nothing above this line has been computed. -->

## Result: nothing fires on CLI 2.1.301, and stage 2 was not bought

160 runs, 0 failed, every one on CLI 2.1.301 (`release.py`: one release, no
imbalanced arm), at the registered `rules_cksum` 4228464778 and
`reminder_cksum` 1027894636.

```
recall-index   0/20
wide-index     1/20
deep-index     0/20
sonnet index   1/60  fires at >= 12: does not fire
recall-metric  0/20  (disclosed)
sonnet index graded-turn median words 35.0
opus index     0/15  (opus, disclosed)

issue  counted                                     k/n   need margin median fires
#116   conditional runs that edited a file        0/20      5   0.00  103.5 no
#113   edit-service turn 3 closing offers         0/20      3   0.00  149.5 no
#46    design-alerting over 600 prose words       0/20      2   0.00  238.5 no
```

The panel decided all 80 sonnet verdicts with no three-way split; sonnet
agreed with the majority on 80, opus and kimi on 79 each.

**The one failure is not #353's.** #353 is a bare "No" with no working fix.
The failing `wide-index` answer names the fix and fails the criterion's other
clause, that the reason the btree goes unused is the `date_trunc` wrapper:

> No. By itself, an index on `created_at` changes nothing: the document built
> it on a restored copy of production and got a byte-identical plan. It only
> helps if the predicate is also rewritten to `created_at >= $1 AND created_at
> < $1 + interval '1 day'`. The document recommends pairing that rewrite with a
> composite `(tenant_id, created_at)` index, which brought the query to 29ms.

With rounds 88 and 99, sonnet's shipped-reminder index verdicts on CLI 2.1.285
to 2.1.301 read 1 of 165, against 45 of 105 on 2.1.282. Round 99's arm F stays
the registered candidate for #353, and its stage 2 can still be bought as
written if a later screen fires.

The three phase-2 screens read zero, as they did in rounds 91 and 103.
`edit-service` turn 3 carried no offer and `conditional` wrote no file in 20
runs each, and the longest `design-alerting` answer is 287 prose words
(median 238.5). The pre-mortem's first line held.

**Every open `rules` issue now reads zero on the current CLI**, or, for #298
and #264, waits on a condition this round did not test. Round 110 owes a
candidate. Since no instrument shows a defect, the next move is a case built
from a new report, not another edit on a screen that reads zero.
