# Round 127: the metric family on the corrected record (#583)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and the detector's archive check
below, which reads stored runs and buys no call. This file and
`evals/pilot/score_record.py` are committed before any generation. No
harness, rule or case file changes in this round.

**This round proposes no rule edit.** It measures whether a fixture
correction moved the numbers earlier rounds read off these cases.

`bash tools/candidate-due.sh` exited 0 at registration: round 126 tested a
rule candidate, so this round may measure, and round 128 owes one.
`bash tools/release-due.sh` exited 0: v0.6.0 is tagged and current.

Decided on **opus**, the model rounds 80 to 126 have decided on and the one
round 100 read #298 on.

## Why this round exists

[#582] corrected `evals/cases/deep-metric/fixture/ANALYSIS.md`, which every
`*-metric` pilot reads by symlink. The record said detecting the 0.3-point
difference at 80% power "needs roughly 34,000 sessions per arm"; its own rates
give roughly 10,000, and that is what it says now. Turn 3 of `deep-`,
`register-` and `fullexplain-metric` asks "walk me through how the
10,000-sessions-per-arm figure is arrived at" (34,000 before). On the old
record nearly every turn-3 answer recomputed the figure and said the record
was wrong, and that dispute was then the model's own context for turns 4 and
5. [#582] also corrected `wide-index`'s FINDINGS.md: 15.7 million heap
"pages" became rows, and a 340-byte payload median became 140.

Turn 5 is what earlier rounds read. [Round 67](round-67.md) read its length on
`deep-` against `work-metric` for [#136]; [round 100](round-100.md) read the
told/cold ratio, `fullexplain-*` turn 5 against `explain-*` asked cold, for
[#298], and parked #298 because opus's told answer was 0.377 of the cold one.
Neither round's reading has been measured on a record that does not invite a
dispute. [#583] asks whether the correction moves the graded turns' length or
verdicts.

## Design

**Two records, one harness, generated at once.** The issue proposed setting a
fresh new-record batch beside the last old-record figures. That comparison
spans five weeks and about thirty CLI releases on cells this project has
measured drifting several-fold at byte-identical rules ([round 37](round-37.md)),
so the old record is regenerated beside the new one instead. The old side's
case directories are exported from `3702bb5`, the commit before [#582], with
`git archive`, and run by master's harness through `--cases-dir`; the new side
is master's own `evals/pilot` and `evals/cases`. Same rules, same harness
code, same CLI window, so the only difference between the sides is the case
text [#582] changed. Running one harness over two case directories, rather
than one harness per worktree, is Kimi's (below).

Laconic arm, level `full`, opus, `--turn-delivery plugin`, 10 reps per cell
per side:

| cell | turns | graded | what changed in its record |
|---|--:|---|---|
| `deep-metric` | 5 | turn 5 | ANALYSIS.md; turn-3 question |
| `register-metric` | 5 | turn 5 | ANALYSIS.md; turn-3 question |
| `fullexplain-metric` | 5 | turn 5 | ANALYSIS.md; turn-3 question |
| `explain-metric` | 1 | turn 1 | ANALYSIS.md only, in two figures it does not ask about |
| `wide-index` | 2 | turn 2 | FINDINGS.md: pages to rows, 340 to 140 bytes |

That is 50 runs and 180 generation calls a side, 360 in all, and about 300
panel calls to grade the 100 graded turns. Each side runs as two shards split
at rep 5, each shard running the four pilot cells and then `wide-index`, so
four `run.py` processes run at once, inside [#255]'s ceiling, all declaring
`--concurrency 4`.

```sh
OUT=evals/snapshots/loop
OLD=/tmp/laconic-r127-oldrecord
mkdir -p $OLD && git archive 3702bb5 evals/cases/deep-metric evals/cases/wide-index \
    evals/pilot/deep-metric evals/pilot/register-metric evals/pilot/fullexplain-metric \
    evals/pilot/explain-metric | tar -x -C $OLD
P='deep-metric:opus,register-metric:opus,fullexplain-metric:opus,explain-metric:opus'
for side in old new; do
  root=$([ $side = old ] && echo $OLD/evals || echo evals)
  for off in 0 5; do
    ( python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $off \
        --cases-dir $root/pilot --cells $P --turn-delivery plugin --concurrency 4 \
        --snapshot $OUT/round-127-$side-p$off.json &&
      python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $off \
        --cases-dir $root/cases --cells wide-index:opus --turn-delivery plugin \
        --concurrency 4 --snapshot $OUT/round-127-$side-w$off.json ) &
  done
done
wait
for side in old new; do
  python3 evals/bench/merge.py $OUT/round-127-$side-p{0,5}.json --out $OUT/round-127-$side.json
  python3 evals/bench/merge.py $OUT/round-127-$side-w{0,5}.json --out $OUT/round-127-$side-wide.json
done
python3 evals/bench/release.py $OUT/round-127-{old,new}.json
python3 evals/bench/release.py $OUT/round-127-{old,new}-wide.json
# each side graded against its own record's criteria
python3 evals/bench/judge.py --judge-all --cases-dir $OLD/evals/pilot --results $OUT/round-127-old.json --out $OUT/round-127-old-judgments.json
python3 evals/bench/judge.py --judge-all --cases-dir evals/pilot --results $OUT/round-127-new.json --out $OUT/round-127-new-judgments.json
python3 evals/bench/judge.py --judge-all --cases-dir $OLD/evals/cases --results $OUT/round-127-old-wide.json --out $OUT/round-127-old-wide-judgments.json
python3 evals/bench/judge.py --judge-all --cases-dir evals/cases --results $OUT/round-127-new-wide.json --out $OUT/round-127-new-wide-judgments.json
```

Each side is graded against its own record's `expect.json`, because a
criterion states fixture facts and [#582] changed the facts several criteria
state.

## The dispute detector, frozen here

`score_record.charges(text, figure)` returns the sentences of a turn-3
answer that charge the record's figure with being wrong. A sentence counts
when it names the figure or the record ("the document", "ANALYSIS.md", "the
author", "the figure") and carries a cue: a negated reach, reproduce, match,
produce or follow ("I can't reproduce that number", "none of them gives
34,000"); a different figure set against the record's ("about 9,600 per arm,
not 34,000"); or a charge word (too high, overstated, discrepancy, error,
wrong, mistake, contradicts, falls short, only if). Two kinds of sentence are
excluded by construction: the vocabulary of a power calculation (standard
error, type II error, error rate) and of turn 5 (the wrong metric), and a
statement that the record shows no derivation ("so I can't retrace its
steps"), because the corrected record shows none either and an answer can say
so while agreeing with it. The same code reads both sides; only the figure
differs, 34,000 on the old side and 10,000 on the new.

Checked against the stored old-record turn-3 answers before registration,
deduplicated by session, beside the count #469 used, which was "recomputes
the figure to 9,000-12,999 or says it falls short of 34,000":

```
$ python3 evals/pilot/score_record.py --archive <every snapshot holding those cases>
arm              model        n       #469    charges   both
laconic          haiku       50         27         20     20
laconic          opus       302        302        273    273
laconic          sonnet     625        622        562    561
all                        1112       1071        961    960
```

On laconic/opus the detector finds a charge in 273 of 302 old-record answers
(90%), where #469's count found a recomputation in all 302; the 29 it misses,
read in a sample, recompute without a sentence the cues reach, or only say
the derivation is missing. It is tuned only on old-record text, so its false
positives on the new record are unmeasured: **every flagged new-record answer
is printed with the sentences that flagged it, and read**, and any the reading
overturns is listed by rep in the results.

## Endpoints, one look

1. **Manipulation check.** Turn-3 answers carrying a charge, pooled over the
   three five-turn cells, old against new, two-sided Fisher. It has worked
   when the old side reads at least 70% and the new side at most 10% after
   the hand read. 0 of 30 bounds the new rate under about 10% at 95%.
2. **Primary: graded-turn prose words**, `metrics.score` words, pooled over
   the three five-turn cells: the geometric ratio new over old as the mean
   over cells of the difference in mean log words, the record label permuted
   inside each cell (two-sided, seed 127), and a within-cell bootstrap 90%
   interval. Read as an equivalence test against a 0.80 to 1.25 margin, as
   Kimi suggested: a 90% interval inside the margin is the two one-sided tests
   at 0.05 each. Opus's graded-turn log spread in the archive is 0.16 to 0.25
   per cell, which at 30 a side puts the interval about ±9% wide around a null
   effect. Each cell and the all-cells pool are printed beside it, deciding
   nothing.
3. **Panel verdicts on the graded turn**, pass over decided, per cell and
   pooled over all five, two-sided Fisher.
4. **Told/cold ratio** on each side, `fullexplain-metric` turn 5 over
   `explain-metric`, by `score_reexplain.py --told fullexplain` with old as its
   control and new as its edit, so its interaction line is the correction's
   effect on the told answer net of its effect on the cold one. `explain-metric`
   is a near-placebo, Kimi's point: its record changed only in two figures its
   question does not ask about.

Disclosed, deciding nothing: turn-3 prose words, which the dispute should have
been lengthening; `wide-index` turn-1 answers that put 15.7 million in pages;
`panel_agreement.py`; `release.py` on both pairs.

## Readings, registered

- **The manipulation check fails** (new side above 10% after the hand read):
  the corrected record still invites a dispute, and an issue is filed with the
  sentences. Endpoints 2 to 4 are still reported, but read as a weaker
  manipulation.
- **Endpoint 2's interval sits inside 0.80 to 1.25 and endpoint 3 does not
  separate:** the dispute did not move the graded turn by a fifth either way
  on opus, so rounds 67 and 100 stand as measured, and #583 closes with that
  bound.
- **Endpoint 2 separates at p < 0.05 with its interval outside the margin, or
  endpoint 3 separates:** the dispute was part of what those rounds measured.
  Round 67's and round 100's documents get a dated correction note naming the
  factor, and the LEDGER rows say so.
- **Neither**: unresolved at this size, reported as such, and #583 stays open
  with the reps a second look would need.
- **Endpoint 4's new-side told/cold ratio exceeds 1:** #298's parking
  condition ("a told answer longer than its cold one") is met on the corrected
  record, and #298 gets a comment saying so. At or under 1, round 100's
  parking stands.

## Where the ideas came from

`bash tools/consult.sh` was asked about this design twice; Codex and DeepSeek
timed out both times. Kimi contributed three things this round adopts: one
harness over two case directories instead of a worktree per side, checking the
dispute detector against the stored old-record answers before freezing it,
and stating the length null as an equivalence bound with `explain-metric` read
as a near-placebo. Its suggestion to extract each answer's own per-arm figure
numerically was not adopted: a power calculation's working carries a dozen
intermediate figures and both arms' total, so a numeric rule needs the
sentence cues anyway.

## What this round cannot establish

- It reads opus only. Round 67 read sonnet; whether the correction moves
  sonnet's turn 5 is not measured here, and round 67's note, if one is owed,
  says it was owed on opus.
- `work-metric`, `deepexplain-metric` and the other pilots that read the same
  record are not regenerated. A result here is a reason to re-read them, not
  a reading of them.
- The detector's new-record precision rests on the hand read of what it flags,
  and its old-record recall on laconic/opus is 90%, not 100%.

## Results

100 runs, 0 failed, all on CLI 2.1.319, generated 21:45 to 22:42 UTC on
2026-11-08: 50 a side, the two sides inside the same hour. `release.py`
reports no span and no imbalance on either pair. The first launch was
stopped by the wrapper around it after about nine minutes; the 16 runs it
had finished were kept and the four shards resumed by key, so the sessions in
flight at the stop were spent without a record. Both sides carry
`rules_cksum` 2442620433; `cases_cksum` is 2123160817 and 747730386 on the old
record, 2652659225 and 1828772765 on the new.

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_record.py "$OUT/round-127-old.json+$OUT/round-127-old-wide.json" \
    "$OUT/round-127-new.json+$OUT/round-127-new-wide.json" \
    --judgments "$OUT/round-127-old-judgments.json+$OUT/round-127-old-wide-judgments.json" \
                "$OUT/round-127-new-judgments.json+$OUT/round-127-new-wide-judgments.json"
python3 evals/pilot/score_reexplain.py --told fullexplain $OUT/round-127-{old,new}.json 127
```

### 1. The manipulation worked

| turn-3 answers with a charge | old record | new record | Fisher p |
|---|--:|--:|--:|
| `deep-metric` | 8 / 10 | 0 / 10 | 0.0007 |
| `register-metric` | 8 / 10 | 0 / 10 | 0.0007 |
| `fullexplain-metric` | 8 / 10 | 1 / 10 | 0.0055 |
| pooled | **24 / 30** | **1 / 30** | < 0.0001 |

The hand read overturns the one new-record flag. `fullexplain-metric` rep 1
says "The result is about 9,600 sessions per arm, which the document rounds
to 'roughly 10,000'", which agrees with the record; the cue that fired is
"no ... gives", reached through "the no-effect assumption, gives about
9,600". So the new record reads **0 of 30** after the hand read and the old
record 24 of 30, past both registered bars.

The detector undercounts the old side, which is the conservative direction.
The six old-record answers it does not flag all recompute the figure to
about 9,600 to 10,200, and at least four of them say in words the cues do not
reach that the record's figure is wrong ("doesn't come out at 34,000", "34,000
per arm matches a difference of about 0.15 points, half the observed one").
On the old record every turn-3 answer, 30 of 30, recomputed the figure.

### 2. Primary: the graded turn did not move

| graded-turn prose words, median | old record | new record | ratio | p |
|---|--:|--:|--:|--:|
| `deep-metric` turn 5 | 44.5 | 44.5 | 1.000 | 0.4337 |
| `register-metric` turn 5 | 50.0 | 46.5 | 0.930 | 1.0000 |
| `fullexplain-metric` turn 5 | 33.5 | 32.0 | 0.955 | 0.8144 |
| `explain-metric` turn 1 | 72.0 | 79.5 | 1.104 | 0.3185 |
| `wide-index` turn 2 | 51.0 | 46.5 | 0.912 | 0.1582 |

Pooled over the three five-turn cells, the geometric ratio new over old is
**1.006, 90% interval [0.928, 1.092], p = 0.9129**, inside the 0.80 to 1.25
margin. Over all five cells it is 0.995, [0.921, 1.074], p = 0.9150. On
opus, a turn 3 that disputed the record did not change how long turn 5 ran
by more than about 8% either way.

Turn 3 itself did not move either, which the registration expected it to:
pooled ratio 0.979, [0.914, 1.050], p = 0.6192 (`deep-metric` 129.0 to
121.0, `register-metric` 242.5 to 211.5, `fullexplain-metric` 227.5 to
239.0). Opus spent about as many words confirming the corrected figure as it
had spent refuting the wrong one.

### 3. Verdicts did not separate

| graded turn, panel pass / decided | old record | new record | Fisher p |
|---|--:|--:|--:|
| `deep-metric` | 10 / 10 | 10 / 10 | 1.0000 |
| `register-metric` | 8 / 10 | 10 / 10 | 0.4737 |
| `fullexplain-metric` | 10 / 10 | 10 / 10 | 1.0000 |
| `explain-metric` | 10 / 10 | 10 / 10 | 1.0000 |
| `wide-index` | 10 / 10 | 10 / 10 | 1.0000 |
| pooled | 48 / 50 | 50 / 50 | 0.4949 |

Both old-record fails trace to the record, and only one of them to the figure
#582 corrected. In `register-metric` rep 7 the answer, carrying its own
turn-3 recomputation, ends "With roughly 10,000 sessions per arm, either
metric would be usable", and all three judges failed it, the majority reason
citing "well below the 34,000 needed": the old criterion states the wrong
figure as the fixture's fact, so a correct answer was graded against it. In
rep 3 the answer disputes a different claim in ANALYSIS.md, that lift cannot
carry an interval, and opus and sonnet failed it for treating lift as usable.
Two fails in 50 do not separate, so this is disclosed and decides nothing.

`panel_agreement.py`: every record decided, no three-way split, kimi cast no
vote on one new-record judgment, so sonnet and opus decided it. Agreement
with the majority is 39 or 40 of 40 per member on both pilot files, and opus
dissented on 2 of 10 new-record `wide-index` answers.

### 4. Told/cold stays under 1 on both records

| | `fullexplain-metric` (told) | `explain-metric` (cold) | told/cold |
|---|--:|--:|--:|
| old record | 33.5 | 72.0 | **0.465** (p = 0.0004) |
| new record | 32.0 | 79.5 | **0.403** |

The correction's effect on the told answer net of its effect on the cold
one is a ratio of ratios of 0.848, p = 0.3428, and 0.3318 under #298's
corrected null. Round 100 read 0.377 on opus pooled over three stems; on the
metric stem alone the told answer is under half the cold one on either
record.

Disclosed: no `wide-index` turn-1 answer on either side repeats 15.7 million
as pages (0 of 10 each), so that half of #582 changed nothing a turn-1 answer
said.

## Result: the corrected record moves nothing the earlier rounds read

The second registered reading obtains. The dispute was real and is gone, 24
of 30 against 0 of 30, and with it gone the graded turn's length sits within
about 8% of the old record's on opus, inside the registered margin, while
verdicts do not separate. So [round 100](round-100.md), which read opus,
stands as measured and takes no correction. [Round 67](round-67.md) read
sonnet, which this round did not regenerate: opus's null is a reason to
expect none there, not a reading of it, and its document takes no note on
that basis alone. #583 closes with the bound. #298's parking also stands, because the told
answer stays under half the cold one on the corrected record. Round 128
owes a rule candidate.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#582]: https://github.com/JordanMPDS/laconic/pull/582
[#583]: https://github.com/JordanMPDS/laconic/issues/583
