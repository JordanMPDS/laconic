# The closing recap: [#305]'s cheapest item, and why it is not testable here

**This is not a round.** It proposes no rule edit, buys no generation, spends no
call, and takes no row in [`LEDGER.md`](LEDGER.md). It is the measurement that
was supposed to precede round 71's registration, and it killed the candidate
before the round was registered. Round 71 is still unregistered and the
[`candidate-due.sh`](../../../tools/candidate-due.sh) allowance is unspent.

Reproduce every number below with:

```sh
python3 evals/results/loop/closing-recap/sweep.py
```

## What [#305] asks for

[#305] reports a narrowing follow-up — eleven words, scoping down to one of
three buckets already enumerated two turns earlier — answered in 309 prose words
where about 40 were correct. It classifies the 309 by paragraph and names three
separable faults. The cheapest of the three is the one that is new:

> **There is no rule against closing with a recap of your own opening.**
>
> `lite` has "No recap of work visible in the diff", which is about tool output,
> and the never-cut list protects reporting failures and skipped steps. Neither
> covers restating, as a final paragraph, the claim the response already led
> with. […] `full` says "Lead with the answer", and a long middle then creates
> pressure to land the answer again at the end so the response feels closed.
> **The lead-with-the-answer instruction may be generating the recap it does not
> forbid.**

That is a good lead. It names a mechanism inside the rule file's own text, it is
intra-response rather than cross-turn — so unlike [#298] it needs no transcript
and no multi-turn harness — and the shape it describes looks countable: a final
paragraph whose claims are a subset of the first.

The round it implies would add one bullet to `lite`'s ceremony list, beside the
existing diff-recap bullet, and score a `closing_recap` count target against a
simultaneous control. **Before buying that, the loop owes itself the detector and
its rate**, because a count target with no headroom is a round that cannot reject
and cannot accept. Getting that order right is what made this cheap.

## The detector

[`closing-recap/detector.py`](closing-recap/detector.py), built on the same
helpers `metrics.py` uses so that paragraphs, code fences and inline spans are
segmented identically. It fires when all of:

- the response has at least 3 prose paragraphs — fewer has no middle to shrink,
  which is the mechanism [#305] describes;
- the closing paragraph is at least 15 words — a one-line sign-off is not the
  reported harm;
- the closing paragraph is at most 25% of the response's prose words — [#305]'s
  recap was 37 words after 270;
- optionally, the closing paragraph names no referent (number, backticked
  identifier, dotted or underscored or internally-capitalised symbol) that has
  not already appeared — a paragraph asserting a new claim usually names a new
  object;
- and the fraction of the closing paragraph's content words that already appear
  in the opening paragraph clears a threshold.

The threshold had to come down before it caught anything. A hand-written
textbook recap — lead with "the migration is done", 200 words of middle, close
with "so the honest answer: the migration is done" — scores **0.50**, because a
recap carries framing vocabulary ("answer", "remaining", "gap", "honest") that
the opening does not. The 0.65 a first draft reaches for rejects the thing the
detector exists to catch. That is preserved as an assertion in `detector.demo()`.

## The rate, and the denominator that makes it readable

A near-zero rate is ambiguous between *the model does not do this* and *the
benchmark never produces an answer long enough to do it in*, and those call for
different responses. So the rate is reported twice: over all 31,595
de-duplicated archived responses, and over the responses that are structurally
able to carry a closing recap at all.

| arm | n | median prose words | eligible | eligible rate | fires \| eligible |
|---|--:|--:|--:|--:|--:|
| `laconic` | 26,080 | 156.0 | 7,813 | 29.96% | 381 (**4.9%**) |
| `baseline` | 1,630 | 193.5 | 546 | 33.50% | 31 (**5.7%**) |
| `terse-control` | 290 | 234.5 | 101 | 34.83% | 8 (**7.9%**) |
| `concise-style` | 289 | 171.0 | 61 | 21.11% | 3 (**4.9%**) |
| `word-compression` | 300 | 221.0 | 118 | 39.33% | 5 (**4.2%**) |

**The instrument is not the limitation.** About a third of every arm's responses
are structurally eligible, and the ruled arm is eligible nearly as often as the
unruled one — so the answer is not "laconic is too short to recap".

**The arms do not separate.** 4.9% against 5.7%, with three controls spanning
4.2% to 7.9% and the ruled arm sitting in the middle of them. Compare the one
detector in this family that was promoted: `closing_offers` reads laconic 3.5%
against baseline 13.1% at Fisher p = 8.6e-18, with every control arm at or above
baseline — 16.8%, 19.6%, 22.0% ([`closing-offers.md`](closing-offers.md)). That
is what a rule binding on a countable shape looks like. This is not that.

Tightening does not rescue it. Over all responses, at overlap 0.40 with the
referent gate on, laconic reads 33 of 26,080 — **0.13%** — against baseline's
0.18%. A target at that base rate cannot be moved by any round this loop buys.

## The precision, and why it is structural

Fifty hits were drawn at seed 71 and hand-read: 30 at the setting whose rate the
table above quotes, 20 at the stricter one. That is the [#155] convention — the
standard set `metrics.closing_offers` cleared at 30 of 30 and the restatement
detector failed at 55.3%. The labels and the criterion are in
[`closing-recap/labels.json`](closing-recap/labels.json); redraw them with
`python3 evals/results/loop/closing-recap/draw.py strict`.

> A hit is a true recap when the closing paragraph asserts only claims the
> response has already asserted, so that deleting it loses no claim. A closing
> that states the fix, asks for information the answer needs, names what was
> left out, or adds a further recommendation is asserting something new and is
> not a recap, however much vocabulary it shares with the opening.

| sample | n | true recaps | precision |
|---|--:|--:|--:|
| loose (overlap 0.25) | 30 | 3 | **10%** |
| strict (overlap 0.40, referent gate) | 20 | 3 | **15%** |
| pooled | 50 | 6 | **12%** |

Twelve percent, against the 55.3% that was already low enough to park the
restatement detector permanently. And the 44 false positives are not scattered.
They are three shapes, and each one is a structural reason lexical overlap
cannot work on this construct:

| shape | n | why it fires |
|---|--:|---|
| **a closing question asking for what the answer needs** | 19 | *"What's in front of `/v1` right now — a gateway, or is it hitting the app directly?"* Drawn entirely from the opening's vocabulary, naming nothing new, and **never-cut protected content**: the rules require asking rather than guessing. |
| **a closing fix** | 16 | *"Remove the `&` from line 10 so the script waits for the upload."* A diagnostic answer names the defect in the opening and the repair in the closing. The repair is about the same object, so it shares its nouns **by construction**. Entirely new claim, maximal overlap. |
| **a closing addition** | 8 | a further optional layer, a net-effect summary, a named omission. [#305]'s own rule file requires the last of these — *"a name for the depth you left out"*. |
| **a closing offer** | 1 | already counted by `metrics.closing_offers`, under its own rule. |

**The referent gate inverts.** It was added to raise precision — a paragraph
asserting something new usually names something new — and it lowers it, from
30 hits containing 6 shapes to 20 hits that are 13 closing questions and 4
closing fixes. A question asking *"what stack do you run?"* introduces no
referent by construction, so the gate selects for the largest false-positive
class instead of against it. Precision went **up** three points only because the
sample got smaller; the shape mix got worse.

## What this closes, and what it does not

**[#305] item 1 is not testable on this benchmark, and not for want of tuning.**
The failure is not a threshold in the wrong place. It is that on any answer
which diagnoses something and then repairs it — which is most of this suite, and
most of the sessions the reports come from — the opening and the closing are
*about the same object*, so content-word overlap between them is high whether or
not a claim was repeated. The measurement is dominated by what the answer is
about rather than by whether it said it twice.

That is the same wall [#155] hit from the other side, and it is worth stating as
one finding rather than two:

> **Redundancy is not a lexical property.** [#155]'s v1 criterion asks whether a
> passage "adds nothing that was not already there" and parks at 55.3%; this one
> asks whether a closing paragraph re-uses the opening's words and reaches 12%.
> Neither is measuring restatement. A response that repeats a claim in fresh
> vocabulary is invisible to both, and a response that repairs the defect it
> just named is caught by both.

So item 1 joins [#150] and [#298] on the route [#146] established: a judged
redundancy verdict, frozen before its validation sample is drawn. It does not
need a round of its own — it needs the verdict the other two are already waiting
on, and it should be added to that verdict's scope rather than chased
separately.

**Items 2 and 3 of [#305] are untouched by this.** Item 2 (name the narrowing
follow-up) is cross-turn and shares [#298]'s instrument problem. Item 3
(distinguish *"what is left?"* from *"give me the report"*) edits the
length-scaling licence, which is now five interventions and one survivor after
[round 70](round-70.md) reverted, and which [#150] is owed a redundancy verdict
on before another edit.

**What would make item 1 testable.** Not a better regex. Either the judged
verdict above, or a case whose fixture makes the correct closing *knowable* — an
answer where the right last paragraph is empty, so a closing paragraph of any
kind is the defect and no semantic judgement is needed to say so. That is a
case-authoring problem, it is the same shape as the two the cluster has already
bought ([`register-inheritance-136.md`](register-inheritance-136.md), round 67),
and it is cheaper than either because it is single-turn.

## Where the design came from

The design this document tests was sharpened by `tools/consult.sh`, and one
target answered — Kimi, via the Kimi Code CLI. Two of its points changed what
was built, and both proved load-bearing:

- **Narrow the trigger to a surface form plus a structural position, the way
  `closing_offers` did, rather than trusting content-word overlap** — because
  recap detection is semantically closer to the parked `restates` than to the
  promoted `closing_offers`. It proposed the no-new-referents test as the
  discriminator. That test is in the detector, it is the reason the strict
  setting exists, and measuring it is what produced the inversion finding above.
- **Stratify the archive sweep rather than quoting an aggregate rate**, because
  an adequate-looking pooled figure can hide the fact that every firing cell is
  on the unruled arm. That is the eligible-denominator table, and it is what
  turned "the rate is near zero" into a readable answer.

Its third point was not adopted. It argued for placing the rule in `full`
alongside "Lead with the answer", where the mechanism the report names lives,
rather than in `lite`'s ceremony list. The counter is this repository's own
record: writing a bound into a licence's own prose is 0 for 4 (rounds 07, 08, 09
and 29) while relocating one under a heading whose limits it inherits is 1 for 1
(round 10), and a sentence appended to "Lead with the answer" is the first
shape, not the second. The argument is recorded because the rule was never
written — if item 1 is ever revived on the judged route, the placement is still
open and Kimi's reading deserves a hearing on its merits.

Codex and DeepSeek were asked and did not answer inside the timeout.

[#146]: https://github.com/JordanMPDS/laconic/issues/146
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
