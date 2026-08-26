<!-- Candidate rule edits for #46, 2026-08-22. Produced by Codex through
`delegate`, in a separate worktree with no access to this session's reasoning.
Committed verbatim as received.

Neither this list nor `candidates-46-deepseek.md` was scored: no round names
either file, and the #46 line the loop actually ran is rounds 23 through 27.
They are recorded as the alternatives that existed at the time, not as
proposals in flight. -->

# Candidate edits for issue #46

These are ranked strongest first. The top candidate is top because it makes
investigation the shortest route to the existing `full`-level promise of one
recommendation, without putting an obligation in a protected every-level list.

## 1. Make a repository-grounded recommendation the compact form

**Exact text to add**

```markdown
- Before recommending a design for code you were pointed at, inspect the
  smallest relevant evidence and make the recommendation from it. A generic
  answer is not a recommendation.
```

**Where it goes.** Add this in `## Level: full — also cut unrequested
substance`, immediately below “One recommendation, not a survey. A real
trade-off gets one line per side, then a pick.” It targets the `full` and
`ultra` slice: the measured failure is at the default `full` level, and this is
an instruction about how to satisfy that section's recommendation constraint,
not an every-level licence or obligation.

**Mechanism.** This may make the model treat a convention-based answer as an
incomplete recommendation when the prompt supplies code context, while
“smallest relevant evidence” keeps the investigation narrow enough that it
competes with, rather than defeats, compression. It is materially different
from the round-16 wording because it gives the model a completion criterion
(the recommendation must be from evidence) instead of merely describing the
survey symptom.

**Collateral risk.** `decision`, `conditional`, and the three `verdict-*` cases
could acquire unnecessary repository inspection before an answer that is
already decidable from the prompt; `walkthrough` could also lose clarity if a
model mistakes a request for explanation for a request to investigate.

**Prediction.** Editing `Before recommending a design for code you were pointed at, inspect the smallest relevant evidence and make the recommendation from it.` should move `one-turn rate` on `design-cache`, `design-realtime`, and `design-upload` downward.

## 2. Add a falsification check before a code-derived answer is sent

**Exact text to add**

```markdown
- Before sending an answer about code you were pointed at, ask whether a file
  could contradict its decisive claim. If it could, check the smallest file
  that would settle it.
```

**Where it goes.** Add this in the `full` section immediately below “Lead with
the answer or the action taken. Reasoning only if the user needs it to act on
the answer.” It targets `full` and `ultra` because it is a readiness test for
an answer, not a protection for content; placing it before the `full` marker
would needlessly require this check in `lite` interactions.

**Mechanism.** The discriminating fixtures are adversarial specifically to the
model's first, generic answer, so a counterexample-oriented check may interrupt
confident recall more reliably than a generic imperative to read first. This
could be wrong if models do not operationalize “could contradict” as a tool
call, or if they check an irrelevant file and retain the first answer anyway.

**Collateral risk.** `badnews`, `silent-success`, and `floor` may prompt a
search for a contradiction even when the visible failure output is sufficient;
`destructive` may add reads but should not displace its already protected schema
inspection.

**Prediction.** Editing `Before sending an answer about code you were pointed at, ask whether a file could contradict its decisive claim.` should move `one-turn rate` on `design-cache`, `design-realtime`, and `design-upload` downward.

## 3. Preserve decisive investigation as requested substance

**Exact text to add**

```markdown
- A fact from code you were pointed at that decides the recommendation is not
  unrequested context; use it instead of a generic design pattern.
```

**Where it goes.** Add this in the `full` section immediately below “No
unrequested alternatives, no \"you could also\".” It targets `full` and `ultra`
because it narrows the local instruction that can make a model omit the
repository fact it would need to investigate, without expanding the every-level
“Never cut” list.

**Mechanism.** The two pre-send checks and the `full` ban on unrequested
substance plausibly frame repository-specific context as optional detail. This
line may reverse that local incentive: finding one decisive fact becomes a way
to remove alternatives and claims, not permission to add an explanation. This
could be wrong if the omission pressure acts before the model considers tools.

