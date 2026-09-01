# The never-cut denominator: why `ordered-steps` stays uncovered

**Status: [#10]'s proposal for `ordered-steps` is measured and does not work.**
Two deterministic designs were built and scored against the archive. Both fail
the majority of responses the judge passes, which makes them vacuous in the
opposite direction from the defect [#10] was written to avoid.

## What [#10] asks for

The never-cut check covers 50 of 80 responses per arm. Three cases carry an empty
`never_cut` list and are not checked at all, and they were emptied deliberately —
an earlier version used `"if"` for `conditional` and it matched "different",
"specify" and "identify", so the assertion always passed.

> **Do not fix this by inventing weaker keywords** — that reintroduces exactly
> the defect that was removed.

The proposal is to check *structure* instead, and for `ordered-steps` that is
well posed: the case promises that all four steps are present and their order is
unmistakable, which is checkable without guessing at nouns.

`ordered-steps` is also the one of the three worth covering. It grades `safety`,
while `floor` and `decision` grade `rule-adherence`, which the loop already
treats as supporting nothing because tuning rules against a case that grades
adherence to those rules is circular.

## Design 1: first mention of each step

Four alternation groups, one per step — publish the new key to the verifier set,
start signing with it, wait out the old tokens' lifetime, retire the old key —
and a check that their first mentions appear in that order.

**430 deduplicated responses: 20.0% ordered**, 62.6% out of order, 17.4% missing
a group.

The diagnostic is in the question itself: *"How do I rotate our JWT **signing**
key…"*. Almost every response uses the word "signing" in its opening sentence,
so step 2 matches before step 1 has been described. First mention is the wrong
anchor when the case's subject noun is one of the step verbs.

## Design 2: order within the enumerated steps

The same groups, matched only against lines that open a numbered or bulleted
step, so prose around the list cannot anchor them.

**430 responses: 29.8% ordered**, 32.1% out of order, 36.0% missing, 2.1% with no
list at all.

Better, and still nowhere near usable.

## Why that settles it

The judge passes **80.2%** of `ordered-steps` responses — 1,243 of 1,550 stored
verdicts, against 265 failures and 42 not-exercised.

A deterministic check that fails 70% of responses where the graded truth fails
20% is not measuring the case's promise. Shipping it would drive
`never_cut_failures` from single digits into the hundreds and break every gate
that reads that counter, which is a worse outcome than the always-passing
assertion [#10] exists to prevent. **An always-failing assertion is not the
opposite of a vacuous one; it is the same defect with the sign flipped.**

The reason it fails is vocabulary spread rather than a fixable regex. Models
render "publish the new key to the verifier set" as adding it to a JWKS,
deploying the public key, rolling it out to validators, or adding a second entry
to the key map, and they interleave the four steps with rollout advice that
re-mentions earlier ones.

## What this means for [#10]

[#10] anticipated this outcome and allows it:

> If a case genuinely cannot be checked deterministically, say so and leave it
> uncovered rather than covering it badly.

So: **`ordered-steps` stays uncovered, and the denominator stays at 50 of 80.**
That is now a measured position rather than an unexamined one, and the two
designs are recorded so they are not rebuilt.

What is *not* closed is the judge route. [#10] permits it for `decision` with a
label, and the same would apply here — a judged never-cut verdict, disclosed as
judge-derived and weighted accordingly, inherits the standing caveat that the
judge is a Claude model grading Claude outputs. Nothing in this document argues
against that; it argues only that the deterministic route is not available for
this case.

[#10]: https://github.com/JordanMPDS/laconic/issues/10
