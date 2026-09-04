# Readability lens — candidate edits to `rules/laconic.md`

Read both files. Here are three candidates.

---

# Candidate 1 — Replace the semantic enumeration with a syntactic boundary

## The edit

In `## Never do this`, replace this paragraph exactly:

```
**No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
steps, stages, states or causes, not to show that one thing maps to or becomes
another, not after a bold label, not in a "quick runbook" line, not inside a
quoted flow. Sequencing is where an arrow is most tempting and least
acceptable: an ordered process is exactly the content whose connecting words
are never cut.
```

with:

```
**No arrows outside a fenced code block.** Never use `→` or `->` anywhere
else — not in a sentence, and not in the fragments that are not sentences: a
bullet, a numbered step, a parenthesis, a heading, a noun phrase, a bold
label. Outside a code block there is no environment where an arrow is
allowed. Sequencing is where an arrow is most tempting and least acceptable:
an ordered process is exactly the content whose connecting words are never
cut.
```

Same position, same length (62 words to 62). The two Wrong/Right bullets and the closing "Arrows belong in..." sentence are untouched.

## The mechanism

Two sentences are doing the damage. The bolded lead — **"No arrows inside a sentence."** — is the highest-salience line in the block and it scopes the prohibition to sentences. Most of the inventory is not sentences: `- Not found → do the `orders` insert`, `- 0 rows affected → key already used.`, `4. No header → current behavior`, `- Ok → parses the body`. A model can obey that heading literally and write every one of them. The surrounding section reinforces the reading: it opens "No dropped articles. No telegraphic fragments," which any style guide the model has absorbed treats as a rule about running prose, with list items conventionally exempt.

The second sentence then enumerates environments, and the inventory shows enumerated prohibitions get read as a list of the named bad cases rather than as a boundary. "Not after a bold label" is explicit, and it is violated at least a dozen times in the shown sample alone — `**401** → clears the whole store`, `**Row inserted** → you won the race`, `**Not personalized** → put a CDN/edge cache in front`, `**Same for everyone** → cache the rendered page`. Naming one more environment will not fix that; naming environments is the failure mode. One boundary — outside a fenced block, nowhere — cannot be satisfied by finding an unlisted context.

## What it predicts

The bullet-fragment and list-item groups move most: `walkthrough`/sonnet (60 responses, 154 lines), `walkthrough`/haiku (27), `cold-service` (9), `verdict-rollout` (6), `drift-service` (4), `design-cache` (3). These are dominated by a single arrow between a condition fragment and its consequence, in a list item.

It predicts much less movement on the rollback family (`confirm-rollback` 20, `deep-rollback` 17, `recall-rollback` 5), where the arrow genuinely does sit inside a grammatical sentence — `The config change (`PAYMENTS_SETTLEMENT_MODE` → `split`) triggered the initial 500s at 14:02`. Those are already covered by the current heading and are written anyway, so the scope was never what was stopping them. That group is Candidate 2's target.

## What would falsify it

Bullet-fragment arrows in `walkthrough` and `cold-service` hold at roughly their current rate. That would mean the model was never reasoning about scope at all — it does not consult the rule and reach a permissive reading, it simply reaches for the arrow when the line is a case label, and the rule text is not in play at the moment of writing. The fix would then have to be an example that matches the shape (Candidate 3), not a definition.

A weaker falsifier: total arrows drop, but the same lines come back as `-`, `=>`, `:` or `/` between condition and consequence. That is the same unreadable telegraphy with a different glyph, and it would say the boundary was drawn around the character rather than around the construction.

---

# Candidate 2 — Close the "quoted material" loophole and name the value-change form

## The edit

Replace the closing sentence of the arrow block, exactly:

```
Arrows belong in a fenced code block or a verbatim error string, where they
are the material being quoted rather than your own prose.
```

with:

```
An arrow is allowed only when it sits *inside* the quoted material: within a
fenced code block, or within the one code span or error string you are
reproducing. An arrow *between* two quoted things is your own prose, not
quoted material. "`legacy` → `split`" is a violation; write "`legacy` changed
to `split`". A value that changed, a setting that was flipped, a type that
replaced another: say it in words.
```

Same position, immediately after the Wrong/Right bullets and before the `<!-- level:lite -->` marker.

## The mechanism

The current sentence defines the exemption by a test applied to the *operands* — "where they are the material being quoted." When both sides of an arrow are code spans, that test returns true. `` (`PAYMENTS_SETTLEMENT_MODE` → `split`) `` is a quoted setting, an arrow, and a quoted value; the model has quoted material on both sides and a rule saying arrows belong with quoted material. It concludes it is transcribing a change rather than writing prose. Nothing in the file distinguishes an arrow inside a span from an arrow between two spans, and that distinction is the entire difference between reproducing something and asserting something.

