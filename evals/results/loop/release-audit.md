# The CLI release stamp was written once per pass, and 17 snapshots span one

**Date:** 2026-09-09
**Status:** an instrument measurement, not a round. No rule changed, no round is
accepted or rejected by it. Addresses [#272].

## What was wrong

`run.py` recorded `claude_cli_version` on every run, and the field looked like a
per-run stamp. It was not. The version was resolved once, at startup:

```python
# Resolved once, then stamped onto every run below.
cli_version = _cli_version(claude_bin)
```

`claude` is a symlink into a versioned payload, and an upgrade re-points it:

```
/home/jordan/.local/bin/claude -> /home/jordan/.local/share/claude/versions/2.1.266
```

So an upgrade during a pass takes effect on the very next generation — the next
`subprocess.run` resolves the symlink afresh — while the label stays on the
release the pass started under. A snapshot that spans a release therefore holds
runs that name a release they did not run on, and nothing in the file says so.

Round 57 stratified on exactly that field.

## Round 57, relabelled

The three payload files still on the machine date each release's arrival, and
`/home/jordan/.local/bin/claude` dates the last flip:

| release | active from |
|---|---|
| 2.1.263 | 2026-09-06T03:02:40Z |
| 2.1.265 | 2026-09-08T20:59:31Z |
| 2.1.266 | 2026-09-09T00:43:13Z |

Round 57's five generating invocations, with the label each wrote and the
releases its runs actually ran under:

| arm | invocation window | stamped | actually |
|---|---|---|---|
| A | 15:15:20 to 15:26:16 | 2.1.263 | 2.1.263 |
| A | 19:23:22 to 19:34:56 | 2.1.263 | 2.1.263 |
| A | 19:39:36 to 20:54:26 | 2.1.263 | 2.1.263 |
| A | 00:25:18 to 02:06:24 | 2.1.265 | **2.1.265 then 2.1.266** |
| A | 05:23:25 to 05:25:58 | 2.1.266 | 2.1.266 |
| B | three blocks to 20:54:35 | 2.1.263 | 2.1.263 |
| B | 00:25:10 to 01:40:23 | 2.1.265 | **2.1.265 then 2.1.266** |
| C | three blocks to 20:54:25 | 2.1.263 | 2.1.263 |
| C | 00:25:22 to 01:50:10 | 2.1.265 | **2.1.265 then 2.1.266** |

The `2.1.263` blocks are clean: all of them ended before 20:59:31. Every block
that started at 00:25 crossed 00:43:13 eighteen minutes later and ran the rest
of its hours on 2.1.266 under a 2.1.265 label. **540 of round 57's 1,440 runs
name a release they did not run on** — 201 in arm A, 156 in arm B, 183 in arm C.

Relabelled by timestamp, the round has three strata rather than two:

| release | A | B | C |
|---|--:|--:|--:|
| 2.1.263 | 108/225 (48.0%) | 162/276 (58.7%) | 138/254 (54.3%) |
| 2.1.265 | 28/45 (62.2%) | 29/48 (60.4%) | 22/43 (51.2%) |
| 2.1.266 | 130/210 (61.9%) | 93/156 (59.6%) | 122/183 (66.7%) |

## What the relabelling does and does not change

**It does not overturn round 57.** Every contrast the round registered stays
null on the corrected strata, and Mantel-Haenszel pooling over three releases
still rescues nothing:

| contrast | pooled | MH odds ratio | p |
|---|---|--:|--:|
| C against A (primary) | 282/480 against 266/480 | 1.184 | 0.2226 |
| B against A (secondary 1) | 284/480 against 266/480 | 1.205 | 0.1759 |
| C against B (secondary 2) | 282/480 against 284/480 | 0.967 | 0.8503 |

Two-sided Fisher within each release:

| release | C-A | B-A | C-B |
|---|--:|--:|--:|
| 2.1.263 | +6.33 (p = 0.1709) | **+10.70 (p = 0.0192)** | -4.36 (p = 0.3350) |
| 2.1.265 | -11.06 (p = 0.3896) | -1.81 (p = 1.0000) | -9.25 (p = 0.4043) |
| 2.1.266 | +4.76 (p = 0.3441) | -2.29 (p = 0.6663) | +7.05 (p = 0.2133) |

Round 57's post-hoc reading survives in shape: the B-A effect is present on
2.1.263 and absent after it. What was one post-boundary block is two releases,
and the larger of them, 2.1.266, is the one the round never knew it had bought.

**It does change what may be claimed from the field.** Round 57 read its strata
off labels that were wrong for 37.5% of the round, and the reading came out
right by luck rather than by construction: had the upgrade landed mid-block on
only one arm, the same procedure would have manufactured a difference between
arms out of a difference between releases. Nothing in the file would have shown
it.

## The archive

`python3 evals/bench/release.py` sweeps every committed snapshot. Seventeen span
more than one release and were stamped once per pass, so which release produced
which run is not recoverable from the file:

| snapshot | runs | releases |
|---|--:|---|
| `baseline-arm-n10` | 470 | 2.1.227, 2.1.232 |
| `quality-rates-design` | 180 | 2.1.227, 2.1.228 |
| `round-16` | 590 | 2.1.227, 2.1.228 |
| `round-17` | 590 | 2.1.227, 2.1.228 |
| `round-18` | 590 | 2.1.227, 2.1.228 |
| `round-19` | 590 | 2.1.227, 2.1.228 |
| `round-20` | 590 | 2.1.227, 2.1.232 |
| `round-21` | 590 | 2.1.227, 2.1.238, 2.1.239 |
| `round-21-n10` | 810 | 2.1.227, 2.1.238, 2.1.239 |
| `round-22` | 590 | 2.1.227, 2.1.238, 2.1.239 |
| `round-22-n10` | 810 | 2.1.227, 2.1.238, 2.1.239 |
| `round-24` | 590 | 2.1.227, 2.1.238, 2.1.240 |
| `round-31-control` | 240 | 2.1.251, 2.1.252 |
| `round-31-edit` | 240 | 2.1.251, 2.1.252 |
| `round-57-arm-a` | 480 | 2.1.263, 2.1.265, 2.1.266 |
| `round-57-arm-b` | 480 | 2.1.263, 2.1.265 |
| `round-57-arm-c` | 480 | 2.1.263, 2.1.265 |

That is **14,860 of the archive's 47,822 recorded runs**, 31%. How many carry a
wrong label is recoverable only for round 57, and only because that machine
still holds the payload files that date the releases. For the other fourteen
the answer is gone. No stored finding rests on the field — round 57 is the only
round that ever stratified on it — so nothing above needs re-scoring. What is
lost is the option of going back and asking.

## The two failures are different, and only one of them is new

**The labels being wrong** is a defect, and it is fixed: `run.py` now reads
`claude --version` before each generation and stamps the answer on that run. The
read costs about 20 ms against a generation of tens of seconds. A pass that
crosses a release prints a warning naming both releases and the run it happened
at, prints a second one at the end, and records `metadata.cli_versions`. A file
whose every run was stamped this way carries `cli_versions_per_run: true`, which
is what tells a later reader the field may be stratified on at all.

`judge.py` is not covered. It shells out to the same CLI and a judging pass takes
hours too, so a judgments file spans releases the same way and records no version
at all. Nothing stored stratifies verdicts by release, so no finding rests on it,
and it is left alone rather than fixed speculatively.

**The arms being imbalanced across a release** is not a defect and cannot be
fixed by a stamp. Round 57 ran its three arms simultaneously, which is the
protection the loop has been relying on since round 38, and simultaneity did not
deliver it: the arms split 225/246, 276/204 and 254/226 across their boundary,
because three processes generating at their own pace drift apart, and a usage
limit hits the slowest hardest. `release.py` tests it, each arm's share of each
release against the pooled rest, two-sided Fisher, Bonferroni over
`arms * (releases - 1)` tests:

```
python3 evals/bench/release.py evals/snapshots/loop/round-57-arm-{a,b,c}.json
```

Round 57 fails it. The correction is over the independent comparisons rather
than over the printed rows, and that is load-bearing: across two releases each
arm's two rows are one test read from either side, and paying for it twice puts
round 57's most skewed arm at 0.057 instead of 0.029, which is the tool letting
through the round it was built for.

## What this says about running a round inside one release

[#272] asks for the three arms re-run inside a single CLI release. On the
evidence here that is not something a round of this size can be designed to do.
Round 57 ran for fourteen hours and the CLI advanced from 2.1.263 to 2.1.266 in
that window, so at three or four hours a release the instrument changes several
times inside any round large enough to answer the question. Sizing the round
smaller does not help, because the effect it is chasing needs the runs.

So the answer is not to fit a round inside a release. It is:

- **Label every run correctly**, which is now true, so a span is measurable
  rather than assumed away.
- **Balance the arms across whatever boundaries land**, and check it rather than
  trust simultaneity to deliver it. `run.py` interleaves arms within one
  invocation, which balances them by construction; a round comparing two rules
  texts cannot use that, because `rules_cksum` is resolved once per invocation,
  so it needs the check.
- **Stratify, and say the strata are post-hoc**, because a release boundary is
  not something a registration can name in advance.

`--stop-on-cli-change` exists for a round whose design genuinely needs one
instrument throughout. It exits at the first generation that would run under a
new release, saving what was already done. It is not the default and should not
become one: a release landing mid-round is the ordinary case, and refusing it by
default would throw away most rounds.

[#272]: https://github.com/JordanMPDS/laconic/issues/272
