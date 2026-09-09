# Round 61 — does post-hoc enforcement do what an in-context rule could not?

**Registered 2026-09-09, before any run. No rule edit.** The first round in this
loop's history that changes the *mechanism* rather than the text. `rules/laconic.md`
is byte-identical between the two arms, at `rules_cksum` 594915793.

## Why the round exists

[#268] makes the argument, and the round record is the argument. Every lever
this project has ever pulled is the same lever: `hooks/hooks.json` registers
`SessionStart` and `UserPromptSubmit`, both of which put the rules *into* the
context and then hope. Nothing measures what came out.

Rounds 44 through 53 are a wall of nulls and rejects. Round 55 shipped an edit
and round 56 then measured that it costs 7.8 points of reading rate ([#264]).
And the four standing feedback issues — [#46], [#113], [#136], [#150] — are one
observation in four costumes: a rule present in the context, unambiguous, and
not followed on a given turn. [#113] is the sharpest, because the same rule held
on the next turn, so the text was never the problem.

An in-context rule cannot fail loudly. It is either followed or it is not, and
nothing downstream can tell the two apart. A post-hoc check does not share that
property.

## The mechanism, and what had to be built for it

A `Stop` hook. Claude Code hands it the completed turn on stdin and reads a JSON
decision from stdout; `{"decision": "block", "reason": ...}` puts the reason in
front of the model as a user-role message and the model answers again. Four
facts were established against CLI 2.1.267 before the round was designed:

1. **It works under `claude -p`.** The payload carries `last_assistant_message`
   verbatim, so nothing parses a transcript. The terminal `result` becomes the
   revised text, and `num_turns` goes 1 to 2.
2. **`stop_hook_active` is true on the firing after a block**, which is how "at
   most one rewrite" is enforced rather than hoped for.
3. **Hooks do not fire under `CLAUDE_CODE_SAFE_MODE=1`** — tested both through
   `--settings` and through a project `.claude/settings.json`. `run.py` has set
   that variable on every call since the beginning, so the enforcement arm is
   ungeneratable under it.
4. **The measurement already exists.** `metrics.decisions(text, level, keywords)`
   returns the deterministic detectors that fired and are in force at that
   level, and `metrics.POLICY_RULE` maps each to the verbatim line of
   `rules/laconic.md` it implements. So the hook cannot enforce a rule the loop
   does not measure, or measure one it does not enforce, and it is monotone
   across the three levels by construction ([#269]).

`evals/bench/stop_hook.py` is the hook. It is benchmark code: nothing under
`hooks/` calls it and no `hooks.json` registers it. [#268] says the round can be
bought before the shipped bash and PowerShell paths are written, and that is
deliberate — the two-path sync burden is the cost of *shipping* the idea and
should be paid after a round says the idea is worth shipping.

## The arms

Both generated in one interleaved pass, arms innermost, so they are sampled at
adjacent moments and no CLI release can correlate with an arm.

| arm | rules | Stop hook | safe mode |
|---|---|---|---|
| `laconic` | shipped `full` slice | none | **off** |
| `laconic-enforced` | the same text, from the same hook call | fires once | **off** |

**Safe mode is off on both, and this is the round's one concession.** It has to
be off for the treatment, because hooks do not run under it. It is therefore off
for the control too: safe mode differing between the arms would confound the
mechanism with the regime, which is the one thing the round cannot afford. All
three consulted targets said the same thing independently, and all three also
said not to buy a third `laconic`/safe-mode-on arm to measure safe mode itself —
it answers a different question and 10 reps would not characterise it. The cost
is that **this round's absolute rates are not comparable with the archive's**,
which is why `run.py` now records `metadata.safe_mode` and it is false here.
`--no-safe-mode` applies to a whole pass, and an arm carrying a hook without it
is refused rather than generated as a silent second copy of its own control.

## Scope, chosen from measured failure rates

The round goes where the rules demonstrably fail today. Scanning every stored
run of the `laconic` arm at the current `rules_cksum` for a level-`full`
detector finding:

| cell | rate under the shipped rules |
|---|--:|
| `walkthrough`/haiku | 15/15 (100%) |
| `fail-open`/haiku | 7/16 (44%) |
| `walkthrough`/sonnet | 5/15 (33%) |
| `design-upload`/haiku | 4/16 (25%) |
| `design-upload`/sonnet | 47/286 (16%) |

Those three cases, on haiku and sonnet, **10 reps a side**: 120 generations plus
one delivery probe, then 120 judgments. Each carries a different question.
`walkthrough` is safety-graded on a never-cut contract — the answer must keep
the 401 path — so it is where a forced rewrite can do real harm. `fail-open` is
quality-graded against a fixture that has to be read. `design-upload` is a
design case and carries [#264]'s reading-rate axis.

## Registered endpoints

**Primary, and the decision endpoint: the blind judge.** `quality_fails` and
`safety_fails`, treatment against control, over all 120 runs — intention to
treat, not conditioned on whether the hook fired. Conditioning would discard
exactly the harms the mechanism's own selection and rewrite cause. This is the
primary because the detector rate is not: the hook fires on the same detectors
the round would score, so "violations fell" is close to guaranteed and close to
meaningless. All three targets said to demote it and all three were right.

**Secondary, matched: the fired stratum.** Treatment responses the hook blocked,
against control responses on which the same detector set fired. Same violation
profile, one rewritten and one not. The arm-level contrast above is unbiased but
dilutes the effect across responses the mechanism never touched; this one is the
mechanism's own effect and is confounded by selection. Both are reported.

**Mechanism readings, not gates:**

- **Fire rate** — the share of treatment responses blocked, which is the extra
  token cost the mechanism charges.
- **Revision success** — of the blocked responses, the share that came back with
  no finding at all. Reported with an exact binomial interval, and *no threshold
  is pre-registered as success*: at 10 reps a side, even 0 residual failures in
  15 fires only bounds the true rate near 18% by the rule of three. If too few
  responses fire, the reading is uninformative rather than positive.
- **Named against unnamed residual.** The block quotes exactly **one** rule, the
  lowest-ranked detector that fired. So a residual scored per detector separates
  two outcomes that a single pooled rate cannot: if the detectors that were
  present but *not* named also clear, the revision generalised; if only the
  named one clears and the rest survive, the model moved the violation rather
  than clearing it. This is deepseek's design and it is why one rule is quoted
  rather than all of them.
- **Reading rate**, from the per-run `tools` list ([#142]) and not from
  `num_turns`. A blocked response has `num_turns` >= 2 by construction, so
  `one_turn` and `turns` are destroyed in this arm and are not read. Defined
  narrowly in advance: whether a fixture file was opened, not whether any tool
  ran.
- **Final `output_tokens`**, inside the reading stratum ([#131]). Descriptive:
  it is a post-treatment stratification and not a causal estimate.

## Where the design came from

`bash tools/consult.sh` was run against all three delegate targets before
anything was built, and all three answered. What was adopted, and from whom:

- **Safe mode off on both arms, no third arm** — unanimous (codex, deepseek,
  kimi). Adopted.
- **The judged endpoint is primary and the detector rate is a manipulation
  check** — unanimous. Adopted; it was not what the round was leaning towards.
- **The fired-stratum comparison against control responses where the same
  detector fired** — deepseek. Adopted as the matched secondary. codex argued
  the opposite, that the judge must not be conditioned on firing; both are
  right about different estimands, so both are reported and the unconditioned
  one decides.
- **Quote one rule and score named against unnamed residuals** — deepseek.
  Adopted. codex argued for quoting every fired rule as closer to a deployed
  contract; the single quote is kept because it buys the "moved or cleared"
  discrimination inside this round rather than needing a second one.
- **Store the pre-revision text and the per-firing record** — codex. Adopted:
  without it, "the hook prevented a failure" and "the hook never fired" are
  indistinguishable in the snapshot.
- **Probe that the hook is actually delivered before spending the pass** —
  deepseek, reasoning from the `concise-style` precedent. Adopted as
  `run.py`'s `stop_hook_reaches_model`.
- **Exact binomial intervals, and no pre-registered residual threshold** —
  codex. Adopted.
- **Not adopted:** kimi argued for a detector-neutral block reason ("you broke a
  rule, find it"), on the grounds that naming the rule tests
  enforcement-as-instruction rather than enforcement-as-reminder. That is a real
  distinction and the round goes the other way for codex's reason: a null under
  vague feedback cannot distinguish a weak mechanism from underspecified
  feedback, and #268 says a null here is worth buying. The reminder-only variant
  is the natural follow-up round on the same cells.

## What this round cannot answer

It scores a syntactic policy proxy and a blind judge on three cases. It can
answer whether one deterministic post-hoc revision clears already-contextualised
rule violations in the cells where the rules fail most, without visible quality
or safety damage. It cannot answer whether post-hoc enforcement generally solves
this project's rule-following problem, and no result below should be read that
way.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#268]: https://github.com/JordanMPDS/laconic/issues/268
[#269]: https://github.com/JordanMPDS/laconic/issues/269
