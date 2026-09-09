# Round 60 — which of the three things the demonstration block does?

**Registered 2026-09-09, before any run. No rule edit.** A replacement round for
[#277]: five arms in one interleaved batch, the shipped `full` slice at the
ceiling, round 59's ablation at the floor, and three word-matched rungs between
them.

## Why the round exists

[Round 59](round-59.md) deleted 209 words of rendered demonstration from the
shipped slice and answers came out **1.119x longer overall and 1.284x longer on
the three `design-*` cells**, while a word-matched 165-word block of on-topic
prohibition did nothing. The block is load-bearing. But round 59 registered in
advance that it tests a block and not a mechanism, because those 209 words are
three things at once:

1. the file's only **rendered** short answer, as against a described one;
2. the file's only side-by-side **calibration** of `lite`, `full` and `ultra`;
3. the only **worked application** of the rule to a specific question — the OOM
   example, plus the design licence's own `Wrong:`/`Right:` pair.

Any of the three explains the result. Separating them is what this round buys.

## The arms

Each arm is `laconic-abl-shown` with a substitute put back at **both** sites
that arm deletes from, and each removes exactly **one** of the three properties
while keeping the other two. So every rung is one difference away from the
shipped slice, not one difference away from the rung below it.

| arm | words | rendered | mapped to a level | worked from a question |
|---|--:|---|---|---|
| `laconic` (ceiling) | 1,041 | yes | yes | yes |
| `laconic-repl-told` | 1,049 | **no** — the same content in prose | described | described |
| `laconic-repl-unlabelled` | 1,042 | yes | **no** — three answers, no level names | yes |
| `laconic-repl-unframed` | 1,034 | yes | yes | **no** — the answers stand free |
| `laconic-abl-shown` (floor) | 832 | no | no | no |

**Both anchors are regenerated inside this round.** Round 59's 1.284x was
measured against a different CLI build and the CLI ships several times a day
([#272]); a rung positioned against a number from a previous round would be
positioned against a different instrument.

`tests/test_bench.py` holds every rung to pure replacement: each must contain
every line of `laconic-abl-shown.md` in order, so nothing the floor keeps can be
dropped or reworded, and each must land within 20 words of the shipped slice.
Because the floor is itself checked line-by-line against the live hook output,
an edit to `rules/laconic.md` that moves the block fails all five arms at once.

## Four registered deviations from [#277]'s proposed ladder

[#277] proposed a cumulative ladder — the table replaced by prose, then the
calibration collapsed to one row, then the question removed — with the effect of
each rung read against the rung below it. All four changes below were made
before generating and each has a reason.

1. **Single removal rather than cumulative.** In [#277]'s ladder the first rung
   changes all three properties at once, so its contrast identifies "the
   canonical block against a prose rendering of it" and not showing against
   telling. `codex` named this on `tools/consult.sh` and it is right: with one
   property removed per arm, each contrast against the ceiling is a main effect.
2. **The rungs are word-matched to the shipped slice, within +8 and −7 words.**
   [#277]'s literal ladder produces rungs of about 1,041, 1,000 and 960 words,
   so arm length would have tracked ladder position — the exact confound the
   round exists to remove. Round 59's `abl-arrow` null is **not** an adequate
   defence, and checking rather than assuming is what showed it: pooled over six
   cells that arm reads 0.967x, but re-scored on the three design cells alone it
   reads **1.058x with a 95% interval reaching 1.119x**, which bounds bulk at
   1.070x per 100 words. A 20-word band bounds it at 1.014x. Both targets
   independently rejected padding with new prose as trading one confound for
   another; word-matching the substitutes avoids needing either.
3. **Scope narrows from six cells to the three `design-*` cells.** Round 59's
   exploratory finding is that the whole effect is there. Measured on round 59's
   own 720 runs the within-(case, arm) standard deviation of log prose words is
   **0.224 on the design cells and 0.467 on the contract cells**, so the three
   dropped cells were contributing most of the noise and none of the signal.
   This is the single largest source of resolution in the design.
4. **The tie-break is a registered interaction, not a second table.** [#277]
   asks for cases that separate "the block governs advice-shaped questions" from
   "design cells are where this file has room to move". `codex` pointed out that
   two contrasts reported side by side is an anecdote and that the estimand is
   their difference, so it is computed and printed as one number with an
   interval.

*Origin: deviations 1, 2 and 4 came from the `codex` target on
`bash tools/consult.sh`. `kimi` independently made the same call on the word
count and on the tie-break cells, and argued for reporting the share of the
block effect each rung recovers rather than pairwise p-values alone, which is
adopted below. `deepseek` was asked and did not answer.*

## Scope and depth

Sonnet only, **720 generations**, no judging in step 1, one `rules_cksum`.

- **Ladder pass: 5 arms × 3 cells × 40 reps = 600.** `design-cache`,
  `design-realtime`, `design-upload` — the sanctioned `one_turn` scope and the
  three cells that can tell a fixture-derived answer from a recalled one
  ([#88]). Three shards splitting the rep range (`run.py --rep-offset`), so
  every shard runs every case and the per-shard printout is a real robustness
  check rather than a restatement of which cases a process owned.
- **Tie-break pass: 2 arms × 3 cells × 20 reps = 120.** Ceiling and floor only,
  on `stale-cache`, `verdict-schema`, `verdict-rollout`.

**Why those three tie-break cells, and why not `walkthrough`.** The cells have
to be long at baseline — so "no room to move" cannot explain a null — and not
advice-shaped, so the two readings make opposite predictions. These three read
a fixture and return a diagnosis or a verdict, and their historical `laconic`
sonnet medians are 163, 269 and 273 words against the design cells' 170 to 225,
so if anything they have *more* room than the primary scope does. `walkthrough`
is the obvious long cell and it is disqualified: at 418 words it is the longest
in the suite, but the rules explicitly protect content the user asked to have
explained, so a null on it would read as "the contract exempted it" rather than
"the block does not generalise". Both delegate targets reached that
disqualification independently and neither was told the other's answer.

## Endpoints, registered before generation

**Primary: mean log prose words, blocked on the case, three rungs against
`laconic` at Bonferroni α = 0.0167**, permutation on arm labels within block at
seed 58, reported as a geometric-mean ratio with a 95% percentile interval from
4,000 bootstrap draws. Each block contributes the difference of its two arm
means and every block weighs the same.

**Reported with the primary, and the reason the round stays readable when a
contrast misses: the share.** For each rung, the fraction of the ceiling-to-
floor gap that removing its property gives back,

    share = (rung − ceiling) / (floor − ceiling)

on the same bootstrap draws, so the numerator and denominator move together. A
rung can be non-significant against both anchors and still carry a share
interval that excludes 0 or excludes 1, and that is a result rather than an
absence of one. If the three properties are additive and exhaustive the three
shares sum to about 1; they are not constrained to, and a sum far from 1 is
itself reportable.

**Also reported: each rung against the floor**, which asks whether that delivery
form buys anything at all rather than whether it buys everything.

**Secondaries**, none of them the primary: the same contrasts additionally
blocked on the reading stratum (`grounded()` is `num_turns > 1`, which is
post-treatment, so it cannot be the primary — round 59's reasoning, unchanged);
the primary per shard as a diagnostic, where a contrast carried by one process
is a warning and not a finding; and the per-cell median sign test as a
robustness display, which with three cells cannot reach any useful p and is
printed only because round 58 and 59 printed it.

**The tie-break, registered as one number.** The floor-against-ceiling contrast
on the three design cells minus the same contrast on the three verdict cells,
with a 95% interval. An interval excluding 1 says the block's effect is specific
to advice-shaped questions; an interval containing 1 with both families
substantially above 1 says it generalises to any cell with room to move.

**Guardrail: reading rate** on the three `design-*` cells, share with
`num_turns > 1`, against `laconic` at the registered 15-point non-inferiority
margin. [#278] fixed the verdict to three outcomes and this round inherits both
the fix and its consequence: at 120 runs an arm the margin certifies only an arm
that falls by less than 5.0 points, and the scorer prints that line beside the
result. So this guardrail can report **HARMED**, and it can report
**inconclusive**, and a non-inferior verdict is available only for a very small
observed fall. That is the guardrail this round has and it is stated in advance
rather than reinterpreted after.

**No never-cut contract guardrail this round, and the reason is not thrift.**
The check needs the three contract cells, which are out of scope for the reasons
in deviation 3, and adding them back at a usable rep count costs more
generations than the round's primary. What replaces it is stronger for these
particular arms than it was for round 59's: every rung is a *replacement*, the
never-cut contract text is byte-identical in all five arms, and
`tests/test_bench.py` proves it on every one. Round 59's arms deleted material
and needed a behavioural check; these do not delete any.

**The manipulation check is the file invariant, and there is no behavioural
one.** Round 59 could check that `abl-arrow` produced more arrows, because the
rule it deleted prohibits an observable behaviour. Nothing here deletes a
prohibition — the three properties are presentational — so no response-level
counter can confirm a rung received its treatment. The test suite proving each
arm is the floor plus its registered substitute is what this round has instead,
and it is weaker: it establishes what the file says, not that the model
attended to it. Named here rather than left for a reader to notice.

## Power, and what a null would mean

The within-(case, arm) standard deviation of log prose words on the three design
cells, measured on round 59's own 720 runs, is **0.224**. At 120 runs per arm
over three blocks that gives a standard error near 0.029 on each contrast and a
**minimum detectable ratio of about 1.101x** at α = 0.0167 with 80% power.

The floor-to-ceiling gap on these cells was **1.284x** in round 59, so the
detection floor is about 39% of the range. That is the honest limit of this
design: a rung sitting at either anchor resolves cleanly, and a rung sitting
near the midpoint will be non-significant against both. It is why the share is
registered as a co-primary display rather than an afterthought — the midpoint
rung is exactly the case where a pairwise p-value says nothing and a share
interval of, say, [0.2, 0.8] still rules out both "this property is the whole
story" and "this property does nothing".

Dropping a rung to buy resolution was considered and rejected. Four arms at 50
reps moves the detectable ratio from 1.101x to 1.087x, which does not change
which rungs resolve, and it costs one of the three questions [#277] asks.

The tie-break pass has 60 runs per arm over three blocks. At the historical
standard deviation of those cells, near 0.19, its detectable ratio is about
1.10x against a design-cell effect of 1.284x, so it can see an effect one third
the size. The interaction of the two contrasts detects about 1.135x.

## The registered reading

Fixed before the numbers. "At the ceiling" below means not separated from
`laconic` and separated from the floor; "at the floor" means the reverse.

- **`repl-told` at the floor, the other two at the ceiling.** Showing rather
  than telling is the mechanism: the same information delivered as prose buys
  nothing, and neither the level mapping nor the worked question matters once
  something is rendered. This is the speculation round 59 named and refused to
  claim.
- **`repl-unlabelled` at the floor, the other two at the ceiling.** The
  calibration is the mechanism — what the block does is show three lengths and
  say which level each belongs to, and a rendered answer with no level attached
  is no better than a described one.
- **`repl-unframed` at the floor, the other two at the ceiling.** The worked
  application is the mechanism: an example needs a question to be an example of.
- **Every rung at the ceiling.** No single property carries it; the block
  degrades only when all three go, which is an interaction rather than a set of
  main effects, and the next round is a factorial with two properties removed at
  a time.
- **Every rung at the floor.** Any disturbance to the block costs its whole
  effect. Not predicted by anything and it would be reported as such — the most
  likely mundane explanation, that the substitutes are simply worse writing,
  cannot be excluded by this design and the round would say so.
- **Nothing resolves.** Every rung's interval spans both anchors. Then the
  shares are the result: they are reported with their intervals, and the round
  states what they exclude rather than reporting a null.

Anything reported outside these endpoints is exploratory and says so where it is
written.

## Bound, fatal to the round

A single `rules_cksum` across every snapshot, and any pass crossing a CLI
release is reported through `python3 evals/bench/release.py` before a contrast
is read out of it ([#272]). `python3 evals/bench/concurrency.py` must read the
declared fan-out on every snapshot.

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#275]: https://github.com/JordanMPDS/laconic/issues/275
[#277]: https://github.com/JordanMPDS/laconic/issues/277
[#278]: https://github.com/JordanMPDS/laconic/issues/278
