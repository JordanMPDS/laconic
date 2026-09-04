# Never-cut lens — arrow candidates

I read only the two files.

## What the arrows are doing

The inventory is not one habit. Sorting the lines by what sits on either side of the arrow, three shapes account for nearly all of it, and each one has protected content on at least one side.

**Shape 1 — a case and its consequence, as a bullet with no verb.** `- 401 → clears the whole store`, `- Non-401, non-ok → throws 'refresh failed: ' + status`, `- 0 rows affected → key already used`, `- Not found → do the orders insert`. This is `walkthrough` (154 + 53 lines), `cold-service` (21), `drift-service` (4), and most of `verdict-rollout` (9). It is the plurality of the whole inventory. The user asked to have this explained; the answer's mechanism is the requested content, and the arrow is precisely where the verb that carries the mechanism used to be. The bullet also stops being a sentence, which matters below.

**Shape 2 — a value transition.** `` `PAYMENTS_SETTLEMENT_MODE` → `split` ``, `` `legacy`→`split` ``. That is `confirm-rollback` (20), `deep-rollback` (17), `recall-rollback` (5): 42 lines that are almost entirely this one pattern, in the case group where the exact config values are the whole question. The never-cut rule demands those values verbatim; the arrow ban forbids the compressed carrier; the file supplies no third form, so the model keeps the values and drops the ban.

**Shape 3 — a chain of steps or causes inside a real sentence.** `rotate the key → wait out the old TTL → remove it`, `sessions → invoices → users`, `upstream gets slow → callers retry → pool exhausts`. `ordered-steps` (9), `destructive` (2), `holdout-explain` (4), the `design-*` pipelines. This is the shape the file's two existing Wrong/Right pairs already cover, and it is the smallest of the three.

So the answer to the lens question is yes, in a specific way: the arrow is a fewer-words-per-claim device, applied to content the file protects absolutely. It is not decorating a cut, it *is* the cut — and it hides it, because the line still scans as complete. The file's opening sentence ("Terse means fewer claims, not fewer words per claim") is the principle the arrow violates, and nothing in the file connects the arrow ban back to it.

---

## Candidate A — the headline scopes the ban to sentences, and the biggest violation shape is not a sentence

**The edit.** In `## Never do this`, replace this text:

> **No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
> steps, stages, states or causes, not to show that one thing maps to or becomes
> another, not after a bold label, not in a "quick runbook" line, not inside a
> quoted flow.

with:

> **No arrows anywhere in your own prose.** A bullet, a list item, a table cell,
> a heading and a bold label are all your prose; a fragment is not exempt for
> not being a sentence. Never use `→` or `->`: not to chain steps, stages,
> states or causes, not to pair a condition with what it does, not to show that
> one thing maps to or becomes another, not after a bold label, not in a "quick
> runbook" line, not inside a quoted flow.

The rest of the paragraph, the four Wrong/Right lines and the fenced-code carve-out are untouched.

**The mechanism.** The bolded headline is the scope statement, and a model reads a bolded scope statement as the rule with the rest as elaboration. It scopes the ban to sentences. `- 401 → clears the whole store` contains no sentence, so the dominant shape in the inventory has literal permission. The nearest clause that might reach it, "not to show that one thing maps to or becomes another", reads as being about mappings (`kid → public key`), not about a branch condition and what the code does in it. Adding "not to pair a condition with what it does" names shape 1 directly, and the new headline closes the fragment loophole for every surface at once.

**What it predicts.** The bullet-shaped groups fall hardest: `walkthrough` (both models), `cold-service`, `drift-service`, `verdict-rollout`. The rollback cluster and the in-sentence `design-*` chains move much less, because those arrows already sit inside sentences and the current headline already reached them.

**What would falsify it.** Bullet arrows persist at the same rate while sentence-internal arrows stay flat — that would mean the headline's scope was never what licensed them. Second falsifier, and the one I care about more: `walkthrough` responses lose the per-branch bullets instead of gaining verbs. If the 401 / non-ok / ok branches collapse into one shorter paragraph, the edit bought arrow compliance by cutting protected content, which is a worse outcome than the arrows.

---

## Candidate B — the ban is filed as a proofreading rule, so it loses to length pressure

