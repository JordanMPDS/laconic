# What the detectors do on a real session, and what that says about shipping

**Registered 2026-09-10, before any turn was scored. No rule edit, no
generation.** The audit is arithmetic over transcripts that already exist on the
operator's disk, so it spends no usage window and regenerates nothing.

## Why this exists

[#283]'s open half is a shipping decision: should the `Stop` hook of rounds 61
and 62 leave `evals/bench/stop_hook.py` and become part of the plugin?

Round 61 measured the mechanism and round 62 measured its block reason. Between
them the benefit side is settled as far as this loop can settle it, and the
answer is split:

- **On the policy it enforces it works.** Responses carrying a level-`full`
  finding fell from 12/60 (20.0%) to 1/60 (1.7%), Fisher p = 0.0020, replicated
  internally in round 62 at 1/22 within the fired stratum. Twenty rounds of rule
  edits have never moved that number this way.
- **On whether the answers are better, the blind judge cannot tell.** Null in
  round 61 at a design powered only for large harms, null again in round 62 at a
  smaller judged size. The right phrasing is `kimi`'s on `tools/consult.sh` and
  it is used throughout below: **no large quality harm was detected in two small
  studies**, which is not the same claim as no quality cost.

What neither round bought is the **cost** side, and the reason is a scope
mismatch that is easy to miss. Both rounds ran the detectors on benchmark
generations: single-turn prose answers to design and walkthrough questions, in a
fixture workspace, one turn per session. A shipped `Stop` hook fires at the end
of **every turn of a real session**, and most turns of a real session are not
prose answers at all. They are tool-call narrations, one-line acknowledgements,
diff summaries and hand-backs. Nothing has ever run these detectors on one.

A block on such a turn costs the user a whole extra generation and a wait, to
rewrite a sentence that may not have been a violation in the first place. That
rate is the number the shipping decision turns on and it has never been
measured.

## What is measured

`evals/bench/transcripts.py` reads Claude Code transcripts — `*.jsonl` under
`~/.claude/projects/`, the operator's own real sessions — reconstructs the input
a `Stop` hook would have received for each completed turn, and runs
`metrics.decisions(text, level)` on it. That is the same level-aware detector set
the benchmark scores and the same one `stop_hook.py` blocks on, so this audit
cannot measure a hook different from the one that would ship.

**The reconstruction, registered before it was run, because a denominator chosen
after seeing the rates is not a denominator:**

- A **turn** runs from a real user message to just before the next one. A `user`
  entry whose content is a `tool_result`, or which carries `isMeta`, is not a
  real user message: those are the harness talking to itself, and the CLI does
  not end a turn on them.
- The **hook input** is the last `assistant` entry in the turn that carries a
  `text` block, joined across its text blocks. This is what
  `last_assistant_message` holds. A turn whose last assistant entry has no text
  is counted separately and excluded: the CLI does not stop mid-tool-call.
- `isSidechain` entries are excluded. Subagents fire `SubagentStop`, a different
  hook, and rounds 61 and 62 measured neither.
- Entries are deduplicated on `uuid` across files. A resumed or forked session
  copies its prior history into a new transcript, so counting files
  independently would count the same turn several times, and the projects with
  the most sessions would be the most inflated.
- `never_cut_missing` **cannot fire here** and is reported as such rather than as
  a clean sheet: it needs a case's never-cut keywords and a real session has no
  case.

**The strata, registered in advance:**

- **prose-only against tool-bearing** — whether any assistant entry in the turn
  used a tool. This is the production distinction the benchmark could not make,
  because every benchmark turn is prose-only by construction.
- **by project**, so one repository's habits cannot carry the headline.
- **by entrypoint**, because some of these sessions are the loop's own unattended
  `sdk-cli` runs rather than a person typing. Those are real turns a hook would
  have blocked, and they are also not a conversation; the composition is
  reported either way.

Levels are not a stratum. Every detector in `POLICY_RANK` is rank 0 or 1 and all
of them are in force from `lite` up, so `decisions()` returns the same set at all
three levels for the same text. That is a property of today's registry, stated
here so the single-level reading is not mistaken for a scope choice.

## Predictions, registered before the numbers were looked at

1. **The block rate over all turns is below 15%.** Rounds 61 and 62 scoped
   deliberately to the highest-firing cells in the archive, and production turns
   are shorter and mostly not prose answers.
2. **`preamble` is the most frequent detector**, as it was in both rounds.
3. **Tool-bearing turns fire at a higher rate than prose-only turns.** The
   `_PRE_NARRATE` branch of the preamble detector — `I read it.`, `Found it.`,
   `Checked the schema.` — exists to catch narration of a tool call, and a
   tool-call narration can only occur in a turn that called a tool. This is the
   prediction most likely to be wrong and the one that most changes the
   decision: it is the mechanism by which a hook that behaves well on the
   benchmark could behave badly in an agentic session.
4. **Adjudicated precision on the sampled firings is at or above 70%.**

## Adjudication

A firing is a **true positive** when the rule the block would have quoted was in
fact broken by that text, judged against the verbatim `metrics.POLICY_RULE` line
and the rule's own carve-outs in `rules/laconic.md`. It is a false positive when
the detector fired on text the rule does not reach.

Sample: **40 firings, drawn at random at seed 283** from the whole corpus, no
stratification, so the sample's detector mix is the corpus's.

Both `codex` and `kimi` were asked how to keep this honest, because the person
labelling is also the person deciding whether to ship, and they disagreed.
`kimi` argued for a blind `claude -p` pass against a rubric written first;
`codex` argued that a `claude -p` labeller is not independent — it shares the
policy instincts of the thing under test and is itself an unvalidated judge —
and wanted a written rubric, de-identified excerpts and disclosure. **Both are
done and reported against each other**: the rubric above is registered here
before any firing was read, a blind pass labels each sampled firing with no
access to the detector name or to this document, and the operator labels the
same 40. Agreement is reported. Where they disagree the operator's label stands
and the disagreement is shown, because a judge whose verdicts are overridden
silently is decoration.

**The exposure is disclosed rather than solved.** The operator adjudicated their
own data and chose the bars below; the bars are registered before the labels
exist, which is the only part of that a procedure can fix.

## The decision, registered in advance

**Ship** only if all three hold:

- **Block rate over all turns at or below 5%.** `kimi`'s threshold on
  `tools/consult.sh`, adopted: above that a user disables the hook, and a
  disabled hook enforces nothing.
- **Adjudicated precision at or above 70%, with the lower bound of its 95%
  interval above 50%.** A hook that is wrong more often than it is right spends
  the user's turns on the detector's mistakes.
- **The blocks are not concentrated where a rewrite is nonsense** — a turn that
  is one line of acknowledgement, or a hand-back mid-task.

**Do not ship** if any fails. `stop_hook.py` stays benchmark instrumentation,
[#283] closes on the number, and the condition that would reopen it is named.

Either way the implementation is **not** in this unit's scope, and that is
registered here rather than decided afterwards. Shipping means detectors and the
`POLICY_RULE` table down `hooks/laconic.sh` and `hooks/laconic.ps1`, in sync with
`rules/laconic.md`, and it is a unit of its own with its own portability
question: the `preamble` pattern uses non-capturing groups and lookahead, which
bash ERE cannot express and `grep -P` cannot portably supply. `kimi` argued for
requiring `python3` at hook runtime and `codex` argued the opposite — that a
plugin with no dependencies should not acquire one, and should instead define a
**narrower portable detector and audit that exact detector rather than an
aspirational one**. That disagreement belongs to the implementation unit, and
`codex`'s framing is the one this document hands it, because a shipped hook that
is not the audited hook makes this audit worthless.

## What this cannot answer

It measures one operator, one model family, and a corpus dominated by one
repository's work. It measures the rate at which a hook would fire, not the
annoyance of being interrupted — `kimi`'s point, and correct: the block rate is a
lower bound on the friction, not an estimate of it. And it says nothing new about
benefit. The two nulls stand.

**No transcript text is committed.** The corpus is the operator's own private
sessions and this repository is public; a fragment that is the operator's to
publish can still quote a third party's code, issue title or name — `kimi`'s
hole, and the reason the report below carries aggregates and hand-written
synthetic examples only. `transcripts.py` prints excerpts only when asked and
writes nothing into the repository.

[#283]: https://github.com/JordanMPDS/laconic/issues/283
