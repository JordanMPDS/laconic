# The harness has been over-delivering the rules on later turns

**Rounds 33, 35 and 36 measured a treatment no real session receives.** Not
wrongly — the arm is well defined and the comparison inside each round is sound
— but the multi-turn treatment is *stronger* than the shipped plugin's, and that
changes what one of their findings can be read as.

## What the plugin sends, and what the harness sent

`hooks/hooks.json` wires two events:

| Event | Fires | Sends |
|---|---|---|
| `SessionStart` | startup, resume, clear, compact | the **full rule slice**, once |
| `UserPromptSubmit` | **every turn** | one line: `LACONIC MODE ACTIVE (full). Make fewer claims…` |

`run.py` sends the full slice as `--append-system-prompt`, and `call()` passes it
on every call — including the `--resume` calls that continue a multi-turn case.
So a five-turn case received the entire rule text **five times**, and never
received the reminder at all.

It is in effect on those later turns rather than being ignored, which round 36
shows directly: laconic held 0 closing offers across all five turns while
baseline ran 12% to 32%.

## Why it matters, and why it is not a retraction

**The accumulated-own-output effect is a lower bound, not an estimate.** Rounds
35 and 36 measured a turn-5 answer running about 35% longer than the identical
question asked cold — 30.8%/36.8% and 33.8%/38.4% — and they measured it *while
the whole rule set was being re-asserted on every one of those turns*. A real
session re-asserts one sentence. Whatever that effect is under the shipped
wiring, it is unlikely to be smaller.

**[#60]'s fix cannot be tested under the old behaviour at all.** That issue
reports the level "stopped binding" after a run of turns where length was
correct, and asks for a persistence clause — laconic has no equivalent of
ponytail's *"ACTIVE EVERY RESPONSE. No drift back to over-building."* Testing
that needs a harness whose baseline does **not** already re-send everything every
turn. Under `repeat` the treatment and its proposed fix are indistinguishable,
because `repeat` is a maximal persistence clause.

**Nothing about rounds 33 to 38 is withdrawn.** Every comparison in them is
between arms generated the same way in the same batch, so the treatment being
strong affects what the number generalises to, not whether the contrast is real.

## The change

`run.py` gains `--turn-delivery`:

- **`repeat`** — the default, and what every stored snapshot holds. Re-appends
  the whole slice on every turn.
- **`plugin`** — the slice once on turn 1, then only the reminder, prepended to
  the prompt the way `UserPromptSubmit`'s `additionalContext` reaches the model.

`repeat` stays the default so no stored comparison shifts, **not because it is
the faithful one**. A multi-turn record now carries `turn_delivery`, so a
snapshot says which treatment it holds instead of leaving a reader to assume;
one-turn records carry no such field, because the distinction does not exist for
them.

The reminder string is a second copy of a line in `hooks/laconic.sh`, so a test
pins them together rather than trusting them to stay equal.

## What a round would do with this

The obvious one: `deep-*` under both delivery modes, one interleaved batch, and
score whether the turn-5 inflation is larger under `plugin`. That is the first
measurement of the plugin's actual multi-turn behaviour, and it sizes the gap
this document only bounds.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
