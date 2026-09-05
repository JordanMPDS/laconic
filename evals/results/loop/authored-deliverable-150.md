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

[#150]: https://github.com/JordanMPDS/laconic/issues/150
