# Laconic — design

**Date:** 2026-07-30
**Status:** Approved design, ready for implementation planning

## Problem

Default assistant responses are padded: preamble, restated questions, unrequested
alternatives, closing offers, and recaps of work already visible in the diff.

The nearest existing tool, the `caveman` plugin, compresses at the word level: its
documented levels drop articles and conjunctions and abbreviate common terms
(`config` → `cfg`, `X → Y` for "X causes Y"). That is an effective way to reduce
token count, and it is what that project optimizes for.

Laconic targets a different dimension, because grammar carries information that
word-level compression can remove along with the words. "OOM → bump limit. Check
leak." does not distinguish "bump the limit" from "bump it only if there is no
leak" — the conjunction was the conditional. So laconic reduces the number of
claims a response makes and leaves each remaining sentence intact.

## Thesis

> Terse means fewer claims, not fewer words per claim.

Every response is ordinary English — complete sentences, real articles, real
conjunctions. What shrinks is the number of things said, not the legibility of
each thing.

## Scope

In scope:

- Three cumulative intensity levels: `lite`, `full`, `ultra`.
- Persistence across a long session, without re-injecting the full rule set every
  turn.
- An off switch that actually stops all injection.
- Distribution as a single-plugin GitHub marketplace.
- An eval suite that grades readability, not only length.

Out of scope for v1:

- Companion skills (`laconic-commit`, `laconic-review`). The prose mode has to
  prove itself first.
- Cross-tool manifests (Codex, Gemini, opencode). Claude Code only until someone
  asks.
- A token-counting benchmark harness. The two-arm runner prints per-arm word
  counts already; a tokenizer-accurate reduction number can wait until it is
  wanted for the README.
- Automatic statusline wiring. The badge script ships; the README documents the
  opt-in line.
- A native-Windows PowerShell port of the hook. Neither `pwsh` nor `powershell`
  exists on the development machine, so it cannot be verified here, and an
  unverified script that writes model context is worse than none. bash covers
  macOS, Linux, WSL, and Git Bash; add the port when a native-Windows user asks.

## Architecture

```
laconic/
├── .claude-plugin/
│   ├── plugin.json           name, version, author — no hooks key (auto-loaded)
│   └── marketplace.json      single-plugin marketplace; one repo serves both
├── hooks/
│   ├── hooks.json            SessionStart | UserPromptSubmit | SubagentStart
│   ├── laconic.sh            one script; $1 = start | subagent | remind
│   └── laconic-statusline.sh optional badge, not auto-wired
├── rules/
│   └── laconic.md            shared block + lite/full/ultra blocks
├── skills/
│   ├── laconic/SKILL.md      points at rules/laconic.md, handles switching
│   └── laconic-help/SKILL.md one-shot reference card
├── commands/
│   ├── laconic.toml          /laconic lite|full|ultra|off|status
│   └── laconic-help.toml
├── evals/
│   ├── CRITERIA.md           what a human checks in each arm
│   ├── run.sh                two-arm runner: each case with and without rules
│   └── {decision,walkthrough,destructive,badnews}/prompt.md
├── tests/
│   ├── test_laconic.sh       branches in laconic.sh and the badge
│   └── test_rules.sh         the marker contract awk depends on
├── README.md
└── LICENSE
```

### Single source of truth for the rules

The rules have two consumers: the hooks that inject them, and the `laconic` skill
that the model reads when the command is invoked. Duplicating the text between a
hook script and a `SKILL.md` is how those two drift apart.

`rules/laconic.md` is therefore the only copy. It opens with a shared block, then
carries one block per level, delimited by HTML comments:

```
<!-- level:lite -->
<!-- level:full -->
<!-- level:ultra -->
```

`laconic.sh` prints the shared block plus every block up to the active level, via
an eight-line `awk` filter. `SKILL.md` instructs the model to read the same file
rather than restating it.

Rejected alternatives: three separate rule files (four files once the never-cut
block gets its own, and no parsing saved that matters); rules inline in the hook
script as heredocs (forces `SKILL.md` to duplicate them — the drift bug,
reintroduced).

### State

One file, `~/.claude/.laconic-level`, containing exactly one of `lite`, `full`,
`ultra`, `off`. Three properties follow:

- **Nothing is injected until opt-in.** No flag file and no `LACONIC_DEFAULT`
  means all three hooks exit 0 silently. Installing the plugin changes nothing
  until `/laconic` runs.
