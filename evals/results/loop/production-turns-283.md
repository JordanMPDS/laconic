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

## Result: the hook does not ship

**1,429 turns from 133 sessions across 17 projects, 2026-08-06 to 2026-09-10,
scored at level `full`. 681 turns ended on a tool call rather than on text and
are excluded, as registered — 311 `sdk-py`, 280 `cli`, 90 `sdk-cli`.**

**Block rate: 93/1,429 (6.5%), 95% [5.3%, 7.9%].** One turn in fifteen would
have been blocked, and each block costs the user a whole extra generation.

| detector | turns it fired on | share of all turns |
|---|--:|--:|
| `symbol_connectors` | 37 | 2.6% |
| `closing_offers` | 32 | 2.2% |
| `sentence_initial_lowercase` | 24 | 1.7% |
| `preamble` | 2 | 0.1% |
| `abbreviated_prose` | 0 | 0.0% |

`never_cut_missing` cannot fire without a case's keywords and is not a clean
sheet.

| stratum | turns | blocked |
|---|--:|--:|
| tool-bearing | 1,105 | 81 (7.3%) |
| prose-only | 324 | 12 (3.7%) |
| 200+ words | 420 | 54 (12.9%) |
| 60 to 200 words | 398 | 29 (7.3%) |
| 20 to 60 words | 203 | 3 (1.5%) |
| under 20 words | 408 | 7 (1.7%) |
| `cli` entrypoint | 947 | 70 (7.4%) |
| `sdk-cli` entrypoint | 479 | 23 (4.8%) |

Per project the rate runs from 4.4% (this repository, 926 turns) to 13.4%
(`spendid`, 67 turns); the four projects with fewer than ten turns are noise and
are in the raw output rather than here.

### The predictions

| # | prediction | read |
|---|---|---|
| 1 | block rate below 15% | **held** — 6.5% |
| 2 | `preamble` is the most frequent detector | **failed** — it is the rarest that fires at all, 2 of 93 |
| 3 | tool-bearing turns fire higher than prose-only | **held, mechanism wrong** — 7.3% against 3.7%, but not through the narration branch it named |
| 4 | adjudicated precision at or above 70% | **failed** — 62.5% by hand, 50.0% blind |

**Prediction 2 is the substantive one and it inverts the benchmark.** Round 62's
`named` arm blocked on `preamble` 16 times and on `symbol_connectors` 6; in
production the ratio is 2 to 37. The benchmark's cells were `walkthrough` and
`fail-open`, where a model opens with `Here's the token refresh flow:`. Real
turns report work already done, and what they carry is an arrow between two
states, a closing offer, or a telegraphic status line. **A mechanism validated
almost entirely on preamble would, in production, spend 98% of its blocks on
rules it has never been measured enforcing.**

Prediction 3 held in direction and not in mechanism, which is worth saying
plainly rather than counting as a hit: the registration attributed the excess to
the preamble detector's tool-narration branch, and that branch fired twice in
1,429 turns. The excess is `symbol_connectors` and `sentence_initial_lowercase`
on turns that report finished work.

### Adjudication: 40 firings, drawn at seed 283, two readings

| reading | called a real violation | 95% |
|---|--:|---|
| hand | 25/40 (62.5%) | [47.0%, 75.8%] |
| blind `claude -p`, sonnet | 20/40 (50.0%) | [35.2%, 64.8%] |

**Both are below the registered bar of 70%, and both lower bounds sit at or
below 50%.** They agree on 27 of 40, Cohen's κ = 0.350, and the aggregate
closeness hides the fact that they disagree systematically and in opposite
directions per detector:

| rule the block would quote | firings | hand | blind |
|---|--:|--:|--:|
| `symbol_connectors` | 18 | 16 (89%) | 8 (44%) |
| `closing_offers` | 13 | 6 (46%) | 9 (69%) |
| `sentence_initial_lowercase` | 9 | 3 (33%) | 3 (33%) |

The `sentence_initial_lowercase` row agrees on the count and not on the items:
two disagreements cancel.

**Where they split is where the rule is undecided, and both splits are
substantive rather than sloppy.**

- **The arrow.** Sixteen of the eighteen arrows are in a markdown table cell, a
  UI breadcrumb (`Settings → Branches → Require status checks`), or after a bold
  label (`**Panel frames 2 → 1.**`). The rule prohibits an arrow "inside a
  sentence" and then lists "not after a bold label, not in a 'quick runbook'
  line" — so the hand reading calls them violations by the list and the blind
  reading clears them by the headline. Round 62 met this once, in the heading its
  single `named` residual left an arrow in, and called it a detector-scope
  observation. **In production it is not an edge case: it is the modal block.**
