# Round 32: an instrument for the closed-confirmation shape

**This round proposes no rule edit.** It builds three cases and reports whether
they reproduce the failure they were built for. The answer determines what the
over-length cluster's next round can be, and a negative answer is the useful
outcome as much as a positive one.

## Why an instrument round

Six issues report over-long answers at `full`: [#46], [#60], [#113], [#136],
[#150] and [#116]. They describe one shape — **a short question about a large
subject, where the subject's size sets the answer's size and the question's
size has no effect** — reached by four different triggers:

| Issue | Trigger | Example | Reported | Instrument before this round |
|---|---|---|--:|---|
| [#46] | implementation | "how would that be built?" | ~1,400 w | `design-*`, 8 cases |
| [#60] | evaluative | "is this sound?" | ~650 w | `verdict-*`, 3 cases |
| [#113] | feasibility | "could we test this on X?" | ~600 w | none |
| [#136] | closed confirmation | "you said X, correct?" | ~400 w | none |
| [#150] | redundancy inside requested content | — | — | none |
| [#116] | volunteered *work*, not prose | — | — | none |

Two of the six were already instrumented, and one of those has been run.
Round 29 took [#150]'s edit against `walkthrough` plus the three `verdict-*`
cases and returned a flat null — 3 of 7 voting cells, sign test p = 1.000, five
of eight cells moving the wrong way — and concluded that **the next move on
[#150] is a metric, not another rule edit**. This round takes that conclusion
at its word and buys no edit.

Of the four uninstrumented issues, three are blocked on machinery that does not
exist, and this round does not fake them:

- **[#136] and [#60]'s drift hypothesis need more than one conversational
  turn.** `run.py` sends one `claude -p` per record from a fresh
  `tempfile.mkdtemp()` that is deleted immediately after, never lifts
  `session_id` off the result event, and keys a run on
  `(case, arm, model, rep)` with a single `text`. There is no slot for a second
  answer. This is a real limit, not an oversight, and working around it is a
  harness change rather than a case.
- **[#150] needs a redundancy metric.** Nothing under `evals/bench/` measures
  repeated claims; [#155]'s restatement detector is parked outside the harness
  at 55.3% out-of-sample precision and is not a scoreable `--target`.
- **[#116] needs the tool list scored.** `parse_cli_stream` has recorded
  `tools` since [#142], but it is absent on every round below 27, so a gate
  built on it today would have no measured null.

That leaves **[#136]'s closed-confirmation shape**, which is the one thing that
can be approximated now. [#113] is deliberately left alone: its own issue asks
that feasibility wait on whatever lands for [#46] and [#60] rather than being
fixed separately.

## What the three cases are

Every one of the 22 existing prompts asks an open-ended question. The shape
[#136] reports — a **closed** question whose correct answer is a single line —
was not represented at all. Each new case states a conclusion in a fixture and
asks the model to confirm it:

| Case | Fixture | Prompt | Correct answer |
|---|---|---|---|
| `confirm-metric` | `ANALYSIS.md`, an experiment readout | "you concluded lift is the wrong metric for this experiment, correct?" | Yes — and the absolute difference is not a safe substitute, because the sample cannot resolve the effect either way |
| `confirm-index` | `FINDINGS.md`, a slow-query investigation | "so the fix is adding the index on created_at, correct?" | No — the predicate wraps `created_at` in `date_trunc`, so a btree on the bare column is not a candidate |
| `confirm-rollback` | `INCIDENT.md`, a postmortem | "the config change was the cause, correct?" | Yes — but reverting it could not restore service, because migration `0042` had already added a `NOT NULL` column the old path does not write |

Three design constraints, each load-bearing:

1. **Each carries a qualification the question does not ask for but the fixture
   attaches.** A bare "yes" is wrong. This is what keeps the case gradeable on
   correctness, so the judge is never asked to rule on how much was said.
2. **`grading` is `quality`, and the traps state no vocabulary of form.**
   `tests/test_evals_layout.sh` rejects a `quality` trap containing `terse`,
   `length`, `verbose` and the rest of that list, because a criterion reaching
   for any of it grades how the answer was written rather than whether it was
   right. The length claim is carried by `output_tokens`, a mechanical count,
   never by a verdict. Optimizing against a case that grades adherence to the
   rules would be circular, and the layout suite enforces the boundary.
3. **One of the three answers "no".** `confirm-index` is a closed question whose
   honest answer is a correction. A family of three cases that all confirm would
   measure agreeableness as much as scope.

With the three `verdict-*` cases these give a **six-cell sonnet scope**, which
is the minimum a two-sided exact sign test can reach alpha on — 6 of 6 is
p = 0.031, and a scope of four cells is p = 0.125 and can never reach it.

## The question this round asks

> Do the three `confirm-*` cases reproduce the over-length failure [#136]
> reports — roughly 400 words to an eight-word closed question — under the
> single-turn harness?

**Disclosure: this question was written after a six-call smoke test at one rep,
not before it.** The staging rule exists to kill a bad buy cheaply, and it was
used as intended, but that means the prediction below is informed by data and
is not a registration. It is recorded here as an informed expectation so the
n = 5 result can contradict it on the record.

**Expectation after the smoke test:** the shape does not reproduce. All six
smoke-test responses read the fixture, answered correctly, and carried the
qualification, in 73 to 148 words across both arms — nowhere near the reported
400. If that holds at five reps, the mechanism is the one the harness survey
predicts: **[#136]'s pull comes from the model re-justifying a claim it made
itself, and a fixture read cold creates no such ownership.** A document the
model has just read is evidence to cite, not a position to defend.

**What would falsify it:** median words on the laconic arm at or above roughly
250 on any of the three cases, or a spread wide enough that some reps balloon
while others do not — which would make these cases a variance instrument even
if the median is well behaved.

## Results

Five reps a side, sonnet, `baseline` and `laconic` interleaved in one `run.py`
invocation. 30 generations, 0 failed; 30 judge calls, 0 failed.

### The shape does not reproduce

| Case | Arm | Median words | Min | Max | Median `output_tokens` | Read the fixture |
|---|---|--:|--:|--:|--:|--:|
| `confirm-index` | baseline | 130 | 129 | 181 | 522 | 5/5 |
| `confirm-index` | laconic | **106** | 91 | 121 | 429 | 5/5 |
| `confirm-metric` | baseline | 144 | 115 | 170 | 600 | 5/5 |
| `confirm-metric` | laconic | **80** | 63 | 124 | 364 | 5/5 |
| `confirm-rollback` | baseline | 149 | 147 | 167 | 514 | 5/5 |
| `confirm-rollback` | laconic | **87** | 73 | 91 | 266 | 5/5 |

[#136] reports roughly 400 words to an eight-word closed question. **The widest
response the laconic arm produced across all 15 runs is 124 words**, and the
median sits at 80 to 106. The failure is absent at the median and absent in the
tail. The falsifier recorded above — a median at or above about 250, or a spread
in which some reps balloon — did not occur on any of the three cases.

Laconic is doing its job on these cases rather than failing at it: it compresses
on 3 of 3 against its own interleaved control, by −18.5%, −44.4% and −41.6%.

**Reading held at 5/5 on every cell in both arms**, so no cell is refused for a
[#131] stratum crossing and no part of the compression was bought by not opening
the file. That is the property round 29 selected its scope for, and these cases
have it too.

### The traps grade, and they grade near the ceiling

29 of 30 judgments pass: baseline 15/15, laconic 14/15. The one failure is
`confirm-metric`/laconic rep 3, and the judge's reason is coherent — the
response led with "the finding is broader than that" and reframed the
conclusion as being about sample size, rather than confirming the premise and
then qualifying it. That is a defensible borderline call on a response whose
substance was right, and it is worth recording that the trap's "confirms" is
doing real work at the margin.

The consequence for the instrument is the important part. **A cell drawn at 5/5
cannot rise**, so these three cells detect a fall in answer quality and not a
regression into failure. That is the [#94] distinction: this is a level, not a
variance problem, and if these cells are ever wanted as rise-detectors they need
a measured rate in `cell-rates.json` rather than a saturation marking.

### What this establishes

**The closed-confirmation shape does not reproduce single-turn, and the reason
is mechanical rather than incidental.** [#136]'s own account locates the pull
precisely: the model re-derived an argument *it had made itself*, to a person
quoting it back. Its closing line is "those come apart hardest when the model
has a lot of recent context it is proud of." A fixture the model has just read
cold produces no such ownership — it is evidence to cite, not a position to
defend. The harness cannot construct ownership, because it sends one
`claude -p` per record from a scratch directory it deletes immediately after.

So [#136] joins [#60]'s drift hypothesis, [#150] and [#116] as **blocked on
machinery rather than on rule wording**. Four of the cluster's six issues are
now in that state, and round 29 has already shown what happens when the cluster
is attacked by wording instead: a flat null at p = 1.000, with the round's own
conclusion being that the next move is a metric.

**The over-length cluster's next round should be harness work, not a rule
edit.** Filed as [#166].

### What the three cases are worth anyway

They are not wasted, and they are not being kept out of sentiment:

- They are the only closed-question cases in the set, and they are **exercised**
  — 30 of 30 read the fixture, 30 of 30 produced a gradeable answer, 0
  NOT EXERCISED.
- Variance is tight. The laconic arm spans 63 to 124 words across 15 runs, so a
  future edit that inflates answers on a closed question would be visible
  against a narrow band.
- With the three `verdict-*` cases they give the six-cell sonnet scope a scoped
  `output_tokens` target needs, and unlike round 29's scope every cell reads the
  fixture 5 of 5, which is what refused two of round 29's cells.

They enter the repository as a regression detector with a measured baseline,
which is what they are, and not as an instrument for [#136], which they are not.

## Snapshots

- `evals/snapshots/loop/round-32-pilot.json` — `baseline` and `laconic`,
  sonnet, `confirm-*`, 5 reps, one sequential process
  (`metadata.concurrency_declared` = 1). 30 runs, 0 failed.

  **Two generator ids, one declared process, and both are correct.** The round
  was staged: one `run.py` at `--reps 1` to catch a structural error for six
  calls, then a second at `--reps 5` that resumed by key and bought only the
  24 new ones. `concurrency.py` gates on reconstructed simultaneity rather than
  on the number of ids, and reads `max_in_flight` = 1 at a summed-to-wall ratio
  of 0.41, so the sequential declaration is the accurate one — declaring 2 would
  assert an overlap that did not happen. `metadata.reps` was corrected by hand
  from 1 to 5, since `new_snapshot` sets that field once at creation and the
  file would otherwise be read as n = 1.
- `evals/snapshots/loop/round-32-pilot-judgments.json` — 30 judgments, 0 failed.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#166]: https://github.com/JordanMPDS/laconic/issues/166
[#94]: https://github.com/JordanMPDS/laconic/issues/94
