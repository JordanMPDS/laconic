# Round 33: ownership is real, and it is not big enough

**This round proposes no rule edit.** It runs the experiment [#166] was built
for, and reports what the mechanism [#136] names is actually worth in words.

## What round 32 left

Round 32 built three closed-confirmation cases for [#136] — `confirm-metric`,
`confirm-index`, `confirm-rollback` — and measured that the reported failure
does not reproduce on them. Laconic's medians came in at 80, 106 and 87 words
against baseline's 144, 130 and 149, and the widest of fifteen laconic
responses was 124 words against the ~400 the issue reports.

It also said why, and the explanation was a claim about the harness rather than
about the rules:

> The mechanism is ownership, and the harness cannot construct it. [#136]
> locates it itself — the model re-derived an argument *it had made* to someone
> quoting it back — and a fixture read cold is evidence to cite, not a position
> to defend.

That claim was filed as [#166], which added multi-turn generation to `run.py`.
This round spends it.

## The instrument

Three multi-turn twins, `recall-metric`, `recall-index` and `recall-rollback`,
share their fixture, their `expect.json` and their turn-2 question with the
`confirm-*` case of the same stem. The only difference is that turn 1 asks the
open question first:

```
read ANALYSIS.md — what is wrong with how this experiment is being reported? Don't edit anything.
<!-- turn -->
you concluded lift is the wrong metric for this experiment, correct? Don't edit anything.
```

Turn 2 deliberately drops the `read FILE —` prefix the `confirm-*` prompt
carries. Telling the model to re-read the file is the thing that would undo the
setup: the point is that the conclusion is in its own context, not on disk.

**`confirm-*` is therefore the exact control for `recall-*`** — same document,
same closed question, same instruction not to edit, differing only in whether
the model is confirming a conclusion it read or one it wrote. That is the
contrast [#136] describes, and round 32 could not construct it.

Both families ran in **one interleaved batch**, 5 reps a side, sonnet,
`--concurrency 1`. The between-batch drift this repo has been burned by twice —
the carried-arm invalidity from round 16 onward, and round 31's registered
baseline moving 70% in three days — cannot reach a contrast generated this way.

## The registered question

Written before the batch ran:

> If [#136]'s mechanism really is ownership, `recall-*` should balloon where
> `confirm-*` stayed at 80–106 words. If it doesn't, the issue's own diagnosis
> is wrong and that's the more interesting result.

## Result

Median words on the graded turn, 5 reps a cell:

| Case | baseline | laconic |
|---|--:|--:|
| `confirm-metric` | 124 | 85 |
| `confirm-index` | 125 | 107 |
| `confirm-rollback` | 153 | 92 |
| `recall-metric` | 154 | 115 |
| `recall-index` | 201 | 133 |
| `recall-rollback` | 175 | 101 |

Pooled by family:

| | baseline | laconic | laconic vs baseline |
|---|--:|--:|--:|
| `confirm-*` | 136 | 93 | −31.6% |
| `recall-*` | 175 | 127 | −27.4% |
| **recall vs confirm** | **+28.7%** | **+36.6%** | |

**Ownership lengthens the answer, and the direction is not in doubt.** Every
one of the six cells is longer under `recall-*` than under its `confirm-*`
control (two-sided exact sign test, p = 0.031), and pairing run by run on
`(arm, stem, rep)` the recall response is longer in **29 of 30 pairs**,
p < 0.0001. The mechanism [#136] names is real and is now measurable.

**It is also small.** Laconic's median moves from 93 words to 127. The widest
laconic response across all 30 runs is 144 words; the widest response in the
round, in either arm, is 217. [#136] reports ~400 words to an eight-word
closed question. Ownership buys about a third more words. It does not buy a
quadrupling, and nothing in 60 runs came close to the reported length.

So the registered question answers **both ways, and the split is the finding**:
the diagnosis in [#136] is correct about the mechanism and wrong about its
size. Ownership is a contributor, not the cause.

## What is not comparable, and why the metric here is words

Every `confirm-*` graded turn carries a tool-use block — 30 of 30 opened the
fixture on the turn that was scored. No `recall-*` graded turn carries one: the
reading happened on turn 1, and turn 2 calls nothing. `output_tokens` counts
those blocks, so **`output_tokens` is not comparable across the single-turn /
multi-turn boundary** and reads backwards on two of the six pairs while words
rise on all six.

This is a property of the boundary, not of these cases. A scoped
`output_tokens` target must not be registered across it. Words are the honest
metric for this contrast and are what the table above reports.

## Reading

**All 60 runs opened their fixture** — 59 through `Read`, one through `cat` in
a `Bash` call, quoting the document verbatim in its answer. Every cell in both
families is 5/5.

There is no [#131] stratum crossing anywhere in the round, so the whole
contrast sits inside one reading stratum and the word counts are comparable for
that reason too. It also means none of laconic's compression here was bought by
not looking, which is the defect round 23 found in the `design-*` scope.

A `Read`-only proxy would have scored the `cat` run as unread and reported
`recall-rollback`/laconic at 4/5. It read.

## Grading

Traps grade **60 of 60**, both arms, both families. No `quality` failure
anywhere in the round.

That is a ceiling, and a cell drawn at 5/5 cannot rise — per [#94] these cases
detect a fall, not a regression. What it does establish is that the extra words
under `recall-*` are not buying correctness: the shorter `confirm-*` answers
were already right, and so were the longer `recall-*` ones.

## Disclosed, not credited

Laconic's proportional inflation under ownership (+36.6%) is larger than
baseline's (+28.7%), so the rules lose about four points of compression under
the harder condition — 31.6% down to 27.4%. At 5 reps a cell this round cannot
separate that from sampling, and it is recorded rather than claimed.

## What this leaves

[#136] stays open with its diagnosis narrowed rather than closed. The gap
between 144 measured words and ~400 reported ones needs an account, and the
obvious candidate is the one round 32's own framing named: **a short question
about a large subject, where the subject's size sets the answer's size.** These
fixtures are a page. [#136]'s subject was an argument developed across a real
session. Ownership was the variable this round could isolate; subject size is
the next one, and `run.py` can now express it.

Four of the over-length cluster's six issues were called blocked on machinery
in round 32. One of the four is now unblocked and measured. The other three —
[#60]'s drift half, [#150], [#116] — are unchanged.

90 generations across 60 runs, 60 judgments, 0 failed, $2.96.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#166]: https://github.com/JordanMPDS/laconic/issues/166
