# Round 45: the quotation exemption, and the one arrow shape no round has aimed at

**Registration. Nothing below the results line has been computed.** This file
and the rules text under test are committed in the same commit, before any
generation, following [round 38](round-38.md) and [round 44](round-44.md).

## Why this edit

[`lens-pilot-26.md`](lens-pilot-26.md) left five untried arrow mechanisms.
[Round 44](round-44.md) scored the first of them — the relocation into
`Never cut` — and it was rejected: `walkthrough` 41 arrows to 45, permutation
p = 0.830, every point estimate leaning the wrong way. The queue is four, and
this round draws the one the pilot's own second read singles out:

> **3 and 6/8 target an idiom no arrow round has seen.** Both aim at the value
> transition — `` `legacy` `` to `` `split` `` in a parenthesis — which lives
> almost entirely in `confirm-rollback`, `deep-rollback` and `recall-rollback`.
> Those three cases were added after the arrow work stopped. No finding speaks
> to them.

**Three of the pilot's five proposers converged on this mechanism
independently**, which no other candidate managed: the compression lens
(candidate 6), the readability lens (candidate 8), and the unlensed control
reader, whose single new candidate was *"close the quotation exemption: an
inline code span is not a fenced block, and the arrow between two quoted values
is yours"*. Round 44's candidate came from one lens.

**And round 44 measured the target cell as a side effect.** It carried
`confirm-rollback` as its registered discriminant and predicted nothing would
happen there, correctly: 26 arrows to 33, p = 0.125. So this round's target is
a cell whose arrows are known to survive the edit tried immediately before it.

## What the archive says the shape is

Every laconic/sonnet response in the archive at `rules_cksum` 136269960,
deduplicated by text:

| case | responses | arrows | carrying one | chains | mappings |
|---|--:|--:|--:|--:|--:|
| `confirm-rollback` | 80 | 46 | 46 (57.5%) | **0** | 46 |
| `walkthrough` | 215 | 204 | 71 (33.0%) | 40 | 164 |

`confirm-rollback` has **no chains at all**. Every arrow it carries is a single
two-term mapping, and reading them they are one sentence with one shape:

> Partly. The config change (`legacy` → `split`) triggered the initial 500s at
> 14:02, but the document is explicit that it is the migration that made the
> incident unrecoverable.

The two values are inline code spans; the arrow sits between them. `metrics.py`
strips inline code before counting, so what it sees — and what the rule's own
self-check in `tests/test_rules.sh` sees — is a bare arrow in prose.

**That is the reading the current text leaves open.** The section ends:

> Arrows belong in a fenced code block or a verbatim error string, where they
> are the material being quoted rather than your own prose.

A parenthesis holding two backticked values is quoted material by every reading
except the one that counts, and nothing in the paragraph says which side of the
line it falls on.

## The edit

One edit, to the exemption sentence only. The prohibition, all four
`Wrong:`/`Right:` lines and the enumeration are untouched.

```diff
 Arrows belong in a fenced code block or a verbatim error string, where they
-are the material being quoted rather than your own prose.
+are the material being quoted rather than your own prose. Quoting the two
+things an arrow joins does not quote the arrow: a parenthesis naming what a
+setting changed from and to is your own sentence, and it takes the word —
+changed from `legacy` to `split`.
```

