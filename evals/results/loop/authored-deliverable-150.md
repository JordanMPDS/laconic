# Grading the file, not the reply: [#150]'s second half

[`authored-files-150.md`](authored-files-150.md) made the question askable —
`run.py` keeps what the model writes instead of deleting it — and left three
things for the next unit to decide:

> - **What grades an authored file.** The never-cut check is a substring test
>   and the quality judge reads `text`. Neither reaches a file today.
> - **Whether the case belongs in `evals/cases/`.**
> - **Snapshot size.**

This unit answers all three and then measures the thing [#150] actually
claims.

## Pre-registered, before the batch ran

> **Laconic compresses the deliverable when the deliverable is the response,
> and does not compress it when the deliverable is a file the model writes.**
> Measured as the median words of the deliverable, laconic against baseline,
> on `authored-reply` and `authored-file`, sonnet, 10 reps a side, one
> interleaved batch.

Predicted: the reply half lands near the archive's sonnet compression, roughly
0.6 to 0.8 of baseline. The file half lands near 1.0.

**Falsifier: the file half's ratio is at or below the reply half's.** That
result says the rules already reach an authored file, and [#150]'s exemption
reading describes nothing this instrument can see.

The trap is the control on content: it is byte-identical across the two cases,
so a fall in words that costs the answer its facts shows up as a fall in trap
passes on the same table.


## Result: falsified

Sonnet, 10 reps a side, 40 runs, 0 failed. Generated at `rules_cksum`
136269960 from `evals/pilot`, two shards at `--concurrency 2`.

| case | arm | n | wrote a file | deliverable words | reply words | trap |
|---|---|--:|--:|--:|--:|--:|
| authored-reply | baseline | 10 | 0/10 | 464.0 | 464.0 | 10/10 |
| authored-reply | laconic | 10 | 0/10 | 369.5 | 369.5 | 10/10 |
| authored-file | baseline | 10 | 10/10 | 631.0 | 103.5 | 9/10 |
| authored-file | laconic | 10 | 10/10 | 502.0 | 52.0 | 10/10 |

    authored-reply: laconic / baseline = 0.7963  (464.0 -> 369.5 words)
    authored-file:  laconic / baseline = 0.7956  (631.0 -> 502.0 words)

**The falsifier fired.** It was "the file half's ratio is at or below the reply
half's", and the two ratios differ by 0.0008 — the file half is nominally the
lower of the two. The reply half landed where predicted, at the top edge of the
0.6 to 0.8 band. The file half was predicted near 1.0 and came in at 0.80,
indistinguishable from the reply half.

So laconic compresses a file the model authors exactly as hard as it compresses
a reply. The rules reach the deliverable wherever the deliverable goes, and
[#150]'s exemption reading describes nothing this instrument can see.

**It cost nothing.** The trap is byte-identical across the pair, so a fall in
words that cost the answer its facts would show here: the reply half is 10/10
in both arms, and on the file half laconic is 10/10 against baseline's 9/10.
Every run of the file half wrote a file, in both arms.

## What the old metric would have said

The file half's *reply* words fall 103.5 to 52.0, a ratio of 0.50. A `text`
metric — every metric the loop had before this unit — reads only that covering
note, so it would have reported the file half as compressing twice as hard as
the reply half, and the pre-registered prediction as inverted rather than
merely wrong. The measured deliverable moves the other way, from 631 to 502.
Grading the artifact is what makes the difference between the two halves
readable at all, which is the case for `grade_artifacts` independent of how
this hypothesis came out.

## What this does not establish

Ten reps a side is a point estimate with a wide interval. Bootstrapping the
difference of the two ratios (20,000 resamples of the per-run word counts,
seed 150) gives a 95% interval of [-0.143, +0.266] on `file - reply`, with
51.4% of resamples putting the file half above the reply half — a coin flip.
The claim this supports is that the predicted gap is absent, not that the two
ratios are equal to three decimal places. A gap of 0.15 in either direction
survives this pilot, and finding one would need roughly an order of magnitude
more reps than a pilot is worth.

## Disposition

The pair stays in `evals/pilot`. It answered the question it was built for, and
promoting it to `evals/cases/` would change `cases_cksum` for every future
round and need a seeded baseline, to keep measuring a hypothesis that is now
falsified. `grade_artifacts` and `metrics.graded_text()` stay: they are what
made an authored deliverable gradable, and the next case whose output is a file
needs them regardless.

[#150]: https://github.com/JordanMPDS/laconic/issues/150
