# Round 47: round 40's edit, on an instrument that can see the thing it edits

**Registration. Nothing below the results line has been computed.** This file,
the edit and the scorer are committed in the same commit, before any
generation, following [round 38](round-38.md) and
[the register pilot](register-inheritance-136.md).

## The edit, byte-identical to round 40's

`rules/laconic.md`, the pre-send checks:

```diff
-Two checks before sending:
+Three checks before sending:

 1. What is the smallest set of claims that fully answers this?
 2. Is anything here something the user did not ask for?
+3. Would this be the same answer if this were the session's first turn?
+   Earlier turns set the subject, never the length.
```

That is [round 40](round-40.md)'s edit reproduced character for character,
deliberately. **The only thing this round changes is the instrument.**

## Why re-run a rejected edit

Round 40 registered `output_tokens` on seven multi-turn sonnet cells —
`drift-service`, `deep-{metric,index,rollback}`, `recall-{metric,index,rollback}`
— and rejected: five of seven moved up, sign test p = 0.4531, median shift +7.5
tokens against a 29.3 floor. Wrong direction in the test and in the point
estimate. The edit was reverted in full.

Three days later the [register pilot](register-inheritance-136.md) established
what those seven cells are:

> `deep-*` cannot produce it, because nothing in `deep-*` asks for a
> licensed-long deliverable. Its turns 2 to 4 are short analysis questions; one
> of the three begins `walk me through`, which is the closest the scored suite
> comes.

And it measured the size of what they are missing. On `deep-*` under `plugin`
delivery, laconic spends **77.5 prose words across all three middle turns**.
There is no inherited register in those sessions to be found — the model's four
prior answers average about 26 words each.

So round 40 tested a licence-expiry clause on sessions where **no licence was
ever granted**. Its null is a null on a condition the clause does not address,
and nothing in it bears on whether the clause works where the mechanism exists.
The pilot built the cells where it does: on `register-*` the same four prior
turns run **704 words**, and the graded turn that follows them runs 52 against
`deep-*`'s 31, at p < 0.00001 with the baseline arm flat as the control.

This round is that re-test, with one variable changed.

## The registered hypothesis

> Editing the pre-send checks to add a third check that recalibrates the answer
> against the current turn alone should **reduce prose words on turn 5 of
> `register-index`, `register-metric` and `register-rollback`**, laconic arm,
> sonnet, `--turn-delivery plugin`.

**Endpoint:** prose words on turn 5 by `metrics.score`, laconic arm, sonnet, 30
runs a side, two-sided permutation of the side label over per-run counts at
200,000 resamples, seed 60.

**Falsifier, registered in advance: `register-*` not separating from its control
at p < 0.05, or separating upward.**

