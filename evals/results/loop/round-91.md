# Round 91: which open `rules` issue still fires at master rules?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 82, 88, 89 and 90, which are merged. This file and
its scorer, `evals/pilot/score_fire.py`, are committed before any generation.
**This round proposes no rule edit.** It finds out which issue the next
candidate round can be tested on.

`bash tools/candidate-due.sh` exited 0 at registration: round 90 carried a
candidate, so round 91 may measure. Round 92 may not.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_fire.py evals/snapshots/loop/round-91-*.json
```

## Why this round exists

The last three candidate rounds each bought an edit for a defect that was
absent from its own control:

| round | issue | control at master rules | earlier reading |
|---|---|--:|--:|
| [88](round-88.md) | [#353], sonnet | 0/60 fails, CLI 2.1.285–286 | 20/60, CLI 2.1.282 |
| [89](round-89.md) | [#298], opus | precheck did not fire | |
| [90](round-90.md) | [#264], sonnet | 0/600 unread, CLI 2.1.286–287 | 387/600, CLI 2.1.280 |

Round 90 also read `conditional`/sonnet editing in 0 of 80 laconic runs, the
[#116] counter that sat between 35% and 50% through September. The rules were
byte-identical across round 88's comparison. The instrument has moved under
the backlog, and a candidate registered from an issue's original numbers is now
likely to be wasted. Round 89 showed the remedy, a cheap precheck before the
edit. This round runs that precheck once for every `rules` issue not measured
in the last 72 hours, so round 92 can pick an issue known to fire instead of
finding out after buying it.

## What is read

Master rules (`rules_cksum` 288018845), the laconic arm only, level `full`,
on **opus**, the model these four reports came from. Each issue keeps the
counter it was already measured by. Every counter is deterministic, and no
judge is bought.

| issue | cell | reps | counted | **fires at** |
|---|---|--:|---|--:|
| [#305] | `settled-failover`, `-retention`, `-rounding` (pilot) | 10 each | answers over 80 prose words, on a closed question whose complete answer is one word | **≥ 9/30** |
| [#116] | `conditional` | 20 | runs that call `Edit`, `Write`, `MultiEdit` or `NotebookEdit` on a question that only asks | **≥ 5/20** |
| [#113] | `edit-service` (pilot, five turns, `plugin` delivery) | 20 | turn 3 carrying a `metrics.closing_offers` hit | **≥ 3/20** |
| [#46] | `design-alerting` | 20 | answers over 600 prose words | **≥ 2/20** |

**Not read, measured within 72 hours at the same rules:** [#353] (round 88),
[#298] (round 89) and [#264] (round 90). [#353]'s last reading was on CLI
2.1.285–286 and the current one is 2.1.287.

**The thresholds are screens, not effect sizes.** Each one is the rate below
which a round of about 800 calls cannot power a fall it would care about.
"Fires" means the defect is observable under laconic at master rules. It does
not mean laconic causes it. Attribution belongs to round 92, which generates
its own contemporaneous control whichever issue it takes.

**Ranking.** The four counters share no scale, so they are ranked by margin,
observed count over threshold, with ties going to the larger n. Round 92 takes
the top firing issue unless no one-line rule edit plausibly reaches its
behaviour, and says so if it passes one over.

**If nothing fires**, this document says so and comments on each issue.
Round 92 still owes a candidate. Its next step is a case built closer to one
report rather than another edit on an instrument that shows nothing.

**Where the ideas came from.** The sweep is this round's own. Through
`tools/consult.sh`, DeepSeek and Kimi both raised #46's cell from 10 reps
firing at one long answer to 20 firing at two, and both proposed ranking by
margin over threshold instead of by raw rate. DeepSeek supplied the wording
that a fire is observable rather than caused. Kimi's 10-rep baseline arms for
#305 and #116 were not taken, because attribution is round 92's job and every
candidate round generates a control anyway. Kimi's liveness probe on #264 was
not taken either: round 90 confirmed its 0/600 reading from transcripts. Codex
did not answer.

## Pre-mortem, registered

**I expect one issue to fire at most, and #305 to be the likeliest.** Round
90 found sonnet's answers several times longer than eight days earlier on
`code-fidelity`, and opus runs longer than sonnet, so a one-word question
answered at over 80 words is the shape most likely to have grown. The
likeliest non-firing cell is #46, at 0/72 in round 82. #113 sat at 1.7% on
haiku, so a fire there would be new. #116 fell to 0/80 on sonnet in round 90,
and opus has not been read on it since the move.

## One pass, four shards

One shard per issue, all four at once, `--concurrency 4` declared on each.

```sh
S=evals/snapshots/loop
P='--arms laconic --concurrency 4'
python3 evals/bench/run.py $P --cells 'settled-failover:opus,settled-retention:opus,settled-rounding:opus' \
  --cases-dir evals/pilot --reps 10 --snapshot $S/round-91-settled.json &
