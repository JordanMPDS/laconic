# Round 98: does #46's design essay come back five turns into a session, on opus?

**Registration. Nothing below the results line has been computed**, except the
figures quoted from rounds 82 and 91, which are merged. This file, the
`session-alerting` case, its layout test and `evals/pilot/score_session.py`
are committed before any generation.

**This round proposes no rule edit.** It measures whether [#46] fires on an
instrument built closer to the report, so that round 99, which has to carry a
candidate, knows whether this issue can be its target.

`bash tools/candidate-due.sh` exited 0 at registration: [round 97](round-97.md)
carried a candidate, so round 98 may measure. `bash tools/release-due.sh`
exited 0: round 97's edit shipped in 0.3.4.

Reproduce every number below the results line with:

```sh
python3 evals/pilot/score_session.py evals/snapshots/loop/round-98.json
```

## Why this round exists

[#46] is a field report from Opus 5 at level `full`: several turns into a
working session over a design document, turns that "had gone well and stayed
terse", the user asked *"multiple areas in [a section] talk about alerting. how
would that be built?"* and got about 1,400 words in eight H2 sections. No
instrument has reproduced it on opus at current rules:

| round | instrument | opus laconic over 600 prose words |
|---|---|--:|
| [82](round-82.md) | `drift-service` (five design questions over code) and `design-alerting` cold | 0/72 |
| [91](round-91.md) | `design-alerting` cold, #46's own prompt | 0/20, median 232, longest 314 |

[#305] had the same history and then reproduced: [round 93](round-93.md)'s
`subset-*` fired once the model's own long answer about the same material was
in context, and that instrument carried round 97's accepted edit. Neither #46
instrument has that. `drift-service`'s earlier turns are design questions over
a code fixture, and `design-alerting` has no earlier turn at all.

## The instrument

`session-alerting` is `design-alerting` with four turns in front of it. The
fixture is the same `SPEC.md` by symlink, and the fifth turn is
`design-alerting`'s prompt byte for byte, with its trap; the layout test pins
both.

1. *read SPEC.md and summarize it for me: the control loop, every guardrail and
   what it does to the cap, and the rollout plan.* This puts the model's own
   long account of the spec in context, which is what made #305 fire.
2. *if the feed goes stale for two cycles and then recovers, does the tenant
   ever fall back to its default cap?* (No: the fallback is after three.)
3. *and if quota_exceeded and floor_at_risk both hold in the same cycle, which
   one fires?* (`quota_exceeded`, by priority order.)
4. *does config_invalid stop the loop for that tenant?* (No: it is served the
   fleet default.)

Turns 2 to 4 are closed and answered by one sentence of the spec, which is the
report's terse stretch. The fixture stays at 458 words: the variable here is
prior material in context, and lengthening the document would change a second
thing at once.

`design-alerting` is symlinked into `evals/pilot` so both cells are generated
in one interleaved pass, and the cold reference does not lean on round 91's
reading from another day.

## Design

Master rules (`rules_cksum` 3660436060, as released in 0.3.4), the laconic arm,
opus, `--turn-delivery plugin`, level `full`, 20 reps, four shards by
`--rep-offset` at `--concurrency 4`. That is 100 session turn calls and 20 cold
calls, all on opus. Nothing is judged, because the readout reads no verdict.

```sh
for off in 0 5 10 15; do
  python3 evals/bench/run.py --arms laconic --reps 5 --rep-offset $off \
    --cases-dir evals/pilot --cells 'session-alerting:opus,design-alerting:opus' \
    --turn-delivery plugin --concurrency 4 \
    --snapshot evals/snapshots/loop/round-98-shard$off.json &
done
wait
python3 evals/bench/merge.py evals/snapshots/loop/round-98-shard{0,5,10,15}.json \
  --out evals/snapshots/loop/round-98.json
python3 evals/bench/release.py evals/snapshots/loop/round-98.json
```

## The readout, and what it sends next

`score_session.py`, whose selftest pins every branch, counts graded turns over
**600 prose words**, round 91's screen for this issue and under half of the
report's 1,400.

| verdict | condition | what follows |
|---|---|---|
| fires | `session-alerting` at least 2/20, cold at most 1/20 | round 99 carries a claim-count edit for #46, scored on this instrument |
| top-up | `session-alerting` exactly 1/20, cold at most 1/20 | both cells extend to 40 reps, and the bar becomes 4/40 |
| null | otherwise, cold at most 1/20 | #46 is recorded as not reproducing with the model's own summary in context; round 99 takes another `rules` issue |
| void | cold over 1/20 (2/40 after a top-up) | the window moved rather than the session, and this round reads nothing |

The bar is absolute rather than a ratio against the cold cell, because the
report's failure is absolute and the cold cell reads 0 of 20. The session's
turn-1 and turns-2-to-4 medians are printed beside it, to confirm turn 1 ran
long and the closed turns stayed terse; they decide nothing.

**Pre-mortem.** The likeliest outcome is a null: opus at these rules has not
gone over 368 words on a design question since the pre-action check shipped,
and [round 94](round-94.md) found four turns of depth moved #305's graded turn
by x1.07. If it is null, the report's remaining unmodelled condition is the
second plugin: ponytail was co-active at `full` and carries its own licence for
full-length explanations, which no harness arm reproduces.

## Where the ideas came from

The case's shape, a summary turn 1 ahead of the closed turns in one cell rather
than closed turns alone, and keeping the fixture at its current length are from
DeepSeek through `tools/consult.sh`. Kimi proposed the same summary turn as a
second cell; one cell was chosen to keep the round at 120 opus calls. The cold
cell's role as a void condition is DeepSeek's, the registered top-up at exactly
1 of 20 is Kimi's, and both named ponytail as the next condition after a null.
Codex did not answer within its timeout.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#305]: https://github.com/JordanMPDS/laconic/issues/305

---

## Results
