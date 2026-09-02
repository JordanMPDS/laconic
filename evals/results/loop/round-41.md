# Round 41: is the turn-2 collapse a defect? A judged round on faithful delivery

**Status: registered. Everything above the results heading was written and
committed before a single judgment was bought.** This round buys no generations
at all in its first stage, so the pre-registration is doing more work than usual
and is worth reading carefully.

## The question, from [#196]

Round 40's control side established that under `--turn-delivery plugin` — the
shipped hook wiring — the answer length **descends** with conversational depth:
pooled sonnet medians of 88.5 words at turn 1, 17 at turn 2 and 27 at turn 5.
Turn 1 is identical under `repeat` delivery (p = 0.576), so the difference is
delivery rather than era. See [`round-40.md`](round-40.md).

Seventeen words on turn 2 against 88.5 on turn 1 is one of two things, and a
token count cannot tell them apart:

- **Correct terseness.** The subject is established by turn 2, so most of the
  first answer's content would be restatement, and laconic is supposed to cut
  restatement.
- **Under-delivery.** The model lost the rule slice, kept only the one-line
  reminder, and answered thinly — dropping content the question actually
  required.

Round 40 bought no judgments. Its target was `output_tokens` and it stopped at
the first failing step per the standing buying order, so no verdict exists on
any of its 220 runs.

## Why this round is judgments only

