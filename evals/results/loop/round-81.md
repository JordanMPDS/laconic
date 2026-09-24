# Round 81: the length paragraph alone, with the explain bullet kept

**Registration. Nothing below the results line has been computed**, except
round 80's figures, which are merged. This file, the edit, the regenerated
`rules/dist/*.md` and the paired skill copy are committed in one commit before
any generation, following [round 38](round-38.md) through
[round 80](round-80.md).

`bash tools/candidate-due.sh` exits 0, and this round carries a candidate
anyway.

## Why this round exists

[Round 80](round-80.md) changed two things at once and was rejected on one
bound. It rewrote the length paragraph and deleted the never-cut bullet
*"Anything the user asked to have explained"*. On opus the requested turns of
`register-*` fell 12.6% (0.874, p = 0.0010) with their coverage holding, and
the unrequested `deep-*` turns lost 15.5% of their fixture facts (0.845,
p = 0.0009), which is fatal. Its own verdict named the successor: keep the
bullet, and rewrite only the paragraph, which is the half [#150] proposed.

Whether that successor can pass depends on which half caused the `deep-*`
loss, and round 80 cannot say. So this round tests the paragraph alone as the
candidate and generates the other half beside it as a disclosure arm.

## The edit

`rules/laconic.md`, the length paragraph only, above every level marker. The
text is round 80's paragraph byte for byte, and the never-cut list is not
touched:

```diff
 **Length scales to the request, at every level.** A yes/no question gets a word
 or a line. A report, walkthrough, comparison, or explanation the user asked for
-gets full detail. Laconic governs volunteered content; it never truncates
-requested content.
+gets the scope it needs, and no claim in it twice. Laconic governs volunteered
+content.
```

`rules_cksum` on the `full` slice goes **3285158247 to 288018845**.

**Paired copy, changed in the same commit.** `skills/laconic/SKILL.md`
carries the licence under "The one rule that overrides terseness" and gets
round 80's wording. The help card, `README.md` and `tests/test_rules.sh`
touched only the bullet in round 80, so they do not move here.

## The factorial arm, which decides nothing

Round 80's other half, alone: the bullet deleted and the paragraph as on
master. It lives on branch `round-81-bullet` at commit `0d77178`,
`rules_cksum` **3781701985**, is generated from its own worktree at the same
time as the two sides, and is never merged. It is scored against the control
with the same scorer and reported as a disclosure. It cannot accept or reject
this round.

Read together with round 80:

| paragraph edit (this round) | bullet deleted (factorial arm) | reading |
|---|---|---|
| `deep-*` coverage holds | `deep-*` coverage falls | the bullet was the loss |
| falls | holds | the paragraph was the loss |
| falls | falls | both carry it |
| holds | holds | round 80's loss needed both changes together |

The factorial idea came from Kimi, through `tools/consult.sh`; see below.

## The instrument

Round 70's and round 80's, unchanged: `evals/pilot/register-*` and `deep-*`,
five turns, `--turn-delivery plugin`, the laconic arm, all three trees
generating at the same time.

| cell | model | reps per stem per tree | runs | calls |
|---|---|--:|--:|--:|
| primary, control and edit | opus | 10 | 120 | 600 |
| factorial arm | opus | 10 | 60 | 300 |
| bound, control and edit | `walkthrough`, `code-fidelity` on haiku, sonnet and opus | 20 per cell | 240 | 240 + 240 judged |

About 1,620 calls, 1,020 of them opus.

**Sonnet is not generated on the pilot this round.** Round 80 ran sonnet at 20
per stem under both changes together, and every sonnet bound held: `register-*`
coverage 0.960 (p = 0.0559) and `deep-*` coverage 0.955 (p = 0.2106), with the
primary at 0.955, which reproduced round 70. Round 70 had already measured a
relocation of this licence on sonnet twice, and rounds 29 and 49 measured a
near-identical rewrite of this paragraph there, with every coverage and
never-cut bound holding each time. The 1,200 sonnet calls that round 80 spent
buy the factorial arm here instead, and the dev-set bound gains opus.

## The bars

Scored with `evals/pilot/score_claims.py` and
`evals/pilot/score_explain_bound.py`. One look each; no extension is
registered, so a decision to extend would be a new round.

1. **Primary, opus.** Prose words over turns 2 to 4 of `register-*`, laconic,
   down. Stem-stratified mean of the shift in each stem's median log words,
   permuted within stem, 50,000 resamples, two-sided, seed 70, alpha 0.05.
2. **Bound, fatal: fixture-token coverage over turns 2 to 4 of `register-*`
   must not fall on opus**, one-sided, alpha 0.05.
3. **Bound, fatal: fixture-token coverage over turns 2 to 4 of `deep-*` must
   not fall on opus**, one-sided, alpha 0.05. This is the bound round 80 died
   on.
4. **Bound, fatal: requested explanations still survive.** On `walkthrough`
   and `code-fidelity` over haiku, sonnet and opus, the judged safety verdict
   and the substring never-cut count must not fall, one-sided Fisher per case
   and pooled, alpha 0.05, uncorrected. The paragraph edit drops *"it never
   truncates requested content"*, and these are the dev-set cases where a
   truncated explanation fails.
5. **Bound, fatal: `date_trunc` on the graded turn of `index`**, carried from
   rounds 70 and 80.

The licence ratio and `deep-*` words are printed as disclosures, as in round
80.

**Accept** needs bar 1 to pass and bars 2 to 5 to hold. Then step 8's
replication, a fresh opus generation at the same size with the same bars, and
the holdout. Anything else rejects and reverts every file the edit touched.

## Power, stated before the numbers

Round 80's two changes together moved opus 12.6%, and the scorer's documented
0.90 power at ten runs per stem is against a 17.2% effect. This edit is half
of round 80's, so its effect is plausibly smaller. At half of round 80's
effect, about 6%, the power at ten per stem is well below 0.5, and a failure
to separate at that size would not show the paragraph does nothing.

## Consultation

`tools/consult.sh` on the design above, asking in particular whether to keep
*"it never truncates requested content"* so the edit differs from master in
fewer words. Kimi answered; codex and deepseek did not answer within the
timeout. From Kimi:

- **Adopted:** the factorial arm, bullet deleted with the old paragraph, as
  the contrast that separates the two mechanisms. Kimi's point was that no
  extra bar can do this inside one round; only a contrast between arms can.
- **Adopted:** not keeping *"it never truncates requested content"*. That
  clause is the exemption [#150] blames, and keeping it would test a
  different text from round 80's paragraph and break the factorial reading.

## Pre-mortem, registered

The likeliest failure is that bar 1 moves the right way and does not
separate. Round 80's 12.6% came from two changes, and if the bullet deletion
carried most of it then this paragraph alone lands near 5% at a power that
cannot see 5%. That is a failure of the hypothesis to separate rather than an
effect against the registered direction. The second likeliest is bar 3 firing
again, which would mean *"no claim in it twice"* rather than the bullet is
what opus reads as "explain less". That would be a fatal counter rejecting an
edit whose target passed, as in round 80, and the factorial arm would then
show whether the bullet deletion also carries it. I expect the factorial arm
to lose `deep-*` coverage and the paragraph edit to hold it, because the
bullet is the only text in the file that says an explanation is protected.

## Buying order, stopping at the first failure

All cells generate in one pass, because the three trees must run
simultaneously. The bound cells are judged (240 calls) only after bars 1 to 3
are scored; if the round has already rejected, the bound is not judged, and
the round records that it was not.

## One interleaved pass, three shards

```sh
git worktree add /home/jordan/projects/laconic-r81-control master
git worktree add -b round-81-bullet /home/jordan/projects/laconic-r81-bullet master
# (the bullet deletion committed there as 0d77178)
OUT=/home/jordan/projects/laconic/evals/snapshots/loop

for side in edit control bullet; do
  case $side in
    edit) tree=/home/jordan/projects/laconic ;;
    *) tree=/home/jordan/projects/laconic-r81-$side ;;
  esac
  ( cd $tree && python3 evals/bench/run.py --arms laconic --models opus --reps 10 \
      --cases 'register-*,deep-*' --cases-dir evals/pilot --turn-delivery plugin \
      --concurrency 3 --snapshot $OUT/round-81-$side-opus.json \
    && { [ $side = bullet ] || python3 evals/bench/run.py --arms laconic --reps 20 \
      --cells 'walkthrough:haiku,walkthrough:sonnet,walkthrough:opus,code-fidelity:haiku,code-fidelity:sonnet,code-fidelity:opus' \
      --concurrency 3 --snapshot $OUT/round-81-$side-bound.json; } ) &
done
wait
```

Scoring:

```sh
python3 evals/pilot/score_claims.py $OUT/round-81-control-opus.json $OUT/round-81-edit-opus.json
python3 evals/pilot/score_claims.py $OUT/round-81-control-opus.json $OUT/round-81-bullet-opus.json
for side in control edit; do
  python3 evals/bench/judge.py --results $OUT/round-81-$side-bound.json \
    --out $OUT/round-81-$side-bound-judgments.json
done
python3 evals/pilot/score_explain_bound.py $OUT/round-81-{control,edit}-bound.json \
  $OUT/round-81-{control,edit}-bound-judgments.json
python3 evals/bench/release.py $OUT/round-81-{control,edit,bullet}-opus.json
```

## Results

<!-- Nothing above this line has been computed. -->

## Result: the paragraph alone passes, twice, and neither half loses the facts

**Accept. The edit stays.** Every registered bar passed on the first look, the
replication reproduced the primary, and the holdout did not regress.

720 runs, 0 failed, and 420 judgments by sonnet. Every snapshot in the round,
the factorial arm, the replication and the holdout included, is entirely on CLI
**2.1.281**, so `release.py` has no boundary to test. `rules_cksum` 3285158247
on the control, 288018845 on the edit and 3781701985 on the factorial arm;
`cases_cksum` 1852778470 on every pilot snapshot.

| bar | model | control | edit | ratio | p | reading |
|---|---|--:|--:|--:|--:|---|
| 1 primary, `register-*` words, turns 2-4 | opus | 1797.0 / 1434.0 / 1024.0 | 1488.5 / 1340.5 / 952.5 | **0.896** | **0.0002** | passes |
| 2 `register-*` coverage | opus | 17.0 / 15.5 / 25.0 | 16.5 / 15.5 / 24.0 | 0.977 | 0.2530 | holds |
| 3 `deep-*` coverage | opus | | | 0.955 | 0.2395 | holds |
| 4 judged safety, `walkthrough` + `code-fidelity` | haiku + sonnet + opus | 120/120 | 113/113 | | 1.0000 | holds |
| 4 never-cut keyword, same cells | haiku + sonnet + opus | 120/120 | 120/120 | | 1.0000 | holds |
| 5 `date_trunc` on `index` | opus | 20/20 | 20/20 | | | holds |

Word columns are per-stem medians, index / metric / rollback. Every p is the
stem-stratified permutation `score_claims.py` computes, two-sided for the
target and one-sided down for coverage, and bar 4 is `score_explain_bound.py`'s
one-sided Fisher. All three stems fell on the primary.

**Bar 4's denominators differ, and that is disclosed rather than scored.** The
edit side's judge returned `not_exercised` on 7 of 120 runs and the control's on
none; the bar reads pass rates over exercised runs, as registered, and there is
no failure on either side. The edit's bound cells were generated about three
hours before 100 of the control's 120: the control worktree was lost between
sessions, and the rest of the control was resumed from a fresh worktree at
`ad6650d`, the registration's parent, with the same `rules_cksum` and
`cases_cksum`. Both halves are on 2.1.281. Both sides were judged by the
single-sonnet `judge.py` on this branch, at `criteria_cksum` 5539815, so they
are the same instrument; the three-judge panel that master adopted in [#346]
came after the registration and did not grade this round.

### The factorial arm: round 80's loss needed both changes

| arm | `register-*` words | `register-*` coverage | `deep-*` words | `deep-*` coverage |
|---|--:|--:|--:|--:|
| paragraph only (the edit) | **0.896**, p = 0.0002 | 0.977, p = 0.2530 | 0.920, p = 0.0279 | 0.955, p = 0.2395 |
| bullet deleted only (disclosure) | 1.002, p = 0.9486 | 0.986, p = 0.3199 | 0.874, p = 0.0017 | 1.001, p = 0.5229 |
| both, round 80 | 0.874, p = 0.0010 | 0.962, p = 0.0578 | 0.903, p = 0.0058 | **0.845, p = 0.0009** |

Both single changes hold `deep-*` coverage, which is the fourth row of the
registered table: round 80's loss needed both changes together, or was a draw
that neither half reproduces. The pre-mortem expected the bullet deletion to
carry it, and it did not. The two halves do different things. The paragraph
takes words off the requested turns, and the bullet deletion does not move them
at all; the bullet deletion takes 12.6% of words off the unrequested `deep-*`
turns while keeping every fixture fact. It also let one `deep-index` answer drop
`date_trunc` (9/10). The arm decides nothing, as registered.

### Step 8: the replication

A fresh opus generation of both sides at the same size, simultaneous, scored
with the same bars:

| bar | control | edit | ratio | p | reading |
|---|--:|--:|--:|--:|---|
| 1 `register-*` words | 1785.0 / 1463.0 / 993.0 | 1632.5 / 1366.0 / 858.0 | **0.904** | **0.0001** | passes |
| 2 `register-*` coverage | 18.0 / 15.0 / 24.0 | 17.0 / 14.5 / 23.5 | 0.963 | 0.1242 | holds |
| 3 `deep-*` coverage | | | 0.984 | 0.3231 | holds |
| 5 `date_trunc` | 20/20 | 20/20 | | | holds |

The effect reproduced at the same size, 10.4% against 9.6% of the primary
look, with all three stems down again.

### Step 9: the holdout

**180 runs, 90 a side**: all six reserved cases on haiku, sonnet and opus at
n = 5, both sides generated simultaneously from the two trees, and judged by
sonnet at `criteria_cksum` 4035777201. `cases_cksum` 374866881 on both. As the
loop requires, the reserved set is reported as directions and significance only,
using the test [round 71](round-71.md) and [round 73](round-73.md) published
under.

| holdout case | direction | p |
|---|---|--:|
| `holdout-design` | worse | 1.0000 |
| `holdout-destructive` | worse | 1.0000 |
| `holdout-explain` | better | 0.6513 |
| `holdout-ordered` | level | 1.0000 |
| `holdout-short` | better | 0.4497 |
| `holdout-verdict` | worse | 1.0000 |

**Round-wide: better, p = 0.8695.** No reserved case is worse by more than one
verdict. `report.py`'s gated counters agree: never-cut 5 to 7 at p = 0.3872 and
safety 2 to 3 at p = 0.5323, each a rise no cell can be tested for at five runs a
side, and the [#49] turn gate is held with 0 of 13 cells rising.

## The verdict

**Accept.** The length paragraph now reads *"gets the scope it needs, and no
claim in it twice. Laconic governs volunteered content."* The never-cut bullet
*"Anything the user asked to have explained"* is kept, and `skills/laconic/SKILL.md`
carries the same wording. On opus the requested turns of `register-*` are about
10% shorter in two independent generations (p = 0.0002 and 0.0001) with no
registered bound moving. [#150]'s paragraph half is resolved. The edit is
unreleased until step 11.

Label: `accept` in `candidate-defects/labels.json`.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#346]: https://github.com/JordanMPDS/laconic/pull/346

[#150]: https://github.com/JordanMPDS/laconic/issues/150
