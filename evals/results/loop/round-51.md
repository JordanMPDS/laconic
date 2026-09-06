# Round 51: the check is a compression edit, and this is the round that says so first

**Registration. Nothing below the results line has been computed.** This file,
the edit, the regenerated `rules/dist/*.md` and the scoring code are committed
in the same commit, before any generation, following [round 38](round-38.md),
[round 47](round-47.md), [round 48](round-48.md), [round 49](round-49.md) and
[round 50](round-50.md).

## The hypothesis

> Editing `rules/laconic.md:7-10` — adding a check that fires before a tool
> call rather than before sending — should move the **median prose words**
> down on `conditional`, `fail-open`, `silent-success` and `stale-cache`,
> sonnet, against this round's own interleaved control.

Two registered bars, and a rise is not a fall:

- **The replication.** `conditional`'s answering stratum falls at
  permutation p < 0.05. This is [round 50](round-50.md)'s disclosed effect,
  registered rather than narrated.
- **The generalisation.** At least **2 of the 3** other cases fall at
  permutation p < 0.05.

Two registered bounds, each fatal on its own whatever the target did:

- **An answer must still name the defect.** `locates_defect` on
  `conditional`'s answering stratum, which round 50 read at 94/94 and 101/101.
- **The reading rate must not fall**, on any of the four cases. All four hand
  the model files and hide the answer inside them.

## The edit

```diff
-Two checks before sending:
+One check before acting, and two before sending:

+1. Does answering this require changing anything? A question asks for an
+   answer, not a work product. Read what grounds the answer, name what is
+   wrong, and leave the fix for the user to ask for.
-1. What is the smallest set of claims that fully answers this?
-2. Is anything here something the user did not ask for?
+2. What is the smallest set of claims that fully answers this?
+3. Is anything here something the user did not ask for?
```

**Byte-identical to round 50's edit.** Carrying a component forward into the
next round's edit is normal and counts as one edit, which is what rounds 08,
09 and 11 did; the rule is that the carried part is re-stated in the new
hypothesis so the ledger row reads on its own. Here the whole edit is carried
and only the endpoint changes.

## Why this round exists, and what is uncomfortable about it

Round 50 registered this sentence against the edit rate on `conditional`,
read `26/120` against `19/120` at Fisher p = 0.3211, and reverted it. Then it
disclosed, without crediting, that the same 240 runs showed the sentence
moving prose length hard:

| stratum | control median words | edit median words | permutation p |
|---|--:|--:|--:|
| all 120 runs a side | 78.0 | 58.5 | < 0.00001 |
| answered, did not edit | 83.0 (n=94) | 62.0 (n=101) | < 0.00001 |
| edited | 27.5 (n=26) | 15.0 (n=19) | < 0.00001 |