The runs already exist. `round-40-control.json` is exactly the batch [#196] asks
for: 11 cells at 10 reps, sonnet, laconic arm, `--turn-delivery plugin`, master
rules (`rules_cksum` 136269960), `cases_cksum` 1866701119, generated
2026-09-02 02:24 to 03:19 UTC with `--concurrency 2` declared, 0 failures. The
`confirm-*` twins are in that same batch, which is the thing [#196] requires and
the thing round 39's pilot lacked.

So the measurement this round needs is a grading of text that has already been
generated, and generating a second identical batch to grade would buy nothing
the first one does not already carry.

**The pre-registration is weaker here than in a normal round, and this is where
it is weak.** The token medians of these runs are published in `round-40.md`, so
the scope is not being chosen in ignorance of *everything* about the batch. Two
things limit the damage. The cells are taken verbatim from [#196], which was
written and filed before this round began and names `recall-*`, `deep-*` and the
`confirm-*` twins. And the quantity being registered — a verdict — does not
exist yet in any form for any of these 220 runs.

## The design: one question asked at three depths

The three families share a fixture, a final question and a trap, and differ only
in how many turns precede the graded question:

| family | turns | graded question |
| --- | ---: | --- |
| `confirm-index` / `confirm-metric` / `confirm-rollback` | 1 | the trap question, cold |
| `recall-index` / `recall-metric` / `recall-rollback` | 2 | the same question, after one prior answer |
| `deep-index` / `deep-metric` / `deep-rollback` | 5 | the same question, after four prior answers |

`recall-metric`'s turn 2 and `deep-metric`'s turn 5 are byte-identical to
`confirm-metric`'s only turn: *you concluded lift is the wrong metric for this
experiment, correct? Don't edit anything.* All three grade against the same
`trap` string in `expect.json`. That is what makes depth the only variable.

`cold-service` (1 turn) and `drift-service` (5 turns) are a fourth pair on a
different fixture, with no turn-2 member. They are judged too, and reported
separately, because they carry the depth contrast on material the other three
families do not share.

## The registered hypothesis

> Under `plugin` delivery at master rules, the quality pass rate on the
> identical final question does not fall with conversational depth: the pooled
> `recall-*` (turn 2) and `deep-*` (turn 5) pass rates are indistinguishable
> from the pooled `confirm-*` (turn 1) rate.

**Primary metric: pass rate over all usable runs**, `pass / n`, pooled across
the three families within each depth. A `not_exercised` counts as not-a-pass,
deliberately: an answer so thin that the trap never fires is precisely the
under-delivery this round is looking for, and folding it in with passes would
hide it. The `fail` and `not_exercised` counts are reported separately at every
depth, because a `not_exercised` at turn 5 means something different from one at
turn 1.

**Test:** two-sided Fisher exact on (pass, not-pass), turn 1 against turn 2 and
turn 1 against turn 5, using `evals/bench/subagent.py`'s `fisher_exact`. Alpha
0.05 per comparison. Two comparisons are made, so the family-wise rate is about
0.10, and both p values are reported whichever way they land.

**The falsifier, registered here:** if either later-turn pooled pass rate is
*below* the turn-1 rate at p < 0.05, the collapse is an under-delivery. That
would make it a defect in `hooks/laconic.sh`'s reminder line rather than in
`rules/laconic.md` — the first result in this repository pointing at the hook.

If neither comparison fires, the collapse is the plugin working as intended, the
multi-turn length question closes, and [#196] closes with it.

## What is bought, in order

1. **`round-40-control.json`, judged.** 110 judgments, master rules. This is the
   primary and it settles the absolute question.
2. **`round-40-edit.json`, judged.** 110 judgments. Pre-committed **whichever way
   stage 1 lands**, so there is no stopping rule to exploit. It is an independent
   second batch of the same cells at the same delivery in the same hour, and it
   replicates the *depth* contrast rather than the shipped configuration: its
   `rules_cksum` is 1135334847, round 40's rejected third pre-send check. A null
   at stage 1 needs the extra n; a hit at stage 1 would change shipped code and
   needs the replication more.
3. **A matched `repeat` batch, conditional on a hit at stage 1 or 2.** Registered
   now with its command, so the scope cannot be chosen later:

   ```sh
   python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
     --cases 'confirm-*,recall-*,deep-*' --turn-delivery repeat --concurrency 1 \
     --snapshot evals/snapshots/loop/round-41-repeat.json
   ```

   This separates delivery from depth. If the pass rate falls with depth under
   `repeat` too, depth is the cause and the hook is exonerated; if it falls only
   under `plugin`, the reminder line is under-delivering.

## What this round cannot measure

`never_cut_failures`, which [#196] names alongside `quality_fails`. All eleven
cases in the batch carry an empty `never_cut` list in `expect.json`, so the
substring check has nothing to look for and the counter is structurally 0 at
every depth. The never-cut half of [#196]'s ask is not answerable on these
cells, and answering it would mean authoring never-cut items into the multi-turn
families first. That is a case-authoring change, not a scoring one, and it is
not in this round. It is the same coverage gap [#10] tracks.

[#10]: https://github.com/JordanMPDS/laconic/issues/10
[#196]: https://github.com/JordanMPDS/laconic/issues/196

---

## What was judged

220 runs, already generated, judged with `--judge-all` so every cell carries a
verdict: `gates_only` is `false` in both files, and 110 of 110 runs are graded on
each side. `criteria_cksum` 2497160060 on both, so the two sides were graded by
the same instrument, and neither side's criteria have moved since [#172]
corrected the `metric` stem on 2026-09-01.

| file | source runs | `rules_cksum` | judgments |
| --- | --- | ---: | ---: |
| `round-41-control-judgments.json` | `round-40-control.json` | 136269960 (master) | 110 |
| `round-41-edit-judgments.json` | `round-40-edit.json` | 1135334847 (round 40's rejected edit) | 110 |

No verdict came back `not_exercised` on either side. The registered rule that
folds one into not-a-pass never had to fire, so the primary reduces to `pass`
against `fail` throughout.

## Stage 1: the primary. The hypothesis holds and the falsifier did not fire

Master rules, `plugin` delivery — the shipped configuration.

| depth | family | median graded answer | pass |
| --- | --- | ---: | ---: |
| turn 1 | `confirm-index` | 101 words | 10/10 |
| turn 1 | `confirm-metric` | 76 | 10/10 |
| turn 1 | `confirm-rollback` | 90 | 10/10 |
| **turn 1** | **pooled** | **88.5** | **30/30 = 100%** |
| turn 2 | `recall-index` | 17 | 9/10 |
| turn 2 | `recall-metric` | 20 | 9/10 |
| turn 2 | `recall-rollback` | 10 | 10/10 |
| **turn 2** | **pooled** | **17** | **28/30 = 93.3%** |
| turn 5 | `deep-index` | 26 | 10/10 |
| turn 5 | `deep-metric` | 40 | 10/10 |
| turn 5 | `deep-rollback` | 16 | 8/10 |
| **turn 5** | **pooled** | **27** | **28/30 = 93.3%** |

Two-sided Fisher exact against turn 1, as registered: turn 2 **p = 0.4915**,
turn 5 **p = 0.4915**. Neither reaches alpha 0.05, in either comparison, and the
family-wise rate does not need to be spent.

**The registered falsifier did not fire, so [#196] answers in the negative: the
turn-2 collapse under `plugin` delivery is not a defect.** The graded answer at
turn 2 is a fifth the length of the answer to the byte-identical question at turn
1 — 17 words against 88.5 — and it catches the trap 28 times in 30 against 30 in
30. That difference is two runs, and two runs out of thirty is what a 93% cell
looks like when you draw it.

The fourth pair is reported separately as registered, and has nothing in it:
`cold-service` (1 turn) 10/10 at 284 words, `drift-service` (5 turns) 10/10 at
134 words. Both perfect on both sides of the round.

`never_cut_failures` is 0 at every depth, structurally, for the reason the
pre-registration gave: every case in the batch carries an empty `never_cut` list.
That half of [#196]'s ask is still unanswered and still wants case authoring
rather than scoring.

## Stage 2: bought whichever way stage 1 landed, and it is the interesting half

`rules_cksum` 1135334847 — round 40's rejected third pre-send check, which told
the model to recalibrate its output length against the conversation so far. Same
cells, same delivery, same hour, same judge.

| depth | pass | vs turn 1 |
| --- | ---: | ---: |
| turn 1 | 30/30 = 100% | — |
| turn 2 | **23/30 = 76.7%** | **p = 0.01054** |
| turn 5 | 29/30 = 96.7% | p = 1.0 |

On this rules revision the depth contrast **does** fire, at turn 2 only, and it
is the direction the round registered as under-delivery.

**Read against the control before reading anything into it.** The comparison that
would establish the edit as the cause is control against edit at the same depth,
and it does not reach alpha:

| depth | control | edit | Fisher |
| --- | ---: | ---: | ---: |
| turn 1 | 30/30 | 30/30 | p = 1.0 |
| turn 2 | 28/30 | 23/30 | **p = 0.1455** |
| turn 5 | 28/30 | 29/30 | p = 1.0 |

So stage 2 is a warning and not a finding, and the pre-registration is what makes
it possible to say so: it was committed before stage 1 was scored, precisely so a
hit here could not be promoted into the round's conclusion after the fact. What
it establishes is narrower and still worth having — **the null at stage 1 is not
a property of these cells.** Turn 2 is capable of falling on this instrument. It
did not fall on master.

**The failure is not length.** Both sides have a median turn-2 answer of 17 and
20 words on the same cells, and the pass rates differ by five runs. Within the
edit side the failing answers are shorter than the passing ones — 12 words at the
median against 19 — but the control's two failures are 13 and 16 words, inside
the same band. Length at the median does not separate the sides; what the judge
objected to does. Every edit-side turn-2 failure dropped a required half of the
criterion rather than answering wrongly:

- `recall-metric` rep 8, in full: *Yes.* The criterion needs the affirmation
  **and** the qualification that the absolute percentage-point difference is not
  a safe substitute. The answer carries the first and not the second.
- `recall-index` rep 7: *No — that index can't serve the query, per FINDINGS.md.*
  Correct, sourced, and missing both the `date_trunc` reason and the working fix.
- `recall-rollback` rep 1: *Migration made it unrecoverable.* True, and it never
  names migration 0042 or the `NOT NULL settlement_currency` column that is the
  load-bearing mechanism.

Under-delivery, when it happens, looks like a correct answer with a required
clause missing — not like a wrong one. That is worth recording because it is what
a token count cannot see, and it is the whole reason this round bought verdicts.


## Stage 3: the matched `repeat` batch, and one deviation from its registered command

Stage 2 hit, so stage 3 was owed. The pre-registration named this command:

```sh
python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
  --cases 'confirm-*,recall-*,deep-*' --turn-delivery repeat --concurrency 1 \
  --snapshot evals/snapshots/loop/round-41-repeat.json
```

**What ran was the same scope in three shards rather than one, at
`--concurrency 3`:**

```sh
for s in confirm recall deep; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --cases "${s}-*" --turn-delivery repeat --concurrency 3 \
    --snapshot evals/snapshots/loop/round-41-repeat-${s}.json &
done
```

Same arm, same model, same reps, same cases, same delivery. What changed is the
regime and the file layout: three CLI invocations in flight instead of one, and
three snapshots instead of one. The declaration is honest either way — each shard
stamps `concurrency_declared` 3 and each reconstructs to a floor of 1, so
`evals/bench/concurrency.py` clears all three, and none of them appears in the
19 arm-days the archive audit still flags. What the regime does to a measurement
is bounded in [`concurrency-audit.md`](concurrency-audit.md): nothing detectable
on `output_tokens`, and the one-turn rate moves in opposite directions on the two
sides of a contrast, which makes it batch rather than regime.

The three `cases_cksum` values differ from each other (2800327034, 187178077,
2136819482) because the checksum covers exactly the cases a snapshot holds, and
each shard holds three of the nine. That is the guard working, not drifting.

The pass was interrupted once, the same way round 40's was: the process that
launched it ended, leaving 22, 14 and 9 of 30. Re-running the identical commands
against the same three files resumed by key and regenerated only what the stop
left behind.

### The result: quality holds at every depth under both deliveries, and the length moves in opposite directions

90 runs, 0 failed. 90 judgments, `--judge-all`, `criteria_cksum` 2497160060 —
the same instrument that graded stages 1 and 2. No verdict came back
`not_exercised`, and **every one of the 90 came back `pass`.**

| depth | `plugin` pass | `plugin` median | `repeat` pass | `repeat` median | quality, Fisher | length, permutation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| turn 1 | 30/30 = 100% | 88.5 words | 30/30 = 100% | 94.0 words | p = 1.0 | p = 0.428 |
| turn 2 | 28/30 = 93.3% | 17 | 30/30 = 100% | 115.0 | p = 0.4915 | **p = 5e-06** |
| turn 5 | 28/30 = 93.3% | 27 | 30/30 = 100% | 159.5 | p = 0.4915 | **p = 5e-06** |

The length column is a two-sided permutation test on the median, 200,000
resamples, seeded 20260902, matching round 40's procedure.

**Turn 1 is the internal control and it holds.** Both deliveries send
byte-identical material on the session's first turn, so a difference there would
be batch rather than delivery: 88.5 words against 94.0, p = 0.428. Every turn
after the first differs by a factor of five to six.

**Under `repeat`, depth makes the answer longer.** Within this batch alone, turn 1
against turn 5 is 94.0 words against 159.5 at p = 5e-06. That is round 40's
retired inflation reproduced on a third batch, and it is the same sign and rough
magnitude as rounds 33, 35 and 36. Under `plugin` the same three families, the
same three questions and the same judge give 88.5 words against 27. The two
deliveries do not differ in degree on this material. They point in opposite
directions.

### The registered disjunction does not resolve, and that is the honest reading

The pre-registration said: if the pass rate falls with depth under `repeat` too,
depth is the cause and the hook is exonerated; if it falls only under `plugin`,
the reminder line is under-delivering. **Neither branch fires, because the pass
rate does not fall under either delivery on master rules.** `repeat` is 90/90.
`plugin` is 86/90, and stage 1 already established that its 4-run shortfall does
not reach alpha.

That disjunction was written expecting a fall to attribute. What stage 3 finds
instead is that on master rules there is no quality fall at any depth under any
delivery, which is a stronger version of stage 1's answer rather than an
arbitration of it. The comparison it does license is `plugin` against `repeat` at
matched depth, and quality is indistinguishable at all three: p = 1.0, 0.4915,
0.4915. Six times the words buy nothing the judge can see.

**What stage 3 cannot arbitrate is stage 2.** Its registered command names no
rules revision, so `run.py` read the working tree and the batch carries
`rules_cksum` 136269960 — master. Stage 2's turn-2 hit was on 1135334847, round
40's rejected edit, which is reverted and unshipped. Separating delivery from
depth *on that revision* would need a fourth batch generated against it, and this
round did not register one. The warning stage 2 recorded stays a warning.

## Verdict

**[#196] answers in the negative. The turn-2 collapse under `plugin` delivery is
not a defect, and the round closes it.**

The evidence is three-layered and each layer was registered before it was bought.
Under the shipped configuration the graded answer at turn 2 is a fifth the length
of the answer to the byte-identical question at turn 1, and it catches the trap 28
times in 30 against 30 in 30, p = 0.4915. Under `repeat` delivery on the same
cells the answer is nearly seven times longer at turn 2 and catches the trap 30
times in 30. The extra 98 words buy no measurable quality. Terseness at depth is
the plugin working.

No change to `hooks/laconic.sh` is proposed, and no rule edit is proposed. This
round buys a verdict on the shipped behavior and leaves the shipped behavior
alone.

Two things stay open, and neither is new:

- **The never-cut half of [#196]**, structurally unanswerable on these cells
  because every one carries an empty `never_cut` list. It wants case authoring,
  which is [#10].
- **Stage 2's turn-2 fall on the rejected rules revision**, un-arbitrated for the
  reason above. It is a property of a revision that is not shipped, so nothing
  turns on it today; what it establishes is that these cells can detect a turn-2
  fall, which is what makes stage 1's null worth something.

## Cost

$17.26 in three parts: $5.84 judging the two existing 110-run batches for stages
1 and 2, $8.98 generating the 90-run `repeat` batch for stage 3, and $2.44
judging it. 90 generations bought, 310 judgments bought, 0 failures on either
side.

## Ledger

No rule edit. Recorded in [`LEDGER.md`](LEDGER.md).
