# Round 100: point back at material already given, decided on opus (#298)

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 68, 69, 89 and 97, which are merged. This file, the
edit, the regenerated `rules/dist/*.md` and the two scorer flags it uses are
committed in one commit before any generation.

`bash tools/candidate-due.sh` exited 1 at registration: rounds 98 and 99 both
measured, so round 100 has to carry a rule edit, under **The edit** below.
`bash tools/release-due.sh` exited 0.

**This edit runs unconditionally.** Rounds 89 and 99 each registered a
candidate behind a fire-rate precheck, the precheck did not fire, and the
withdrawn edit left the round recorded as measuring. Every open `rules` issue
read zero in the last week (rounds 88 to 99), so a third precheck would very
likely do the same and leave the cap broken twice. This round generates the
edit whatever the control side shows, and accepts or rejects on the bars below.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_reexplain.py --told fullexplain $OUT/round-100-{control,edit}.json 100
python3 evals/pilot/score_claims.py --register-family fullexplain $OUT/round-100-{control,edit}.json 100
python3 evals/bench/release.py $OUT/round-100-{control,edit}.json
```

## Why this round exists, and why this issue

[#298] is an Opus 5 report at level `full`: late in an analytical session a
seven-word *"what is <metric A> and <metric B>?"* got 342 prose words, 70% of
them restating rationale the session had already delivered. Two earlier
rounds put a sentence into the never-cut explain bullet and found nothing to
remove, because their instrument had one prior turn and the already-told
answer was already short:

| round | model | instrument | told / cold |
|---|---|---|--:|
| [68](round-68.md) | sonnet | `reexplain-*` against `explain-*` | 0.415 |
| [89](round-89.md) | opus | the same, precheck only | 0.500 |

[Round 69](round-69.md) found the shape the report actually had. On sonnet the
told answer rose 1.83x (27.0 to 49.5 laconic words) when the three prior turns
were written at length on explicit request, which is `fullexplain-*`; depth on
its own moved it 1.13x. No round has run `fullexplain-*` on opus, the observed
model, and none has tested an edit on it.

[Round 97](round-97.md) then accepted, on opus, the level-`full` bullet that a
narrowing follow-up gives items it already listed a back-reference rather than
their names again. #298 is the same move for prose rather than for a list, and
the accepted bullet is evidence opus follows a back-reference instruction
without dropping what the user asked for.

## The edit

A new bullet in `## Level: full`, directly after round 97's:

```diff
   - Right: "The same six failing tests, unchanged, plus `auth_retry`, which
     broke since. `flaky_dns` stays quarantined."
+- A question whose answer would restate material you already gave this
+  session gets the part that is new; for the rest, point back to the earlier
+  answer rather than restating it.
```

It differs from rounds 68 and 89 in two ways:

1. **Placement.** It sits in `level: full`, not in the never-cut explain
   bullet, so the protection for a requested explanation is untouched and the
   new sentence inherits `full`'s limits rather than qualifying a never-cut
   item. It also does not reach `lite`.
2. **Trigger.** It fires on the *answer* restating delivered material, not on
   the *subject* having been explained. In #298 the definitions were new and
   the rationale was not; "something you already explained" would read the
   definitions as unexplained and find nothing to cut.

