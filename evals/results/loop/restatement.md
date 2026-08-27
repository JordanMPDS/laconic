# `restates`: building the instrument #150 needs

**Status: batch 1 labelled. No detector exists yet.**

Round 29 rejected [#150]'s rules edit and, more usefully, established that
`output_tokens` cannot answer [#150] at all. The scoped floor computed from that
round's own control is 298 tokens on a 1684-token median — a **17.7% bar** —
against the **17.2%** harm [#150] measured. An edit that removed every restated
word would land 8 tokens short, and more reps cannot help, because the floor is a
per-cell standard deviation rather than a standard error.

So the next move is a metric, and this is the file that builds it. The route is
the one [#146] established for `unread_asks` and [#49] took before it: define the
criterion, label a sample, validate a detector out of sample, re-score the
archive, publish the null, and only then let it score a round.

## What is committed, and in what order

The order is the point. `unread_asks` learned what happens otherwise — its v2
detector was designed on batch 1's errors and read 93.1% precision in sample
against 73.7% fresh.

| commit | what it fixed |
|---|---|
| `bb8462b` | [`criterion.md`](restatement/criterion.md), the labelling rule; [`draw.py`](restatement/draw.py); `key.json` and `blind.md` for batch 1; [`lexical_probe.py`](restatement/lexical_probe.py) |
| this one | `labels.json`, and everything below |

## The frame and the draw

Every stored laconic response on the four requested-content cases —
`walkthrough` and the three `verdict-*` — across every snapshot in the archive.
**1,780 responses.** Round 29 established these as the cells where [#150]'s harm
would live: the prompt asks for an explanation or an evaluation, and the answers
are long enough to carry a restated claim.

Batch 1 is an **unstratified simple random draw** of 60 at seed 150, spanning 14
distinct rules texts and 23 snapshots, 31 sonnet and 29 haiku. Unstratified
because that is what leaves precision *and* recall unbiased for whatever detector
is eventually scored against it — `unread_asks` published an 80% recall that was
really 48% because its first batch was stratified 1:1 against a true ratio near
1:5. There is also no detector yet, so there is nothing to stratify on.

Labelled blind: `blind.md` carries an id and a case name, and no arm, model,
snapshot, rules text or token count.

## The base rate

**26 of 60, 43.3%.** That matters for the metric's shape: a binary label that
fired on nearly every long response would saturate and could not move, and this
one does not.

| case | haiku | sonnet |
|---|---|---|
| `walkthrough` | **8/8, 100.0%** | 4/11, 36.4% |
| `verdict-experiment` | 5/8, 62.5% | 2/6, 33.3% |
| `verdict-rollout` | 4/6, 66.7% | **0/9, 0.0%** |
| `verdict-schema` | 3/7, 42.9% | **0/5, 0.0%** |
| **all** | **20/29, 69.0%** | **6/31, 19.4%** |

## The finding that will shape the metric: restatement is a haiku behaviour

**haiku 69.0% against sonnet 19.4%, one-sided Fisher p = 0.000117**, and haiku is
higher in every one of the four cases, so it is not a case confound. The labels
were written blind to model, which is what makes the split a finding rather than
an artefact of expecting one.

Two consequences, both registered here before any detector exists:

1. **A sonnet-scoped target would have almost nothing to move.** Sonnet reads 0
   of 9 and 0 of 5 on two of the four cases. This is the mirror image of
   `one_turn`, which is sonnet-only because its proxy leaks on haiku; here the
   behaviour itself is concentrated on haiku, and any scope decision has to be
   made on that basis rather than copied from the existing targets.
2. **The benchmark's restatement may not be [#150]'s.** [#150] was reported
   against Opus at level `full`, writing a document. What this sample measures is
   overwhelmingly a haiku behaviour on chat responses. They may be the same
   phenomenon at different rates, or they may not be, and nothing here settles
   it. A metric built on this population should not be described as measuring
   the thing [#150] reported without that caveat.

## What the cheap detectors do, measured rather than assumed

**Lexical containment does not work, and it fails in the wrong direction.**
[`lexical_probe.py`](restatement/lexical_probe.py) splits a response into units,
drops stopwords, and flags a unit whose content words are largely contained in an
earlier one. On the known-redundant response the closing recap scores **0.21**;
on the known-dense response the top score is **0.40**, on a passage that
*contrasts* two kinds of 401 rather than repeating either. The dense response
outranks the redundant one. Restatement is semantic, and lexical overlap tracks
shared technical vocabulary, which recurs most in the responses working hardest.

**A closing-flourish regex is precise and mostly blind.** Matching "the key
insight", "the critical invariant", "in short", "bottom line" and similar in the
last two paragraphs reads, against these 60 labels:

| | |
|---|--:|
| precision | **87.5%** (7 of 8) |
| recall | **26.9%** (7 of 26) |

So a formulaic closing sentence is nearly always a real restatement, and it
accounts for about a quarter of them. The other 19 are recap *lists* that re-ask
questions the response already posed, sections that re-argue a mechanism the
enumeration above already stated in full, and "what to add" blocks that restate
the problems as imperatives. None of those has a surface form to match on.

**This is why the detector has to be judged.** `asks_back` is a regex, which is
what made `unread_asks` free to re-score across 27,291 stored runs. A judged
detector costs about $0.039 a call at the judge's measured rate, so re-scoring
even this four-case frame of 1,780 responses is roughly $69 — affordable, but not
free, and worth knowing before it is designed rather than after.

## What happens next, in order

1. **Write the judged detector against `criterion.md`**, and commit it *before*
   drawing anything to validate it on. `draw.py --exclude` takes batch 1's
   `key.json` so batch 2 cannot overlap it.
2. **Draw batch 2, disjoint, and label it blind.** Measure precision and recall
   out of sample. In-sample numbers are not evidence; that is the whole lesson of
   `unread_asks` v2.
3. **Decide the metric's shape from the measured base rate**, not before it.
   43.3% leaves room for the binary; whether a count of restated passages
   discriminates better is an open question this sample cannot answer, because it
   was labelled binary.
4. **Re-score the archive and publish the null.** How much does this move round to
   round at fixed rules text, and does it ever fire where the archive's verdict
   says it should not?
5. **Only then register a round against it.**

Nothing here is a gate, a target, or a disclosure yet. It is a base rate and two
measured negative results about the cheap ways of getting one.

[#49]: https://github.com/JordanMPDS/laconic/issues/49
[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#150]: https://github.com/JordanMPDS/laconic/issues/150
