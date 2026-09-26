# Round 86: does the per-turn reminder cause the bare "No"?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 83 to 85, which are merged. This file is committed
before any generation. **This round proposes no rule edit.** It measures
whether the one-line UserPromptSubmit reminder, rather than the rules text,
produces [#353]'s failure.

`bash tools/candidate-due.sh` exits 0: round 85 carried a candidate.

## Why this round exists

[#353]: on a follow-up turn that proposes a fix as a closed question with a
wrong premise, sonnet answers "No" plus the reason in one line and names no
fix that works. Three rounds have edited or swapped the rules text, and none
moved it: [round 83](round-83.md) 26 → 18, p = 0.146; [round 84](round-84.md)
27 of 59 on master against 28 of 60 on the pre-round-81 rules; [round
85](round-85.md) 26 → 27. `recall-index`/sonnet failed 15 of 15 on both sides
of round 85.

The graded turn is turn 2 or later. Under `--turn-delivery plugin`, which is
the shipped wiring, the rule slice arrives on turn 1, and every later turn
carries only the reminder prepended to the prompt:

> LACONIC MODE ACTIVE (full). Make fewer claims and keep normal grammar. Cut
> content, not words.

That line is the most recent instruction the model reads before the graded
question, and *"Make fewer claims"* and *"Cut content"* both describe a
one-line "No". No round has varied it on these cases.

## The two trees

Both are worktrees at `master` and differ only in `evals/bench/run.py`, the
harness, not the rules. The `+` side sends no reminder on later turns and
leaves the prompt as the case wrote it:

```diff
-REMINDER = ("LACONIC MODE ACTIVE (%s). Make fewer claims and keep normal "
-            "grammar. Cut content, not words.")
+REMINDER = ""
...
-            if system_prompt and level:
+            if system_prompt and level and REMINDER:
```

`rules_cksum` is 288018845 on both. `reminder_cksum` separates the snapshots:
master's is the shipped line, and the no-reminder side's is `crc32("")`, 0.
Neither tree's change is committed, and the no-reminder side is not a
candidate for shipping: it is the delivery with the reminder removed, to see
whether the reminder is what moves.

## The instrument

Laconic arm, `--turn-delivery plugin`, `--concurrency 4`, four shards, both
trees at the same time, judged by the panel.

| shard | cells | reps | runs a tree |
|---|---|--:|--:|
| sonnet | `recall-index`, `wide-index`, `deep-index`, `recall-metric` | 15 | 60 |
| opus | the same four | 5 | 20 |

160 generations and about 480 judge calls. Opus failed these four cases 1 of
20 and 0 of 20 in round 84; it is here because every round generates on opus,
and it decides nothing.

## The decision, registered

**Primary:** sonnet `quality_fails` pooled over the four cases, reminder
against no reminder, one-sided Fisher, no reminder lower, alpha 0.05.

| reading | what it means | next |
|---|---|---|
| **A**: no reminder lower at p < 0.05 | the reminder produces the bare "No" | round 87's candidate rewrites the reminder in `hooks/laconic.sh` and `hooks/laconic.ps1` together, and in `run.py`'s `REMINDER` |
| **B**: not significant | removing the reminder does not remove the failure | the rules text and the delivery are both ruled out as single causes; [#353] goes back to the queue with rounds 83 to 86 recorded on it |

**Disclosed, deciding nothing:** the same comparison on opus, per-cell counts,
median words on the graded turn, `panel_agreement.py` and `release.py`.

## Power, stated before the numbers

Master has read 26, 27 and 26 fails in 60 across rounds 83 to 85. At 60 a
side, a no-reminder rate of 0.20 is detected with power of about 0.7, and a
rate of 0.10 with power of about 0.98, the same figures round 84 used.

## Pre-mortem, registered

I expect **B**. The failure survived four rules texts, including one written
against it, and the reminder says nothing about premises or fixes. How I
expect to be wrong: the reminder is short, recent and general, and a model
weighing a one-line "No" may be reading *"Cut content"* as permission the
slice never gave it.

## One interleaved pass, four shards

```sh
git worktree add --detach /home/jordan/projects/laconic-r86-plugin master
git worktree add --detach /home/jordan/projects/laconic-r86-silent master
# apply the diff above in laconic-r86-silent
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric'

for tree in plugin silent; do
  for m in sonnet opus; do
    reps=$([ $m = sonnet ] && echo 15 || echo 5)
    cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
    ( cd /home/jordan/projects/laconic-r86-$tree &&
      python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
        --turn-delivery plugin --concurrency 4 \
        --snapshot $OUT/round-86-$tree-$m.json ) &
  done
done
wait
```

Scoring:

```sh
for f in $OUT/round-86-{plugin,silent}-{sonnet,opus}; do
  python3 evals/bench/judge.py --results $f.json --out $f-judgments.json
done
python3 evals/bench/release.py $OUT/round-86-{plugin,silent}-{sonnet,opus}.json
```

## Results

<!-- Nothing above this line has been computed. -->

## Result: reading A. The reminder produces the bare "No"

160 runs, 0 failed, all four shards on CLI **2.1.282** per `release.py`, which
finds no release span. `rules_cksum` 288018845 on all four; `reminder_cksum`
1027894636 on the plugin side and 0 on the no-reminder side, as registered.
Every judgment has a panel majority; there are no three-way splits.

**Primary: sonnet `quality_fails` over the four cases, 25 of 60 with the
reminder against 5 of 60 without it, one-sided Fisher p = 1.9 × 10⁻⁵.** This is
**reading A**.

Per cell, sonnet, pass / fail, and median words on the graded turn:

| case | reminder | no reminder | words, reminder | words, no reminder |
|---|--:|--:|--:|--:|
| `recall-index` | 1 / 14 | 11 / 4 | 17 | 59 |
| `wide-index` | 5 / 10 | 14 / 1 | 19 | 71 |
| `deep-index` | 15 / 0 | 15 / 0 | 59 | 87 |
| `recall-metric` | 14 / 1 | 15 / 0 | 29 | 61 |

The reminder side reproduces rounds 83 to 85's control, 25 against 26, 27
and 26. The four failures left on the no-reminder side are the same one-line
*"No — FINDINGS.md says that index cannot serve this query, since …
`date_trunc` …"*, so removing the reminder makes the line rarer rather than
impossible.

**The pre-mortem's second branch is what happened.** Four rules texts did not
move the failure because the rules were not what produced it: on the graded
turn, the last instruction the model reads is *"Make fewer claims … Cut
content"*, and sonnet reads a named fix as a claim to cut.

### Disclosures

| | reminder | no reminder |
|---|--:|--:|
| the four cases, opus, fails | 0 of 20 | 0 of 20 |
| median words on the graded turn, opus, cases in the order above | 55, 90, 58, 45 | 73, 78, 95, 54 |

Removing the reminder lengthens sonnet's graded turn on every cell, `deep-index`
included, where it changed no verdict. That is why round 87 rewrites the line
rather than deleting it: the reminder is the only laconic instruction a later
turn carries.

Panel agreement, pairwise, sonnet files:

| pair | reminder | no reminder |
|---|--:|--:|
| sonnet / opus | 39/60, kappa 0.212 | 55/60, kappa 0.265 |
| sonnet / kimi | 40/60, kappa 0.226 | 56/60, kappa 0.314 |
| opus / kimi | 59/60, kappa 0.966 | 59/60, kappa 0.900 |

## What round 87 carries

Reading A's registered candidate: a rewritten reminder, in `hooks/laconic.sh`,
`hooks/laconic.ps1` and `run.py`'s `REMINDER` together. It has to keep the
later-turn length control the table above shows the reminder provides, and
stop reading as a licence to drop the answer's substance. [#353]'s four cases
are the target, and round 48's reminder instrument is the precedent.

[#353]: https://github.com/JordanMPDS/laconic/issues/353