**Collateral risk.** `code-fidelity` and `walkthrough` could become more verbose
by treating too many implementation details as decisive; `ordered-steps` could
receive an irrelevant fact before its protected sequence.

**Prediction.** Editing `A fact from code you were pointed at that decides the recommendation is not unrequested context; use it instead of a generic design pattern.` should move `one-turn rate` on `design-cache`, `design-realtime`, and `design-upload` downward.

## 4. Clarify that concise tool-call narration does not mean avoiding tools

**Exact text to change**

```markdown
No preamble. Do not restate the question, announce what is about to happen, or
narrate tool calls the user can already see; make needed calls before answering.
```

**Where it goes.** Replace the two-line opening paragraph of `## Level: lite —
cut ceremony` with this text. It targets the `lite`, `full`, and `ultra` slice
because the present wording is the only explicit mention of tool calls and may
be misread as a discouragement that follows into every level. That broad reach
is intentional here, but is also why this candidate ranks below `full`-only
edits.

**Mechanism.** The model may collapse “do not narrate tool calls” into “do not
make tool calls” while optimizing for a direct first message. Adding an explicit
distinction supplies a different causal lever from the earlier read-first rule:
it removes a possible negative cue rather than adding another obligation. This
could be wrong because the line governs visible prose, not internal action
selection.

**Collateral risk.** This directly risks issue #49's failure mode on `decision`,
`conditional`, and `floor`: a model may make gratuitous calls or edits merely
because it can call them silently. It could also slow simple `badnews` and
`silent-success` answers.

**Prediction.** Editing `narrate tool calls the user can already see; make needed calls before answering.` should move `one-turn rate` on `design-cache`, `design-realtime`, and `design-upload` downward.

## 5. Make “lead with the answer” depend on what establishes it

**Exact text to change**

```markdown
- Lead with the answer or the action taken, and with the repository fact that
  establishes it when the user pointed you at code. Reasoning only if the user
  needs it to act on the answer.
```

**Where it goes.** Replace the first bullet in `Level: full` with this text. It
targets `full` and `ultra`: it changes the existing instruction most likely to
reward immediate answering, while preserving the same section and its
compression budget.

**Mechanism.** “Lead with the answer” may privilege producing a polished answer
in the first assistant turn. Requiring the decisive repository fact in that
lead reframes a file read as part of the answer's minimum claim set, rather than
as optional supporting reasoning. This could be wrong if it makes models invent
file facts instead of opening files.

**Collateral risk.** `code-fidelity` is exposed to invented or overly specific
file references; `destructive` and `stale-cache` may front-load implementation
detail before the user can act; `verdict-schema` may become less clear if a
single fact crowds out the requested evaluation.

**Prediction.** Editing `Lead with the answer or the action taken, and with the repository fact that establishes it when the user pointed you at code.` should move `num_turns` on `design-cache`, `design-realtime`, and `design-upload` upward.

## 6. Forbid unanswered forks that the repository already resolves

**Exact text to add**

```markdown
- Do not hand a design decision back to the user when the code you were pointed
  at can resolve it; inspect that constraint, then make the pick.
```

**Where it goes.** Add this in the `full` section immediately below “No
unrequested alternatives, no \"you could also\".” It targets `full` and `ultra`
because it is a constraint on the section's one-recommendation behaviour. It
must not go in “Never cut”: that location turned the earlier design licence
into a leak affecting ordered procedures.

**Mechanism.** The round-16 strata show that answers which hand the decision
back got worse even as resolving answers improved. This wording attacks that
observable failure mode directly, but differs from its predecessor by making
the prohibited act—not a survey—the focus and by connecting it to a concrete
next action. It could be wrong if models cannot tell which fork the repository
can settle without already having inspected it.

**Collateral risk.** `conditional` and `decision` can legitimately require a
user preference, so the model may overclaim; `design-alerting` and
`design-audit-log` may receive a premature pick where their prompt leaves a
real product decision open.

**Prediction.** Editing `Do not hand a design decision back to the user when the code you were pointed at can resolve it; inspect that constraint, then make the pick.` should move `quality_fails` on `design-cache`, `design-realtime`, and `design-upload` downward.
