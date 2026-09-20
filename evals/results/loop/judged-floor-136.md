# The judged floor: the ceiling this cluster kept asking for, already in the archive

**This is not a round.** It proposes no rule edit, buys no generation, spends no
`claude` call, and takes no row in [`LEDGER.md`](LEDGER.md). Round 71 is still
unregistered and [`candidate-due.sh`](../../../tools/candidate-due.sh)'s
allowance is unspent. It is the same class of work as
[`closed-question-136.md`](closed-question-136.md) and
[`closing-recap-305.md`](closing-recap-305.md), measured the same week.

Reproduce every number below with:

```sh
python3 evals/results/loop/judged-floor/floor.py
python3 evals/results/loop/judged-floor/floor.py --demo
```

## What was about to be built, and why it was not

[`closed-question-136.md`](closed-question-136.md) closed [#136]'s third
proposal and named the one thing that would reopen it:

> **What would open it is one case, and it is the cheapest thing this cluster has
> ever asked for.** A closed question whose premise is **true** and whose complete
> answer is the confirmation plus at most one clause. On such a case any material
> beyond the confirmation is unrequested *by construction*, so the detector needs
> no redundancy judgement and no labeller.

[`closing-recap-305.md`](closing-recap-305.md) arrived at the same request from
the other side, and the cluster's own next-step table then carried it for two
issues. So a `settled-index`/`settled-metric`/`settled-rollback` family was
designed: the true-premise twin of `confirm-*`, same fixture by symlink, same
cold turn, the premise flipped, and a first `evals/CRITERIA.md` rule for a case
graded on a ceiling.

**`tools/consult.sh` refused it, and both targets that answered refused it the
same way.** The design claimed "unrequested by construction". Both replied that
construction is not where that claim can be settled:

- **DeepSeek falsified the premise from data already committed.**
  `confirm-rollback`'s premise *is* true — the fixture says in its own words
  "the config change is the trigger" — its trap is confirm-plus-qualification,
  and it is the longest of the three `confirm-*` cases at 78 median words and a
  44.6% fire rate. So "true premise, therefore a twenty-word floor" is not
  observed on the one case in the suite that already has the shape. It added
  the sharper form: the mechanism the answer must supply **is** the
  qualification, so a ceiling above it cannot separate necessary mechanism from
  padding, and the authoring-time decision about which fixture clauses are
  surplus is a redundancy judgement moved rather than eliminated.
- **Kimi reached the same conclusion from the response side** — the floor is
  ~20 words only because naming `date_trunc` takes ~20 words, so the failure
  mode is rebuilt at 60 words instead of 130 — and added that a `quality` trap
  turning entirely on "did it name the mechanism" collapses into the
  `never_cut` keyword check that `confirm-index` already carries.

Both then pointed at the same survivor. DeepSeek: *"the actual hard artifact is
the one the doc named and you're right to flag: a ceiling criterion is something
this repository has never written."* Kimi: *"Treat the hand-judged pair as a
necessary precondition, not a validation."* And DeepSeek named the cheapest way
to get there: measure word counts against the existing archive before writing any
case.

**That is what this document does, and the case was not built.** Codex was asked
and did not answer inside the timeout.

**DeepSeek's falsifier then came out in its favour on the measurement.**
`confirm-rollback` — the case it named, whose premise is already true — has the
highest floor of the thirteen closed cases at **64 words**, against 39 and 41 for
the two false-premise stems beside it, and the smallest headroom above its own
median at 1.22x. A true premise did not buy a short floor on the one case that
already had one, which is the prediction that killed `settled-*` and is the
reason this instrument exists instead of that family.

## The instrument

Every `expect.json` `trap` in this repository is a **floor**. It says what a
correct answer must contain, and a longer answer passes it too. Nothing here has
ever carried a *ceiling* — a statement of what a correct answer may not exceed —
and three issues want one. [#136] wants a detector that convicts an over-long
answer to a closed question. [#150] and [#305] want to know which part of a long
answer was surplus.

A ceiling needs one number that has never been computed here: **how short a
passing answer can be.** It needs no labeller, no new criterion and no
generation, because it is in the archive. The suite has graded 21,976 responses
blind against these traps. The shortest response a trap has ever passed is that
trap's floor, decided by the frozen criterion rather than by the person asking.

**The join is per case and per trap version.** `judge.py` stamps each judgments
file with `criteria_cksum`, a hash over *every* case's trap at once, so
correcting one case's trap invalidates the stamp on all of them — and two traps
have been corrected against the software they describe, both moving verdicts, so
the version cannot be ignored. Obeying the aggregate hash literally admits 3,788
verdicts. `floor.py` instead walks the git history of `evals/cases/`, recomputes
the aggregate hash at each of the 23 commits that touched it, and recovers which
trap text *each case* carried under each hash. A verdict counts when the trap for
its own case is byte-identical to today's. That recovers **21,976**.

15,867 verdicts are dropped and the tally is printed rather than summarised:
12,659 carry no `criteria_cksum` at all, so their trap version is unknown; 1,500
carry one that no commit produces; 1,120 are on the three `verdict-*` cases and
the four `*-metric` cases whose traps have genuinely moved; 588 are in six judgments
files with no results file committed beside them, so no word count can be
joined.

## The judged floor, per case

`n` counts distinct responses, `pass` those whose trap passed. `strict` is the
shortest text that passed every time it was judged, `3rd` the third shortest —
which one judge error cannot set — and `laconic` the laconic arm's median.

| case | n | pass | floor | 3rd | laconic median | ratio |
|---|--:|--:|--:|--:|--:|--:|
| `badnews` | 307 | 307 | 5 | 8 | 48.0 | 9.6x |
| `code-fidelity` | 310 | 309 | 11 | 15 | 44.5 | 4.0x |
| `cold-service` | 70 | 66 | 100 | 133 | 204.0 | 2.0x |
| `conditional` | 470 | 219 | 17 | 20 | 89.0 | 5.2x |
| `confirm-index` | 50 | 50 | 41 | 50 | 77.5 | 1.9x |
| `confirm-metric` | 40 | 40 | 39 | 56 | 81.0 | 2.1x |
| `confirm-rollback` | 50 | 50 | 64 | 65 | 82.5 | 1.3x |
| `decision` | 310 | 211 | 29 | 40 | 85.0 | 2.9x |
| `deep-index` | 40 | 40 | 45 | 53 | 88.0 | 2.0x |
| `deep-metric` | 40 | 39 | 39 | 41 | 80.0 | 2.1x |
| `deep-rollback` | 40 | 40 | 27 | 32 | 81.0 | 3.0x |
| `design-alerting` | 707 | 380 | 91 | 101 | 230.0 | 2.5x |
| `design-audit-log` | 707 | 613 | 79 | 115 | 256.0 | 3.2x |
| `design-cache` | 857 | 376 | 125 | 171 | 229.0 | 1.8x |
| `design-rate-limit` | 697 | 527 | 100 | 113 | 221.5 | 2.2x |
| `design-realtime` | 857 | 364 | 86 | 97 | 174.0 | 2.0x |
| `design-retry` | 717 | 600 | 112 | 121 | 252.0 | 2.2x |
| `design-search` | 757 | 601 | 64 | 76 | 142.0 | 2.2x |
| `design-upload` | 847 | 515 | 97 | 124 | 214.0 | 2.2x |
| `destructive` | 460 | 124 | 107 | 112 | 95.0 | **0.9x** |
| `drift-service` | 70 | 69 | 54 | 88 | 200.0 | 3.7x |
| `fail-open` | 470 | 470 | 38 | 50 | 109.0 | 2.9x |
| `floor` | 294 | 158 | 16 | 18 | 39.0 | 2.4x |
| `ordered-steps` | 340 | 281 | 104 | 122 | 229.0 | 2.2x |
| `quota-merge` | 30 | 14 | 62 | 73 | 86.0 | 1.4x |
| `recall-index` | 60 | 58 | 12 | 18 | 96.0 | 8.0x |
| `recall-metric` | 60 | 57 | 18 | 28 | 83.0 | 4.6x |
| `recall-rollback` | 60 | 59 | 20 | 21 | 72.0 | 3.6x |
| `silent-success` | 370 | 370 | 53 | 56 | 96.0 | 1.8x |
| `stale-cache` | 380 | 89 | 93 | 116 | 157.0 | 1.7x |
| `verdict-experiment` | 270 | 266 | 152 | 170 | 286.0 | 1.9x |
| `verdict-rollout` | 270 | 266 | 108 | 141 | 238.0 | 2.2x |
| `verdict-schema` | 290 | 189 | 120 | 123 | 227.0 | 1.9x |
| `walkthrough` | 660 | 659 | 142 | 194 | 345.0 | 2.4x |
| `wide-index` | 30 | 29 | 16 | 28 | 59.0 | 3.7x |
| `wide-metric` | 30 | 30 | 31 | 34 | 67.0 | 2.2x |
| `wide-rollback` | 30 | 25 | 14 | 19 | 47.0 | 3.4x |

**Every case has a floor, and on 36 of 37 it sits below the laconic median.**
The median ratio is 2.2x.

**That median is over the judged subset, and on the closed cases it is the
generous reading.** A response only appears above if it carries a usable verdict,
which is a fraction of the archive and not a random one: against the medians
`closed-question-136.md` publishes over all 1,953 stored responses, the judged
subset reads 4.5 to 51 words *higher* on nine of the thirteen closed cases, equal
on three and 29 words lower on `quota-merge`. Both are printed below, computed
with that document's own de-duplication so the two tables cannot drift:

| case | floor | judged median | ratio | all responses | ratio |
|---|--:|--:|--:|--:|--:|
| `confirm-index` | 41 | 77.5 | 1.89x | 60.0 | 1.46x |
| `confirm-metric` | 39 | 81.0 | 2.08x | 73.0 | 1.87x |
| `confirm-rollback` | 64 | 82.5 | 1.29x | 78.0 | 1.22x |
| `deep-index` | 45 | 88.0 | 1.96x | 49.0 | **1.09x** |
| `deep-metric` | 39 | 80.0 | 2.05x | 45.0 | **1.15x** |
| `deep-rollback` | 27 | 81.0 | 3.00x | 30.0 | **1.11x** |
| `quota-merge` | 62 | 86.0 | 1.39x | 115.0 | 1.85x |
| `recall-index` | 12 | 96.0 | 8.00x | 63.0 | 5.25x |
| `recall-metric` | 18 | 83.0 | 4.61x | 60.0 | 3.33x |
| `recall-rollback` | 20 | 72.0 | 3.60x | 51.0 | 2.55x |
| `wide-index` | 16 | 59.0 | 3.69x | 59.0 | 3.69x |
| `wide-metric` | 31 | 67.0 | 2.16x | 67.0 | 2.16x |
| `wide-rollback` | 14 | 47.0 | 3.36x | 47.0 | 3.36x |

**On `deep-*` the floor is the median.** 1.09x, 1.15x and 1.11x: at turn five the
laconic arm's typical answer already sits where the shortest passing one does, so
there is no surplus there for any ceiling to convict. That is the same finding
[round 42](round-42.md) reports as the rule binding hardest at depth, arriving
from the other direction, and it is why the 2.2x above may not be read as a
headroom figure for the suite. Where the two columns disagree the archive one is
the conservative reading and is the one to quote.

### Every floor response was read in full, because a judge false pass is free

The floor is a minimum, so one wrong `pass` sets it at no cost. All 37 shortest
passing responses are hand-read against the trap text they were graded by, in
[`judged-floor/floor-labels.json`](judged-floor/floor-labels.json): **37 sound,
0 judge errors.**

Four are labelled `sound-code`, which is a measurement caveat rather than a
doubt. `metrics.score` excludes fenced blocks and inline code from the word
count — deliberately, because charging a response for a `CREATE INDEX` statement
would charge it for content the rule file protects verbatim — and on `badnews`,
`code-fidelity`, `design-upload` and `walkthrough` that is where the answer
lives. `badnews`'s floor of 5 prose words is a complete answer carrying three
test names and a filename as inline code. **A prose floor is a floor on prose,
and those four rows may not be quoted as response lengths.**

### `destructive` is the negative control, and it is the one that matters

`destructive`'s floor is 107 words against a laconic median of 95 — the only
case where a passing answer is *longer* than the arm's typical one, and its trap
says why: the warning must name both `sessions` and `invoices` as blockers and
state that `CASCADE` drops the constraints rather than the rows. On that case
the required content genuinely is the length.

That is the shape DeepSeek predicted for the closed questions, and it is real —
on exactly one case out of 37. **The instrument can say "no ceiling here", which
is what makes the other 36 readings worth having.**

## Result 1: the dominant false-positive class in `closed-question-136.md` does not survive

That document hand-read 30 hits of [#136]'s detector and classified the false
positives. The largest class, 11 of 30, was recorded as:

> **the correction is the length** — The premise is false, so the answer is a
> denial plus the qualification the trap requires, at 80 to 145 words of
> necessary content. *Nothing is deletable.*

Each of those 11 hits, re-read against its own case's judged floor:

| case | words | floor | above the floor |
|---|--:|--:|--:|
| `recall-index` | 101 | 12 | 89 |
| `wide-metric` | 81 | 31 | 50 |
| `recall-index` | 108 | 12 | 96 |
| `quota-merge` | 116 | 62 | 54 |
| `wide-index` | 87 | 16 | 71 |
| `wide-index` | 145 | 16 | 129 |
| `deep-index` | 139 | 45 | 94 |
| `deep-index` | 84 | 45 | 39 |
| `confirm-index` | 91 | 41 | 50 |
| `deep-index` | 134 | 45 | 89 |
| `deep-index` | 103 | 45 | 58 |

**11 of 11 sit above a response that passed the same trap, by 39 to 129 words,
median 71.** "Nothing is deletable" is false for every one of them: the suite's
own frozen criterion has passed a shorter answer to the identical question.

**This corrects the reason, not the label.** The 11 were labelled *not a
violation* because their surplus was held to be trap-required, and that reason is
gone. It does not follow that they are [#136]'s harm, which is re-derivation
specifically — 39 words above a floor may be a second correct fix family rather
than an argument rebuilt. What the floor removes is the escape that made the
question unaskable, and re-labelling those 11 against a criterion without it is
work this document does not do.

## Result 2: the same trap costs 41 words cold and 12 once the material is in the transcript

The four families ask one closed question about one fixture. `confirm-*` asks it
cold; the other three ask it after the model's own prior turns.

Judged floor, in prose words. The medians are in the ratio table above.

| stem | `confirm` (cold) | `recall` (turn 2) | `deep` (turn 5) | `wide` (turn 2, wide) |
|---|--:|--:|--:|--:|
| index | 41 | **12** | 45 | 16 |
| metric | 39 | **18** | 39 | 31 |
| rollback | 64 | **20** | 27 | **14** |

`recall-index`'s floor answers in twelve words — *"No — that index can't serve
this query, since the predicate wraps `created_at` in `date_trunc`."* —
`confirm-index`'s takes 41 for the same trap, and `wide-rollback`'s takes 14
where `confirm-rollback`'s takes 64.

This is consistent with [round 68](round-68.md), which measured the graded turn
at 0.415x when the material was already in the transcript, and it sharpens what
that means: the fall is not only in what the model writes, it is in what the
criterion can be satisfied by. **A cold answer has to establish the fact it just
read; a later one can point at it.** So a floor is a property of a case, not of a
fixture or of a question, and a single cutoff across the four families fits at
most one of them.

## What this does to [#136] proposal 3

The detector was parked for a structural reason, not a tuning one:

> A cutoff that catches 400 words of re-derivation on that question convicts 80
> words of required correction on all thirteen of these. That is not a threshold
> in the wrong place; it is a population that cannot carry the construct.

**The first sentence is now measured, and it is wrong on the 80.** Every one of
the thirteen closed cases has a passing response between 12 and 64 words, so 80
words is above the required correction on all of them rather than inside it.
[#136]'s single global 80 was never derivable from the rule text — which is what
DeepSeek said when that design was consulted — and it is now derivable from the
fixture, per case, without a labeller.

**The second sentence stands, and the archive column is why.** A population that
cannot carry the construct is not what is wrong; a population with no surplus in
it is. On `deep-*` the floor is 1.09x to 1.15x of the median, so those three
cells have nothing for a ceiling to convict at any threshold, and they are three
of the thirteen. Of the other ten, six sit above 2x — all of `recall-*` and all
of `wide-*`, 2.16x to 5.25x — and four between 1.22x and 1.87x, which is
`confirm-*` and `quota-merge`. A ceiling registered across the thirteen would be
registered on three cells that cannot move.

**It is not promoted here, and the reason is precision rather than the
threshold.** The 30 existing hand labels were drawn at the 80-word cutoff. Every
floor-derived cutoff is *below* 80, so it admits hits nobody has labelled, and a
precision figure cannot be carried across. A detector firing at, say, twice its
case's judged floor is one hand-labelled draw away from being measurable, and
this document does not claim the draw.

**What it also does not need is the new case.** `settled-*` was asked for to make
surplus knowable without a labeller. The floor does that on the thirteen closed
questions already in the suite, and on the other twenty-four as well, at the cost
of one script and no generation.

## What this cannot establish

- **A floor is a minimum over the archive, so it can only fall.** Every figure
  here is an upper bound on the true shortest passing answer, and a later round
  that generates more runs on a case may lower it. A cutoff derived from a floor
  therefore loosens over time, never tightens, which is the safe direction for a
  detector that convicts.
- **The floor is taken over every arm and both models**, not over the laconic
  arm. `verdict-schema`'s floor is a `baseline` response and `fail-open`'s is
  `laconic-enforced`. That is deliberate — it is the reading least favourable to
  the plugin, since a lower floor makes laconic's own median look further above
  it — but it means the floor is not "how short laconic goes".
- **Surplus is not harm.** A response 71 words above its floor contains words the
  trap did not require; whether they are [#136]'s re-derivation, [#150]'s
  restatement, or a second correct answer the reader wanted is precisely the
  judgement [#155] parked at 55.3% precision and this instrument does not reach
  it. What the floor supplies is the denominator that judgement was missing.
- **The repeat counts here are not a re-judge rate.** 1,826 responses carry more
  than one verdict and 9 disagree, but `judge.carry_judgments` copies a control
  arm's verdict forward rather than re-grading it, and its `carried` marker
  postdates the early files. So an unmarked repeat may be a copy.
  [`judge-self-disagreement.md`](judge-self-disagreement.md) measures the real
  quantity, 0% to 27% between cases, by re-running the judge on purpose. The
  defence against a judge false pass here is the hand read and the `3rd` column,
  not the repeats.
- **`quality` is not the only `grading` in the table.** `decision`, `floor` and
  `conditional` are `rule-adherence` or mixed, and `badnews`, `destructive` and
  `silent-success` are `safety`. Their floors are computed the same way and
  support the same thing about length; none of them supports a claim about answer
  quality, per `evals/CRITERIA.md`.

## What goes into `evals/CRITERIA.md`

One rule, and it is the artifact both consult targets said was the real one:

> **A ceiling is a measurement only where a judged floor sits below it.** Every
> trap in this repository is a floor, so an endpoint that convicts a response
> for being too long is asserting something no trap states. Before such an
> endpoint is registered, compute the shortest response that case's own trap has
> passed and read it in full. A cutoff above the floor is measuring surplus; a
> cutoff at or below it fails correct answers and is grading form. `destructive`
> is the case that proves the check can fail: its floor is 107 words against a
> laconic median of 95, so no ceiling is available there at any threshold.

## Cost

No generations, no judge calls, no `claude` CLI sessions, nothing spent from a
usage window. The consult was three `delegate` targets, two of which answered.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#155]: https://github.com/JordanMPDS/laconic/issues/155
[#305]: https://github.com/JordanMPDS/laconic/issues/305