**The edit.** In `## Never cut (every level, including ultra)`, insert a bullet immediately after the "Ordered instructions" bullet and before "Bad news":

> - The words that join one thing to the next: what causes what, which condition
>   produces which result, what happens before what. These are claims, not
>   connective tissue, and an arrow (`→`, `->`) is how they get deleted while
>   the line still looks complete.

And in the arrow paragraph under `## Never do this`, delete the now-redundant trailing sentence:

> Sequencing is where an arrow is most tempting and least
> acceptable: an ordered process is exactly the content whose connecting words
> are never cut.

so that paragraph ends at "not inside a quoted flow."

**The mechanism.** The arrow ban currently sits among dropped articles, telegraphic fragments and `impl`/`config` abbreviations — a section of things to catch while proofreading, all of which trade against the pressure to be short. `Never cut` is the only section in the file marked absolute at every level, and it is the only one about content rather than form. The arrow deletes content, so filing it under form is a category error that costs it its authority. The sentence being deleted already makes exactly this argument, but makes it as an aside at the tail of a style paragraph, where it reads as emphasis rather than as a protection; moving the claim into the protected list is what changes which decision the model consults it during.

**What it predicts.** Movement concentrated in the groups where both sides of the arrow are protected content: `walkthrough` (requested explanation), `ordered-steps` and `destructive` (ordered instructions), `verdict-rollout` and `holdout-explain` (a failure chain, which is bad news). Little movement in `design-cache`, `design-rate-limit`, `design-search` — those arrows join two options or two nouns, and nothing in the never-cut list covers them. It also predicts the effect is largest at `ultra`, since the never-cut list is most of what survives there.

**What would falsify it.** The `design-*` groups drop as much as `walkthrough`. That would mean the reclassification carried no information and the improvement is just the file saying "arrows" one more time — in which case the cheaper edit is to say it once, well, and this one is not earning its lines.

---

## Candidate C — a changed setting has no permitted prose form, so the arrow wins

**The edit.** In `## Never cut`, extend the first bullet. Replace:

> - Code, config, commands, and error strings — verbatim and complete. Never
>   abbreviate an identifier, never elide lines with `...`.

with:

> - Code, config, commands, and error strings — verbatim and complete. Never
>   abbreviate an identifier, never elide lines with `...`. A setting that
>   changed keeps both values and the word for the change: "`LOG_LEVEL` was
>   changed from `warn` to `debug`". An arrow between two values does not say
>   which one is now in effect.

**The mechanism.** In the three rollback cases the model is under two instructions at once: reproduce the config verbatim, and never write an arrow that shows one thing becoming another. It resolves the collision in favour of the protected content, because that is the one marked absolute — and the file gives it no third form to resolve it with. The fix has to land on the never-cut bullet itself, at the moment the model decides to preserve the config, rather than in the style section it consults afterwards. The arrow is also genuinely lossy here in a way the other shapes are not: `` `PAYMENTS_SETTLEMENT_MODE` → `split` `` does not say whether `split` is the old value or the new one, and every inventory line that survives does so because the surrounding prose says "triggered". The verbatim string is being asked to carry a relation it cannot express.

Use a neutral identifier, not the fixture's. Putting `PAYMENTS_SETTLEMENT_MODE` into the rule file would teach to the benchmark case rather than to the shape.

**What it predicts.** `confirm-rollback` (20), `deep-rollback` (17) and `recall-rollback` (5) collapse — 42 lines, nearly all one pattern. It predicts essentially nothing for `walkthrough`, `cold-service` or the `design-*` groups, whose arrows are not value transitions. If those move too, this bullet is not what did it.

**What would falsify it.** The rollback responses keep the arrow, or switch to `legacy->split`. And the failure mode to watch: a response that writes "the config was flipped to `split`" and drops `legacy`. That is the edit trading an arrow for a cut in the exact content the bullet exists to protect, and it would be a reason to revert rather than to tune.

---

Compatibility: A and B are independent and can ship together — A fixes which surfaces the ban covers, B fixes which section it lives in. C is orthogonal to both and addresses a cluster neither one reaches. If only one ships, A moves the most lines; B is the one that makes the ban survive `ultra`.
