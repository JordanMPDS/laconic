# Loop round 05 — pending

## Hypothesis

Written before the round was generated:

> Stating in the never-cut section that protection covers claims, not volume —
> "Protected means the claims stay, not that the level stops", with the level's
> cuts named as still applying inside a walkthrough, a failure report, or a
> numbered procedure — and rephrasing "gets full detail" to "gets every claim
> it needs" in the length-scales paragraph, should move `output_tokens`
> downward round-wide, with the largest drops on `walkthrough`, `badnews`,
> `ordered-steps`, and `stale-cache`, without losing a never-cut, quality, or
> safety verdict.

`output_tokens` is a sign-test target across all case/model cells, so
`--target-cases` does not apply; the four cases are named here as where the
mechanism predicts the effect, and their per-cell movement is reported below
whatever the round-wide verdict is.

## Root cause the edit addresses

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

Round 01 is master's rules exactly, which is why no baseline was regenerated.
Controls are carried in both rounds; none of them takes rules in its system
prompt.

## Result

Pending.
