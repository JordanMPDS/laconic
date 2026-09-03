# The harness has been over-delivering the rules on later turns

> **Corrected 2026-09-03 by round 40. The central reading below is wrong in
> sign.** This document argued that the accumulated-own-output inflation rounds
> 33, 35 and 36 measured is a *lower bound* on what the shipped plugin does,
> because those rounds measured it while the whole rule set was being re-asserted
> every turn. [`round-40.md`](round-40.md) generated the same cells under
> `--turn-delivery plugin` and the effect does not shrink, it reverses: at master
> rules the laconic median goes 88.5 words at turn 1, **17** at turn 2 and **27**
> at turn 5, against 94.0, 115.0 and 159.5 under `repeat`. Turn 1 is the internal
> control — both modes send byte-identical turn-1 material — and it does not move
> (p = 0.576). Under the wiring the plugin actually ships, depth makes the answer
> *shorter*. The section headed "Why it matters, and why it is not a retraction"
> is left standing with its claim struck rather than deleted: being wrong in a
> way a round could test is what made round 40's second registered comparison
> worth buying.

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

**~~The accumulated-own-output effect is a lower bound, not an estimate.~~**
**Falsified by round 40.** Rounds 35 and 36 measured a turn-5 answer running
about 35% longer than the identical question asked cold — 30.8%/36.8% and
33.8%/38.4% — and they measured it *while the whole rule set was being
re-asserted on every one of those turns*. A real session re-asserts one sentence,
and the inference drawn here was that whatever the effect is under the shipped
wiring, it is unlikely to be smaller.

It is not merely smaller. It is the other sign. Under `plugin` the same cells at
the same rules read 88.5 words at turn 1, 17 at turn 2 and 27 at turn 5. The
other family moves with it: computed from `round-40-control.json`, `cold-service`
to `drift-service` reads 284 to 134.5 where round 36 read 263 to 364, and
`cold-service` is one turn, so delivery cannot reach it. Re-assertion was not working against the inflation; re-assertion **was** the
inflation. The reasoning error is worth naming, because it is available to any
future round: a treatment that over-delivers the intervention was assumed to
suppress an effect the intervention opposes, when it was in fact producing it.

**[#60]'s fix cannot be tested under the old behaviour at all.** That issue
reports the level "stopped binding" after a run of turns where length was
correct, and asks for a persistence clause — laconic has no equivalent of
ponytail's *"ACTIVE EVERY RESPONSE. No drift back to over-building."* Testing
that needs a harness whose baseline does **not** already re-send everything every
turn. Under `repeat` the treatment and its proposed fix are indistinguishable,
because `repeat` is a maximal persistence clause.

**No within-round comparison in rounds 33 to 38 is withdrawn, and their
generalisation to the shipped plugin is.** Every comparison in them is between
arms generated the same way in the same batch, so each contrast is real *under
`repeat`*. What the sentence above got wrong is the next step: rounds 33 and 35
were run to explain [#136], a report from a real session under the shipped
wiring, and under that wiring the direction reverses. They characterise `repeat`,
not the plugin. Each round doc now carries the same note.

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

## What a round did with this

The round this section asked for is [`round-40.md`](round-40.md), and its answer
is above: the turn-5 inflation is not larger under `plugin`, it is absent and
replaced by a fall. [`round-41.md`](round-41.md) then bought the verdict a token
count cannot give, because a fall could be correct terseness or a dropped clause.
It is terseness: on the identical final question, `plugin` grades 30/30 at turn 1,
28/30 at turn 2 and 28/30 at turn 5 (p = 0.4915 on both comparisons), and a
matched `repeat` batch grades 90/90 while spending six times the words. So the
extra words `repeat` buys are not carrying anything the judge can see, and
`plugin` is the mode a round about the shipped product has to use.

**`repeat` is still the default**, so a round that means to describe the plugin
has to say `--turn-delivery plugin` explicitly. Round 40 is the first that did.

[#60]: https://github.com/JordanMPDS/laconic/issues/60
[#136]: https://github.com/JordanMPDS/laconic/issues/136
