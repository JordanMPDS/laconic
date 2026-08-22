# The design failures are ungrounded, not short

**Date:** 2026-08-22
**Issue:** [#46]
**Cost:** 0 generations and 0 judge calls. Every number below is recomputed from
snapshots already committed under `evals/snapshots/`, plus `git archive` of two
commits.
**Status:** a diagnosis, not a round. No rule was edited and no gate was changed.

## What this changes about [#46]

[#46] was filed as a length bug: a bare "how would that be built?" produced a
~1,400-word answer at level `full`. Ten rounds attacked it with a
design-question licence that bounds what a design answer must contain. The
licence shortens design answers reproducibly — 6 of 6 cells, p = 0.031, a
median 2288 to 2414 tokens across five independent generations — and it was
rejected every time, ultimately on answer quality, by the round 15 holdout and
then by round 20's dev set.

**Length was never the mechanism.** Every run record carries `num_turns` from
the Claude Code CLI, and on sonnet `num_turns == 1` means the model wrote one
message and called no tools. A representative failing laconic response on
`design-cache` is 2,423 output tokens — longer than the arm's median — of
confident, well-structured design that recommends Redis while `CDN.md` and the
app-wide `no-store` header in `middleware/security.js` sit unopened in the
fixture.

The separation is exact. Matching each response against its own case's fixture
filenames, over round 21's laconic arm on sonnet design cases:

| | names a fixture file | names none |
|---|--:|--:|
| `num_turns == 1` | **0** | 41 |
| `num_turns > 1` | 151 | 8 |

No overlap. On the three cases built for [#88], one-turn responses fail quality
22 of 27 against multi-turn's 5 of 63, Fisher p = 8.4e-12, and 0 of 27 one-turn
responses name the fixture's contradicting fact against 63 of 63 multi-turn.

## What `num_turns` is, and where the proxy leaks

`num_turns` is passed through from the CLI's `--output-format json` payload at
`evals/bench/run.py:105`. The harness records no independent tool-call count.

**On sonnet the proxy is sound.** `cache_read_input_tokens` is cleanly bimodal
with no overlap: [23812, 24560] for one-turn runs against [80933, 168976] for
multi-turn.

**On haiku it leaks.** Eight of 183 one-turn design runs reproduce content only
obtainable from the fixture — `design-cache`/`baseline`/`haiku`/rep3 is recorded
at `num_turns: 1` and quotes `productBySlug (~40ms)` verbatim from
`fixture/db.js:4`. Haiku's fixtures are small enough that reading barely moves
the token counts. Everything below is sonnet-scoped for this reason, and haiku
shows no effect in any case: laconic 29/40 against baseline 30/40.

## Sixteen of 22 cases are structurally pinned

| group | one-turn rate | why |
|---|--:|---|
| 4 cases with no `fixture/` (`code-fidelity`, `decision`, `floor`, `ordered-steps`) | 100%, always | nothing to open |
| 10 non-design cases with a fixture | 0%, always — 0 of 200 across the two rounds compared below, and 0 of 370 across the wider set | the fixture is read every time |
| `design-alerting` | 0/10 in all eight stored rounds | across three rules revisions and four CLI versions |
| `design-audit-log` | 0 or 1 of 10 | as above |

Six cells carry all the variance: `design-rate-limit`, `design-retry`,
`design-search`, `design-cache`, `design-realtime`, `design-upload`.

This retires a "specificity control" that looked clean and is not. Across all 72
snapshot-and-arm cells under `evals/snapshots/` covering the 14 non-design
sonnet cases — every arm, every rules revision, CLI 2.1.223 through 2.1.239 —
the one-turn count takes four values spanning 0.271 to 0.286. Total variation in
the whole corpus is three runs. A comparison there returns p = 1.000 by
construction and is not evidence of anything.

## The arm contrast is confounded and must not be published

Round 21 reads laconic 14/40 against baseline 3/40 on sonnet design cases,
Fisher p = 0.0052. **That number is not usable.** Round 21's three control arms
are not merely an older CLI — they are literally the same 120 run records
carried forward from `round-01-n10-v4.json` via `round-20.json`, generated
2026-08-11 and 2026-08-12 on CLI 2.1.223/2.1.227. The laconic arm ran
2026-08-22 on 2.1.239. Zero control runs exist in the new batch, so treatment
and batch are perfectly collinear.

`round-01-n10-v4.json` breaks the collinearity — same rules text, same eight
cases, all four arms generated in one interleaved pass:

| arm | one-turn, sonnet design |
|---|--:|
| baseline | 3/40 (7.5%) |
| terse-control | 4/40 (10.0%) |
| word-compression | 2/40 (5.0%) |
| laconic | 15/80 (18.8%) |

Fisher against baseline: **p = 0.173**. `round-01-n10-v3.json`, also single
batch, reads 9/50 against 1/25, p = 0.150. Batch drift measured within the
treatment arm at fixed rules and fixed cases is 0.188 to 0.350, p = 0.070 —
comparable to the effect itself.

Permission and tooling asymmetry is ruled out: `run.py:283-297` is identical
across arms, same fresh `mkdtemp` and `copytree` of the fixture, same
`CLAUDE_CODE_SAFE_MODE=1`, no `--allowedTools` anywhere. `concise-style`'s only
difference is `--settings '{"outputStyle":"Concise"}'`, and all 22 of its
multi-turn runs quote fixture content.

**Defensible statement:** laconic's one-turn rate on sonnet design cases runs
about 0.19 against controls' 0.08 — replicated in direction in every
single-provenance snapshot, never significant.

## Between-round overdispersion is phi = 3.03

Every stored snapshot whose laconic arm ran byte-identical rules text
(`rules_cksum` 3980812364), sonnet, design cases. No two files share a run,
verified by MD5 over every response text:

| round | one-turn | rate | CLI |
|---|--:|--:|---|
| round-10 | 8/30 | 27% | pre-stamp |
| round-10-replication | 8/30 | 27% | pre-stamp |
| round-12 | 8/30 | 27% | pre-stamp |
| round-14 | 10/30 | 33% | 2.1.227 |
| round-15-replication | 16/50 | 32% | 2.1.227 |
| round-15 | 23/50 | 46% | 2.1.227 |
| round-20 | 45/80 | 56% | 2.1.232 |

Chi-square homogeneity **18.16 on 6 df, p = 0.0059, phi = 3.03**, an sd
inflation of 1.74. Rounds 14, 15-replication and 15 all ran on 2.1.227 and span
33% to 46%, so this is not purely CLI drift. The value matches, to two decimals,
the 3.0 clustering ratio `_cluster_count_p` records for `violations_total` at
`report.py:232-236`, reached by an unrelated mechanism.

A second, independent estimate comes from the **master** side. Three batches of
byte-identical master rules over `design-cache`, `design-realtime` and
`design-upload`: `round-01-n10-v4` 6/30 (0.200), `quality-rates-design` 13/90
(0.144), `round-21-n10` 12/30 (0.400). Chi-square **8.97 on 2 df, phi = 4.49**,
sd inflation 2.12. The two estimates were computed on opposite sides of the
contrast and agree that the overdispersion is real.

Applied to the within-arm contrasts:

| contrast | binomial | phi = 3.03 | phi = 4.49 |
|---|--:|--:|--:|
| round 20 licence 45/80 against round 21 master 26/80, all 8 cases | 0.0025 | 0.082 | **0.154** |
| pooled licence 41/110 against master 15/80 | 0.0057 | 0.112 | — |

**Batch alone produces shifts larger than the rules effect.** On the only three
cases where both contrasts are measurable, at byte-identical rules text:

| contrast | rates | Fisher |
|---|---|--:|
| batch only, master rules (`quality-rates-design` against `round-21-n10`) | 0.144 to 0.400 | **0.0078** |
| rules only (`round-21-n10` against `round-20`) | 0.400 to 0.633 | 0.121 |

That is the bound. This instrument's between-batch variance exceeds the effect
it is being asked to detect, so a single-snapshot-per-side comparison is not
identified.

**Drift is not monotonic**, so "the later batch has the lower rate, therefore
drift works against the effect" is not a safe argument and is not made here.
Master rules on those three cases run 0.200, then 0.144, then 0.400 — it dips
before it rises. The sign of drift is not a function of time or CLI version in
this instrument.

The attribution itself is identified. Reconstructing the hook output with
`git archive` reproduces `rules_cksum` 3980812364 at `561e896` and 1830906901 at
`8e26aa3`, and `git diff 8e26aa3 561e896 -- rules/laconic.md` is a single
11-line block: the design-question licence and nothing else. Nothing else in
that commit touches the rules beyond the regenerated `rules/dist/*`.

**Where the pairing's significance actually comes from.** Split by case group,
round 20 against round 21: the five non-discriminating cases give 26/50 against
14/50, p = 0.024, while the three [#88] cases built to detect real harm give
19/30 against 12/30, p = 0.121. The pairing is strongest exactly where the
endpoint is least meaningful.

**What survives everything is one cell.** `design-search` reads master 3/10 and
4/10 across two independent generations ten days and twelve CLI releases apart,
against licence 8, 9, 8, 5 and 9 of 10 across five independent generations —
pooled 7/20 against 39/50, Fisher **p = 0.0016** — and returns to baseline when
the rules revert.

## The endpoint is not a validated surrogate for quality

This is the finding that decides how the endpoint may be used.

| rules revision | one-turn | quality fails |
|---|--:|--:|
| master (`round-01-n10-v4`) | 15/80 = 18.8% | 10/80 = 12.5% |
| licence (round-10) | 8/30 | 4/30 |
| licence (round-14) | 10/30 | 5/30 |
| licence (round-15) | 23/50 | 6/50 |
| **licence pooled** | **41/110 = 37.3%** | **15/110 = 13.6%, p ~ 1.0** |

An 18.5-point move in the mediator produced a 1.1-point move in the endpoint.
Rounds 10, 14 and 15 carry only the five old design cases, and
[`design-discrimination.md`](design-discrimination.md) established that on those
"the answer a model gives without opening a file is already the fixture's
answer." The surrogate moved because the model stopped reading; quality did not
move because on those cases reading never mattered.

The six live cells therefore split:

- **`design-cache`, `design-realtime`, `design-upload`** — variance and a
  quality link, with perfect separation on naming the contradicting fact.
- **`design-rate-limit`, `design-retry`, `design-search`** — variance, no
  quality link. These carry most of the pooled effect above.

"Fully mediated" was itself an n=5 artifact. Round 21 at n=5 reads the
multi-turn-only arm contrast as 2/26 against 1/37, p = 0.564; at n=10 the same
comparison is 8/54 against 1/37, **p = 0.078**, a residual direct effect.

The mediation is also near-tautological on these cases: the design `expect.json`
criteria are written around fixture content, so not reading implies failing, and
the judge's reasons for one-turn failures name the unread file verbatim.

## Why the endpoint is still worth having

Power at n = 40 per side, exact Fisher, two-sided, alpha = 0.05 (multiply by
about 3 if phi = 3 holds):

| endpoint | 35% to 10% | 21% to 8% |
|---|--:|--:|
| one-turn rate | **0.72** | — |
| judge-graded `quality_fails` | — | **0.29** |

It costs nothing to grade. `num_turns` is present on **27,291 of 27,291** usable
runs across every stored snapshot, so every round in the archive re-scores for
free and a future round scored on it needs no judge calls at all — judging was
$41.37 of round 14's $60.68.

## Rules for using it, registered here before any round uses it

1. **Target only, never a fatal counter.** The four fatal counters are harm
   counters; not opening a file is not harm, and on four cases it is the only
   possible behaviour.
2. **`--target-cases` required.** Unscoped, it is 16 pinned cases diluting 6
   live ones.
3. **The scope is the quality-linked three**, registered at step 5. Scoring it
   on `design-rate-limit`, `design-retry` or `design-search` is scoring a
   behaviour with no established consequence.
4. **`--target-models sonnet`.** Haiku sits at 65-77% in every arm and revision
   and the proxy leaks there.
5. **An edit must clear it in addition to not regressing `quality_fails`, never
   instead of it.** Until a round exists in which the surrogate moved and
   quality was then scored at adequate n and moved as predicted, this endpoint
   screens candidates; it does not accept them. No such round exists, and the
   one contrast that has been run showed the opposite.
6. **The gate needs the inflation factor**, not `#103`'s clustered bootstrap.
   `_cluster_count_p` resamples responses within cells, and a one-turn flag is
   one Bernoulli per run, so it would return the binomial number. The
   overdispersion here is between rounds and no within-round resample recovers
   it.

## What to buy next

**Calibrate phi at the current CLI: two independent replications of the laconic
arm at master rules, sonnet, the six live cells, n = 10. 120 generations, zero
judge calls.** With `round-21-n10` that gives three independent same-rules
same-CLI measurements and a 2-df chi-square. `round-21-n10` reads 26/60 (43%) on
those cells.

| outcome | reading |
|---|---|
| all three within ±8 points of 43% | phi ~ 1, the binomial gate is honest |
| spread like the historical series, ±15 points | phi ~ 3 confirmed; an 18-point effect sits at the edge of the null |
| wider | not gate-able round-against-round; demote to a within-round disclosure |

Do not buy more reps of an edit against round 21. The dominant error term is
between-round and does not shrink with reps inside a round.

**Every future comparison on this endpoint needs both sides in one batch.** The
corpus has never contained a licence-against-master measurement generated in a
single interleaved sequential pass, and the batch bound above shows why that is
not a formality: batch alone moves this statistic further than the edit does.

`evals/snapshots/loop/one-turn-cli-control.json` is a separate, smaller
experiment already generating: `baseline`, `terse-control` and `laconic` in one
interleaved sequential pass on the current CLI, sonnet, all eight design cases,
n = 5. It settles the arm contrast that round 21 cannot. It does **not** settle
the licence question, because all three of its arms run master rules.

## Two provenance facts found while checking the above

**`round-18.json` and `round-20.json` were not produced by the committed
sequential loop.** `run.py` runs one `subprocess.run` and one `save_snapshot`
per cell, so wall-clock span should exceed summed duration. Reconstructing each
run's window as `[generated_at - duration_ms, generated_at]` over the full
440-run laconic arm:

| snapshot | wall span | summed duration | ratio | max runs in flight |
|---|--:|--:|--:|--:|
| round-18 | 35.4 min | 152.9 min | 4.32 | **5** |
| round-20 | 26.5 min | 115.4 min | 4.36 | **6** |
| round-21-n10 | 717.2 min | 140.2 min | 0.20 | 1 |
| round-22-n10 | 612.3 min | 130.7 min | 0.21 | 1 |

Round 20's records in timestamp order are also scrambled relative to the loop
order at `run.py:447-455`, which round 21's follow exactly. Whatever produced
those two arms ran several CLI invocations concurrently. Across the 16 snapshots
with at least 30 laconic sonnet design runs, Spearman correlation between the
concurrency ratio and the one-turn rate is **0.174** — no measured association,
so this is a limitation of the round-20-against-round-21 pairing rather than an
explanation of it. It is nowhere disclosed in either snapshot's metadata.

**`round-21.json` is a strict subset of `round-21-n10.json`.** All 40 shared
laconic sonnet design cells have byte-identical `text`. They are one experiment
at two sample sizes and must never be treated as two measurements.

## Latent exposure, currently zero

`run.py:459-465` retries a failed call once and records `ok=False` after, and
the 300-second timeout preferentially kills long, many-turn runs, which would
inflate the one-turn rate among survivors. Every round cited in this document
has **0 failed runs**, so nothing here is contaminated. A round with failures
would need this checked before its one-turn rate is read.

## What this says about the ten rounds

The design-question licence bought its token reduction partly by removing the
reading step. It compresses genuinely — among responses that read the repo,
median output falls 4476 to 2930 — and it also roughly doubles how often the
model answers from priors. No round separated the two, because nothing measured
the split. That is why five replications of a reproducible token win kept dying
on quality.

It also explains why rounds 16 and 17 could not work. Their rule was gated on "a
question about code you were pointed at", and all 14 of round 21's one-turn
failures fall on the six design prompts that name no file. `design-alerting`
("multiple places in SPEC.md") and `design-audit-log` ("on this service")
produce 0 of 40 between them. The gate fires only where the failure does not
happen. Any candidate edit for [#46] has to be ungated.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#88]: https://github.com/JordanMPDS/laconic/issues/88
[#103]: https://github.com/JordanMPDS/laconic/issues/103
