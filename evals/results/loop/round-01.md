# Loop round 01 — rejected

The arrow prohibition was widened to name the colon-introduced chain. The
target metric moved and cleared its gate; a never-cut verdict was lost in the
same round, which rejects on its own. The edit was thrown away.

## Hypothesis

Written before the confirming round was generated:

> Editing `rules/laconic.md:49` — generalizing the arrow prohibition from
> "inside a sentence" to all prose, and naming the colon-introduced chain —
> should move `violations_total` on `ordered-steps`, `silent-success` and
> `walkthrough` downward from 7, without raising `never_cut_failures` (0) or
> `quality_fails` (0).

It came from the round-01 inventory. Two of the three arrow findings were
chains introduced by a colon, a position the rule enumerated forbidden places
without ever naming:

- `ordered-steps`/sonnet rep3: "Rotating then just means: publish new key in
  JWKS → wait propagation/cache TTL → start signing with it → later drop the
  old"
- `silent-success`/haiku rep3: "The race condition is: `aws s3 cp` starts →
  `rm -f` deletes the file → upload fails because the file is gone → script
  exits 0 anyway"

## The edit

```diff
-**No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
+**No arrows in prose, anywhere.** Never use `→` or `->` in prose: not to chain
 steps, stages, states or causes, not to show that one thing maps to or becomes
-another, not after a bold label, not in a "quick runbook" line, not inside a
-quoted flow. Sequencing is where an arrow is most tempting and least
-acceptable: an ordered process is exactly the content whose connecting words
-are never cut.
+another, not after a bold label, not after a colon that introduces a chain, not
+in a "quick runbook" line, not inside a quoted flow. Sequencing is where an
+arrow is most tempting and least acceptable: an ordered process is exactly the
+content whose connecting words are never cut.
+- Wrong: The race is: the copy starts → the delete removes the file → the
+  upload fails.
+- Right: The race is that the copy starts, the delete removes the file, and the
+  upload then fails. A colon does not license the arrows that follow it.
```

`tests/test_rules.sh` rejected a first version of this edit that illustrated the
colon case with an inline arrow outside a `Wrong:` example. The guard worked.

## Result

Both rounds: 110 laconic responses, 11 cases × 2 models × 5 reps, controls
carried unchanged from `evals/snapshots/results.json`.

| | round 01 | round 02 | |
|---|--:|--:|---|
| `never_cut_failures` | 0 | **1** | fatal |
| `quality_fails` | 0 | 0 | |
| `violations_total` | 7 | 0 | p = 0.008 |
| median output tokens | 696 | 778 | not the target |
| preference flip rate | 40% | 35% | not citable either round |

**Verdict: reject.** `report.py --against` exits 1 on `never-cut lost (0 -> 1)`.
The failure is `conditional`/sonnet rep1, which never names the leak:

> Applied the fix. Once callers reliably release on error, watch whether
> `waiting` still climbs under normal load — only then does increasing `max`
> make sense.

One failure in 110 responses is not strong evidence that the edit caused it,
and the never-cut gate applies no significance test — it rejects on any
increase. That is deliberate, and honoring it is the point: a rule set that
trades a safety item for a formatting win is worse, not cheaper. The edit is
reverted.

## What the target number does not say

`violations_total` fell 7 to 0, but the scorer counts arrows only in
running-prose lines. `_symbol_hits` in `evals/bench/metrics.py:121` skips
`STRUCTURAL` lines — bullets, headings, table rows — and skips numeric
progressions.

Counting every non-numeric arrow outside code, bullets included, the same two
rounds read **26 to 9**, not 7 to 0. Round 02 still produced the same runbook
chain the edit targeted, moved into a bullet where the scorer does not look:

> `ordered-steps`/sonnet rep3: "- Rotation runbook: mint new key → publish it
> in the verification set alongside the old one → flip signer to new key → wait
> out max TTL → retire old key"

So the direction is real and large on the broader count, but the scored 100%
drop overstates it, and part of the measured win is the model relocating arrows
rather than writing the conjunction. `rules/laconic.md` forbids arrows "in a
'quick runbook' line" and "after a bold label" — both structural positions the
scorer exempts by design. **The rule and its detector disagree about bullets**,
and until that is settled `violations_total` is not a sound optimization
target. That is the finding this round produced, and it outranks the edit.

## Instrumentation fixed mid-round

`accept_verdict` ran a statistical test only for `target == "output_tokens"`.
Every other target fell through to the fatal conditions, which fire only on a
regression — so any round that merely failed to get worse returned "accept",
reading as a confirmed hypothesis. An unrecognized target now rejects, and the
three fatal counters are gated by an exact conditional binomial test at the
same alpha, with exposure read from each round's usable-run count rather than
assumed equal. Without that fix this round's verdict line would have been
"accept" on a metric nothing had tested.

## Not run

Steps 8 and 9 — replication and holdout — are for accepted edits. The holdout
set was not touched.
