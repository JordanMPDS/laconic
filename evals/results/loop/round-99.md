# Round 99: drop "Cut content, not words." from the per-turn reminder (#353)

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 83 to 88, which are merged. This file and
`evals/pilot/score_reminder.py` are committed before any generation. The edit
is registered here as text and is applied only if stage 1 fires, so stage 1
runs at master rules and the shipped reminder (`rules_cksum` 3660436060,
`reminder_cksum` 1027894636).

**This round proposes no rule edit.** Its candidate was registered behind the
stage-1 precheck below, the precheck did not fire, and the edit was never
applied, so the round is recorded as measuring and the next round has to carry
a candidate.

`bash tools/candidate-due.sh` exited 1 at registration: [round 98](round-98.md)
was the one measuring round the cap allows, so round 99 carries an edit, under
**The edit** below. `bash tools/release-due.sh` exited 0. If stage 1 does not
fire, the edit is withdrawn unrun, as rounds 89 and 92 withdrew theirs, and
this document says so in its results.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_reminder.py precheck \
  evals/snapshots/loop/round-99-precheck-sonnet.json \
  evals/snapshots/loop/round-99-precheck-sonnet-judgments.json
```

## Why this round exists, and why this issue

Every open `rules` issue has been read at master rules in the last week, and
none fired: [#305] was accepted in [round 97](round-97.md), [#46] did not fire
in [round 98](round-98.md), and [round 91](round-91.md) read #116, #113 and #46
at zero on opus. [#298] and [#264] did not fire in rounds 89 and 90. [#353] is
the one issue never read on the current CLI, 2.1.287:

| round | CLI | sonnet index-family fails, shipped reminder |
|---|---|--:|
| [86](round-86.md) | 2.1.282 | 25/60 (5/60 with no reminder) |
| [87](round-87.md) | 2.1.282 | 20/45 |
| [88](round-88.md) | 2.1.285–286 | 0/45 |

#353 is a sonnet report from the 2026-09-24 benchmark: a follow-up closed
question with a wrong premise (*"so the fix is adding the index on created_at,
correct?"*) answered with a bare "No" and its reason, and no fix that works.
Sonnet is the observed model and decides this round, per
[round 89](round-89.md). Round 86 located the cause in the one-line reminder
the plugin prepends to every later turn, not in `rules/laconic.md`.

## The edit

The reminder, in its three copies: `hooks/laconic.sh`, `hooks/laconic.ps1` and
`evals/bench/run.py`'s `REMINDER`, which `tests/test_bench.py` pins to the
hook. `tests/test_laconic.sh` and `tests/test_laconic.ps1` assert only on
"Make fewer claims and keep normal grammar", which stays.

```diff
-LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.
+LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar.
```

This is round 88's arm F. Round 88 could not score it on the failure, because
its control read 0, but did score its length: dropping the clause moved the six
guard cases +1.1 words (p = 0.33), while dropping "Make fewer claims" moved
them +13.2 (p = 1e-05). So "Cut content" carries no measured length control,
and it is the clause that literally tells the model to remove substance, which
a working fix is.

**Origin.** My first design put a sentence in `rules/laconic.md` after the
closed-question specimen. `tools/consult.sh` (deepseek; codex and kimi did not
answer) pointed out that this was [round 83](round-83.md)'s edit almost word
for word, rejected at 26 to 18 (p = 0.146), and that round 86 explains why: on
the graded turn the reminder, not the rules slice, is what the model has just
read. Deepseek proposed arm F as the candidate and the threshold reasoning
below; both are adopted.

## Stage 1: does #353 fire on CLI 2.1.287? (about 450 calls)

Master rules and reminder, laconic arm, `--turn-delivery plugin`. Two shards at
once, `--concurrency 2`.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric'
for m in sonnet opus; do
  reps=$([ $m = sonnet ] && echo 20 || echo 5)
  cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
  python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
    --turn-delivery plugin --concurrency 2 \
    --snapshot $OUT/round-99-precheck-$m.json &
done
wait
for m in sonnet opus; do
  python3 evals/bench/judge.py --results $OUT/round-99-precheck-$m.json \
    --out $OUT/round-99-precheck-$m-judgments.json \
    --cases recall-index,wide-index,deep-index,recall-metric
done
```

