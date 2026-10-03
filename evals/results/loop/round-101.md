# Round 101: does #46's design essay come back with ponytail co-active, on opus?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 82, 91 and 98, which are merged. This file, the
`laconic-ponytail` arm, its vendored text and `evals/pilot/score_ponytail.py`
are committed before any generation.

**This round proposes no rule edit.** It measures whether [#46] fires once the
second plugin from the report is in the session, so that the next candidate
round knows whether this issue has an instrument.

`bash tools/candidate-due.sh` exited 0 at registration: [round 100](round-100.md)
carried a candidate, so round 101 may measure. `bash tools/release-due.sh`
exited 0: round 100 was rejected and released nothing.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_ponytail.py evals/snapshots/loop/round-101.json
python3 evals/bench/release.py evals/snapshots/loop/round-101.json
```

## Why this round exists

[#46] is a field report from Opus 5 at level `full`: in a working session over
a design document, *"how would that be built?"* got about 1,400 words in eight
H2 sections, with an invented schema the model called never-cut content. No
instrument has reproduced it on opus:

| round | instrument | opus laconic over 600 prose words |
|---|---|--:|
| [82](round-82.md) | `drift-service` and `design-alerting` cold | 0/72 |
| [91](round-91.md) | `design-alerting` cold, #46's own prompt | 0/20 |
| [98](round-98.md) | `session-alerting`: a spec summary, three closed turns, then #46's prompt | 0/20, median 153 |

Round 98's pre-mortem named the one condition of the report that none of these
modelled: **ponytail 4.8.4 was co-active at `full`**. Its SessionStart text
carries two lines that bear on exactly this failure. *"Explanation the user
explicitly asked for (a report, a walkthrough, per-phase notes) is not debt,
give it in full"* is a second licence for a long answer to a "how" question,
beside laconic's own never-cut bullet that the report's thinking quoted. And
*"Code first"* is a plausible source of the invented schema.

## The instrument

A new benchmark-only arm, `laconic-ponytail`: the live laconic `full` slice, a
blank line, and ponytail's `full` SessionStart text, vendored unedited into
`evals/arms/vendor/ponytail-full.md` with its MIT licence beside it. It is
composed in `run.py` at runtime, so it differs from `laconic` in the second
plugin's text and nothing else, and `tests/test_bench.py` checks that by exact
equality. The text was taken from ponytail 4.9.0; its `SKILL.md`, instruction
builder and activate hook are byte-identical to the 4.8.4 release commit, so
it is the text the report ran under. Laconic comes first, as it does in the
SessionStart output of this machine's own sessions; a real session's order
follows plugin load order, so that is a pinned choice.

Under `--turn-delivery plugin` both texts arrive on turn 1 only, and later
turns get laconic's one-line reminder. Ponytail's UserPromptSubmit hook emits
nothing, so that is what a real co-active session receives. `rules_cksum`
covers only the laconic slice, so a resume compares the composed arm against
the text the snapshot was started with and refuses a change.

The cells are round 98's, unchanged: `session-alerting` (the five-turn
session) and `design-alerting` (the same fifth prompt, cold).

## Design

Master rules (`rules_cksum` 3660436060, as released in 0.3.4), arms `laconic`
and `laconic-ponytail` interleaved in one pass, opus, level `full`,
`--turn-delivery plugin`, 20 reps, four shards by `--rep-offset` at
`--concurrency 4`. That is 2 arms x (100 session turn calls + 20 cold calls) =
240 opus calls. Nothing is judged, because the readout reads no verdict.

```sh
for off in 0 5 10 15; do
  python3 evals/bench/run.py --arms laconic,laconic-ponytail --reps 5 \
    --rep-offset $off --cases-dir evals/pilot \
    --cells 'session-alerting:opus,design-alerting:opus' \
    --turn-delivery plugin --concurrency 4 \
    --snapshot evals/snapshots/loop/round-101-shard$off.json &
done
wait
python3 evals/bench/merge.py evals/snapshots/loop/round-101-shard{0,5,10,15}.json \
  --out evals/snapshots/loop/round-101.json
```

## The readout, and what it sends next

`score_ponytail.py`, whose selftest pins every branch, applies round 98's
screen, graded turns over **600 prose words**, to the ponytail arm's session
cell. The two `laconic` cells are the in-pass control.

| verdict | condition | what follows |
|---|---|---|
| fires | `laconic-ponytail` session at least 2/20, both `laconic` cells at most 1/20 | #46 has an instrument; the next candidate round may target it on this arm, with an edit to laconic's own text |
| top-up | `laconic-ponytail` session exactly 1/20 | all four cells extend to 40 reps in one interleaved pass, and the bar becomes 4/40 |
| null | otherwise, `laconic` cells at most 1/20 | #46 is recorded as not reproducing with both plugins' texts in context, and no candidate is registered on it until a new instrument fires |
| void | either `laconic` cell over 1/20 (2/40 after a top-up) | the window moved rather than the second plugin, and this round reads nothing |

Three labels print beside the verdict. They decide nothing, and are fixed here
so that what each sends next is not chosen after the numbers:

| label | condition | what follows |
|---|---|---|
| `cold-fires` | the ponytail cold cell clears the same bar | the SessionStart text alone suffices; a later round may drop the five-turn scaffold |
| `smoldering` | a null whose ponytail session median is at least 1.5x laconic's at permutation p < 0.05 (two-sided, log prose words, seed 101) | not a clean null: the interaction exists below the essay regime, and the next #46 instrument should pull harder rather than re-run this one |
| `code-balloon` | at least 5/20 ponytail session graded turns carry a fenced block, with laconic's at most 1/20 | the length went into code the prose screen cannot see; filed as its own issue rather than read as #46 firing, since #46 is essay-shaped |

The bar stays absolute rather than relative to the laconic arm, because the
report's failure is an essay regime (1,400 words, eight sections) and not an
inflation; the ratio is the `smoldering` disclosure. Per-cell H2 medians are
printed beside the counts.

**Pre-mortem.** The likeliest outcome is a null with no label: opus has gone
0 for 112 over 600 words on three instruments, and ponytail's own text says it
"governs what you build, not how you talk", which opus may read as leaving
prose to laconic. If it fires, it fires through the licence line rather than
through code, and the session cell should carry H2 sections the control never
has. A fire whose control also reads over 1/20 would be the window, not the
plugin, and is the void row.

## Where the ideas came from

Keeping the absolute 600-word bar, keeping the cold cell in the ponytail arm,
and pre-specifying the ratio statistic are from both DeepSeek and Kimi through
`tools/consult.sh`. The resume guard on the vendored text is DeepSeek's, from
noticing that `rules_cksum` cannot see it. The `smoldering` and `code-balloon`
labels and the pre-written follow-ups are Kimi's, as is checking the 4.8.4 text
against 4.9.0. Codex did not answer within its timeout.

[#46]: https://github.com/JordanMPDS/laconic/issues/46

---

## Results

<!-- Nothing below this line has been computed. -->

## Result: null, with no label

**#46 does not fire with ponytail co-active, on opus.** 80 runs, 0 failed, CLI
2.1.288 throughout (`release.py`: one release, no unreadable span),
`rules_cksum` 3660436060, `cases_cksum` 3426733662, `--turn-delivery plugin`,
level `full`. `merge.py` reconstructs 4 in flight against the declared 4. The
merged snapshot records the `laconic-ponytail` arm as 2,115 words against
`laconic`'s 1,239, with ponytail's header present, so the second text was
delivered.

```
laconic          session-alerting n=20  median  156.0  max   214  over 600:  0  fenced  0  H2 median 0.0
laconic          design-alerting  n=20  median  240.5  max   279  over 600:  0  fenced  0  H2 median 0.0
laconic-ponytail session-alerting n=20  median  149.5  max   190  over 600:  0  fenced  0  H2 median 0.0
laconic-ponytail design-alerting  n=20  median  251.5  max   299  over 600:  0  fenced  0  H2 median 0.0

session median ratio ponytail/laconic 0.958, permutation p 0.1839 (two-sided, log prose words, seed 101)
ponytail session over 600: 0/20 against a bar of 2: NULL
```

No label printed. The cold cell did not clear the bar, the session ratio is
under 1 rather than at 1.5, and none of the 80 answers carried a fenced block
or an H2 heading, so "Code first" moved nothing into code either. The control
reproduces round 98 closely (session median 156.0 against 153, cold 240.5
against 242.5), which is the void row's other purpose: the window did not move.

The pre-mortem's likeliest outcome is what happened. Ponytail's licence for
requested explanation did not reach the design answer; its own closing line,
that it "governs what you build, not how you talk", is the plausible reason,
and this round cannot separate that from opus not reading *"how would that be
built?"* as a requested explanation at all.

### What this sends next

The null row applies. #46 has now been read on four instruments on opus
(rounds 82, 91, 98 and 101) and none fires, including the one carrying both
plugins from the report. No candidate is registered on #46 until a new
instrument fires; what this round leaves unmodelled is the report's own
document, which was far longer than `SPEC.md`'s 458 words, and its earlier
turns, which the report describes only as having gone well.

`bash tools/candidate-due.sh` now exits 1, so round 102 carries a rule edit.
The four shard files were merged and are not committed; `metadata.shards` in
the merged snapshot records them.
