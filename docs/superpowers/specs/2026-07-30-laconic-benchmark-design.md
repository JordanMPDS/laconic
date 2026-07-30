# Laconic benchmark — design

**Date:** 2026-07-30
**Status:** Approved design, ready for implementation planning
**Applies to:** `laconic` v0.1.1 and later
**Resolves:** the n=1 and gitignored-results entries in [`v0.1.0-known-limits.md`](../../v0.1.0-known-limits.md)

## Problem

`evals/run.sh` runs four cases, two arms, one sample, on the cheapest model, and a
human grades the output by reading it. That was enough to answer "does the harness
produce signal" during v0.1.0. It cannot answer the questions that now matter:

- **Is a miss a rule defect or a small model's adherence ceiling?** Two findings in
  `v0.1.0-known-limits.md` were deferred with exactly this reasoning and remain open.
  One sample on one model cannot separate the two.
- **Does laconic beat simply asking for terseness?** No control arm exists, so every
  measured difference is confounded with the generic "be concise" effect.
- **Does the readability claim hold?** The project's central claim — terse *and*
  readable — has never been measured at all, only asserted and spot-checked by reading.
- **What do the numbers cost to trust?** `evals/results/` is gitignored, so no number
  is auditable from a diff.

## Goals

1. Report a compression number that is honest, including the rules' own injection cost.
2. Report a **readability** number, mechanically, with a validation suite proving the
   detectors work — this is the axis laconic exists to defend and the one neither
   reference harness publishes.
3. Run at n=5 across two models, enough to separate a rule defect from adherence noise.
4. Make every published number regenerable offline from a committed snapshot.

## Non-goals

- **Winning on token count.** A word-deletion approach compresses harder by
  construction; that is the tradeoff laconic chose. A benchmark scored on tokens alone
  would pressure the rules toward the exact behavior the project exists to avoid.
  Compression is reported next to readability, never alone.
- **Measuring real session cost.** These are single-turn calls. See Honesty notes.
- **Grammar checking.** The readability detectors are heuristics with a stated
  false-positive guard, not a parser.

## Architecture

```
evals/
  run.sh                    # unchanged in purpose: read ONE case side by side
  CRITERIA.md               # extended: new cases, metric definitions
  cases/<name>/prompt.md    # 8 cases (moved from evals/<name>/)
  cases/<name>/fixture/     # staged into the run cwd, only where the prompt needs it
  bench/run.py              # generation → snapshots/results.json
  bench/metrics.py          # deterministic scoring (no network, no deps)
  bench/judge.py            # blind LLM judge → snapshots/judgments.json
  bench/report.py           # snapshots → markdown tables
  snapshots/results.json    # committed
  snapshots/judgments.json  # committed
  results/YYYY-MM-DD-*.md   # committed dated writeups
  scratch/                  # gitignored; run.sh output moves here
tests/test_metrics.py       # validates the detectors themselves
```

**Dependencies: python3 and the `claude` CLI. Nothing else.** `json` is stdlib and
the CLI returns exact token counts, so there is no tiktoken, promptfoo, node, or
pandas requirement. This is a deliberate match to the project's no-dependency
character and a strict improvement over both reference harnesses.

`run.sh` keeps its job — produce one readable side-by-side for diagnosis — and needs
two edits: its case glob points at `evals/cases/`, and its output moves to
`evals/scratch/` so `evals/results/` can hold committed writeups.

`report.py` reads arm definitions out of the snapshot rather than a shared config
module, so there is no second source of truth to drift.

## Arms

Four arms. The word-compression arm is an instruction **we author and publish**, so it
represents the technique rather than any particular plugin, and its wording can be
disputed by anyone reading the spec.

| Arm | System prompt |
| --- | --- |
| `baseline` | none |
| `terse-control` | `Answer concisely.` |
| `word-compression` | `Answer concisely. Drop articles and filler words, abbreviate common terms, and use arrows instead of conjunctions.` |
| `laconic` | stdout of `hooks/laconic.sh start` at the configured level |

The laconic arm is built by invoking the real hook with `CLAUDE_CONFIG_DIR` pointed at
a temp dir, exactly as `run.sh` already does. The rules are never copied into the
benchmark, so the benchmark cannot drift from what ships.

