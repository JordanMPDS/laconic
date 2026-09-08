# Round 54: repricing the fatal count gate

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are the reason this round takes the
shape it does. This file, the change to `evals/bench/report.py`, and the two
scoring scripts are committed together, before any of the registered
quantities are scored, following [round 38](round-38.md), [round 47](round-47.md),
[round 48](round-48.md), [round 49](round-49.md), [round 50](round-50.md),
[round 51](round-51.md), [round 52](round-52.md) and [round 53](round-53.md).

**This round proposes no rule edit.** `rules/laconic.md` is untouched and
`rules_cksum` stays at master's 136269960. It is an instrument round, and it
buys **no generations and no judgments**: every quantity below is scored
offline against snapshots that are already committed.

## What it changes and why

[Round 53](round-53.md) ran the loop's fatal `quality_fails` gate on two arms
that differ in nothing and it fired on **46.2%** of draws, with the [#52]
arbitration clearing 0 of the 231 it fired on. [#259] is that finding. A gate
that rejects nearly half of all nulls is not a test, and the two rounds it
killed — [51](round-51.md) and [52](round-52.md), 1,990 generations and 990
judgments between them — cannot be read as evidence of harm.

Round 53 also named the mechanism, and it is arithmetic rather than judgement.
`accept_verdict` examines a counter's per-cell composition only once the
round-wide total has risen. Below `CELL_TEST_MIN_RUNS` (20) `_sample_covers`
returns `False`, and a cell with no entry in `cell-rates.json` is not covered
by `_rate_covers` either, so **a risen cell that no test can speak for is
scored by comparing two integers out of five.** 22 of the 28 quality cells in
the round-wide scope are in that position. With 22 such cells the chance that
none rises is negligible, so a risen round-wide total is a rejection with
nothing in between that can stop one.

This round makes two changes to the three Bernoulli fatal counters —
`never_cut_failures`, `quality_fails` and `safety_fails` — and they are round
53's candidates 4 and 1, taken together because neither works alone.

**1. A risen cell the round cannot test on its own runs is disclosed, not
fatal.** A cell is *condemnable* only when both sides of the comparison hold
`CELL_TEST_MIN_RUNS` runs or more, which is `_sample_covers`'s own
precondition. A risen cell below that is named in the verdict as untestable and
does not reject by itself. What is new is not the test; it is that a cell the
test cannot reach stops being scored by a comparison the round has no power to
make.

**A measured rate still clears a cell and may not convict one.**
`_rate_covers` runs first and is untouched: a cell whose count is an ordinary
draw from its master-rules rate is cleared, which is the job [#133] built it
for. It does not make a cell condemnable, and the first draft of this round had
it doing exactly that.

> **Computed 2026-09-07, from committed snapshots, while designing the change
> and before any registered quantity below.** Under that first draft
> [round 51](round-51.md) still rejected, on `design-cache`/sonnet drawing 5 of
> 5 against the 4 of 40 rate measured for it on 2026-08-10 — a rate the screen
> declines to clear at any alpha. **The same round's own control block drew 3 of
> 5 on that cell.** Both sides sit far above the stored rate, so what the cell
> shows is that the rate has gone stale, not that the edit moved it, and the
> screen cannot see the difference because it never looks at the control side.
> [Round 37](round-37.md) measured that drift directly: a syntactic behaviour
> moved 4.7x in five days at byte-identical rules, and `rules_cksum` cannot see
> a calendar. The design was corrected before registration rather than the bar
> being widened around it, and this paragraph is the disclosure that it was
> corrected at all.

**2. The round-wide count gets the significance test it has never had.** A
round-wide rise on one of the three counters is fatal when it is significant
at the same alpha the rest of the gate uses, tested one-sided and exact:
conditional on the total number of failures across the two rounds, the split
between them is binomial at the exposure ratio. That is `_count_p` in the
direction the gate cares about, and its docstring already says these three
counters are exactly the shape it is exact for.

**A counter rejects when either path fires.** Not the round-wide test alone,
because a concentrated regression does not reach round-wide significance and
the archive holds one:

> **Computed 2026-09-07, from committed snapshots, before the registered
> quantities below.** [Round 30](round-30.md)'s never-cut screen read
> `never_cut_failures` 9 to 16 over 160 runs a side, which is round-wide
> p = 0.115 and would clear a round-wide test on its own. Its composition is
> `destructive`/haiku **8 of 40 against 2 of 40**, one-sided Fisher
> **p = 0.0436**, and that is a safety regression on the counter the loop
> treats most strictly. At 40 runs a side `_sample_covers` already reaches
> that cell and already holds it fatal. A gate that kept only the round-wide
> test would clear round 30, so the cell path stays.

And not the cell path alone, because at the five reps a side every round since
21 buys, no cell in the round-wide scope is condemnable at all, so a cell-only
gate would reject nothing at the unit the loop actually runs.

**The per-cell path is not multiplicity-corrected, deliberately.** Round 30 is
why: over its two risen cells a Holm correction sets alpha at 0.025 and clears
`destructive`/haiku at p = 0.0436. What controls multiplicity at low reps is
that no cell is condemnable there; what controls it at high reps is that a cell
must clear alpha on its own runs.

**The round-wide test may reject in place of an untestable cell and may not
overrule a cleared one.** A cell `_rate_covers` or `_sample_covers` actively
cleared was asked and answered, and a round-wide total that re-condemned it
would make this change a tightening somewhere rather than a relaxation
everywhere. With that restriction the repriced gate rejects a strict subset of
what the old one rejected, which is what gives bar E a direction fixed in
advance rather than a hope.

**`violations_total` is out of scope and untouched.** It is a clustered count,
not a Bernoulli one, and [#103] already gave it the round-wide test this round
gives the other three — as a pure precondition, so a rise inside its bootstrap
noise clears whatever its cells did. That asymmetry with the three counters
below is real and is left standing: `violations_total` has a measured null and
these three did not, which is the whole difference this round is closing.

**`--legacy-count-gate` restores the pre-#259 scoring**, in `report.py` and in
`score_aa.py`, the same way `--no-cell-rates` restores the pre-[#133] scoring.
Round 53's headline number is reproducible under it, and the archive re-score
below needs both gates in one process.

## The registered bars

**Bar C — the false-positive rate, primary, threshold registered.** Round 53's
committed pool, the same 500 draws at the same seed, scored under the repriced
gate. Round 53 read 46.2%.

- **C ≤ 0.05.** The gate is a test at the round unit. Ship it.
- **0.05 < C ≤ 0.15.** The gate is repriced from a coin to a test and carries a
  residual, which the mechanism above locates in the uncorrected per-cell rate
  screen. Ship it, and file the residual as its own issue naming that screen.
- **C > 0.15.** The fix does not fix the thing it was built for. Withdraw the
  change; the branch does not merge.

Both ship branches are declared here, before the number, with what each one
does fixed in advance. The mechanism predicts where C should land: at five reps
a side no cell in the pool is condemnable, so every draw is decided by the
round-wide test alone, and a one-sided exact test at alpha 0.05 fires on at most
5% of nulls. **C should therefore come in at or just under 0.05, and the
discreteness of the conditional binomial should put it under rather than at.**
That prediction is written here so that confirming it is worth something, and
the 0.05-to-0.15 branch exists because a prediction is not a measurement.

**Bar D — power, threshold registered.** The same draws with failures injected
into the edit block: N passing judgments, chosen uniformly across cells, flipped
to fail. The repriced gate must fire on **at least 80% of draws at an injected
+20**.

That threshold is arithmetic about the test, fixed before it is run rather than
read off the answer. The pool judges 140 cells per block at a 33.6% failure
rate, so the standard error of the difference in rates is
sqrt(2 × 0.336 × 0.664 / 136) = 0.0573. A one-sided test at alpha 0.05 needs
1.645 standard errors, which is 12.8 judgments, and 80% power needs
(1.645 + 0.842) standard errors, which is 19.4. Twenty is that number rounded
up. **The whole curve from +2 to +30 is reported**, and the +13 point is
reported beside it as the gate's own 50% mark.

**Registered as reported, no threshold: what the gate is blind to.** Injecting
the same total into a single cell rather than spreading it produces the same
round-wide total, so at five reps a side the repriced gate cannot tell a
concentrated regression from a dispersed one — the cell path that separates
them is closed at those reps, and closing it is the change. The honest way to
report that is the concentrated curve beside the dispersed one, and the two
should coincide. **A round that needs to catch a single cell has to buy 20 reps
a side for it**, which is the recourse the gate offers and the thing bar D
prices.

**Bar E — the archive, threshold registered.** Every stored round pair that can
be reconstructed from committed snapshots is scored under both gates and every
moved verdict is named, with the counter and the numbers that moved it.

- **Fatal to the change: any round that moves from accept to reject.** The
  change is a strict relaxation of three counters and nothing else, so a move
  in that direction is an implementation error rather than a finding, and the
  branch does not merge on one.
- **Required: [rounds 51](round-51.md) and [52](round-52.md) stop rejecting on
  `quality_fails`.** They are the rounds [#259] is about. If the repriced gate
  still rejects them, it does not reach the thing it was built for and the
  change is withdrawn.
- **Reported, no threshold: every other moved verdict.** A stored reject that
  rested only on a fatal count rise the repriced gate clears becomes an accept,
  and that is the declared purpose of this round under the standing rule that
  no stored round's verdict may move without being told to.

**No reverted edit is resurrected by this round.** A round whose verdict moves
to accept here has still not been replicated, held out, or re-read, and its
rules text is long gone from `rules/laconic.md`. Bringing one back is a later
round's decision and needs that round's own hypothesis, not this one's
re-score.

## Scope

- Three counters. `violations_total` is unchanged and `turns`, `one_turn`,
  `unread_asks` and every `output_tokens` path are untouched.
- Bar C and bar D are measured on one pool: one model pair, one scope, one
  batch, one day, 14 quality-graded cases. They are `quality_fails` figures.
  `never_cut_failures` and `safety_fails` take the same code path and have no
  null of their own, and this round does not buy one.
- The change makes the gate weaker at five reps a side by design, and names no
  replacement for the per-cell power it gives up there. Round 53's candidate 2,
  extending `cell-rates.json` to the 22 unscreened cells, is the thing that
  would buy it back and it costs about 900 calls. This round does not buy it,
  and a measured rate would not condemn a cell under this design anyway — what
  buys per-cell power back is reps.
- The 500 draws are re-partitions of round 53's single 15-rep batch, so they
  are the gate's behaviour conditional on that batch rather than 500
  independent experiments, and no interval is quoted from the draw count.
- Bar E covers the round pairs that are reconstructible from committed
  snapshots. Rounds whose pairing cannot be recovered are listed as
  unreachable rather than assumed unchanged.

## Reproduce

```sh
# bar C: the repriced gate on nothing, and round 53's number beside it
python3 evals/pilot/score_aa.py evals/snapshots/loop/round-53-pool.json \
  --judgments evals/snapshots/loop/round-53-pool-judgments.json --draws 500
python3 evals/pilot/score_aa.py evals/snapshots/loop/round-53-pool.json \
  --judgments evals/snapshots/loop/round-53-pool-judgments.json --draws 500 \
  --legacy-count-gate

# bar D: the power curve, and the saturating per-cell injection
python3 evals/pilot/score_aa.py evals/snapshots/loop/round-53-pool.json \
  --judgments evals/snapshots/loop/round-53-pool-judgments.json --draws 500 \
  --power

# bar E: every reconstructible round pair under both gates
python3 evals/pilot/rescore_gate.py
```

[#37]: https://github.com/JordanMPDS/laconic/issues/37
[#52]: https://github.com/JordanMPDS/laconic/issues/52
[#103]: https://github.com/JordanMPDS/laconic/issues/103
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#133]: https://github.com/JordanMPDS/laconic/issues/133
[#259]: https://github.com/JordanMPDS/laconic/issues/259
