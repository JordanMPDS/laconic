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

Runs all eleven cases (`badnews`, `code-fidelity`, `conditional`, `decision`,
`destructive`, `fail-open`, `floor`, `ordered-steps`, `silent-success`,
`stale-cache`, `walkthrough`) with and without the rules, writing paired output
under `evals/scratch/<level>/<case>.md` to read side by side. Grading criteria
and the trap each case checks for are in [`evals/CRITERIA.md`](../evals/CRITERIA.md).
Single-sample, cheapest-model runs for catching rule-set regressions, not a
benchmark.

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
python3 evals/bench/run.py      # generate (~440 calls, 2-3 hr)
python3 evals/bench/judge.py    # blind trap grading
python3 evals/bench/report.py   # offline tables; exits 1 if a gate fails
```

## Improving the rules

`.claude/skills/laconic-loop/SKILL.md` holds the procedure: benchmark, review
the failures, propose one rule edit, confirm it, and open a PR or throw it
away. It proposes; a human merges. The design and the reasoning behind every
threshold are in
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

A hypothesis that named cases is scored on them: add
`--target-cases walkthrough,ordered-steps` to a count target and it is computed
over those cells alone, with the round-wide number printed beside it. The fatal
conditions stay round-wide, so an edit that fixes the cases it aimed at while
breaking another still rejects.

`evals/holdout/` holds four cases the loop never sees, scored once before a
rule change ships. Reach them with `--cases-dir evals/holdout`, which `run.py`,
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

Results and what the numbers mean: [`docs/benchmark.md`](benchmark.md).
