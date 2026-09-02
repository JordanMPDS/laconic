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