## Cases

Eight. The four from v0.1.0 are unchanged; four are new.

| Case | Question | Fixture | Trap |
| --- | --- | --- | --- |
| `decision` | Should we switch ORMs mid-project? | none | Surveys both options, adds a migration lecture, closes with an offer |
| `walkthrough` | Walk me through this auth flow, including the 401 path and the concurrency collapse | `auth.js` | Compressed to a summary, or one named branch silently dropped |
| `destructive` | About to run `DROP TABLE users;` — anything I should know? | `schema.sql`, `fixtures/users.json` | Cascade or FK blast radius unmentioned, or the warning trimmed to a fragment |
| `badnews` | Did the rounding fix work? | `last-run.log` | Reports success, omits or buries the three still-failing tests |
| `conditional` | Connection pool keeps hitting max — should I raise the pool size? | `pool.log`, `db.js` | **The core case.** Correct advice is conditional: raise it only if the connections are genuinely concurrent; if they are leaked, a bigger pool delays the same failure. Fails when the condition is dropped or collapsed into a symbol (`pool max → raise`), making the advice wrong half the time |
| `ordered-steps` | Rotate the JWT signing key without logging everyone out | none | Any of the four steps missing, or the ordering words removed — this procedure is wrong in any other order |
| `floor` | What does `git restore --staged` do? | none | Nothing here *should* be cut. Measures whether the rules add tax where there is no padding to remove (the floor effect ponytail documents) |
| `code-fidelity` | Give me a one-liner to find files >100MB modified this week, and explain the flags | none | Code altered, truncated, or abbreviated; or the explanation dropped despite being explicitly requested. Also exercises the metric's code-stripping |

**Fixture rule:** a prompt that references project artifacts gets a fixture; a
general-knowledge prompt does not. v0.1.0 lost three of four traps to prompts that
named files which existed nowhere, and the model stalled asking for the project
instead of answering. `ordered-steps`, `floor`, and `code-fidelity` are
self-contained knowledge questions and need no fixture.

## Metrics

### Compression — exact, from the CLI

`claude -p --output-format json` returns real Claude token counts. Recorded per run:
`usage.output_tokens`, `usage.input_tokens`, `usage.cache_creation_input_tokens`,
`usage.cache_read_input_tokens`, `total_cost_usd`, `duration_ms`, `num_turns`.

`usage.output_tokens` is the headline: it is the length of the answer, which is what
the rules control. `modelUsage.*.outputTokens` reports a larger figure that
aggregates session overhead; the two are recorded but only the former is compared
across arms, and the choice is stated in the writeup.

### Readability — heuristics, honestly labeled

**All detection runs on prose only.** Fenced code blocks, inline spans, and URLs are
stripped before any detector sees the text. `->` in Rust and `impl` in a command are
correct usage; counting them would make the metric worthless. This stripping is the
metric's single largest correctness risk and is covered by a dedicated test.

*Counted violations* — high confidence, reported with the offending span so every
violation is auditable:

| Detector | Definition |
| --- | --- |
| `symbol_connectors` | `→`, `->`, `=>` in prose |
| `abbreviated_prose` | word-boundary matches of `impl`, `req`, `resp`, `func`, `val`, `obj`, `arg`, `msg`, `err`, `w/`, `b/c` |
| `sentence_initial_lowercase` | a sentence beginning with a lowercase letter, excluding sentences that begin with an inline-code span |

The abbreviation list is deliberately tight. `config`, `repo`, `auth`, `env`, and `db`
are normal developer English and were excluded: including them would generate false
positives against correct prose and inflate every arm's score.

*Reported rates* — proxies, never a standalone verdict:

- `article_rate` = count of `the|a|an` ÷ prose words. Normal English runs ~7–9%;
  telegraphic prose falls to 1–2%.
- `aux_verb_rate` = count of `is|are|was|were|be|been|being|has|have|had|do|does|did|will|would|can|could|should|may|might|must` ÷ prose words. Word-deletion strips
  auxiliaries and copulas first, so this drops sharply when grammar degrades.

### Gates

Applied to the `laconic` arm, per case, per model, on the median across reps:

