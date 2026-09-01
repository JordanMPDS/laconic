# `unread_asks` v3: the narrowing hypothesis fails, and no sample was drawn

**Status: v3 is not a promotion candidate. It is worse than v2 on the batch it
was designed against, which is the optimistic direction, so no third sample was
drawn and no labelling was spent.**

[#153] specifies the protocol: freeze a candidate, then draw a third sample
disjoint from the 140 already labelled, then label blind, then score. The freeze
comes first because designing on the sample you then score on overstates the
result — v2 read 93.1% precision in-sample and 73.7% fresh, a 19-point gap.

This candidate never reached the draw, for a reason that needs no fresh data.

## The hypothesis

[#153] names two error shapes v2 leaves. Reading v2's seven actual errors on
batch 2 shows both have the same structure:

- **All five false positives** carry a question *earlier* in the closing two
  paragraphs and then resolve it, ending on enumeration or a recommendation —
  "Left out: EXIF orientation/GPS stripping, ...", "I'd ship the Postgres
  version first and only reach for Meilisearch if ... demands it."
- **Both false negatives** put the hand-back in the *final sentence* with no
  question mark — "Which database are you on, and roughly how many products —
  that decides which of the two to actually spec out."

So v3 narrows position and widens form: read only the last two sentences of the
final paragraph, and fire on interrogative *content* rather than punctuation
alone.

## The result, in sample

| detector | precision | recall | F1 |
|---|--:|--:|--:|
| v2, fresh (batch 2) | 73.7% | 87.5% | **80.0%** |
| **v3, in sample (batch 2)** | **78.6%** | **68.8%** | **73.4%** |

The narrowing worked on what it was aimed at — false positives fell from 5 to 3.
It cost more than it bought: **false negatives rose from 2 to 5**, because real
hand-backs are not reliably in the last two sentences.

**v3's figure here is in-sample and therefore optimistic**, and it is already
below v2's *out-of-sample* F1. A fresh draw could only lower it. There is no
version of the third batch that rescues this candidate, so drawing and labelling
one would have spent sixty hand-labels to confirm a loss.

## What this tells a v4

**Position is not the discriminator.** v2 buys its recall by reading two whole
paragraphs, and that width is doing real work — narrowing it to two sentences
loses three true hand-backs to save two false ones. A v4 should keep v2's window
and attack the false positives *within* it, by detecting that a question was
resolved rather than by moving away from where questions appear.

That is the harder problem, and it is the one [#153] actually describes: "a fork
posed as a question and resolved for both branches in the same breath." The
resolution is semantic — "If sellers are often on weak connections, resumable is
worth the extra complexity" answers its own question — and a regex that reaches
it is not obviously available. That may make this the same shape as [#155]'s
restatement metric, which parked at 55.3% precision for the same reason: the
boundary is semantic, not syntactic.

## Files

`detector_v3.py` is kept, frozen, with its in-sample figure recorded in this
file rather than in its docstring. It is evidence about a design direction, not
a candidate. Nothing in `evals/bench/` calls it and the `asks_back` pin in
`tests/test_bench.py` still points at `detector_v2.py`.

[#153]: https://github.com/JordanMPDS/laconic/issues/153
[#155]: https://github.com/JordanMPDS/laconic/issues/155
