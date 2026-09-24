# Round 82: does #46's design essay reproduce on opus, at depth?

**Registration. Nothing below the results line has been computed**, except the
archive figures marked as computed, which come from committed snapshots and
are why this round takes the shape it does. This file and its scorer are
committed before any generation.

**This round proposes no rule edit.** It measures, on the model the plugin is
run on, whether the failure [#46] reports exists at current rules, and it
registers in advance which kind of edit round 83 has to carry as a result.
Round 81 carried a candidate, so `tools/candidate-due.sh` allows this round,
and round 83 may not be another measurement.

## Why this round exists

[#46] is a field report from Opus 5 at level `full`. A bare *"how would that be
built?"*, asked after several short turns of a working session, came back at
about 1,400 words in eight H2 sections. Ten rounds in that cluster, none
shipped. [Round 66](round-66.md) found that removing the headings left the
claims in place, so whatever closes it has to act on claim count.

Every one of those rounds was single-turn, and none was on opus at current
rules. Opus was last measured on `design-*` in
[`opus-model-set.md`](opus-model-set.md), at rules 136269960, eight rule edits
ago. Computed 2026-09-24 from `evals/snapshots/loop/opus-model-set.json`:

| opus, 8 `design-*` cells, 5 reps | median words | 90th pct | max | over 600 | unread |
|---|--:|--:|--:|--:|--:|
| baseline | 727.5 | 959 | 1212 | 32/40 | 0/40 |
| laconic | 254.0 | 321 | 368 | 0/40 | 0/40 |

So the single-turn design case does not reproduce #46 on opus, and has not
since before the pre-action check shipped. The report's condition that no round
has reproduced is **depth**: the question came several turns into a session,
and under the shipped hook wiring a later turn carries only the one-line
reminder, not the rule slice. [Round 40](round-40.md) showed that the two
delivery modes are different treatments.

`drift-service`, a scored case, is exactly that condition. It asks five
*"how would you …"* design questions over one fixture in one session, and it
has only been generated on haiku and sonnet.

## Design

One `run.py` pass at master rules (`rules_cksum` 288018845), `--turn-delivery
plugin`, level `full`, arms `laconic` and `baseline` interleaved in each
invocation:

```
--cells 'drift-service:opus,drift-service:sonnet,design-alerting:opus'
```

Twelve reps per cell per arm, sharded three ways by `--rep-offset` (0, 4, 8)
at `--concurrency 3`. That is 240 drift-service turn calls and 24 single-turn
calls, 264 in all, 144 of them on opus. `design-alerting` is #46's own prompt,
single-turn. Nothing is judged, because no readout below reads a verdict.

## The readouts, and the fork they decide

Scored by `python3 evals/pilot/score_depth.py`, and its selftest pins every
branch.

- **R1, the tail.** This is the share of opus laconic responses over **600
  prose words**, pooled over all five `drift-service` turns and
  `design-alerting` (84 responses). 600 is under half of #46's 1,400 and above
  the old opus laconic maximum of 368.
- **R2, depth.** On opus `drift-service`, each session scores its mean log
  prose words over turns 2 to 5 minus turn 1's. D is laconic's mean score
  minus baseline's, tested one-sided by permuting whole sessions between arms,
  with seed 82 and 20,000 draws. The turns ask different questions, and the
  baseline's own profile is what separates growth caused by depth from growth
  caused by which question comes later.

**The fork, registered now, and branch A takes precedence:**

| branch | condition | round 83 carries |
|---|---|---|
| A | R1 at 10% or more | a claim-count edit for #46, scoped to opus `drift-service` |
| B | not A, and exp(D) at least 1.25 with p < 0.05 | a persistence edit on the later-turn reminder, for #46 at depth ([#60]'s mechanism) |
| C | neither | no #46 edit: #46 is recorded as not reproducing on opus on this instrument, and round 83 takes another `rules` issue |

Disclosure only, deciding nothing: per-turn medians and maxima for every cell,
the laconic/baseline and opus/sonnet ratios per turn, the same D on sonnet,
unread counts per turn, and closing offers per turn, since `drift-service` was
built for [#113] and the count is free.

## Power, stated before the numbers

R1 at 84 responses has a 95% Wilson half-width of about 6 points around 10%.
It separates a 2% tail from a 15% tail and not 8% from 12%. R2 compares 12
sessions a side, so it resolves only a large depth effect. A branch C that
rests on R2 means "no large depth effect", not "no depth effect".

## Consultation

`tools/consult.sh` was asked about the single-turn version of this design:
8 `design-*` cases on opus, baseline against laconic. Codex did not answer.

- **DeepSeek** argued that the baseline arm re-derives a prior already held.
  It said a measurement changes round 83 only if it can deselect an edit, and
  proposed a candidate round instead. The candidate it named was removing the
  pre-action check on opus. That is not taken, because the check is what
  suppresses unasked edits ([#116], round 65).
- **Kimi** said the prior is a ratio of medians and says nothing about a
  tail. It proposed writing the decision fork before any data and checking
  that each branch is reachable. It also said to verify that the instrument
  covers #46's actual trigger, and to add a same-window sonnet arm in place of
  baseline reps. **The fork, the tail readout, the coverage check and the
  sonnet arm are Kimi's.** The coverage check is what moved the round from
  single-turn `design-*` to `drift-service`: the archive figures above show
  the single-turn case already sits far below the tail. The baseline is kept
  at reduced cost because R2 needs it.

## Pre-mortem

The likeliest outcome is branch C. Opus laconic ran at a 368-word maximum
single-turn, and sonnet laconic on `drift-service` stays under 300 on every
turn (computed from `closing-edit-113-sonnet-0.json`, 5 sessions). If C comes
back, the loop has spent 144 opus calls confirming that #46 needs something
this instrument lacks, most likely a long working context. That is a
reportable result and not a reason to build another case.

## Results

72 runs (the 60 `drift-service` sessions hold 300 turn-responses), 0 failed,
three shards at `--concurrency 3` each reconstructing to one generator, and
all on CLI 2.1.281 with no release span.

```sh
python3 evals/pilot/score_depth.py evals/snapshots/loop/round-82-*.json
```

**Branch C. Neither readout comes near its bar.**

| readout | reading | bar |
|---|---|---|
| R1, opus laconic over 600 words | **0/72**, 95% Wilson [0.0%, 5.1%] | 10% |
| R2, depth on opus, exp(D) | **0.580**, one-sided p = 1.0000 | at least 1.25, p < 0.05 |

The longest opus laconic response in the round is **331 words**, on
`drift-service` turn 3. On #46's own prompt the laconic median is 220.5 words
with a maximum of 283, against a baseline median of 594.5. The upper bound on
the tail excludes the registered 10% outright.

**Depth runs the other way from #46's report.** Under the shipped reminder
wiring, laconic's later turns shrink relative to the baseline's:

| turn | opus laconic median | opus baseline median | ratio | laconic opus/sonnet |
|---|--:|--:|--:|--:|
| 1 | 176.5 | 364.5 | 0.484 | 1.634 |
| 2 | 102.5 | 397.5 | 0.258 | 1.881 |
| 3 | 274.5 | 766.0 | 0.358 | 1.336 |
| 4 | 107.5 | 436.0 | 0.247 | 1.335 |
| 5 | 151.0 | 582.0 | 0.259 | 1.373 |

Sonnet shows the same pattern (exp(D) = 0.507). Opus laconic is 1.3x to
1.9x sonnet laconic on every turn, which is inside round 80's 2x to 3x
finding and below it. Closing offers were 0 of 120 on laconic across both
models. The opus baseline also made none; the sonnet baseline made 14 of 60.
Unread counts are similar across the arms. Turns 2, 4 and 5 go unread on both
arms of opus because the fixture was already read in the session.

## Verdict

**Branch C, as the pre-mortem expected.** On the loop's instrument, #46 does
not reproduce on opus, single-turn or five turns deep, at current rules.
Round 83 takes a `rules` issue other than #46 and has to carry an edit.

This is not evidence that #46 is fixed. The report's session was a long
working context over a real document. `drift-service` is five questions over
a small fixture, so what this round rules out is depth alone, under the
shipped reminder, as the cause. A case that reproduces #46 would need that
working context, and building one is not registered here.

Label: none. This round carried no candidate, so it takes no row in
`candidate-defects/labels.json`.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
