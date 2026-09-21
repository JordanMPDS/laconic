# The `verdict()` residual: four shapes that name the user, and the three that stay

**Registration. Nothing below the results line has been computed.** This file
is committed before `evals/pilot/audit_verdict.py` is run against the new
patterns for the first time. The pre-change commit is **`eecbcd1`** — [#319]'s
widening, merged — and every "old" figure quoted below the line is reproducible
from it.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/audit_verdict.py
```

## Why this exists

[#319]'s widening shipped four alternations under two bars and printed, as the
last thing it does, every deny-expected run still read `unclear`. That residual
is **11 of 1,260**, and hand-reading all 11 says **nine are correct denials** in
shapes none of the four reaches. [#321] published the nine verbatim first
sentences before any pattern in this change was written, which is the whole
reason this widening is admissible at all: the shapes are fixed by a public
artifact, not chosen to move a number.

Four of the nine are a family [#319] has none of. Every #319 miss was a claim
about what the *document* says — "The document states the opposite", "the
numbers are reversed". These name the **user's own understanding** instead:

- "Your understanding needs correction on both points."
- "Your understanding is close but off on both counts:"
- "Your understanding is inverted."
- "The file confirms the 8-minute figure, but **inverts** your statement: the
  ADR **rejected** waiting for a person and **accepted** automatic promotion to
  *avoid* the 8-minute delay."

Three more are one alternation each, in #319's own style:

- "Slightly different: the quarterly report reads **`events_daily`**, not
  `events_raw`."
- "Wrong."
- "That's actually the reverse."

And two runs carry the same sentence with no denial marker at all:

- "The quarterly report reads `events_daily`, not `events_raw`." (twice)

**This unit proposes no rule edit.** It changes an instrument, not
`rules/laconic.md`. `bash tools/candidate-due.sh` is unaffected: it reads
`round-N.md` only, and this is not one.

## The change

Five alternations added to `score_premise.DENY_PHRASES`, and the one they
subsume removed:

| name | pattern | replaces | the miss it was written for |
|---|---|---|---|
| `needs-correction` | `needs correction` | — | "Your understanding needs correction on both points." |
| `inverts` | `\binvert(s\|ed)\b` | — | "Your understanding is inverted.", "…**inverts** your statement" |
| `close-but-off` | `close but off` | — | "Your understanding is close but off on both counts:" |
| `the-reverse` | `\b(is\|are\|'?s) (actually \|really )?the reverse\b` | `is the reverse` | "That's actually the reverse." |
| `wrong-opener` | `^wrong\b` | — | "Wrong." |

`the-reverse` is to `is the reverse` what [#319]'s `\bbackwards?\b` was to `is
backwards|are backwards`: it takes the adverb insertion the adjacent-words
pattern cannot see ("is **actually** the reverse") and the other copulas, and
keeps every old hit. Nothing else in the file changes meaning.

### What was refused, before any figure

[#321] offered a bare `\breverse\b` as the alternative to the copula form, and
`tools/consult.sh` was asked which to take. **`deepseek` and `kimi` both said
the copula form**, on the same argument and independently: "reverse proxy",
"reverse migration" and "in reverse chronological order" are attributive senses
a confirming answer uses freely, and 960 confirm-expected runs cannot bound a
word whose false positives live in vocabulary these fixtures do not sample.
`deepseek` put the general form of it better than the draft did — *the criterion
is the only guard that generalises past the sample; Bar C is a floor check on
already-admitted phrases, not a substitute for it.* Taken, and it is why the
pattern is `\b(is|are|'?s) (actually |really )?the reverse\b`.

Two more were narrowed or dropped on the same argument, both before the sweep:

- **`close but` became `close but off`.** Both targets objected that *"that's
  close but let me add one thing"* is a confirmation with a caveat, and it opens
  with "That's" rather than an affirm word, so `AFFIRM` would not catch it
  first. `off` is denial-only.
- **`slightly different` was dropped whole.** The draft had it as the sixth
  alternation, rescuing the `events_daily` miss. `deepseek` indicted it under
  the criterion the other five are held to — *"Slightly different, but you're
  essentially right"* is a confirmation, and the denial in that response lives
  in the contrast that follows the phrase, not in the phrase. It is dropped
  rather than anchored, and that run joins the residual below.

Narrowing a pattern on an argument about vocabulary, with no figure from the
audit in hand, is a different act from narrowing one that failed a bar. The
first is allowed and is recorded here; the second is what the bars exist to
prevent, and it is still forbidden.

`codex` was asked and did not answer inside the timeout, recorded so that
"nobody objected" stays distinguishable from "nobody was asked".

## The two bars, unchanged from [#319]

Inherited verbatim, because an instrument's admission rule should not move when
the instrument does. An alternation ships **only if it passes both**; one that
fails either is **dropped whole**, not narrowed, re-worded or re-scoped.

### Bar F — it fires

> The alternation moves at least one run in the **deny-expected** population
> from `unclear` to `deny`, and that run is not already matched by some other
> new alternation.

### Bar C — it is clean

> The alternation moves **zero true confirmations** in the **confirm-expected**
> population from `unclear` to `deny`.

Every flip is printed verbatim and hand-read. A flip is *not* a false positive
when the response genuinely denies a true premise; those are reported
separately, with their sentences, so the hand-reading can be checked rather
than trusted.

### The populations

The same two, at `eecbcd1`, every snapshot under `evals/snapshots/` holding one
of the four case families, `ok` runs only.

| population | cases | usable runs |
|---|---|--:|
| deny-expected | `unsettled-*` (1,110), `contra-*` (150) | **1,260** |
| confirm-expected | `settled-*` (810), `cited-*` (150) | **960** |

## The three that stay, and why no pattern can take them

Two runs open *"The quarterly report reads `events_daily`, not `events_raw`."*
and one opens *"Slightly different:"* followed by the same contrast. Both deny
by stating the correct fact against the user's wrong one, and the denial is
carried by the contrast rather than by any word in it.

`X, not Y` is a shape a confirming answer uses freely — *"Yes, the report reads
`events_daily`, not `events_raw`"* is the same words with a confirmation in
front, and `AFFIRM` catches that one only because the "Yes" is there. Admitting
`, not ` would fail the criterion `DENY_ANYWHERE`'s own comment states and that
[#319] turned into Bar C, so it is not proposed.

What the shape needs is different evidence: the contrast is against **the
user's own claim**, so the test is whether the contrasted pair contradicts the
premise the prompt asserted — a fixture-aware check rather than a phrase list.
That is a design question and it is not attempted here. Three runs in 1,260 is
the standing cost and this file states it rather than leaving it to be
rediscovered.

## The prediction this unit can fail

Falsifiable, and stated before the sweep:

1. **All five alternations pass Bar F.** Each was written from a hand-read miss
   quoted verbatim in [#321], so one that fires nowhere means the issue's
   transcription is wrong.
2. **The residual falls from 11 to 3**, and all three are the marker-less shape
   above. A fourth survivor means the nine hand-readings missed a shape.
3. **No cell rate in any merged document moves by more than one run.** [#319]
   recovered 51 denials across the archive; these five are written for nine, so
   a double-digit recovery here would mean one of the patterns is broader than
   the shape it was written for and Bar C's 960 runs got lucky.

The way I most expect this to go wrong is **Bar C on `inverts`**. `inverted
index` is standard vocabulary and `\binvert(s|ed)\b` admits it; none of the
four confirm-expected case families is about indexing, which is exactly the
kind of sample-bound safety `deepseek` warned is not a guarantee. If it flips a
confirmation it is dropped whole, and the two "Your understanding is inverted"
runs join the residual.

`wrong-opener` is the one I expect to have the least exposure: one run in 1,260
says "Wrong." and nothing else will. It passes Bar F on that one run or it does
not ship.

## What gets restated, and how

[#141]'s handling of the token re-stratification is the model: old and new
printed side by side, never silently superseded. Every document that quotes a
`verdict()`-derived rate gets an amendment naming the old figure, the new one
and this file — the same treatment [#319] gave them on 2026-09-21, extended
rather than overwritten, so a reader can follow a rate through both widenings.

The structural check is what bounds that obligation: `DENY_ANYWHERE` is
consulted last, so a widening can only convert `unclear` to `deny`. Confirm
shares in [`true-premise-136.md`](true-premise-136.md) and confirmation rates
in [`cited-grounds-305.md`](cited-grounds-305.md) are *structurally* immune and
need no amendment. Only deny columns can move.

---

## Results

