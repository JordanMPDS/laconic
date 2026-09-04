# Why the arrow rule fails, and three edits to the rule file

## Diagnosis

The rule is not vague. It already names, in one sentence, almost every violation
the inventory contains: chaining steps, chaining states, chaining causes, showing
that one thing maps to or becomes another, arrows after a bold label, arrows in a
runbook line. If enumeration were the fix, the file would already be fixed. So the
failure is not that the model lacks the instruction — it is that the model reads
the instruction as not applying to the line it is about to write.

Two shapes account for roughly three quarters of the 225 offending responses, and
each one has a specific escape route out of the current text.

**Shape 1: the case-and-outcome list item (~120 responses).** `walkthrough` (87),
`cold-service` (9), `verdict-rollout` (6), `drift-service` (4), `design-cache` (3),
`holdout-verdict` (2), plus bullets inside `design-alerting`, `ordered-steps` and
`design-retry`. Nearly every offending line in these groups is a list item, and a
large share puts the arrow immediately after a bold or code-span label:

    - **401** ("refresh rejected") → clears the whole store ...
    - 0 rows affected → key already used. Fetch the stored row; ...
    - Missing header → treat as non-idempotent (current behavior) ...
    - **Personalized** → cache at the app layer instead: Redis, ...
    1. Migration runs → `full_name` is dropped

The rule's headline is **"No arrows inside a sentence."** That is a scope
statement, and it is the most salient clause in the paragraph — bolded, first,
short. None of the lines above is a sentence. They are labels with glosses. The
paragraph body does say "not after a bold label", but that is instance four of
five in a mid-sentence negation list, and it contradicts the scope the headline
just set. When a stated domain and an enumerated instance conflict, fast pattern
matching keeps the domain. The rule hands the model its own exemption in its first
four words.

**Shape 2: the value transition between two code spans (~50 responses).** The
whole rollback family is one stereotyped line: `confirm-rollback` (20),
`deep-rollback` (17), `recall-rollback` (5) = 42 responses, 18.7% of the total,
and essentially all of them are

    the config change (`PAYMENTS_SETTLEMENT_MODE` → `split`)
    the config flip (`legacy`→`split`)

with `verdict-schema` (`` `DOUBLE PRECISION` → `NUMERIC` ``), `verdict-experiment`
(`2% → 2.04%`), `design-realtime`/haiku (`client→server`) and both `design-upload`
groups (`HEIC→JPEG`) doing the same thing with different material. These are not
list items, so Shape 1's escape does not explain them. Their escape is the closing
sentence: *"Arrows belong in a fenced code block or a verbatim error string, where
they are the material being quoted rather than your own prose."* The model writing
`` `legacy`→`split` `` is quoting two configuration values and believes the whole
construction is quoted material. It is not — the values are quoted, the arrow
between them is the model's own prose — but the file never draws that line, and an
inline code span sits close enough to "a fenced code block" to slide.

**A third, smaller mechanism, visible in both shapes.** Both Wrong examples in the
file show a chain: three items and two arrows. The modal violation in the
inventory is one arrow between exactly two things. A model matching its draft
against the examples sees no match and concludes the ban is about arrow *chains*.

One thing the diagnosis rules out: length pressure is not the driver. The worst
case by a factor of four is `walkthrough`, and "walk me through" is explicitly
protected by the Never-cut list, so those responses are under no compression
pressure at all. The arrow there is a notation habit for state machines and branch
tables, not a compression device. That is why none of the candidates below tries to
give the model more room; the fix is to close the scope loopholes and supply the
sanctioned notation.

---

## Candidate A — fix the scope predicate

### The edit, exactly

In `## Never do this`, in the arrow paragraph, replace the first sentence and the
words that run into the enumeration. Currently the paragraph opens:

> **No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain
> steps, stages, states or causes, not to show that one thing maps to or becomes
> another, not after a bold label, not in a "quick runbook" line, not inside a
> quoted flow.

Delete:

> **No arrows inside a sentence.** Never use `→` or `->` in prose: not to chain

Insert in its place:

> **No arrows anywhere in your own writing.** A bullet, a numbered step, a table
> cell, a heading, and the gloss that follows a bold or code-span label are all
> prose for this rule; an arrow is not permitted merely because the line is not a
> sentence. Never use `→` or `->`: not to chain

