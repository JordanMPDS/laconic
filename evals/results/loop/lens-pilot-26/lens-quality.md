# Lens: answer quality

I read both files and nothing else.

# Finding first: a large share of these arrows cost the reader nothing

Reading the inventory as answers rather than as violations, the 502 arrows are not one phenomenon. They split three ways, and only two of the three damage the answer.

**Free — the condition/consequence bullet.** `cold-service` (21 lines), `design-cache` (5), `drift-service` (4), `holdout-verdict` (3), and a large fraction of `walkthrough`/sonnet's 154:

    - `status = 'completed'` → replay `response_status`/`response_body` verbatim, no new order created.
    - **Not personalized** → put a CDN/edge cache in front (Cloudflare, Fastly, your LB)…
    - 4. No header → current behavior (always inserts), so the fix is additive.

This is a two-column table written on one line. The left side is a condition, fixed as such by being bolded or in a code span and by heading its own bullet; the arrow reads as "then" and cannot read as anything else. Written out — "If the status is `completed`, replay the stored response verbatim" — the answer is identical in content and marginally longer. The reader loses nothing. Same for the direction indicators in `design-realtime`: "one-directional (server → client)" and "no client→server needed" mean exactly "server to client".

**Cheap but genuinely ambiguous — the value pair.** The whole rollback family (`confirm-rollback` 20, `deep-rollback` 17, `recall-rollback` 5) is essentially one line repeated:

    the config change (`PAYMENTS_SETTLEMENT_MODE` → `split`)
    the config flip (`legacy`→`split`)

Those two are not the same relation. The first is "was set to"; the second is "changed from, to". The same symbol does both jobs within the same corpus, and a reader who does not already know the incident has to pick. Same defect in ``mapping `kid` → public key`` (`ordered-steps`), ``a small plan→limit map`` (`design-rate-limit`), ``The `DOUBLE PRECISION` → `NUMERIC` change`` (`verdict-schema`), `"head" → "headphones"` (`design-search`). Small cost each, ~51 lines, and the repair is strictly an improvement because it names the relation.

**Expensive — the multi-hop chain.** `walkthrough`/haiku (53), `ordered-steps` (9), `verdict-rollout` (9), `holdout-explain` (4), `stale-cache` (2), `conditional` (1), plus the chains inside `design-upload` and `design-retry`. Here the arrow carries the argument and does not state it:

    A typical cadence: generate new key → dual-verify period lasting ≥ max token lifetime → cut over signing → retire old key.

That is a procedure the user will follow one step at a time, compressed to one line, and the arrows have eaten the words that say the dual-verify period must *complete* before cutover. The reader cannot tell "then" from "only after". `conditional`/haiku is worse — `7 → 11 → 14 → 19 → timeout → 23 → 28` changes type mid-chain, since `timeout` is not a queue depth. And `holdout-explain`'s cascade line stakes its whole claim on causation the arrows never assert.

So: the failure the symbol is a symptom of is **an unnamed relation**, not sequencing per se. All three candidates below target that.

---

## Candidate 1 — replace the context list with a relation test

**The edit.** In `## Never do this`, replace lines 49-54 in full.

Delete:

    **No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
    steps, stages, states or causes, not to show that one thing maps to or becomes
    another, not after a bold label, not in a "quick runbook" line, not inside a
    quoted flow. Sequencing is where an arrow is most tempting and least
    acceptable: an ordered process is exactly the content whose connecting words
    are never cut.

Insert in its place:

    **No arrows inside a sentence.** Never use `→` or `->` in prose. An arrow is
    not a word. It stands in for whichever of "then", "becomes", "causes", "is
    set to", "changed to", or "maps to" you meant, and leaves the reader to
    guess which — so write the word. Two or more arrows in a row is the worst
    case: `A → B → C` asserts that each step follows from the last without
    saying whether that is order, cause, or state change, and an ordered process
    is exactly the content whose connecting words are never cut.

**The mechanism.** The current sentence enumerates *contexts* — "after a bold label", "in a quick runbook line", "inside a quoted flow" — and a context list is satisfiable by finding a context not on it. `(legacy→split)` is not after a bold label, not a runbook line, not a quoted flow, and does not look like "chaining steps"; a model checking its draft against that list clears it. The rewrite replaces the enumeration with one test the model can apply to any arrow it is about to type: name the word this replaces, then write that word instead. It also promotes the multi-hop case from a trailing remark to the named worst case.

