# `stale-cache` was grading backwards

Closes [#39](https://github.com/JordanMPDS/laconic/issues/39). The issue offered
two explanations for one cell failing 3 of 5 in two unrelated rounds: the case
is unstable at haiku, or both edits really broke it. **The first is right, and
the check it proposed measures it: 7 passes in 20 redraws under unchanged
rules.**

There was also a third thing wrong that the issue could not have seen. The
case's criterion required an answer that is wrong about HTTP, so the judge was
passing the responses that got caching backwards and failing the ones that got
it right. The instability was real all along; it was being scored on the wrong
face of the coin.

## What #39 asked

`stale-cache`/haiku lost the same three quality verdicts in round 03 and round
04, on two rule edits that both concerned arrows and neither of which mentions
caching. Round 01, under master's rules, lost none. Since `quality_fails` is a
fatal gate — any increase rejects an edit on its own, with no significance test
— a cell that flips at random would reject rule edits it has nothing to do with.

The issue proposed a 20-call check under master's unchanged rules to tell
sampling noise from a real effect. That check was run, and is reported below —
but scoring it meant reading the criterion it would be graded against, and the
criterion turned out to be wrong.

## The criterion, and what it required

The fixture is a feature-flag client with a 60-second in-process cache that
sends a request header, and a captured response from the flag service:

```
'Cache-Control': 'max-age=3600',          # flags.js, on the REQUEST

cache-control: public, max-age=30         # response-headers.txt
age: 2841
x-cache: HIT
via: 1.1 varnish
```

The old trap:

> Passes when it identifies the `Cache-Control: max-age=3600` header that
> flags.js sends on the request as the cause: as a request directive it tells
> the shared cache in front of the flag service that a response up to an hour
> old is acceptable, which is why the cache serves a HIT with an age of 2841
> seconds even though the origin sets max-age=30.

A request `max-age` does not do that. RFC 9111 §5.2.1.1 has it the other way
round: the directive says the client *prefers* a response no older than the
given value, and "unless the max-stale request directive is also present, the
client does not wish to receive a stale response." It limits what the client
will accept. It cannot extend what a cache is allowed to store or serve, and
`flags.js` sends no `max-stale`.

## What Varnish actually does

Verified against `varnish:7.4` with an origin returning the fixture's own
`cache-control: public, max-age=30`, not from memory. Grace was set to 0 so
freshness alone decides.

Identical URLs, one always sent with the fixture's request header and one never:

```
### A. request WITH 'Cache-Control: max-age=3600'
t=0    Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS   body={"serial": 3}
t=10   Cache-Control: public, max-age=30   Age: 10   X-Cache: HIT    body={"serial": 3}
t=35   Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS   body={"serial": 4}

### B. request WITHOUT any Cache-Control
t=0    Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS   body={"serial": 5}
t=10   Cache-Control: public, max-age=30   Age: 10   X-Cache: HIT    body={"serial": 5}
t=35   Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS   body={"serial": 6}
```

The two are the same at every step. At t=35 both revalidate — the serial
increments and the age resets — because the object's 30-second lifetime is up.
The header the criterion called the cause changes nothing.

Varnish ignores the client's `Cache-Control` in the other direction too:

```
### C. does Varnish honour a client 'Cache-Control: no-cache'?
       Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS   body={"serial": 7}
+3s    Cache-Control: public, max-age=30   Age: 3    X-Cache: HIT    body={"serial": 7}
```

And the fixture's headers reproduce exactly with **no request `Cache-Control`
sent at all**, from one line of VCL on the cache side:

```
### D. Varnish with 'set beresp.ttl = 1h', no request Cache-Control
       Cache-Control: public, max-age=30   Age: 0    X-Cache: MISS
+40s   Cache-Control: public, max-age=30   Age: 40   X-Cache: HIT
```

`cache-control: public, max-age=30` alongside a `HIT` at an age past it is a
property of the cache's configuration. It is not something a client can ask for.

## The verdicts were inverted, and the transcript shows it

Round 01's five `stale-cache`/haiku responses all **passed** the old criterion.
All five say the request header is what makes the cache hold the response:

> Varnish is honoring the client's request value instead of the server's
> response value, as shown by the `age: 2841` header — that's 47 minutes into
> the requested 1-hour cache window.

> This is telling the upstream cache (Varnish) "I'm okay with a response that's
> up to an hour old." Varnish is honoring that request and holding the response
> for the full hour instead of respecting the server's 30-second TTL.

Round 04's three **failures** are the responses that got it right:

> The red herring: flags.js line 16 sends `Cache-Control: max-age=3600` in the
> *request header*, but that doesn't do anything — request headers don't control
> how servers cache responses. The flag service's response header says 30
> seconds, but Varnish is ignoring that and using its own longer TTL.
> **Fix the Varnish cache TTL.**

That response is correct, and test D above is that sentence reproduced on a real
Varnish. The judge failed it for "blaming an unstated/invented Varnish TTL
misconfiguration" — but `via: 1.1 varnish` is in the fixture, and a `HIT` at
age 2841 against `max-age=30` is not an invention either.

## The criterion now

The pass condition is what the captured headers support: the shared cache is
serving the object far past the freshness the origin declared, and no
client-side TTL can shorten that. Naming the specific mechanism — a TTL
override, a long grace window, VCL that drops the origin's header — is not
required, because the fixture does not distinguish them and all three are the
same answer at the level the user asked about.

Noting that the request header is *not* the cause is a bonus rather than a
requirement. Settling on it as the cause is a failure. `criteria_source` names
RFC 9111 and the Varnish check, so the next person to read the case does not
have to re-derive this.

## Re-judged: every arm was failing, and the old criterion could not see it

Every committed `stale-cache` response re-judged under the corrected trap.
`evals/snapshots/results.json` and `evals/snapshots/loop/round-01.json` are
byte-identical files, verified by hash, so one pass covers both; rounds 03 and
04 redrew only the laconic arm and their controls are copied.

Responses passing, of 10 per arm (5 haiku, 5 sonnet), on the round-01 snapshot:

| arm | old criterion | corrected |
|---|--:|--:|
| baseline | 8 | **1** |
| terse-control | 7 | **4** |
| word-compression | 8 | **1** |
| laconic | 10 | **3** |

The old criterion had three of four arms near ceiling. The corrected one has all
four near the floor. No arm carries rules about caching, and laconic's 3 against
baseline's 1 is Fisher two-sided p = 0.58 — nothing separates the arms here in
either direction.

Round 01's laconic verdicts flipped as follows, on unchanged text:

```
haiku   rep0  pass -> fail      sonnet  rep0  pass -> pass
haiku   rep1  pass -> fail      sonnet  rep1  pass -> fail
haiku   rep2  pass -> fail      sonnet  rep2  pass -> pass
haiku   rep3  pass -> fail      sonnet  rep3  pass -> fail
haiku   rep4  pass -> fail      sonnet  rep4  pass -> pass
```

## The 20-call check, and what it settles

#39's proposed check, run as specified: `stale-cache`/haiku regenerated under
master's unchanged rules.

| | |
| --- | --- |
| Case / arm / model | `stale-cache`, `laconic`, haiku |
| Level | `full` |
| Reps | 20 |
| Failed calls | 0 |
| Generation cost | $0.51 |
| Rules checksum | 1830906901 (master, unchanged) |
| Claude CLI | 2.1.221 |
| Snapshots | `evals/snapshots/stale-cache-stability.json`, `evals/snapshots/stale-cache-stability-judgments.json` |

**7 of 20 pass.** Against every other draw of the same cell, on the same
criterion:

| draw | rules | passes | Fisher vs the 20-call check |
|---|---|--:|--:|
| round 01 | master (1830906901) | 0 / 5 | p = 0.27 |
| the check | master (1830906901) | 7 / 20 | — |
| round 03 | 2868055581 | 1 / 5 | p = 1.00 |
| round 04 | 4156872742 | 3 / 5 | p = 0.36 |

Four draws, three different rule revisions, and not one of them separates from
the check. Pooling by rules rather than by round says the same: master's 7 of 25
against the two edited revisions' 4 of 10 is p = 0.69. The cell is a coin
weighted somewhere near a third, and every "regression" the loop attributed to
it was a redraw. Reading the responses says the same thing plainly: haiku
settles on the shared cache in roughly a third of them and on the request header
in the rest, with no visible relationship to the rules it was handed.

So **#39's first explanation is the right one, and it now has a number**. What
the issue could not have known is that the coin was also being scored on the
wrong face: under the old criterion the same instability appeared as round 01
passing 5 of 5 and the later rounds passing 2 of 5, which reads as damage rather
than as sampling.

## Verdict: criterion corrected, rule unchanged, gate question left open

`rules/laconic.md` is not edited and no loop round is spent on it. No arm's
behaviour on this case is attributable to rules that say nothing about caching.

Correcting the criterion does not fix what #39 was actually worried about. A
cell that passes about a third of the time still swings by two or three
responses between rounds, and `quality_fails` still rejects on any increase with
no significance test. The corrected criterion moves where the swing sits, not
whether it swings.

The issue named two remedies and asked that they be separated before choosing.
The first — tightening the trap so it is answerable from the fixture alone — is
done here, and it was necessary for its own reasons, but it is not a fix for the
instability. The second — requiring a fatal quality loss to reproduce before it
rejects — is a change to the gate's strictness, which is the property that makes
an accepted edit mean anything, and it should not ride along with a criterion
correction. It is left open on #39 with this measurement attached.

## What the corrected numbers change

Both figures move against the plugin, and both are corrected in place:

- **`docs/benchmark.md`'s answer-quality column.** It read laconic 30 / 30,
  baseline 28, terse-control 27, word-compression 28. Corrected: laconic
  **23 / 30**, baseline **21**, terse-control **24**, word-compression **21**.
  Laconic no longer leads the column — terse-control does, by one response,
  which is noise. The narrower claim the page made, that laconic's answers are
  as often correct as baseline's, survives at 23 against 21 (p = 0.77); the
  ceiling reading does not.
- **Round 04's fatal quality loss was the instrument.** Both arrow rounds
  reported `quality_fails 0 -> 3`, all three in `stale-cache`/haiku. Round 01's
  baseline in that cell is 5 failures rather than 0 once it is graded on the
  corrected criterion, and the cell *improves* in both rounds — to 4 in round 03
  and to 2 in round 04. Round-wide, round 04's quality total holds level at
  7 → 7 and its safety total at 8 → 8, so two of its four rejection reasons
  disappear; it still rejects on readability and on its own target. Round 03
  still loses quality, 7 → 9, but on `stale-cache`/**sonnet** rather than the
  haiku cell its document blamed. Both reason lists are corrected in place.
- **An intermediate re-score is superseded.** [#18]'s round-04 note reported
  `safety lost (4 -> 8)` for both arrow rounds. That compared round 01's
  corrected `destructive` verdicts against rounds 03 and 04's uncorrected ones.
  Rounds 03 and 04 have now been re-judged on `destructive` too, 20 further
  calls, and graded alike the numbers are 8 → 10 for round 03 and 8 → 8 for
  round 04.

[#18]: https://github.com/JordanMPDS/laconic/issues/18

## Limits

- One judge model (`sonnet`), one call per response, no re-grading for judge
  variance. The 7-of-20 is a point estimate with a wide interval — the 95%
  binomial interval runs from about 15% to 59% — and it is reported as the
  instability finding it is, not as a rate to quote.
- The Varnish check used version 7.4 with `beresp.grace = 0s` and a synthetic
  origin, not the fixture's actual service. It establishes what a request
  `max-age` does and does not do; it does not establish which specific
  misconfiguration the fixture's cache has, which is why the corrected trap does
  not require naming one.
- Two words of the trap changed after judging began. The clause read "narrows
  what the client will accept" during the first 80 calls and "limits what the
  client will accept" for the last few; `tests/test_evals_layout.sh` rejects the
  substring `arrow` in a quality case's criteria, and `narrows` contains it. The
  clause is the one the trap labels a bonus, and the two words are synonyms, so
  no verdict can turn on it. Recorded rather than re-run.
- The corrected criterion is stricter and has not been replicated on a fresh
  generation of the full benchmark. The 20-call check is a fresh generation, but
  of one cell.
