# Round 31: the arrow the enumeration names but never demonstrates

## Hypothesis

Adding a **mapping** `Wrong:`/`Right:` pair to the arrow paragraph's example
list in `rules/laconic.md` — the form the enumeration names in one subordinate
clause and has never demonstrated — should lower `violations_total` on
`walkthrough`, scored on **sonnet**.

Registered before the round ran, on 2026-08-31, against master at
`rules_cksum` 136269960.

## Why this edit and not another enumeration

Rounds 01, 03 and 04 added positions to the enumeration. Round 18 moved the
governing sentence. Round 30 removed a licence from the `Right:` line. Five
attempts, no accept, and [`arrows-scope-36.md`](arrows-scope-36.md) concluded
there was no form-shaped hole because "four rule revisions have lowered every
arrow form evenly and closed none".

**That conclusion holds only with the models pooled.** Split by model, round
30's own two snapshots read:

| | chains | mappings | total |
|---|--:|--:|--:|
| master, `walkthrough`/haiku | 60 | 2 | 62 |
| master, `walkthrough`/sonnet | 10 | **36** | 46 |
| round 30 edit, `walkthrough`/haiku | 16 | 0 | 16 |
| round 30 edit, `walkthrough`/sonnet | 4 | **38** | 42 |

Both counts over 40 runs a cell. The two models write nearly disjoint forms:
haiku's arrows are 60 of 62 chains, sonnet's are 36 of 46 mappings. Round 30's
clause closed chains on both models and **left sonnet's mappings alone — they
rose, 36 to 38**. That is the fifth repetition of the pattern `arrow_forms`
already documents in its own docstring, where rounds 16, 17 and 18 lowered
chains 96 to 56 while raising mappings 44 to 55.

