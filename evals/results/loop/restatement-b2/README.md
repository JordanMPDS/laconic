# Batch 2

The out-of-sample validation batch for `restates` ([#150], [#155]). Drawn
**after** `detector_v1.py` was frozen at `1e116ac`, which is what makes the
figures in [`../restatement.md`](../restatement.md) out-of-sample rather than a
re-score of the detector's own training data.

There is no `draw.py` here on purpose. It lived here as a byte-identical
153-line copy of [`../restatement/draw.py`](../restatement/draw.py), which is a
second thing to keep in sync for no benefit — the dedupe fix had to be
hand-copied across once already, and a copy that drifts would document a frame
that no longer matches the one this batch was drawn from.

Regenerate `key.json` and `blind.md` with:

```sh
python3 evals/results/loop/restatement/draw.py \
  --n 60 --seed 2150 --prefix S \
  --allow-duplicate-texts \
  --exclude evals/results/loop/restatement/key.json \
  --out evals/results/loop/restatement-b2
```

`--allow-duplicate-texts` is required and is not optional bookkeeping: this
batch was drawn before the frame's 19.7% text duplication was noticed, so the
raw frame is what reproduces it. Verified byte-identical. Do not use that flag
for a new draw.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
