# The judge panel, validated before it became the default

Since 2026-09-24 every judgment is a panel's: sonnet, opus and kimi (the Kimi
Code subscription, `kimi-code/kimi-for-coding`) grade each response blind, and
the record's `verdict` is their majority. Before it replaced the single sonnet
judge, the panel re-graded a sample that sonnet had already graded, under the
same criteria (`criteria_cksum` 5539815).

**The sample.** 90 runs from `round-73-wide-control.json`: 45 that sonnet had
failed and 45 it had passed, drawn with seed 80. The sample is half fails by
construction, so the flip counts below overstate what a round-wide file would
show.

| member | agrees with the majority | kappa | no vote |
|---|--:|--:|--:|
| sonnet | 83/90 | 0.844 | 0 |
| opus | 88/90 | 0.955 | 0 |
| kimi | 84/90 | 0.864 | 0 |

| pair | agree | kappa |
|---|--:|--:|
| sonnet, opus | 81/90 | 0.800 |
| sonnet, kimi | 77/90 | 0.710 |
| opus, kimi | 82/90 | 0.820 |

- **Every judgment was decided.** No member failed a call or returned
  something that did not parse, and no judgment split three ways.
- **Sonnet is the member furthest from the majority.** Re-graded here, it
  matched its own earlier verdict on 83 of 90, the 5 to 10% self-disagreement
  [`judge-self-disagreement.md`](judge-self-disagreement.md) measured.
- **The panel moved 10 of 90 of sonnet's verdicts:** 7 fails to passes and 3
  passes to fails. On this sample, a single sonnet judge fails more than the
  majority does.

It took 16 minutes at `--jobs 4`, about 11 seconds a judgment, and 270 calls.

Reproduce:

```sh
python3 evals/bench/judge.py --results evals/results/loop/judge-panel/sample.json \
  --out evals/results/loop/judge-panel/sample-judgments.json --judge-all --jobs 4
python3 evals/bench/panel_agreement.py evals/results/loop/judge-panel/sample-judgments.json \
  evals/snapshots/loop/round-73-wide-control-judgments.json
```
