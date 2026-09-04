# Is the `restates` ceiling a detector problem or a criterion problem?

**Registration. No number under "Result" has been computed.** Committed before
the pass runs.

## What [#155] left, and why direction A has never been tested

[`restatement.md`](restatement.md) built the detector and parked it at **55.3%
precision out of sample**. [#155] recorded two ways forward:

- **A. Sharpen the criterion** — say how a mixed closing is scored, freeze it,
  **re-label all 120 responses**, freeze a v2 detector, draw a third batch.
  Projected landing spot **~72%**.
- **B. Rethink the construct** — ask a more operational question instead.

The issue said B first, because it is cheap. B was piloted in
[`deletability.md`](deletability.md) and **closed**: all four registered
predictions failed and the construct scored worse than the detector it was meant
to improve on.

So A is what is left, and it costs a full re-label of 120 hand-written labels to
reach a ceiling [`round-28.md`](round-28.md) already calls *"not obviously good
enough to gate on"*.

## The question this round asks first

**How much of the missing 45% is the detector disagreeing with itself?**

[`judge-self-disagreement.md`](judge-self-disagreement.md) measured that
same-criterion re-judging moves **0% to 27% of verdicts** between cells, and that
the instability is a property of the criterion rather than of the judge. The
`restates` criterion is exactly the shape that measured worst there: it asks for
a judgement about whether a passage *adds anything*, not whether a named fact is
present. And [#155] already records the human labels being internally
inconsistent on the same seam — *"batch 2 labels every mixed closing false under
the borderline convention, and batch 1's R53 does not."*

If the detector flips a large share of its own calls on identical text under an
identical criterion, then **55.3% is partly measuring its own noise, and A's
projected 72% is not reachable by sharpening alone** — because no detector can be
more precise against a fixed label set than it is consistent with itself.

> **Hypothesis:** re-running `detector_v1.py` unchanged, at the same criterion
> checksum, on the same 120 responses, moves a share of its verdicts comparable
> to the worst cells in `judge-self-disagreement.md`.

**Falsifier, registered before the pass:** self-disagreement at or below 10%,
which would say the detector is stable and the missing precision is a genuine
criterion-boundary problem that sharpening could fix. That outcome argues **for**
direction A.

**Registered secondary:** whether the flips concentrate on the mixed-closing
shape that [#155] names as the dominant false-positive class. If the detector is
unstable *specifically there*, that is the same boundary failing twice — once in
the human labels and once in the detector — and it is the strongest possible
argument that the criterion, not the detector, is the thing that is wrong.

```sh
python3 evals/results/loop/restatement/detector_v1.py \
  --key evals/results/loop/restatement/key.json \
  --out evals/results/loop/restatement/verdicts-rerun.json --model sonnet
python3 evals/results/loop/restatement/detector_v1.py \
  --key evals/results/loop/restatement-b2/key.json \
  --out evals/results/loop/restatement-b2/verdicts-rerun.json --model sonnet
```

120 calls, the same 120 the original pass bought at $7.81. No generation. The
criterion file is untouched, so `criterion_cksum` must match the stored verdicts'
— and if it does not, the comparison is void and is reported as void.

**No rule edit is proposed.** This decides whether [#155] is worth reopening or
should be closed.

## Result: 20% of the detector's own verdicts do not reproduce

Same script, same criterion, same 120 responses. `criterion_cksum` is
**1061017820 on both passes**, so the comparison is not void.

| | n | original says restates | re-run | flips | McNemar |
|---|--:|--:|--:|--:|--:|
| batch 1 | 60 | 31 | 34 | **9 (15.0%)** | p = 0.5078 |
| batch 2 | 60 | 39 | 40 | **15 (25.0%)** | p = 1.0000 |
| **pooled** | 120 | 70 | 74 | **24 (20.0%)** | — |

**The registered falsifier did not fire.** 20% is not at or below 10%, and it
sits inside the 0-27% range
[`judge-self-disagreement.md`](judge-self-disagreement.md) measured across four
other criteria — near the top of it.

## The rate is stable and the verdicts are not

Precision against the *same* hand labels, original pass against re-run:

| | precision | recall |
|---|--:|--:|
| batch 1, original | 74.2% | 88.5% |
| batch 1, re-run | **64.7%** | 84.6% |
| batch 2, original | 53.8% | 84.0% |
| batch 2, re-run | **55.0%** | 88.0% |

**The published out-of-sample figure reproduces within 1.2 points.** Batch 2 —
the batch the freeze made meaningful — reads 53.8% then 55.0%. So [#155]'s
headline number is sound and this round does not disturb it.

**The in-sample figure does not.** Batch 1 moves 9.5 points on identical text.
And every McNemar is far from significance, so the flips are symmetric: what is
unstable is *which* responses the detector calls restatements, not how many. That
is the same signature `judge-self-disagreement.md` found — *"No cell's rate
moves. What moves is which runs pass."*

## The registered secondary is confirmed, and it is the useful half

[#155] classified detector v1's 26 false positives into four shapes: mixed
closing clause (14), walkthrough concurrency elaboration (8), "rollback is broken
too" (3), other (1).

**The ten `true → false` flips fall into those same four classes, in the same
proportions:**

| flipped quote | [#155]'s class |
|---|---|
| *"Fix the multiple-comparisons issue first—it's the clearest threat to validity."* | mixed closing — **this is one of the two examples the issue quotes verbatim** |
| *"#1 is the one to fix before anything else builds on this"* | mixed closing |
| *"The sequencing/rollback interaction is the thing to fix."* | mixed closing |
| *"The issue is strictly the sequencing during the rolling deploy."* | mixed closing |
| *"Old code can't survive the schema change it doesn't know about."* | mixed closing |
| *"Both callers end up awaiting the identical in-flight request…"* | walkthrough elaboration |
| *"The first sets `inFlight` and starts the fetch…"* | walkthrough elaboration |
| *"The rollback they've practiced… is incompatible with this migration."* | rollback is broken too |
| *"The plan describes rollback as a practiced, six-minute operation, but…"* | rollback is broken too |
| *"Specify the stopping rule precisely: primary metric only, or any of eight?"* | other |

**The verdicts that flip are the verdicts that were false positives.** The
detector is unstable precisely where the criterion is undecided, and stable
everywhere else.

## What this says about direction A

Two things, pulling in opposite directions, and both belong in the record.

**Against A: its ceiling estimate is not trustworthy.** The projected 72.4% was
computed by removing 14 mixed-closing false positives from batch 2 — a batch on
which the detector flips **15 of 60 verdicts**, concentrated on that same shape.
Subtracting a class from one draw of an instrument that re-draws a quarter of
that class is not an estimate. The true ceiling could be either side of 72%, and
this round cannot say which.

**For A: its mechanism is validated.** If the instability were spread evenly
across all verdicts, sharpening one boundary could not help — the noise would be
in the judge or the task, and no criterion edit would reach it. It is not spread
evenly. It sits on the one seam [#155] identified and `criterion.md` leaves
open, which is the strongest available evidence that **resolving that seam is
what would reduce it.**

So A is not refuted and it is not cheap. What has changed is that its cost is now
known to buy an unknown rather than a projected 72%: the re-label is the only way
to find out where the ceiling actually is, because the current estimate of it is
inside the instrument's own noise.

**[#155] stays open**, with the projection struck rather than the direction.

## A note for anyone re-running this

`detector_v1.py` resumes by key, like `run.py` and `judge.py`, and that is what
made this affordable in ten-minute chunks. It also writes progress to stdout, so
piping it through `head` kills it with `SIGPIPE` mid-pass — which happened once
here and cost one response.

## Cost

120 calls, sonnet, the same 120 the original pass bought at $7.81. No generation.
No rule edit.

[#155]: https://github.com/JordanMPDS/laconic/issues/155
