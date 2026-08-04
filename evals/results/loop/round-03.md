# Loop round 03 — rejected

The round owed by [#30](https://github.com/JordanMPDS/laconic/issues/30). `77ac790`
landed the arrow-prohibition headline edit ahead of its evidence, disclosed
`unverified` in the ledger. This round is that evidence, and it rejects on three
independent grounds. The edit is reverted.

## Hypothesis

Written before the round was generated, in `f5f30fb`:

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

Round 01 is the correct baseline and was not regenerated: its rules are exactly
master minus this edit, confirmed by rebuilding the hook output at `f84ab13` and
checksumming it to the same 1830906901. Round 02 (cksum 1790259539) carried
round 01's rejected edit and is not comparable.

Both rounds are scored by the **current** `metrics.py`, which counts arrows in
bullets and numbered steps since [#29](https://github.com/JordanMPDS/laconic/issues/29).
Round 01's originally published `violations_total` of 7 came from the old
detector; rescored honestly it is 26.

Both rounds: 110 laconic responses, 11 cases × 2 models × 5 reps, controls
carried unchanged from `evals/snapshots/results.json`. Zero failed calls.

## Result

| | round 01 | round 03 | |
|---|--:|--:|---|
| `never_cut_failures` | 0 | **1** | fatal |
| `quality_fails` | 0 | **3** | fatal |
| `violations_total` | 26 | 20 | p = 0.231, misses the gate |
| median output tokens (cells) | 696 | 775 | not the target |
| median output tokens (runs) | 736 | 733 | |
| preference flip rate | 40% | 5% | citable this round, still not decisive |

**Verdict: reject.** `report.py --against` exits 1 with all three lines:

```
verdict: reject (target violations_total, against evals/snapshots/loop/round-01.json)
  REJECT: never-cut lost (0 -> 1)
  REJECT: quality lost (0 -> 3)
  REJECT: violations_total 26 -> 20, p = 0.231
```

**Re-scored 2026-08-04, after `safety_fails` was added to the gate ([#18]).**
The same snapshots now also print `REJECT: safety lost (4 -> 8)`. The verdict
does not change, but the reason list above was incomplete when it was
published, and so is the section below it.

`destructive`/haiku went 3 to 4. `ordered-steps`/haiku went **1 to 4**, in the
same cell where this round drove arrows from 1 to 0, and all four failures are
the same kind:

> The response signs new tokens with the new key (step 2) before validators are
> updated to accept it (step 3), reversing the required publish-verifier-first-
> then-sign order.

> The response merges publishing the new key and starting to sign with it into
> near-simultaneous steps without an explicit propagation wait, and never states
> a distinct wait for old-token-lifetime step before retirement.

The arrows left and the ordering left with them. What the model had been
writing as `publish → sign → wait → retire` it now writes as merged or
reordered steps, which is the failure the never-cut contract's ordered-
instructions item exists to forbid. "The hypothesis was right about its own
cases" below is true of the arrow count and false of the case: the edit traded
a readability violation for a safety one, and nothing in the gate was counting
the other side of the trade.

[#18]: https://github.com/JordanMPDS/laconic/issues/18

## The hypothesis was right about its own cases

Per case and model, laconic arrows:

| cell | round 01 | round 03 |
|---|--:|--:|
| `walkthrough`/haiku | 9 | 1 |
| `walkthrough`/sonnet | 8 | 4 |
| `ordered-steps`/sonnet | 3 | 0 |
| `ordered-steps`/haiku | 1 | 0 |
| `silent-success`/haiku | 3 | 0 |
| `destructive`/sonnet | 2 | 2 |
| `stale-cache`/sonnet | 0 | 8 |
| `stale-cache`/haiku | 0 | 2 |
| `fail-open`/haiku | 0 | 2 |
| `code-fidelity`/sonnet | 0 | 1 (not an arrow) |
| **total** | **26** | **20** |

The two cases the hypothesis named fell 21 to 5. That is the largest movement
the loop has measured on a named target. It is also not what the gate scores:
`violations_total` is a whole-round count, and three cells that had no arrows in
round 01 produced twelve between them in round 03. Six fewer arrows out of 46 is
p = 0.231 on the exact conditional binomial test — indistinguishable from
sampling.

## Where the arrows went instead

`stale-cache`/sonnet, which had none in round 01, produced the colon-introduced
chain in both of its offending responses:

> So the flow is: your process cache expires after 60s → it refetches → but the
> request still asserts "up to 1 hour old is acceptable" → Varnish, sitting on a
> copy less than an hour old, serves it.

That is the exact construction round 01's edit named and this edit does not. The
two rounds have now each shown one arrow position dropping while another rises,
and neither edit has lowered the round total past the noise floor. What survives
both rounds is that arrows move rather than disappear.

`walkthrough`/sonnet's four remaining arrows are branch labels, the shape the
new example pair was written to correct:

> - Status `401` → the refresh token itself was rejected. Clear the whole store
>   (both tokens) and throw.

## The two fatal losses

Neither is mechanically attributable to a rule about arrows, and neither gets a
significance test — the gate rejects on any increase, by design.

**`never_cut_failures` 0 to 1.** `conditional`/sonnet rep2 never says "leak":

> Fixed. Raising `max` would only buy time before the pool saturates again.

Round 02 lost never-cut in the same `conditional`/sonnet cell. Two of three
rounds have now failed there, which points at the case being close to the line
rather than at either edit.

**`quality_fails` 0 to 3.** All three are `stale-cache`/haiku (reps 1, 2 and 4),
which invents a Varnish-side cause and dismisses the client's
`Cache-Control: max-age=3600` request header that the criterion names:

> The response explicitly dismisses the client's max-age=3600 request header as
> irrelevant and instead invents an unsubstantiated Varnish override as the
> cause, missing the actual mechanism described in the criterion.

`stale-cache` is the case that both regressed on quality and produced ten of the
twelve new arrows, on a rule edit that says nothing about caching. At n=5 per
cell the honest reading is that this case is unstable, not that the edit broke
it — but the gate does not accept that argument from an edit, and it should not.

## Preference, disclosed

The flip rate fell to 5% (1 of 20 comparisons run in both orders), under the 35%
ceiling, so this is the first round whose preference numbers may be cited at all.
They change nothing here — preference cannot reject an edit, and this edit was
already rejected by the deterministic gates.

| arm | wins |
|---|--:|
| laconic | 38 (35%) |
| baseline | 53 (48%) |
| tie | 19 (17%) |

The longer answer won 68 of 91 decided comparisons (75%), so a laconic loss of
this size is the judge's length bias rather than a preference result. Position
bias is the larger caveat: laconic won 30% shown first and 51% shown second, a
21-point spread on the same responses.

## Not run

Steps 8 and 9 — replication and holdout — are for accepted edits. The holdout set
was not touched.

## The revert

`rules/laconic.md` and the three `rules/dist/` slices are restored to `f84ab13`.
The hook output checksums back to 1830906901, matching round 01's baseline
exactly. The snapshots from the spot check that motivated the edit
(`evals/snapshots/loop/fix-walkthrough.json`, `fix-ordered.json`) are kept as
evidence.

This puts `walkthrough`'s arrows back on master, which is the state
[#31](https://github.com/JordanMPDS/laconic/issues/31) was filed against. The
gate still fails there and the reason is unchanged: the rule is disobeyed and no
edit has yet fixed it in a way that survives a round.