**The file gains no rendered arrow specimen.** The added sentence names the
construction in words and shows only the remedy, so [#164] item 2 — a
`Wrong:`/`Right:` pair pre-registering every cell that carries the demonstrated
form — stays out of this round, as it did in round 44. That is also what
`tests/test_rules.sh` enforces: outside a single-backtick span an arrow may
appear only on a `- Wrong:` line.

The edit lands above the `<!-- level:lite -->` marker, so it ships at all three
levels including `ultra`, and `ultra`'s slice grows by about 45 words.

## Hypothesis

> Closing the quotation exemption — an arrow between two quoted things is your
> own prose, with the value-transition idiom named and the word given as its
> remedy — should lower the arrow count on `confirm-rollback`, sonnet.

## Falsifier, registered before the batch

**The two `confirm-rollback` cells not separating at p < 0.05, or separating
upward.** Direction is registered because three of the six prior arrow edits
moved the wrong way, and round 44 made it four of seven.

## The discriminant, and why `walkthrough` is in the batch

`walkthrough` carries the other shapes — 40 chains and 164 mappings across 215
archived responses, none of them a value transition — and this edit does not
name them. Round 44 ran the same pair in the opposite direction, targeting
`walkthrough` with `confirm-rollback` as its discriminant, so the two rounds
between them read every cell of a 2x2.

| `confirm-rollback` | `walkthrough` | reading |
|---|---|---|
| falls | flat | the exemption was the licence, and it was licensing exactly the shape it names. The candidate works as described |
| falls | falls as much | generic re-emphasis rather than the exemption — the file said "arrows" one more time, which round 03 already did |
| flat | flat | the exemption is not the carrier either. [#26]'s second scored candidate fails and the queue is three |
| flat | falls | the sentence moved a shape it does not name and not the one it does. An anomaly to record, not a pass |

## Registered harm checks, free with the batch

Both are substring tests over text this batch generates anyway, so neither
costs a judge call. Rounds 30 and 31 were both rejected on never-cut damage
outside the cells their hypotheses named, and [`arrows.md`](arrows.md)
finding 6 says that propagation is what has been blocking this line.

- **`walkthrough` carries never-cut item `401`**, and names it in 215 of 215
  archived responses. A fall in that share rejects this round whatever the
  arrow counts do.
- **`confirm-rollback` has an empty `never_cut` list**, so its load-bearing
  content is checked the same way against its trap instead: the share of
  responses naming `0042` or `settlement_currency` — the migration that is why
  the rollback failed, which the trap calls the load-bearing half. That reads
  74 of 80 (92.5%) in the archive, so it is a rate comparison against this
  round's own control at Fisher p < 0.05, not a hard 40 of 40.

The wider propagation check — `destructive`, `ordered-steps` and the round-wide
fatal counters — is **not bought by this batch**. The staged rule is to score
the cheap target first and buy the round-wide arm only for an edit that passed
it.

## The batch

Both sides generated simultaneously, each from its own tree, so era and CLI
release cancel between them rather than confounding them.

```sh
git worktree add /tmp/laconic-r45-control master

# edit side, from this branch
python3 evals/bench/run.py --arms laconic --models sonnet --reps 40 \
  --cases walkthrough,confirm-rollback --concurrency 2 \
  --snapshot evals/snapshots/loop/round-45-edit.json

# control side, from the worktree, writing back to this tree
cd /tmp/laconic-r45-control && python3 evals/bench/run.py --arms laconic \
  --models sonnet --reps 40 --cases walkthrough,confirm-rollback \
  --concurrency 2 \
  --snapshot <abs>/evals/snapshots/loop/round-45-control.json
```

160 generations, no judging. `--concurrency 2` on both, because two CLI
invocations really are in flight. Control at `rules_cksum` 136269960, edit at
**1194758662**.

**The registered baseline is this round's own control**, not round 44's and not
the archive. Both are quoted above for sizing only.

Both cases are single-turn, so `--turn-delivery` does not apply and the batch
carries no multi-turn work.

## Scoring

`metrics.score(text)["symbol_connectors"]`, the counter rounds 38 and 44
published and the one `review.py` reads for its `arrow` violations. Two
statistics per cell, both two-sided:

- **arrow count**, by permutation of the side label over the per-response
  counts, 200,000 resamples, seed 45. This is the primary.
- **responses carrying at least one**, by Fisher exact, which is the figure
  rounds 30, 31, 38 and 44 published.

`metrics.arrow_forms` is reported as disclosure, because round 44 found
`walkthrough`'s chains and mappings moving in opposite directions and asked
that a later round look deliberately.

## Power, stated before the numbers

Round 44's control read 26 arrows in 40 `confirm-rollback` responses, and the
archive rate puts about 23 of 40 responses carrying one. Against a control at
23 of 40 this round detects a halving — 12 of 40 reads Fisher p = 0.0236 — and
does not detect a third, 16 of 40 at p = 0.179. It is sized to resolve an
effect the size of round 30's, which is the largest any arrow edit has produced
on its own target, and nothing smaller.

## Cost

160 generations, 0 judgments. Roughly $8 API-equivalent, bought from a usage
window rather than an API budget.

[#26]: https://github.com/JordanMPDS/laconic/issues/26
[#164]: https://github.com/JordanMPDS/laconic/issues/164
