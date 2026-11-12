# Round 136: a feasibility question gets the verdict and what decides it (#113)

**Registration. Nothing below the results line has been computed**, except
the figures quoted from earlier rounds and the sizing look below, which ran
at master rules before the edit was committed. This file is committed first,
with `plugin/rules/laconic.md` at master, so the control worktree is that
commit; the edit, the regenerated `plugin/rules/dist/*.md` and the slice
budget are committed after it. Both commits precede any stage-2 generation.

`bash tools/candidate-due.sh` exited 1 at registration: round 135 proposed no
rule edit, so this round has to carry one, and does, under **The edit**
below. `bash tools/release-due.sh` exited 0: v0.9.0, which ships round 134's
sentence, is tagged and current.

Decided on **opus**: [#113] was observed on Opus at level `full`.

## Why this round exists

[#113] reports two feasibility questions about a storage backend, *"is it
possible to test on X?"* and *"what about on Y instead?"*, answered at about
600 words each at `full`, and proposes, as its item C, that *"'Is it possible
to X?' is answerable as a verdict plus the constraint that decides it."*
[Round 125](round-125.md) tested item C's list-of-findings half and left the
feasibility shape open. [Round 131](round-131.md) measured that shape on opus
and found it does not fire in the co-authoring session the report came from:
0 of 30 sessions reached three times a frozen reference answer. It found the
length one place, which its result section names and leaves untested: the
same turn-3 question asked cold, with no session before it.

| stem | reference | in session, median | cold, median |
|---|--:|--:|--:|
| `replay` | 82 | 103.0 | 195.0 |
| `shadow` | 65 | 116.5 | 170.0 |
| `state` | 60 | 103.5 | 210.0 |

Prose words, opus, `rules_cksum` 1610267591, CLI 2.1.319, 10 sessions and 5
cold answers a stem. The cold `shadow` and `state` answers carried a median 3
and 4 bold labels where no session answer carried any, and all five cold
`state` answers reached three times the reference. The median one is a
bolded three-item list of reasons that closes on an alternative nobody asked
for (*"you could store it in the cycle record"*), which `full` already rules
out in "No unrequested alternatives". The cold question is where the length
shows, so it is where an edit has something to move.

Every other open `rules` issue is behind a precheck its defect no longer
passes ([#46], [#264], [#298], [#353]), or is the zero-behaviour [#438], so
this is the one candidate with a reading that fires.

## Sizing look, at master, before the edit

The rules have moved twice since round 131 measured the cold cells (rounds
132 and 134 rewrote the explanation bullet), and the CLI two releases. A
round this size costs about 3,000 calls, and a target that had stopped firing
would reject on a primary with nothing to move, so 15 calls bought a look
first: `coldfeasible-*`, opus, master (`rules_cksum` 2816272927), 5 answers a
cell, into `round-136-look.json`. The look decided whether to register this
candidate at all, and nothing in the edit below was written after it.

15 runs, 0 failed, CLI 2.1.321, stamped 13:17 to 13:26 UTC on 2026-11-12, one
process, $2.25.
`score_feasible.py` on the look, prose words:

| stem | reference | round 131 cold | look, median | ratio | at 3x or more |
|---|--:|--:|--:|--:|--:|
| `replay` | 82 | 195.0 | 155.0 | 1.89 | 0 of 5 |
| `shadow` | 65 | 170.0 | 148.0 | 2.28 | 0 of 5 |
| `state` | 60 | 210.0 | 201.0 | 3.35 | 4 of 5 |

The cold answers are shorter than round 131's on two stems and still about
twice their references, with a median 2 bold labels on `shadow` and
`state`. A factor of 0.80 would put the medians near 124, 118 and 161, all
still above the references, so the primary has room to move and this
candidate was registered. The look's 15 answers are not part of the round's
control, which is generated beside the edit.

## The instrument

No pilot case or criterion is edited for this round. The cells:

| role | cells | reps a side |
|---|---|--:|
| primary | `coldfeasible-{replay,shadow,state}`/opus | 20 |
| bounds | `coldfeasible-*`/sonnet; `keep-cdc`, `keep-disk`, `keep-checkout`/opus; `walkthrough`/opus | 10 |
| bound | `feasible-{replay,shadow,state}`/opus, the four-turn session | 5 |

- **`coldfeasible-*`** are round 131's cold cases over session-alerting-long's
  2,578-word SPEC.md. Their traps grade the deciding constraint and its
  consequences: `state` fails an answer that drops the integral term and the
  stale count, which is the consequence chain #113 says a fix must not cost.
- **`keep-cdc`** (*"can we fix the reordering by turning off retries in
  wal2queue?"*) and **`keep-disk`** (*"can I get the space back by dropping a
  replication slot?"*) are feasibility questions on other fixtures, written
  for [#384]'s round 108 and never drafted against here. Their right answer is
  conditional: each trap fails "yes without condition" and a "no" on a cause
  the record does not establish. An edit that asks for a verdict is likeliest
  to cost exactly that, so they are bounds rather than targets.
- **`keep-checkout`** (*"should we move checkout to our backup card
  provider?"*) is the same family's decision question, there to see the
  bullet reach a shape it does not name.
- **`walkthrough`**/opus carries a never-cut keyword (`401`), and
  **`feasible-*`** is #113's own session, whose trap grades the last
  question (*"what about Redis instead?"* and its siblings).

`evals/pilot/score_feasible_edit.py` scores every bar below. It is new in
this commit, imports round 131's references from `score_feasible.py`
unchanged, and passes `--selftest`.

## The edit

One bullet appended to `level: full`, after the explanation bullet:

```diff
   description of what they name: say what happens, not which component
   does it.
+- A feasibility question gets the verdict, the constraint that decides it
+  and its consequences, and at most one caveat.
```

- **"A feasibility question"**, a class rather than the literal *"Is it
  possible to X?"* #113 quotes, so that "could we", "can I" and "what about Y
  instead?" are covered by the same words. The neighbouring bullet names its
  shape the same way ("Explaining what you read").
- **"the verdict"** can be conditional: "only if a slot is what holds the
  WAL" is a verdict, and it names the deciding constraint at the same time.
  `keep-disk` and `keep-cdc` are where a flat yes or no would show.
- **"and its consequences"** keeps the failure chain. Round 131's `state`
  reference is "Each five-minute run takes a lease ... so state held in memory
  is gone by the next cycle. The integral term would restart at zero every
  cycle, and the stale count could never reach three": the first sentence is
  the constraint and the second its consequences, and the trap needs both.
- **"at most one caveat"** is the neighbouring bullet's limit, without its
  qualifier, for characters.

**The slice budget rises with it, from 9,500 to 9,700 characters.** The hook's
`ultra` output measured 9,480 before the edit, against the 9,500 that
`tests/test_laconic.sh` enforces, and every `full` bullet reaches `ultra` by
inheritance. Cutting text elsewhere to pay for the bullet would put a second
edit in the treatment, so the budget moves instead, as `AGENTS.md` allows,
and stays 300 under Claude Code's 10,000-character cap. A rejection reverts
the budget with the bullet.

## Hypothesis

> Appending "A feasibility question gets the verdict, the constraint that
> decides it and its consequences, and at most one caveat." to `level: full`
> should move prose words on `coldfeasible-replay`, `coldfeasible-shadow` and
> `coldfeasible-state` on opus **down**, to a factor of 0.80 of the control or
> less, without raising prose words on the three `keep-*`/opus cells, without
> lowering the panel pass rate on any bounds cell or on the `feasible-*`
> sessions, without lowering the share of `coldfeasible-*`/opus answers free
> of readability violations, and without lowering the share of
> `walkthrough`/opus answers carrying `401`.

## Stage 2: the edit on opus

Two trees generating at once ([round 38](round-38.md)): the control from
`/home/jordan/projects/laconic-r136-control` at the registration commit, the
edit from `/home/jordan/projects/laconic-r136-edit` at the edit commit, both
on disk rather than under `/tmp`. Two shards a side, so four `run.py`
processes at most; each side's bounds shard runs its session cells after its
single-turn cells, in the same shell.

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
T='coldfeasible-*:opus'
B='coldfeasible-*:sonnet,keep-cdc:opus,keep-disk:opus,keep-checkout:opus,walkthrough:opus'
S='feasible-*:opus'
common="--arms laconic --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
for side in control edit; do
  ( cd /home/jordan/projects/laconic-r136-$side && python3 evals/bench/run.py \
      $common --reps 20 --cells "$T" --snapshot $OUT/round-136-$side-target.json ) &
  ( cd /home/jordan/projects/laconic-r136-$side && python3 evals/bench/run.py \
      $common --reps 10 --cells "$B" --snapshot $OUT/round-136-$side-bounds.json \
    && python3 evals/bench/run.py \
      $common --reps 5 --cells "$S" --snapshot $OUT/round-136-$side-session.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-136-$side-{target,bounds,session}.json \
      --out $OUT/round-136-$side.json
done
python3 evals/bench/release.py $OUT/round-136-{control,edit}.json
S=evals/pilot/score_feasible_edit.py
python3 $S words $OUT/round-136-{control,edit}.json
python3 $S longer $OUT/round-136-{control,edit}.json
python3 $S readability $OUT/round-136-{control,edit}.json
python3 $S nevercut $OUT/round-136-{control,edit}.json
```

That is 160 opus calls and 30 sonnet calls a side, the 15 sessions counted
at four turns each. **The primary and the three deterministic bounds are
scored before any judging is bought**: if any fails, the round rejects and
nothing is judged. If all pass:

```sh
for side in control edit; do
  python3 evals/bench/judge.py --cases-dir evals/pilot --jobs 2 \
      --results $OUT/round-136-$side.json --out $OUT/round-136-$side-judgments.json
done
python3 $S bounds $OUT/round-136-{control,edit}-judgments.json
python3 evals/bench/panel_agreement.py $OUT/round-136-{control,edit}-judgments.json
```

### The bars

1. **Primary: prose words fall on `coldfeasible-*`/opus.** One-sided
   stratified permutation of the side label within each cell, on median log
   prose words (`score_compression.words`, inline code out); seed 136,
   200,000 resamples, alpha 0.05; **and** the factor, exp of the mean log
   ratio, at 0.80 or less. One look, declared here.
2. **Prose words, fatal:** may not rise on the three `keep-*`/opus cells, the
   same statistic with the sides swapped, one-sided at alpha 0.05.
3. **Readability, fatal:** the share of `coldfeasible-*`/opus answers with no
   `metrics.score` violation may not fall, pooled, one-sided Fisher at alpha
   0.05.
4. **Never-cut keywords, fatal:** `walkthrough`/opus answers carrying `401`,
   one-sided Fisher at alpha 0.05.
5. **Bounds, fatal:** the panel pass rate may not fall on any of the ten
   single-turn cells, each a one-sided Fisher at alpha 0.05, uncorrected, nor
   on the three `feasible-*`/opus cells pooled, whose 15 sessions a side are
   too few for a per-stem test.

**Disclosed, deciding nothing:** per cold cell, the median against round 131's
reference, median bold labels and headings, and closing offers; prose words on
every other cell, and on the session's turns 3 and 4; which `keep-*` answers
give a flat yes or no, read by hand; how many `coldfeasible-state` answers
name both the integral term and the stale count; `release.py` and
`panel_agreement.py`.

**Replication, bought only if the primary passes and every bound holds:** a
fresh sample from the same two trees (`--rep-offset 20` on the target shard,
`--rep-offset 10` on the bounds shard and `--rep-offset 5` on its session
cells, into `round-136-rep-*`), scored on the same bars. **Then step 9's
holdout:** all six reserved cases, sonnet and opus, 5 reps, both trees,
judged with `--cases-dir evals/holdout`, scored with `score_feasible_edit.py
holdout`: no reserved case worse at one-sided p < 0.05. The snapshots are
named `round-136-holdout-{control,edit}.json` so that `report.py`'s wear count
reads them. By the runs in rounds 129, 132 and 134, this is the fourth
consultation of the five cases authored in #566 and the third of
`holdout-scratch`, whose budget is four; all six are within their budgets.

**Accept** needs the primary to pass and every bound to hold, twice, and the
holdout. Anything else rejects, and `plugin/rules/laconic.md`,
`plugin/rules/dist/` and the slice budget are reverted before the merge.

## Origin

The shape is [#113]'s own item C, and the cold cells are where
[round 131](round-131.md) found it. I put a draft to the delegate targets
through `tools/consult.sh`: *'"Is it possible to X?" gets the verdict, the
constraint that decides it, and at most one caveat that changes what to do.'*
Codex and DeepSeek did not answer within 240 seconds; Kimi answered. Adopted
from Kimi: **a class trigger, "a feasibility question"**, in place of the
literal question, so that `keep-disk`'s "can I ..." is reached by the same
words as `coldfeasible-state`'s "is it possible to ...", and in the
neighbouring bullet's idiom; and **"and its consequences"**, because the
draft's three slots left the consequence chain the `state` trap grades in
none of them, and Kimi ranked its loss the likeliest failure. Kimi also
argued for raising the budget rather than cutting text, on the grounds this
section gives. Not adopted: a clause asking for the spec section, since no
trap grades a citation.

## Pre-mortem, registered

The likeliest rejection is the third class on bound 5 at `keep-disk` or
`keep-cdc`: "the verdict" reads as yes or no, opus answers "No: archiving is
failing" or "Yes, drop the slot", and the panel fails the flat verdict the
trap names. The second likeliest is the third class on bound 2: "its
consequences" and "one caveat" ask for slots a `keep-*` answer did not fill
before, and prose words rise there by a few percent while the cold cells
fall. A second-class rejection, the cold cells falling to about 0.85 and
missing the 0.80 bar, would come from opus keeping the bolded list and
trimming each item, which is how round 125's findings cut arrived. I give the
first class little weight: the cold answers ran 2.1 to 3.5 times a complete
reference in round 131, so a rise would have to come from a slot the control
leaves empty.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

### Stage 2

Control from `laconic-r136-control` (`9470e8d`, `rules_cksum` 2816272927,
master), edit from `laconic-r136-edit` (`a45a9c2`, `rules_cksum` 87207730),
four shards at once, 145 records a side (130 single answers and 15 four-turn
sessions), 0 failed, all CLI 2.1.321, stamped 13:29 to 14:12 UTC on
2026-11-12. `release.py`: no unreadable span, no arm imbalanced across a
release. Each merged side declares 4 and reconstructs to 2 in flight.

**Primary: fails.** Mean log ratio −0.023, factor **0.977** against the 0.80
it needed, one-sided **p = 0.310**.

| cell | control median | edit median | edit / reference |
|---|--:|--:|--:|
| `coldfeasible-replay`/opus | 157.5 | 167.5 | 2.04 |
| `coldfeasible-shadow`/opus | 169.5 | 163.0 | 2.51 |
| `coldfeasible-state`/opus | 204.0 | 186.0 | 3.10 |

The control reads within 3 words of the sizing look on `replay` and `state`
and 21.5 above it on `shadow`, so the defect still fired; the edit left it
where it was. Under the registration the round rejects here, and nothing was
judged: no panel call was made, and the holdout was not consulted.

The three deterministic bounds were scored anyway, since they cost nothing,
and all hold. **Prose words on `keep-*`/opus** fell rather than rose, factor
0.915, one-sided p = 0.947 for a rise: medians 147.0, 162.5 and 143.0 on the
control against 132.0, 149.5 and 133.0 on the edit, `keep-cdc`, `keep-disk`
and `keep-checkout` in that order. **Readability:** 60 of 60 clean on both
sides. **Never-cut:** `walkthrough`/opus carries `401` in 10 of 10 on both
sides.

### Disclosed, deciding nothing

- **The edit restructured the cold answer instead of cutting it.** The
  median edit `coldfeasible-state` answer (191 prose words) leads with the
  verdict, "Not as the supervisor is specified", where the control's (208)
  leads with "Yes, as far as `govern()` goes", and then gives the constraint
  and a bolded three-item list of what every tenant loses, plus a paragraph
  on replay. That reads as the bullet obeyed: a verdict, the constraint, and
  its consequences, each consequence written out. "And its consequences", the
  clause adopted to protect the trap, reads as a licence to list every one.
  All 20 `state` answers on each side name both the integral term and the
  stale count.
- **Bold labels fell on two cold cells and stayed on the third.** Medians
  0.5, 2.0 and 3.0 on the control against 0.0, 0.0 and 3.0 on the edit, the
  same order as above. No cold answer on either side carries a heading or a
  closing offer.
- **The session answers got longer.** Turn 3 of `feasible-*`/opus, where
  round 131 found the session answering at about the reference's size, ran
  medians of 96, 89 and 99 prose words on the control against 123, 147 and
  112 on the edit, and 3 of the 15 edit answers carry three bold labels
  against 1 control answer carrying two. Turn 4 moved less (42, 72 and 66
  against 40, 95 and 77). At 5 sessions a stem this is a description rather
  than a test, but it is the opposite of the direction registered for the
  cold cells, on #113's own condition.
- **Sonnet moved more than opus.** `coldfeasible-*`/sonnet medians 138.5,
  162.5 and 184.0 on the control against 111.0, 145.5 and 172.0 on the
  edit, with bold labels at a median 0 on all three edit cells. Sonnet is
  disclosed, not a bar.
- **No flat verdict on the conditional cases.** All 20 `keep-disk` answers
  open on a conditional ("Only if a slot is what's holding the WAL", "Possibly,
  but DISK.md doesn't show that a slot is the cause"). On `keep-cdc` a bare
  "No." opens 1 of 10 control answers and 3 of 10 edit answers, each followed
  by why turning retries off is unsafe rather than by a cause the record does
  not establish.
  Neither was judged.
- **The pre-mortem named the class and overstated the movement.** It ranked
  a second-class rejection third and expected the cold cells near 0.85; they
  reached 0.977. It ranked a `keep-*` length rise second, and `keep-*` fell.
- Generation cost $56.22 for the 290 records, and the sizing look $2.25.

## Result: rejected

The primary failed on both of its conditions, factor 0.977 at p = 0.310, so
the round rejected before any judging. `plugin/rules/laconic.md`,
`plugin/rules/dist/` and the slice budget in `tests/test_laconic.sh` and
`AGENTS.md` are reverted to master in this pull request. On opus, a bullet
naming the feasibility shape and its parts does not shorten the cold answer;
it reorders it around the verdict and keeps every consequence. [#113] stays
open on the cold shape, which this round measured at master again and did not
move.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353
[#384]: https://github.com/JordanMPDS/laconic/issues/384
[#438]: https://github.com/JordanMPDS/laconic/issues/438