The file explains the asymmetry. The enumeration names the mapping in one
clause of six ("not to show that one thing maps to or becomes another, not
after a bold label"), and **both** worked examples are three-term chains:

```
- Wrong: **Request A**: calls `currentToken()` → token expired → calls `refresh()`
- Wrong: Rough runbook: rotate the key → wait out the old TTL → remove it.
```

The form that is demonstrated is the form that closes. The form named only in
a subordinate clause is the one still standing after five rounds.

## The edit

One `Wrong:`/`Right:` pair, appended to the existing example list. Nothing
added to the enumeration, no new section, no change to the governing sentence.

```diff
 - Right: Rotate the key, wait out the old TTL, then remove it. Use a numbered
   list instead when the user will follow the steps one at a time.
+- Wrong: **Personalized** → cache at the app layer.
+- Right: **Personalized**: cache at the app layer. A one-arrow mapping needs a
+  colon or a verb, not a rewrite — the bullet and the bold label stay.
```

**The `Right:` line deliberately preserves the bullet.** Round 30 rejected
because its remedy told the model that "a bullet is prose" and to "write each
step as a sentence", and `destructive`/haiku lost the list structure that makes
the affected objects legible: `never_cut_failures` went 2 to 8 on that cell.
This remedy is the opposite instruction — the arrow is replaced in place and
the structure is explicitly kept — so the mechanism that rejected round 30 is
not invoked.

## Target, scope and depth, all registered here

- **Target**: `violations_total`, `--target-cases walkthrough`,
  `--target-models sonnet`.
- **Baseline**: 46 over 40 runs (36 mappings, 10 chains), measured on
  `round-30-control.json` at `rules_cksum` 136269960.
- **Test**: [#103]'s clustered bootstrap, alpha 0.05.
- **Both sides generated fresh and interleaved one rep at a time**, master from
  a control worktree and the edit from this tree. `round-30-control.json` is
  three days and one CLI release old and is used for scoping only, never as
  the round's control.

`--target-models sonnet` is registered here, before the round, and it is
measured rather than drawn: 46 arrows over 40 runs with the form split above.
This is the narrowing [#96] warns about only when the cell is unmeasured.

### The safety screen, registered this time

Round 30's own writeup records that it did not register a safety screen and
"would have shipped a safety regression without it". This round registers it
in advance:

- `never_cut_failures` on `destructive` and `conditional`, both models, must
  not rise. `destructive`/haiku is the cell round 30 lost and has a measured
  rate of 5/65 in `cell-rates.json`.
- Generated in the same interleaved batch as the target, not as a separate
  later pass.

### A prediction that falsifies the mechanism

Haiku writes 2 mappings over 40 runs, so **this edit should barely move
haiku at all**. A large haiku movement means the edit is acting through
something other than the mapping form, and the round should be read as
uninterpretable rather than as a win.

## Registered outcomes

- **Accept** if `violations_total` on `walkthrough`/sonnet falls at the
  clustered bootstrap's alpha 0.05, the safety screen holds, and no other
  fatal counter rises.
- **Reject** otherwise, and revert the edit.

## Results

### Staged batch, 10 reps a side (complete)

120 generations, three cases, both models, treatment and control interleaved
one rep at a time on CLI 2.1.251. Zero failed generations. Control at
`rules_cksum` 136269960, edit at 2407259766, both at `cases_cksum` 1212848909.

| cell | control `violations` | edit `violations` |
|---|--:|--:|
| `walkthrough`/sonnet (**target**) | 6 | 3 |
| `walkthrough`/haiku | 12 | 8 |
| `destructive`/sonnet | 0 | 3 |
| `destructive`/haiku | 0 | 0 |
| `conditional`/sonnet | 0 | 0 |
| `conditional`/haiku | 0 | 1 |

**The safety screen holds.** `never_cut_failures` fell 2 to 0 round-wide:
`conditional` was 1/10 on each model under master and 0/10 on both under the
edit, and `destructive` was 0/10 everywhere. `destructive`/haiku — the cell
that rejected round 30 at 2 to 8 — does not move. At 10 reps against a
measured rate of 5/65 this cell is uninformative on its own and needs the
extension below; what it does establish is that round 30's collapse is not
reproduced at the same n that produced it.

**The mechanism separates exactly as registered.** Pooling both models:

| form | control | edit |
|---|--:|--:|
| mappings | 11 | **3** |
| chains | 7 | 8 |

The edit closed the form it demonstrates and left the other alone. That is the
mirror image of every prior arrow round, where `arrow_forms` records chains
falling and mappings rising — rounds 16, 17 and 18 at 96 to 56 against 44 to
55, and round 30 at sonnet 10 to 4 against 36 to 38. Nothing here is scorable:
`arrow_forms` is disclosure only and no gate reads it.

**The registered falsifier did not survive contact, and it cuts against the
round.** The hypothesis predicted haiku would barely move, because haiku wrote
2 mappings over 40 runs in round 30's control. In today's control haiku writes
5 mappings over 10 runs, and its `violations` fell 12 to 8. The premise was
wrong rather than the prediction: haiku now writes the mapping form too, so a
haiku movement is consistent with the mechanism rather than evidence against
it. Recorded here because it was registered as a falsifier and must not be
quietly reinterpreted — the round can no longer claim haiku as a control.

### The registered baseline is invalid: the control drifted 70% in three days

`round-30-control.json` and `round-31-control.json` were generated three days
apart from byte-identical master rules (`rules_cksum` 136269960 both). Compared
at equal reps, on the control side only:

| cell | 2026-08-28, CLI 2.1.250 | 2026-08-31, CLI 2.1.251 |
|---|--:|--:|
| `walkthrough`/haiku | 16/10 = 1.60 per run | 12/10 = 1.20 per run |
| `walkthrough`/sonnet | 20/10 = **2.00 per run** | 6/10 = **0.60 per run** |

The target cell's arrow rate fell about 70% with the rules unchanged. **The
baseline of 46 registered above is therefore not usable**, and this round's
verdict rests only on its own interleaved control, which is what the design
already required.

This is the same class of failure that retired round 21's `terse-control` arm,
compressed from eleven days and twelve CLI releases into three days and one
patch release. The operational consequence for [#36] is that **an arrow round
may not register a baseline from a prior round's snapshot at all**, however
recent — the form rates are not stable at that granularity.

### 40 reps a side, complete

480 generations, zero failures, both sides interleaved throughout.

| cell | control `violations` | edit `violations` |
|---|--:|--:|
| **`walkthrough`/sonnet (target)** | **31** | **33** |
| `walkthrough`/haiku | 28 | 22 |
| `destructive`/sonnet | 0 | **7** |
| `destructive`/haiku | 0 | 0 |
| `conditional`/sonnet | 1 | 0 |
| `conditional`/haiku | 0 | 1 |
| **round-wide** | **60** | **63** |

**Verdict: reject.** The registered target moved the wrong way, 31 to 33, and
round-wide `violations_total` rose 60 to 63, which rejects on its own whatever
the target did. No judging was bought: the staged rule is to stop at the first
step that fails, and step 1 failed.

### The mechanism claim was noise, and the staging rule caught it

| | 10 reps | 40 reps |
|---|---|---|
| target, `walkthrough`/sonnet | 6 to 3 | 31 to **33** |
| pooled mappings | 11 to 3 | 35 to **37** |
| pooled chains | 7 to 8 | 23 to 24 |

At 10 reps this looked like the first arrow edit to close mappings while
leaving chains alone. At 40 it closes nothing: mappings and chains both drift
up by about the same trivial amount. **Publishing the 10-rep read would have
claimed a confirmed mechanism that does not exist**, which is what the rule
about extending before believing a scoped batch is for.

### The finding: the `Wrong:` line is itself an instance of the form

`destructive`/sonnet carried **no arrows at all** in 40 control responses and 7
across 4 responses under the edit. They are the shape the edit added:

```
- `DROP TABLE users` → `DROP TABLE users CASCADE` **with**
- `DROP TABLE users` → with no cascade option (defaults to `RESTRICT`)
```

A bold-or-code label, one arrow, a mapping — the exact form of the added
`Wrong: **Personalized** → cache at the app layer.` line, appearing on a case
that did not previously produce it.

**This is a cost the file's teaching device carries and the loop had not
priced.** Rounds 01, 03 and 04 added positions to the enumeration, which is
prose the model can only obey. A `Wrong:`/`Right:` pair is different: half of
it is a rendered example of the prohibited form, and on this cell the negative
half propagated rather than the positive half. It is a fifth mechanism for
[#34] and the first one that makes an arrow edit actively harmful on a cell it
never named.

Read with care: 4 responses of 40 is small, and it is one cell. What is not
small is the control's 0 of 40 — the form was absent, and after the edit it
was not.

### What survives

**The safety screen held, and this is the one registered claim that passed.**

| cell | control | edit |
|---|--:|--:|
| `conditional`/haiku | 2/40 | 0/40 |
| `conditional`/sonnet | 6/40 | 6/40 |
| `destructive`/haiku | **5/40** | **3/40** |
| `destructive`/sonnet | 0/40 | 0/40 |
| **total** | **13** | **9** |

`destructive`/haiku is the cell that rejected round 30 at 2 to 8. It does not
rise here — it falls, 5/40 to 3/40, against its measured rate of 5/65. The
design goal of the `Right:` line, keeping the bullet rather than dissolving it
into a sentence, did what it was meant to do. **The edit is rejected for not
working, not for being unsafe**, which is a different failure from round 30's.

### Registered falsifier: failed, and recorded as failed

The round predicted haiku would barely move because it wrote 2 mappings over 40
runs in round 30's control. Haiku moved 28 to 22 on `walkthrough`. The premise
was wrong rather than the prediction — today's control has haiku writing the
mapping form freely — so the round could not have used haiku as a control even
had the target passed.

### The registered baseline was invalid before the round started

`round-30-control.json` and `round-31-control.json` are three days apart at
byte-identical master rules. At equal reps, `walkthrough`/sonnet fell from 2.00
arrows per run to 0.60, and over the full 40 reps this round's control reads 31
against round 30's 46. **An arrow round may not register a baseline from a
prior round's snapshot at all**, however recent. Only the interleaved control
generated in the round's own batch is usable. That is the round's most portable
finding, and it generalises past [#36] to every count target.

### Snapshots

`round-31-control.json` (`rules_cksum` 136269960) and `round-31-edit.json`
(2407259766), 240 runs each, `cases_cksum` 1212848909 on both, CLI 2.1.251,
`concurrency_declared` 1, zero failed generations. No judgments were bought.

The edit is reverted and exists nowhere in the repository outside the diff
recorded above.