The narrowing also gives the model the replacement phrasing, which the current text never does for this shape. The Wrong/Right pairs both cover chains of actions; neither covers "old value became new value," which is the single most-repeated line in the inventory.

## What it predicts

The rollback family drops hardest: `confirm-rollback` (20 responses), `deep-rollback` (17), `recall-rollback` (5). Every offending line in all three is the same construction — `(`PAYMENTS_SETTLEMENT_MODE` → `split`)` or `(`legacy`→`split`)`. That is 42 responses, roughly a fifth of the 225.

Also predicted to move: `verdict-schema` (``DOUBLE PRECISION` → `NUMERIC``), `verdict-experiment` (`2% → 2.04%`, both responses), `holdout-design` (`1% → 100%`), `holdout-explain`/haiku (`1s → 2s → 4s → 8s`, twice), `design-upload`/sonnet (`HEIC→JPEG`, twice), `design-search` (`"head" → "headphones"`).

It predicts little movement in `walkthrough`, where the right-hand side is a clause describing behavior, not a replacement value.

## What would falsify it

`confirm-rollback` and `recall-rollback` keep writing `` (`legacy` → `split`) `` at the same rate. The most likely reason would be register imitation rather than rule interpretation: the fixture is an incident write-up, and config-change notation is how incident documents are written, so the model is copying the source document's idiom and never consults the exemption sentence at all. If that is what is happening, no edit to the exemption will help — the rule would need to say something about not adopting the notation of the document you are reading.

The second falsifier is substitution: the parenthetical becomes `` (`legacy` to `split`) `` in some responses and `` (`legacy`/`split`) `` or `` (`legacy` => `split`) `` in others. Partial substitution means the edit taught the specific string, not the construction.

---

# Candidate 3 — Add a Wrong/Right pair for the single-arrow case list

## The edit

Insert a third Wrong/Right pair into the existing example list, after the bullet ending `list instead when the user will follow the steps one at a time.` and before the blank line preceding `Arrows belong in a fenced code block`:

```
- Wrong: a case list with the arrow between condition and consequence —
  "**401** → clears the store and throws", "Non-401, non-ok → throws
  `'refresh failed: ' + status`".
- Right: same bullets, with the verb restored — "A **401** clears the store
  and throws", "Any other non-ok status throws `'refresh failed: ' + status`".
  The connecting word costs one word per bullet.
```

Nothing is deleted or moved; this is an addition to the list at lines 56 to 60.

## The mechanism

Both existing Wrong examples are multi-arrow chains: `calls `currentToken()` → token expired → calls `refresh()`` and `rotate the key → wait out the old TTL → remove it`. A model checking its own output against those examples is looking for a chain. The dominant inventory shape is a *single* arrow in a bulleted case table — one condition, one consequence, no sequence — and it does not resemble either example. `- Found, hash differs → `422``, `- Missing header → skip the dedup path`, `- **Row inserted** → you won the race` are all one arrow, and a model pattern-matching against "chains are the problem" does not see itself in them.

The tail sentence addresses the model's actual motive. Under a rule whose stated logic is claim-count, the arrow reads as a legitimate compression. Stating the price — one word per bullet, not one claim — removes the justification rather than just forbidding the output.

## What it predicts

Exactly the groups whose lines are single-arrow case bullets: `cold-service` (9 responses, 21 lines, nearly all of this shape), `drift-service` (4, all four), `design-cache` (3), and the large condition-bullet portion of `walkthrough`/sonnet — lines 26 to 46 of the inventory are almost entirely `- **401** →`, `- Ok →`, `- Success →`, `- Not found →`.

It predicts nothing for `ordered-steps` or `verdict-rollout`, which are already covered by the runbook example and are violating it anyway.

## What would falsify it

Case bullets in `cold-service` and `drift-service` keep their arrows while chained sequences drop. That would mean examples are being read as a closed enumeration of forbidden shapes — the same failure the file already shows with "not after a bold label" — and adding a third example only buys the third shape. The remedy would then be Candidate 1's boundary, not more examples.

A second falsifier: the arrow disappears but the bullet stays a fragment — "**401**: clears the store and throws" or "**401**, clears the store". The tail sentence would have been read as a rule about the glyph rather than about restoring the verb, and readability would be unchanged.

---

## Note on interaction

Candidates 1 and 3 overlap on one point: both say a list item is subject to the rule. If you apply both, the phrase `and not in the fragments that are not sentences: a bullet, a numbered step` in Candidate 1 makes Candidate 3's example redundant as a *statement*, though not as a *pattern*. I would still apply both — Candidate 1 carries the boundary and Candidate 3 carries the shape — and drop nothing.

Candidate 2 is independent of the other two and targets a group neither reaches. If you can apply only one edit, apply Candidate 1: it addresses the largest number of responses and it fixes the file's structural problem (an enumeration where a boundary is needed) rather than one construction.
