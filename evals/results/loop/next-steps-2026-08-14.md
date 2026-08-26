<!-- Next-steps report, 2026-08-14. Produced by DeepSeek through `delegate`, in
a separate worktree with no access to this session's reasoning. Committed
verbatim as received, at the path it was written to (the repository root); the
date is in the filename because the content is dated.

STALE BY CONSTRUCTION. It was written when round 19 was the most recent round
and it ranks what to do next from there. Rounds 20 through 27 have since run, so
read it as a record of what the open questions looked like on 2026-08-14, not as
a plan. -->

# Next steps

## Where the loop stands

Round 19 (commit `451314d`) was rejected on two grounds, and `rules/laconic.md`
stays at the pre-round checksum (`rules_cksum` 1830906901). Its registered
`output_tokens` target read 11 of 15 voting cells down — sign test p = 0.118,
median shift +340 — against a registered 12 of 15 and a 658-token floor, while
`never_cut_failures` rose 2 → 5 (`evals/results/loop/round-19.md`, "Results").
The write-up names the cause: the verdict cells have never moved under any edit
(design family 7 of 9 down at a median −71, verdict family 4 of 6 at +116), so
the evaluative-question rule this round tested did not reach them.

## Next steps, ranked

1. **Settle whether `Level: full` is saturated on length, and pick the next edit
   shape from the answer.** Round 19 ends by flagging the useful reading — "no
   additional `Level: full` bullet about length will work" — as testable and
   cheap (`round-19.md`, "What that says about the rule"). The loop's three most
   recent length edits (rounds 16, 17, 19) all added an abstract claim and moved
   their targets inside the noise; the one edit ever to pass step 7, round 15,
   was a relocation of an existing licence to where its limits are inherited
   (`LEDGER.md`, `SKILL.md` step 5). *Unblocks the next round.* Depends on:
   unblocked.

2. **Measure the never-cut lottery cells harder.** Round 19's other rejection was
   `conditional`/sonnet at 4 of 10 against a measured 8 of 60 (13.3%) that the
   screen did not clear, and the write-up's remedy is "more measurement, not an
   arbitration" (`round-19.md`, "The other rejection"). These cells reject rounds
   independently of the target — round 18's target passed and it still rejected —
   and `instrument-notes.md` records `conditional`/haiku as the only never-cut
   movement in the series that survives measurement. *Unblocks the next round.*
   Depends on: unblocked (≈40 calls per cell, per `SKILL.md`).

3. **Decide whether #60/#46 is a rules problem or a capability boundary.** The
   verdict cells have now been measured under two revisions that moved design
   answers and one written for them specifically, and they have never moved
   (`round-19.md`, "What this round establishes", point 1). Round 16 reached the
   same shape on quality — a rule saying "read the code first" does not make
   haiku read the code, a capability boundary rather than a rules defect
   (`LEDGER.md`, round 16). *Unblocks the next round*: it determines whether
   another #60 edit is worth the calls. Depends on: unblocked.

4. **Salvage round 18's arrow clause, which met its target and is not safe to
   ship.** Round 18 is the first round ever to meet a registered `violations_total`
   target — 117 → 74, p = 0.015 under the corrected bootstrap, past a threshold of
   83 registered before the round — and it rejected solely because `destructive`/
   haiku dropped the `sessions` identifier (0 of 10 → 6 of 20, reproduced at
   p = 0.026) (`round-18.md`, "Results" and "Why it rejects"). The mechanism — an
   edit that makes a bulleted `sessions.user_id → users` harder to write pushes
   haiku toward a shorter sentence — is named, not proven (n = 6). The arrow-forms
   measurement says the arrow rule is not what is failing and the clause should be
   retried rather than abandoned (`arrow-forms-across-revisions.md`, "What this
   means for #34"). *Unblocks a violations_total round.* Depends on: item 2, since
   the failure mode is the same never-cut cell.

5. **Instrument action scope, not prose, for #49.** A one-line factual question
   produced four tool calls and a file edit; laconic bounds how much prose an
   answer spends, not how many actions it takes. No current metric counts tool
   calls or edits, so there is nothing to score a rule against — the same gap #36
   describes for the arrow work. *Independent of the length loop.* Depends on: a
   new detector in the evals suite.

6. **Port to Cursor (#16), Copilot (#15), Codex (#14), and Gemini (#13).** These
   are infrastructure work against `docs/other-agents.md`'s hook-vs-static-file
   table; they touch `hooks/` and the static `rules/dist/` files, not the loop.
   *Independent of the loop.* Depends on: unblocked.

7. **Close the eval instrument gaps in #11 and #10.** #11 asks for readability
   detectors for fragments and prose abbreviations — `violations_total` already
   counts abbreviations and sentence-initial lowercase but not fragments
   (`round-18.md`, "What the violations actually are"). #10 notes the never-cut
   check covers only 50 of 80 responses. Both widen what the loop can detect
   without changing the rules. *Independent of the loop, but improves it.*
   Depends on: unblocked.

8. **Reconsider the one-edit-per-round procedure via #26.** Nineteen rounds have
   produced one step-7 pass, killed by the holdout (`LEDGER.md`), and rounds 16,
   17 and 19 each moved their target by amounts inside the noise. Multi-agent
   candidate generation (approach C) is a structural change to the loop, not a
   rules edit. *Independent of the next round.* Depends on: a decision that the
   single-edit procedure is the bottleneck, not the rule text.

## Known open questions

- **Is `Level: full` already saturated on length?** Round 19 proposes the reading
  and says nothing in the round settles it (`round-19.md`, "What that says about
  the rule").
- **Can evaluative questions (#60) be compressed at all?** The verdict cells have
  never moved under any edit the loop has tried (`round-19.md`, point 1).
- **How much of a round's rejection is gate noise?** `instrument-notes.md` finds
  the noise rejecting rounds is upstream of the judge, and that judge-verdict
  counters move ±4 to ±5 at two sigma on re-grading; the never-cut lottery cells
  (`conditional`/sonnet, `destructive`/haiku) remain the unstable gates.
- **What exactly drops `sessions`?** Round 18 names a mechanism — shorter list
  structure loses the second table — and explicitly flags it as "a mechanism, not
  a proof — n = 6" (`round-18.md`).
- **Preference is uninformative.** The judge favours the longer answer 63% of the
  time and laconic is the short arm by construction (`SKILL.md`, step 7).
- **Does the arrow enumeration ever close?** `arrow-forms-across-revisions.md`
  answers #34's relocation question in the negative — arrows do not relocate —
  but the zero-per-cell bar "remains unreached in aggregate."
