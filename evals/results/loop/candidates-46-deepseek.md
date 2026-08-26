<!-- Candidate rule edits for #46, 2026-08-22. Produced by DeepSeek through
`delegate`, in a separate worktree with no access to this session's reasoning.
Committed verbatim as received.

Neither this list nor `candidates-46-codex.md` was scored: no round names either
file, and the #46 line the loop actually ran is rounds 23 through 27. They are
recorded as the alternatives that existed at the time, not as proposals in
flight. -->

# Candidate rule edits for issue #46

Ideas for one edit per round, ranked strongest first. Every candidate is
written against the round-21 finding: laconic's design-answer quality deficit is
mediated by suppressed investigation (one-turn rate 35% vs baseline 8%,
p = 0.0052), not by shortened prose. Conditional on reading the repo, laconic
passes 6 of 6 on the three discriminating cases. So every candidate below aims
to make the model *read before it answers* a design question about code it was
pointed at, without granting the length licence that rounds 07–20 rejected and
without enumerating trigger words.

Ranking: **(1)** rewrites the self-check the model performs immediately before
sending — the one mechanism that today green-lights the from-memory answer at
the exact moment of decision; **(2)** attacks the "lead with the answer" bullet,
which is what blesses the immediate archetype; **(3)** attacks the "one
recommendation" bullet, which is what rewards the confident-but-wrong single
recommendation; **(4)** teaches by example instead of assertion; **(5)** reframes
the founding "terse" premise so compression stops competing with reading; **(6)**
removes a *disincentive* to read rather than adding a requirement, so it is the
weakest lever on the one-turn rate.

The top candidate is top because it is the only one that changes the gate the
model itself runs against its answer before it sends, so it intercepts the
zero-tool-call failure at the decision point rather than downstream in the prose.

---

## 1. Make "fully answers" read-dependent

**Text:**

```markdown
Two checks before sending:

1. What is the smallest set of claims that fully answers this? For a question
   about code the user pointed at, "fully" is decided by that code, not by
   memory of similar code: an answer that could have been written without
   opening a file of it does not fully answer it.
2. Is anything here something the user did not ask for?
```

**Where it goes:** the pre-send checks block, lines 7–10, *before* the first
`<!-- level:lite -->` marker — so it reaches every level. It is a change to
check #1 only (one added sentence), not a new check. The pre-marker is the right
slice because this is a definition of what "fully answers" means, and the two
checks are where the model decides an answer is done; placing it in a lower
section would leave ultra able to send an ungrounded answer.

**Mechanism:** the model runs "what is the smallest set of claims that fully
answers this?" against its own draft immediately before sending, and today the
archetype answer ("add Redis") passes that check because the claim set is
computed over pre-trained patterns, where no tool call is needed. Adding that
"fully" is *decided by the pointed-at code* makes the from-memory answer fail
the model's own gate, and the only way to pass is to open the files. This is
wrong if the model skips or rationalizes the check under load — it may still
assert that "add Redis" is about *this* code without having read it.

**Collateral risk:** `conditional` ("Should I raise the pool size?" — points at
`pool.log` and `db.js`) could trigger an unnecessary read, but that case is
graded on conditionality and arrow use, not on reading, so no quality harm.
`stale-cache`, `walkthrough`, `badnews` and the three `verdict-*` cases all
already name the file to read, so the check is redundant there rather than
damaging. The realistic damage is token cost from extra tool calls, not a fatal
counter.

**Prediction:** Editing pre-send check #1 should move the one-turn rate on the
eight design cases (sonnet) down.

---

## 2. Make the read the "action taken"

**Text:**

```markdown
- Lead with the answer or the action taken. Reasoning only if the user needs it
  to act on the answer. For a question about code the user pointed at, the
  action taken is the read: open the files the question is about, then answer
  from them. A recommendation that jumps straight past the read is leading with
  the wrong answer.
```

**Where it goes:** the `<!-- level:full -->` section, first bullet
("Lead with the answer or the action taken", line 90), extending that bullet in
place. It targets `full` and `ultra` only — the slice where design questions
get their compression and where the one-turn harm was measured.

**Mechanism:** "Lead with the answer" currently blesses the immediate archetype,
because "the answer" is already in the model's memory and leading with it needs
no tools. Saying the *action taken is the read* moves the tool call from an
optional afterthought to the thing that leads, so the model sequences
read-before-answer instead of answer-and-stop. This is wrong if "lead with the
answer" is not what drives the zero-tool-call behaviour — the model may skip
tools for confidence or latency reasons this sentence cannot reach.

**Collateral risk:** `decision` and `conditional` are "Should I…?" questions, so
"the action taken is the read" could add a redundant read to `conditional`
(harmless; graded on conditionality). `badnews`, `walkthrough` and `verdict-*`
already require reading and are only reinforced. `ordered-steps` has no
pointed-at code, so the guard does not fire there.

**Prediction:** Editing the "Lead with the answer" bullet should move the
one-turn rate on design-cache, design-realtime and design-upload (sonnet) down.

---

## 3. Grounding is what makes a recommendation singular

**Text:**

```markdown
- One recommendation, not a survey. A real trade-off gets one line per side,
  then a pick. For a question about code the user pointed at, the
  recommendation is what that code needs — which you know only after reading
  it; a single confident answer built from memory is still a survey of every
  codebase you have seen.
```

**Where it goes:** the `<!-- level:full -->` section, the "One recommendation,
not a survey" bullet (line 92), extended in place. Same slice as #2 for the same
reason: it is the level where design answers are compressed and where the harm
sits.

