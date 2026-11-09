# Round 131: does #113's feasibility question run long, or close with an offer? (#113)

**Registration. Nothing below the results line has been computed.** This file,
the `feasible-*` and `coldfeasible-*` pilot cases, `score_feasible.py` with its
six reference answers, and the layout check that holds the family together are
committed before any generation.

**This round proposes no rule edit.** It is a fire-rate screen at master rules
for the one shape of [#113] no round has measured, so that round 132, which
has to carry a candidate, either has this shape as a target or knows it does
not fire.

`bash tools/candidate-due.sh` exited 0 at registration: round 130 tested a
candidate, so this round may measure. `bash tools/release-due.sh` exited 0:
v0.7.0 is tagged and current.

## Why this round exists

[#113] reports two consecutive feasibility questions about a storage backend,
*"is it possible to test on X?"* and then *"what about on Y instead?"*, asked
deep in a session co-authoring a design document, at `full` on Opus. Both got
about 600 words, and the first closed with *"Want me to write the schema, or
add a note to the spec?"*. The issue reads the offer as a binary signal for
length drift, and asks for feasibility as a named trigger: *"Is it possible to
X?" is answerable as a verdict plus the constraint that decides it.*

Every screen of the offer half since has read zero on opus: `edit-service`
0 of 50 runs on any turn (rounds 91, 109 and 117), `build-*` 0 of 60 (round
117). None of them asked a feasibility question. [Round 125](round-125.md)
measured proposal C's findings half, on `verdict-*`, and left the feasibility
shape open. It is the last part of the report without a reading.

## The instrument

`feasible-replay`, `feasible-shadow` and `feasible-state` are one four-turn
session over session-alerting-long's 2,578-word SPEC.md, a design for an
ingest throughput governor. Turns 1 and 2 are identical across the three:

> read SPEC.md and settle open question 5: cycle records are kept for 120
> days, then deleted. Go ahead and make the change.
>
> settle open question 2 as well: cap_clamped feeds the end-of-day view and
> never alerts. Go ahead and make the change.

That is the report's co-authoring session, at two edits rather than many.
Turns 3 and 4 are the feasibility pair, one storage backend and then another:

| stem | turn 3 | turn 4 |
|---|---|---|
| `replay` | is it possible to run the simulation rung against a SQLite copy of the cycle record table? | what about DuckDB instead? |
| `shadow` | could we run the shadow week against a staging copy of the config store instead of production? | what about a read replica of the production config store instead? |
| `state` | is it possible to keep controller state in memory for the pilot instead of persisting it? | what about Redis instead? |

Neither feasibility turn says whether to edit, as the report's did not, so an
answer that edits SPEC.md or offers to is visible. Each `coldfeasible-*` case
asks its stem's turn 3 with no session before it, and decides nothing.

Each trap grades its case's final question from facts it states with their
SPEC.md section. This round judges nothing.

## The reference answers

`score_feasible.py` holds one reference answer for each feasibility turn: the
verdict, the constraint that decides it, and the bad news a correct answer
cannot drop. They were written before any generation and are frozen in this
commit. Prose words, counted by `score_compression.words` (inline code out):

| stem | turn 3 | turn 4 |
|---|--:|--:|
| `replay` | 82 | 42 |
| `shadow` | 65 | 57 |
| `state` | 60 | 47 |

The `state` turn-3 reference, for the shape:

> Not without changing the supervisor. Each five-minute run takes a lease and
> writes a heartbeat at its start (section 10), so state held in memory is gone
> by the next cycle. The integral term would restart at zero every cycle, and
> the stale count could never reach three, so a stale feed would freeze the cap
> instead of falling back to `cap_default`.

That is #113's "four-step failure chain" in miniature, the volunteered content
the issue says a fix must not cost. The other five are in the script.

## The run (about 120 opus session turns and 15 cold calls)

Master rules (`rules_cksum` 1610267591), opus, arm `laconic`, plugin delivery,
10 sessions a stem in three shards split by rep, and the cold cells at 5 reps
in a fourth.

```sh
OUT=evals/snapshots/loop
C="--arms laconic --models opus --cases-dir evals/pilot --turn-delivery plugin --concurrency 4"
python3 evals/bench/run.py $C --cases 'feasible-*' --reps 4 \
  --snapshot $OUT/round-131-session-0.json &
python3 evals/bench/run.py $C --cases 'feasible-*' --reps 3 --rep-offset 4 \
  --snapshot $OUT/round-131-session-4.json &
python3 evals/bench/run.py $C --cases 'feasible-*' --reps 3 --rep-offset 7 \
  --snapshot $OUT/round-131-session-7.json &
python3 evals/bench/run.py $C --cases 'coldfeasible-*' --reps 5 \
  --snapshot $OUT/round-131-cold.json &
wait
python3 evals/bench/merge.py $OUT/round-131-session-{0,4,7}.json \
  --out $OUT/round-131-session.json
python3 evals/bench/release.py $OUT/round-131-session.json $OUT/round-131-cold.json
python3 evals/pilot/score_feasible.py $OUT/round-131-session.json $OUT/round-131-cold.json
```

## The bars

The unit is the session, because one session's two feasibility answers are
not independent. Over the 30 sessions:

| half | a session counts when | fires at | from |
|---|---|--:|---|
| length | a feasibility answer reaches 3 times its reference's prose words | 6 of 30 | `--fire-at 0.30 --quiet-at 0.05` |
| ceremony | a feasibility answer carries a closing offer (`metrics.closing_offers`) | 3 of 30 | `--fire-at 0.20 --quiet-at 0.02` |

```
$ python3 evals/bench/precheck.py --cells 10,10,10 --fire-at 0.30 --quiet-at 0.05
  bar        fire@0.3      quiet@0.05
    5           0.970           0.016  meets the pair
    6           0.923           0.003  meets the pair
    7           0.840           0.001
bars meeting the pair: 4 to 6 of 30
$ python3 evals/bench/precheck.py --cells 10,10,10 --fire-at 0.20 --quiet-at 0.02
  bar        fire@0.2      quiet@0.02
    2           0.989           0.121
    3           0.956           0.022  meets the pair
    4           0.877           0.003
bars meeting the pair: 3 to 3 of 30
```

The length bar is the highest that meets its pair. 30% of sessions is the
lowest rate a candidate on this shape is worth a round at, by round 117's
sizing; 5% counts as gone. The offer bar is the only one that meets its pair:
a 20% offer rate is worth a round, and 2% is the rate rounds 76 and 79 found
not worth one.

**What each outcome means.** A half that fires is a target for round 132,
which owes a candidate: it shows the shape occurs at master rules on opus, not
that the rules cause it. A half that does not fire is a measured null on the
report's last shape, and [#113] gets the reading. Neither outcome withdraws
anything, since nothing is registered behind the screen.

**Disclosed, deciding nothing:** per stem and per turn, median prose words and
median ratio to the reference; answers at 300 and at 600 prose words or more,
the latter the report's own size and the bar rounds 91 and 109 used for [#46];
headings and bold labels, for the report's *"six bolded section headers"*;
feasibility answers that call an editing tool; every offer verbatim; the cold
cells beside each session's turn 3; cost; and `release.py`.

## Where the design came from

`tools/consult.sh` asked Codex, DeepSeek and Kimi about a design that fired the
length half at 600 prose words. Only Kimi answered.

- **Kimi** said a 600 bar sits above opus's observed range, so its null would
  show nothing the loop does not already know, and that one word count is not
  comparable across stems with different natural answer sizes. It proposed
  the ratio to a per-stem reference answer frozen before any run, with 600
  kept as a disclosed line. Adopted, with the reference written per turn.
- **Kimi** asked for the per-turn split to be disclosed, because the report's
  offer was on the first feasibility turn and not the second, and for the
  per-stem rates beside the pooled count. Both are printed.
- **Kimi** warned that a screen with no control arm shows the shape occurs,
  not that the rules cause it. The outcome paragraph above says so.

## Pre-mortem, registered

I expect the ceremony half not to fire: opus has read zero offers on every
#113 instrument for two months, the widened detector included. I expect the
length half to fire, mostly on turn 4, whose references are 42 to 57 words
against opus answers that have run 200 words or more on every explain and
design cell this loop has measured. The likeliest way this round misleads is
through the references: they are mine, and short, so a fire may say as much
about where the reference sits as about the answers. The six are printed in
`score_feasible.py` so that a reader can judge them, and the 300- and 600-word
lines are printed beside the ratio so the fire can be read in absolute terms
too.

## Results

<!-- Nothing below this line was computed at the registration commit. -->

### Neither half fires

45 runs, 0 failed, every one on CLI 2.1.319, from four shards at once on
2026-11-09, stamped 08:30 to 08:46 UTC, at master rules (`rules_cksum`
1610267591). `release.py`: no unreadable span, no arm imbalanced across a
release. The merged session snapshot declares 4 and reconstructs to 3 in
flight.

```
## Feasibility answers, opus, laconic
   case                 turn  n  median  ratio >=3x >=300  >=600 offers heads bolds  wrote
   feasible-replay         3 10   103.0   1.26    0    0      0      0   0.0   0.0  0
   feasible-replay         4 10    35.5   0.85    0    0      0      0   0.0   0.0  0
   feasible-shadow         3 10   116.5   1.79    0    0      0      0   0.0   0.0  0
   feasible-shadow         4 10    72.5   1.27    0    0      0      0   0.0   0.0  0
   feasible-state          3 10   103.5   1.73    0    0      0      0   0.0   0.0  0
   feasible-state          4 10    74.5   1.59    0    0      0      0   0.0   0.0  0
   coldfeasible-replay     3  5   195.0   2.38    0    0      0      0   0.0   0.0  0
   coldfeasible-shadow     3  5   170.0   2.62    2    0      0      0   0.0   3.0  0
   coldfeasible-state      3  5   210.0   3.50    5    0      0      0   0.0   4.0  0
## Every closing offer, verbatim
   none
## Verdict, over the feasible-* sessions (10 a stem expected)
   sessions with a feasibility answer at >= 3x its reference: 0 of 30 (fires at 6)
   sessions with a closing offer on a feasibility answer: 0 of 30 (fires at 3)
## length does not fire, ceremony does not fire
```

**No session answer reaches three times its reference, and none closes with
an offer.** The longest of the 60 feasibility answers is 169 prose words, and
the highest ratio is 2.82 (`state`, turn 3). Medians run 0.85 to 1.79 times
the reference, so a typical answer is the reference with a sentence or two
more. No feasibility answer carries a heading or a bold label, and none
edits SPEC.md. The report's 600 words is more than three times the longest.

**The manipulation held.** All 30 sessions changed SPEC.md over turns 1 and 2,
27 of them through `Edit` or `Write` on turn 1. No edit turn carries an offer
either.

A median `feasible-state` turn-3 answer, 114 prose words:

> Not with the supervisor as the spec describes it. Section 10 treats each
> cycle as a separate run: it writes a heartbeat at the start, and if it can't
> take the lease it exits. Anything held in memory would be gone by the next
> cycle.
>
> That state includes the integral term, and probably the consecutive-stale
> count and the previous cap. Without it, the integral would reset every
> cycle, the three-cycle `feed_stale` fallback would never trigger, and the
> cap would have nothing to scale from. [...]

That is the verdict, the deciding constraint and the failure chain #113 asks
a fix to keep, at the reference's size.

### Disclosed, deciding nothing

- **The cold question runs about twice as long as the same question in the
  session.** Turn-3 medians of 195, 170 and 210 prose words cold against 103,
  116.5 and 103.5 in session, and the cold `shadow` and `state` answers carry
  a median 3 and 4 bold labels where no session answer carries any. All five
  cold `state` answers reach three times the reference. The median one is a
  bolded three-item list of reasons, and closes on an alternative nobody
  asked for (*"you could store it in the cycle record"*). This is round 36's
  direction, depth suppressing what a cold question draws, on a new shape. No
  test was registered on it, and at 5 reps a stem it is a description.
- **The pre-mortem was half wrong.** It expected the length half to fire on
  turn 4, and turn 4 is the shortest turn in every stem.
- **Cost.** $28.38 for the 30 sessions (120 turns) and $2.26 for the 15 cold
  calls. Nothing was judged.

## Result: neither half fires

At master rules on opus, #113's feasibility pair, asked in the co-authoring
session it was reported from, is answered at about the size of a complete
reference answer and never closes with an offer. Every shape [#113] reports
now has a reading on opus: the offer on `edit-service` (0 of 50 runs), on a
build request with ponytail beside laconic (0 of 60), and on this pair (0 of
30), and the length on this pair (0 of 30 at three times the reference). The
cold cells are the one place the length still shows, and they are not the
report's condition.

Round 132 owes a candidate, and this round gives it no target on [#113].

[#46]: https://github.com/JordanMPDS/laconic/issues/46
[#113]: https://github.com/JordanMPDS/laconic/issues/113
