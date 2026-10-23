# Round 119: does a tool-less judge grade the fixture once the trap carries it? (#414)

**Registration. Nothing below the results line has been computed**, except
the tool-use counts in **Why this round exists**, which read stored
judgments and bought nothing, and the draw `score_facts.py build` printed,
which reads stored runs. This file, `evals/pilot/fixture_facts.py`, the
twelve rewritten traps, `evals/pilot/score_facts.py` and the layout check are
committed before any judging.

**This round proposes no rule edit.** It tests an instrument change, so
round 120 owes a candidate.

`bash tools/release-due.sh` exited 0 at registration: v0.3.9 is tagged and
current. `bash tools/candidate-due.sh` exited 0: round 118 tested a
candidate, so this round may measure.

## Why this round exists

Since [#411] no judge has tools. Each one sees the question, the criterion
and the response, and no file. Some pilot criteria grade the response
against the fixture all the same. `simplify-*` and `verify-*` fail an answer
that *"states something about the current code, tables or `<data file>`
that the fixture contradicts"*, and `subset-*` and `deepsubset-*` fail one
that *"states a seeded value the record does not give"*.

Until #411 the judges opened the fixture to check those clauses
themselves. A tool-less judgment is one turn per claude member, so
`num_turns` above the number of claude members that voted is a judgment
that used a tool. Across every committed judgments file:

| case | judgments that used a tool |
|---|--:|
| `simplify-quota`, `simplify-rates`, `simplify-routing` | 80/80 each |
| `subset-ledger` | 58/180 |
| `subset-gateway` | 49/180 |
| `subset-scheduler` | 45/180 |
| the other 35 pilot cases ever judged, pooled | 23/6,259 |

The answers make claims only the fixture can settle: round 118's
`simplify-rates` answers print the whole 7-by-6 price grid and say *"13
heavy parcels to remote zones"*, and its `simplify-routing` answers say
*"billing received none of September's 22 sev1/sev2 payments and ledger
alerts"*. From #411 on, no judge could check any of that. [#414] is the
issue.

## The instrument change

Option 1 of #414. Each affected trap now ends with a block that
`evals/pilot/fixture_facts.py` writes from the fixture itself, so the judge
stays text-only and all three members see the same evidence.

- **`simplify-*` and `verify-*`:** every fixture file except the data file,
  verbatim, which is the code, the two tables and the README. Then the value
  the fixture's own function gives for every combination its tables hold,
  each cell the special case changes marked with its value before the
  change. Then the data file, which no judge could read by eye: its header,
  row count and date range, how many rows the special case changes (62, 13
  and 22), and its rows per combination. `simplify-routing` also states
  that `apply_payments_override` replaces the owning team, although its
  docstring says *"as well as the owner"*, because that is the one place a
  fixture disagrees with itself and answers quote it.
- **`subset-*` and `deepsubset-*`:** `STATUS.md`, verbatim. It is the whole
  fixture.

The code is run with `runpy`, which writes no `__pycache__` into the
fixture. The block opens by saying that it is evidence for the clauses
above it and that an answer need not mention any of it. It adds no fail
condition: a `subset-*` trap that fails only a misstated seeded value must
not start failing a miscounted section because the record is now on the
page. `tests/test_evals_layout.sh` runs `fixture_facts.py --check`, so a
fixture edit that leaves its trap behind fails the suite.

Two things this changes for any comparison. `criteria_cksum` and the
twelve cases' `cases_cksum` both move, so `judge.py` refuses to carry a
pre-#414 verdict on these cases into a post-#414 file, as #414 asks. And a
`simplify-*` verdict from round 118 and one from round 120 are now from
different instruments in two ways (tools, then the block), so a round that
compares across them re-judges one side.

## The test (210 judgments, about 420 claude calls and 210 kimi calls)

`python3 evals/pilot/score_facts.py build` draws, at seed 119:

- **U:** 45 responses the tool-using panel passed: 10 per `simplify-*` case
  from round 118's four judged snapshots, and 5 per `subset-*` case from
  rounds 96 and 97. A `subset-*` response qualifies only if it names one of
  its record's eight seeded questions as `OQ-n`, so that it can be mutated.
- **F:** every response the tool-using panel failed on those six cases: 1
  `simplify-rates` and 14 `subset-*`.
- **M:** each U response with one near-miss fixture error seeded into it.
  The token is a figure the case's block states and its pre-#414 trap does
  not, and every occurrence of it moves by one in its last place: 3000 to
  3001, 7.22 to 7.23, 812 to 813. A `subset-*` mutant renames one seeded
  question to an OQ number its record does not have. All 45 draws were read
  in context before registration and each states a fixture fact, so none
  was redrawn: 16 grid cells (limits or prices), 1 band edge (70 kg), 5 row
  totals, 5 routing-table sizes ("37 rows (9 services × 4 severities)"), 3
  override counts, and 15 seeded-question IDs.

U and F are one snapshot and M another. Each is judged by the panel twice,
tool-less: with the traps at `c1c431d` (before #414) and with this branch's.

```sh
OUT=$PWD/evals/snapshots/loop
python3 evals/pilot/score_facts.py build $OUT
git worktree add /tmp/laconic-control-119 c1c431d
for s in source mutants; do
  python3 evals/bench/judge.py --results $OUT/round-119-$s.json --judge-all \
    --cases-dir /tmp/laconic-control-119/evals/pilot --jobs 2 \
    --out $OUT/round-119-$s-old-judgments.json &
  python3 evals/bench/judge.py --results $OUT/round-119-$s.json --judge-all \
    --cases-dir evals/pilot --jobs 2 \
    --out $OUT/round-119-$s-new-judgments.json &
done
wait
python3 evals/pilot/score_facts.py score $OUT
```

## The bars

1. **Sensitivity:** the new traps fail at least 24 of the 30 `simplify-*`
   mutants, and more of them than the old traps do, exact one-sided McNemar
   on the paired verdicts, alpha 0.05.
2. **Specificity:** the new traps pass at least 41 of U's 45. Every new-trap
   fail on U is read by hand. A fail the read finds to be a genuine fixture
   contradiction leaves the denominator and is reported, because the panel
   that passed it could have missed it.
3. **No leniency on real fails:** the new traps fail no fewer of F than the
   old traps do, one-sided McNemar for a fall, alpha 0.05.
4. **Coverage:** in nine U `simplify-*` responses, three per stem drawn at
   seed 119, I list by hand every claim whose truth depends on the fixture
   and mark whether the block settles it. At least 80% must be settled.

**Disclosed, deciding nothing:** the `subset-*` mutants, old against new;
the old traps' pass rate on U, which is the tool-less noise floor bar 2 is
read against; each member's fail rates in every condition;
`panel_agreement.py` on all four files; and a hand read of every mutant the
new traps pass.

**Decision.** All four bars: the traps stand and #414 closes. Bar 1 or
bar 4 fails while 2 and 3 hold: the traps stand, since they add evidence
and cost no verdict, and #414 stays open for its option 2, a read-only copy
of the fixture. Bar 2 or bar 3 fails: the twelve traps revert, and #414
stays open.

## Where the design came from

`tools/consult.sh` asked Codex, DeepSeek and Kimi about the design I was
leaning towards. Codex and DeepSeek did not answer within the timeout.

- **Kimi** proposed the F arm, since every U response is a pass and the
  mutants alone are synthetic; judging U under the old traps too, so bar 2
  is read against the tool-less noise floor rather than an absolute; near-miss
  mutants rather than wild ones; the coverage audit, its answer to my own
  worry that mutating facts I chose to state is circular; telling the judge
  an answer need not mention the facts; per-member rates; and stating which
  side of `route.py`'s docstring the code takes.
- **Not adopted:** Kimi's third mutant arm, new wording without the block,
  because the block is the only wording that changed. Its `judge.py` feature
  that inlines named fixture files at prompt time would still need the
  derived facts written somewhere, and keeping everything in the trap puts
  it under `criteria_cksum`.

## Pre-mortem, registered

I expect bar 1 to be the one at risk. A one-cent change in one cell of a
42-cell grid is the hardest error to see, and a judge comparing a pasted
grid to the block's may read the two as matching. If the round fails, I
expect it there: the new traps catch the counts (518, 813, 23) and miss
several grid cells, landing near 20 of 30. I expect the old traps to catch
the five "37 rows (9 × 4)" mutants by arithmetic and little else. Bar 2 is
the next risk, from a judge treating the block as a checklist and failing
an answer for a cell it left out.

## Results

<!-- Nothing above this line has been computed, as the preamble says. -->