**Mechanism:** the failing response's signature is "confident, well-structured,
entirely wrong design" — precisely what "one recommendation, not a survey"
rewards. Redefining *the recommendation* as "what that code needs, which you
know only after reading it" makes the archetype answer fail the bullet it
currently satisfies, turning the model's own confidence machinery against the
from-memory answer. This is wrong if the model cannot tell "what this code
needs" from "what code like this needs," so the sentence changes nothing about
the recommendation's content.

**Collateral risk:** `decision` ("UUID or integer?") is graded on this exact
bullet but has no fixture, so the guard clause does not fire; the
"built-from-memory is still a survey" tail could push it toward *more*
commitment, which its trap wants. `verdict-*` grade "which finding decides,"
and this bullet governs options not findings (round 22); the new tail could leak
into findings and make the model name one deciding defect — which the traps
require, so the risk is naming the *wrong* defect as deciding, and `verdict-schema`/sonnet
is the cell to watch. `conditional` is the one to watch for the reverse: the
tail could push away the required two-branch conditional if misread.

**Prediction:** Editing the "One recommendation" bullet should move quality_fails
on design-cache, design-realtime and design-upload (sonnet) down.

---

## 4. A worked Wrong/Right pair for grounded vs. archetype design answers

**Text:**

```markdown
A question about code the user pointed at is answered from that code, not from
the pattern it resembles.

- Wrong: "How would weekly email digests be built?" — "A cron job plus an SMTP
  client, with a deliveries table for retries." Correct for any app; says
  nothing about this one.
- Right: "jobs/weekly.js already sends them through mailer.js; the only missing
  piece is the unsubscribe link the footer references. Add it there."
```

**Where it goes:** the `<!-- level:full -->` section, after the five bullets and
*before* the "Typical shape" line (line 98), as a new example block. `full` and
`ultra` only, alongside the rule it illustrates. The example deliberately uses a
domain (weekly email digests) that appears in no benchmark case, so it cannot
leak a fixture answer.

**Mechanism:** worked examples are the file's strongest generalizer — the OOM
table is the part of the rules the model visibly copies — and this pair teaches
the *shape* (name the file, name the single delta) instead of asserting it.
Copying that shape forces the tool call, because the "Right" line names a file
that only exists after reading. This is wrong if the model reads the pair as a
length template ("one sentence plus one file") and over-compresses a genuinely
multi-part design, or ignores it in favour of the imperative bullets above.

**Collateral risk:** the "only missing piece" shape could over-compress the five
older design cases, but those are token-scored rather than
quality-discriminating, so a shorter-correct answer does not fail a gate. `decision`
could read "says nothing about this one" as a nudge to ground, but it has no
fixture. The real watch is `walkthrough` (a multi-part explanation) — if the
exemplar reads as "one line," the requested 401 and concurrent-refresh branches
could be cut, which would be a never-cut failure.

**Prediction:** Editing level:full (the exemplar block) should move the one-turn
rate on the eight design cases (sonnet) down.

---

## 5. Terseness is a property of a correct answer

**Text:**

```markdown
**Length scales to the request, at every level.** A yes/no question gets a word
or a line. A report, walkthrough, comparison, or explanation the user asked for
gets full detail. Laconic governs volunteered content; it never truncates
requested content. Terseness is a property of a correct answer: you cannot be
terse about code you have not read, because cutting is choosing which claims
are load-bearing, and that choice is made from the code, not from memory.
```

**Where it goes:** the "Length scales to the request" paragraph (lines 12–15),
before the first level marker, appending one sentence. This is the founding
premise of the plugin, so it belongs in the pre-marker slice that every level
inherits.

**Mechanism:** the current rules make compression look like the *opponent* of
investigation — a tool call produces output the rules tell the model to trim. This
sentence reframes the premise so reading is *how you know what to cut*, removing
the meta-incentive to answer from memory. It is the least targeted candidate
because it changes the value proposition rather than any single gate; it is
wrong if the model already sees reading as compatible with terseness and the
real suppression is the "smallest set of claims" computation, which this
sentence does not touch.

**Collateral risk:** none of the fatal cases is harmed — `ordered-steps` has no
fixture, and the sentence only *adds* a reason to read where code was pointed
at. The round-wide risk is token cost if the model starts opening files on cases
where reading was never needed; that is the intended direction and not a fatal
counter.

**Prediction:** Editing the "Length scales" paragraph should move the one-turn
rate on the eight design cases (sonnet) down.

---

## 6. Evidence is not narration

**Text:**

```markdown
- No narration of tool calls the user can already see — but what a file you read
  said is not narration. When the answer rests on a file, name the file and the
  thing in it the answer depends on; that is evidence, and cutting it is not
  terseness.
```

**Where it goes:** the `<!-- level:lite -->` section, as a new bullet in the
ceremony list, after "No pleasantries or performative agreement" (line 72) and
before "No closing offers". It reaches `lite`, `full` and `ultra`, because the
narration cut it amends is itself a `lite`-level rule.

**Mechanism:** the model may avoid opening files because doing so produces the
"I opened X, it says Y" prose that "lead with the answer" and "don't narrate
tool calls" read as cutting. Explicitly protecting the *finding* removes that
disincentive — reading stops costing output tokens. This is the weakest lever on
the one-turn rate because it operates only once a file has been opened: it is
wrong if the real failure is the tool call never happening at all, in which case
there is nothing to name and the sentence changes nothing.

**Collateral risk:** `badnews` ("the output is in last-run.log") and `verdict-*`
already require naming what was read, so this reinforces them. The risk is on
`stale-cache` and `conditional`, where the model already reads and this could
lengthen the evidence recital; neither is length-gated fatally, but `conditional`
could pick up a stray arrow if the model chains "file says X -> raise Y," so
watch `violations_total` on it.

**Prediction:** Editing the level:lite narration line should move quality_fails
on design-cache, design-realtime and design-upload (sonnet) down among responses
that already read the repo (num_turns > 1).