- **`off` means off.** It fails the level whitelist, so every hook no-ops. This
  property is explicit because the opposite behavior was observed in practice:
  with caveman build `655b7d9c5431` installed, a `UserPromptSubmit` hook continued
  injecting `CAVEMAN MODE ACTIVE` after `/caveman off`. That plugin documents its
  off switch as the phrases "stop caveman" / "normal mode" rather than an
  argument, so the flag may simply have been outside what the hook read. Either
  way, a persistent mode needs one state that unambiguously stops every hook, and
  laconic makes that a tested guarantee.
- **Always-on is available but explicit.** `LACONIC_DEFAULT=full` in
  `settings.json` `env` writes the flag on first session start.

The flag file is read defensively: symlinks are refused (a local attacker could
otherwise point it at a file whose bytes are echoed into model context every
turn), the read is capped at 16 bytes, and the content must match the whitelist
or the hook emits nothing.

### Persistence

| Hook | Emits | Cost |
| --- | --- | --- |
| `SessionStart` (`startup\|resume\|clear\|compact`) | full rule set for the active level | ~250 tokens, once per session |
| `UserPromptSubmit` | one line: `LACONIC MODE ACTIVE (full)` | ~8 tokens per turn |
| `SubagentStart` | full rule set | once per subagent |

Rejected: session-start only (tone drifts back to verbose over a long session,
the known failure of skill-only approaches) and re-injecting the full rules every
turn, which caveman does — at roughly 250 tokens per turn that is about 50k tokens
across a 200-turn session, which is the cost this split avoids.

`UserPromptSubmit` does double duty. It greps its own stdin payload for
`/laconic <level>` and persists the match to the flag file, so switching levels
is durable without a second script. `jq` is not required.

### Level switching

`/laconic ultra` triggers two things. The `remind` hook sees the string in the
prompt payload and writes `ultra` to the flag file; separately, the command's own
prompt text carries the rules inline, so the new level applies to the very next
response instead of waiting for a session restart.

`/laconic` with no argument sets `full`. `/laconic status` writes nothing and asks
the model to report the current level and where the flag file lives, so a user who
has lost track can check without editing anything.

## The rule set

### Shared preamble (all levels)

Terse means fewer claims, not fewer words per claim. Write ordinary English —
complete sentences, real articles, real conjunctions. Delete content, never
grammar.

Two checks before sending:

1. What is the smallest set of claims that fully answers this?
2. Is anything here something the user did not ask for?

**Length scales to the request, at every level.** A yes/no question gets a word or
a line. A report, walkthrough, comparison, or explanation the user asked for gets
full detail. Laconic governs volunteered content; it never truncates requested
content.

### Never cut (all levels, including ultra)

- Code, config, commands, and error strings — verbatim and complete. Never
  abbreviate an identifier, never elide lines with `...`.
- Security warnings, and the reasoning that makes them actionable.
- Confirmation before destructive or irreversible actions, including exactly what
  will be affected.
- Anything the user asked to have explained: "why", "how", "walk me through",
  "explain".
- Ordered instructions: every step, and the words that fix their order ("before",
  "after", "first").
- Bad news: a failure, a broken test, a limit hit, a thing not done. Omitting it
  is not terseness.
- Uncertainty that changes what the user should do.

### `lite` — cuts ceremony

- No preamble. Do not restate the question, announce what is about to happen, or
  narrate tool calls the user can already see.
- No pleasantries or performative agreement: no "Great question", "Sure!",
  "You're absolutely right".
- No closing offers: no "Let me know if...", "Hope this helps".
- No stacked hedging. One qualifier or none: "Probably X", not "It might possibly
  be that X".
- No recap of work visible in the diff. Name the file and what changed. Reporting
  a failure, a skipped step, or a surprise is not a recap — that is never-cut
  content and stays.
- Keeps full reasoning, context, and trade-offs. Lite is normal professional prose
  with the ceremony stripped.

### `full` — adds: cuts unrequested substance

- Lead with the answer or the action taken. Reasoning only if the user needs it to
  act on the answer.
- One recommendation, not a survey. A real trade-off gets one line per side, then
  a pick.
- No unrequested alternatives, no "you could also".
- No teaching a concept the question already demonstrates the user knows.
- No next-steps list unless they asked what is next.
- Typical shape: one to three sentences, or a short list. One sentence is a
  complete answer.

### `ultra` — adds: cuts to the result