**Registered pass condition: at least 12 of the 60 sonnet index-family
verdicts fail.** That is a screen, not an effect size: at round 87's rate
(0.44) it fires almost surely, and at stage 2's size a control under 0.20 gives
the primary too little to move. Opus (5 reps a stem) and `recall-metric` are
disclosed and decide nothing.

## Stage 2: the edit, only if stage 1 fires (about 1,000 calls)

Two trees generating simultaneously, per [round 38](round-38.md): the control
from a worktree at master, the edit from this branch with the reminder changed
in all three copies. Sonnet: the three index stems at 30 reps,
`recall-metric` and the six guards (`recall-rollback`, `wide-rollback`,
`wide-metric`, `deep-rollback`, `deep-metric`, `drift-service`) at 15. Opus:
all ten at 3. Judged by the panel on the index stems and `recall-metric` only.

```sh
python3 evals/pilot/score_reminder.py compare \
  $OUT/round-99-control.json $OUT/round-99-control-judgments.json \
  $OUT/round-99-edit.json $OUT/round-99-edit-judgments.json
python3 evals/bench/release.py $OUT/round-99-{control,edit}*.json
```

Each side's sonnet and opus shards are merged with `evals/bench/merge.py`
before scoring.

1. **Primary.** Sonnet index-family panel fails, edit below control, one-sided
   Fisher, alpha 0.05. Simulated power at 90 a side against an edit at round
   86's no-reminder rate (0.083): 0.67 if the control reads 0.20, 0.995 at
   0.33.
2. **Bound, fatal: guard-case graded-turn words must not rise.**
   `score_settled.stratified` over the six guards on sonnet and opus, twelve
   cells, one-sided, alpha 0.05, seed 99.
3. **Bound, fatal: `recall-metric` fails must not rise** on sonnet, one-sided
   Fisher, alpha 0.05.

`settled-*` is not a bound: it is single-turn, and the reminder never reaches
turn 1. Disclosed, deciding nothing: per-stem cells, opus fails,
`panel_agreement.py`, `release.py`.

**Accept** needs bar 1 to pass and bars 2 and 3 to hold, then step 8's
replication at the same size. Anything else rejects and the reminder stays.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**: round 88 read 0 of
45 two releases ago, and nothing since suggests the failure came back. If it
fires, the likeliest rejection is the primary moving with the registered
direction and not separating, as round 87's rewrite did (20 to 14): "Make
fewer claims" may be part of the licence too, and only the no-reminder arm has
ever reached 5 in 60.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#353]: https://github.com/JordanMPDS/laconic/issues/353

## Results

<!-- Nothing above this line has been computed. -->

## Result: #353 does not fire on CLI 2.1.287, and stage 2 was not bought

100 runs, 0 failed, all on CLI 2.1.287 (`release.py`: one release), master
rules `rules_cksum` 3660436060 and the shipped reminder, `reminder_cksum`
1027894636. The registration first named `rules_cksum` 288018845, master's
checksum before round 97's accept; it was corrected to the stamped value with
this result, and nothing in the design depended on it.

```
recall-index   0/20
wide-index     0/20
deep-index     0/20
sonnet index   0/60  fires at >= 12: does not fire
recall-metric  0/20  (disclosed)
sonnet index graded-turn median words 44.0
opus index     0/15  (opus, disclosed)
```

The panel agreed on all 80 sonnet verdicts. Every sonnet graded turn denies
the bare index and names a working fix, in a median of 37.5 words on
`recall-index` (25 to 49), the stem that failed 12 of 15 in round 87:

> No. An index on bare `created_at` cannot serve a predicate on
> `date_trunc('day', created_at)`, so the plan would not change. Rewrite the
> predicate to a range on `created_at` and index `(tenant_id, created_at)`.

With round 88 that is 0 of 105 sonnet index verdicts on the shipped reminder
across CLI 2.1.285 to 2.1.287, against 45 of 105 on 2.1.282 in rounds 86 and 87.
The failure left with a CLI release and has not come back, so the edit was
withdrawn unrun as the pre-mortem expected, and round 100 owes a candidate on
another issue.

Arm F stays the registered candidate for #353: if a later screen fires, this
document's stage 2 can be bought as written.

