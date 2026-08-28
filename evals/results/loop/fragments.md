# Fragments and prose abbreviations: both halves of #11, measured

**Result: neither detector goes into `evals/bench/metrics.py`.** One of the two
already exists there and has for longer than the issue has; the other was built,
validated at 84.6% precision, and separates no arm from any other because the
thing it detects is almost absent from the corpus.

Everything here is offline against the committed snapshot
`evals/snapshots/results.json` (`rules_cksum` 1830906901, 440 responses, four
arms at n=5 over 11 cases and two models). No API calls were spent.

```sh
python3 evals/results/loop/fragments/detector.py                            # self-check
python3 evals/results/loop/fragments/detector.py evals/snapshots/results.json
```

## The abbreviation half was already done

#11 opens with:

> The readability gate watches three signals: arrows, article rate, and
> auxiliary-verb rate. [...] Telegraphic fragments and prose abbreviations are
> unmeasured.

That was true when it was written and had stopped being true the day before.
`ABBREV` landed in `b264734` on 2026-07-30, and `abbreviated_prose` is summed
into `violations` and therefore into `violations_total`, which is a fatal gate.
The issue was filed on 2026-07-31.

What is worth reporting is how little it fires: **3 hits in 440 responses**, one
in `baseline` and two in `word-compression`. The tight set (`impl`, `req`,
`resp`, `func`, `val`, `obj`, `arg`, `msg`, `err`, `w/`, `b/c`) describes a
register these models do not write in.

#11 proposes widening it to `config`, `repo`, `env`, `auth` and similar. Measured
on the same snapshot, that set fires **144 times**, a 48-fold rise:

| arm | proposed set | of which a filename or path | shipped `abbreviated_prose` |
| --- | --: | --: | --: |
| `baseline` | 30 | 12 | 1 |
| `laconic` | 36 | 16 | 0 |
| `terse-control` | 36 | 7 | 0 |
| `word-compression` | 42 | 14 | 2 |

By token: `auth` 95, `repo` 21, `db` 18, `config` 9, `env` 1.

Two things kill the widening. **`auth` alone is two thirds of it**, and it is
`auth.js` — the fixture filename in `walkthrough` — or "your auth service", which
is what the thing is called. Stripping inline code does not help, because a
filename in running prose is not in backticks. And **only `config` and `env`, ten
hits between them, are what the rule actually names**: "write `configuration`,
not `config`". The module's existing comment predicted this in one line, and it
was right:

> Deliberately tight. config, repo, auth, env and db are normal developer
> English; including them would fire on correct prose in every arm.

The arms are also within 30 to 42 of each other, so the widened counter would not
discriminate even if every hit were real.

## The fragment half was built, and detects nothing

`detector.py` is frozen, deterministic and stdlib-only. A segment is one sentence
of prose or the body of one bullet; a fragment is an admitted segment with no
finite verb. Finiteness is decided against a 900-verb lexicon of base forms,
inflected at import. **Participles are deliberately not evidence** — "Waiting
queue growing linearly" and "Not handling exceptions properly" are the shapes the
rule forbids, and an `-ing` or `-ed` form with no auxiliary in front of it is
what makes them fragments. Irregular past tenses are evidence, because they are
finite.

`criterion.md` was committed before any label was written. It excludes four
verbless shapes that are correct English: list lead-ins, headings and bold
labels, definition glosses, and residues of code stripping.

### Per arm

| arm | responses | prose segments | flagged | rate | responses with ≥1 |
| --- | --: | --: | --: | --: | --: |
| `baseline` | 110 | 903 | 1 | 0.11% | 1 |
| `laconic` | 110 | 843 | 4 | 0.47% | 4 |
| `terse-control` | 110 | 913 | 4 | 0.44% | 3 |
| `word-compression` | 110 | 933 | 4 | 0.43% | 4 |

**`word-compression` is the arm whose system prompt says "Drop articles and
filler words, abbreviate common terms, and use arrows instead of conjunctions."**
It is the positive control, and it is indistinguishable from every other arm:
Fisher p = 1.000 against `laconic`, p = 1.000 against `terse-control`, p = 0.369
against `baseline` — and that last one is in the direction of the telegraphic arm
having *more*, on a difference of three responses.

