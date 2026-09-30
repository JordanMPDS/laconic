# Round 88: which clause of the reminder produces the bare "No"?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 83 to 87, which are merged. This file is committed
before any generation. **This round proposes no rule edit.** It ablates the
one-line per-turn reminder clause by clause to find which words produce
[#353]'s failure and which provide the length control.

`bash tools/candidate-due.sh` exits 0: round 87 carried a candidate.

## Why this round exists

[#353]: on a follow-up turn that proposes a fix as a closed question with a
wrong premise, sonnet answers "No" plus the reason in one line and names no
fix that works. [Round 86](round-86.md) found the cause: the reminder the
plugin prepends to every later turn,

> LACONIC MODE ACTIVE (full). Make fewer claims and keep normal grammar. Cut
> content, not words.

Without it, sonnet's fails fell from 25 to 5 in 60 (p = 1.9 × 10⁻⁵), and every
graded turn got longer. [Round 87](round-87.md) replaced the whole line with a
rewrite and got the worst of both: fails 20 → 14 (p = 0.196) and guard-case
words up 12.5 (p = 0.0002). A whole-line rewrite changes every clause at once,
so it cannot say which clause did what. The line has two instructions after
its header, *"Make fewer claims"* and *"Cut content, not words"*. This round
removes each one separately, and removes both, so the next candidate edits the
clause that causes the failure and keeps the one that provides the length control.

## The four trees

All four are worktrees at `master`. They differ only in `evals/bench/run.py`'s
`REMINDER`, the harness copy of the hook line. The change is not committed in
any of them, as in round 86. `rules_cksum` is the same on all four;
`reminder_cksum` separates the snapshots.

| arm | `REMINDER` |
|---|---|
| **S**, shipped | `LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar. Cut content, not words.` |
| **F**, fewer only | `LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal grammar.` |
| **C**, cut only | `LACONIC MODE ACTIVE (%s). Keep normal grammar. Cut content, not words.` |
| **H**, header only | `LACONIC MODE ACTIVE (%s).` |

H tests the third possibility: the mere presence of a laconic marker on the
graded turn licenses the bare line. In that case every arm with a header fails
alike, and round 86's no-reminder arm is the only low one.

## The instrument

Laconic arm, `--turn-delivery plugin`, one process per tree, four trees at
once, `--concurrency 4`. Each process generates sonnet first, then opus, into
two snapshots.

| model | cells | reps | runs a tree |
|---|---|--:|--:|
| sonnet | the four target cases, `recall-index`, `wide-index`, `deep-index`, `recall-metric`; the six guards, `recall-rollback`, `wide-rollback`, `wide-metric`, `deep-rollback`, `deep-metric`, `drift-service` | 15 | 150 |
| opus | the same ten | 3 | 30 |

720 generations. Only the four target cases are judged, by the panel
(`judge.py --cases`): 288 judgments, about 864 judge calls. The guards
are scored on words alone, which needs no judge. Opus is here because every
round generates on opus, and it decides nothing.

## The decision, registered

**Primary.** For each of F, C and H against S: sonnet `quality_fails` pooled
over the four target cases, one-sided Fisher, the variant lower, alpha
0.05 / 3 = 0.0167 (Bonferroni over the three comparisons).

**Length bar.** For each variant against S: median graded-turn words on the
six guard cases, sonnet and opus, twelve cells. The test is
`score_settled.stratified` with S as control, one-sided for a rise, alpha
0.05, words counted on the last turn's text. This is the same test as round
87's bar 3. It is a regression screen, so it is not corrected.

| reading | what it means | next |
|---|---|---|
| a variant passes the primary and holds the length bar | that line keeps the length control without the failure | round 89 ships it in `hooks/laconic.sh`, `hooks/laconic.ps1` and `run.py` as a candidate |
| F passes the primary, C does not | *"Cut content, not words"* produces the failure | round 89 rewrites or drops that clause |
| C passes the primary, F does not | *"Make fewer claims"* produces the failure | round 89 rewrites or drops that clause |
| only H passes the primary | both clauses contribute, and neither alone is safe | round 89 tests the header plus a length instruction that does not tell the model to cut |
| none passes | the header alone licenses the line | a candidate has to change the delivery, not the wording; [#353] goes back to the queue |

**Disclosed, deciding nothing:** per-cell counts, graded-turn words on the
target cases, opus fails on the target cases, `panel_agreement.py`,
`release.py`.

## Power, stated before the numbers

S has read 25 and 20 fails in 60 in rounds 86 and 87. Taking S at 0.40, one-sided Fisher
at alpha 0.0167 with 60 a side has power 0.96 against a variant at 0.10
(round 86's no-reminder rate), 0.79 at 0.15, and 0.54 at 0.20. This round
cannot tell two variants apart unless one sits near no-reminder and the other
near S.

## Pre-mortem, registered

I expect **F to pass the primary and C not to**. *"Cut content"* is the
clause that tells the model to remove substance, and a named fix is
substance. I am least sure about the length bar: round 87 showed the length
control and the failure may come from the same words, in which case F passes
the primary and fails the length bar. H is the arm most likely to surprise
either way.

## Consultation

`tools/consult.sh` was asked the design and the three open questions (power,
whether H is worth a shard, and whether any length instruction on the graded
turn licenses the line). None of codex, deepseek or kimi answered within the
timeout. The design is my own.

## One interleaved pass, four trees

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric recall-rollback wide-rollback wide-metric deep-rollback deep-metric drift-service'
for arm in S F C H; do
  git worktree add --detach /home/jordan/projects/laconic-r88-$arm master
done
# patch REMINDER in laconic-r88-{F,C,H} per the table above

for arm in S F C H; do
  ( cd /home/jordan/projects/laconic-r88-$arm &&
    for m in sonnet opus; do
      reps=$([ $m = sonnet ] && echo 15 || echo 3)
      cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
      python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
        --turn-delivery plugin --concurrency 4 \
        --snapshot $OUT/round-88-$arm-$m.json
    done ) &
done
wait

for f in $OUT/round-88-{S,F,C,H}-{sonnet,opus}; do
  python3 evals/bench/judge.py --results $f.json --out $f-judgments.json \
    --cases recall-index,wide-index,deep-index,recall-metric
done
python3 evals/bench/release.py $OUT/round-88-{S,F,C,H}-{sonnet,opus}.json
```

## Results

<!-- Nothing above this line has been computed. -->

[#353]: https://github.com/JordanMPDS/laconic/issues/353
