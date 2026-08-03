# Loop round 03 — in progress

The round owed by [#30](https://github.com/JordanMPDS/laconic/issues/30). `77ac790`
landed the arrow-prohibition headline edit ahead of its evidence, disclosed
`unverified` in the ledger. This round is that evidence.

## Hypothesis

Written before the round was generated:

> Editing `rules/laconic.md` — changing the arrow prohibition's headline from
> "No arrows inside a sentence" to "No arrows in prose, anywhere. A bullet and a
> numbered step are prose too", plus a third `Wrong:`/`Right:` pair showing the
> correct shape for a branch list — should move `violations_total` on
> `walkthrough` and `ordered-steps` downward from round 01's baseline, without
> raising `never_cut_failures` (0) or `quality_fails` (0).

Root cause it addresses: the rule already enumerated every construction the
model produced — "not after a bold label", "in a 'quick runbook' line", "inside
a quoted flow" — and the model still wrote a numbered step close to verbatim the
rule's own `Wrong:` example. What it appears to act on is the headline, and a
bullet is not a sentence.

## Rounds compared

| | round 01 | round 03 |
|---|---|---|
| snapshot | `evals/snapshots/loop/round-01.json` | `evals/snapshots/loop/round-03.json` |
| `rules_cksum` | 1830906901 | 2868055581 |
| rules | master before `77ac790` | master at `77ac790` |

Round 01 is the correct baseline and is not regenerated: its rules are exactly
master minus this edit, confirmed by rebuilding the hook output at `f84ab13` and
checksumming it. Round 02 (cksum 1790259539) carried round 01's rejected edit
and is not comparable.

Both rounds are scored by the **current** `metrics.py`, which counts arrows in
bullets and numbered steps since [#29](https://github.com/JordanMPDS/laconic/issues/29).
Round 01's published `violations_total` of 7 was produced by the old detector;
rescored honestly it is 26.

## Result

_Pending._
