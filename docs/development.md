# Development

```bash
bash tests/test_rules.sh && bash tests/test_laconic.sh \
  && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict \
  && claude plugin validate .claude-plugin/plugin.json --strict
```

No framework, bash 3.2-safe. Covers the marker contract in `rules/laconic.md`
and the hook script's level whitelist, off switch, and write guard against a
symlinked flag file. `claude plugin validate .` resolves the marketplace
manifest and does not check skills or commands, so the second invocation points
at `.claude-plugin/plugin.json` directly.

The PowerShell hook has its own suite, running the same numbered cases against
`hooks/laconic.ps1`. It needs a Windows host, so CI is the normal place to see
it; on Windows you can run it directly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tests\test_laconic.ps1
```

```bash
./evals/run.sh full
```

Runs every case in `evals/cases/` — thirty-seven as of 2026-09-16 — with and
without the rules, writing paired output under `evals/scratch/<level>/<case>.md`
to read side by side. Grading criteria and the trap each case checks for are in
[`evals/CRITERIA.md`](../evals/CRITERIA.md). Single-sample, cheapest-model runs
for catching rule-set regressions, not a benchmark.

| Family | Cases | What it holds |
|---|--:|---|
| original | 11 | `badnews`, `code-fidelity`, `conditional`, `decision`, `destructive`, `fail-open`, `floor`, `ordered-steps`, `silent-success`, `stale-cache`, `walkthrough` |
| `design-*` | 8 | design questions, where the reading-rate mechanism lives |
| `verdict-*` | 3 | evaluative questions whose fixture contradicts itself |
| `confirm-*` / `recall-*` | 6 | the read-it against wrote-it pair for [#136], two turns each |
| `deep-*` / `wide-*` | 6 | the same three fixtures at five turns and at two |
| `cold-service` / `drift-service` | 2 | one fixture asked cold and at depth |
| `quota-merge` | 1 | a closed confirmation whose fixture hides a second consequence |

Ten of the thirty-seven are multi-turn, so a pass over them costs more calls
than cells — see [`evals/CRITERIA.md`](../evals/CRITERIA.md#a-case-may-ask-more-than-one-turn).
Cases under test live in [`evals/pilot/`](../evals/pilot/README.md) and are
outside the default glob, because adding one to `evals/cases/` moves
`cases_cksum` for every round that follows.

## End-to-end check

The unit and eval suites drive the hook script directly. This exercises the real
plugin in a live session, the only place the failure it guards against — a mode
that keeps injecting after being switched off — shows up.

In a fresh session:

1. Run `/laconic full`.
2. `cat ~/.claude/.laconic-level` → prints `full`.
3. Ask something ordinary — the response should come back with no preamble
   and no closing offer.
4. Run `/laconic off`.
5. `cat ~/.claude/.laconic-level` → prints `off`.
6. Ask something else — no `LACONIC MODE ACTIVE` line on that turn or after.

For the project flag, in a repository you do not mind writing a file into:

1. Run `/laconic full` first, so the machine flag is set and there is something
   for the project flag to override.
2. Run `/laconic ultra project`.
3. Confirm `cat .claude/.laconic-level` prints `ultra` and
   `cat ~/.claude/.laconic-level` still prints `full`.
4. Ask something ordinary and confirm the response is at `ultra`, not `full`.
5. Delete `.claude/.laconic-level`, start a fresh session, and confirm the level
   is back to `full`.

## Reproducing the benchmark

```bash
python3 evals/bench/run.py \
  --arms baseline,terse-control,word-compression,concise-style,laconic \
  --turn-delivery plugin                   # generate (~2,950 calls)
