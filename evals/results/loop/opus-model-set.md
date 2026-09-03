# Opus: does the compression claim generalise off the two models that made it?

**Status: pre-registration. No number below the line has been computed.** The
predictions and their bars are written here first, and the batch that scores
them is generated afterwards, so the scope cannot be chosen once the numbers
are in.

Answers step 1 of [#117].

## The question

`docs/benchmark.md` publishes every figure off two models, `haiku` and
`sonnet`, and says so under Scope. The compression headline — laconic cuts
Sonnet output 32% and Haiku output 9% — is therefore a claim about two points
on one vendor's ladder, and the gap between those two points is the reason the
question matters. On Haiku the median saving is 9% with eight of 22 cells
negative; on Sonnet it is 32%. Two points cannot say whether that is a
capability gradient or something specific to Sonnet, and the answer changes
what the plugin should tell a user about which models it helps.

Opus is also the model this repository is maintained from, so the one model the
plugin's own author runs is the one it has never been measured on.

## The design, and what it fixes about round 21

One interleaved batch. Three models, two arms, the 22 cases round 21 covered,
five reps: 660 generations.

```sh
python3 evals/bench/run.py --arms baseline,laconic --models <model> --reps 5 \
  --cases '<the 22>' --concurrency 4 --snapshot <shard>
```

Two things about this design are deliberate and neither is round 21's.

**Both arms are generated in the same batch.** Round 21's baseline is carried
from round 20 and is eleven days and eleven CLI patch releases older than its
laconic arm. Round 37 then measured a syntactic behaviour moving 4.7x in five
days at byte-identical rules, so a cross-era arm comparison is exactly the
exposure to avoid. Every reduction figure below is laconic against a baseline
generated beside it, on the same day and the same CLI.

**It runs at the rules this repository ships.** Every published figure is at
`rules_cksum` 1830906901, two accepted edits behind master's 136269960, and
`docs/benchmark.md` says in as many words that no round-wide 22-case benchmark
has been generated at the shipped revision. This is that batch, which makes the
sonnet column news in its own right rather than only a control for the opus one.

## What is not bought, and why

`terse-control`, `word-compression` and `concise-style` are not generated. The
question registered here is whether *the compression claim* generalises, and
that claim is laconic against baseline; the three other arms are what rank the
field, which is a different question and roughly $50 more of Opus. So this
batch cannot restate round 21's five-arm table, and in particular **it cannot
say whether `concise-style` still out-compresses laconic on Opus** — round 21's
sharpest negative result. That stays open and belongs to step 2 of [#117].

Preference is not bought either, per the standing rule.

## Predictions, registered before the batch

| # | prediction | bar |
|---|---|---|
| 1 | The gradient is monotone in capability | median per-cell reduction: haiku < sonnet < opus |
| 2 | Fewer cells get *longer* under laconic as capability rises | negative cells: opus < sonnet < haiku |
| 3 | The matched sonnet figure restates the published one | sonnet reduction within 10 points of −32% |
| 4 | The quality deficit does not widen with capability | on opus, laconic's pass rate over the quality-graded cases is no more than 10 points below baseline's |

Bars 1 and 2 are the capability-gradient hypothesis stated two ways, one on the
central tendency and one on the tail; a gradient that shows up on neither is not
a gradient. Bar 3's 10-point band is the width the headline has already moved
across publications — 28%, 33%, 38%, 32% — so anything inside it restates the
claim and anything outside it is news about the matched design or the shipped
rules. Bar 4 is loose on purpose: round 21 read laconic 59.7% against baseline
68.1% at z = −1.45, which is not a demonstrated regression, and a bar tighter
than the effect round 21 could not resolve would be scored on noise.

Readability violations, never-cut failures, latency and cost are reported as
disclosure. They carry no bar, because nothing here predicted them.

[#117]: https://github.com/JordanMPDS/laconic/issues/117

---

## Results

**Status: scored.** Everything above this line was committed in 1d37de5, before
the batch ran.

### What was generated, and what was judged

660 generations, 0 failed: 22 cases x 3 models x 2 arms x 5 reps, level `full`,
`rules_cksum` 136269960, `cases_cksum` 2389944869, CLI 2.1.258, 2026-09-02 19:05
to 2026-09-03 00:35 UTC. They were produced by seven `run.py` processes, each
owning one shard file and each strictly sequential, with `--concurrency 7`
declared on every one. The seven shards are committed beside the merged
snapshot, and [`evals/bench/merge.py`](../../bench/merge.py) is what unions
them: `metadata.shards` in `opus-model-set.json` names every one, so the merge
can be re-run and checked rather than taken on trust.

Judging is scoped to the **14 quality-graded cases**, 420 verdicts, which is the
set that supports an arm comparison at all and the only judged quantity any bar
names. The other eight cases — five `safety`, three `rule-adherence` — grade a
contract the treatment arm was instructed to follow and the control was not, so
their verdicts cannot be read as laconic against baseline; `docs/benchmark.md`
says so under Scope. Not buying them is a deliberate omission, and it means
**this round says nothing about whether opus is safer or less safe under
laconic.** That is unmeasured, not measured-and-fine.

The round cost $64.08: $48.57 for 660 generations, $15.50 for 420 judgments.

### The headline: the gradient is real and it is steep

Median output tokens, and the reduction the published figure is computed from —
the ratio of the two arms' medians of per-cell medians:

| | haiku | sonnet | opus |
|---|--:|--:|--:|
| baseline median tokens | 752 | 2,256 | 4,864 |
| laconic median tokens | 682 | 1,585 | 1,552 |
| **reduction** | **9%** | **30%** | **68%** |
| median per-cell reduction | +8.5% | +43.1% | +62.4% |
| cells where laconic is longer | 6 of 22 | 0 of 22 | 0 of 22 |
| cells reduced, sign test | 16/22, p = 0.052 | 21/22, p = 1.1e-05 | 22/22, p = 4.8e-07 |

The two instruments disagree by a lot on sonnet — 30% pooled against 43.1%
per-cell — because the pooled figure divides one median by another and is
therefore weighted by the cases with the most tokens to give up, while the
per-cell median weights every case alike. Both are reported throughout. Bar 3 is
scored on the pooled one, because that is the instrument that produced the −32%
it is a prediction about.

Opus reduces **every one of the 22 cases**, by between 27% and 81%.

### The bars, scored

| # | prediction | bar | result |
|---|---|---|---|
| 1 | The gradient is monotone in capability | median per-cell reduction: haiku < sonnet < opus | **met.** +8.5% < +43.1% < +62.4% |
| 2 | Fewer cells get longer as capability rises | negative cells: opus < sonnet < haiku | **not met, on a tie at the floor.** 0, 0, 6 |
| 3 | The matched sonnet figure restates the published one | within 10 points of −32% | **met.** 30%, 2 points off |
| 4 | The quality deficit does not widen with capability | opus laconic no more than 10 points below baseline | **met.** 91.4% against 91.4%, exactly equal |

**Bar 2 is scored as a failure and it should not be read as one.** It was
registered as a strict ordering, and `opus < sonnet` is false because both are
zero: the tail this bar was built to track has already collapsed at sonnet, so
opus has nothing left to improve on. The bar cannot distinguish "no gradient in
the tail" from "the gradient ran out of room", and on this batch it is the
second. Writing it as a strict inequality on a quantity with a floor at zero was
the mistake, and it is recorded here rather than repaired after the fact.

Bars 1 and 2 were registered as the same hypothesis stated on the central
tendency and on the tail, with the note that "a gradient that shows up on
neither is not a gradient". It shows up on one of the two, decisively.

### Every cell

Per-cell reduction, laconic against baseline, medians of 5 reps each:

| case | haiku | sonnet | opus |
|---|--:|--:|--:|
| `badnews` | +5% | +0% | +46% |
| `code-fidelity` | +22% | +45% | +74% |
| `conditional` | +8% | +42% | +62% |
| `decision` | +12% | +71% | +62% |
| `design-alerting` | +7% | +46% | +80% |
| `design-audit-log` | +43% | +51% | +77% |
| `design-cache` | +19% | +26% | +67% |
| `design-rate-limit` | +11% | +63% | +71% |
| `design-realtime` | **−26%** | +35% | +81% |
| `design-retry` | **−7%** | +45% | +68% |
| `design-search` | **−28%** | +40% | +77% |
| `design-upload` | +13% | +29% | +65% |
| `destructive` | +12% | +35% | +47% |
| `fail-open` | +7% | +55% | +48% |
| `floor` | +9% | +64% | +69% |
| `ordered-steps` | +23% | +57% | +56% |
| `silent-success` | +9% | +48% | +28% |
| `stale-cache` | **−41%** | +30% | +39% |
| `verdict-experiment` | +7% | +45% | +48% |
| `verdict-rollout` | **−10%** | +20% | +63% |
| `verdict-schema` | **−5%** | +35% | +38% |
| `walkthrough` | +9% | +34% | +27% |

`badnews`/sonnet is a genuine tie rather than a rounding artefact: both arms have
a median of 453 tokens. It is the one sonnet cell the sign test does not count as
a reduction, and it is not counted as an increase either.

### Quality: no deficit anywhere, and the level rises with capability

Pass rate over the 14 quality-graded cases, 70 responses per arm per model:

| | baseline | laconic | Fisher |
|---|--:|--:|--:|
| haiku | 29/68 = 42.6% | 37/65 = 56.9% | p = 0.120 |
| sonnet | 54/70 = 77.1% | 56/69 = 81.2% | p = 0.677 |
| opus | 64/70 = 91.4% | 64/70 = 91.4% | p = 1.000 |

Denominators differ from 70 where a verdict came back `not_exercised`, which is
counted as neither a pass nor a fail.

Round 21 read laconic 59.7% against baseline 68.1% at z = −1.45 and called it
undemonstrated. On a batch where both arms are generated side by side, at the
shipped rules, the sign of that gap is **reversed on two models and zero on the
third**, and no comparison is close to significant. The deficit round 21
reported does not reproduce. Bar 4 predicted the deficit would not widen with
capability; what happened is that it is not there to widen.

The quality level itself is strongly ordered by capability on both arms, 42.6%
to 77.1% to 91.4% on baseline. That is a property of the case set rather than of
laconic, and it is worth saying because it bounds what the opus column can show:
at 91.4% there are six failures per arm to move, so this batch could not have
detected a small opus-specific regression even if one existed.

### Disclosure

Nothing below carried a bar.

**Readability violations** — the arrows-and-fragments gate, counted over all 110
responses per arm per model:

| | haiku | sonnet | opus |
|---|--:|--:|--:|
| baseline, total | 50 | 52 | 76 |
| laconic, total | 19 | 19 | **1** |
| baseline, responses with ≥1 | 20 | 24 | 38 |
| laconic, responses with ≥1 | 9 | 8 | **1** |

Opus is where the rules text actually lands. Its baseline is the *worst* of the
three — 76 violations across 38 of 110 responses, mostly arrows — and its
laconic arm is the best result this benchmark has recorded from any arm on any
model: one violation in 110 responses. The prohibition that haiku and sonnet
half-follow, opus follows.

**Never-cut failures**, deterministic keyword check, 75 checked responses per
arm: baseline 2, laconic 1. Unchanged from round 21's reading and far too small
to separate.

**Reading rate.** Responses that called no tool at all, out of 110:

| | baseline | laconic | Fisher |
|---|--:|--:|--:|
| haiku | 46 | 51 | p = 0.587 |
| sonnet | 29 | 35 | p = 0.458 |
| opus | 5 | 13 | p = 0.083 |

Laconic answers without reading slightly more often on every model, and on none
of them significantly. The opus contrast is the closest to a signal and the one
worth watching, because reading is the covariate that predicts quality here
([#46]): opus reads on 105 of 110 baseline responses against 97 of 110 under
laconic. Its quality did not move, so on this batch the extra 8 unread answers
cost nothing measurable — but 13 against 5 is the kind of ratio that would matter
at a larger n, and this round did not power it.

**Latency and cost per call**, medians:

| | baseline | laconic | change |
|---|--:|--:|--:|
| haiku duration | 10.1 s | 9.8 s | −2% |
| sonnet duration | 28.2 s | 20.8 s | −26% |
| opus duration | 71.3 s | 24.1 s | **−66%** |
| haiku cost | $0.0146 | $0.0135 | −8% |
| sonnet cost | $0.0594 | $0.0491 | −17% |
| opus cost | $0.2014 | $0.1098 | **−45%** |

The opus rows are the practical result. A 45% cost reduction on the most
expensive model in the set is a larger absolute saving per call than the entire
cost of a haiku call in either arm.

## What this answers, and what it does not

**The compression claim generalises, and it understates itself on the model this
repository is maintained from.** The published headline is a sonnet claim of
−32%; on opus the same instrument reads −68%, every case reduces, and the
readability violations the gate exists to count nearly vanish. The gradient
across the three points is monotone and steep, which is consistent with capacity
rather than with something specific to sonnet — three points is still three
points, and one vendor is still one vendor.

**Haiku is where the plugin's claim is weak, and this round sharpens why.** At
+8.5% per-cell with six cases longer and a sign test at p = 0.052, the honest
statement for haiku is that laconic does not reliably shorten it. That was
visible in round 21 and is unchanged by a matched batch at the shipped rules, so
it is not an artefact of round 21's cross-era baseline.

**What stays open, all of it step 2 of [#117]:**

- **Whether `concise-style` still out-compresses laconic on opus.** Round 21's
  sharpest negative result, and this batch cannot speak to it: the three control
  arms were not generated, per the pre-registration.
- **Whether opus joins the loop's per-round model set.** It needs its own
  `cell-rates.json` measurements first — 22 unmeasured cells — and the round-wide
  fatal counters have to be restated before any round can be scored across the
  boundary.
- **Whether opus saturates any cell.** `saturated_models` in every `expect.json`
  is measured on haiku and sonnet only.
- **Safety and rule-adherence on opus.** Not judged here, as stated above.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
