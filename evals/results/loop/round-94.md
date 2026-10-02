# Round 94: does session depth turn #305's narrowing follow-up long on opus?

**Registration. Nothing below the results line has been computed**, except
the figures quoted from round 93, which is merged. This file, the
`deepsubset-*` cases, their layout test and the `depth` command in
`evals/pilot/score_subset.py` are committed before any generation.

**This round proposes no rule edit.** Round 93 carried one, so
`tools/candidate-due.sh` allows this round to measure, and round 95 may not.
Everything here runs at master rules (`rules_cksum` 288018845).

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_subset.py depth \
  --shallow evals/snapshots/loop/round-94-shallow.json \
  --deep evals/snapshots/loop/round-94-deep-{ledger,scheduler,gateway}.json
python3 evals/bench/release.py evals/snapshots/loop/round-94-*.json
```

## Why this round exists

[#305] was reported on Opus 5 from a long working session: an inventory of a
three-bucket status file, housekeeping items closed, then an eleven-word
follow-up narrowing to one bucket, answered in 309 prose words where about 40
were right. [Round 93](round-93.md) rebuilt the inventory and the follow-up as
two turns (`subset-*`). The re-listing fired, 87 of 90 control graded turns
naming the eight seeded questions again, but those turns ran a median of about
50 prose words. The length harm, which is the report's actual complaint, did
not fire, and a bullet aimed at the re-listing moved it by 0.18 of an item.

Round 93 named the remaining difference from the report as session depth.
[Round 82](round-82.md) tested depth for [#46] with five short design turns and
found it not enough there; nothing has tested it for #305.

## What is read

`deepsubset-<stem>` is `subset-<stem>` with four turns inserted between the
inventory and the narrowing question. The fixture is byte-identical and the
first and last turns are subset's two, which `tests/test_evals_layout.sh`
checks:

1. `read STATUS.md — what is left with <project>? Don't edit anything.`
2. `walk me through IMPL-4 — what does it still need, and what does it depend on? Don't edit anything.`
3. `VAL-3 is done — CI runs the validator on pull requests now. Mark it closed in STATUS.md.`
4. `VAL-2 is done too. Close it in STATUS.md.`
5. `how would you approach IMPL-6? Don't edit anything.`
6. `what is left at the SPEC level to finish <project>? Don't edit anything.` (graded)

Turns 3 and 4 are the report's housekeeping, as real edits to the workspace.
Closing VAL items leaves the SPEC bucket unchanged, so turn 6 has subset's
correct answer.

Both depths generate in one pass, laconic arm, level `full`, opus,
`--turn-delivery plugin`, 10 reps per stem: 30 shallow runs (60 calls) and 30
deep runs (180 calls). Four shards run at once, all `--concurrency 4`: the
three deep stems one each, and the shallow family in one.

```sh
python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
  --cells 'deepsubset-<stem>:opus' --turn-delivery plugin --concurrency 4 \
  --snapshot evals/snapshots/loop/round-94-deep-<stem>.json
python3 evals/bench/run.py --arms laconic --reps 10 --cases-dir evals/pilot \
  --cells 'subset-ledger:opus,subset-scheduler:opus,subset-gateway:opus' \
  --turn-delivery plugin --concurrency 4 \
  --snapshot evals/snapshots/loop/round-94-shallow.json
```

### The registered readouts

1. **Fire, the headline.** At least **9 of 30** deep graded turns run over
   **150 prose words** (fenced code, inline code and URLs out). 150 is about
   three times the shallow median round 93 measured and half the report's
   309. Nine of 30 keeps round 91's screen: below it, a round of the size an
   edit needs cannot power a fall.
2. **Depth contrast.** Mean log graded prose words, deep minus shallow,
   averaged over stems, with the depth label permuted within stem, two-sided,
   seed 94. A fire with this contrast at p < 0.05 and deep longer is
   attributable to depth; a fire without it is a length the shallow arm also
   shows, and the shallow arm's own count over 150 is printed beside the fire
   for that reason.

Disclosed, deciding nothing: per-stem medians, re-listings of at least 5 of 8
at each depth, runs that wrote to the workspace at each depth, and
`release.py`.

**A run that edits on a turn that said not to is kept.** The harness records
the workspace diff for the whole session, not per turn, so a deep run's write
cannot be attributed to turn 3 or 4 rather than another. The count is
disclosed. A shallow run that writes anything is disclosed the same way.

### What each outcome sends to round 95

- **Fires, attributable to depth:** round 95 takes #305's length on
  `deepsubset-*`, opus, with an edit aimed at the surplus that appears.
- **Fires, not attributable:** the shallow arm drifted long since round 93; round
  95 takes the length on `subset-*`, the cheaper instrument.
- **Does not fire:** this licenses "no reliably firing length harm at six
  turns of this kind", not "depth is ruled out" — at 0 of 30 the 95% upper
  bound is about 10%, and a twelve-turn session is untouched. Round 95 still
  owes an edit, and takes it from the `rules` issue with the strongest current
  fire, which is #305's re-listing on `subset-*`.

## Pre-mortem, registered

**I expect it not to fire.** Round 82's depth null for #46, round 91's null at
five turns on `edit-service`, and round 93's 50-word graded turns all point at
opus answering a plainly scoped question plainly whatever came before it. The
likeliest positive is a modest depth contrast without a fire: the deep turn
somewhat longer, carrying a recap of the housekeeping, with very few turns past
150.

## Where the ideas came from

The depth question is round 93's stated next step and round 91's. Through
`tools/consult.sh`, Kimi argued against padding turn 1 with a pasted transcript,
since that tests context size rather than a session the model wrote; proposed
disclosing the shallow arm's own count over the line, so a fire cannot be read
off an arm that drifted; proposed permuting within stem; asked for the handling
of an edit on a "don't edit" turn to be registered in advance; and warned that a
null licenses less than "depth is ruled out". All five were taken. Its
suggestion to rewrite turns 2 and 5 so that their IMPL items do not touch the
seeded questions was not: re-listing is disclosed here, not decided on. Codex
and DeepSeek did not answer.

[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#46]: https://github.com/JordanMPDS/laconic/issues/46

## Results

<!-- Nothing above this line has been computed. -->