- **The closing offer.** Seven of the thirteen are the carve-out — *"Asking the
  user to confirm a destructive action is never a closing offer"*. `Want me to
  merge #99 and #100 once #100's checks land?` is authorisation for a production
  merge, not an offer of extra work, and two of the seven are the phrase
  appearing inside a quotation the answer is analysing. The detector cannot see
  the difference; the hand reading applied the carve-out and the blind reading
  mostly did not.
- **The lowercase sentence.** Six of the nine are not degraded grammar at all:
  two are lowercase proper nouns starting a sentence (`laconic is 84%, tied
  with…`, `mechanics-review was responding to…`), three are a sentence split at
  a false boundary, and one is the whole reply `ok`. This is the detector the
  audit reads worst on, and it is a grammar *proxy* — quoting its rule at a user
  tells them they dropped an article when they capitalised a product name.

### The decision, against the bars registered above

| bar | registered | measured | |
|---|---|---|---|
| block rate | ≤ 5% of turns | **6.5%**, 95% [5.3%, 7.9%] | **fails** |
| precision | ≥ 70%, lower bound > 50% | **62.5%** hand [47.0%, 75.8%], 50.0% blind | **fails** |
| not concentrated where a rewrite is nonsense | — | 1.7% on turns under 20 words, 12.9% on turns over 200 | **holds** |

**Two of three fail, so the hook does not ship.** `evals/bench/stop_hook.py`
stays benchmark instrumentation, and [#283] closes on this number.

The third bar holding is the part worth keeping: the worry that drove it — a
hook interrupting a one-line acknowledgement to rewrite it — is not what the
data shows. Blocks land on long answers, which is where the rules are about
something. The mechanism fails on precision and volume, not on absurdity.

**What would reopen it**, named here so a later round does not have to invent
it: a fire set restricted to detectors with a *measured production* precision
above the bar, re-audited on this corpus before shipping rather than after.
Nothing here licenses assembling that set post hoc from the table above — three
detectors at n = 9 to 18 on one operator's transcripts is a reason to measure
again, not a ranking to ship. And the two readings disagree most on exactly the
detector that would carry such a set.

### What this changes about the benefit half, which is nothing

Rounds 61 and 62 stand as they are. The mechanism clears what it names, no
large quality harm was detected in two small studies, and neither of those
claims is touched by a corpus that contains no arms. What the audit changes is
the population those claims are about: **the benchmark measured the hook on the
violation it almost never meets in production.** A round wanting to license
shipping would have to be scoped to the production mix — arrows in tables and
breadcrumbs, closing offers next to their carve-out — and both of those are
places where the rule itself is what needs deciding first.

`kimi`'s framing on `tools/consult.sh` deserves recording, because it is the
strongest argument against the way this document was set up and it survives the
result: compliance is the mechanism and not the outcome, so a mechanism with no
measured outcome benefit is evidence that the mechanism misfires or the rules
are wrong, not that the judge measured the wrong thing. The audit is consistent
with that reading. Half of these blocks would have been the rules misfiring.

### Disclosures

**The reconstruction was corrected once, mid-audit, and the first labels were
discarded.** The first implementation took the last text-bearing assistant entry
in a turn rather than the last entry, which the registration above already ruled
out in as many words. It scored the opening line of turns that were cut short
after a tool call — an agentic turn opens with `I'll start by reading the
backlog.` — and it read 13.5% over 1,824 turns with `symbol_connectors` at 144
and `preamble` at 49. Correcting it to the registered rule removed 681 turns,
including 311 structured-output agent turns that end every turn on a tool call,
and halved the rate. A sample of 40 had already been drawn and blind-judged
under the wrong denominator; it was discarded, the sample redrawn at the same
seed from the corrected population, and every number above is from the second
draw. **The uncorrected figure is stated here rather than dropped**, because the
two differ by a factor of two and a reader deciding how much to trust the
denominator is entitled to see what it was sensitive to.

**One operator, one model family, one dominant repository.** 926 of 1,429 turns
are this repository's own work, and every session ran under the operator's
`CLAUDE.md` as well as the plugin's rules. A different user writes differently
and a different corpus would read differently.

**The hand labels and the design are the same author.** The bars were registered
before the labels existed, which is what a procedure can fix; that the labeller
also wanted an answer is disclosed and not fixed. The blind pass is a partial
check and `codex` is right that it is not an independent one — it is a model
from the same family as the one whose turns are being judged.

**The blind pass sent 40 sampled replies to the API.** They are the operator's
own text and they were generated in sessions that already ran against it. No
transcript text is in this document or anywhere in the repository, and
`transcripts.py` writes a sample only to a path it is told to use.

**One thing this measured is a fact about a hook, not about the loop's
scoring.** These detectors were validated as scorers of benchmark responses and
the audit says nothing against that. What it says is that scoring an arm and
blocking a user's turn are different jobs, and a precision that is adequate for
the first is not automatically adequate for the second.
