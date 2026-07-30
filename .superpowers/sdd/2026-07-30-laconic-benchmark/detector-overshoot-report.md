# Detector overshoot fix + benchmark republish

Scoped re-review task: the readability detector over-corrected in laconic's own favor,
hiding real violations. Fixed the detector, recomputed, republished the docs with the
resulting (worse-for-laconic) numbers.

## Part 1 — detector fixes (`evals/bench/metrics.py`)

**B1 — `STRUCTURAL` bullet regex.** Changed
`r"^\s*([-*+>|#]|\d+[.)])"` to `r"^\s*([-*+#]\s|[>|]|\d+[.)]\s)"` — `-`, `*`, `+`, `#`, and
an ordered-list digit now require a following space to count as a bullet marker; `>` and
`|` still don't (blockquotes/table rows). This stops `**Request A**: ...` (a bolded prose
paragraph) from being misread as a bullet and dropped whole from `_symbol_hits`, and stops
`-> arrow` / `  -> arrow` (post-inline-code-strip) from being misread as a `-` bullet.
`ordered-steps/sonnet`'s genuine 5-arrow runbook still scores 5 (verified, unchanged).

**B3 — `_lowercase_starts` false positives (all 5 in the run).**
- Added `DOTTED_IDENTIFIER` regex to skip a sentence opening with a bare filename/dotted
  identifier (`auth.js`, `pool.max`) not wrapped in backticks — fixes 2 false positives
  (`walkthrough/laconic/sonnet` reps 1 and `word-compression/sonnet` rep 2).
- Widened `FENCE` from `r"```.*?```"` to `r"\s*```.*?```\s*"` so removing a fenced block
  also removes its immediately flanking whitespace/newlines, instead of leaving a
  whitespace-only line that `_paragraph_prose` reads as a paragraph break. Fixes 3 false
  positives, all in `destructive` (baseline reps 0 and 3, word-compression rep 2), where a
  fence-interrupted sentence like "...safer sequence: ```sql...``` or if you do want to
  actually drop/recreate: ..." was splitting "or"/"then" off as a fake new sentence.

All 4 fixes are covered by new assertions in `tests/test_metrics.py`, each proven to fail
against the pre-fix detector before the fix was applied, and passing after. An assertion
that a bolded-label arrow chain **is** counted (the regression this work exists to prevent)
is included and passes.

## Part 2 — recompute

`python3 evals/bench/report.py --no-gate --judgments evals/snapshots/judgments.json`
against the unmodified `evals/snapshots/` — no re-generation, no re-judging.

- Symbol hits: 12 → 25 (reviewer predicted ~24).
- `sentence_initial_lowercase`: 5 → 0 project-wide (all 5 were false positives).
- Readability violations total: 17 → 25.
- Per-arm/model totals: baseline 0|0, terse-control 2|3, word-compression 0|4,
  **laconic 8|8** (was 0|6).
- Gate failures: 4 → **5** — new failure at `walkthrough/haiku` (8 violations, a
  two-bolded-paragraph, 4-arrows-each "Request A"/"Request B" response — confirmed genuine
  by reading the text, same construction the B1 bug was hiding).
- `ordered-steps/sonnet` still scores 5/5, confirmed unchanged.

## Part 3 — document updates

**D1** — Rewrote the correction-log entry that falsely claimed the previous version didn't
disclose laconic's gate failure (it did, twice: prose in "Rate gates are unvalidated" and a
`**FAILED (9):**` block). Replaced with what's actually new: the sum-based gate, the
verified `ordered-steps` defect, promotion to a body section. Added a new correction-log
item (8) disclosing this revision's own detector fix and its effect.

**D2** — Rewrote every readability figure: headline, per-arm/model table, "no arm degrades
grammar meaningfully" claim, "6 of 17 belong to laconic" claim — all replaced with the
corrected numbers and an honest statement that laconic now has the worst count of any arm
(16/25, 64%), driven by a stylistic habit the earlier detector bug was blind to.

**D3** — Added disclosure of two remaining detector gaps (neither triggered in this run):
`_is_numeric_progression` can't distinguish a quoted data progression from a
digit-adjacent conjunction (`"scale replicas 2 → 4 to fix it"`), and `SYMBOLS` doesn't
match `⇒`, `~>`, or `>>`.

**D4** — Added a paragraph applying the same skepticism to the two firing rate-gate
readings (`badnews/haiku` clears the absolute floor at exactly 5.0; `conditional/sonnet`'s
baseline ranges 3–15 per rep) that the doc already applies to the three suppressed ones.

**D5** — Fixed the exclusion table (`word-compression` is 50/59 = 85%, not 50/60 = 83%,
due to one `judge_failed` cell; this technically moves it above `terse-control`, noted
explicitly — the "laconic 3rd of 4" conclusion is unaffected). Disambiguated "+0.9%" as
"laconic 0.9% shorter (598.5 vs 604.0 flat median)". Updated README wherever it repeated
changed figures.

## Part 4 — code nits

- `report.py`: wrapped `bench_run.load_snapshot(args.results)` in the same
  try/except-ValueError guard `_load_judgments` already had, with a matching test.
- `judge.py`: renamed the stored/read checksum key from `results_cksum` to `rules_cksum`
  (it always held the rules checksum, not a hash of results.json). Reads fall back to the
  legacy `results_cksum` key so the already-committed `judgments.json` snapshot (which
  still has the old key) keeps working without being touched. New test asserts the write
  path uses the new key name.

## Verification

Full gate green: `test_rules.sh`, `test_laconic.sh`, `test_evals_layout.sh`,
`test_metrics.py`, `test_bench.py`, `claude plugin validate . --strict`,
`claude plugin validate .claude-plugin/plugin.json --strict`. The doc's "Full tables"
section byte-matches `report.py --no-gate --judgments evals/snapshots/judgments.json`
(diffed directly). `evals/snapshots/` untouched (`git diff --stat` empty for that path).