- The answer alone: a decision, a value, a `file:line`, a yes or no.
- Reasoning only where withholding it would make the answer unusable or unsafe.
- Still complete sentences. "Use a UUID." — not "UUID better".
- **Fallback rule:** if the answer genuinely does not fit in a line or two, ultra
  does not apply to this turn; answer at `full` instead. Never truncate something
  the user needs in order to hit a length target.

### Worked example (ships in the rules file and the README)

Question: *"Our deploy failed with an OOM kill on the worker. Should I bump the
memory limit?"*

| Level | Response |
| --- | --- |
| `lite` | "Bump it, but check the trend first. An OOM kill at a steady memory ceiling means the limit is too low; a climbing curve means a leak, and a bigger limit only delays the next kill. `kubectl top pod` over a few minutes tells you which one you have." |
| `full` | "Check the trend first. If memory sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and a bigger limit only delays the next kill. Watch `kubectl top pod` for a few minutes." |
| `ultra` | "Only if memory is flat, not climbing. Check `kubectl top pod` first." |

Ultra keeps the conditional, because dropping it would give wrong advice half the
time. That is the fallback rule working.

### Anti-patterns (explicit negative examples in the rules file)

No dropped articles. No telegraphic fragments. No abbreviated prose words
(`config`, `impl`, `req`, `res`). No arrows substituted for conjunctions in
running prose. The model gets the negative examples, not only the positive ones.

## Testing

### Eval suite

`claude plugin eval` is the natural home for this, and it supplies a no-plugin
baseline arm automatically — but it is gated behind early access
(`claude plugin eval init --bare probe` returns "`plugin eval` is currently in
early access"). Until it opens up, `evals/run.sh` stands in: for each case it
asks the same question twice, once plain and once with the rules injected via
`claude -p --append-system-prompt`, and writes both answers to one file with
their word counts for side-by-side reading. The treatment arm's system prompt
comes from running the real hook, so the eval exercises what ships rather than a
copy that can drift. The case layout ports to `plugin eval` unchanged.

Grading is by human review against `evals/CRITERIA.md`, which defines the same
two dimensions an LLM judge would have scored:

- **Terseness** — banned categories absent: preamble, closing offers,
  unrequested options, visible-work recaps.
- **Integrity** — no degraded grammar (missing articles, telegraphic fragments,
  abbreviated prose words) and no never-cut item dropped.

Cases:

| Case | Prompt shape | What it catches |
| --- | --- | --- |
| `decision` | "UUID or auto-increment PK for a sharded table?" | Padding on a question with a one-line answer |
| `walkthrough` | "Walk me through how our auth middleware refreshes tokens." | Over-compression of explicitly requested detail |
| `destructive` | "Drop the users table and reseed from the fixture." | Warning or blast radius omitted to stay short |
| `badnews` | "Did the tests pass?" against a repo with three failures | A failure hidden by brevity |

The last three are the credibility cases: they fail the plugin for compressing
too much. Caveman's harness measures token reduction, which suits what it
optimizes for; laconic's has to be able to fail a run for cutting too much, so
three of its four cases exist for exactly that.

### Unit check

`tests/test_laconic.sh` — plain asserts, no framework, covering the branching in
`laconic.sh`:

- flag absent → no output, exit 0
- flag `off` → no output
- flag `ultra; rm -rf /` → no output (whitelist rejects it)
- flag `lite` → shared and lite blocks present, full and ultra blocks absent
- flag `ultra` → all three blocks present
- `remind` with `/laconic off` in the payload → flag becomes `off`, no output
- `remind` with `/laconic status` in the payload → level unchanged
- `remind` with a valid level → one line only, not the whole rule set
- `LACONIC_DEFAULT=full` with no flag → flag seeded, rules emitted
- symlinked flag → no output (never dereferenced)

`tests/test_rules.sh` covers the marker contract `laconic.sh` depends on: exactly
one marker per level, in ascending order, with the thesis and never-cut list in
the shared block ahead of them.

The `off` assertion is the regression test for the off-switch guarantee above. If
`off` ever stops meaning off, the suite fails.

## Licensing note

The eval cases are written fresh. Caveman's three-arm eval design (baseline /
"Answer concisely." control / control-plus-skill) is a good idea worth crediting
in the README, but its code is not copied, so its license terms are not inherited.

## README outline

Install block; levels table with the worked example at all three levels; the
never-cut list; how to turn it off (`/laconic off`, and it actually stops); how to
make it permanent (`LACONIC_DEFAULT=full`); and an honest comparison with caveman
— caveman compresses at the word level, laconic at the claim level. Describe both
factually and let the reader pick; someone choosing between them deserves the
mechanism, not a verdict.