python3 evals/bench/judge.py --judge-all   # blind trap grading, every case
python3 evals/bench/report.py              # offline tables; exits 1 if a gate fails
```

**`run.py` with no `--arms` does not run.** The default is all sixteen arms,
two of which carry a Stop hook and refuse without `--no-safe-mode`, and the
suite now holds multi-turn cases, so `--turn-delivery` is refused-on-absence
too. Name the five arms the published tables use, as above. `run.py` prints the
call count and the cost before it makes a call, so check that line rather than
this one: ten of the thirty-seven cases are multi-turn, and a five-turn case at
5 reps across 5 arms is 250 calls where a single-turn one is 50.

`run.py` and `judge.py` both print what the pass will cost before making a call,
and both stop themselves after eight consecutive failures — a usage limit or an
outage otherwise fails every remaining key at two calls each. Re-run the same
command to resume; neither a failed key nor a failed judgment is recorded as
done.

`--judge-all` because the published tables report every case, including the
three graded `rule-adherence`. The default grades only the cells a fatal counter
can read, which is what a loop round wants and 35 fewer calls at n=5.

**Sharding the pass across processes is allowed, and must be declared.** One
`run.py` is sequential, so a snapshot merged from five of them describes a
regime no single process could produce. Running several is roughly 4x faster
and each process owns its own shard file, but every one of them needs
`--concurrency N`, where N is how many processes are being launched over the
round including this one. That stamps `metadata.concurrency_declared`, and each
pass warns when its own timestamps reconstruct to more invocations than it
declared. `--concurrency` defaults to 1, which is correct for the single
sequential command above and needs no flag.

Audit the whole archive at any time — it reads committed snapshots and calls
nothing:

```bash
python3 evals/bench/concurrency.py   # exits non-zero on an undeclared snapshot
```

### What a generation pass refuses to do

`run.py` fails at startup rather than producing a snapshot that cannot be read.
Each refusal names the round that bought it:

| Guard | Refuses when | Override |
|---|---|---|
| `--turn-delivery` | the pass has multi-turn work left and no delivery mode was named. `plugin` reproduces the shipped hook wiring; `repeat` re-appends the whole slice every turn and is what every snapshot below round 40 holds | name one; there is no default |
| `--allow-opus '<why>'` | `judge.py --model` names an opus, in single-judge compatibility mode. The default panel includes opus, and `run.py` refuses nothing | `--allow-opus` with a reason, recorded as `metadata.opus_justification` |
| `--max-shards` | that many `run.py` processes are already running. Five shards plus the supervisor's own child took the loop for low memory on a 7.6 GiB machine | `--max-shards N`, `LACONIC_MAX_SHARDS=N` per machine, or `--max-shards 0` |
| `--cells` | it is passed alongside `--cases` or `--models`, or a resume names a different cell set | drop the other two flags |
| `--allow-stale-arm` | a requested arm under `evals/arms/` was built from a different rules slice than this tree carries | rebuild the arm and update `evals/arms/BUILT-FROM.json`, or pass the flag deliberately |
| `--allow-case-change` | `cases_cksum` moved since the snapshot was started | the flag, which stamps the fact into the snapshot |
| `--no-safe-mode` | an arm carries a Stop hook, which `CLAUDE_CODE_SAFE_MODE=1` would disable outright — the arm would generate as a second copy of laconic | the flag, which drops safe mode for every arm in the pass |
| rules checksum | a resume finds `rules/laconic.md` has moved | none; move the snapshot aside |

`--concurrency` refuses nothing. It is a declaration, and `concurrency.py`
audits it. `--max-consecutive-failures` defaults to 8 and stops a pass that an
outage or a usage limit would otherwise fail key by key; re-run the same command
to resume.

`--stop-on-cli-change` refuses a round that spans a `claude` release instead of
recording it. It is not the default, because a round that runs for hours
normally spans one.

### Sharded rounds, and which release generated them

Merge a round's shards into the snapshot the report reads. It refuses shards
that disagree on `rules_cksum`, level or arm definitions, so two designs cannot
be merged into one round:

```bash
python3 evals/bench/merge.py evals/snapshots/loop/round-70-a.json \
  evals/snapshots/loop/round-70-b.json --out evals/snapshots/loop/round-70.json
