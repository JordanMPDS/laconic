# Round 84: does round 81's paragraph cause the bare "No"?

**Registration. Nothing below the results line has been computed**, except the
archive figures marked as such, which come from committed snapshots. This file
is committed before any generation. **This round proposes no rule edit.** It
measures which part of the shipped rules produces [#353]'s failure, so that
the next candidate edits the right sentence.

`bash tools/candidate-due.sh` exits 0: round 83 carried a candidate.

## Why this round exists

[Round 83](round-83.md) appended a sentence against the bare "No" and moved
sonnet's `quality_fails` on the four [#353] cases from 26 to 18 in 60, p = 0.146.
Every failure left on the edit side was the same one line: *"No — that index
can't be used, since … `date_trunc` …"*. Arguing against the line did not
remove it. The next candidate should change what licenses it, and two
sentences in the shipped rules could be doing that:

- **Round 81's length paragraph**, shipped in v0.3.3: a requested answer
  *"gets the scope it needs, and no claim in it twice"*. On a follow-up turn,
  the working fix was already given in an earlier turn, and a model reading
  "no claim in it twice" across turns would drop it. Round 81 generated no
  sonnet at all, and none of its bounds was a follow-up question.
- **The closed-question specimen** from rounds 71 and 73: *"The one word is
  the whole answer, not the opening of one."* It is written about a true
  premise and says nothing about a false one.

The archive points at the first but cannot separate them. Computed from
committed snapshots, sonnet, laconic, pass counts on `recall-index`,
`wide-index`, `deep-index`:

| source | rules | judge | pass |
|---|---|---|--:|
| round 73, edit side | 3285158247 (v0.3.2) | sonnet alone | 14/15 |
| benchmark 2026-09-24 | 288018845 (v0.3.3) | panel | 8/15 |
| round 83, control side | 288018845 (v0.3.3) | panel | 20/45 |

The judge changed between the first row and the others, so this table is a
lead, not a comparison. This round is the comparison: both rule texts,
generated at the same time and graded by the same panel.

## The two trees

Both are worktrees at `master` (`94d469d`) and differ only in the length
paragraph:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets the scope it needs, and no claim in it twice. Laconic governs volunteered
-content.
+gets full detail. Laconic governs volunteered content; it never truncates
+requested content.
```

The `-` side is master, `rules_cksum` **288018845**. The `+` side is the
paragraph as it stood before round 81 (`git show d12fe94~1:rules/laconic.md`),
with `rules/dist/*.md` rebuilt, `rules_cksum` **3285158247**. The harness,
cases and hooks are master's in both trees, and neither tree's rules change
is committed.

## The instrument

Laconic arm, `--turn-delivery plugin`, `--concurrency 4`, four shards, both
trees at the same time. Every run is judged by the panel with `--judge-all`,
so `conditional` is graded too.

| shard | cells | reps | runs a tree |
|---|---|--:|--:|
| sonnet | `recall-index`, `wide-index`, `deep-index`, `recall-metric`, `conditional` | 15 | 75 |
| opus | the same five | 5 | 25 |

200 generations and about 600 judge calls. Opus runs at 5 reps because it
passed the four quality cases 60 of 60 on both sides of round 83. It is here
because every round generates on opus, and it decides nothing.

## The decision, registered

**Primary:** sonnet `quality_fails` pooled over `recall-index`, `wide-index`,
`deep-index` and `recall-metric`, master against v0.3.2, one-sided Fisher,
v0.3.2 lower, alpha 0.05.

| reading | what it means | the round-85 candidate |
|---|---|---|
| **A**: v0.3.2 lower at p < 0.05 | round 81's paragraph produces the bare "No" | narrow *"no claim in it twice"* to repetition inside one answer, leaving what an earlier turn said to be repeated when the question needs it |
| **B**: not significant, and v0.3.2 fails at least 15 of 60 | the rules before round 81 produce it too | scope the specimen's *"The one word is the whole answer"* to a true premise, so a false premise loses the licence |
| **C**: not significant, and v0.3.2 fails fewer than 15 of 60 | the round cannot separate the two | extend both trees by 15 reps, registered as a second look, before choosing |

**Disclosed, deciding nothing:** `conditional` pass rates on both models, the
same comparison on opus, median words on the graded turn, `panel_agreement.py`
on both judgment files and `release.py` across the four shards.

## Power, stated before the numbers

Round 83's control read master at 26 of 60. Round 83's simulation, the same
test at 60 a side, gives power 0.98 if v0.3.2 fails at 0.10 and 0.72 if it
fails at 0.20. Round 73's single judge read v0.3.2 at 1 fail in 15.

## Pre-mortem, registered

I expect **A**, because the three-row table above moved when the paragraph
did. How I expect to be wrong: the panel is stricter than sonnet alone on
exactly these cases, so v0.3.2 also fails near 20 of 60 and the reading is
B. Round 73's sonnet-only judge passed answers that named a fix loosely, and
the panel's opus and kimi votes do not.

## One interleaved pass, four shards

```sh
git worktree add --detach /home/jordan/projects/laconic-r84-master master
git worktree add --detach /home/jordan/projects/laconic-r84-v032 master
( cd /home/jordan/projects/laconic-r84-v032 &&
  git show d12fe94~1:rules/laconic.md > rules/laconic.md && bash tools/build-rules.sh )
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
CASES='recall-index wide-index deep-index recall-metric conditional'

for tree in master v032; do
  for m in sonnet opus; do
    reps=$([ $m = sonnet ] && echo 15 || echo 5)
    cells=$(for c in $CASES; do printf '%s:%s,' $c $m; done); cells=${cells%,}
    ( cd /home/jordan/projects/laconic-r84-$tree &&
      python3 evals/bench/run.py --arms laconic --cells "$cells" --reps $reps \
        --turn-delivery plugin --concurrency 4 \
        --snapshot $OUT/round-84-$tree-$m.json ) &
  done
done
wait
```

Scoring:

```sh
for f in $OUT/round-84-{master,v032}-{sonnet,opus}; do
  python3 evals/bench/judge.py --judge-all --results $f.json --out $f-judgments.json
done
python3 evals/bench/release.py $OUT/round-84-{master,v032}-{sonnet,opus}.json
```

The primary is the pooled fail count read from the two sonnet judgment files,
with the one-sided Fisher `evals/pilot/score_settled.fisher_le` computes.

## Results

<!-- Nothing above this line has been computed. -->

[#353]: https://github.com/JordanMPDS/laconic/issues/353
