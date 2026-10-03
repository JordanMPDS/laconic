# Round 103: does #46's design essay come back over a long design document?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 82, 91, 98, 101 and 102, which are merged. This
file, the `session-alerting-long` case and `evals/pilot/score_long.py` are
committed before any generation.

**This round proposes no rule edit.** It measures whether [#46] fires when the
session is over a design document the length of the report's, so that the next
candidate round knows whether this issue has an instrument.

`bash tools/candidate-due.sh` exited 0 at registration: [round 102](round-102.md)
carried a candidate, so round 103 may measure. `bash tools/release-due.sh`
exited 0: round 102 was rejected and released nothing.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_long.py evals/snapshots/loop/round-103.json
python3 evals/bench/release.py evals/snapshots/loop/round-103.json
```

## Why this round exists

[#46] is a field report from Opus 5 at level `full`, with ponytail 4.8.4 also
at `full`: in a working session over an internal design document, *"how would
that be built?"* got about 1,400 words in eight H2 sections. No instrument has
reproduced it on opus:

| round | instrument | opus over 600 prose words |
|---|---|--:|
| [82](round-82.md) | `drift-service` and `design-alerting` cold | 0/72 |
| [91](round-91.md) | `design-alerting` cold, #46's own prompt | 0/20 |
| [98](round-98.md) | `session-alerting`: a spec summary, three closed turns, then #46's prompt | 0/20, median 153 |
| [101](round-101.md) | the same, with ponytail's SessionStart text co-delivered | 0/20, median 149.5 |

[Round 102](round-102.md) then tested a sentence on the design bullet and
moved opus design answers by a ratio of 0.976, because there was little plan
in them to cut. Round 101 named what was still unmodelled: the report's
document itself. Every instrument above put #46's prompt over a 458-word
`SPEC.md`, and the report describes a business design document long enough
that "multiple areas" of one section talk about alerting. A longer document
gives the model more to enumerate, and the report's answer was an
enumeration: a nine-row routing table, dedup rules, an end-of-day digest and a
testing note, each traceable to a part of the spec.

## The instrument

A new pilot case, `session-alerting-long`: `session-alerting`'s five turns byte
for byte, and its trap, over a 2,578-word `SPEC.md` of the same system (5.6x
the short one). The long spec keeps every sentence the short one's turns and
trap depend on. Its section on the control loop and its pseudocode, with the
inline `alert()` under a `# pure: no I/O inside` comment, are verbatim, as are
the guardrail list and its priority order, the eight observability triggers
and the rollout sentence, under numbered headings. So turns 2 to 4 have the same one-sentence answers,
and the trap grades the same contradiction. Around them it adds what a real
design document has: background, goals and non-goals, a glossary, the
controller math with a tolerance zone and a manual override, per-guardrail
notes, a configuration table, the cycle record, failure modes, ownership
across four teams, a four-rung test ladder, rollout gates and five open
questions. Seven of its sections use the word "alert", the override and
failure-mode sections ask for the same thing without it, and a ninth trigger
(an override armed for more than four hours) joins the list. Like the short
spec, it names no monitoring system. `tests/test_evals_layout.sh` pins the
prompt and trap to `session-alerting`'s and the length ratio to at least 5.

Turn 1 stays, so the model's own summary of the long document is in context
when turn 5 arrives, as round 98 designed it. A run that skipped the summary
would change two things at once.

## Design

Master rules (`rules_cksum` 3660436060, as released in 0.3.4), arms `laconic`
and `laconic-ponytail` interleaved, opus, level `full`,
`--turn-delivery plugin`. The long case at 20 reps per arm; `session-alerting`
at 10 reps per arm as the in-pass anchor, which reproduces rounds 98 and 101
and detects a moved window. That is 2 arms x 5 turns x (20 + 10) = **300 opus
calls**, in three shards of 100 at `--concurrency 3`. Nothing is judged,
because the readout reads no verdict.

```sh
OUT=evals/snapshots/loop
common='--arms laconic,laconic-ponytail --reps 10 --cases-dir evals/pilot --turn-delivery plugin --concurrency 3'
python3 evals/bench/run.py $common --rep-offset 0 \
  --cells 'session-alerting-long:opus' --snapshot $OUT/round-103-long0.json &
python3 evals/bench/run.py $common --rep-offset 10 \
  --cells 'session-alerting-long:opus' --snapshot $OUT/round-103-long10.json &
python3 evals/bench/run.py $common --rep-offset 0 \
  --cells 'session-alerting:opus' --snapshot $OUT/round-103-short.json &
wait
python3 evals/bench/merge.py $OUT/round-103-long0.json $OUT/round-103-long10.json \
  $OUT/round-103-short.json --out $OUT/round-103.json
```

## The readout, and what it sends next

`score_long.py`, whose selftest pins every branch, applies round 98's screen,
graded turns over **600 prose words**, to the `laconic-ponytail` long cell:
both plugins over a long document, which is the report's condition.

| verdict | condition | what follows |
|---|---|---|
| fires | `laconic-ponytail` long at least 2/20, both short cells at most 1/10 | #46 has an instrument; the next candidate round may target it on this case, with an edit to laconic's own text |
| top-up | `laconic-ponytail` long exactly 1/20 | both long cells extend to 40 reps in one interleaved pass, and the bar becomes 4/40 |
| null | otherwise, both short cells at most 1/10 | #46 is recorded as not reproducing over a document of this length, and no candidate is registered on it until a new instrument fires |
| void | either short cell over 1/10 | the window moved rather than the document, and this round reads nothing |

Two labels print beside the verdict. They decide nothing:

| label | condition | what follows |
|---|---|---|
| `long-fires` | the `laconic` long cell clears the same bar | the document is enough without the second plugin, and the candidate round may drop the ponytail arm |
| `dose` | a null whose ponytail long median is at least 1.5x the ponytail short median, permutation p < 0.05 (two-sided, log prose words, seed 103) | document length scales the answer below the essay regime; the next #46 instrument is a longer document, around 8,000 words, rather than another variable |

The bar stays absolute at 600, as in rounds 98 and 101, so that every #46
instrument reports in one unit and the report's tolerance, an answer of 1,400
words, is what is tested. A longer source can justify a longer answer, which
is what `dose` discloses. Printed beside the counts, deciding nothing: each
cell's turn-1 summary median, fenced blocks and H2 median, and the Spearman
correlation between a run's turn-1 summary length and its graded turn in each
long cell. That correlation is the cheap read on whether the summary or the
document carries any length, and it is read only if the round fires.

**Pre-mortem.** The likeliest outcome is a null with `dose` absent. Opus has
gone 0 for 132 over 600 words on four instruments, and its design answers at
master are prose of about 150 to 250 words with no headings. A longer document
offers more to enumerate, but the graded prompt is the same, and round 98
found the model's own summary in context *shortened* the answer (0.62x cold).
If anything moves, I expect the long cell's median to rise by 20% to 40% while
staying far under 600, because there are nine triggers to route instead of
eight and four owners instead of none, and that would be neither a fire nor a
`dose`. A fire that arrives with H2 headings would be the report's shape; a
fire of long unheaded prose would be length without the essay structure, and
the candidate round would have to say which one it targets.

## Where the ideas came from

Keeping turn 1 rather than delivering the document at turn 5 is from Kimi,
through `tools/consult.sh`. Its argument was that dropping the summary changes
two variables at once and leaves the document arriving unlike the field
session. Keeping the bar flat with a ratio as disclosure, logging the turn-1
summary length to read the summary-versus-document question after the fact,
and writing each branch's follow-up into the registration, including an
8,000-word document after a `dose`, are also Kimi's. Codex and DeepSeek did
not answer within the timeout. Reusing round 101's two arms and running the
short case at half the reps as the anchor are this round's own choices, made
to keep the cost at 300 opus calls.

[#46]: https://github.com/JordanMPDS/laconic/issues/46

---

## Results

<!-- Nothing below this line has been computed. -->