**What it predicts.** The rollback family moves most — `confirm-rollback`, `deep-rollback`, `recall-rollback`, plus `verdict-schema`, `verdict-experiment`, `design-search`, `design-rate-limit` — because "set to" and "from … to" are the obvious replacements once the model is told to name one. `ordered-steps` and `walkthrough`/haiku move next, targeted by the chain clause. The condition bullets (`cold-service`, `design-cache`, `drift-service`) move least, since "then" is arguably already supplied by the bullet structure.

**Known cost, accepted deliberately.** Dropping "not after a bold label" removes the clause that most directly targets the condition bullets, so that group may grow. On an answer-quality reading that is the right trade: the condition bullet is the cheapest arrow in the corpus, and the clause is buying compliance where nothing is at stake while failing where something is.

**What would falsify it.** Arrow counts in the rollback cases holding flat; or the model substituting a different symbol — `PAYMENTS_SETTLEMENT_MODE = split`, or `legacy -> split` — rather than a word, which would mean the instruction was read as "avoid this glyph" and not as "name the relation". Persistent `ordered-steps` chains would also falsify, since the chain clause names that shape explicitly.

---

## Candidate 2 — add the single-arrow examples to the wrong/right list

**The edit.** In `## Never do this`, after the existing runbook pair (line 60, ending "…one at a time.") and before the paragraph beginning "Arrows belong in a fenced code block", insert:

    - Wrong: The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the 500s at 14:02.
    - Right: The config change, setting `PAYMENTS_SETTLEMENT_MODE` to `split`, triggered the 500s at 14:02.
    - Wrong: a keystore mapping `kid` → public key
    - Right: a keystore mapping each `kid` to its public key

**The mechanism.** Both existing examples are multi-arrow chains, and the sentence immediately above them says sequencing is the target. Examples fix the extension of a rule more strongly than its statement does, so a model comparing `(legacy→split)` against these two sees something unlike both: one arrow, no steps, inside a parenthesis, quoting real config values that a fenced block would be allowed to contain. Adding the single-arrow form — once as a value assignment, once as a mapping — moves the boundary onto the two shapes that actually recur.

**What it predicts.** `confirm-rollback`, `deep-rollback` and `recall-rollback` should drop sharply; those 42 lines are nearly all one instance of exactly the first example. `ordered-steps`'s two ``kid` → public key` lines and `design-rate-limit`'s `plan→limit` and `client_id→plan` should follow the second. The `walkthrough` chains should not move — the existing examples already cover them and they persist anyway.

**What would falsify it.** The rollback lines persisting after the edit. That would say the failure is not about where the model draws the rule's boundary but that the rule is not consulted at generation time at all, in which case no example placement helps and only the never-cut framing of candidate 3 has any lever.

**Note.** This can be halved to the first pair alone if you want the smaller edit; the value-assignment form is by far the higher-volume one.

---

## Candidate 3 — put the sequencing arrow in the never-cut list

**The edit.** In `## Never cut (every level, including ultra)`, replace the bullet at lines 27-28.

Delete:

    - Ordered instructions: every step, and the words that fix their order
      ("before", "after", "first").

Insert:

    - Ordered instructions: every step, and the words that fix their order
      ("before", "after", "first", "until"). An arrow is not one of those
      words: replacing them with `→` cuts the ordering, and the ordering is
      never-cut content.

**The mechanism.** The arrow ban currently lives only in `## Never do this`, alongside "write `configuration`, not `config`" — a register section, read as style. `## Never cut` is the section stated as absolute at every level including ultra, and the model demonstrably honors it, since security reasoning and destructive-action confirmations do ship. The arrow shows up precisely under length pressure, which is the pressure the never-cut list exists to resist; restating the sequencing arrow as an instance of *losing content* rather than *choosing a symbol* puts it in the category the model does not trade away.

**What it predicts.** `ordered-steps` on both models, `verdict-rollout`/haiku (numbered migration steps), `walkthrough`/haiku (numbered concurrency traces), and `holdout-explain`'s cascade. It should not touch the condition bullets or the value pairs, which are not ordered instructions — by design; this candidate targets only the group where I found real reader cost.

**What would falsify it.** `ordered-steps` arrows persisting while other groups move under a different edit. That would say section placement carries no extra authority, and the never-cut list's compliance comes from the content types it names rather than from the label on the section.

---

Candidates 1 and 3 are compatible but overlap in reasoning about chains; each stands alone. Candidate 2 composes cleanly with either.
