# Round 108: the never-cut uncertainty item covers the answer, not a claim nobody asked for (#384)

**Registration. Nothing below the results line has been computed.** This file,
the nine `open-*`, `unsettled-*` and `keep-*` cases, `evals/pilot/score_open.py`
and the layout test are committed before any generation. The edit and the
regenerated `rules/dist/*.md` are committed only if stage 1 fires, and before
stage 2 generates.

`bash tools/candidate-due.sh` exited 0 at registration (round 107 tested a rule
candidate), and `bash tools/release-due.sh` exited 0. This round carries a
rule edit anyway, under **The edit** below, because the maintainer asked for
the next rule item in the backlog.

Reproduce every number below the results line with:

```sh
OUT=evals/snapshots/loop
python3 evals/pilot/score_open.py --precheck $OUT/round-108-precheck.json
python3 evals/pilot/score_open.py $OUT/round-108-{control,edit}.json \
    $OUT/round-108-{control,edit}-judgments.json
python3 evals/bench/release.py $OUT/round-108-{control,edit}.json
```

## Why this round exists

[#384] reports an either/or answer whose second paragraph inferred a cause
inside the option it had just named, which nobody had asked about, and hedged
it: *"The likely cause is `<connector>`'s `<queue>` sink publishing in
parallel or retrying without an ordering key. That's inferred, because we
haven't seen `<colleague>`'s connector configuration."* The report suspects
the never-cut item *"Uncertainty that changes what the user should do."*
licensed it: *"That's inferred" reads as protected uncertainty. The
uncertainty was about the cause, a claim nobody asked for, not about the
answer, which was certain.* Its third direction: *"Scope the never-cut
uncertainty item to the answer itself. A caveat on a claim the response
should not have made is not protected."*

Rounds 105 and 106 took the first direction, which v0.3.6 ships, and round
107 found the second does not fire. No case in this repository has a record
that leaves something open inside the answer, so nothing here can see the
third.

## The instrument

Three new fixtures. Each settles an either/or and leaves the mechanism inside
the winning option unestablished, saying so in one sentence of the narrative
rather than under a heading:

| stem | settled | left open, in passing |
|---|---|---|
| `cdc` | the reordering happens when `wal2queue` publishes to the topic, not in the subscription | why the connector hands changes over late: its sink settings "were not collected for this write-up" |
| `disk` | the volume is filling with `pg_wal`, not application logs | why the server keeps WAL segments: "nothing past this `du` has been run" |
| `checkout` | the p99 regression is in the card-provider call, not the database | what inside the call got slower: no finer spans, and the provider "has not yet answered our support ticket" |

Three families over each fixture, all single-turn and panel-graded:

- **`open-*`, the target.** The settled either/or, `cdc`'s in [#384]'s own
  words. `score_open.OPEN` counts an answer that carries the open question,
  either as a cause inferred inside the option (`INFER`: ordering keys and
  retries; replication slots and archiving; the provider's side and the
  network path) or as the fixture's note that it is unknown. The layout test
  holds every fixture free of `INFER`'s words, so a match is the model's own
  inference.
- **`unsettled-*`, a bound.** An either/or about the open mechanism itself
  ("a stale replication slot, or failing archiving?"). The record cannot
  settle it, so the uncertainty is the answer, and a passing answer says so.
- **`keep-*`, a bound.** Whether a remedy would work ("can I get the space
  back by dropping a replication slot?"). It works only if the open mechanism
  is the one the remedy assumes, so a passing answer makes its advice
  conditional on it or says to establish it first. This is uncertainty that
  changes what the user should do, on a question the user did ask.

## Stage 1: does it fire on opus? (60 generation calls)

Master rules (v0.3.6), the laconic arm, opus, `--turn-delivery plugin`:
`open-*` at 10 reps, and `unsettled-*` and `keep-*` at 5 each to see whether
the bounds have room. Four shards:

```sh
OUT=/home/jordan/projects/laconic/evals/snapshots/loop
O='open-cdc:opus,open-disk:opus,open-checkout:opus'
U='unsettled-cdc:opus,unsettled-disk:opus,unsettled-checkout:opus'
K='keep-cdc:opus,keep-disk:opus,keep-checkout:opus'
for spec in "$O 0 open0" "$O 5 open5" "$U 0 unsettled" "$K 0 keep"; do
  set -- $spec
  python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $2 \
    --cases-dir evals/pilot --cells "$1" --turn-delivery plugin \
    --concurrency 4 --snapshot $OUT/round-108-precheck-$3.json &
done
wait
python3 evals/bench/merge.py $OUT/round-108-precheck-{open0,open5,unsettled,keep}.json \
    --out $OUT/round-108-precheck.json
python3 evals/pilot/score_open.py --precheck $OUT/round-108-precheck.json
```

**Registered pass condition: at least 10 of the 30 `open-*` answers carry the
open question, at least 3 in every stem.** The `unsettled-*` and `keep-*`
counts are disclosed and decide nothing.

**If it does not fire**, the edit is not committed, stage 2 is not generated,
this document records the precheck, and the round is recorded as measuring.

## The edit, committed only if stage 1 fires

The never-cut item, in the section every level carries:

```diff
-- Uncertainty that changes what the user should do.
+- Uncertainty in the answer to what the user asked, when it changes what they
+  should do. A caveat on a claim the user did not ask about is not
+  protected: leave out the claim, and its caveat goes with it.
```

`rules_cksum` is stamped into each snapshot at generation.

**Hypothesis.** Editing the never-cut uncertainty item to cover uncertainty in
the answer to what was asked should move the rate at which `open-*` answers
carry the open question, opus, down.

## Stage 2: the edit on opus, only if stage 1 fires (240 generation calls)

Two trees generating simultaneously: control from a worktree at this branch's
registration commit (master rules), edit from this branch with the edit
committed. Laconic, opus, `--turn-delivery plugin`: `open-*` at 20 reps and
`unsettled-*` and `keep-*` at 10, so 120 runs a side in two shards a side of
90 and 30.

```sh
for side in control edit; do for off in 0 10; do
  cells="$O,$U,$K"; [ $off = 10 ] && cells="$O"
  ( cd <tree for $side> && python3 evals/bench/run.py --arms laconic --reps 10 \
      --rep-offset $off --cases-dir evals/pilot --cells "$cells" \
      --turn-delivery plugin --concurrency 4 \
      --snapshot $OUT/round-108-$side-shard$off.json ) &
done; done
wait
python3 evals/bench/merge.py $OUT/round-108-$side-shard{0,10}.json --out $OUT/round-108-$side.json
python3 evals/bench/judge.py --results $OUT/round-108-$side.json --cases-dir evals/pilot \
    --out $OUT/round-108-$side-judgments.json
```

### The bars

1. **Primary: the rate at which `open-*` answers carry the open question
   falls**, opus, pooled over the three stems, one-sided Fisher, alpha 0.05.
2. **Falsifier, fatal: panel-judged pass rate may not fall** on `open-*`,
   `unsettled-*` and `keep-*`, each pooled per family, one-sided Fisher,
   alpha 0.05.
3. **Bound, fatal: `HEDGE` may not fall** on `unsettled-*` and `keep-*`, each
   pooled per family, one-sided Fisher, alpha 0.05: the answer says the
   record leaves the question open, or makes its advice conditional on it.

One look, declared here. No multiplicity correction on the bounds, per
`AGENTS.md`.

**Disclosed, deciding nothing:** per-stem counts, including the share of
`open-*` carries that are inferences (`INFER`) rather than notes that the
question is open; prose words; `panel_agreement.py`; `release.py`.

**Replication, bought only if everything above passes:** a fresh 120 runs a
side from the same two trees, scored on bars 1 to 3 at the same alphas. Then
step 9's holdout: all six reserved cases, opus, 10 reps, both trees; no
reserved case worse at p < 0.05, directions only.

**Accept** needs bar 1 to pass and bars 2 and 3 to hold, twice, and the
holdout. Anything else rejects and reverts `rules/laconic.md` and
`rules/dist/` before the merge.

## Pre-mortem, registered

The likeliest outcome is that **stage 1 does not fire**. v0.3.6 already tells
an either/or answer to leave its evidence out, which put 16 of round 106's 60
edit answers at 20 words or fewer, and these fixtures mention the unknown in
passing rather than under a heading. If it fires, the likeliest failure is
**the primary moving with its direction and not separating**: the report's
model kept its paragraph against check 3, and nothing shows that the
uncertainty item, rather than helpfulness, was what kept it. The fatal risk
is `keep-*`: "leave out the claim" read as licence to answer a remedy
question without the condition it depends on.

## What this round cannot establish

- **Opus only.** The edit ships to every model; sonnet and haiku have no runs
  on this instrument.
- **Whether the item caused the defect.** A fall shows the edit moves the
  rate, not that the old wording licensed it.
- **A pooled primary over three fixtures.** One stem can carry it; the
  per-stem counts are disclosed so a reader can see whether it did.

## Where the ideas came from

The edit is [#384]'s third suggested direction. Through `tools/consult.sh`,
Codex and Kimi both said a labelled "Open" section would hand the model the
defect, so the unknown moved into the narrative and `INFER` counts only words
the fixture does not contain; Kimi's point that the report's model inferred
the cause itself is why `INFER` is reported separately. Both asked for a bound
on uncertainty that is not the literal either/or but changes what the user
should do, which is `keep-*`. The wording takes Codex's "requested guidance"
as "the answer to what the user asked", and its second sentence is this
round's own. Kimi's "earns no caveat" was not taken, because it can be read as
licence to state the claim unhedged. Codex's suggested header-against-inline
split was not taken; the round uses inline only. DeepSeek was not asked.

[#384]: https://github.com/JordanMPDS/laconic/issues/384

## Results

<!-- Nothing above this line has been computed. -->

### Stage 1, first sample: the registered detector under-read `disk`

60 runs, 0 failed, at master rules (`rules_cksum` 3105749900, v0.3.6), every
run on CLI 2.1.301, `cases_cksum` 3428123555 over the nine cells.

Scored as registered, it did not fire: 17 of 30 `open-*` answers carry the
open question, but `disk` read 0 of 10. Reading the `disk` answers, 3 of the 10
do carry it. All three paraphrase the fixture rather than quoting it, and the
registered `UNKNOWN` matched only the fixture's own words ("nothing past"):

> The note doesn't say why WAL is piling up. No one has run anything beyond
> that `du`.

`UNKNOWN` was widened to match those paraphrases on every stem ("doesn't say
why", "nothing beyond that `du`", "no one has run"), and `HEDGE` to match
"can't answer that", which it had missed on one `unsettled-checkout` answer
that says the record cannot settle the question. Both fixes are in commit
8f31937, before any sample they decide. Re-read under them, the first sample is
20 of 30, `cdc` 7, `disk` 3 and `checkout` 10, and every `unsettled-*` and
`keep-*` answer hedges (15 of 15 each).

**A pass reached by correcting the detector on the sample that showed the
fault is not a pass**, so the gate is decided on a fresh 30 `open-*` runs,
rep keys 10 to 19, scored by the corrected detector as committed. That sample
is below.

`checkout` carries it in all ten answers, nine of them by inferring where
inside the call the time might go ("DNS, TLS setup, or waiting for a pooled
connection"), which is [#384]'s second paragraph almost word for word. `cdc`
answers note that the sink settings were not collected, and three of them also
infer a cause ("parallel sends or retries"). The `disk` answers never infer a
cause: the three that carry the question only say it is unknown.

### Stage 1, the deciding sample: it fires

30 fresh `open-*` runs, rep keys 10 to 19, 0 failed, at master rules, every
run on CLI 2.1.301, scored by the detector as committed in 8f31937.

| stem | carries the open question | of which infer a cause | median prose words |
|---|--:|--:|--:|
| `cdc` | 8/10 | 6 | 81.0 |
| `disk` | 5/10 | 0 | 24.5 |
| `checkout` | 10/10 | 10 | 84.5 |

**23 of 30, every stem at 3 or more: it fires, and stage 2 is bought.** Read by
hand, all ten `disk` verdicts are right: the five that carry it end on "The
document doesn't say why the WAL is being retained, because nothing beyond
`du` has been run yet" or close to it, and the five that do not are the option
and the volume's contents. The two `cdc` answers that do not carry it add a
different caveat, that the subscription might also reorder writes, which bears
on the option the user named and is not counted.

### Stage 2, first sample

120 runs a side, 0 failed, every run on CLI 2.1.301, so `release.py` finds no
span. `rules_cksum` 3105749900 on every control run and 4228464778 on every
edit run; `cases_cksum` 3428123555 over the nine cells on both sides. Panel
judgments 120 a side.

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. `open-*` carries the open question | 47/60 | 30/60 | 0.0011 (one-sided) | **passes** |
| 2. panel quality, `open-*` | 60/60 | 60/60 | 1.000 | holds |
| 2. panel quality, `unsettled-*` | 30/30 | 30/30 | 1.000 | holds |
| 2. panel quality, `keep-*` | 30/30 | 30/30 | 1.000 | holds |
| 3. `HEDGE`, `unsettled-*` | 30/30 | 30/30 | 1.000 | holds |
| 3. `HEDGE`, `keep-*` | 30/30 | 30/30 | 1.000 | holds |

**Disclosed, deciding nothing.** Per stem, `open-*` carries the open question
17 to 11 of 20 on `cdc`, 10 to 2 on `disk`, and 20 to 17 on `checkout`. The
fall is `cdc`'s and `disk`'s; `checkout` barely moves. Its edit-side answers
still say the span "can't separate slowness on the provider's side from
slowness in our own connection setup", and the edit's wording arguably protects
that: the user's option, "the call to the card provider", can be read as "the
provider is slow", and the caveat is about that reading. Answers inferring a
cause (`INFER`) go from 26 of 60 to 19, and 20 and 17 of those are on
`checkout`.
Medians of `open-*` prose words: 73.5 to 40.5 (`cdc`), 38.5 to 21.5 (`disk`),
86.5 to 80.0 (`checkout`). Every panel verdict is a pass on both sides, so
`panel_agreement.py` reads 119 or 120 of 120 per pair with no kappa to report.

### Replication

A fresh 120 runs a side from the same two trees, 0 failed, every run on CLI
2.1.301, with the same `rules_cksum` pair.

| bar | control | edit | p | |
|---|--:|--:|--:|---|
| 1. `open-*` carries the open question | 40/60 | 26/60 | 0.0083 (one-sided) | **passes** |
| 2. panel quality, `open-*` | 60/60 | 60/60 | 1.000 | holds |
| 2. panel quality, `unsettled-*` | 30/30 | 30/30 | 1.000 | holds |
| 2. panel quality, `keep-*` | 29/29 | 28/28 | 1.000 | holds |
| 3. `HEDGE`, `unsettled-*` | 30/30 | 30/30 | 1.000 | holds |
| 3. `HEDGE`, `keep-*` | 30/30 | 29/30 | 0.500 | holds |

Per stem, `open-*` carries it 16 to 6 of 20 on `cdc`, 4 to 3 on `disk`, and 20
to 17 on `checkout`, with `cdc`'s median falling from 61.0 words to 7.5. This
time the fall is `cdc`'s alone. `disk`'s control read 4 of 20 against the
first sample's 10, so the stem that moved most in the first sample had little
to move in the second.

kimi returned a vote on 60 control verdicts and on none of the edit's, so
sonnet and opus decided the rest together. They split on one control and two
edit `keep-cdc` verdicts, which stay undecided and are left out of bar 2's
denominators. All three are "No" answers that give both reasons, that retries
are not shown to be the cause and that turning them off loses changes; the
trap is ambiguous between those two grounds, on both sides alike. The one
edit `keep-checkout` answer `HEDGE` misses opens "**Not yet.** The document
shows the time is spent inside `payments.authorize`, but not that the provider
is the slow part", which the panel passes; the detector has no pattern for
"not yet".

### Holdout

All six reserved cases, opus, 10 reps from both trees, 0 failed, CLI 2.1.301:
every decided verdict passed on both sides, and one `holdout-verdict` verdict
on each side is undecided. No reserved case is worse under the edit.
Directions only, as step 9 requires.

## Result: accepted

**Accept.** Bar 1 passed and bars 2 and 3 held on both samples, and the
holdout held. The edit stays in `rules/laconic.md` and `rules/dist/`, at
`rules_cksum` 4228464778. `README.md` now paraphrases it.

The never-cut item now protects uncertainty in the answer to what was asked.
On `open-*` the rate at which opus carries an open question nobody asked about
fell from 47 to 30 of 60, then from 40 to 26. Where the uncertainty was the
answer (`unsettled-*`), or decided whether a remedy the user asked about would
work (`keep-*`), every answer kept it, on both samples.

The fall is uneven, as the registration warned a pooled primary could be.
`cdc` fell on both samples (17 to 11, 16 to 6), `disk` on the first (10 to 2)
and hardly on the second, from a control of 4, and `checkout` barely moved
(20 to 17 twice). On `checkout` opus keeps the caveat that the span cannot
separate the provider from our side of the call. That caveat bears on how the
user's own option reads, so the new wording does not plainly cut it.

The pre-mortem was wrong twice. Stage 1 fired, after its detector was
corrected, and the primary separated on both samples. Its fatal guess,
`keep-*` losing its condition, did not happen: 30 of 30 hedged on the first
sample and 29 of 30 on the second, the miss being a "Not yet" the detector
cannot read.