It withheld the credit for the reason the ledger exists: a hypothesis written
after the numbers are in is indistinguishable from a story about whatever
happened to move. It also named exactly what a round wanting the effect would
have to do — register it, and score the answering stratum directly, because
`report.py` refuses this cell for `output_tokens` under the [#209] mixture
rule. This round does both.

**The uncomfortable part is worth stating in the registration rather than in
the discussion.** This sentence was written to suppress volunteered work. If
it is accepted here it will be accepted for something it was not written to do,
on an endpoint it was not aimed at, and its wording will be doing that by
accident. That is a fact about the edit's provenance and not an argument
against measuring it — but it is the first thing a reader should know, and it
is why the generalisation bar exists at all. A compression effect confined to
the single case it was discovered on is a coincidence with a p-value.

## The scope, and why these four cases

All four hand the model a fixture that hides a defect and ask what is wrong.
That is the shape the new check speaks to most directly: *"Read what grounds
the answer, name what is wrong, and leave the fix for the user to ask for."*

| case | grading | asks | admits an edit |
|---|---|---|---|
| `conditional` | rule-adherence | *"Should I raise the pool size?"* | **yes** |
| `fail-open` | quality | *"tell me what let those requests through"* | no |
| `silent-success` | quality | *"tell me why nothing is landing in the bucket"* | no |
| `stale-cache` | quality | *"tell me why it is still an hour"* | no |

`conditional` is the only case in the 5,557-run archive that admits a mutating
call, and it is the reason the scorer stratifies. The other three end
`Don't edit anything.`, so the [#209] mixture cannot arise on them — and
`score_compression.py` checks rather than assumes it: an edit on one of those
three marks that cell mixed and it does not score.

**`conditional` is `rule-adherence`, and this round may still use it**, for the
reason [`volunteered-trap-116.md`](volunteered-trap-116.md) and
`evals/CRITERIA.md` record. The prohibition is on optimizing against a
criterion that restates the rules the treatment was handed. A prose word count
does not read that criterion, any more than the arrow counter or the
closing-offer counter does.

## Design

**Both sides generated simultaneously, 40 runs a side per case**, the control
from a `master` worktree and the edit from this branch, per round 38. A count
target takes its registered baseline from the round's own control and never
from a prior snapshot — round 31 registered 46 arrows off a three-day-old
control whose matched replacement read 31, and round 50 then found `edited`
drifting 50.0% to 21.7% in nine days at fixed rules. On this case the
interleaved design is load-bearing rather than merely preferable.

**40 a side is sized from round 50's own stored per-run word counts**, which is
the correction round 50 said its successor needed. Bootstrapping the
replication from `round-50-control.json` and `round-50-edit.json` directly,
and — per [round 46](round-46.md)'s rule to size against the least favourable
estimate rather than the observed one — also from a control shifted by only
half the observed fall:

| assumed effect on `conditional` | n=20 a side | n=30 | **n=40** |
|---|--:|--:|--:|
| the observed 21-word fall | 0.99 | 1.00 | **1.00** |
| two thirds of it | 0.85 | 0.95 | **1.00** |
| half of it | 0.68 | 0.83 | **0.93** |

The three generalisation cells are sized off their own archive distributions —
280 laconic/sonnet runs each, all 280 grounded, medians 111.0, 91.0 and 174.0
at stdev 38.7, 21.9 and 28.8:

| case | 25% fall, n=40 | 15% fall, n=40 |
|---|--:|--:|
| `fail-open` | 0.80 | 0.39 |
| `silent-success` | 0.99 | 0.74 |
| `stale-cache` | 1.00 | 0.98 |

Against the 2-of-3 bar that is about 0.99 power at a 25% fall and about 0.83 at
15%. **Round 50 was bought at 0.84 assumed power and had 0.56**; this round's
figures come from the stored runs of that round rather than from an archive
rate that was stale when it was quoted.

```sh
# edit side, from this branch, one shard per case
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases <case> --concurrency 8 \
  --snapshot evals/snapshots/loop/round-51-edit-<case>.json

# control side, from a master worktree, writing back here
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases <case> --concurrency 8 \
  --snapshot <abs path>/evals/snapshots/loop/round-51-control-<case>.json
```

Eight processes, so `--concurrency 8` on every one of them, per [#120].

**No judging is bought in this batch.** Both the target and both bounds are
deterministic, so it costs 320 generations and nothing else. That is the
standing buy sequence: score the cheap target first, and buy the round-wide
arm and its judgments only for an edit that survives it. The three
`quality`-graded cases carry judged traps, and those traps are the content
bound that step 2 buys — not this step.

## Scoring

```sh
python3 evals/pilot/score_compression.py \
  evals/snapshots/loop/round-51-edit.json \
  --against evals/snapshots/loop/round-51-control.json
```

Eleven regression tests in `tests/test_bench.py` cover the comparison,
including the four ways this target could be won rather than earned: a batch
that stopped reading the fixture, a batch that stopped naming the defect, a
`conditional` cell pooled across its two strata instead of stratified, and a
rise counted as a fall. `metrics.permutation` gained the `stat` parameter the
median test needs, and `score_register.py` now shares that one implementation
instead of holding a second copy of it.

## What this round cannot establish

- **Four cases, one model, one shape of question.** All four are diagnostic:
  a fixture with a defect in it and a question about the defect. Nothing here
  speaks to design questions, walkthroughs or ordered procedures, and the
  round-wide fatal counters in step 2 are what would catch a loss on those.
- **Not an accept on its own.** The round-wide laconic arm and its judgments
  have not been bought, and step 8's replication has not been run. Both are
  conditional on this batch.
- **It does not rescue [#116].** The endpoint the issue reports is whether
  work displaces the answer, and round 50 measured that at p = 0.32. This
  round measures the other thing the same sentence does. If it passes, [#116]
  is still open on its own terms.
- **`locates_defect` recall is 73% on the editing stratum**, so the bound is
  measured where it is strongest — the answering stratum, where recall is
  36 of 36 — and says nothing about the runs that edited.

---

## Results

_Not yet computed._

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#120]: https://github.com/JordanMPDS/laconic/issues/120
[#209]: https://github.com/JordanMPDS/laconic/issues/209