No `Wrong:`/`Right:` pair. Round 97's pair disambiguated a list transform;
this action is already concrete, and a `Wrong:` example would put a specimen
of re-explanation into the file ([#164]). Since no form is demonstrated, no
cells are pre-registered under #164 item 2; the spillover screen below covers
the closed questions an over-applied pointer would most likely reach.

## Design

Two trees generating simultaneously, per [round 38](round-38.md): control from
a worktree at master (`rules_cksum` 3660436060, as released in 0.3.4), the edit
from this branch. Laconic arm, level `full`, opus, `--turn-delivery plugin`, 20
reps per stem on `fullexplain-{index,metric,rollback}` (five turns) and
`explain-{index,metric,rollback}` (one turn): 120 runs and 360 generation calls
a side, 720 in all. Each side runs as two shards by `--rep-offset`, four
processes at `--concurrency 4`, inside [#255]'s ceiling.

```sh
CELLS='explain-index:opus,explain-metric:opus,explain-rollback:opus,fullexplain-index:opus,fullexplain-metric:opus,fullexplain-rollback:opus'
for side in control edit; do for off in 0 10; do
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$CELLS" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-100-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-100-$side-shard{0,10}.json --out $OUT/round-100-$side.json
```

### The bars

1. **Primary, opus.** Prose words on the graded turn, laconic, as a log-scale
   difference of differences
   `(fullexplain_edit − fullexplain_control) − (explain_edit − explain_control)`,
   aligned-residual permutation (`interaction_corrected`), seed 100,
   two-sided, alpha 0.05. Registered direction: negative. `explain-*` is the
   placebo: a cold question has nothing already given to point back to, so an
   edit that shortens both equally is general brevity, not this rule.
2. **Bound, fatal: fixture-token coverage over `fullexplain-*` turns 2 to 4
   may not fall**, edit against control, stem-stratified, one-sided, alpha
   0.05, by `score_claims.py`. Those turns ask in so many words for the full
   form, and an answer that points back to turn 1 instead drops fixture
   tokens. This is the bound [round 80](round-80.md) died on.
   **2b. Bound, fatal: prose words over the same turns may not fall below
   0.85 of control's**, stem-stratified ratio as printed, a point floor with
   no test. Coverage cannot see a paraphrase that keeps the tokens and loses
   the argument; length can.
3. **Bound, fatal: `date_trunc`** kept on the `index` stem's graded turn, both
   families, as rounds 68 and 89 had it.
4. **Falsifier, fatal: judged quality on the `fullexplain-*` graded turn**, by
   the panel, may not fall, one-sided Fisher, alpha 0.05. Bought only if bars
   1 to 3 pass.

One look, declared here. Disclosed, deciding nothing: the control side's
told/cold ratio (whether the fixture had headroom on opus at all), the
per-stem cells (three cannot reach alpha), the raw-token format check,
`panel_agreement.py`, `release.py`.

**Spillover screen, bought only if bars 1 to 4 pass**, as round 97 registered
it: `recall-index`, `wide-index` and `deep-index`, opus, 10 reps a side from
both trees, `--turn-delivery plugin`; panel quality may not fall, one-sided
Fisher on the pooled count, alpha 0.05, fatal. "Point back" is the likeliest
thing in this edit to license [#353]'s bare answer to a closed follow-up.

**Replication, bought only if everything above passes**: a fresh 120 runs a
side on the same cells from the same two trees, scored on bars 1 and 4 at the
same alphas. Then step 9's holdout: all six reserved cases, opus, 10 reps,
both trees; no reserved case worse at p < 0.05, directions only.

**Accept** needs every bar above to pass or hold, and only then does the PR
merge with the edit in it. Anything else rejects and reverts
`rules/laconic.md` and `rules/dist/` before the merge.

### What each outcome sends next

- **Bar 1 fails with the control's told/cold ratio under 1:** opus does not
  inflate the told answer even after long prior turns, the fixture had no
  headroom, and #298 has now been read on every instrument this repository
  has. No further candidate is registered on it until a new case reproduces
  the report.
- **Bar 1 fails with the ratio over 1:** the harm exists and the sentence
  does not reach it; a `Right:` example is the next lever.
- **Bar 2 or 2b fails:** the pointer reaches requested full answers, and the
  next candidate scopes it to a question that does not ask for the full form.
- **Bar 4 or the screen fails:** the pointer costs the answer its content,
  and the edit is withdrawn from this issue.

## Pre-mortem, registered

The likeliest outcome is **bar 1 failing on headroom**, the same way rounds
68 and 89 did. On sonnet the `fullexplain-*` told answer read 49.5 words in
round 69 and the cold `explain-*` answer 98.0 in round 89, so across those two
dates the told answer was already about half the cold one, and the `metric`
stem's told answer was 13 words. If opus behaves the same there
is little for a pointer to remove, and the difference of differences cannot
separate. That is the point estimate moving with the registered direction and
not separating. If bar 1 does pass, the likeliest failure is bar 2b: a model
that reads "point back rather than restating" at turn 3 shortens a requested
step-by-step walkthrough to a reference to turn 1, which is a fatal bound
rejecting an edit whose target passed.

## Where the ideas came from

The bullet's trigger, firing on the answer restating material rather than on
the subject having been explained, and its wording are Kimi's, through
`tools/consult.sh`; my draft said "a question about something you already
explained", which Kimi and DeepSeek both read as finding nothing to cut in
#298's own case. Leaving out an example pair was both targets' advice. Bar 2b,
a length floor beside the coverage bound, is DeepSeek's; keeping coverage as
the fatal test rather than replacing it is Kimi's. Disclosing the control's
told/cold ratio as the headroom check is Kimi's. Codex did not answer within
its timeout.

[#164]: https://github.com/JordanMPDS/laconic/issues/164
[#255]: https://github.com/JordanMPDS/laconic/issues/255
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#353]: https://github.com/JordanMPDS/laconic/issues/353

## Results

<!-- Nothing above this line has been computed. -->

## Result: rejected on bar 1, for want of headroom, and on bar 2

**Reject, labelled `noise-floor`.** Bar 1 did not separate and pointed the
wrong way, and bar 2's fatal coverage bound failed as well. The bullet is
reverted from `rules/laconic.md` and `rules/dist/` in this PR, so master's
rules are unchanged at `rules_cksum` 3660436060.

240 runs, 0 failed, `cases_cksum` 3178833469 on both sides; `rules_cksum`
3660436060 on every control and 2672697832 on every edit. The first pass
stopped at a usage limit at 18:57 UTC with about half of each shard written,
and the same four commands resumed by key from 21:56, after the control
worktree had been recreated at `ec281f2`. The resume crossed a CLI release:
control 44 runs on 2.1.287 and 76 on 2.1.288, edit 47 and 73. `release.py`
finds no unreadable span and no imbalance (p = 0.790). `merge.py`
reconstructs 2 in flight per side from the timestamps against the declared
4. The panel was not run, because bar 4 is bought only if bars 1 to 3 pass.

### Bars 1 to 3

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. graded-turn prose words, log difference of differences (aligned residuals) | | ratio of ratios 1.015 | 0.863 (two-sided) | **fails** |
| &nbsp;&nbsp;`fullexplain-*` median | 53.0 | 55.0 | 0.504 | |
| &nbsp;&nbsp;`explain-*` median | 140.5 | 141.0 | 0.859 | |
| 2. fixture-token coverage, turns 2 to 4, stem-stratified | | ratio 0.948 | 0.021 (one-sided) | **fails, fatal** |
| 2b. prose words, turns 2 to 4, stem-stratified | | ratio 1.009 | floor 0.85 | holds |
| 3. `date_trunc` kept on the `index` graded turn | 40/40 | 40/40 | | holds |
| 4. panel quality, `fullexplain-*` graded turn | | | | not bought |

Per stem, as disclosed:

| stem | `explain` c / e | `fullexplain` c / e | log DiD | coverage c / e (of) |
|---|--:|--:|--:|--:|
| `index` | 128.0 / 117.0 | 48.5 / 51.0 | 0.140 | 17.0 / 16.0 (37) |
| `metric` | 119.5 / 133.5 | 39.5 / 36.5 | -0.190 | 16.0 / 14.5 (24) |
| `rollback` | 204.0 / 197.5 | 75.5 / 84.0 | 0.139 | 24.0 / 24.0 (30) |

One of three cells is negative, sign test p = 1.000. The raw-token format
check moves with the prose count (`fullexplain` 69.0 against 66.0 raw tokens),
so nothing here is markup.

**Opus has no headroom on this instrument.** The control's told answer is
0.377 of the cold one, 53.0 against 140.5 prose words, p < 0.0001. After three
turns written at length on request, opus already answers the definition
question in about a third of the words it uses cold. That is the same
direction as rounds 68 (0.415) and 89 (0.500), and further from #298's
report than either. There is little left for a pointer to remove, and the
edit removed none of it. The pre-mortem's likeliest outcome is what happened.

**Bar 2 fails on its own, and it is the cost the registration priced.** On
the turns that ask for the full form the edit covers about 5% fewer fixture
tokens, one-sided p = 0.021, from `index` and `metric`, while their prose
length did not fall (bar 2b holds at 1.009). The pointer reaches requested
full answers as a paraphrase that drops named fixture items rather than as a
shortening, which is the case bar 2 was registered beside 2b to catch.

The `score_claims.py` sections reading the licence ratio against `deep-*`
print `nan`: this round generated no `deep-*` family, and those bounds were
not registered here.

### What this sends next

Both registered branches apply. Bar 1 failed with the control ratio under 1,
so **#298 has now been read on every instrument this repository has**
(`reexplain-*` on sonnet and opus, `fullexplain-*` on sonnet and now opus), and
no further candidate is registered on it until a new case reproduces the
report's told answer running longer than its cold one. Bar 2 failed too, so
any later candidate has to scope the pointer away from a turn that asks for
the full form.

The control worktree was removed once the round was scored. The four shard
files were merged and are not committed; `metadata.shards` in each merged
snapshot records them.
