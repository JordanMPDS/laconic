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
