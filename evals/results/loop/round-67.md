# Round 67: the cluster's last untested explanation — a session that works

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are why this round has the scope and
the power it has. This file, the case triple, the extended layout contract and
the scorer are committed in one commit before any generation, following
[round 38](round-38.md) through [round 66](round-66.md).

**This round proposes no rule edit.** `bash tools/candidate-due.sh` exits 0:
[round 66](round-66.md) carried a candidate and rejected it, so round 67 may
measure. It is the one measuring round the cap allows, and round 68 has to carry
an edit.

## Why this round exists

The over-length cluster is six user-filed issues — [#46], [#60], [#113],
[#116], [#136], [#150] — and thirteen rounds. Its index document,
[`over-length-cluster.md`](over-length-cluster.md), states the cluster's central
question as the gap between what the reports describe and what the benchmark can
produce, and names exactly two candidate explanations for it. One has been
tested. The other has not been touched by anything:

> - **The harness's earlier turns are not the reports' earlier turns.** Both
>   reports describe a session whose prior answers were *legitimately long*.
> - **A real session interleaves work with questions.** Every turn in these
>   cases ends `Don't edit anything.`

The first was built as `evals/pilot/register-*` and measured in
[`register-inheritance-136.md`](register-inheritance-136.md). It reproduced the
reported mechanism for the first time in the loop's history: after four turns
whose length the rules licensed, laconic's answer on a byte-identical graded
turn runs **31.0 words to 52.0, a ratio of 1.677 at permutation p < 0.00001**,
three stems of three, while the baseline arm does not move at all (185.5 to
190.5, p = 0.9135, zero stems of three). The licence does not expire.

That pilot also stated its own limit, and the limit is this round's subject:

> **The magnitude gap is not closed and is the honest limit.** [#136] reports
> about 400 words; this reads 52. The mechanism reproduces at roughly an eighth
> of the reported size, so it is a mechanism finding and not a reproduction of
> the report. **The cluster's second candidate — a session that interleaves work
> with questions — is untouched and remains the candidate for the rest.**

The reports say the same thing in their own words. [#136] locates the pull
*"when the model has a lot of recent context it is proud of"*. [#116]'s failure
is a one-line comprehension question answered correctly and then substantiated
with analysis nobody asked for, deep in a session where the model had been doing
work. Neither describes a stretch of long prose. Both describe a stretch of
work.

Nothing in the scored suite can produce that, and the reason is a rule rather
than an oversight: `CRITERIA.md` requires every prompt to end `Don't edit
anything.`, because a diagnosis delivered in the diff is a diagnosis the judge
cannot grade. Every one of `deep-*`'s five turns carries it. So the instrument
has a structural floor on how much work a session can contain, and the
explanation the cluster has left is the one the instrument was built to exclude.

## The instrument: one clause of difference, on three turns

`evals/pilot/work-{index,metric,rollback}` is `evals/cases/deep-*` with

- **turn 1 byte-identical**,
- **turn 5 byte-identical**, and the same `trap`, `never_cut` and `grading`,
- **the same fixture**, by symlink rather than by copy,
- **turns 2 to 4 asking deep's three questions verbatim**, with the deliverable
  moved from the reply into the fixture file.

`deep-rollback` turn 2 against `work-rollback` turn 2, in full:

    how bad was the customer impact here? Don't edit anything.

    how bad was the customer impact here? Write it into INCIDENT.md under a
    "Customer impact" heading, rather than answering here.

That is the whole manipulation. Subject matter, fixture, turn count, turn order
and the graded question are all held; what varies is whether the model's own
three prior turns produced prose or produced work. It is `register-*`'s design
with a different clause bolted to the same three turns, which is deliberate:
two pilots sharing turn 1, turn 5, the fixture and the trap are comparable to
each other as well as to their common control.

**The graded turn keeps `Don't edit anything.`, and that is not an oversight.**
`CRITERIA.md`'s rule is that a case needs the clause *"or its verdicts measure
whether the model chose to act"*, and turn 5 is the only turn here that produces
a verdict. Holding it also settles, at no cost, the confound a separate arm
would otherwise have to buy: standing permission to edit is identical on the
graded turn in both families, so a movement there cannot be the permission.
`tests/test_evals_layout.sh` holds both halves — the pair contract, now run over
`register-*` and `work-*` alike, and a second check that `work-*` forbids
editing on the graded turn and on no other.

## What the manipulation does to the middle turns, and why that is the round

Two archive figures, computed before this round and stated as its design input
rather than its evidence:

- On `deep-*`, laconic spends **77.5 prose words across all three middle
  turns**, against baseline's 924.5 ([`register-inheritance-136.md`](register-inheritance-136.md)).
- A response that edits a file runs **45 median words against 144** for one that
  does not, on the same case, permutation p = 5e-06
  ([`volunteered-work.md`](volunteered-work.md), [#209]).

So `work-*`'s middle turns will very likely carry *less* prose than `deep-*`'s
already-thin 77.5 words, and more work. The two accounts of the cluster
therefore predict opposite signs on the graded turn:

| account | middle turns | predicts turn 5 |
|---|---|---|
| recent context the model is proud of ([#136]'s own words) | work accumulates | **rises** |
| accumulated prose register (what `register-*` moved) | prose falls | **falls or flat** |

**That is why the primary is two-sided and why both directions are interpreted
in advance.** It is not a device for guaranteeing a story: the two readings are
asymmetric, and the asymmetry is registered below because `tools/consult.sh`
insisted on it.

## Registered endpoints

**Primary.** Median prose words on the graded turn 5, **laconic** arm,
`work-*` against `deep-*`, pooled over the three stems, two-sided permutation on
the family label at seed 67, alpha = 0.05. Reported per stem beside the pooled
figure.

**Control, and it is what makes the primary readable.** The **baseline** arm,
same cases, same interleaved batch, same test. `register-*`'s null on this arm —
p = 0.9135, zero stems of three, a mean that fell — is what ruled out the "it is
just a longer case" reading there, and it is what has to rule it out here. A
`work-*` movement that appears on both arms is the case, not the rules.

**Manipulation check 1, and failing it voids the primary rather than
footnoting it.** The share of `work-*` laconic runs whose turns 2 to 4 call a
workspace-changing tool (`Edit`, `Write`, `MultiEdit`, `NotebookEdit`), read off
the per-turn tool list `run.py` records. **Registered bar: at least 24 of 30.**
Below that the arm did not receive its treatment and the round reports a failed
manipulation, not a null — round 59's `abl-arrow` check is the precedent, and
laconic is known to suppress volunteered edits hard (30.0% to 5.8% on
`conditional`, [round 65](round-65.md)), so this is a live risk rather than a
formality. Turn 5 is excluded from the check on purpose: it forbids editing in
both families, so counting a tool call there would let a rule violation clear
the check. The run-level `artifacts` field ([#150]'s first half) is printed
beside it as a second, independent reading of the same fact.

**Manipulation check 2, a measurement and not a bar.** Prose words summed over
turns 2 to 4, both arms, both families. This is the quantity the two accounts
disagree about, so it is what makes a fall on the primary interpretable rather
than merely negative.

**Harm check.** The `index` stem's one never-cut keyword, `date_trunc`, present
on the graded turn. It covers a third of the batch and the other two stems carry
no keyword, exactly as in the register pilot. Nothing is judged: every endpoint
here is deterministic, and the graded turn's trap is left for the round an
effect earns, on [#94]'s reading of a cell graded 120 of 120.

## The registered decision rule, written before any generation

Three branches, and the interpretation of each is fixed here.

1. **The laconic arm separates upward and the baseline arm does not.** Required
   work on turns 2 to 4 inflates the answer on a turn that forbids it. The
   cluster's second candidate is supported, and the round's recommendation is a
   judged batch on `work-*` plus the promotion decision `register-*` is also
   waiting on.
2. **The laconic arm separates downward and the baseline arm does not.** Work
   displaces prose and the graded turn follows the prose rather than the work.
   That is evidence against a large net inflation from required work, and it is
   **not** proof that prose register rather than recent context carried
   `register-*` — the manipulation changes more than prose volume, there is no
   third arm, and the mechanism is not identified by this design. The candidate
   closes as an explanation for the magnitude gap; the cluster's gap then has no
   remaining named candidate, which is itself the finding.
3. **Neither arm separates.** A bounded null, bounded by the power below, and
   the cluster's second candidate is answered in the negative at that bound.

The asymmetry in branch 2 is `codex`'s, from `tools/consult.sh`, and so is the
resolution of the permission confound in the instrument section above — its
first answer pointed out that a byte-identical turn 5 already holds standing
permission constant, which removed a third arm and 50% of the generations from
the draft design. `deepseek` and `kimi` were asked twice and neither answered
inside the timeout; that is reported so a reader can tell "nobody objected" from
"nobody was asked".

## Power, stated before the numbers

Computed from the 30 laconic `deep-*` turn-5 responses of the committed
`register-136.json`, which is this round's own control family at
`rules_cksum` 136269960: median 31.0 words, mean 30.5, standard deviation 12.7,
and 0.498 on the log scale. Resampling that distribution at 30 against 30 and
scoring it with the round's own two-sided permutation, 300 trials a point:

| true ratio | power |
|---:|---:|
| 0.70 | 0.89 |
| 0.80 | 0.48 |
| 1.25 | 0.51 |
| 1.40 | 0.86 |
| 1.60 | 0.99 |
| 1.80 | 1.00 |

So the round is well powered for an effect of the size `register-*` produced
(1.677x) and for the mirror of it, and it is **not** powered for anything inside
roughly 0.8x to 1.25x. Branch 3 is a null bounded at that band and says nothing
below it. That is stated here rather than discovered afterwards.

## The command

Three shards, one per stem, launched together and declaring each other:

```sh
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms baseline,laconic --models sonnet --reps 10 \
    --cases "deep-$stem,work-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 3 \
    --snapshot "evals/snapshots/loop/round-67-$stem.json" &
done
wait
python3 evals/bench/merge.py evals/snapshots/loop/round-67-*.json \
  --out evals/snapshots/loop/round-67.json
```

Six cases, two arms, ten reps: 120 runs and **600 calls**, because every case
here is five turns. The shard boundary is the stem, so both families and both
arms of every contrast are generated inside one process, interleaved — the split
is across contrasts, never inside one. `--concurrency 3` is declared on all
three per [#120], and three shards is inside [#255]'s ceiling of four.
`--turn-delivery plugin` because this is a claim about the product and the
cluster's whole multi-turn instrument reverses under `repeat` — see
[`turn-delivery.md`](turn-delivery.md).

Scored by `python3 evals/pilot/score_register.py <snapshot> 67 work`. That is
the register pilot's scorer with the treatment family parameterised rather than
a copy of it: the two pilots differ only in which family sits on the right-hand
side of every table, and a copy would be a second place for the permutation, the
stratification and the broken-interaction note to drift apart. Its default is
still `register`, and every figure published in
[`register-inheritance-136.md`](register-inheritance-136.md) reproduces from the
stored snapshot under the command that produced it — verified before this
registration was committed.

## What this round cannot establish

**It does not identify a mechanism.** Moving the deliverable into the file
changes more than prose volume: it creates a diff, it completes a task, and it
leaves the model's own text in the workspace rather than only in the
conversation. With no third arm, a movement is the effect of required work and
not of any one component of it.

**The model's prior output lands in the fixture.** On `work-*` the model appends
its own analysis to the file the graded turn is answered from, and on `deep-*`
the same analysis sits in the conversation instead. That is a real difference
between the families beyond the one being manipulated, it is inherent to what
"a session that does work" means, and it is disclosed here rather than defended.
None of the three appended headings is the graded turn's question.

**One batch, one date, three stems, ten reps.** The two within-arm contrasts are
generated in one interleaved pass so era cancels between them, which is what
[round 37](round-37.md) requires; nothing here replicates across days.

**No rule edit is proposed, as registered.** The triple stays in `evals/pilot`.
Promoting it to `evals/cases/` moves `cases_cksum` for every future round and
needs a seeded baseline, and that decision belongs to the rule edit that wants to
be scored on it.

---

# Results

*Nothing above this line has been computed. Nothing below it had been computed
when the commit carrying this file was made.*

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#255]: https://github.com/JordanMPDS/laconic/issues/255
