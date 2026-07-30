# Final whole-branch review: code fixes (A-G)

Branch `feat/benchmark-v0.2.0`. Code and tests only - no `.md` file touched.

## Method

For every fix: added the assertion first, ran it against the pre-fix code to
confirm it failed (for real - `git stash` isolating only the source files,
or a copy of the old module loaded from `git show HEAD:...`), then
implemented the fix and reran to confirm green. Details of what was broken
and what failed are below per item.

## A - metrics.py symbol detector

`_symbol_hits()` now scans line-by-line, skipping `STRUCTURAL` lines
(bullets/headings/tables) and skipping arrows with a digit on both sides
(numeric progressions). `abbreviated_prose` checked separately: real dataset
shows 0 hits for it (no observed defect), left as-is per instructions.

Pre-fix failures observed (via `tests/test_metrics.py`):
- `- **401** -> the token is dead.` scored `symbol_connectors == 1` (wanted 0)
- `The queue climbed (7 -> 11 -> 14) over the hour.` scored `2` (wanted 0)
- Added the bullet line to the shared `GOOD` fixture - `good prose has no
  violations` also failed pre-fix (`violations == 1`)
- `Deploy failed -> restart.` already scored `1` pre-fix (no regression there)

All four pass post-fix.

## B - report.py readability gate used a median

`gate_failures()` now checks `violations_total` (sum across reps), not the
median. `aggregate()` adds `violations_total` and
`violations_flagged_responses`; median stays in the display table.

Proof: built a synthetic 5-rep bucket (3 clean, 2 with 2 running-prose-arrow
violations each). `statistics.median([0,0,0,2,2]) == 0`. Ran the **old**
`gate_failures()` against it: returned `[]` - the regression was invisible.
New code returns a failure naming the case. This is not just synthetic: the
regenerated report on the real snapshot now shows a genuine catch -
`ordered-steps/sonnet: 0.0 readability violation(s) (total 5)` - a case the
old median-based gate would have passed clean.

## C - output-token dispersion (min/max/stdev)

Added to `aggregate()`: `output_tokens_min`, `_max`, `_stdev`
(`statistics.stdev`, guarded for n<2 -> 0.0). Rendered as three sub-tables
under "Output tokens dispersion across reps".

Proof: old `aggregate()` had none of these three keys; old `render()` output
had neither `"min:"` nor `"stdev:"` anywhere.

## D - never-cut checked vs unchecked

`aggregate()` adds `never_cut_checked` (bool: case's `never_cut` list is
non-empty). Table is now `| arm | checked | unchecked | failures |`.

Proof: old table for a synthetic mix of a checked case (`destructive`) and
an unchecked one (`floor`, empty `never_cut`) rendered `| laconic | 0 |` -
indistinguishable from "verified clean" versus "never checked at all". Real
snapshot now shows, e.g., laconic: 50 checked / 30 unchecked / 0 failures.

## E - "unparseable" judge output misrouted

`REASON_JUDGE_CALL_FAILED`, `REASON_UNPARSEABLE`, `INFRA_REASONS` defined
once in `judge.py`; `report.py` imports `judge` and routes both reasons to
`judge_failed` instead of matching only the literal `"judge call failed"`.

Proof: old code, given one judgment with `reason: "unparseable"`, rendered
`not_exercised=2, judge_failed=1` for the mixed fixture; correct split is
`not_exercised=1, judge_failed=2`.

## F - judge.py integrity gaps

1. **Retry**: `_call_blind()` retries once, mirroring `run.py`. Proof: a
   stub that fails on invocation 1 and succeeds on 2, run through the old
   `judge.py` - counter file read `"1"`, judgment recorded
   `"judge call failed"`. New code: counter reads `"2"`, judgment is a real
   result.
2. **Checksum guard**: hard-exits if `judgments.json`'s `results_cksum`
   doesn't match the current `results.json`'s `rules_cksum`. Proof: old
   `judge.py` given a deliberately mismatched pair exited 0 with no
   complaint; new code exits non-zero naming both checksums and leaves the
   file untouched.
3. **Blindness**: `_call_blind()` runs each attempt in a fresh `tempfile.mkdtemp()`,
   not `cwd=ROOT`. Proof: a stub that logs `$PWD` to a file independent of
   its JSON stdout showed `cwd == ROOT` under the old code (able to see
   `evals/snapshots/results.json` and `rules/laconic.md`); new code logs a
   scratch dir.