```

The CLI ships several times a day and a round runs for hours, so a round
normally spans a release. `run.py` reads `claude --version` before every
generation and stamps that run with it. Report the composition, and test whether
the arms are balanced across the boundary:

```bash
python3 evals/bench/release.py evals/snapshots/loop/round-70.json
```

With no arguments it sweeps the archive and reports only what it cannot read.
Balance testing runs when snapshots are named explicitly. Seventeen committed
snapshots predate the per-run stamp and carry a label that is wrong for part of
their runs — `round-21.json`, the one the published benchmark tables come from,
is among them. They are listed in
[`evals/results/loop/release-audit.md`](../evals/results/loop/release-audit.md),
and the field may not be stratified on for those files.

### The rest of the harness

| Script | What it is |
|---|---|
| `evals/bench/metrics.py` | the deterministic detectors, `decisions()` and `score()`. A library, not a command; both graders and both test suites route through it |
| `evals/bench/stop_hook.py` | the [#268] enforcement arm: a `Stop` hook that asks for one revision when the completed turn broke a rule already in context. **Benchmark-only — nothing under `hooks/` registers it**, and [`production-turns-283.md`](../evals/results/loop/production-turns-283.md) is why: over 1,429 real turns it blocks 6.5% against a 5% bar, and half the blocks are wrong |
| `evals/bench/transcripts.py` | runs the shipped detectors over real session transcripts, which is how that cost was measured |
| `evals/bench/subagent.py` | the subagent relay arm ([#6]): hands one arm's response to a parent model as a subagent report and grades the parent's answer |

[#268]: https://github.com/JordanMPDS/laconic/issues/268
[#6]: https://github.com/JordanMPDS/laconic/issues/6

## Tools

| Script | What it answers |
|---|---|
| `bash tools/build-rules.sh` | regenerates `rules/dist/*.md` by driving the hook itself, so the marker contract is never reimplemented. Required whenever `rules/laconic.md` changes; `tests/test_rules.sh` fails on a stale copy |
| `bash tools/release-due.sh` | is a release owed? Diffs the shipped surface against the newest `laconic--v*` tag, names every file that moved, and recommends patch or minor. `README.md` and `docs/` are deliberately outside that surface |
| `bash tools/candidate-due.sh` | must the next round carry a rule candidate? Exits 1 when two measuring rounds would run back to back, reading the declaration each round document already makes |
| `bash tools/reclaim-scratch.sh` | removes spent scratch worktrees. On this machine `/tmp` is tmpfs, so a worktree left behind is held RAM. It removes one only when nothing is working inside it, it holds no untracked file, and its HEAD has already landed on `origin/master`; `--dry-run` says what would go |
| `bash tools/consult.sh "<question>"` | asks the delegate targets one question and prints what they say. Creates no worktree and writes nothing; a dead target is named rather than failing the caller |
| `bash tools/loop.sh` | the backlog supervisor: one `claude` process per issue, so each gets a genuinely empty context. It runs `reclaim-scratch.sh` at the top of every iteration |

Each of the five with a `--selftest` is exercised by `tests/test_rules.sh`.

**It exits 1 on the archive as it stands**, because snapshots generated before
the flag existed have their regime reconstructed from timestamps rather than
declared. Those are documented in
[`evals/results/loop/concurrency-audit.md`](../evals/results/loop/concurrency-audit.md),
which also bounds what the regime does to a measurement: nothing detectable on
`output_tokens`. Read the command as a diff against that known set — a snapshot
you generated appearing in the list is the signal, not the exit code alone.

## Improving the rules

`.claude/skills/laconic-loop/SKILL.md` holds the procedure: benchmark, review
the failures, propose one rule edit, confirm it, and open a PR or throw it
away. A round ends in a pull request either way — the repository refuses a
direct push to master — and the round document lands whether the edit shipped
or reverted. The design and the reasoning behind every threshold are in
[`docs/superpowers/specs/2026-08-01-rules-loop-design.md`](superpowers/specs/2026-08-01-rules-loop-design.md).

The read step runs offline over snapshots you already have:

```bash
python3 evals/bench/review.py evals/snapshots/results.json \
  --judgments evals/snapshots/judgments.json \
  --preferences evals/snapshots/preferences.json
```

Every failure comes back with its excerpt verbatim and the line of
`rules/laconic.md` that governs it. A failure with **no** governing rule ranks
first — the rule set is silent where the benchmark checks, which points at
writing a rule rather than editing one.

The compare step turns two rounds into a verdict and exits 1 on reject:

```bash
python3 evals/bench/report.py --results <round-N+1> --judgments <round-N+1-judgments> \
  --against <round-N> --against-judgments <round-N-judgments> \
  --preferences <round-N+1-preferences>
```

Four counters reject on their own, whatever the target did: a never-cut item
dropped, a quality verdict lost, a **safety** verdict lost, readability
violations up.

A hypothesis that named cases is scored on them: add
`--target-cases walkthrough,ordered-steps` to a count target and it is computed
over those cells alone, with the round-wide number printed beside it. The fatal
conditions stay round-wide, so an edit that fixes the cases it aimed at while
breaking another still rejects.

`evals/holdout/` holds six cases the loop never sees, scored once before a
rule change ships: two never-cut items, a requested explanation, a short
question whose correct answer is brief, a bare design question and an
evaluative one. Reach them with `--cases-dir evals/holdout`, which `run.py`,
`judge.py`, `report.py` and `review.py` all accept. Their numbers never enter a
published table.

Every attempt goes in [`evals/results/loop/LEDGER.md`](../evals/results/loop/LEDGER.md),
**including rejected ones** — an accept rate is what lets a reader discount a
claim the loop produces.

## Blind pairwise preference

`evals/bench/prefer.py` grades responses the snapshot already holds — it calls no
generation and regenerates nothing. Count the calls before spending anything:

```bash
python3 evals/bench/prefer.py --dry-run
# 130 comparisons (110 forward, 20 flipped) over 220 responses
```

Then run it, and tally an existing run without calling at all:

```bash
python3 evals/bench/prefer.py --control baseline   # or --control terse-control
python3 evals/bench/prefer.py --report-only
```

Resumable on the same snapshot semantics as `judge.py`, and refuses to top up
verdicts built against a different `rules_cksum`. `--both-orders N` re-runs N
comparisons with A and B swapped; the flip rate prints beside the headline, and
at or above 50% the result is position bias rather than preference. What a
preference verdict may and may not support is in
[`evals/CRITERIA.md`](../evals/CRITERIA.md).

The three-level run, and its offline report:

```bash
for L in lite full ultra; do
  python3 evals/bench/run.py --level "$L" --arms laconic \
    --snapshot "evals/snapshots/levels-$L.json"
done
python3 evals/bench/levels.py   # ladder verdicts, never-cut and readability per level
```

`levels.py` exits non-zero when the cross-level run is incomplete - a level with
no usable snapshot, or a model with no usable run at one of them - and zero
otherwise. The length ladder verdict (`monotonic`, `flat`, `broken`) never
decides the exit code: it reports what a generation run measured, and on the
committed snapshots it reads `broken` for both models. What is gated instead is
decision monotonicity, which is a property of the code rather than of a run:
`metrics.decisions(text, level)` returns the findings in force at one level, and
`tests/test_metrics.py` and `tests/test_bench.py` assert that those sets nest
across `lite`, `full` and `ultra`.

Results and what the numbers mean: [`docs/benchmark.md`](benchmark.md).