For contrast, the same arm separates cleanly on the metrics already in the gate:
its article rate is 8.65% against `laconic`'s 9.50%, and its auxiliary-verb rate
is 4.36% against 4.58%. The existing proxies see the effect. A direct fragment
count does not, because there is nothing left for it to see.

### Precision: 84.6%

All 13 flagged segments were labelled by hand against `criterion.md`, in
`labels.json`. Eleven are fragments:

    Monitoring/alerting for tokens still using old key                    terse-control
    Not handling exceptions properly (leaking the connection on error)    terse-control
    Calling `pool.connect()` directly and forgetting to `client.release()`  terse-control
    Cleaner than trying all keys blindly                                  word-compression
    UUID — specifically UUIDv7 (or ULID), not a random v4.                laconic

The third is quoted with its code spans restored; the detector reads it after
stripping them, as `Calling   directly and forgetting to`.

Two are not. Both are the definition-gloss exclusion reached through a bold label
rather than a bullet, so `PROSE_START` admits them:

    **Server response** (response-headers.txt): `cache-control: public, max-age=30` (30 seconds only)

A label, a filename and a value. Not running prose.

Four of the eleven are **elliptical** — `UUID — specifically UUIDv7`, dropping
"use" rather than a copula. They are marked `"elliptical": true` so a reader who
disagrees can subtract them; doing so leaves 7 fragments and changes no
conclusion.

### The limit: noun/verb homographs

The lexicon cannot be sized correctly, and the failure is not symmetric.

A 300-verb lexicon flags 81 segments, most of them ordinary sentences whose verb
is simply not on the list — "This module only reacts to a 401", "UUIDs sidestep
this entirely", "Any Redis hiccup silently bypasses rate limiting". Precision
around 35%.

The 900-verb lexicon rescues 43 of those. Four of the rescues are wrong, and the
homograph that caused each one is the vocabulary of this domain:

| segment | rescued by |
| --- | --- |
| Critical for race conditions | `race` |
| Harmless in practice, just inconsistent with the rest of the dedup story. | `practice` |
| Misconfigured to override the origin's `max-age=30` with the request's `max-age=3600`, or | `override`, `request` |
| UUID — specifically a time-ordered variant like UUIDv7 [...] | `like` |

`use`, `queue`, `check`, `cache`, `request`, `store`, `access`, `log`, `set`,
`match` and `race` are all noun/verb homographs, and they are exactly the head
nouns a telegraphic fragment in this corpus is built from: "All 20 connections in
use at every checkpoint", "Waiting queue growing linearly". Two of those misses
are asserted in the self-check so they cannot be quietly "fixed" — buying them
back costs every sentence that uses the same word as a verb.

Correcting for the four wrong rescues moves the true counts to `baseline` 2,
`laconic` 4, `terse-control` 5, `word-compression` 4. The conclusion does not
move.

## Why it is not in `metrics.py`

Fifteen fragments in 3,592 prose segments, and the arm explicitly instructed to
write telegraphically produces the same number as the arm instructed not to.
Adding this to `score()` would put a counter in the fatal `violations_total` sum
that fires roughly once per 110 responses and cannot tell the arms apart — a gate
component whose movement would be a coin flip, on the one counter [#103] already
records as clustered and hard to read.

The same reasoning `arrow_forms` and `structure_markers` are disclosure-only
applies here, one step further: a disclosure counter still has to disclose
something.

**What this does say about `rules/laconic.md`:** "No telegraphic fragments" is a
rule with almost no violations to prevent, in any arm, including one whose
instructions ask for the violation. It is not costing anything, and there is no
case for a round aimed at it.

## Reproducing

```sh
python3 evals/results/loop/fragments/detector.py                             # 25 assertions
python3 evals/results/loop/fragments/detector.py evals/snapshots/results.json  # the per-arm table
```

The self-check covers every exclusion #11 named — fenced blocks, inline spans,
paths, verbatim error strings — plus headings, table rows, blockquotes, list
lead-ins, definition glosses, hard-wrapped sentences, and the two known false
negatives.

[#103]: https://github.com/JordanMPDS/laconic/issues/103