1. `symbol_connectors + abbreviated_prose + sentence_initial_lowercase == 0`
2. `article_rate ≥ 0.70 × baseline article_rate` for the same case and model
3. `aux_verb_rate ≥ 0.70 × baseline aux_verb_rate` for the same case and model
4. Case never-cut keywords all present (per-case list in `CRITERIA.md`; e.g.
   `destructive` requires the cascade and the `invoices` FK)

The 0.70 factor is a threshold, and a threshold nobody calibrated is an assertion. It
is set from the observed spread in the first full run and **the observed values are
published alongside it**, so a reader can see whether the gate is tight or slack. If
the first run shows arms separated by less than 2×, the factor is wrong and gets
revised in the writeup rather than quietly kept.

Gates are evaluated by `report.py`, which exits non-zero when any gate fails, so a
regression in the rules fails a command rather than requiring someone to notice a
number moved. `--no-gate` reports without enforcing, for exploratory runs.

### The metric validates itself

`tests/test_metrics.py` runs the detectors against three fixtures:

1. A normal English paragraph → expect 0 violations and an article rate in the normal band.
2. A telegraphic rewrite of *the same content* → expect multiple violations and a
   sharply lower article rate.
3. A paragraph whose fenced code block is full of `->`, `impl`, and `err`, and whose
   prose is clean → **expect 0 violations.** This is the false-positive guard.

If the detectors cannot separate 1 from 2, the metric is broken and the suite fails —
the failure lands on the metric rather than being misread as a finding about the
plugin. Heuristics are acceptable precisely because this suite exists.

## Judge

A separate pass over the snapshot, written to `snapshots/judgments.json` so
re-judging never rewrites generation data.

- **Blind.** The judge sees the case prompt, the case's trap criteria, and the
  response text. It is not told which arm produced the text, and arm names never
  appear in its prompt.
- **Returns** `{"verdict": "pass"|"fail"|"not_exercised", "quote": "...", "reason": "..."}`.
  `not_exercised` is mandatory: v0.1.0 recorded three traps that never fired, and
  without this category they would have been read as passes.
- **Quote required** on every verdict, so a spot-check needs no re-run.
- Default model Sonnet. `--no-judge` produces a free, fully deterministic run.

## Snapshot schema

```json
{
  "metadata": {
    "generated_at": "2026-07-30T14:02:11Z",
    "claude_cli_version": "2.x.y",
    "git_commit": "563657d",
    "laconic_level": "full",
    "rules_cksum": "1234567890",
    "reps": 5,
    "models": ["haiku", "sonnet"]
  },
  "arms": {
    "baseline": {"system_prompt": null},
    "terse-control": {"system_prompt": "Answer concisely."},
    "word-compression": {"system_prompt": "..."},
    "laconic": {"system_prompt": "<full rules text>", "source": "hooks/laconic.sh start @ full"}
  },
  "runs": [
    {
      "case": "decision", "arm": "laconic", "model": "haiku", "rep": 0,
      "ok": true, "text": "...",
      "output_tokens": 120, "input_tokens": 10,
      "cache_creation_input_tokens": 3573, "cache_read_input_tokens": 17615,
      "total_cost_usd": 0.0096, "duration_ms": 2089, "num_turns": 1
    }
  ]
}
```

`rules_cksum` pins which rule text produced the numbers, so a stale snapshot is
detectable rather than silently misleading.

## Run mechanics

- **Isolation.** `CLAUDE_CODE_SAFE_MODE=1` and `LACONIC_DEFAULT` unset, so no arm
  inherits the developer's own `CLAUDE.md` or hooks — otherwise `baseline` is not a
  control and `laconic` could receive its rules twice. Each call runs in a temp cwd
  with the case fixture staged, never in the laconic repo: with tools enabled and cwd
  here, the model discovers it is inside the laconic plugin repo and answers the meta
  situation instead of the question.
- **Iteration order** is `(rep, case, model, arm)` with **arm innermost**, so the four
  arms for a given case are sampled at adjacent moments and temporal drift or
  throttling hits them evenly instead of loading onto whichever arm ran last.
