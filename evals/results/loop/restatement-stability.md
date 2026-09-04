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

## Result

_To be filled in by the pass._

[#155]: https://github.com/JordanMPDS/laconic/issues/155