Words rather than round 40's `output_tokens`, because that is the pilot's
registered endpoint, because [#136] is a report about prose, and because the
effect being removed is stated in words (52.0 against 31.0). Naming the same
metric as round 40 would have been the tidier story and the wrong measurement.

**`deep-*` is the registered specificity control**, generated in the same
interleaved batch, with `run.py` looping cases inside one invocation per stem.
Round 40 already used the same idea and the pilot supplies the number: `deep-*`
laconic turn 5 sits at 31 words, which is about as far down as this instrument
goes. Registered reading:

1. **`register-*` falls and `deep-*` does not.** The licence expires, and the
   clause does what [#60] proposal B asks for.
2. **Both fall by similar proportions.** This is a general compression edit, not
   a persistence clause, and the 1.68x carry-forward the pilot measured is
   untouched. The gate's round-wide counters would then be deciding an ordinary
   length edit, and it should be judged as one.
3. **Neither moves.** The clause does not work where the mechanism exists
   either, and [#60]'s proposal B is answered negatively for the first time on
   an instrument that could have seen it.

The arbiter for 1 against 2 is the difference of differences, registered **on
log words** — the pilot's finding is a ratio and the scale-free statement of it
is the register/deep ratio, 1.68 under master rules. Unlike the pilot's
interaction this one is not the broken test round 42 recorded: both groups here
are the laconic arm on the same fixture, so shuffling the side label does not
build a mixture of two modes an order of magnitude apart. The raw-words version
is printed beside it and both come out of `score_persistence.py`, so neither is
recomputed by hand.

## The harm check is fatal to the edit, and it is why this round is worth buying

**Registered: prose words summed over turns 2 to 4 on `register-*`, laconic arm.
A fall significant at p < 0.05 rejects the edit whatever the primary does.**

Those three turns ask, in as many words, for a complete assessment, the whole
argument step by step, and a table with the evidence for each row. The ruleset
promises them full detail — *"Laconic governs volunteered content; it never
truncates requested content"* — and the pilot measured laconic honouring that
promise at 704 words against 77.5 on the plain form, a 9.1x response to the
request.

A clause that tells the model to answer as though this were the session's first
turn can suppress exactly that. [#60] names the risk itself, about its other
proposal: *"this is the kind of edit that could trade one failure mode for the
opposite one."* The instrument that makes the effect visible is the same one
that makes the harm visible, and a round that measured only the primary would
ship the trade without seeing it.

**Free second harm check:** `date_trunc` on the `index` stem, the pair's one
`never_cut` keyword, on the graded turn of all four groups. The other two stems
carry none, so it covers a third of the batch and is stated as such.

## Delivery: `plugin`, and there is no choice about it

Both sides run `--turn-delivery plugin`. `run.py`'s docstring settles it:

> a persistence clause of the kind [#60] asks for cannot be tested under
> `repeat` at all, because `repeat` already over-delivers persistence.

Under `plugin` the added check reaches turn 5 the same way the licence sentence
it modifies does: once, in the turn-1 slice, behind four of the model's own
answers. That is the shipped wiring, and it is the harder test — the clause has
to survive to the turn it governs rather than being re-asserted on it.

## Two trees, generated simultaneously

`rules_cksum` resolves once at `run.py` startup, so the two revisions cannot
share an invocation. Edit side from this branch, control side from a `master`
worktree writing back into this tree, launched together, following
[round 38](round-38.md) — [round 37](round-37.md) measured a syntactic behaviour
moving 4.7x in five days at byte-identical rules, so a sequential window is the
exposure to avoid. Era and CLI release cancel between the sides instead of
confounding them.

```sh
git worktree add /tmp/laconic-control master
for stem in index metric rollback; do
  python3 evals/bench/run.py --arms laconic --models sonnet --reps 10 \
    --cases "deep-$stem,register-$stem" --cases-dir evals/pilot \
    --turn-delivery plugin --concurrency 6 \
    --snapshot "evals/snapshots/loop/round-47-edit-$stem.json" &
done
for stem in index metric rollback; do
  (cd /tmp/laconic-control && python3 evals/bench/run.py --arms laconic \
    --models sonnet --reps 10 --cases "deep-$stem,register-$stem" \
    --cases-dir evals/pilot --turn-delivery plugin --concurrency 6 \
    --snapshot "<abs>/evals/snapshots/loop/round-47-control-$stem.json") &
done
```

Six cases across two revisions, ten reps, five turns each: 120 runs and **600
calls**, the same size as the pilot and half what it would cost with a baseline
arm. The baseline arm is not bought, because it carries no rules and therefore
cannot move under a rules edit — the pilot already measured it flat on these
same six prompts (p = 0.9135, mean falling), which is what licenses dropping it
here.

The shard boundary is the stem, so both families of every contrast are generated
inside one process, interleaved; the split is across contrasts, never inside one.
`--concurrency 6` is declared on all six per [#120], because six invocations
really are in flight.

Scored by `python3 evals/pilot/score_persistence.py <control> <edit>`, which
imports its word measure and its tests from `score_register.py` so the two
scorers cannot drift on what a word is.

## What this round does not buy, yet

**No judging, and no round-wide arm, until the scoped target passes.** The skill's
standing order is to buy in sequence and stop at the first step that fails, which
is what saved round 40 its 220-generation arm. If the primary clears and the harm
check holds, the round-wide laconic arm and its judgments are the next purchase
and no rule change ships without them.

**Nothing is promoted.** The pair stays in `evals/pilot`, so `cases_cksum` does
not move and no fatal counter gains an unseeded cell.

## Power, stated before the numbers

The pilot separated 31.0 from 52.0 at 30 runs a side on this exact endpoint at
p < 0.00001. This round is sized identically and is powered to see the effect
being removed, which is the same 21 words in the other direction. It is not
powered for a 5-word shift, so a null here is a null on a large effect. The
floor matters as much as the ceiling: `deep-*` at 31 words is close to the
bottom of what these prompts produce, so a specificity control that "does not
move" is partly a floor and is read as such.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#136]: https://github.com/JordanMPDS/laconic/issues/136

<!-- RESULTS BELOW THIS LINE -->
