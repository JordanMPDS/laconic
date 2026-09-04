# Compression lens — candidate edits to `rules/laconic.md`

Read both files. Here are my three candidates, as the compression reader.

---

## The reading behind all three

Every grammar protection in this file is scoped to a *sentence* or to *prose*: "No arrows inside a sentence", "Never use `→` or `->` in prose", "Do not shorten words in running prose", "Still complete sentences". The one form the `full` level explicitly licenses — "or a short list" — is named nowhere in those scopes. So the list is the unprotected channel, and word-level compression flows into it. Count the inventory: the overwhelming majority of offending lines are bullets, numbered steps, or lines after a bold label, not running sentences. The second largest idiom (the rollback trio, ~42 lines) is an arrow sitting *between two inline code spans*, which reads to a model as inside the exemption the file already grants to quoted material.

And note the asymmetry: `ultra` restates the grammar protection locally ("Still complete sentences."). `full` — the level that produced all 502 arrows — states a shape budget with no such restatement.

---

## Candidate 1 — a bullet is a sentence

**The edit.** In `## Never do this`, append one sentence to the end of the first paragraph, immediately after "Shorter is not the goal; fewer claims is."

Current:

```
No dropped articles. No telegraphic fragments. Do not shorten words in running
prose: write `configuration`, not `config`; `implementation`, not `impl`.
Shorter is not the goal; fewer claims is.
```

Becomes:

```
No dropped articles. No telegraphic fragments. Do not shorten words in running
prose: write `configuration`, not `config`; `implementation`, not `impl`.
Shorter is not the goal; fewer claims is. A bullet, a numbered step, and a
line after a bold label are sentences; every rule in this section applies to
them exactly as it does to a paragraph.
```

**The mechanism.** The arrow ban's own lead sentence is "**No arrows inside a sentence.**" and its body says "in prose" — on a literal reading, `` - `401` → clears the entire store `` is neither. The sentence is placed in the first paragraph of the section so it governs the arrow paragraph below it as well as the dropped-article rules above; one insertion brings the file's whole existing grammar apparatus onto the form where most violations live, without restating the arrow ban itself. I deliberately left "table cell" out — a real markdown table is a legitimate place for fragments, and there are no table violations in the inventory.

**What it predicts.** The condition-consequence bullet groups fall: `walkthrough`/sonnet (154 lines), `cold-service` (21), `verdict-rollout` (9), `design-cache` (5), `drift-service` (4), plus the bullet-shaped lines in `design-alerting` and `design-retry`. Little movement in the running-prose cases (`confirm-rollback`, `deep-rollback`, `stale-cache`), which were already squarely covered and violated the rule anyway.

**What would falsify it.** Bullet arrows persist at the same rate — meaning the model was never reading a scope exemption, and the driver is content density, not form; the fix would then have to be a replacement idiom for the condition-consequence line rather than a scope statement. Watch a second failure mode too: bullet arrows drop but the model stops using lists, or turns each bullet into a telegraphic fragment instead. Either means the edit shifted the compression rather than removing it.

**Apply this one first.** It has the widest reach of the three.

---

## Candidate 2 — the `full` shape line budgets claims, not words

**The edit.** In `## Level: full — also cut unrequested substance`, replace the closing paragraph.

Current:

```
Typical shape: one to three sentences, or a short list. One sentence is a
complete answer.
```

Becomes:

```
Typical shape: one to three sentences, or a short list. One sentence is a
complete answer. That budget counts claims, not the words inside one — a
question that earns eight claims gets eight lines, each written out in full,
not eight compressed ones.
```

**The mechanism.** This is the last thing a model reads before writing at `full`, and it is a length anchor stated in units of form ("one to three sentences, or a short list"). The licence that overrides it — "Length scales to the request... a report, walkthrough, comparison, or explanation the user asked for gets full detail" — is 100 lines earlier and never cross-referenced here. A model answering "walk me through how this module works" resolves the conflict the only way it can: it takes the licence on claim count (keeps all eight branches) and pays the shape budget at the word level (compresses each line). The arrow is the artifact of exactly that seam. `ultra` already carries its own local protection, "Still complete sentences."; `full` carries none, and `full` is where all 502 arrows were produced.

**What it predicts.** The heaviest movement in the many-claim cases: `walkthrough` (both models, 207 lines) and `cold-service`. Response length in those cases should go *up* slightly — that is the intended trade, and it should be measured, not treated as regression.

**What would falsify it.** Arrow rate unchanged *and* length unchanged: the model was not under a length budget, so the pressure story is wrong and only the scope story (candidate 1) survives. The other falsifier is a side effect: length rising in cases that should stay short — `conditional`, the `verdict-*` one-liners — which would mean the edit bought arrow reduction with padding, a net loss against the file's own thesis.

---

## Candidate 3 — an arrow between two quoted things is not quoted

**The edit.** In `## Never do this`, extend the paragraph that grants the exemption.

Current:

```
Arrows belong in a fenced code block or a verbatim error string, where they
are the material being quoted rather than your own prose.
```

Becomes:

```
Arrows belong in a fenced code block or a verbatim error string, where they
are the material being quoted rather than your own prose. An arrow between two
quoted things is not itself quoted: naming a change of value, a mapping, or a
conversion still needs the word — "changed from `legacy` to `split`", not
"`legacy` → `split`".
```

**The mechanism.** This is the one sentence in the file that tells a model when an arrow is legitimate, and its test is "is this the material being quoted". `` (`PAYMENTS_SETTLEMENT_MODE` → `split`) `` passes that test on a plausible reading: both operands are literal configuration values, the whole parenthetical is an annotation about data rather than an assertion, so the arrow feels like notation the model is reporting rather than prose it is writing. The edit moves the boundary to where it belongs — the spans are quoted, the gap between them is your sentence — and names the three jobs the arrow was doing there (change of value, mapping, conversion). Note this is a compression device with no verb at all to drop, which is why the "never cut connecting words" framing of the sequencing paragraph does not reach it.

**What it predicts.** The rollback trio collapses: `confirm-rollback` (20), `deep-rollback` (17), `recall-rollback` (5) are almost entirely this single idiom. Also `verdict-schema` (`DOUBLE PRECISION` → `NUMERIC`), `verdict-experiment` (`2% → 2.04%`), `design-realtime` (`client→server`), `design-rate-limit` (`client_id→plan`, `plan→limit`), `ordered-steps` (`kid` → public key), `design-upload` (`HEIC→JPEG`), `holdout-design` (`1% → 100%`). No effect at all on the sequence chains in `walkthrough`/haiku, `holdout-explain`, or `stale-cache` — those are a different mechanism and candidates 1 and 2 own them.

**What would falsify it.** The rollback cases keep the arrow. That would mean the model is not reasoning about the quoted-material exemption at all, and the idiom is pure availability — in which case the fix is a supplied replacement phrasing, not a boundary clarification.

---

## What I considered and did not propose

Adding a Wrong/Right pair for the condition-consequence bullet (`` - `401` → clears the store ``), which is the single dominant form and is not covered by either existing example pair — both current examples are running-prose or runbook lines. It is a strong candidate, but it is a different kind of change from candidate 1, and candidate 1 has to land first: an example teaches a replacement form, and there is no point teaching one while the rule still reads as not applying to bullets. If candidate 1 ships and bullet arrows persist, that example is the next thing to try.
