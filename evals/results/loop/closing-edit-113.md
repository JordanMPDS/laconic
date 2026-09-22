# Closing offers in a session that edits: the regime #113 came from

**Registration. Nothing below the results line has been computed.** This file,
the pilot case, the symlink and the scorer are committed in one commit before
any generation, so git dates every bar and prediction below against the data.

**This is a pilot, not a loop round, and it proposes no rule edit.** It carries
no round number, so `tools/candidate-due.sh` reads round 75 as before and round
76 is still permitted to measure. `rules/laconic.md` and `evals/cases/` do not
move, and neither does `cases_cksum`.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_closing_edit.py evals/snapshots/loop/closing-edit-113-*.json
```

## Why this exists

[#113] reports the no-closing-offers rule breaking on one turn of a long `full`
session and holding on the adjacent one. [`closing-drift-113.md`](closing-drift-113.md)
read the only multi-turn family built for it, `drift-service`, and found laconic
at **0 of 525 turn-responses** against a baseline arm at 23.2%. Its own
limitations section names what that cannot say:

> It did not break under five read-only turns that each end `Don't edit
> anything.` [#113]'s session had editing turns [...] so this instrument
> excludes the regime the report came from by construction.

and names the purchase that would:

> **An editing multi-turn case.** The model produces diffs across turns and the
> detector runs on the turn-final prose, testing whether 0 of 325 survives the
> regime [#113] actually reports.

This is that purchase. It answers the one question the sweep left open, whether
the rule breaks only while editing, and it is also the instrument [#113]'s
proposal A (a terminal-sentence check) would need before it could be a
candidate round.

## The pair

`edit-service` is `drift-service` with one clause changed:

| turn | `drift-service` ends | `edit-service` ends |
|---|---|---|
| 1, 2, 4, 5 | `Don't edit anything.` | `Go ahead and make the change.` |
| 3 (a walk-through) | `Don't edit anything.` | nothing |

Same fixture by symlink, same trap byte for byte, same five questions.
`evals/pilot/drift-service` links the scored case so both halves are generated
in one interleaved pass rather than read against the archive's
`drift-service` runs, which are up to three weeks and many CLI releases old.
`tests/test_evals_layout.sh` holds the pair to all of that.

Turn 3 cannot take an edit instruction, and dropping the clause makes it a
different treatment from the other four (unstated rather than permitted). Both
consulted targets said this does not threaten a run-level primary and asked
for the turn-level bound to be split, which the scorer does.

## The command

Four shards, split by model and by rep range, so every contrast — edit against
drift, laconic against baseline — is generated inside one process, interleaved:

```sh
for model in haiku sonnet; do for off in 0 5; do
  python3 evals/bench/run.py --arms baseline,laconic --models $model \
    --reps 5 --rep-offset $off \
    --cases edit-service,drift-service --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 4 \
    --snapshot evals/snapshots/loop/closing-edit-113-$model-$off.json &
done; done; wait
```

Two cases, two arms, two models, ten reps: 80 runs of five turns, **400 calls**,
no judgments. `--turn-delivery plugin` because this is a claim about the
product. Level `full`, the level [#113] reports.

## The bars, in order

**M, manipulation.** At least **80%** of `edit-service` turns 1, 2, 4 and 5,
pooled over arms and models, invoke `Edit`, `Write`, `MultiEdit` or
`NotebookEdit`. If this fails, the regime was not induced and nothing below is
about editing.

**B1, instrument.** The baseline arm fires the detector on at least **10%** of
`edit-service` turn-responses. `drift-service` baseline reads 23.2% in the
archive. If this fails, an editing session does not elicit offers even
unruled, and a laconic zero would be an instrument floor, as it was on the
`recall-*` family's 0 of 315.

**Primary.** Laconic `edit-service` runs, pooled over both models, with at least
one `metrics.closing_offers` hit. **It fires on one hit confirmed by hand-reading**,
and every hit is printed verbatim for that reading. The detector is the
instrument and was measured at 30 of 30 precision before this pilot existed; the
hand-read guards the one new thing here, which is prose written after a diff.

Presence rather than a contrast is DeepSeek's correction, and it is the right
unit: laconic on `drift-service` is already a measured zero at 0 of 525, so any
confirmed offer on the editing half *is* the separation. The Fisher contrast the
first draft made the primary had power about 0.35 at a 15% run rate; presence
over 20 runs has power **0.96** at 15% and **0.64** at 5%.

**Descriptive, and decides nothing:**

- run-level one-sided Fisher, `edit-service` over `drift-service`, per arm;
- laconic turn-level Clopper-Pearson upper bounds on `edit-service`, split into
  the four instructed turns and turn 3;
- a hand-read of the final paragraph of every laconic `edit-service`
  turn-response for offers the detector misses. DeepSeek pointed at the
  likeliest one: `should i` fires only before `look|check|review|dig|go`
  (`metrics.py`), because the loose version was 13 of 13 false positives, so
  *"Should I also apply this to accounts.js?"* is a genuine offer the detector
  cannot see. Misses are counted and quoted, and do not fire the primary,
  because a hand count chosen after reading is not the registered instrument.

## Is an offer after an edit a violation at all?

Asked of both targets, and both answered the same way: yes. The rules exempt
*"Asking the user to confirm a destructive action"*, and running the tests or
extending the change to another file is neither destructive nor a confirmation
of the change just made. So a hit on *"Want me to run the tests?"* measures the
rule breaking, not a carve-out.

## What each outcome means, registered

| M | B1 | primary | reading |
|---|---|---|---|
| fail | — | — | The prompt did not induce editing. Nothing about the regime; the case needs rewording before any second purchase. |
| pass | fail | — | Editing suppresses offers even unruled. A laconic zero is uninformative, and the hole stays open for want of an instrument. |
| pass | pass | 0 | **The editing hole closes at a stated bound.** Proposal A has nothing to fix in either regime at this depth, and #113 stays open only on its length half and proposals B and C. |
| pass | pass | ≥ 1 | **The rule breaks while editing.** Proposal A becomes a candidate round, scored on `edit-service`, laconic, sized from this pilot's run rate. |

## Pre-mortem

I expect the primary to read 0, with M and B1 both passing. The shipped rules
state the prohibition in `lite`, `plugin` delivery sends a one-line reminder
on every later turn, and nothing about an edit gives the model a
new reason to offer. What would make that wrong is the shape an editing turn
ends on: a diff invites *"want me to run the tests / apply this elsewhere?"* in
a way an answer does not, and baseline on `edit-service` may fire well above
`drift-service`'s 23%. If laconic fires at all, I expect it on haiku, on turns 4
and 5, where two earlier diffs give the model a pattern of following one change
with the next. The likeliest failure of the design itself is the detector's
recall on exactly that shape, which is why the misses are counted.

## Where the design came from

`tools/consult.sh` was asked with the issue, this design and the three things I
was least sure of. **Codex did not answer** inside 240 seconds.

- **DeepSeek** changed the primary from a Fisher contrast to presence, on the
  argument above, and pointed out that the first draft's decision tree had a
  hole, "fires but does not separate", that fell through to nothing. It also
  located the recall gap on `should i ...` in the detector's source.
- **Kimi** proposed pooling the models for the primary, which this does, and a
  cluster-robust turn-level secondary, which this does not do: at the
  within-run clustering `closing-drift-113.md` measured, 100 turns carry about
  the effective sample of 20 runs, which is DeepSeek's arithmetic and the
  reason the run is the unit.
- Both asked for the turn-3 split.

[#113]: https://github.com/JordanMPDS/laconic/issues/113

---

## Results
