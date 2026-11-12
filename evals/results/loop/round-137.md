# Round 137: is #353 gone on CLI 2.1.321? (#353)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from rounds 86 to 109, which are merged, and the
`precheck.py` curve below, which reads no run. This file and the `reading`
command added to `evals/pilot/score_reminder.py` are committed before any
generation. Stage 1 is [round 99](round-99.md)'s precheck, command for
command, at today's master (`0efbcd0`) and the shipped reminder
(`reminder_cksum` 1027894636). What is new is how it is read: three ways,
with a reading that closes the issue.

`bash tools/candidate-due.sh` exited 0 at registration ([round 136](round-136.md)
carried a candidate), and `bash tools/release-due.sh` exited 0: v0.10.0 is
tagged and current. This round carries round 99's registered candidate for
[#353] under **The edit** below, behind the stage-1 precheck. If the precheck
does not fire, the edit is withdrawn unrun, this preamble gains the
disclaimer, and round 138 owes a candidate.

Decided on **sonnet**: #353 is a finding of the 2026-09-24 benchmark on
sonnet, and sonnet is where it fired at 45 of 105. Opus is generated and
disclosed.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_reminder.py reading \
  $OUT/round-137-precheck.json $OUT/round-137-precheck-judgments.json
python3 evals/bench/release.py $OUT/round-137-precheck.json
python3 evals/bench/panel_agreement.py $OUT/round-137-precheck-judgments.json
```

## Why this round exists

[#353] is a wrong-premise follow-up (*"so the fix is adding the index on
created_at, correct?"*) answered on sonnet with a bare "No" and its reason,
and no working fix. It arrived and left with a CLI release, and every reading
since it left is zero or one:

| round | CLI | sonnet index-family panel fails, shipped reminder |
|---|---|--:|
| [86](round-86.md), [87](round-87.md) | 2.1.282 | 45/105 |
| [88](round-88.md) | 2.1.285–2.1.286 | 0/45 |
| [99](round-99.md) | 2.1.287 | 0/60 |
| [109](round-109.md) | 2.1.301 | 1/60 |

Round 109's one fail named the working fix and missed the `date_trunc`
reason, so it is not #353's shape. Since round 109 the CLI has moved twenty
releases, to 2.1.321, and `plugin/rules/laconic.md` has moved through every
accept from round 111 to round 134 and #438's word fix. The issue has been
parked on "if a later screen fires" for seven weeks with no reading that
could close it, so the round's registration adds one.

The other parked issues ([#46], [#264], [#298]) are not read here. Round 138
owes a candidate if this one withdraws, and per [round 89](round-89.md) that
round runs its own precheck on its own issue's observed model.

## The edit

Round 99's arm F, unchanged, applied only if stage 1 fires: the reminder, in
its three copies (`plugin/hooks/laconic.sh`, `plugin/hooks/laconic.ps1`,
`evals/bench/run.py`'s `REMINDER`).

```diff
-LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.
+LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar.
```

## Stage 1 (about 400 calls)

Master rules and reminder, laconic arm, `--turn-delivery plugin`, two shards
at once, merged before judging so one panel pass and one reading cover both
models.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric'
for m in sonnet opus; do
  reps=$([ $m = sonnet ] && echo 20 || echo 5)
  cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
  python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
    --turn-delivery plugin --concurrency 2 \
    --snapshot $OUT/round-137-precheck-$m.json &
done
wait
python3 evals/bench/merge.py $OUT/round-137-precheck-{sonnet,opus}.json \
  --out $OUT/round-137-precheck.json
python3 evals/bench/judge.py --results $OUT/round-137-precheck.json \
  --out $OUT/round-137-precheck-judgments.json --jobs 2 \
  --cases recall-index,wide-index,deep-index,recall-metric
```

That is 100 generations and 100 panel verdicts at three calls each.

### The reading, registered

Over the 60 sonnet index-family verdicts (`recall-index`, `wide-index`,
`deep-index`, 20 each), counting only `pass` and `fail`:

- **FIRES at 10 fails or more.** Round 99's stage 2 is bought as that
  document registers it, its three bars and its replication, under the
  `round-137-` prefix.
- **GONE when the one-sided 95% Clopper-Pearson upper bound on the fail rate
  is under 0.083**, which at n = 60 is 0 or 1 fails. 0.083 is round 86's
  no-reminder arm, 5 of 60: the rate arm F was predicted to bring the cells
  down to, and the lowest any arm has read on the old CLI. A master whose
  rate is bounded below it leaves the edit nothing to remove. **#353 closes**,
  and arm F is retired with it.
- **OPEN otherwise**, 2 to 9 fails. #353 stays parked on a later screen, as
  it is today.

`recall-metric`, opus, and the graded-turn median words are disclosed and
decide nothing.

**Why the bar is 10 and not round 99's 12.** Round 99 chose 12 before
[#467] asked a precheck to state how often it fires, and it misses the pair
this round declares: 0.25 is the lowest rate the edit is worth a round at,
since round 99's stage 2 has power 0.67 against a control at 0.20 and 0.995
at 0.33, and 0.083 is the rate at which the defect counts as gone, for the
reason above.

```
$ python3 evals/bench/precheck.py --cells 20,20,20 --fire-at 0.25 --quiet-at 0.083 --rate 45/105
cells 20,20,20, 60 runs; the pair: P(fire) >= 0.9 at 0.25, <= 0.1 at 0.083
  bar       fire@0.25     quiet@0.083     at 0.428571    own rate
    9           0.979           0.058           1.000       0.555  meets the pair
   10           0.955           0.025           1.000       0.554  meets the pair
   11           0.914           0.010           1.000       0.552  meets the pair
   12           0.852           0.003           1.000       0.551
bars meeting the pair: 9 to 11 of 60
```

(Rows 0 to 8 and 13 to 60 cut here; the command prints them.) 10 is the
middle of the three bars that meet the pair. At 45 of 105, the benchmark's
own rate, every one of them fires surely.

**What GONE would not show.** The defect came with a release and left with
one, so a GONE is a reading of today's CLI and today's rules on the three
fixture stems that found it, not a guarantee it stays gone. It closes the
issue because the issue asks for a rule edit, and an edit needs a defect to
remove; a later benchmark that reads the shape again is a new report, with
its own instrument and its own precheck.

## Pre-mortem, registered

**I expect GONE.** Three screens across five weeks have read 1 of 165 on the
shipped reminder, and nothing merged since adds licence to drop a fix: the
accepts from round 111 on cut explanation length and findings lists, which
are not this shape. If it is not GONE, my guess is OPEN at 2 or 3 through
`wide-index`, on round 109's shape, a fix named and the `date_trunc` reason
missed, which the criterion fails and #353 does not describe. If it fires,
the likeliest rejection is round 99's: the primary moving with the
registered direction and not separating, because "Make fewer claims" may
carry the licence too.

## Origin

The design is round 99's precheck with a closing reading added, and the
closing reading is round 135's: close on a bound with a stated smallest rate
that matters, not on a bar failing to fire. Round 135 took that from Kimi
through `tools/consult.sh`. This round put the design above, in draft, to the
same targets, and nothing in it came from them: codex and deepseek did not
answer within 240 seconds, and kimi, asked again with 600, returned one
sentence of preamble and no answer.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#467]: https://github.com/JordanMPDS/laconic/issues/467

## Results

<!-- Nothing below this line was computed at the registration commit. -->