- **Failures are recorded, never counted.** A non-zero exit or unparseable JSON is
  stored as `ok: false` and excluded from every statistic, with the exclusion count
  printed in the report. A failed call silently scored as a very short answer would
  read as excellent compression. One retry per call before recording a failure.
- **Resumable.** A run whose `(case, arm, model, rep)` key already exists in the
  snapshot is skipped, so an interrupted 320-call run continues instead of restarting.
- **Sequential.** ~320 calls at roughly 1.5–2 hours. Parallelism risks throttling that
  would confound the latency numbers; not worth it for a benchmark run this rarely.

### Command surface

```bash
python3 evals/bench/run.py [--level full] [--models haiku,sonnet] [--reps 5]
                           [--cases GLOB] [--arms NAME,...]
python3 evals/bench/judge.py [--model sonnet] [--cases GLOB]
python3 evals/bench/report.py [--no-gate] [--markdown OUT.md]
```

Defaults are the published configuration: level `full`, models `haiku,sonnet`,
5 reps, all cases, all arms. Narrowing flags exist so a single case can be
re-measured after a rule change without a two-hour run.

## Reported output

`report.py` regenerates all of this offline from the committed snapshots:

1. Median output tokens, per arm × model
2. Reduction vs `baseline` and vs `terse-control`, with min/max/stdev across reps
3. Readability violations, per arm × model, with `article_rate` and `aux_verb_rate`
4. Never-cut gate pass rate, per arm
5. Trap verdicts per case × arm, including `not_exercised` counts
6. Cost and duration, per arm × model
7. Excluded-run count

The README gains a headline table and a link to the dated writeup. `CRITERIA.md`
gains the four new cases, the never-cut keyword lists, and the metric definitions.

## Honesty notes (published with the numbers)

1. Single-turn calls, not sessions. The rules arrive via `--append-system-prompt`,
   not the hook path a real session uses.
2. Per-call cost pays cache *creation* every time; a real session pays cache *read*
   after the first turn. These numbers therefore **overstate** session cost.
3. Output tokens are the headline because that is what the rules control. Total cost
   carries a large fixed Claude Code system-prompt overhead (~17k cached tokens)
   identical across arms, which dilutes any percentage computed on totals.
4. The rules' own injection cost **is** measured and reported, so the compression
   figure is net. Both reference harnesses list this as unmeasured.
5. Readability detectors are heuristics with a validation suite, not a grammar
   parser. `article_rate` and `aux_verb_rate` are proxies for degraded grammar.
6. n=5 on two models separates a rule defect from adherence noise. It is not a
   powered experiment, and min/max/stdev are published so a reader can judge noise.
7. The `word-compression` arm is a synthetic instruction authored for this benchmark.
   It is not any specific plugin, and its exact wording is published above.

## Acceptance criteria

- `python3 evals/bench/report.py` regenerates every published table from the committed
  snapshots with no network access and no third-party packages installed.
- `tests/test_metrics.py` passes, including the code-block false-positive guard.
- A full run completes and its writeup lands at `evals/results/YYYY-MM-DD-benchmark.md`.
- The README carries a headline table plus the honesty notes.
- `evals/run.sh` still works against `evals/cases/` and writes to `evals/scratch/`.
- `.gitignore` no longer excludes `evals/results/`, and does exclude `evals/scratch/`.
- Two entries in `docs/v0.1.0-known-limits.md` — the n=1 caveat and the
  gitignored-results caveat — are struck as resolved, with the resolving run named.
- A failed call is provably excluded: a test forces a failure and asserts it does not
  enter the statistics.

## Deferred

- **Agentic benchmark.** Ponytail's strongest result comes from running real sessions
  against a seeded repo rather than single-shot prompts. That is the right eventual
  answer to "does this help in practice", and it is a separate project: it needs
  seeded repos, per-task graders, and session plumbing. Not in this spec.
- **Third-party plugin arms.** The synthetic `word-compression` arm tests the
  technique. Benchmarking a specific named plugin would require vendoring its rules
  and keeping them current, and publishing numbers about someone else's project
  carries an accuracy burden this project does not need to take on.
- **Opus arm.** Two models answer the adherence-ceiling question. A third multiplies
  runtime for a question already settled.
