# Giving the verdict traps something to fail on

**Date:** 2026-08-14
**Rules under test:** `rules_cksum` 1830906901, master — unchanged
**Status:** an instrument change plus the baseline re-grading it forces. No rule
changed. It accepts and rejects no round.

## Why

The three `verdict-*` cases were added to instrument [#60], and
[`design-quality-covariate.md`](design-quality-covariate.md) established that
they cannot signal: **0 quality failures in 300 gradings**, across all four arms
and both rules revisions, with no `not_exercised` in the denominator. A case that
always passes cannot tell a rules defect from a capability boundary, which is
what [#60] needs to know.

The reason is that the traps were one-sided. Each passed on naming one specific
defect, and every stored response names it: across all 150 `-v4` verdict
responses, **150 of 150 name the required defect within the first 500
characters**. The models were never missing the defect. They were wrapping it in
a review of everything else, and no trap clause bit on the wrapping.

## What changed

The `trap` field on all three cases, and nothing else. `criteria_source`,
`never_cut`, `grading` are byte-identical, and `criteria_cksum` moved 3279849760
to 997100469 — that checksum hashes exactly the trap, which is why it fires here
and did not fire when `ordered-steps` was marked saturated.

Two axes were added, both derived from the fixture rather than from
`rules/laconic.md`:

**A. The co-equal framing.** The required defect must be given as the one that
decides the answer, not as one member of a set offered as equally decisive. Each
prompt asks a precedence question in its own words — `verdict-schema` asks
whether the schema holds up *"before we build the ledger on it"*, and the
fixture's trailing comment defines the balance as `sum(amount)` over
`ledger_entries`, so the money type is the defect the ledger's core operation
runs through and the append-only guarantee is not.

**B. Items the document already settles.** `ROLLOUT.md` states the first-space
split is "a known and accepted limitation, not an open question". `EXPERIMENT.md`
states the 0.3% loss "applies to both buckets equally", that the logged-out
exclusion is accepted, and that mobile web is out of scope. Demanding those
change is a misreading of the document. Both drafts say explicitly that naming
such an item as sound is not a failure — only asking for it to change is —
because without that sentence axis B would fail correct answers.

**`verdict-schema` carries axis A alone**, since `schema.sql` declares nothing
accepted.

Each draft was checked against `tests/test_evals_layout.sh`'s `FORBIDDEN` tuple
for `quality` traps, which is a substring test: `narrow` contains **arrow** and
`particle` contains **article**, so neither word could be used and `ROLLOUT.md`'s
own phrase "names with particles" could not be quoted. All three pass with zero
hits.

## Results, and they are weaker than intended

The `-v4` baseline's 150 verdict judgments were re-graded under the new traps —
150 judge calls, no generation, since the responses already existed.

| case | all arms | `laconic` arm |
| --- | --: | --: |
| `verdict-schema` | 5 of 50 | 4 of 20 |
| `verdict-experiment` | 1 of 50 | 0 of 20 |
| `verdict-rollout` | **0 of 50** | **0 of 20** |
| **total** | **6 of 150** | **4 of 60** |

Against 0 of 150 before. Round-wide `laconic` `quality_fails` in the baseline
moves **83 to 87**, all four on `verdict-schema`.

**This is an improvement, not a fix, and the gap against expectation is large.**
The drafts were expected to fire on somewhere between 6 and 9 of 20 per cell.
The best cell fires on 4 of 20, and `verdict-rollout` is still at zero across all
50 responses — exactly as saturated as before. `verdict-experiment` at 1 of 50 is
barely distinguishable from saturated.

So one of the three cases now discriminates weakly and two do not discriminate at
all. [#60] still lacks an instrument that can carry a target.

**Why `verdict-rollout` did not move is worth recording.** Its axis-A clause
targets answers that offer the ordering as one problem among several, but the
enumerated items in a `verdict-rollout` answer are usually the expand/contract
release steps — which the prompt requests, and which a correct answer must
contain. The clause has almost nothing to bite on there.

## What this does not do

**It re-scores no stored round.** Rounds 11 through 19 were graded under the old
traps and keep those verdicts, per `token-scope.md`. Only the `-v4` baseline was
re-graded, into a new file
(`round-01-n10-v4-judgments-traps2.json`); the original
`round-01-n10-v4-judgments.json` is untouched.

**Any round comparing against `-v4` must now use the new judgments file**, or it
publishes a delta between two instruments — the failure `SKILL.md` warns about,
and the reason the re-grading was bought at the same time as the trap change
rather than later.

**A new failure mode now exists.** These cases can fail for reasons unrelated to
compression, so a rules edit that makes answers longer and better could read as a
quality regression. That is the price of a case that can signal at all, and it is
worth paying at 4 of 60 in a way it would not be at 40 of 60.