The rest of the paragraph ("steps, stages, states or causes, not to show that one
thing maps to or becomes another, …") continues unchanged, as do the Wrong/Right
list and the closing paragraph. Nothing else in the file moves.

### The mechanism

The bolded opening clause is the rule's scope statement, and "inside a sentence"
is a scope the majority of the violations genuinely fall outside — a label plus a
gloss is not a sentence, which is precisely why the model reaches for the arrow
there. The paragraph's later "not after a bold label" contradicts the headline, and
loses to it because the headline is bolded, first, and short enough to survive as
the remembered form of the rule. Replacing the predicate makes the list item the
central case rather than an exception buried in an enumeration.

### What it predicts

Down, and sharply: `walkthrough` for both models, `cold-service`, `drift-service`,
`verdict-rollout`, `design-cache`, `holdout-verdict`, and the bulleted arrows
inside `design-alerting`, `ordered-steps` and `design-rate-limit`. Roughly flat:
the rollback family, `verdict-schema`, `stale-cache`, `holdout-explain`/sonnet and
`design-audit-log`, where the arrow sits in a running paragraph and the "not a
sentence" excuse was never available. The signature of a working edit is that
differential — list-shaped groups fall while paragraph-shaped groups hold.

### What would falsify it

Total violations fall but the survivors are still mostly list items with an arrow
after a bold or code-span label. That would mean the scope predicate was never the
binding constraint and the drop came from generic salience — the same drop any
rewording of that paragraph would produce. Equally falsifying: `walkthrough` and
`cold-service` hold while the rollback family also holds, i.e. no differential
movement at all.

---

## Candidate B — close the quotation exemption

### The edit, exactly

Replace the closing paragraph of the arrow rule. Currently:

> Arrows belong in a fenced code block or a verbatim error string, where they
> are the material being quoted rather than your own prose.

Replace with:

> Arrows belong in a fenced code block or a verbatim error string, where they are
> the material being quoted rather than your own prose. An inline code span is
> neither. In `legacy` → `split` the two values are quoted and the arrow between
> them is yours; write "from `legacy` to `split`" instead. The same holds for an
> arrow fused into a term — `HEIC→JPEG`, `client→server`, `pace-error->15%` —
> unless the entire term is one code span you are reproducing verbatim.

Position is unchanged: it stays the last paragraph of the arrow rule, immediately
after the Wrong/Right list and immediately before the `<!-- level:lite -->` marker.

### The mechanism

The current sentence states an exemption in terms of a *property* — "the material
being quoted" — and then names two containers that have that property. A model
writing `` (`PAYMENTS_SETTLEMENT_MODE` → `split`) `` is quoting material, sees the
property satisfied, and takes the exemption; that its container is an inline span
rather than a fenced block is a distinction the sentence never draws. The edit
converts the exemption from a property test into a container test and states the
one substitution ("from X to Y") that the file currently supplies for chains and
runbooks but not for a two-valued transition.

### What it predicts

The rollback family collapses: `confirm-rollback` (20), `deep-rollback` (17) and
`recall-rollback` (5) are 42 responses whose offending line is almost entirely this
one construction, so this group should move further than any other under this edit.
Also down: `verdict-schema`, `verdict-experiment`, `design-realtime`/haiku,
`design-upload` for both models, and the `1s → 2s → 4s → 8s` and `7 → 11 → 14 → 19`
numeric progressions in `holdout-explain` and `conditional`. Unchanged:
`walkthrough`'s step chains and every case-and-outcome bullet, which contain no
quoted-material claim.

### What would falsify it

The rollback family holds its rate. Since 42 responses converge on the same eight
words, a rule that actually reached the model's reasoning about that line should be
visible immediately; if it is not, the arrow there is unreflective habit rather
than a rationalized exemption, and no rewording of the exemption sentence will
touch it. A second, subtler falsification: the arrow disappears and the comparison
disappears with it — the response says "the config change triggered the 500s"
without naming either value. That is content loss dressed as compliance, and it
means the edit removed the notation without the substitution landing.

---

## Candidate C — add the case-and-outcome pair to the examples

### The edit, exactly

In the arrow rule's Wrong/Right list, insert a third pair after the runbook pair.
The list currently reads:

> - Wrong: **Request A**: calls `currentToken()` → token expired → calls `refresh()`
> - Right: Request A calls `currentToken()`, finds the token expired, and calls `refresh()`.
> - Wrong: Rough runbook: rotate the key → wait out the old TTL → remove it.
> - Right: Rotate the key, wait out the old TTL, then remove it. Use a numbered
>   list instead when the user will follow the steps one at a time.

Append these two items to the end of that list, so it becomes three pairs:

> - Wrong: **401** → clears the store and throws `'refresh rejected'`.
> - Right: **401** — the store is cleared and it throws `'refresh rejected'`. A
>   bullet that pairs a case with its outcome keeps the bold label and gets a
>   verb; one arrow between two things is as banned as a chain of five.

Nothing else changes. The prose paragraph above the list and the exemption
paragraph below it are untouched.

### The mechanism

Both existing Wrong examples are multi-hop chains — three items, two arrows — while
the modal violation in the inventory is a single arrow between exactly two things,
so a model checking its draft against the examples finds no match and reads the ban
as being about chains. The new pair is the shape that actually dominates the
corpus, and its Right side supplies what the file otherwise never supplies: a
sanctioned form for the branch table, keeping the bold label the model wants and
replacing only the arrow. The trailing clause states the one-hop point explicitly,
in the same place the existing Right lines carry their generalization ("Use a
numbered list instead when…").

### What it predicts

Down: `walkthrough`/sonnet's `- **401** → …`, `- Ok → …`, `- Non-401, non-ok → …`
family; `cold-service`'s `- 0 rows affected → …`; `drift-service`'s
`- Missing header → …`; `design-cache`'s `- **Personalized** → …`;
`holdout-verdict`. Down less: `walkthrough`/haiku, whose lines are mostly the
multi-hop interleaving chains the first existing example already covers — this
edit predicts a smaller sonnet-versus-haiku gap on `walkthrough` than Candidate A
does, and that split is the cleanest way to tell the two candidates apart if both
are tried.

### What would falsify it

The case bullets keep their arrows at the same rate; or, more informatively, they
lose the arrow and grow a substitute at the same position — `- **401**: store
cleared → throws`, or `- **401** ⇒ …`, or an em dash that still fronts a verbless
fragment. Either of those means the example taught the surface form of the one
bullet shown rather than the rule behind it, and that adding examples one shape at
a time will never converge.

---

## Considered and rejected

Adding a third item to the "Two checks before sending" list at the top of the file
("does anything here use an arrow?"). It would convert a generation-time
prohibition into a review-time scan, which is mechanically cheap and would plausibly
catch all four shapes at once. I left it out because it has the weakest support in
the inventory: nothing in the data distinguishes "the model never checked" from
"the model checked and concluded the rule did not apply", and the label-and-gloss
and quoted-material escapes above are evidence for the second. A scan item that
inherits the same wrong scope predicate scans for the wrong thing.
