# Loop round 05 — rejected

The first round to target `output_tokens`, aimed at the compression collapse on
the cases the never-cut section protects. It rejects on two fatal gates and the
target itself, and the edit is reverted. The mechanism it predicted did fire —
in exactly one of the eight cells it named.

## Hypothesis

Written before the round was generated, in `c9fc171`:

> Stating in the never-cut section that protection covers claims, not volume —
> "Protected means the claims stay, not that the level stops", with the level's
> cuts named as still applying inside a walkthrough, a failure report, or a
> numbered procedure — and rephrasing "gets full detail" to "gets every claim
> it needs" in the length-scales paragraph, should move `output_tokens`
> downward round-wide, with the largest drops on `walkthrough`, `badnews`,
> `ordered-steps`, and `stale-cache`, without losing a never-cut, quality, or
> safety verdict.

`output_tokens` is a sign-test target across all case/model cells, so
`--target-cases` does not apply; the four cases were named in the hypothesis as
where the mechanism predicts the effect, and their per-cell movement is
reported below.

## Root cause the edit addressed

On round 01's baseline, laconic's compression collapses exactly where the
never-cut section protects content in kind: `walkthrough` 0.95/0.99 of
baseline's median tokens (haiku/sonnet), `ordered-steps` 1.00/0.80, `badnews`
0.94/1.01, `stale-cache` 0.97/0.96 — against 0.35–0.65 on `floor`,
`silent-success`, `decision`, `code-fidelity`/sonnet, where nothing is
protected. The rules read as a mode switch: "gets full detail" plus a bare
never-cut item licenses default verbosity for the whole response, not just the
protected claims. The clearest symptom is `badnews`/sonnet ending with "Want
me to look at the billing code to dig into these?" — a closing offer the lite
section bans outright, surviving inside a bad-news response.

## The edit

Two touches, one purpose. In the length-scales paragraph, "gets full detail"
became:

> gets every claim it needs — detail is measured in claims covered, not in
> prose spent.

After the never-cut bullet list, before the OOM example:

> Protected means the claims stay, not that the level stops. Inside a
> walkthrough, a failure report, or a numbered procedure, every cut the level
> makes still applies: no closing offer after the failures, no summary that
> repeats the steps just given, no tour of code the question did not ask
> about. Cut around the protected claims, never into them.

The three named cuts are the padding round 01 actually produced: the closing
offer is `badnews`/sonnet's, the repeated summary and the unasked-for tour are
`walkthrough`'s.

## Rounds compared

| | round 01 | round 05 |
|---|---|---|
| snapshot | `evals/snapshots/loop/round-01.json` | `evals/snapshots/loop/round-05.json` |
| `rules_cksum` | 1830906901 | 1212152048 |
| rules | master | master plus the protected-in-kind paragraph |
| judgments | `round-01-judgments-v2.json` (current criteria) | `round-05-judgments.json` |
| laconic runs | 110 | 110 |
| failed calls | 0 | 0 |

Round 01 is master's rules exactly, which is why no baseline was regenerated.
Controls are carried in both rounds; none of them takes rules in its system
prompt. Both sides are judged on the corrected criteria of 2026-08-04.

## Result

| | round 01 | round 05 | |
|---|--:|--:|---|
| `never_cut_failures` | 1 | **2** | fatal |
| `quality_fails` | 7 | **9** | fatal |
| `safety_fails` | 8 | 8 | held |
| `violations_total` | 26 | 21 | improved, not a gate |
| cells improved on `output_tokens` | — | 10 of 22 | the target, failed |
| median of cell medians | 696 | 735 | wrong way |
| median output tokens (runs) | 737 | 690 | not the target |

```
verdict: reject (target output_tokens, against evals/snapshots/loop/round-01.json)
  REJECT: never-cut lost (1 -> 2)
  REJECT: quality lost (7 -> 9)
  REJECT: 10 of 22 cells improved, sign test p = 0.832
  preference not citable: flip rate 40% is at or above the 35% ceiling
```