4. **Completeness check**: `report.py` adds `_judgment_gap()`; warns (stderr
   and in the rendered markdown) when judgments don't cover all usable runs,
   naming the shortfall (`"judgments cover 1/3 usable runs (2 missing)"`).
   Proof: old `render()` had no such function and produced no warning for
   the same partial-coverage fixture.

## G - cheap correctness

- `_cli_version(claude_bin)` now takes the resolved binary (was hardcoded
  `"claude"`), with a 10s timeout and a return-code check. Proof: pointed
  `run.py --claude-bin` at a stub whose `--version` prints a distinctive
  marker; old code's snapshot recorded the real `claude` CLI's version
  instead (ignored the flag entirely).
- `--arms bogus-arm` now exits with `"unknown arm(s): bogus-arm (valid: ...)"`
  before any work starts. Proof: old code raised a bare `KeyError` traceback
  from inside the run loop.
- `parse_cli_json` treats a missing or non-string `result` (with
  `is_error: false`) as `ok: false`. Proof: old code returned `ok: True`
  for both `{"is_error": false, "result": null}` and `{"is_error": false}`.
- `report.py` main() catches a corrupt judgments file and exits naming the
  file, instead of a raw `JSONDecodeError` traceback. Proof: reproduced the
  raw traceback against old code via subprocess.
- `tests/stubs/claude-stub.sh` escapes backslashes and quotes in `STUB_TEXT`
  before interpolating into JSON. Proof: `STUB_TEXT='He said "stop".'`
  produced invalid JSON under the old stub.
- `tests/test_bench.py`: replaced the tautological `"arm" in md` (matches
  the literal string "warm") with a check on the actual rendered table
  header; the adjacent "excluded" check now asserts the exact count (`1`),
  not just the word's presence.
- `.gitignore` now ignores `__pycache__/`.

## Verification

```
bash tests/test_rules.sh && bash tests/test_laconic.sh && bash tests/test_evals_layout.sh \
  && python3 tests/test_metrics.py && python3 tests/test_bench.py \
  && claude plugin validate . --strict && claude plugin validate .claude-plugin/plugin.json --strict
```
All green (0 failures across every suite; both plugin manifests validate).

`python3 evals/bench/report.py --no-gate --markdown /tmp/bench-tables-v2.md`
regenerated cleanly from the existing committed snapshots - no new model
calls. With gating on (no `--no-gate`), the regenerated report now fails 7
gates that were previously invisible (rate-floor gates plus two real
readability regressions the median was hiding: `ordered-steps/sonnet` and
`walkthrough/sonnet`, both laconic arm). That's the detector and the gate
doing their jobs on real data, not a regression introduced here.

## Readability numbers: before vs. after (n=80 responses per arm)

**Before** (buggy detector - arrows counted in markdown bullets/headings/
tables and numeric progressions):

| arm | total violations | responses with >=1 violation | symbol hits | lowercase-start hits |
|---|--:|--:|--:|--:|
| baseline | 79 | 21 | 77 | 2 |
| terse-control | 50 | 11 | 50 | 0 |
| word-compression | 70 | 20 | 68 | 2 |
| laconic | 75 | 16 | 74 | 1 |
| **total** | **274** | | **269** | **5** |

**After** (fixed detector - running-prose arrows only, numeric progressions
excluded):

| arm | total violations | responses with >=1 violation | symbol hits | lowercase-start hits |
|---|--:|--:|--:|--:|
| baseline | 2 | 2 | 0 | 2 |
| terse-control | 4 | 3 | 4 | 0 |
| word-compression | 5 | 3 | 3 | 2 |
| laconic | 6 | 2 | 5 | 1 |
| **total** | **17** | | **12** | **5** |

`abbreviated_prose` is 0 in both before and after for every arm (unaffected,
unchanged). The 12 post-fix symbol hits match the review's own estimate of
"12 candidate running prose" arrows exactly.

## Follow-up: absolute-count floor on rate gates, and gate message clarity

Coordinator flagged two issues after independently verifying the A-G wave.

**1. Rate gates false-fired on baselines with too little raw material.**
`RATE_FLOOR` floors the *rate*, which a short answer clears trivially even
with ~1 auxiliary word in it. Added `ABS_COUNT_FLOOR = 5` and two new
`aggregate()` fields, `article_count`/`aux_count` (median of `words *
rate` per response - the actual count the rate is built from). Each rate
gate now additionally requires `base["article_count"]` /
`base["aux_count"] >= 5` before it applies; `RATE_FLOOR` kept as a cheap
secondary check per the coordinator's "keep it if you like."

