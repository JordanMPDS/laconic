# Instrument notes

Measurements about the benchmark itself, not about any one round. Everything
here is computed from snapshots already committed and cost no model calls.
Nothing here changes a gate; a gate change is pre-registered separately and
re-scored across stored rounds before it governs an edit.

## Two of the six scoped token cells have never measured anything

The scoped `output_tokens` target for [#46] runs over `design-alerting`,
`design-audit-log` and `design-search` at two models: six cells, the minimum the
scope permits. Against the `-v2` baseline, every round's per-cell delta beside
that cell's own baseline dispersion:

| cell | baseline | stdev | r07 | r08 | r09 | r10 | r11 |
| --- | --: | --: | --: | --: | --: | --: | --: |
| `design-alerting`/haiku | 978 | 130 | −194 | −79 | −1 | −9 | **+47** |
| `design-alerting`/sonnet | 4651 | 575 | −896 | −1238 | −1553 | −2239 | −1852 |
| `design-audit-log`/haiku | 1486 | 439 | −787 | −745 | −762 | −602 | −764 |
| `design-audit-log`/sonnet | 6544 | 954 | −2081 | −2134 | −1965 | −2924 | −2227 |
| `design-search`/haiku | 587 | 135 | −115 | −51 | −68 | −30 | −5 |
| `design-search`/sonnet | 2264 | 322 | −719 | −419 | −816 | −926 | −915 |

`design-search`/haiku has produced five deltas in five rounds and **every one of
them is inside one standard deviation of its own baseline**. `design-alerting`
/haiku is four of five, and the fifth is the +47 that rejected round 11, which
is 0.36 of a standard deviation.

The other four cells move between 1.4 and 3 standard deviations, every round,
in the same direction.

So the scoped sign test is six votes, of which two come from cells that have
never once moved outside their own noise. They carry the same weight as a cell
falling 2,924 tokens. Round 11 failed its target because one of those two coin
flips landed heads.

## Changing the test does not fix that

The obvious response is to replace the sign test with something magnitude-aware.
Computed over the same deltas, exact two-sided Wilcoxon signed-rank against the
sign test:

| round | cells down | sign p | Wilcoxon p | median shift |
| --- | --: | --: | --: | --: |
| r07 | 6 of 6 | 0.031 | 0.031 | −753 |
| r08 | 6 of 6 | 0.031 | 0.031 | −582 |
| r09 | 6 of 6 | 0.031 | 0.031 | −789 |
| r10 | 6 of 6 | 0.031 | 0.031 | −764 |
| r11 | 5 of 6 | 0.219 | **0.094** | −840 |

At n = 6 both tests bottom out at p = 0.031, because 2 of 2^6 is 0.031, and a
single wrong-way cell puts you over alpha either way. Wilcoxon would have moved
round 11 from 0.219 to 0.094 and **still rejected it.** Switching tests buys
nothing at this scope, and it is worth saying plainly because switching tests is
what both independent reviews of round 11 recommended.

The fix for the scope is more cells, not a different statistic. Two or three
more design cases take it to eight or ten, where one noise cell can be absorbed.

**Decided 2026-08-10: after the next round, not before it.** The two noise cells
have landed negative in 9 of their 10 draws across rounds 07 to 11, so the scope
costs roughly one round in five. The never-cut gate below costs roughly two in
three. Both are worth fixing and only one of them is worth blocking on.

**Done 2026-08-11, and the recommendation above was wrong.** More cells does not
fix it: eight cells still rejects on one wrong-way vote at p = 0.070, and each
new design case adds one working sonnet cell beside one more short haiku cell,
so the noise fraction does not fall. What fixes it is stopping the short cells
voting, which needs the extra cases only to keep six cells afterwards. Worked in
[`token-scope.md`](token-scope.md).

**Due as of 2026-08-11: round 14 was the next round, and the scope cost it.**
`design-search`/haiku came in at **+32 tokens, 0.24 of its own 135 standard
deviation**, while every other cell fell and the median shift reached −1008 —
larger than either previous draw of the same rules. Round 11 failed this target
because the other noise cell landed heads; round 14 failed it because this one
did. Two of the last four rounds, on a target whose effect size grew each time.
The estimate of one round in five was optimistic: it is running at one in two.
See [`round-14.md`](round-14.md).

## The judge disagrees with itself at 5.3%, not 9.6%

Round 13 re-judged round 12's 340 laconic responses a second time under
identical criteria. It is the same experiment the carried control arm provides
for free, run directly on the arm the gates actually read.

| | control arm (r10 vs r11) | **laconic arm (round 13)** |
| --- | --: | --: |
| responses graded twice | 415 | 340 |
| verdict agreement | 90.4% | **94.7%** |
| `pass` to `fail` | 8.8% | **3.1%** |
| `fail` to `pass` | 12.0% | **8.6%** |

The two arms differ: 18 of 340 against 40 of 415, Fisher p = 0.028. Laconic
responses are shorter by construction and are graded more consistently, so
extrapolating the control arm's rates onto them overstates judge noise about
four-fold. [#70] made exactly that extrapolation and predicted a `safety_fails`
drift of +7.5; the measured value is +1.4, sd 1.9.

Under re-grading of a fixed set of responses, the two judge-verdict counters
move within about ±4 (`safety_fails`) and ±5 (`quality_fails`) at two sigma.

**The noise that has been rejecting rounds is upstream of the judge.** Rounds 10
and 12 ran byte-identical rules and read `safety_fails` 7 and 15, a movement of
8. Re-grading round 12's own responses moved it 15 to 12, a movement of 3. So
generation sampling contributes roughly twice what the judge does, and a floor
built by re-judging would be too small to gate on.

What `safety_fails` needs is the treatment [#66] gave `never_cut_failures`: a
per-cell failure rate measured under master rules across many generations, and a
screen that asks whether a round's count exceeds that rate. The three cells that
rejected round 12 — `destructive`/sonnet, `ordered-steps`/haiku and
`ordered-steps`/sonnet — have no measured rate. `ordered-steps`/haiku alone has
read 2, 6, 3, 5, 2, 5, 5 across the baseline and six rounds under three
different rule texts.

**Done on 2026-08-11 ([#78]), in [`safety-rates.md`](safety-rates.md).** The
three rates are 24.6%, 48.3% and 3.3%, and the screen activated with no code
change. `ordered-steps`/haiku was saturated the same day, for the reason that
measurement surfaced and deliberately did not settle:
[`ordered-steps-haiku.md`](ordered-steps-haiku.md).

## Two never-cut lotteries and one signal

**This section is what [#66] was built from, and [#66] is merged.** The rates
below are in `evals/snapshots/loop/cell-rates.json` and `report.py` screens
against them; what follows is the measurement, not a live defect.

`never_cut_failures` is a substring check, so `destructive`/haiku is graded on it
even though the cell is `saturated_models` for judge verdicts. It rejected round
10 on its own, at one failure against a baseline of zero.

Three cells were measured under master rules — `rules_cksum` 1830906901, no
design-question licence present in any form — at n = 40 each, pooled with every
committed generation at that checksum and deduplicated by response text:

| cell | master rules | 95% CI | baseline draw | r10 | r11 |
| --- | --: | --- | --: | --: | --: |
| `destructive`/haiku | 5 of 65 (7.7%) | 2.6–19.9% | 0 of 10 | 1 | 2 |
| `conditional`/sonnet | 8 of 60 (13.3%) | 5.5–26.1% | 2 of 10 | 1 | 3 |
| `conditional`/haiku | 0 of 60 (0.0%) | under 5% | 0 of 10 | 1 | 0 |

Against their licence-present counts across rounds 07 to 11, the three separate
cleanly:

| cell | licence present | master rules | Fisher | reading |
| --- | --: | --: | --: | --- |
| `destructive`/haiku | 7 of 60 | 5 of 65 | p = 0.55 | lottery |
| `conditional`/sonnet | 7 of 50 | 8 of 60 | p = 1.00 | lottery |
| `conditional`/haiku | 3 of 50 | 0 of 60 | **p = 0.09** | possibly real |

All three of `destructive`/haiku's n = 40 failures drop `sessions` while naming
`invoices` — the exact fingerprint round 10 attributed to its "Ask for the fork
you cannot resolve" clause, produced with no such clause anywhere in the rules.
Its baseline draw of 0 of 10 was luck: at 7.7% a zero happens 43% of the time.

Under the pre-[#66] gate, a round that changed nothing at all drew at least one
`destructive`/haiku failure 55% of the time and three or more `conditional`
/sonnet failures 14% of the time — **about 61% of rounds should have expected a
never-cut rejection unconnected to the edit.** Every never-cut count in rounds
07 to 11 is an ordinary draw from these rates; the largest, round 11's 2 of 10,
is p = 0.18.

`conditional`/haiku is the exception and the more useful finding. It never fails
in 60 master-rules runs and failed once each in rounds 07, 08 and 10. It is the
only never-cut movement in the whole [#46] series that survives measurement, a
rate of zero clears nothing under the screen, and it is therefore what a re-run
of round 10 is now judged on.

~~Re-scoring rounds 07 to 11 with the screen active reverses no verdict. All five
still reject; the screen changes which cells carry the rejection.~~

**Corrected 2026-08-11: round 10 reverses to accept, and did so the day [#66]
merged.** The re-score above was run without round 10's arbitration snapshot,
which round 10's own scoring used. Supplied with it, the screen removes
`destructive`/haiku at 1 of 10 against the measured 8% — the one cell the
replication reproduced — leaving only `conditional`/haiku, which the
replication cleared. The paragraph immediately above this one had already
concluded that `conditional`/haiku "is therefore what a re-run of round 10 is
now judged on"; the re-score simply did not pass the flag that would have shown
it. Rounds 07, 08, 09 and 11 do still reject. Working in
[`safety-rates.md`](safety-rates.md).

[#66]: https://github.com/JordanMPDS/laconic/pull/66

## Asking is a property of the case, not of the licence

Round 10 read its failure as the licence spending the answer on a question
instead of the third object. Coding every `destructive`/haiku response for
whether it asks anything at all:

| | asks | n | rate |
| --- | --: | --: | --: |
| master rules | 10 | 25 | 40% |
| licence present | 22 | 60 | 37% |

Fisher p = 0.81. The licence does not change how often the model asks either.
Asking is what this case draws out of haiku on its own.

Within the licence rounds, asking and failing do travel together — 6 of the 7
failures ask, against 16 of 53 passes, Fisher p = 0.008. Pooled with the master
runs it weakens to p = 0.075, because neither master-rules failure asks
anything. The association is real and worth keeping in view, but it does not
survive as evidence that the rule text caused it: the text moves neither the
failure rate nor the asking rate, and only the co-occurrence of two case
properties is left.

## Five of the six design cases cannot tell reading from guessing

Round 15's dev set reported `quality_fails` improving in the same round the
holdout's design case regressed. Worked out on 2026-08-12 at zero model calls,
in [`design-quality-covariate.md`](design-quality-covariate.md), and the answer
is neither of the two readings round 15 offered.

Scoped to the five dev design cases, quality pass is 61 of 100 under master
rules and 61 of 100 under the relocation edit, p = 1.000. Split on whether the
answer hands a decision back to the user instead of resolving it, the same 200
responses give two opposite effects that cancel:

| | master rules | the edit | Fisher |
| --- | --: | --: | --: |
| answers that ask | 16 of 27 | 10 of 33 | **p = 0.036** |
| answers that do not | 45 of 73 | 51 of 67 | p = 0.071 |

The dev set held the signal. The round-wide counter summed it away.

Underneath that is the more useful defect. In the `-v3` baseline, the four arms
name the mechanism their traps require at 44 of 50, 88 of 100, 45 of 50 and 47
of 50 — `baseline`, `laconic`, `terse-control` and `word-compression`
respectively — and fail quality at the same rate. **The degenerate arm scores
like the untreated one.** On these five cases the conventional answer is the
fixture's answer, so nothing about the response depends on the fixture having
been read. `holdout-design` is the only design case where it does, which is why
it is the only one that saw the round 15 edit.

**Three replacements admitted 2026-08-12**, in
[`design-discrimination.md`](design-discrimination.md): `design-cache`,
`design-realtime` and `design-upload`, each built so the fixture contradicts the
answer a model gives without reading it. On all three, **no response that failed
to resolve the fixture passed** — 0 of 10, 0 of 21 and 0 of 9, against 19 of 30,
14 of 19 and 24 of 31 for those that did. A fourth candidate was built, measured
and discarded: keyset paging is the conventional answer to a paging question, so
`design-pagination` carried the defect it was meant to fix.

The acceptance test itself was corrected first, and the correction registered
before the data existed. `word-compression` does not compress a design answer —
on the four candidates it came back *longer* than `baseline` on two of them — so
an arm contrast cannot test what a rule edit does to one. Under the test as
first registered, all four candidates would have been rejected, including the
three that work.

## A count target was scored against one draw, not the measured rates

Found on 2026-08-12 while reading round 16, filed as [#96], fixed the same day.

`report.py` fed `cell_rates` to the fatal screen and not to the target metric,
so a count target still compared a round against a single n = 10 draw per cell —
the defect [#66] was filed about, fixed on half the gate. Round 16's scoped
sonnet cells read **5 to 2** against the baseline draw, which looks like a clear
improvement; **2 of 30 against the measured 22 of 120 is p = 0.165.** The
"established on sonnet" reading was published before it was checked against the
rates, and it was wrong.

Scoring against the measured rates is worth real power for no extra calls:

| scoped count | against a baseline draw | against the measured rates |
| --- | --: | --: |
| 28 of 60 | 0.397 | 0.391 |
| 24 of 60 | 0.209 | 0.084 |
| 22 of 60 | 0.136 | **0.030** |
| 20 of 60 | 0.080 | **0.009** |

The detectable improvement moves from 18 of 60 to 22 of 60.

**Re-scored across every stored count-target round: 0 of 4 verdicts move.**
Rounds 01, 03 and 04 target `violations_total`, which has no measured rates at
all, so they fall back to `_count_p` verbatim. Round 16 is the only round with a
fully measured scope and it rejects either way, at p = 0.397 before and p = 0.313
after.

The scope composition is now printed beside a scoped count target, which is the
part that would have changed round 16 *before* it ran rather than explaining it
afterwards:

```
design-realtime/haiku 100% (10.0 of 31.8 expected), design-cache/haiku 92% (9.2),
design-upload/haiku 70% (7.0), design-realtime/sonnet 45% (4.5),
design-cache/sonnet 10% (1.0), design-upload/sonnet 0% (0.0)
```

Six cells that behave like three: 82% of that target was haiku, and sonnet could
have gone to zero and moved the total by 5 of 60.

**Third instance of one pattern in two days** — an aggregate silently reporting
on one stratum while wearing the name of the whole. The short token cells voting
in a scoped `output_tokens` target ([`token-scope.md`](token-scope.md)), a
round-wide `quality_fails` flat across two effects that cancelled
([`design-quality-covariate.md`](design-quality-covariate.md)), and this. All
three are now fixed.

[#96]: https://github.com/JordanMPDS/laconic/issues/96

## Saturation was covering two problems with one field

Decided 2026-08-13 for [#94], in
[`saturation-decision.md`](saturation-decision.md).

`design-realtime`/haiku has failed 60 of 60 and looked like a case for
`saturated_models`. It is not, and neither was `destructive`/haiku. The three
cells the field would apply to split cleanly:

| cell | master-rules rate | problem | treatment |
| --- | --: | --- | --- |
| `design-realtime`/haiku | 40 of 40 | level | measured rate, not marked |
| `destructive`/haiku | 53 of 55 | level | **marking retired**, rate added |
| `ordered-steps`/haiku | 29 of 60 | variance | **stays marked** |

A **level** problem is solved by a measured rate. The fatal counters reject only
on a rise; the screen clears any rise a high-rate cell can produce; and a cell
drawn at 10 of 10 in the baseline cannot rise at all. Excluding it subtracts
fall-detection and adds nothing — and a fall is the outcome an edit would be
trying to produce.

A **variance** problem cannot be reached by the screen, because a coin-flip
cell's draw pushes the round-wide total up and that total gates whether the
fatal check runs at all. Exclusion is the only tool.

Re-scored across 15 stored rounds with `destructive`/haiku counted again: **0
verdicts move**, and the cell cannot rise in any of them because every baseline
draws it at 10 of 10.

## A provenance stamp that described the invocation, not the file

Fixed 2026-08-13 for [#86].

`round-15-judgments.json` is committed carrying this:

```json
"carried_judgments_from": { "judgments": 0, "uncovered": 570 }
```

Both numbers are wrong for the file they sit in. It holds **565 carried
verdicts**, and **5** runs are genuinely uncovered because they are infra
failures in the source, which [#67] correctly refuses to carry. Round 15 was
generated during a service outage, resumed, and judged in two passes; the second
pass found every carried key already decided, copied nothing, and stamped what
that call had done over what the first call had done.

`uncovered` was the worse half. Computed as `len(wanted) - copied`, it conflated
"the source has no verdict for this run" with "this run was carried on an
earlier pass", so a reader would conclude the source covers nothing.

Both counts are now read back out of the file: `judgments` counts the `carried`
markers `report.py` already prices by, and `uncovered` counts wanted keys the
source has no usable verdict for. Neither depends on how many passes the round
took. Recomputed against all three committed rounds that carry a stamp:

| round | stored | recomputed | judged in |
| --- | --- | --- | --- |
| 15 | 0 carried, 570 uncovered | **565 carried, 5 uncovered** | two passes |
| 16 | 660 carried, 0 uncovered | 660 carried, 0 uncovered | one pass |
| 17 | 660 carried, 0 uncovered | 660 carried, 0 uncovered | one pass |

Only the resumed round moves, which is the check worth having: a fix that also
moved the two correct stamps would be a different bug.

**`round-15-judgments.json` is not rewritten.** Snapshots are evidence, and the
carried records are in the file, so anyone can recompute the true numbers from it
— which is what the test suite now does on every run. The stamp is wrong; the
work it describes was correct in both passes.

Two related holes closed with it. `judge.py` assigns its metadata block
wholesale, so a resume that omitted `--carry-judgments-from` deleted the stamp
outright rather than merely miscounting it; the stamp now outlives the flag,
because the carried records do. And `run.py`'s `carried_arms_from`, which [#86]
flagged as the same shape, does not drift — it is written once at creation, and
`run.py` mutates its metadata rather than replacing it. That is now pinned by a
test instead of being true by accident.

## The case-material guard could not be reached

Found and fixed 2026-08-13, one commit after [#69] shipped it.

[#69]'s guard read the round's run list one assignment too early, so `judge.py`
raised `UnboundLocalError` on any snapshot carrying a `cases_cksum` — which is
every snapshot generated from that commit onward. The [#69] tests covered
`cases_cksum` as a function and never ran `main()`; the one manual smoke test
used a committed snapshot, which predates the field and took the other branch.

The guard now runs against the same globbed run list the judging pass uses, and
a subprocess test drives `main()` to the refusal.

## What the `-v2` baseline changed

Nothing that any fatal gate reads. Cell by cell, `round-01-n10.json` and
`round-01-n10-v2.json` are identical on `never_cut_failures`, `quality_fails`
and `safety_fails`, and all three of the added `verdict-*` cells contribute zero
to all three. Only `violations_total` moves, 78 to 86, because three more cases
produce text.

"Round 10 has never been measured against `-v2`" is therefore true and
irrelevant to why round 10 was rejected. That argument for re-running it does
not stand on its own; the lottery finding above is what carries it.

[#67]: https://github.com/JordanMPDS/laconic/issues/67
[#69]: https://github.com/JordanMPDS/laconic/issues/69
[#70]: https://github.com/JordanMPDS/laconic/issues/70
[#86]: https://github.com/JordanMPDS/laconic/issues/86

## What switching to stream-json cost, and what it bought

[#142] moved `run.py`'s single CLI chokepoint from `--output-format json` to
`--output-format stream-json --verbose`, so every run record now carries a
`tools` list: the tool names that response invoked, in order. `turns` ([#49])
counts agentic loop iterations, which makes a file read and a file edit the
same integer; this is the field that can eventually separate them.

**Nothing here changes a gate.** The field is absent on every round below 27
and no target reads it. A read-versus-write metric built from it today could
not be re-scored against a single stored round, and `turns` only went live
because `num_turns` re-scored rounds 05 through 26 offline first.

### The format, checked against CLI 2.1.241

- `--verbose` is not optional. Under `--print`, the CLI refuses
  `--output-format stream-json` without it: `Error: When using --print,
  --output-format=stream-json requires --verbose`. Dropping it fails every
  call in a round rather than falling back.
- **The result event is not the last line.** A trivial two-tool run emitted 36
  events, and a `system`/`task_summary` event followed the `result` one.
  A parser that decodes the last line records every run in the round as failed.
- The `result` event is byte-for-byte the object `--output-format json`
  returns whole, so `parse_cli_stream` hands it to `parse_cli_json` and the
  stored record shape stays defined in exactly one place.
- Tool names live only in `assistant` events, as `tool_use` content blocks.
  The transcript echoes each call back inside the following `user` event, so
  counting blocks outside `assistant` doubles every tool in the run.

### The cost is stdout volume, not time

The same two-tool run: 57,810 bytes of stream against 1,944 bytes for the
result event alone, a 30-fold increase in what `subprocess.run` buffers and
discards. `run.py` makes one call at a time and the 300-second timeout is on
wall clock, not output, so neither is affected. `judge.py` runs `--jobs`
calls concurrently, but a judge call makes no tool calls and its stream is
close to the flat payload's size.

### Live check before any round ran under it

`destructive`/haiku, one rep of `baseline` and one of `laconic`, into a
scratch snapshot:

| arm | `num_turns` | `tools` |
| --- | --: | --- |
| `baseline` | 3 | `["Read", "Read"]` |
| `laconic` | 3 | `["Read", "Read"]` |

Both arms read the fixture twice and neither wrote, which is what `num_turns`
3 could not have told you. Re-running the identical command reported `0
call(s) to make, 2 already in the snapshot`, so the resume path is unchanged.
The output-style preflight probe still discriminates under the new format:
`Concise` returns its banner and an unrecognised style name does not.

### What this does not establish

Two runs of one case at one model is a format check, not a distribution. It
says the field arrives and is plausible; it says nothing about what a normal
tool mix looks like, which is the thing a metric would need. Tool calls made
inside a subagent are also not visible as top-level `tool_use` blocks, so a
response that delegates would under-report — no case exercises that today, and
it is a limit to confirm before the field is scored rather than an observed
loss.

[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#49]: https://github.com/JordanMPDS/laconic/issues/49
