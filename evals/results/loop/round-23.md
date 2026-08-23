# Round 23

**Baseline:** `evals/snapshots/loop/round-21.json` (+`-judgments`)
**Snapshot:** `evals/snapshots/loop/round-23.json`, `round-23-judgments.json`,
plus the matched batch `round-23-matched.json` and `round-23-matched-judgments.json`
**Rules under test:** baseline `rules_cksum` 1830906901
**Verdict:** pending — this file is the pre-registration, written before any
generation.

First round to score [#46] on `one_turn`, and the first to generate its target
comparison as a **matched interleaved batch** rather than against a stored
baseline.

## Hypothesis

> Adding an ungated third pre-send check to the shared block at
> `rules/laconic.md:7-10` — asking whether the answer claims anything about the
> codebase that was not read, and stating that brevity is a reason to write
> less and never a reason to look less — should move **`one_turn` down** on
> `design-cache`, `design-realtime` and `design-upload`, **sonnet only**, while
> `quality_fails` on those same three cases does not rise and the four
> round-wide fatal counters hold.

`--target one_turn --target-cases design-cache,design-realtime,design-upload
--target-models sonnet`, which is rules 1, 2 and 3 of the six governing this
target. Rule 4 is the `quality_fails` clause above: the surrogate clears **in
addition to** the harm counter, never instead of it.

## Where the hypothesis came from

[`one-turn-investigation.md`](one-turn-investigation.md) established that
laconic's design-answer failures are ungrounded rather than long, and that on
sonnet `num_turns == 1` means the model never opened a file.
[`interleaved-batch.md`](interleaved-batch.md) then measured the mediation chain
end to end in one batch: pooling both sides, answers given without opening a
file fail quality **20 of 39** against **6 of 40** for answers that read the
repository, Fisher p = 7.6e-4, and conditioning on reading removes the rules
effect almost entirely. The harm is not that laconic writes short answers. The
harm is that it stops the model reading, and unread answers are wrong.

**Rounds 16 and 17 aimed at this and missed for a locatable reason.** Their
rule required "a question about code you were pointed at to be resolved from
that code". Every one of the 14 one-turn failures in the investigation falls on
a prompt that names no file, so the gate that rule opens with never fired. The
one change this round makes is removing that gate.

## The edit

`rules/laconic.md`, the shared block above `<!-- level:lite -->`, so it applies
at `lite`, `full` and `ultra` alike:

```diff
-Two checks before sending:
+Three checks before sending:

 1. What is the smallest set of claims that fully answers this?
 2. Is anything here something the user did not ask for?
+3. Am I claiming anything about this codebase that I have not read?
+
+Brevity is a reason to write less, never a reason to look less. A short answer
+about code you did not open is a guess with the hedging removed.
```

Placement is deliberate, and it is round 10's lesson applied: where a rule lives
outranks what it says about where it lives. The pre-send checklist is the
ritual the model already runs before answering, and a grounding check belongs
inside it rather than beside it. It is not in `Level: full`, where rounds 16 and
17 put their version, because the failure is not a full-level behaviour — the
model skips reading at every level, and `ultra` has the least room to recover.

The second sentence is aimed at the mechanism rather than the symptom. What
`interleaved-batch.md` found is that the pressure is **brevity itself**:
`terse-control`, the two-word system prompt `"Answer concisely."`, suppresses
investigation exactly as much as the entire plugin (11/40 against 10/40,
p = 1.000). An edit that only says "read the code" competes with that pressure.
An edit that says brevity does not license skipping the reading contradicts it
directly.

## The registered risk

**This edit may not be able to work.** If a two-word brevity instruction
produces the same suppression as 130 lines of rules, then the pressure is a
property of asking for terseness and not of anything `rules/laconic.md` says,
and no sentence inside the plugin can remove a pressure that two words also
create. Registering that now: if the target does not move, the reading is that
the mechanism is out of the rules file's reach, and [#46] closes as a property
of brevity rather than as a defect to be fixed. That is a real answer.

## Design

**Batch A — the matched target measurement.** `design-cache`,
`design-realtime`, `design-upload`, sonnet, **n=10**, generated as one
interleaved pass alternating one rep at a time between two trees: master from a
`git archive` of the pre-edit commit, and the edit from the repository. Master
runs all five arms; the edit runs `laconic`. 180 generations.

`concise-style` is in it, per the standing rule that it belongs in every
interleaved batch. Round 21's figures for it are from carried arms generated ten
days before the treatment, and inherit exactly the provenance defect that
retired the `terse-control` claim this week; this is the first matched
measurement of the native output style against the plugin.

n is 10 rather than the round's 5 because batch A carries its own master side
and is not scored against the round-21 baseline, so the reps are free to choose.
At 15 a side the target would need something near a 6-of-15 to 0-of-15 collapse
to reach alpha; at 30 a side it can resolve the size of drop that is actually
plausible.

**Batch B — the round-wide fatal counters.** The edit's `laconic` arm at 22
cases, both models, **n=5** to match the round-21 baseline, controls and control
verdicts carried from round 21. 220 generations. This is what
`never_cut_failures`, `quality_fails`, `safety_fails` and `violations_total` are
read from, and carrying is correct for them because they compare the laconic arm
of two rounds and read no control at all.

Batch B also covers the three target cells on sonnet a second time, at n=5 and
cross-batch. That reading is **disclosed, not scored** — it is the comparison
this session spent 200 generations establishing to be unreliable.

**Both batches run strictly sequentially**, one CLI invocation in flight, per
[#120]. The overlap sweep goes in this file when the round reports.

## Cost

About 400 generations and 280 judge calls, roughly $30.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#120]: https://github.com/JordanMPDS/laconic/issues/120
