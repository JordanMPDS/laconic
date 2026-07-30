# Mutation-hardening report — 14 gaps from the mutation sweep (33/60 missed)

Scope: test infrastructure only (`tests/test_bench.py`, `tests/test_metrics.py`,
`tests/stubs/claude-stub.sh`). No behavior changes in `evals/bench/*.py`.

Method for every row below: write the assertion → apply the named mutation to
the source (via a scratch `sed`/Python edit, never committed) → run the
suite and confirm it FAILS on the named assertion → revert the mutation
(`git diff` clean) → confirm the suite passes again.

## Table

| # | Gap | Mutation applied | Assertion that fired |
|---|-----|-------------------|------------------------|
| 1 | G1 — `call()` never exercised with a system prompt | Deleted the `if system_prompt: cmd += ["--append-system-prompt", system_prompt]` block from `run.py:call()` | `system_prompt is passed via --append-system-prompt immediately followed by the prompt text` |
| 2 | G2 — `laconic_rules()` could return a stale hardcoded copy | Replaced `laconic_rules()`'s body with a fixed string | `laconic_rules output matches invoking the hook directly for the same level` and `laconic rules differ between lite and ultra levels (a hardcoded constant could not do this)` |
| 3 | G3a — isolation: `CLAUDE_CODE_SAFE_MODE=1` unasserted | Changed `env = dict(os.environ, CLAUDE_CODE_SAFE_MODE="1")` to `env = dict(os.environ)` | `call() sets CLAUDE_CODE_SAFE_MODE=1 for the subprocess` |
| 4 | G3b — isolation: `LACONIC_DEFAULT` unset unasserted | Removed `env.pop("LACONIC_DEFAULT", None)` from `call()` | `call() strips LACONIC_DEFAULT from the subprocess env` |
| 5 | G4 — `run_key` can drop `rep` | Changed `run_key` to `return (case, arm, model)` | `run_key varying only rep produces distinct keys` |
| 6 | G5a — `never_cut_failures` could be hardcoded to 0 | Replaced the `never_cut_failures` computation in `aggregate()` with the literal `0` | `never_cut_failures counts the response missing a required keyword` and `the never-cut gate fires when a required keyword is missing` |
| 7 | G5b — never-cut gate could be deleted from `gate_failures()` | Removed the `if v["never_cut_failures"] > 0: ...` block from `gate_failures()` | `the never-cut gate fires when a required keyword is missing` |
| 8 | G6 — gate-failure exit contract unasserted through `main()` | Replaced `sys.exit(1)` in `report.py:main()` with `pass` | `a degraded laconic arm exits non-zero through main() by default` |
| 9 | G7 — bullet lowercase-start check was tautological | Neutralized `STRUCTURAL` regex (`re.compile(r"(?!)")`, never matches) | `bullet text starting lowercase after the marker does not trip lowercase-start (STRUCTURAL drops the whole bulleted line)` (plus 3 pre-existing assertions) |
| 10 | G8 — fenced-code checks were actually testing `INLINE`, not `FENCE` | Neutralized `FENCE` regex (`re.compile(r"(?!)")`, never matches) | `a fenced block with an odd internal backtick count (INLINE alone cannot consume it) still has its arrow stripped by FENCE` |
| 11 | G9-1 — `resolve_claude_bin` PATH lookup tautological | Changed `resolve_claude_bin` to `return arg` unconditionally (drop `shutil.which`) | `resolve_claude_bin('claude') resolves through PATH to the stub's real absolute location, not the bare string` |
| 12 | G9-2 — median fixture couldn't distinguish median from mean | Changed `"output_tokens": _median(tokens)` to `statistics.mean(tokens)` in `aggregate()` | `output_tokens is the true median (20), not the mean (40), of [10, 20, 90]` |
| 13 | G9-3 — excluded-run count unasserted (verified still-effective) | Hardcoded the excluded count to `0` in `render()`'s `"**Excluded runs..."` line | `report states the exact excluded count` |
| 14 | G9-4 — `threshold` argument could be ignored | Hardcoded `threshold = 0.70` at the top of `gate_failures()`, ignoring the caller's value | `two different thresholds produce different gate outcomes on the same data (threshold is not ignored)` |
| — | G9-5 — `STUB_FAIL` branch removal undetected | Removed the `[ "${STUB_FAIL:-0}" = "1" ] && exit 3` line from `claude-stub.sh` | `STUB_FAIL=1 makes the stub exit non-zero` |

14/14 items mutation-verified (row 13 was already a correct, effective
assertion in the current branch tip — re-verified rather than rewritten).

## Files changed

- `tests/stubs/claude-stub.sh` — records argv and the relevant isolation env
  vars (`CLAUDE_CODE_SAFE_MODE`, whether `LACONIC_DEFAULT` is set) to
  `STUB_ARGV_OUT` when that variable is set, ahead of the existing
  `STUB_FAIL`/`STUB_TEXT` behavior (unchanged).
- `tests/test_bench.py` — added/strengthened assertions for G1–G6 and all of
  G9; replaced the two tautological `resolve_claude_bin` and median checks.
- `tests/test_metrics.py` — added a discriminating lowercase-after-bullet-
  marker case (G7) and a FENCE-only fenced-code case (G8).

## Full gate

```
bash tests/test_rules.sh && bash tests/test_laconic.sh && \
  bash tests/test_evals_layout.sh && python3 tests/test_metrics.py && \
  python3 tests/test_bench.py && claude plugin validate . --strict && \
  claude plugin validate .claude-plugin/plugin.json --strict
```
All green, 0 failures across every suite.

## Published gate outcome — unchanged

```
python3 evals/bench/report.py --no-gate --judgments evals/snapshots/judgments.json
```

Still fails the same 4 gates:
- `badnews/haiku` article rate
- `conditional/sonnet` article rate
- `ordered-steps/sonnet` 5 readability violations
- `walkthrough/sonnet` 1 readability violation

No `evals/bench/*.py`, `evals/snapshots/*`, or `*.md` file (other than this
report) was modified — only test files and the offline stub.
