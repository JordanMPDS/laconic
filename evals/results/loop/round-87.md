# Round 87: a reminder that cuts the unasked, not the answer

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 83 to 86, which are merged. This file and the edit
are committed in one commit before any generation.

`bash tools/candidate-due.sh` exits 1: round 86 measured, so this round has to
carry a candidate. It is the one [round 86](round-86.md) registered for its
reading A. **This is the last round on [#353].** Accepted or rejected, the
issue goes back to the loop's queue afterwards.

## Why this round exists

[#353]: on a follow-up turn that proposes a fix as a closed question with a
wrong premise, sonnet answers "No" plus the reason in one line and names no
fix that works. Rounds 83 to 85 edited or swapped the rules text and none of
them moved it. [Round 86](round-86.md) removed the one-line reminder that the
plugin sends on every later turn and sonnet's fails fell from 25 to 5 in 60,
p = 1.9 × 10⁻⁵. Removing the reminder also lengthened every sonnet cell, from
17 to 59 median words on `recall-index`, so deleting it would trade the
failure for the length control the reminder provides. This round rewrites it.

## The edit

The edit is not in `rules/laconic.md`. It is the per-turn reminder, in the
three places that line lives, following [round 48](round-48.md):
`hooks/laconic.sh`, `hooks/laconic.ps1` and `evals/bench/run.py`'s `REMINDER`,
which `tests/test_bench.py` pins to the hook's text.

```diff
-LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.
+LACONIC MODE ACTIVE (%s). Cut what was not asked for, never what the answer needs, and keep normal grammar.
```

`tests/test_laconic.sh` and `tests/test_laconic.ps1` assert on the reminder's
wording and change with it. `rules_cksum` is 288018845 on both sides;
`reminder_cksum` is 1027894636 on the control and 2065362485 on the edit.

## The hypothesis

The shipped line tells the model to cut, and says nothing about what must
stay. On a closed follow-up, sonnet reads the fix as content to cut. The
rewrite keeps the cut, aims it at what was not asked for, and names the
answer's substance as the thing it may not touch. It should keep most of the
length control round 86 saw the reminder provide.

## The instrument

Two trees, control at `master` and edit at this branch, generating at the
same time, laconic arm only, `--turn-delivery plugin`, four shards at
`--concurrency 4`. The reminder only reaches turn 2 onward, so the instrument
is every multi-turn case in `evals/cases`:

| shard | cells | reps | runs a side |
|---|---|--:|--:|
| sonnet | the four target cases, `recall-index`, `wide-index`, `deep-index`, `recall-metric`; the six guards, `recall-rollback`, `wide-rollback`, `wide-metric`, `deep-rollback`, `deep-metric`, `drift-service` | 15 | 150 |
| opus | the same ten | 5 | 50 |

400 generations, all judged by the panel. Round 85's pilot bars are dropped:
the `settled-*` and `contra-*` cases are single-turn, and the reminder cannot
reach them.

## The bars

One look each; no extension is registered.

1. **Primary.** `report.py --target quality_fails --target-cases
   recall-index,wide-index,deep-index,recall-metric --target-models sonnet`,
   edit against control, `--looks 1`, alpha 0.05. The target must fall and
   separate.
2. **Fatal: the four counters over all twenty cells**, as `report.py` gates
   them in the same call.
3. **Fatal: graded-turn words must not rise on the six guard cases**, sonnet
   and opus, twelve cells. `score_settled.stratified` with the sides swapped
   so it tests a rise, one-sided, alpha 0.05, words counted on the last
   turn's text. This is the length control the reminder exists for.

**Disclosed, deciding nothing:** graded-turn words on the target cases, which
the edit is expected to raise; per-cell counts; `panel_agreement.py`;
`release.py`.

**Accept** needs bar 1 to pass and bars 2 and 3 to hold. Anything else
rejects and reverts all five files.

## Power, stated before the numbers

Round 86 measured the control at 25 of 60 and no reminder at 5 of 60. At 60 a
side, one-sided Fisher at alpha 0.05 has power 0.98 against a fall from 0.40
to 0.10 and 0.72 against a fall to 0.20.

## Pre-mortem, registered

The likeliest failure is **bar 3**. The words that produce the bare "No" may
be the same words that hold later turns short, and a line that stops cutting
the fix may also stop cutting everything else. The second risk is that the
rewrite is still a cut instruction and sonnet still reads the fix as unasked,
so the target moves and does not separate. I expect the target to separate,
because round 86's effect was large, and bar 3 to be the close call.

## Consultation

None.

## One interleaved pass, four shards

```sh
git worktree add --detach /home/jordan/projects/laconic-r87-control master
git worktree add --detach /home/jordan/projects/laconic-r87-edit round-87
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric recall-rollback wide-rollback wide-metric deep-rollback deep-metric drift-service'

for side in control edit; do
  for m in sonnet opus; do
    reps=$([ $m = sonnet ] && echo 15 || echo 5)
    cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
    ( cd /home/jordan/projects/laconic-r87-$side &&
      python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
        --turn-delivery plugin --concurrency 4 \
        --snapshot $OUT/round-87-$side-$m.json ) &
  done
done
wait
```

Scoring merges each side's two shards into one snapshot and one judgments file
before `report.py`.

## Results

<!-- Nothing above this line has been computed. -->

[#353]: https://github.com/JordanMPDS/laconic/issues/353