python3 evals/bench/run.py $P --cells 'edit-service:opus' --cases-dir evals/pilot \
  --turn-delivery plugin --reps 20 --snapshot $S/round-91-edit-service.json &
python3 evals/bench/run.py $P --cells 'conditional:opus' --reps 20 \
  --snapshot $S/round-91-conditional.json &
python3 evals/bench/run.py $P --cells 'design-alerting:opus' --reps 20 \
  --snapshot $S/round-91-design-alerting.json &
wait
```

90 runs and about 170 opus calls. `python3 evals/bench/release.py` is run over
the four snapshots before any count is read, per [#272].

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#264]: https://github.com/JordanMPDS/laconic/issues/264
[#272]: https://github.com/JordanMPDS/laconic/issues/272
[#298]: https://github.com/JordanMPDS/laconic/issues/298
[#305]: https://github.com/JordanMPDS/laconic/issues/305
[#353]: https://github.com/JordanMPDS/laconic/issues/353

---

# Results

*Nothing above this line was written after the numbers came in.*

## Nothing fires

*90 runs, 0 failed, four shards, all `--concurrency 4`. The `edit-service`
shard was stopped by the session's background time limit at 12 of 20 runs and
resumed with the registered command from the same tree. `release.py` finds
all 90 runs on CLI 2.1.287, with no span to read.*

| issue | counted | observed | fires at | 95% upper bound | median prose words |
|---|---|--:|--:|--:|--:|
| [#305] | settled answers over 80 prose words | **0/30** | 9 | 11.6% | 1 |
| [#116] | `conditional` runs that edited a file | **0/20** | 5 | 16.8% | 117.5 |
| [#113] | `edit-service` turn-3 closing offers | **0/20** | 3 | 16.8% | 168 (turn 5) |
| [#46] | `design-alerting` over 600 prose words | **0/20** | 2 | 16.8% | 232 |

Each zero was checked against the transcripts, not just the counter. All 30
settled answers are the single word `Yes.`. Every `conditional` run used
`Bash` alone, to read the fixture, and none wrote. Every `edit-service` run
has five turns, and turn 3 ends on the defect it found, with no offer and no
write in any of them. The longest `design-alerting` answer is 314 words.

## The verdict

**No open `rules` issue not measured in the last 72 hours fires on opus at
master rules under CLI 2.1.287.** With rounds 88, 89 and 90, that covers all
seven. The pre-mortem expected one fire, most likely #305. Instead #305 read
the floor of its scale: opus answers the one-word question with one word,
every time.

Round 92 still owes a candidate, and none of the backlog's instruments can
carry one. As registered, its next step is a case built closer to one report.
The reports share a shape these cells do not: #305, #298, #113 and #46 each
came from a long working session with several turns of the model's own prior
material in context, while every cell here is a single turn or five short
ones over a small fixture. Round 82 found the same for #46 when it held
everything constant except depth. A case that carries a long prior context is
the untested condition.

No arm, rule or worktree was created, so there is nothing to revert or
reclaim. The four snapshots stay.
