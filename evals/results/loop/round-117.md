# Round 117: does a co-active "Need full X? Say so." bring the offers back? (#113)

**Registration. Nothing below the results line has been computed**, except
the archive passes quoted in **The detector** below, which read stored runs
and bought no generation. This file, the `build-*` pilot cases, the widened
`metrics.closing_offers`, `score_invite.py` and the layout test are committed
before any generation. The edit under **The edit** is registered here and is
applied only if stage 1 fires, in a commit before stage 2.

**This round proposes no rule edit.** Added after stage 1 did not fire, as
the registration below said it would be: the edit under **The edit** was
withdrawn unrun, so the round is recorded as measuring and round 118 owes a
candidate.

`bash tools/candidate-due.sh` exited 0 at registration: round 116 tested a
candidate, so this round may measure. It carries an edit anyway, behind a
stage-1 precheck. If the precheck does not fire, the edit is withdrawn unrun
and the round is recorded as measuring, so round 118 owes a candidate.
`bash tools/release-due.sh` exited 0: v0.3.8 is tagged and current.

## Why this round exists

[#113] reports `lite`'s *"No closing offers and no offers to do more work"*
breaking on one turn of a long editing session at `full`: *"Want me to write
the schema, or add a note to the spec?"* Every screen since has read laconic
at or near zero on opus. `edit-service`, built for this report, reads 0 of 20
on turn 3 in [round 91](round-91.md) (CLI 2.1.287) and in
[round 109](round-109.md) (2.1.301), and 0 of those 40 runs carries an offer
on any turn.

Every one of those screens ran laconic alone. The same reporter ran ponytail
4.8.4 at `full` beside laconic in the sessions behind [#46] (filed 2026-08-06)
and [#298] (2026-09-15). #113 was filed between them, on 2026-08-20, and says
nothing either way. Ponytail's SessionStart text prescribes the shape laconic
bans:

> Complex request? Ship the lazy version and question it in the same
> response, "Did X; Y covers it. Need full X? Say so."

[Round 101](round-101.md) built the `laconic-ponytail` arm for #46, and
rounds 101, 103 and 115 generated 410 turn-responses under it on opus. None
carries an offer, but every one answers a design or explain question, which
has no lazy version to ship. No ponytail run has been asked to build anything.

## The detector

**`metrics.closing_offers` could not see ponytail's shape.** "Did X; Y covers
it. Need full X? Say so." matched nothing, and neither did "say the word"
without a preceding "just". The pattern now also matches "say the word" on its
own, a question followed by "Say so", and "If you want ..., tell me" or "let me
know". A "say the word" followed by "and I'll run it", "go ahead", "proceed" or
"execute" is left out, because there it asks to confirm the action the user
requested, which the rules carve out.

Over the archive's 80,030 distinct non-holdout responses the widened pattern
catches 79 more and loses none. **30 drawn at seed 117 and read by hand were
30 of 30 genuine offers to do more work.** 48 of the 79 are on the `laconic`
arm, nearly all *"say the word if you want it implemented"* on `design-*` and
`cold-service`, sonnet. With "Want me to...?" quoted as banned, the arm reached
for a closer the rule does not quote. At today's rules the same pattern finds
nothing new on opus. The #113 families barely move: laconic `drift-service`
stays 0 of 1,529 distinct turn-responses, `edit-service` 10 of 3,499. Details
are in [`closing-offers.md`](closing-offers.md); `tests/test_metrics.py` pins
the three new shapes and the two confusables.

The detector is disclosure and ranked policy, never a gate, so no stored
verdict and no gate moves.

## The instrument: `build-*`

`build-cache`, `build-retry` and `build-rate-limit` are `design-cache`,
`design-retry` and `design-rate-limit` with "Don't edit anything." replaced by
"Go ahead and make the change.", the manipulation that made `edit-service` from
`drift-service`. The fixture is the design case's, by symlink, and the trap is
byte for byte the same: an implementation passes it the same way an answer
describing one does. Each request has a lazy version and a full one, which is
where ponytail's invitation would go. `tests/test_evals_layout.sh` holds the
family to that.

`score_invite.py` reads, per run, an offer (`closing_offers`); a change to
the workspace (the recorded artifacts, or an `Edit`, `Write`, `MultiEdit` or
`NotebookEdit` call, amended as **Results** says); and a statement of what the
answer left out (`OMIT`, first person or sentence-initial: "Skipped Redis, add
it when...", "I didn't add backoff", "Out of scope:"). On the 200 stored opus
`edit-service` turns, `OMIT` finds one, and it is genuine. Every offer and
every `OMIT` hit is printed so it can be read by hand.

## Stage 1: does it fire? (60 build calls, about 50 session turn calls)

Master rules (`rules_cksum` 529118877), opus, CLI 2.1.309, arms
`laconic-ponytail` and `laconic` interleaved in one pass over `build-*` at
10 reps, and `laconic-ponytail` on `edit-service` at 10 reps, plugin
delivery, disclosed only. Four shards.

```sh
OUT=evals/snapshots/loop
for off in 0 5; do
  python3 evals/bench/run.py --arms laconic-ponytail,laconic --models opus \
    --cases-dir evals/pilot --cases 'build-*' --reps 5 --rep-offset $off \
    --concurrency 4 --snapshot $OUT/round-117-precheck-$off.json &
  python3 evals/bench/run.py --arms laconic-ponytail --models opus \
    --cases-dir evals/pilot --cases edit-service --turn-delivery plugin \
    --reps 5 --rep-offset $off --concurrency 4 \
    --snapshot $OUT/round-117-session-$off.json &
done
wait
python3 evals/bench/merge.py $OUT/round-117-precheck-{0,5}.json --out $OUT/round-117-precheck.json
python3 evals/bench/merge.py $OUT/round-117-session-{0,5}.json --out $OUT/round-117-session.json
python3 evals/pilot/score_invite.py --precheck $OUT/round-117-precheck.json $OUT/round-117-session.json
python3 evals/bench/release.py $OUT/round-117-precheck.json $OUT/round-117-session.json
```

| outcome | condition | what happens |
|---|---|---|
| fires | `laconic-ponytail` `build-*` runs with an offer at least 9 of 30 | stage 2 runs under `laconic-ponytail` |
| fires without ponytail | `laconic` `build-*` at least 9 of 30, whatever the other arm reads | the defect needs no second plugin; stage 2 runs under `laconic`, the shipped arm |
| does not fire | neither | the edit is withdrawn unrun, the round is recorded as measuring, and #113 gets the reading |

9 of 30 is a 30% rate. Stage 2 at 90 a side then has power of at least 0.90
against an edit that cuts the rate to a quarter, for any control rate from
20% up (2,000 simulations under the primary's own test and margin).

**`OMIT` is read by hand on stage 1's answers before stage 2 is bought.** If
fewer than 80% of its hits there say what the answer left out, its bound
below is disclosed rather than fatal.

## The edit

Registered now, applied only if stage 1 fires:

```diff
 - No closing offers and no offers to do more work: no "Let me know if...",
-  "Hope this helps", "Want me to...?". Asking the user to confirm a destructive
-  action is never a closing offer; offering to go read something for them is.
+  "Hope this helps", "Want me to...?", "Need the full version? Say so.". Saying
+  what you left out is not an offer; inviting the user to ask for it is.
+  Asking the user to confirm a destructive action is never a closing offer;
+  offering to go read something for them is.
```

**Hypothesis:** this edit lowers the rate at which `build-*` answers on opus
carry an offer, under the arm stage 1 names, without lowering the rate at
which they write a file, the rate at which they say what they left out, the
panel's pass rate on `build-*`, or `destructive`'s never-cut keywords and
panel pass rate.

It quotes the shape and does not name the plugin: the behaviour is the
model's, ponytail rephrases between releases, and laconic's own arm produced
the unquoted closer 48 times in the archive.

## Stage 2, only if stage 1 fires (180 build calls, 40 destructive calls)

Two trees generating simultaneously: the control from a worktree at the
registration commit, the edit from this branch with the edit committed and
`rules/dist/` regenerated. `$ARM` is the arm stage 1 named. `build-*` at
30 reps a stem (90 a side) and `destructive` at 10, opus, two shards a side.

```sh
OUT=$PWD/evals/snapshots/loop      # the main tree's, from either tree
P="--arms $ARM --models opus --concurrency 4"
for side in control edit; do
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases-dir evals/pilot --cases 'build-*' \
      --reps 15 --snapshot $OUT/round-117-$side-0.json ) &
  ( cd <tree for $side> &&
    python3 evals/bench/run.py $P --cases-dir evals/pilot --cases 'build-*' \
      --reps 15 --rep-offset 15 --snapshot $OUT/round-117-$side-15.json &&
    python3 evals/bench/run.py $P --cases destructive --reps 10 \
      --snapshot $OUT/round-117-$side-destructive.json ) &
done
wait
for side in control edit; do
  python3 evals/bench/merge.py $OUT/round-117-$side-{0,15}.json \
    --out $OUT/round-117-$side.json
  python3 evals/bench/judge.py --results $OUT/round-117-$side.json \
    --cases-dir evals/pilot --cases 'build-*' --jobs 2 \
    --out $OUT/round-117-$side-judgments.json
  python3 evals/bench/judge.py --results $OUT/round-117-$side-destructive.json \
    --jobs 2 --out $OUT/round-117-$side-destructive-judgments.json
done
python3 evals/pilot/score_invite.py $OUT/round-117-{control,edit}.json \
  $OUT/round-117-{control,edit}-judgments.json \
  $OUT/round-117-{control,edit}-destructive.json \
  $OUT/round-117-{control,edit}-destructive-judgments.json
python3 evals/bench/release.py $OUT/round-117-{control,edit}*.json
python3 evals/bench/panel_agreement.py $OUT/round-117-{control,edit}-judgments.json
```

## The bars

1. **Primary: `build-*` answers carrying an offer fall**, opus, pooled
   one-sided Fisher, alpha 0.05, **and the edit's rate is at most half the
   control's**, round 116's margin.
2. **Bounds, fatal**, each a one-sided Fisher for a fall at alpha 0.05,
   uncorrected per `AGENTS.md`:
   - `build-*` answers that write a file, pooled: the build is still done.
   - `build-*` answers that say what they left out, pooled, unless stage 1's
     hand read demoted it.
   - the panel's pass rate on `build-*`, pooled: no silent under-building.
   - `destructive` answers keeping every never-cut keyword, and the panel's
     pass rate on `destructive`: the edit sits beside the carve-out for
     confirming a destructive action.

One look, declared here. **Disclosed, deciding nothing:** every offer and
`OMIT` hit verbatim, median prose words, cost, `panel_agreement.py` and
`release.py`.

**The buying order stops at the first failure.** If bar 1 fails, no judging
is bought, as in round 116.

**Replication, bought only if both bars pass:** a fresh 90 a side and
`destructive` at 10 from the same two trees (`build-*` reps 30 to 59,
`destructive` reps 10 to 19, into `round-117-rep-*`), scored on the same bars.
**Then step 9's holdout:** all six reserved cases, sonnet and opus, 5 reps,
both trees, arm `laconic` (the shipped default, which every user without a
second plugin runs), judged; no reserved case worse at p < 0.05, directions
only.

**Accept** needs bar 1 to pass and bar 2 to hold, twice, and the holdout.
Anything else rejects, and `rules/laconic.md` and `rules/dist/` are reverted
before the merge. The detector, the cases and the scorer merge either way.

## Where the design came from

`tools/consult.sh` asked Codex, DeepSeek and Kimi about a design that
screened `edit-service` alone; DeepSeek did not answer.

- **Kimi and Codex** both said `edit-service` is the wrong place to look:
  its edit turns grant an agreed change and leave no lazy-or-full fork for
  "Need full X?" to sit in. Kimi proposed a single-turn, underdetermined build
  request as the precheck. Adopted as `build-*`, with `edit-service` kept as a
  disclosed reading of #113's own shape.
- **Both** proposed keeping the rule general and quoting the shape rather
  than naming the plugin, which the edit does.
- **Both** proposed a bound on saying what was left out, so "don't invite"
  cannot bleed into "don't mention", and Kimi asked that it be validated before
  it gates. Adopted as the `OMIT` bound and its stage-1 hand read.
- **Codex** proposed a bound on silent under-building. Adopted as the panel's
  pass rate on `build-*`, which grades the fixture-derived trap the design
  cases already discriminate on.
- **Kimi** proposed hand-validating the widened detector before it gates, and
  running `destructive` under the stage-2 arm rather than plain laconic. Both
  adopted. Kimi's warning that a 15% fire bar leaves stage 2 unable to confirm
  is why the bar is 30% and stage 2's size is simulated above.

## Pre-mortem, registered

I expect stage 1 not to fire. Laconic's offer rate on opus has read zero for
a month, the 410 stored ponytail turns are clean, and laconic's ban comes
first in the session, so ponytail's "Need full X? Say so." most likely loses
to it. If it fires and the round rejects, the likeliest way is the point
estimate moving and missing the margin, because "Saying what you left out is
not an offer" may also be read as permission to keep the invitation inside a
statement ("Skipped Redis; add it when you need it"), which no longer matches.
A fatal `OMIT` fall is second: "inviting the user to ask for it" may be read as
a ban on mentioning what was skipped.

## Results

<!-- Nothing above this line has been computed, except the archive passes
quoted under The detector, as the preamble says. -->

### Stage 1: it does not fire

70 runs, 0 failed, every one on CLI 2.1.309, in four shards from 06:48 to
07:20 UTC on 2026-10-23, at master rules (`rules_cksum` 529118877).
`release.py` finds no release boundary.

```
## Stage 1: does #113 fire on opus with ponytail co-active?
   build-cache      laconic-ponytail n 10  offers  0  writes 10  says what it left out  7  median words  217.0  $1.54
   build-cache      laconic          n 10  offers  0  writes 10  says what it left out  1  median words  249.0  $1.68
   build-retry      laconic-ponytail n 10  offers  0  writes 10  says what it left out  0  median words  250.5  $3.15
   build-retry      laconic          n 10  offers  0  writes 10  says what it left out  2  median words  286.5  $3.16
   build-rate-limit laconic-ponytail n 10  offers  0  writes 10  says what it left out  4  median words  224.5  $2.23
   build-rate-limit laconic          n 10  offers  0  writes 10  says what it left out  0  median words  251.0  $1.73
   laconic-ponytail 0 of 30 (fires at 9), laconic 0 of 30 (needs no ponytail at 9)
## Disclosed: edit-service, every turn, laconic-ponytail (decides nothing)
   runs 10  with an offer on any turn 0  on turn 3 0
## does not fire
```

**No answer on either arm offers more work, under the widened detector.**
Every one of the 60 build answers changed the fixture, and none of the 50
`edit-service` turn-responses under `laconic-ponytail` carries an offer, on
turn 3 or any other. `edit-service` on opus now reads 0 of 50 runs with an
offer on any turn: 40 under laconic alone in rounds 91 and 109, read again
here with the widened detector, and 10 with ponytail beside it.

**Ponytail's text does reach the answer, on the half that does not conflict
with laconic.** Its *"what was skipped, when to add it"* shows up in 11 of 30
`laconic-ponytail` answers against 3 of 30 `laconic` ones (two-sided Fisher
p = 0.030): *"Skipped: different limits for each plan, using the `plan`
column."*, *"I skipped an in-app cache such as Redis or an in-memory LRU. Add
one only if..."*. The *"Need full X? Say so."* that would follow it never
does. Where the two plugins agree the answer carries both, and where they
conflict laconic's ban wins.

Disclosed, deciding nothing: `laconic-ponytail` build answers are shorter, a
mean stem-median shift of -31.5 prose words (217.0 against 249.0, 250.5 against
286.5, 224.5 against 251.0; stem-stratified permutation, two-sided,
p = 0.0005, seed 117). `edit-service` cost $20.24 for its 50 turns.

**`OMIT` was read by hand: all 14 hits say what the answer left out.** One
amendment to the scorer, made before any bar read it: opus changed files
through `Bash` heredocs in three of the first 20 runs, with no `Edit` or
`Write` call, so a write is now read from the recorded artifacts as well as
the tool names. No stage-1 decision reads writes.

## Result: the precheck does not fire, and the edit was withdrawn unrun

The pre-mortem's expectation held. `rules/laconic.md` and `rules/dist/` are
unchanged. The widened detector, the `build-*` cases and `score_invite.py`
merge. This is [#113]'s third null on opus, after rounds 91 and 109, and the
first with the second plugin its reporter ran.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#298]: https://github.com/JordanMPDS/laconic/issues/298
