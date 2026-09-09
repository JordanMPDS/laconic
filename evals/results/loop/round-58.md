# Round 58 — is most of `rules/laconic.md` dilution?

**Registered 2026-09-09, before any run. No rule edit.** An arm round for
[#270]: three arms in one interleaved batch, the shipped `full` slice against
two minimal slices built to the same content specification.

## Why the round exists

Six rounds have each tested one clause of the file and read null — the lens
candidate (44), the quotation exemption (45), the incentive (46), round 40's
edit re-run through the other channel (47, 48), and the licence (49). Every one
of those nulls was read as a fact about its clause. The reading nobody has
tested is that it is a fact about the *file*: 1,055 words of rules at the
shipped `full` level, of which any one clause is a few percent, so a clause with
a real effect would have to overcome the other 1,000 words to show one.

Round 56 is the shape that makes this urgent, and it happened here rather than
in the prior art. The round 55 edit cleared `evals/pilot/score_compression.py`
on all four cases at p < 0.00001 and then cost 7.8 points of reading rate
([#264]) — the file won on the counter it was tuned against and lost on one a
reader sees. [#270] takes its experimental design, and nothing else, from
[SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), which measured a
50-plus rule skill against an eight-line hand prompt and found the prompt won
every reader-visible column while the skill won only on its own linter. That
project publishes no licence, so no text was copied from it.

## The arms

| arm | words | what it is |
|---|--:|---|
| `laconic` | 1,041 | `hooks/laconic.sh start` at level `full`, the shipped slice |
| `laconic-min-a` | 295 | extract: the specification below, in the shipped file's own sentences |
| `laconic-min-b` | 317 | rewrite: the same specification, worded from scratch |

The content specification both minimal slices are built to, fixed before either
was written: the whole never-cut contract (all seven items), the thesis sentence
that separates fewer claims from fewer words, the level-`full` cuts, round 55's
pre-action check, and the design-question licence in the form rounds 26 and 28
accepted. Everything else the full slice carries is absent — the worked OOM
example and its level table, the whole arrow section with its four
`Wrong:`/`Right:` pairs, the section headings, and the six clauses rounds 44
through 49 measured at zero.

Both slices are delivered by `--append-system-prompt`, the same path the
`laconic` arm uses, so the comparison is treatment against treatment rather than
treatment against a differently-delivered competitor. `run.py` reads them from
`evals/arms/` at import, and `tests/test_bench.py` asserts every never-cut item
survives in both — a minimal slice that quietly dropped one would answer a
question nobody asked.

**Two variants, not one, and this is the design's load-bearing decision.** A
single hand-authored slice that loses to the full file cannot separate "the full
file is load-bearing" from "that slice was written badly". Two slices carrying
the same instructions in different words do separate them. `-a` holds wording
constant and varies only what is present; `-b` varies the wording too.

They are two drafts by one author in one sitting, not two independent authors.

*Origin: the two-variant design and the framing of the registered reading below
came from the `codex` and `kimi` delegate targets, which reached it
independently of each other on `bash tools/consult.sh`. `deepseek` did not
answer.*

## Level: `full`, where [#270] says `ultra`

Registered deviation, with its reason. Every clause with a measured effect in
[`LEDGER.md`](LEDGER.md) was measured at `full`; `full` is what the plugin
delivers unless a user sets otherwise; and a headline has to quote the word
count of the slice actually tested. So this round tests **1,041 words** and says
1,041 — `rules/dist/laconic-full.md` is 1,055 by `wc -w`, and the 14-word
difference is the generated-by header comment, which the hook does not send.
`ultra`'s 1,138 is the maximum the product can deliver and is not what this
round measures. A claim about the whole ladder needs its own round.

*Origin: both answering delegate targets raised the mismatch unprompted.*

## Scope and depth

Sonnet only, 30 reps per arm, six cases, 540 generations, no judging in step 1.

- **Reading rate and prose words:** `design-cache`, `design-realtime`,
  `design-upload`. These are the three cases that can tell a fixture-derived
  answer from a recalled one ([#88], `design-discrimination.md`), and they are
  the sanctioned `one_turn` scope — the cells with reading variance *and* a
  measured link to answer quality.
- **The never-cut contract:** `destructive`, `code-fidelity`, `badnews` — the
  three cases whose `expect.json` carries never-cut keywords, so the check is a
  substring test and costs nothing. `ordered-steps` is deliberately excluded
  from this scope: its `never_cut` list is empty, so the free check cannot see
  it, and it reaches the contract only through the judge.

## Endpoints, registered before generation

**Primary, both free, both on the three `design-*` cells:**

1. **Reading rate** — the share of responses with `num_turns > 1`, the same
   definition every round's reading strata use. Non-inferiority, one-sided, with
   a **margin of 15 points**: a minimal slice is non-inferior when the lower
   bound of the difference against `laconic` sits above −15.
2. **Prose words** — the per-cell median inside the grounded stratum ([#131]),
   permutation at seed 58, with a sign test across the three cells. Reported in
   both directions; the interesting result is a fall.

**Guardrail, free:**

3. **Never-cut keyword failures** pooled over `destructive`, `code-fidelity` and
   `badnews`, 90 runs per arm. **Registered as a smoke alarm, not an equivalence
   test.** The archive's rate on these cells is near zero, so 90 runs bound a
   rate at about 3.3% by the rule of three and certify nothing. It is fatal to a
   minimal slice only on a catastrophic loss, defined in advance as **more than
   5 failing runs of 90 where `laconic` fails 1 or fewer**.

*Origin: the "smoke alarm, not equivalence" framing and the explicit power
caveat came from both answering delegate targets, which independently refused
the stronger reading.*

**Step 2, bought only if step 1 does not kill the round:** judge the 270
`design-*` runs for `quality` and the 270 contract runs for `safety`. Reading
rate is a proxy for design-answer quality with a measured link, not a
substitute for it.

## The registered reading

Fixed before the numbers, because "the minimal slice won" is a claim the round
can only make one way:

- **Both minimal slices non-inferior on reading rate, no worse on words, no
  contract loss.** Then 1,055 words buy what 300 buy, and the per-session cost
  of the other 750 is the finding.
- **Both minimal slices worse.** Then dilution is ruled out on this content
  specification, the six nulls are facts about their clauses, and [#270] closes.
- **One worse, one not.** Then the round has measured slice quality, not the
  file, and it proposes nothing about either.

Anything the round reports outside these three endpoints is exploratory and says
so where it is written.

## Bound, fatal to the round

Zero failed runs is not required, but a single `rules_cksum` across every
snapshot is, and any pass that crosses a CLI release is reported through
`python3 evals/bench/release.py` before a contrast is read out of it ([#272]).

[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#275]: https://github.com/JordanMPDS/laconic/issues/275
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#270]: https://github.com/JordanMPDS/laconic/issues/270
[#272]: https://github.com/JordanMPDS/laconic/issues/272

---

# Result: the file is not dilution, and it is not close

**540 generations, 0 failed, one `rules_cksum` (594915793), one CLI release
(2.1.266). No judging, per the stop-at-the-first-failing-step order.** The bound
the round set itself is met: `python3 evals/bench/release.py` reports no
unreadable span and no arm imbalanced across a release.

**Registered reading 2 obtains: both minimal slices are worse, in the same
direction, by a large margin.** They do not merely fail to beat the shipped
slice — they produce answers **1.7x and 2.1x longer** than it does, on every
cell, in both reading strata, on both case families. Nine length comparisons,
nine losses.

Reproduce with:

```sh
python3 evals/pilot/score_dilution.py evals/snapshots/loop/round-58-{a,b,c}.json
```

## Primary 2 — prose words, the endpoint that decides the round

Per-cell median prose words inside the grounded stratum ([#131]), permutation at
seed 58. Every cell is longer under both minimal slices.

| cell | `laconic` | `laconic-min-a` | p | `laconic-min-b` | p |
|---|--:|--:|--:|--:|--:|
| `design-cache` | 234.0 | 398.0 | 0.0001 | 477.0 | < 0.00001 |
| `design-realtime` | 144.0 | 176.0 | 0.0047 | 264.0 | < 0.00001 |
| `design-upload` | 189.0 | 303.0 | 0.0079 | 329.0 | 0.0005 |

Sign test: **0 of 3 cells shorter** for each minimal slice. Pooled over the
three cells, and shown in both strata because the round is entitled to only one
of them and the other is the check that the first is not a composition artifact:

| stratum | `laconic` | `laconic-min-a` | `laconic-min-b` |
|---|--:|--:|--:|
| grounded | 182.0 (n=30) | **303.0, 1.66x** (n=23) | **380.0, 2.09x** (n=37) |
| unread | 172.5 (n=60) | 212.0, 1.23x (n=67) | 321.0, 1.86x (n=53) |

All four pooled comparisons are at permutation p ≤ 0.00002. The effect is
present inside each stratum separately, so it is not [#131]'s marginal-median
trap and not [#209]'s mixture: no cell crossed a stratum boundary to produce it.

## Primary 1 — reading rate, where the two variants split

Share of responses with `num_turns > 1`, over the three `design-*` cells,
90 runs per arm. Non-inferiority margin registered at 15 points, one-sided.

| arm | rate | difference | lower bound | verdict |
|---|--:|--:|--:|---|
| `laconic` | 30/90, 33.3% | — | — | — |
| `laconic-min-a` | 23/90, 25.6% | −7.8 pts | −18.7 | **inferior** at the registered margin |
| `laconic-min-b` | 37/90, 41.1% | +7.8 pts | −4.0 | non-inferior |

Neither difference against `laconic` separates (Fisher p = 0.3265 and 0.3549).
**The two minimal slices differ from each other more than either differs from
the shipped slice** — 23/90 against 37/90, Fisher **p = 0.0394** — which is
precisely what the two-variant design was bought to detect. Reading rate here is
a property of the particular wording, not of minimality, and this round makes no
claim about minimality and reading rate in either direction.

That is worth stating as a method result rather than a footnote. With one
minimal arm this round would have reported either "a minimal slice suppresses
reading" or "a minimal slice does not", on a 7.8-point difference in the
direction the single draft happened to fall.

## Guardrail — the never-cut contract

**0 failures of 90 runs on every arm**, pooled over `destructive`,
`code-fidelity` and `badnews`. The alarm did not fire, and as registered it
certifies nothing: the rule of three bounds each arm's failure rate at about
3.3% and the shipped slice's own count is 0, so this round has no power to
detect a contract regression smaller than catastrophic. What it does establish
is that the minimal slices were not shortened by dropping the contract, which is
the one way the length result could have been trivial in the other direction.

## Exploratory, registered as such

Not in the registered scope, computed after the numbers were in, and not citable
as a result. Median prose words on the three contract cases, all runs:

| case | `laconic` | `laconic-min-a` | `laconic-min-b` |
|---|--:|--:|--:|
| `destructive` | 136.5 | 193.5 | 227.0 |
| `code-fidelity` | 26.5 | 41.0 | 73.5 |
| `badnews` | 9.5 | 36.0 | 60.0 |

Every one at permutation p < 0.00001. The gap widens as the correct answer gets
shorter: on `badnews`, where the whole job is to say plainly that three tests
still fail, the shipped slice answers in 9.5 words and the minimal slices in 36
and 60. So the length effect is not confined to the design family the primary
endpoint was scoped to.

Action scope is flat — median 7 turns in the grounded stratum on all three arms
— so no arm bought its length by doing more or less work.

## What this settles, and what it does not

**[#270]'s third outcome obtains, and the issue closes.** Dilution is ruled out
on this content specification: the six nulls of rounds 44 to 49 are facts about
their clauses, not artifacts of a file too large for any one clause to move.
A reader should take the six nulls at face value from here.

**The direction is the finding, not just the verdict.** The dilution hypothesis
predicts that a slice carrying the same instructions in a quarter of the words
does at least as well. Both slices carry every instruction with a measured
effect, the whole never-cut contract, the thesis sentence, the level-`full`
cuts, round 55's pre-action check and the rounds 26/28 licence — and both come
in at roughly double the length. Whatever produces laconic's compression is
substantially in the **750 words the minimal slices dropped**: the worked OOM
example and its level table, the arrow section with its four `Wrong:`/`Right:`
pairs, the section headings, and the six clauses measured at zero.

Three limits, all of them real:

- **It does not say which of those 750 words matter.** The obvious candidate is
  the demonstrations — the file teaches brevity by showing short answers, and
  both minimal slices removed every rendered instance while keeping every
  instruction. That is an ablation this round did not run, and it is filed as a
  separate issue rather than asserted here.
- **No quality was judged.** Step 2 was registered as conditional on step 1 and
  step 1 killed the round, so nothing here says the minimal slices give worse
  answers — only longer ones. On this product that is the axis, but it is one
  axis.
- **Two drafts, one author, one sitting.** A third minimal slice could beat
  both. What the two-variant design bounds is the reading a single draft cannot
  bound: two slices differing in almost every phrase lost in the same direction
  by 1.66x and 2.09x, which is much harder to attribute to one bad draft than a
  single loss would be. And they demonstrably do differ — they separate from
  each other on reading rate at p = 0.0394.

**The prior art does not transfer, and the reason is worth recording.**
SimpleEnglish's eight-line prompt beat its own 50-plus rule skill on every
reader-visible column. The same experiment run here inverts: the long file wins
on the reader-visible column by a factor of two. The difference between the two
projects is not the design of the test, which is the same test — it is that
[`LEDGER.md`](LEDGER.md) has 30 attempts in it and that four of the clauses in
the shipped slice were put there by a round that measured them. A rule
catalogue's length is not by itself evidence of dilution, and this round is the
measurement that separates the two cases.