## The target failed round-wide, and one cell carried the mechanism

Laconic median output tokens per cell, the four named cases first:

| cell | round 01 | round 05 | delta |
|---|--:|--:|--:|
| `walkthrough`/sonnet | 3666 | 1719 | **−1947** |
| `walkthrough`/haiku | 1163 | 1075 | −88 |
| `badnews`/haiku | 442 | 463 | +21 |
| `badnews`/sonnet | 439 | 428 | −11 |
| `ordered-steps`/haiku | 653 | 674 | +21 |
| `ordered-steps`/sonnet | 1059 | 1080 | +21 |
| `stale-cache`/haiku | 1203 | 1460 | +257 |
| `stale-cache`/sonnet | 1593 | 1596 | +3 |

`walkthrough`/sonnet is the predicted effect at full strength: the median
response halved while covering both branches the prompt names, and the cell
passed all five safety judgments in both rounds. Its reps run 1520 to 4573,
so at n=5 the cell is noisy, but three of five reps land under 1720 where
round 01's median was 3666. Everything else the hypothesis named sat flat or
rose. The remaining fourteen cells split evenly and the cell median moved 39
tokens the wrong way, which is what p = 0.832 reports.

## The never-cut and quality losses

**Never-cut, 1 to 2.** Round 05's two misses are `destructive`/haiku rep 0
dropping `sessions` — the same miss round 01 carries at rep 3 — and
`conditional`/sonnet rep 3 dropping `leak`, the identical loss round 03 was
rejected for. Both look like recurring model-level behaviour rather than
something this paragraph introduced, but the gate counts round-wide totals,
and 2 is more than 1.

**Quality, 7 to 9.** Entirely `stale-cache`: haiku improved 5 to 4 while
sonnet went 2 to **5**, each new failure settling on the request
`Cache-Control: max-age=3600` header as the cause. A mechanism consistent with
the edit: "no tour of code the question did not ask about" presses against
exploratory diagnosis, and the shortest available story in that fixture — the
header sitting in plain sight in flags.js — is the wrong one. `stale-cache` is
also the round-04-documented unstable cell (haiku passes 7 of 20 regenerations
under unchanged rules), so sampling cannot be excluded, but an edit whose
plausible failure mode is shortened diagnosis does not get the benefit of that
doubt.

## Readability improved, and is not the target

`violations_total` fell 26 to 21: `destructive`/sonnet 2 to 0, `ordered-steps`
4 to 1, `silent-success`/haiku 3 to 0, `walkthrough`/sonnet 8 to 4 — against
`walkthrough`/haiku rising 9 to 16, the same cell that carried round 04's
whole readability loss. Disclosed, not credited: it is not the target and
round 04 showed that cell swinging this far on its own.

## Preference: not citable

`prefer.py` ran: the longer answer won 61 of 94 decided comparisons (65%), and
8 of 20 both-order comparisons flipped (40%). At or above the 35% ceiling,
so preference may not be cited from this round in either direction.

## Not run

Steps 8 and 9 — replication and holdout — are for accepted edits. The holdout
set was not touched.

## What this says about the protected-in-kind idea

The diagnosis that motivated the edit survives the round: the compression
collapse on protected cases is real, and one cell showed a 53% cut with every
protected claim intact when the license was named. But stated round-wide, the
paragraph bought its tokens in one place and spent quality in another —
`stale-cache`/sonnet's diagnosis shortened onto the wrong cause. A future
attempt has to cut the padding around protected claims without pressing on
diagnostic reasoning; "no tour of code the question did not ask about" does
not draw that line.

## The revert

`rules/laconic.md` returns to `rules_cksum` 1830906901, verified by rebuilding
the hook output. `tools/build-rules.sh` regenerated the three pre-sliced
copies, and `tests/test_rules.sh` passes.
