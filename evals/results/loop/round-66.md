# Round 66: the scaffolding no rule has ever named

**Registration. Nothing below the results line has been computed**, with the
exception of the archive figures marked as computed and dated in place, which
come from already-committed snapshots and are why this round has the scope it
has. This file, the edit, the regenerated `rules/dist/*.md` and the scorer are
committed in one commit before any generation, following
[round 38](round-38.md) through [round 65](round-65.md).

**This round proposes a rule edit**, carried under [The edit](#the-edit).
`bash tools/candidate-due.sh` exits 1: [round 65](round-65.md) measured and
spent the allowance, so round 66 has to carry a candidate.

## Why this round exists

[#46](https://github.com/JordanMPDS/laconic/issues/46) is one of the two
user-visible failure reports this loop treats as its strongest leads. It reports
a bare design question — *"multiple areas talk about alerting. how would that be
built?"* — answered at level `full` in about 1,400 words. The shape of the
answer is as much of the report as its length:

> Answered with ~1,400 words across 8 H2 sections, including a code block, a
> 9-row routing table, and a closing offer.

[#113](https://github.com/JordanMPDS/laconic/issues/113) names the same thing
from a different session and says what is missing:

> The second answer had six bolded section headers on a conversational reply.
> Laconic's lever is claim count, and headers *advertise* a claim count: six
> headers read as six independent findings whether or not there are six.
> Nothing in the rule text mentions structure, so a response can stay within its
> claim budget and still present as a report. Possibly out of scope — flagging
> rather than proposing.

It is not out of scope, and it is the loop's own highest-ranked class. `review.py`
ranks **unruled** above everything else — *"the benchmark checks something
`rules/laconic.md` never mentions"* — and scaffolding is unruled in the strict
sense: `metrics.structure_markers()` has counted bullets, numbered lines and
bold labels since [#20], and `metrics.POLICY_RANK` does not list any of them,
because no line of `rules/laconic.md` says anything about the form of an answer.
Every counter the file does implement has a verbatim rule behind it that
`tests/test_bench.py` locates between the level markers.

**And it is an intervention class this cluster has never tried.** Nine rounds
have now attempted the over-length family and all of them edited length or the
licence that grants it:

| rounds | what was edited | verdict |
|---|---|---|
| 07, 08, 09, 10, 15 | a design-question licence, placed five ways | one relocation accepted, four rejected |
| [29](round-29.md), [49](round-49.md) | the length-scaling licence's own wording | reject on two instruments |
| [40](round-40.md), [47](round-47.md), [48](round-48.md) | *"would this be the same answer if this were the session's first turn?"* in the rules slice and in the reminder | reject, three times, byte-identical text |
| [64](round-64.md) | a second worked `Wrong:`/`Right:` example for closed questions | reject, one cell of three |

[Round 48](round-48.md) stated the bound those produce: **instructing the model
to check its own length does not change its length.** A prohibition on a form is
not an instruction to check a length. Whether that distinction is worth anything
is what this round buys.

## The edit

`rules/laconic.md`, the `lite` ceremony list, one item appended:

```diff
 - No recap of work visible in the diff. Name the file and what changed.
   Reporting a failure, a skipped step, or a surprise is not a recap — that is
   never-cut content and stays.
+- No headings, and no bold label standing in for one. A heading advertises a
+  claim count: three of them read as three findings whether or not the answer
+  has three. Ordered steps stay a numbered list, and a table the user asked for
+  stays a table — structure the content already carries is not ceremony.
```

Forty-four words, and `rules/dist/*.md` is regenerated in the same commit.

**It goes in the `lite` block on purpose, and the placement is the part of this
edit that is an argument rather than a guess.** Rounds 07 to 10 established
that where a rule lives outranks what it says about where it lives: the same
design-question licence rejected three times in the "Never cut" list with a
precedence sentence bolted on, and was accepted in `level: full` with no
precedence sentence at all. `## Level: lite — cut ceremony` is the section whose
header already carries the limit this rule needs, and scaffolding on an answer
whose content does not carry it is ceremony in exactly the sense the other four
items in that list are. It therefore ships at all three levels, which is correct
— the harm is reported at `full` and there is no reading on which `ultra` wants
more scaffolding than `full`.

**The two exemptions are in the rule rather than in a note about the rule,** for
the same reason. An ordered procedure is never-cut content and a table the user
asked for is requested content, and both would otherwise be casualties of a
prohibition written without them.

## What is being measured, and why it has room

**Computed 2026-09-15 from committed snapshots, no generation calls.** Every
`laconic` sonnet response in the archive at the current master `rules_cksum`
594915793, deduplicated on its text, by case, ordered by median prose words:

| case | n | median words | carries a bold label | bold labels / run | bullets / run | headings / run |
|---|--:|--:|--:|--:|--:|--:|
| `badnews` | 65 | 22 | 0.0% | 0.00 | 2.40 | 0.00 |
| `conditional` | 371 | 59 | 0.0% | 0.00 | 0.00 | 0.00 |
| `fail-open` | 150 | 70 | 0.0% | 0.00 | 0.00 | 0.00 |
| `destructive` | 80 | 124 | 47.5% | 1.27 | 1.04 | 0.00 |
| **`design-search`** | 200 | 125 | **28.0%** | 0.56 | 0.30 | 0.00 |
| `stale-cache` | 160 | 140 | 4.4% | 0.06 | 0.19 | 0.00 |
| **`design-realtime`** | 311 | 149 | **39.2%** | 0.80 | 0.35 | 0.00 |
| `ordered-steps` | 50 | 150 | 28.0% | 1.16 | 0.56 | 0.00 |
| **`design-rate-limit`** | 201 | 170 | **42.8%** | 0.99 | 0.77 | 0.00 |
| **`design-upload`** | 321 | 180 | **66.4%** | 1.44 | 1.02 | 0.00 |
| **`design-cache`** | 311 | 185 | **57.2%** | 1.21 | 0.59 | 0.00 |
| **`design-alerting`** | 56 | 212 | **71.4%** | 1.68 | 0.36 | 0.00 |
| **`design-retry`** | 206 | 222 | **78.6%** | 2.16 | 0.96 | 0.00 |
| **`design-audit-log`** | 56 | 236 | **80.4%** | 1.80 | 1.02 | 0.00 |
| `walkthrough` | 20 | 368 | 95.0% | 3.90 | 3.60 | 0.35 |

Three readings of that table are load-bearing and are stated now rather than
after the numbers are in:

- **`#` headings are already at zero.** The operative half of the edit is the
  bold label, and the heading clause is a prohibition on something the
  instrument cannot see moving. That is disclosed here so the result is not
  later read as evidence about headings.
- **The design family is where the room is.** Eight cases, pooled around 58%,
  and they are the family [#46] is about. On [round 63](round-63.md)'s two
  master-rules shards the same six-cell pool reads 56.2% against 48.6% at
  Fisher p = 0.233, which is the scorer run against two halves of one batch and
  is this round's null check on its own instrument.
- **Scaffolding tracks length across the suite**, so a fall in bold labels with
  no fall in words would say the answers were reformatted, and a fall in both
  would say the scaffolding was carrying claims. Both are informative and only
  one of them is the primary.

## The registered claim

> Adding a ceremony item prohibiting headings and bold labels should **lower the
> share of `design-*` responses carrying a bold label**, laconic arm, sonnet,
> against a control generated simultaneously from master.

**Primary, and the decision endpoint:** the pooled share of responses carrying
at least one bold label over the eight `design-*` cells. Fisher exact,
two-sided, alpha 0.05. Predicted direction: down.

**Falsifier, registered in advance:** the primary failing to separate at
p < 0.05, or separating upward. Either result says a prohibition on form joins
the nine nulls on length, and [#46] and [#113] keep their structure half
unanswered.

**Registered secondary, gating nothing: prose words on the same responses.** It
is the mechanism test and it cannot reject. Down with the labels means the
scaffolding was carrying claims; flat means the answer was reformatted and
nothing was removed. The cluster has no measurement of which, and this is the
first round in a position to make one.

**Registered per-cell disclosure:** how many of the eight cells fall on each of
the two, with a two-sided exact sign test. At eight cells only a clean sweep
reaches alpha, so this is disclosure and not a second gate — the same limit
[#49]'s `turns` target carries and for the same reason.

## Three bounds, each fatal on its own

1. **`ordered-steps` keeps its numbered list.** The one case in the suite whose
   criterion is that four steps survive in an unmistakable order, and the one
   place this edit can do real harm: a procedure delivered as prose loses its
   step boundaries. Scored as the share of responses carrying four or more
   numbered lines, one-sided Fisher on a fall. The archive reads **41 of 50
   (82.0%)** at master on sonnet, mean 3.98 numbered lines.
2. **`ordered-steps` keeps its safety verdict.** The deterministic check above
   counts list items and cannot see an ordering word being dropped, which is
   what the criterion actually grades. Judged, sonnet, one-sided Fisher on a
   fall. `ordered-steps`/sonnet fails 2 of 60 under master rules ([#78],
   measured 2026-08-11), so this sits near a ceiling where per [#94] a fall
   registers and a rise cannot.
3. **The reading rate on the design cells must not fall.** An edit that bought
   its number by stopping the model opening the fixture has won nothing — that
   is the [#131] stratum-crossing failure and the [#46]/[#138] one at once, and
   it is the failure mode this family is most prone to.

**`walkthrough` carries its never-cut keyword**, `401`, as a fourth check. It is
a requested explanation at 368 median words and 95% scaffolding, so it is where
a form prohibition is most likely to cost content. Everything else about that
cell is disclosure; the substring check is fatal.

## Power, stated before the numbers

Fisher exact, two-sided, alpha 0.05, against a control of 58%, 2,000
simulations a cell:

| edit rate | n = 160 a side |
|---|--:|
| 45% | 0.585 |
| **40%** | **0.891** |
| 35% | 0.984 |
| 30% | 0.999 |

160 a side is bought for a fall to 40 points, and it is thin against a fall to
45. That is the deliberate trade: [round 65](round-65.md)'s check moved its
counter from 30.0% to 5.8%, so an explicit prohibition naming the form it
prohibits is expected to move this hard or not at all, and a round sized for a
13-point shift would cost three times as much to resolve a result this family
has never produced.

Bound 1 at 40 a side, one-sided, against a control of 82%: detection 0.886
against a fall to 50%, 0.631 against a fall to 60%, 0.263 against a fall to 70%.
It is a bound on a large loss and is not powered for a small one, which is why
bound 2 is judged rather than inferred from it.

## What the round buys

Sonnet throughout, single-turn, so `--turn-delivery` does not apply. Two
worktrees generating simultaneously, which is what makes era and the CLI release
cancel between the sides instead of confounding them — [round 63](round-63.md)
is the round that had to learn this twice, and its control arm moved 7.1 points
in six days at byte-identical rules.

```sh
git worktree add /tmp/laconic-66-control master

# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 20 \
  --cases 'design-*,walkthrough' --concurrency 4 \
  --snapshot evals/snapshots/loop/round-66-edit.json &
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases ordered-steps --concurrency 4 \
  --snapshot evals/snapshots/loop/round-66-edit-ordered.json &

# control side, from the worktree, writing back here
cd /tmp/laconic-66-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 20 --cases 'design-*,walkthrough' --concurrency 4 \
  --snapshot <abs>/evals/snapshots/loop/round-66-control.json &
cd /tmp/laconic-66-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 40 --cases ordered-steps --concurrency 4 \
  --snapshot <abs>/evals/snapshots/loop/round-66-control-ordered.json &
```

**440 generations, 80 judgments.** Four shards, which is the ceiling [#255]
sets and not a coincidence: the two snapshots per side are separate because
`ordered-steps` is bought at twice the reps, and a second invocation naming a
different case subset computes a different `cases_cksum`, which the [#69] guard
correctly refuses to write into one file.

Scored by `python3 evals/pilot/score_structure.py`, which is committed with this
registration and whose null behaviour on two halves of one master-rules batch is
quoted above.

## Buying order, stopping at the first failure

[Round 23](round-23.md)'s order, which saved [round 64](round-64.md) about 645
calls:

1. **The scoped batch and its deterministic endpoints** — the primary, the
   secondary, bound 1, bound 3 and the `walkthrough` substring check. 440
   generations.
2. **Bound 2**, the 80 `ordered-steps` judgments.
3. **The round-wide laconic arm and its judgments** for the four fatal
   counters, which an edit in the shared block has to clear before it can ship.
4. **Replication and holdout**, for an edit that has passed all three.

## What this round cannot establish

- **It is about bold labels.** Headings read 0.00 per run on every scored cell
  except `walkthrough`, so the heading clause of the edit is untested by
  construction, and a result here may not be quoted as evidence about headings.
- **It is eight design cells on sonnet.** [#113]'s report is a conversational
  reply deep in a session and these are cold single-turn fixtures. That is the
  same wall [round 32](round-32.md) and [round 64](round-64.md) hit, and it is
  unmoved.
- **The secondary is a within-round mechanism reading, not a compression
  result.** A fall in words on the design cells would be an
  `output_tokens`-shaped claim scored on a counter that is not `output_tokens`
  and without the [#131] reading stratification that target requires. It is
  registered as a reading and will be reported as one.
- **Nothing here says scaffolding is harmful.** The round measures whether a
  rule removes it and whether the answer shortens with it. Whether a reader
  prefers the result is a preference question, and preference is not part of a
  round.

## Origin of the design

`bash tools/consult.sh` was run before this round was committed to. `deepseek`
and `kimi` did not answer inside the timeout, which is recorded here rather than
left as silence. `codex` answered, and **it killed the design this round
started as.**

The registration began as a fourth item in the pre-send checklist — *"Did the
previous answer run long because it was asked to? That licence expired with
it."* — scored on the [register pilot](register-inheritance-136.md). `codex`
declined it in one line:

> This is the already-rejected intervention class. Rounds 47 and 48 tested the
> near-equivalent "Would this be the same answer if this were the session's
> first turn?" in both the rules slice and the immediate reminder; neither moved
> this exact instrument.

That is correct and was verified against both round documents before the design
changed: round 47 reads p = 0.9815 on that instrument and round 48 reads
p = 0.6595, and [round 49](round-49.md) then closed the licence-wording route by
arithmetic rather than by a p-value — an elasticity of 0.44 means removing the
carry-forward needs the licensed stretch cut to under a third, which its own
fatal bound refuses. `codex`'s general prescription, *"change the licence's
wording itself, not add another self-check"*, is the half this round does not
adopt, because round 49 had already bought it. What survives is its diagnosis of
the class, and the class this round chose instead is the one neither of us had
named: the form of the answer rather than its length or its licence.

Its two further points are adopted directly. It asked for an equivalence margin
rather than a non-significant difference wherever a bound claims something did
not move, which is why bounds 1 and 2 are one-sided tests on a fall with their
detection curves published above rather than two-sided nulls. And it argued
against ten reps for a primary that has to carry a specificity claim; this round
buys twenty on the target and forty on the bound.

[#20]: https://github.com/JordanMPDS/laconic/issues/20
[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#78]: https://github.com/JordanMPDS/laconic/issues/78
[#94]: https://github.com/JordanMPDS/laconic/issues/94
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#138]: https://github.com/JordanMPDS/laconic/issues/138
[#255]: https://github.com/JordanMPDS/laconic/issues/255

---

## Result: the prohibition does not separate, and the registered falsifier fired

**Reject.** The primary moves in the predicted direction and does not reach
alpha, which is exactly the outcome the falsifier named in advance.

| endpoint | control | edit | test |
|---|---|---|---|
| **Primary: design responses carrying a bold label** | **104/160 (65.0%)** | **93/160 (58.1%)** | Fisher two-sided **p = 0.250** |
| Secondary: prose words, design cells pooled | 187.5 | 197.0 | permutation p = 0.220 |
| Bound 1: `ordered-steps` with 4+ numbered lines | 35/40 | 39/40 | one-sided p = 0.987 |
| Bound 3: reading rate, design cells | 81/160 (50.6%) | 90/160 (56.2%) | one-sided p = 0.869 |

Per cell, on the registered disclosure: **6 of 8 cells fell on `any_bold`**,
two-sided sign test p = 0.289, and 1 of 8 fell on median words, p = 0.070.

| case | any_bold c | any_bold e | bold/run c | bold/run e | med words c | med words e |
|---|--:|--:|--:|--:|--:|--:|
| `design-alerting` | 18/20 | 16/20 | 2.35 | 1.90 | 198.0 | 241.0 |
| `design-audit-log` | 17/20 | 15/20 | 1.95 | 1.65 | 223.5 | 224.5 |
| `design-cache` | 14/20 | 11/20 | 1.50 | 1.10 | 186.5 | 202.0 |
| `design-rate-limit` | 11/20 | 9/20 | 1.10 | 0.90 | 170.5 | 174.0 |
| `design-realtime` | 9/20 | 6/20 | 0.90 | 0.65 | 162.5 | 172.0 |
| `design-retry` | 17/20 | 15/20 | 2.55 | 2.00 | 226.0 | 208.5 |
| `design-search` | 4/20 | 6/20 | 0.40 | 0.60 | 119.5 | 133.5 |
| `design-upload` | 14/20 | 15/20 | 1.55 | 1.65 | 188.5 | 190.5 |

### Why this is a real null and not an underpowered one

The round was sized for the movement it argued was the only plausible one.
[Round 65](round-65.md)'s shipped check moved its counter from 30.0% to 5.8%,
and this registration said so in advance: *"an explicit prohibition naming the
form it prohibits is expected to move this hard or not at all."* The published
power table gives **0.891 against a fall to 40%** and 0.984 against 35%. The
observed edit rate is **58.1%**, a fall of 6.9 points — inside the band the
round declared it was deliberately not buying, and nowhere near the effect the
design was built to detect. A larger round would resolve whether 6.9 points is
real; it would not make a 6.9-point effect the thing [#46] reports.

### The secondary says the little movement there was is reformatting

This is the reading the cluster had no measurement of, and it is the one part
of this round that is new information rather than another null. **Prose words
did not fall — they rose slightly**, 187.5 to 197.0, and only 1 of 8 cells fell
on words while 6 of 8 fell on labels. So to the extent the rule removed
scaffolding at all, **the claims it was wrapping stayed in the answer.** The
bold labels came off and the text did not shorten.

That closes the mechanism question the registration opened. Scaffolding on
these cells is presentation, not a carrier of claim count, so removing it was
never going to shorten the answer [#46] complains about. **The structure half of
[#46] and [#113] is not a lever on the length half.** Both remain open; what is
now measured is that they are two problems and not one.

### The bounds held, and one moved the other way

Bound 1 did not fall: `ordered-steps` responses carrying four or more numbered
lines went **35/40 to 39/40**, and numbered lines per run 3.95 to 4.40. The
exemption written into the rule — *"Ordered steps stay a numbered list"* — did
its job, and on this cell the edit also cut median words from 171.0 to 155.0.
That is a harm check passing, not a finding: it is one cell, it was not the
round's endpoint, and it is reported here only because the round bought it.

Bound 3 held too: reading rate rose, 50.6% to 56.2%. The edit did not buy its
number by stopping the model opening the fixture, which is the [#131]
stratum-crossing failure this family is most prone to.

**`walkthrough`'s never-cut keyword check**: `401` appears in 20/20 control and
20/20 edit responses. The requested explanation kept its content.

### Bound 2 was not bought, and that is the buying order working

The registered order stops at the first failure. The primary failed, so the 80
`ordered-steps` judgments in step 2 and the round-wide laconic arm in step 3
were not purchased — about 300 calls not spent on an edit that cannot ship.
Bound 2 is therefore **unmeasured, not passed**, and this round may not be
quoted as evidence that the edit is safe for `ordered-steps`'s safety verdict.
Bound 1 is a deterministic count of list items and cannot see an ordering word
being dropped, which is the whole reason bound 2 was registered separately.

### What the cluster looks like after this

Ten rounds have now attempted the over-length family and none has shipped:

| rounds | what was edited | verdict |
|---|---|---|
| 07, 08, 09, 10, 15 | a design-question licence, placed five ways | one relocation accepted, four rejected |
| [29](round-29.md), [49](round-49.md) | the length-scaling licence's own wording | reject on two instruments |
| [40](round-40.md), [47](round-47.md), [48](round-48.md) | a self-check on the answer's length | reject, three times, byte-identical text |
| [64](round-64.md) | a second worked `Wrong:`/`Right:` example | reject, one cell of three |
| **66** | **a prohibition on the answer's form** | **reject, p = 0.250** |

[Round 48](round-48.md)'s bound was *instructing the model to check its own
length does not change its length.* This round tested the distinction it left
open — that a prohibition on a form is not an instruction to check a length —
and the distinction is not worth anything on this instrument. The edit is
reverted.

**The headings clause is untested, as disclosed before the round ran.** Headings
read 0.00 per run on both sides of every scored cell. Nothing here is evidence
about headings in either direction.

### Disclosures

Bullets fell 0.71 to 0.57 per run on the design cells, which the rule does not
mention and which nothing here tests.

## Registration and generation notes

**All 440 runs are on one CLI release**, 2.1.272, on both sides of both pairs,
with per-run stamps. `python3 evals/bench/release.py` reports no unreadable span
and no arm imbalanced across a boundary, so nothing here needs stratifying —
which is the exposure [round 57](round-57.md) had and [round 63](round-63.md)
had to learn twice. `python3 evals/bench/concurrency.py` reads one generator in
flight per snapshot against a declared 2, so no arm-day exceeds its declaration.

**Generation deviated from the buying plan above in one respect, recorded here
before any of it was scored.** The registration launches all four shards at
once. They were run as two pairs instead — the design cells first, then
`ordered-steps` — because the supervisor that registered this round was killed
for low memory at 04:58 on 2026-09-15 with no shard running at all, which says
this machine is tighter today than the four-shard ceiling [#255] assumes. Each
comparison is still generated simultaneously against its own control, which is
the property the design needs; what the split gives up is wall-clock, not
balance. Both processes declare `--concurrency 2`.

**The working tree was switched to master and back at 14:24 while the edit
shard was still generating, which is the thing `AGENTS.md` forbids mid-round.**
Recorded here rather than left silent, with the check that settles it. `run.py`
resolves the rules slice once in `main()` and passes that in-memory string to
every generation, so an in-flight shard keeps the text it started with and the
switch could not reach it. The snapshots carry the checksums that follow from
that: the edit side reads `rules_cksum` 4035212029, which is this branch's
slice, the control side reads 594915793, which is master's, and both read
`cases_cksum` 2774319889. Had the process instead crashed and been resumed
inside that window, the [#69] guard would have refused the resume rather than
producing one round from two instruments — which is the case the guard exists
for and is not the case that occurred.

**`evals/pilot/score_structure.py` was changed after registration and before
any of this round was scored, in two ways that move no arithmetic.** Both are
recorded here because the scorer was committed with the registration precisely
so that it could not be tuned against the result.

1. **Each side now accepts a comma-separated list of snapshots.** The buying
   plan above splits every side in two, because `ordered-steps` is bought at
   twice the reps and a second invocation naming a different case subset
   computes a different `cases_cksum`. The scorer as registered took one file
   per side, so both bounds on `ordered-steps` would have reported "not
   generated in these snapshots" — the registration specified four files and a
   scorer that could read two. Merging snapshots that cover disjoint cases
   changes nothing: every endpoint is computed per case and pooled over a fixed
   case tuple. A merge whose two files disagree on `rules_cksum` is refused,
   since a side pooled across two instruments is the failure this round is
   built to avoid.
2. **The three bounds are renumbered to match this document.** The scorer
   printed the reading-rate bound as 1 and the two `ordered-steps` bounds as 2
   and 3; the registration numbers them the other way. The registration is what
   was written first, so the scorer now follows it, and the sections print in
   that order.

Neither change was made with any of this round's numbers in view. The check
that says so is the published null: run against round 63's two master-rules
shards before and after, the scorer reads 56.2% against 48.6% at Fisher
p = 0.232995 both times, to the last digit.