Proof: `git stash` on `report.py` alone (isolating this one change on top of
the already-committed A-G fixes), reran the two new assertions - both
failed pre-fix (`a baseline with ~1 auxiliary word does not trip the
aux-rate gate` failed; the "healthy count still gates" counterpart already
passed, confirming it wasn't a vacuous test). Restored the fix, both pass.

**2. Gate message contradicted itself.** Reworded to lead with the number
the gate used: `"%d readability violation(s) across %d response(s) (median
%.1f) sample: %s"` - total first, median still shown (not rounded away),
`spans` relabeled `sample:` since it's pooled and truncated to 5 regardless
of the actual violation count. Proof: same stash isolation - the old format
string doesn't contain `"N readability violation(s) across N response(s)"`,
so both new message-format assertions failed pre-fix.

**`ordered-steps/sonnet` confirmed to survive.** Regenerated
`/tmp/bench-tables-v3.md` from the same committed snapshot (no new model
calls, no `evals/snapshots/` changes). Gate failures dropped from 7 to 4:

```
- badnews/haiku: article rate 0.048 below 70% of baseline 0.076 (baseline had ~5.0 article words)
- conditional/sonnet: article rate 0.067 below 70% of baseline 0.102 (baseline had ~10.0 article words)
- ordered-steps/sonnet: 5 readability violation(s) across 5 response(s) (median 0.0) sample: ['→', '→', '→', '→', '→']
- walkthrough/sonnet: 1 readability violation(s) across 5 response(s) (median 0.0) sample: ['auth.js is self-contained — 40 lines, no']
```

Suppressed (baseline had <5 article/aux words - not enough raw material for
"below 70%" to mean anything): `code-fidelity/haiku` (aux, ~1.0 words),
`floor/haiku` (aux, ~2.0 words), `floor/sonnet` (aux, ~4.0 words). Both
readability-total failures (the real regressions, including the genuine
`ordered-steps/sonnet` arrow chain in running prose) are untouched by this
change - they gate on `violations_total`, not the rate/count logic - and
both still fire.

## Follow-up 2: the "totals" table rendered a median, not a total

Coordinator caught this while extracting numbers for the writeup:
`_by_arm_model` medians across cases unconditionally, so the tables headed
"Readability violations (total across responses; this is what gates)" and
"Responses with >=1 readability violation" both rendered a
median-of-per-case-totals under a "total" label. For laconic/sonnet the
per-case `violations_total` values are `[5, 1, 0, 0, 0, 0, 0, 0]` - sum 6,
median 0 - so the table printed 0 next to a gate reporting 5. Same defect
shape as the gate-message fix above, one level up in the rendering.

**Fix:** `_by_arm_model` now takes an `agg_fn` parameter (default
`_median`, unchanged for the seven other tables that use it - output
tokens, dispersion, article/aux rate, cost, duration). The two
violation-count tables pass `agg_fn=sum`, since they're explicitly labeled
totals and sum is what `gate_failures()` actually uses. One shared
function, no duplicate table-rendering code.

Proof: added a 3-case fixture (`c1`/`c2`/`c3`) with per-case
`violations_total` of `[5, 0, 0]` (sum 5, median 0) and asserted the
rendered row shows `| laconic | 5 |`. `git stash` on `report.py` alone (on
top of the already-committed fixes) reran it: `FAIL` pre-fix. Restored,
passes. Applied the same fixture/assertion to the flagged-responses table
(`[1, 0, 0]` -> expected `1`) since it has the identical defect - also
proven to fail on the same isolated pre-fix code, now passes.

Regenerated `/tmp/bench-tables-v4.md` from the same committed snapshot (no
new model calls, `evals/snapshots/` untouched). Corrected totals table:

| arm | haiku | sonnet | row total |
|---|--:|--:|--:|
| baseline | 0 | 2 | 2 |
| terse-control | 1 | 3 | 4 |
| word-compression | 0 | 5 | 5 |
| laconic | 0 | 6 | 6 |

Row totals match the coordinator's independent 80-response check exactly
(baseline 2, terse-control 4, word-compression 5, laconic 6). Gate outcome
re-verified unchanged - still exactly 4 failures: `badnews/haiku` and
`conditional/sonnet` (article rate), `ordered-steps/sonnet` (5 violations
across 5 responses), `walkthrough/sonnet` (1 violation across 5 responses).
