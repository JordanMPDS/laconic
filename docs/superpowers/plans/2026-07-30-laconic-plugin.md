# Laconic Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a distributable Claude Code plugin named `laconic` that makes responses terse by cutting claim count rather than grammar, with three cumulative levels and an off switch that genuinely stops all injection.

**Architecture:** A single bash script (`hooks/laconic.sh`) is wired to three hook events. It reads one flag file (`~/.claude/.laconic-level`) and prints an `awk`-extracted slice of one markdown rule set (`rules/laconic.md`) — the full slice on session/subagent start, a one-line reminder on each prompt. The rules file is the only copy of the rules; the skill reads the same file rather than restating it. No flag, or a flag that fails the level whitelist, means every hook exits 0 having printed nothing.

**Tech Stack:** bash (3.2-compatible), POSIX `awk`, markdown, TOML command manifests, `git`. No runtime dependencies beyond a POSIX shell.

## Global Constraints

- Target **bash 3.2** (macOS ships it). No `mapfile`, no associative arrays, no `${var,,}`, no `+=` on arrays.
- **POSIX awk only.** No GNU extensions (`gensub`, `length(array)`, `asort`).
- **No `jq` dependency.** It is not installed on many target machines, including the development machine. Parse hook payloads with `grep`.
- Flag file path is `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level` — honor the env var everywhere, including the statusline script.
- Level whitelist is exactly `lite`, `full`, `ultra`, `off`. Anything else, including empty or malformed content, produces no output.
- Names, used verbatim: plugin `laconic`; command `/laconic`; flag file `.laconic-level`; env override `LACONIC_DEFAULT`; rules file `rules/laconic.md`; block markers `<!-- level:lite -->`, `<!-- level:full -->`, `<!-- level:ultra -->`.
- Sentinel phrases the tests grep for must appear verbatim in `rules/laconic.md`: `fewer claims` (shared), `No preamble` (lite), `One recommendation, not a survey` (full), `The answer alone` (ultra).
- Every script starts `#!/usr/bin/env bash` and is committed executable (`git update-index --chmod=+x` if needed).
- The plugin must never write to stdout when the level is `off` or unset. A single stray byte becomes model context.

## Deviations from the spec

Two, both discovered while verifying the spec's mechanics against this machine. Note them in the spec before starting Task 1.

1. **`claude plugin eval` is gated behind early access** (`claude plugin eval init --bare probe` returns "`plugin eval` is currently in early access"). Task 6 therefore builds `evals/run.sh` on top of `claude -p --append-system-prompt`, which is available, and grades by human review against written criteria instead of an LLM judge. The four case prompts are authored in a layout that ports to `plugin eval` when it opens up.
2. **No `hooks/laconic.ps1` in v1.** Neither `pwsh` nor `powershell` exists on this machine, so a PowerShell port cannot be tested here, and shipping an unverified script that writes model context is worse than not shipping it. The README states the requirement: bash, which covers macOS, Linux, WSL, and Git Bash. Add the port when a native-Windows user asks for it.

## File Structure

| File | Responsibility |
| --- | --- |
| `.claude-plugin/plugin.json` | Plugin manifest: name, version, description, author. Deliberately no `hooks` key — see Task 1 Step 4 |
| `.claude-plugin/marketplace.json` | Single-plugin marketplace so one repo serves both roles |
| `rules/laconic.md` | The only copy of the rule set; shared block plus three level blocks |
| `hooks/laconic.sh` | Reads the flag, extracts the rule slice, prints it. All logic lives here |
| `hooks/hooks.json` | Wires `laconic.sh` to SessionStart, SubagentStart, UserPromptSubmit |
| `hooks/laconic-statusline.sh` | Optional `[LACONIC:FULL]` badge; opt-in, never auto-wired |
| `skills/laconic/SKILL.md` | Level switching; points at `rules/laconic.md` instead of restating it |
| `skills/laconic-help/SKILL.md` | One-shot reference card |
| `commands/laconic.toml` | `/laconic lite\|full\|ultra\|off\|status` |
| `commands/laconic-help.toml` | `/laconic-help` |
| `tests/test_laconic.sh` | Asserts over every branch in `laconic.sh` and the statusline |
| `tests/test_rules.sh` | Asserts the marker contract `laconic.sh` depends on |
| `evals/run.sh` | Two-arm runner: each case with and without the rules |
| `evals/<case>/prompt.md` | Four case prompts |
| `evals/CRITERIA.md` | What a human checks in each arm's output |
| `README.md` | Install, levels, never-cut list, off switch, caveman comparison |
| `LICENSE` | MIT |

---

### Task 1: Manifests and repo skeleton

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `LICENSE`
- Create: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `plugin.json` with NO `hooks` key. `hooks/hooks.json` at the standard path is auto-loaded by the runtime; declaring it as well loads it twice and the plugin fails outright with "Duplicate hooks file detected". Plugin name `laconic`, version `0.1.0`.

- [ ] **Step 1: Write the manifest**

`.claude-plugin/plugin.json`:

```json
{
  "name": "laconic",
  "version": "0.1.0",
  "description": "Terse responses that stay readable. Cuts claim count, not grammar: no preamble, no unrequested options, no recaps — with complete sentences at every level.",
  "author": {
    "name": "Jordan Martinetti",
    "url": "https://github.com/JordanMPDS"
  }
}
```

- [ ] **Step 2: Write the marketplace manifest**

`.claude-plugin/marketplace.json`:

```json
{
  "name": "laconic",
  "description": "Terse responses that stay readable. Cuts claim count, not grammar: no preamble, no unrequested options, no recaps — with complete sentences at every level.",
  "owner": {
    "name": "Jordan Martinetti"
  },
  "plugins": [
    {
      "name": "laconic",
      "source": "./",
      "description": "Terse responses that stay readable. Cuts claim count, not grammar."
    }
  ]
}
```

The top-level `description` is required, not decorative: `claude plugin validate --strict` treats a missing marketplace description as an error (`✘ Validation failed (--strict treats warnings as errors)`).

- [ ] **Step 3: Write LICENSE and .gitignore**

`LICENSE` — MIT, copyright `2026 Jordan Martinetti`. Use the standard MIT text verbatim.

`.gitignore`:

```
evals/results/
.superpowers/
*.tmp
```

- [ ] **Step 4: Validate**

Run: `claude plugin validate . --strict`
Expected: passes. Do **not** add a `hooks` key pointing at `hooks/hooks.json`. `validate --strict`
accepts it, but the runtime refuses to load the plugin: the standard `hooks/hooks.json` is loaded
automatically, so a manifest reference makes it a duplicate and the whole plugin fails with
"Duplicate hooks file detected". `manifest.hooks` is only for *additional* hook files. This bug
shipped in v0.1.0 and was caught only by installing from the marketplace — neither validate
invocation nor the skills-dir install surfaced it.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin LICENSE .gitignore
git commit -m "feat: plugin and marketplace manifests"
```

---

### Task 2: The rule set and its marker contract

**Files:**
- Create: `rules/laconic.md`
- Test: `tests/test_rules.sh`

**Interfaces:**
- Consumes: nothing.
- Produces: `rules/laconic.md` containing, in this order: a shared block with no marker, then `<!-- level:lite -->`, `<!-- level:full -->`, `<!-- level:ultra -->`, each on its own line with no trailing whitespace. Task 3's `awk` filter depends on this exact ordering and syntax. Sentinel phrases per the Global Constraints.

- [ ] **Step 1: Write the failing test**

`tests/test_rules.sh`:

```bash
#!/usr/bin/env bash
# Asserts the marker contract that hooks/laconic.sh depends on.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES="$ROOT/rules/laconic.md"
fails=0

fail() { printf 'FAIL %s\n' "$1"; fails=$((fails + 1)); }
ok()   { printf 'ok   %s\n' "$1"; }

[ -f "$RULES" ] || { fail "rules file exists"; printf '\n%d failure(s)\n' 1; exit 1; }
ok "rules file exists"

for m in lite full ultra; do
  n=$(grep -c "^<!-- level:$m -->$" "$RULES" || true)
  if [ "$n" = "1" ]; then ok "exactly one $m marker"; else fail "exactly one $m marker (found $n)"; fi
done

lite_ln=$(grep -n "^<!-- level:lite -->$"  "$RULES" | cut -d: -f1)
full_ln=$(grep -n "^<!-- level:full -->$"  "$RULES" | cut -d: -f1)
ultra_ln=$(grep -n "^<!-- level:ultra -->$" "$RULES" | cut -d: -f1)
if [ "$lite_ln" -lt "$full_ln" ] && [ "$full_ln" -lt "$ultra_ln" ]; then
  ok "markers in ascending order"
else
  fail "markers in ascending order (lite=$lite_ln full=$full_ln ultra=$ultra_ln)"
fi

# The shared block is everything before the first marker. It must carry the
# thesis and the never-cut list, because those apply at every level.
shared=$(sed -n "1,$((lite_ln - 1))p" "$RULES")
for phrase in "fewer claims" "Never cut" "Security warnings" "Length scales to the request"; do
  case "$shared" in
    *"$phrase"*) ok "shared block contains: $phrase" ;;
    *) fail "shared block contains: $phrase" ;;
  esac
done

# Sentinels the unit tests for laconic.sh grep for, one per level block. Each check
# is scoped to its own block: an unscoped grep would still pass if a sentinel drifted
# across a marker into the wrong block, which is exactly the drift that breaks Task 3.
last_ln=$(wc -l < "$RULES")
lite_block=$(sed -n "$((lite_ln + 1)),$((full_ln - 1))p"  "$RULES")
full_block=$(sed -n "$((full_ln + 1)),$((ultra_ln - 1))p" "$RULES")
ultra_block=$(sed -n "$((ultra_ln + 1)),${last_ln}p"      "$RULES")

case "$lite_block" in
  *"No preamble"*) ok "lite sentinel in lite block" ;;
  *) fail "lite sentinel in lite block" ;;
esac
case "$full_block" in
  *"One recommendation, not a survey"*) ok "full sentinel in full block" ;;
  *) fail "full sentinel in full block" ;;
esac
case "$ultra_block" in
  *"The answer alone"*) ok "ultra sentinel in ultra block" ;;
  *) fail "ultra sentinel in ultra block" ;;
esac

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
```

- [ ] **Step 2: Run it to make sure it fails**

Run: `bash tests/test_rules.sh`
Expected: FAIL — `FAIL rules file exists`, exit 1.

- [ ] **Step 3: Write `rules/laconic.md`**

Copy the rule set from the spec's "The rule set" section verbatim, arranged as shared block, then the three marked blocks. The shared block covers the thesis, the two pre-send checks, the length-scaling rule, the never-cut list, the worked example, and the anti-pattern list. Structure:

```markdown
# Laconic mode

Terse means fewer claims, not fewer words per claim. Write ordinary English —
complete sentences, real articles, real conjunctions. Delete content, never
grammar.

Two checks before sending:

1. What is the smallest set of claims that fully answers this?
2. Is anything here something the user did not ask for?

**Length scales to the request, at every level.** A yes/no question gets a word
or a line. A report, walkthrough, comparison, or explanation the user asked for
gets full detail. Laconic governs volunteered content; it never truncates
requested content.

## Never cut (every level, including ultra)

- Code, config, commands, and error strings — verbatim and complete. Never
  abbreviate an identifier, never elide lines with `...`.
- Security warnings, and the reasoning that makes them actionable.
- Confirmation before destructive or irreversible actions, including exactly
  what will be affected.
- Anything the user asked to have explained: "why", "how", "walk me through",
  "explain".
- Ordered instructions: every step, and the words that fix their order
  ("before", "after", "first").
- Bad news: a failure, a broken test, a limit hit, a thing not done. Omitting
  it is not terseness.
- Uncertainty that changes what the user should do.

## Never do this

No dropped articles. No telegraphic fragments. No abbreviated prose words
(`config`, `impl`, `req`, `res`). No arrows standing in for conjunctions in
running prose. Shorter is not the goal; fewer claims is.

<!-- level:lite -->

## Level: lite — cut ceremony

No preamble. Do not restate the question, announce what is about to happen, or
narrate tool calls the user can already see.

- No pleasantries or performative agreement: no "Great question", "Sure!",
  "You're absolutely right".
- No closing offers: no "Let me know if...", "Hope this helps".
- No stacked hedging. One qualifier or none: "Probably X", not "It might
  possibly be that X".
- No recap of work visible in the diff. Name the file and what changed.
  Reporting a failure, a skipped step, or a surprise is not a recap — that is
  never-cut content and stays.

Keeps full reasoning, context, and trade-offs. Lite is normal professional
prose with the ceremony stripped.

<!-- level:full -->

## Level: full — also cut unrequested substance

- Lead with the answer or the action taken. Reasoning only if the user needs it
  to act on the answer.
- One recommendation, not a survey. A real trade-off gets one line per side,
  then a pick.
- No unrequested alternatives, no "you could also".
- No teaching a concept the question already shows the user knows.
- No next-steps list unless they asked what is next.

Typical shape: one to three sentences, or a short list. One sentence is a
complete answer.

<!-- level:ultra -->

## Level: ultra — also cut to the result

The answer alone: a decision, a value, a `file:line`, a yes or no.

- Reasoning only where withholding it would make the answer unusable or unsafe.
- Still complete sentences. "Use a UUID." — not "UUID better".
- **Fallback:** if the answer genuinely does not fit in a line or two, ultra
  does not apply this turn. Answer at `full` instead. Never truncate something
  the user needs in order to hit a length target.
```

Also include the spec's worked example (the OOM question at all three levels) in the shared block, immediately before `## Never do this`, so the model sees a concrete rendering of every level regardless of which level is active.

- [ ] **Step 4: Run the test to verify it passes**

Run: `bash tests/test_rules.sh`
Expected: every line `ok`, `0 failure(s)`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add rules/laconic.md tests/test_rules.sh
git commit -m "feat: laconic rule set with level markers"
```

---

### Task 3: The hook script

**Files:**
- Create: `hooks/laconic.sh`
- Test: `tests/test_laconic.sh`

**Interfaces:**
- Consumes: `rules/laconic.md` and its marker contract from Task 2.
- Produces: `hooks/laconic.sh <mode>` where mode is `start`, `subagent`, or `remind`. `start` and `subagent` print the rule slice for the active level; `remind` prints one line and persists any `/laconic <level>` found on stdin. Exit status is always 0. Task 4's `hooks.json` invokes exactly these three modes.

- [ ] **Step 1: Write the failing test**

`tests/test_laconic.sh`:

```bash
#!/usr/bin/env bash
# Unit checks for hooks/laconic.sh. No framework: explicit asserts, bash 3.2 safe.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/hooks/laconic.sh"
CLAUDE_CONFIG_DIR="$(mktemp -d)"
export CLAUDE_CONFIG_DIR
FLAG="$CLAUDE_CONFIG_DIR/.laconic-level"
trap 'rm -rf "$CLAUDE_CONFIG_DIR"' EXIT
fails=0

fail() { printf 'FAIL %s\n' "$1"; fails=$((fails + 1)); }
ok()   { printf 'ok   %s\n' "$1"; }

assert_empty() {
  if [ -z "$2" ]; then ok "$1"; else fail "$1 — expected no output, got: $2"; fi
}

# Capture stdout, stderr, and exit status together. Checking stdout alone is not
# enough for the silent cases: a missing script, a syntax error, or a crash all
# produce empty stdout too, so an assert that only reads stdout passes against a
# script that never ran. That is the one guarantee this suite exists to prove.
run() { # run <mode> [stdin-string]; sets out, err, rc
  if [ -n "${2:-}" ]; then
    out=$(printf '%s' "$2" | bash "$SCRIPT" "$1" 2>"$CLAUDE_CONFIG_DIR/stderr"); rc=$?
  else
    out=$(bash "$SCRIPT" "$1" </dev/null 2>"$CLAUDE_CONFIG_DIR/stderr"); rc=$?
  fi
  err=$(cat "$CLAUDE_CONFIG_DIR/stderr")
}

assert_silent() { # deliberate silence, not a crash
  assert_empty "$1 (stdout)" "$out"
  assert_empty "$1 (stderr)" "$err"
  if [ "$rc" = "0" ]; then ok "$1 (rc=0)"; else fail "$1 — rc=$rc"; fi
}
assert_has() {
  case "$3" in *"$2"*) ok "$1" ;; *) fail "$1 — output missing: $2" ;; esac
}
assert_lacks() {
  case "$3" in *"$2"*) fail "$1 — output should not contain: $2" ;; *) ok "$1" ;; esac
}

set_level() { printf '%s' "$1" > "$FLAG"; }

# No case below wants an inherited default; the two that test seeding set it inline.
unset LACONIC_DEFAULT

# 1. No flag file and no default: the plugin is inert.
rm -f "$FLAG"
run start
assert_silent "no flag file"

# 2. off means off. The off-switch regression.
set_level off
run start
assert_silent "level off"

# 3. Garbage in the flag file is rejected by the whitelist, not echoed.
set_level 'ultra; rm -rf /'
run start
assert_silent "malformed level"

# 4. lite gets the shared and lite blocks only.
set_level lite
out=$(bash "$SCRIPT" start </dev/null)
assert_has   "lite has shared block"  "fewer claims" "$out"
assert_has   "lite has lite block"    "No preamble" "$out"
assert_lacks "lite omits full block"  "One recommendation, not a survey" "$out"
assert_lacks "lite omits ultra block" "The answer alone" "$out"

# 5. full gets shared + lite + full, not ultra.
set_level full
out=$(bash "$SCRIPT" start </dev/null)
assert_has   "full has lite block"    "No preamble" "$out"
assert_has   "full has full block"    "One recommendation, not a survey" "$out"
assert_lacks "full omits ultra block" "The answer alone" "$out"

# 6. ultra is cumulative: all three blocks.
set_level ultra
out=$(bash "$SCRIPT" start </dev/null)
assert_has "ultra has lite block"  "No preamble" "$out"
assert_has "ultra has full block"  "One recommendation, not a survey" "$out"
assert_has "ultra has ultra block" "The answer alone" "$out"

# 7. subagent mode behaves like start.
out=$(bash "$SCRIPT" subagent </dev/null)
assert_has "subagent emits rules" "The answer alone" "$out"

# 8. remind is one line, not the whole rule set.
set_level full
out=$(printf '{"prompt":"fix the test"}' | bash "$SCRIPT" remind)
assert_has   "remind names the level" "LACONIC MODE ACTIVE (full)" "$out"
assert_lacks "remind is not the rules" "No preamble" "$out"

# 9. A /laconic switch in the payload persists.
out=$(printf '{"prompt":"/laconic ultra"}' | bash "$SCRIPT" remind)
assert_has "switch persists to flag" "ultra" "$(cat "$FLAG")"
assert_has "switch reports new level" "LACONIC MODE ACTIVE (ultra)" "$out"

# 10. /laconic off both persists and silences in the same turn. The central
# promise of the whole plugin, so it gets full run/assert_silent coverage
# rather than a stdout-only check.
run remind '{"prompt":"/laconic off"}'
assert_has    "off persists to flag" "off" "$(cat "$FLAG")"
assert_silent "off silences immediately"

# 11. /laconic status must not be mistaken for a level.
set_level full
out=$(printf '{"prompt":"/laconic status"}' | bash "$SCRIPT" remind)
assert_has "status leaves level alone" "full" "$(cat "$FLAG")"

# 12. LACONIC_DEFAULT seeds the flag when absent.
rm -f "$FLAG"
out=$(LACONIC_DEFAULT=full bash "$SCRIPT" start </dev/null)
assert_has "default seeds flag" "full" "$(cat "$FLAG")"
assert_has "default emits rules" "One recommendation, not a survey" "$out"

# 13. A symlinked flag is refused rather than dereferenced.
rm -f "$FLAG"
printf 'full' > "$CLAUDE_CONFIG_DIR/decoy"
ln -s "$CLAUDE_CONFIG_DIR/decoy" "$FLAG"
run start
assert_silent "symlinked flag emits nothing"
rm -f "$FLAG"

# 14. The remind-mode write guard: never write THROUGH a symlinked flag. Without
# this, /laconic ultra would clobber the link target and the read-path check would
# then exit silently, so no other assert in this suite would notice.
rm -f "$FLAG"
printf 'keep' > "$CLAUDE_CONFIG_DIR/decoy"
ln -s "$CLAUDE_CONFIG_DIR/decoy" "$FLAG"
run remind '{"prompt":"/laconic ultra"}'
assert_silent "symlinked flag on remind"
assert_has "symlinked flag not written through" "keep" "$(cat "$CLAUDE_CONFIG_DIR/decoy")"
rm -f "$FLAG"

# 15. Prose mentioning the command must not switch the level. A prompt that only
# talks about /laconic — including one asking whether "off" works — must leave the
# stored level alone. Otherwise prompt text can re-enable the mode after off,
# which is the exact defect this plugin exists to avoid.
set_level full
run remind '{"prompt":"does /laconic off actually work?"}'
assert_has "prose does not switch level" "full" "$(cat "$FLAG")"
run remind '{"prompt":"the docs say run /laconic lite to switch"}'
assert_has "prose mid-sentence does not switch" "full" "$(cat "$FLAG")"
run remind '{"cwd":"/home/jordan/projects/laconic","prompt":"off topic"}'
assert_has "path containing laconic does not switch" "full" "$(cat "$FLAG")"

# 16. A real slash command still switches, including with extra spaces.
run remind '{"session_id":"x","prompt":"/laconic  lite"}'
assert_has "real command still switches" "lite" "$(cat "$FLAG")"

# 17. An invalid LACONIC_DEFAULT must not create a flag file at all — a persisted
# typo would be rejected by the whitelist forever with no way to re-seed.
rm -f "$FLAG"
LACONIC_DEFAULT=fulll run start
assert_silent "invalid default emits nothing"
if [ -f "$FLAG" ]; then fail "invalid default must not create the flag file"; else ok "invalid default leaves no flag file"; fi

# 18. An unknown mode does nothing rather than falling through to the rule slice.
set_level ultra
run bogus
assert_silent "unknown mode"

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
```

- [ ] **Step 2: Run it to make sure it fails**

Run: `bash tests/test_laconic.sh`
Expected: FAIL on every assert — `hooks/laconic.sh` does not exist yet, so each `bash "$SCRIPT"` prints "No such file or directory" to stderr and the captured stdout is empty. The `assert_has` cases fail; exit 1.

- [ ] **Step 3: Write the implementation**

`hooks/laconic.sh`:

```bash
#!/usr/bin/env bash
# laconic — emit the active rule set for Claude Code hooks.
# Usage: laconic.sh start|subagent|remind
#   start, subagent  print the rule slice for the active level
#   remind           persist any "/laconic <level>" on stdin, print one line
# Prints nothing at all unless a valid level is active.
set -uo pipefail

MODE="${1:-}"
case "$MODE" in
  start|subagent|remind) ;;
  *) exit 0 ;;   # unknown or missing mode: do nothing rather than guess
esac

CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
FLAG="$CONFIG_DIR/.laconic-level"
RULES="$(cd "$(dirname "$0")/.." && pwd)/rules/laconic.md"

# On UserPromptSubmit the hook payload arrives on stdin as JSON. Grep it rather
# than requiring jq, which is not present on many target machines. The match is
# anchored to the "prompt" field's opening quote so only a prompt that STARTS
# with the slash command switches the level: prose like "does /laconic off
# actually work?" must not flip it, and must never re-enable the mode after the
# user set off. "status" is absent from the alternation so it cannot be stored.
if [ "$MODE" = "remind" ]; then
  payload=$(cat)
  switch=$(printf '%s' "$payload" \
    | grep -oE '"prompt"[[:space:]]*:[[:space:]]*"/laconic +(lite|full|ultra|off)' \
    | grep -oE '(lite|full|ultra|off)$' \
    | tail -1) || switch=""
  # This write precedes the read-path symlink check below, so it needs its own
  # guard: without it, /laconic ultra against a symlinked flag would write
  # through the link into an attacker-chosen file.
  if [ -n "${switch:-}" ] && [ ! -L "$FLAG" ]; then
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    { printf '%s' "$switch" > "$FLAG"; } 2>/dev/null || true
  fi
fi

# Never read through a symlinked flag. The whitelist below already stops foreign
# bytes from reaching stdout; this check's real job is the write guard above.
# Do not delete it as redundant.
[ -L "$FLAG" ] && exit 0

if [ ! -f "$FLAG" ]; then
  # Opt-in only: with no flag and no configured default, do nothing.
  [ -n "${LACONIC_DEFAULT:-}" ] || exit 0
  # Validate before persisting. An unvalidated typo (LACONIC_DEFAULT=fulll)
  # would create a flag file the whitelist rejects forever, and because the file
  # now exists it would never be re-seeded — a silent, permanent brick.
  case "$LACONIC_DEFAULT" in
    lite|full|ultra|off) ;;
    *) exit 0 ;;
  esac
  mkdir -p "$CONFIG_DIR" 2>/dev/null || true
  { printf '%s' "$LACONIC_DEFAULT" > "$FLAG"; } 2>/dev/null || exit 0
fi

# Cap the read and strip everything outside [a-z] so malformed contents cannot
# reach the terminal or the model. The whitelist below is the real gate.
LEVEL=$(head -c 16 "$FLAG" 2>/dev/null | tr -cd 'a-z')
case "$LEVEL" in
  lite)  RANK=1 ;;
  full)  RANK=2 ;;
  ultra) RANK=3 ;;
  *)     exit 0 ;;
esac

if [ "$MODE" = "remind" ]; then
  printf 'LACONIC MODE ACTIVE (%s). Fewer claims, normal grammar. Cut content, not words.\n' "$LEVEL"
  exit 0
fi

[ -f "$RULES" ] || exit 0

# Print the shared block (rank 0) plus every block up to the active level.
awk -v want="$RANK" '
  BEGIN                    { rank = 0 }
  /^<!-- level:lite -->$/  { rank = 1; next }
  /^<!-- level:full -->$/  { rank = 2; next }
  /^<!-- level:ultra -->$/ { rank = 3; next }
  rank <= want
' "$RULES"
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `chmod +x hooks/laconic.sh && bash tests/test_laconic.sh`
Expected: every line `ok`, `0 failure(s)`, exit 0.

If assert 9 fails because the second `grep -oE '(lite|full|ultra|off)$'` finds nothing, the anchor is the problem — the first grep's match ends with the level, so `$` should hold; drop the `$` and keep `tail -1` if it does not.

- [ ] **Step 5: Commit**

```bash
git add hooks/laconic.sh tests/test_laconic.sh
git commit -m "feat: hook script with level whitelist and off switch"
```

---

### Task 4: Hook wiring and the statusline badge

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/laconic-statusline.sh`
- Modify: `tests/test_laconic.sh` (append the statusline and manifest asserts below)

**Interfaces:**
- Consumes: `hooks/laconic.sh` from Task 3, invoked as `start`, `subagent`, `remind`.
- Produces: `hooks/hooks.json` at the path `plugin.json` declares. `hooks/laconic-statusline.sh` prints `[LACONIC]` or `[LACONIC:LEVEL]` and nothing when inactive.

- [ ] **Step 0: Finish converting the silent asserts (carried over from Task 3)**

Three cases still assert on stdout alone, which is the weakness Task 3's `assert_silent`
helper was added to close — an empty stdout is also what a crashed script produces.
Convert each to `run` + `assert_silent`, keeping every other line as-is:

- case 10, `off silences immediately` — the central promise, so it should be the
  best-covered assert in the file, not the weakest
- case 13, `symlinked flag emits nothing`
- case 17, `invalid default emits nothing` — keep its companion flag-file-existence
  check, which is the load-bearing half

Run the suite after converting and confirm the count grows by the added
stdout/stderr/rc triples with no failures.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_laconic.sh`, before the final `printf '\n%d failure(s)\n'` line:

```bash
# --- hooks.json ---
HOOKS="$ROOT/hooks/hooks.json"
if [ -f "$HOOKS" ]; then ok "hooks.json exists"; else fail "hooks.json exists"; fi
if python3 -c "import json,sys;json.load(open('$HOOKS'))" 2>/dev/null; then
  ok "hooks.json is valid JSON"
else
  fail "hooks.json is valid JSON"
fi
# Assert the event-to-mode pairing, not just that the event name appears somewhere.
# laconic.sh's mode gate exits 0 silently on any argument other than start/subagent/
# remind, so a typo like "subagnet" would disable that hook with no other symptom,
# and a substring check for the event name alone would still pass.
for pair in "SessionStart:start" "SubagentStart:subagent" "UserPromptSubmit:remind"; do
  ev=${pair%:*}; mode=${pair#*:}
  found=$(python3 -c "
import json
d = json.load(open('$HOOKS'))['hooks']
print(' '.join(h['command'].split()[-1].strip('\"')
               for g in d.get('$ev', []) for h in g['hooks']))
" 2>/dev/null)
  if [ "$found" = "$mode" ]; then
    ok "hooks.json wires $ev -> $mode"
  else
    fail "hooks.json wires $ev -> $mode (got: ${found:-nothing})"
  fi
done

# The SessionStart matcher is load-bearing: without it the rules would not reload
# after /clear or a compaction, and the mode would appear to silently lapse.
matcher=$(python3 -c "
import json
print(json.load(open('$HOOKS'))['hooks']['SessionStart'][0].get('matcher', ''))
" 2>/dev/null)
if [ "$matcher" = "startup|resume|clear|compact" ]; then
  ok "SessionStart matcher covers startup/resume/clear/compact"
else
  fail "SessionStart matcher (got: ${matcher:-nothing})"
fi

# --- statusline ---
BADGE="$ROOT/hooks/laconic-statusline.sh"
rm -f "$FLAG"
out=$(bash "$BADGE" 2>/dev/null)
assert_empty "badge silent with no flag" "$out"
set_level off
out=$(bash "$BADGE" 2>/dev/null)
assert_empty "badge silent when off" "$out"
set_level full
out=$(bash "$BADGE" 2>/dev/null)
assert_has "badge shows plain name at full" "[LACONIC]" "$out"
set_level ultra
out=$(bash "$BADGE" 2>/dev/null)
assert_has "badge shows level when not full" "[LACONIC:ULTRA]" "$out"
rm -f "$FLAG"
```

- [ ] **Step 2: Run it to make sure it fails**

Run: `bash tests/test_laconic.sh`
Expected: the twelve original asserts pass; the new ones fail — `FAIL hooks.json exists`, `FAIL badge shows plain name at full`, and so on. Exit 1.

- [ ] **Step 3: Write `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/laconic.sh\" start",
            "timeout": 5,
            "statusMessage": "Loading laconic rules..."
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/laconic.sh\" subagent",
            "timeout": 5,
            "statusMessage": "Loading laconic rules..."
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/laconic.sh\" remind",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Write `hooks/laconic-statusline.sh`**

```bash
#!/usr/bin/env bash
# laconic — optional statusline badge. Opt in by adding to settings.json:
#   "statusLine": { "type": "command",
#                   "command": "bash \"$HOME/.claude/plugins/.../hooks/laconic-statusline.sh\"" }
FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level"

# Same hardening as the hook: never dereference a symlinked flag, never echo
# bytes that failed the whitelist.
[ -L "$FLAG" ] && exit 0
[ -f "$FLAG" ] || exit 0

MODE=$(head -c 16 "$FLAG" 2>/dev/null | tr -cd 'a-z')
case "$MODE" in
  lite|full|ultra) ;;
  *) exit 0 ;;
esac

COLOR=108
[ "$MODE" = "ultra" ] && COLOR=173

if [ "$MODE" = "full" ]; then
  printf '\033[38;5;%sm[LACONIC]\033[0m' "$COLOR"
else
  printf '\033[38;5;%sm[LACONIC:%s]\033[0m' "$COLOR" "$(printf '%s' "$MODE" | tr '[:lower:]' '[:upper:]')"
fi
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `chmod +x hooks/laconic-statusline.sh && bash tests/test_laconic.sh && bash tests/test_rules.sh && claude plugin validate . --strict`
Expected: all asserts `ok`, `0 failure(s)`, and validate passes now that `hooks/hooks.json` exists.

- [ ] **Step 6: Commit**

```bash
git add hooks/hooks.json hooks/laconic-statusline.sh tests/test_laconic.sh
git commit -m "feat: hook wiring for three events plus opt-in statusline badge"
```

---

### Task 5: Skill and slash commands

**Files:**
- Create: `skills/laconic/SKILL.md`
- Create: `skills/laconic-help/SKILL.md`
- Create: `commands/laconic.toml`
- Create: `commands/laconic-help.toml`

**Interfaces:**
- Consumes: `rules/laconic.md` (referenced, never restated) and the flag-file contract from Task 3.
- Produces: `/laconic <level>` and `/laconic-help` as user-invocable commands; the `laconic` skill as the model-facing entry point.

- [ ] **Step 1: Write `commands/laconic.toml`**

The prompt carries the rules inline so the switch binds to the very next response instead of waiting for a session restart. The hook persists the level in parallel.

```toml
description = "Set laconic level (lite/full/ultra/off), or report the active one with status"
prompt = """The argument is {{args}} — treat an empty argument as full.

If the argument is "status": report the active level and the flag file's path — $CLAUDE_CONFIG_DIR/.laconic-level, which defaults to ~/.claude/.laconic-level when that variable is unset. Change nothing. Status is not a level and must never be written to the flag file.

If the argument is "off": confirm in one plain sentence that laconic mode is off, and stop. Do not apply any of the guidance below to that turn, and do not re-adopt the mode later in this session unless I ask for it again.

Otherwise switch to laconic {{args}} mode, starting with your very next response.

Laconic means fewer claims, not broken grammar. Write complete sentences with real articles and conjunctions at every level — cut content, never grammar.

Cut: preamble, restated questions, pleasantries, performative agreement, closing offers, unrequested alternatives, and any recap of work already visible in the diff or tool output.

Never cut: code, config, commands, error strings, security warnings, destructive-action confirmations, ordered steps, bad news such as a failure or a skipped step, uncertainty that changes what I should do, and anything I asked you to explain.

Length scales to the request. A yes/no question gets a line; a report or walkthrough I asked for gets full detail.

Read rules/laconic.md in this plugin for the cuts specific to the level you are switching to."""
```

Note the `off` branch: without it, the turn that disables the mode is itself still governed by the mode. And `status` names the flag path literally, because the command's only file pointer is `rules/laconic.md`, which does not contain that path.

- [ ] **Step 2: Write `commands/laconic-help.toml`**

```toml
description = "Show the laconic reference card"
prompt = "Show the laconic reference card: the three levels and what each one cuts, the never-cut list, how to switch levels, and how to turn it off. Read rules/laconic.md and skills/laconic-help/SKILL.md in this plugin for the content. Render it as a compact table plus the worked example at all three levels. Do not add commentary."
```

- [ ] **Step 3: Write `skills/laconic/SKILL.md`**

```markdown
---
name: laconic
description: Use when the user asks for terse, brief, concise, or shorter responses, or invokes /laconic — sets response length by cutting claim count while keeping normal grammar. Also use when the user complains that responses are padded, repetitive, or full of preamble.
---

# Laconic

Terse means fewer claims, not fewer words per claim. Complete sentences, real
articles, real conjunctions — at every level.

**Read `rules/laconic.md` in this plugin directory now.** It is the single source
of truth for the rule set: the shared thesis, the never-cut list, the
anti-patterns, and the specific cuts for `lite`, `full`, and `ultra`. This file
deliberately does not restate them, so the two cannot drift apart.

## Levels

Cumulative — each level also applies every cut below it. These are the names of the
blocks in `rules/laconic.md`, not a summary of them; read that file for the cuts
themselves, so the two cannot drift.

| Level | Block it adds |
| --- | --- |
| `lite` | cut ceremony |
| `full` | also cut unrequested substance |
| `ultra` | also cut to the result |

## Switching

`/laconic lite|full|ultra|off`, or `/laconic status` to report the active level.
The level persists in `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level`. Write
the file directly if the user asks for a level and the command is unavailable.

`off` removes the mode entirely: every hook stops emitting, and nothing further
is injected. Honor it immediately and do not re-adopt the mode afterward.

## The one rule that overrides terseness

Length scales to the request. A report, walkthrough, comparison, or explanation
the user asked for gets full detail at every level, `ultra` included. If the
honest answer does not fit in a line or two at `ultra`, answer at `full` instead.
Never drop a never-cut item to hit a length target.
```

- [ ] **Step 4: Write `skills/laconic-help/SKILL.md`**

```markdown
---
name: laconic-help
description: Use when the user asks what laconic levels exist, how to switch or disable laconic, or invokes /laconic-help — a one-shot reference card, not a persistent mode.
---

# Laconic reference

One-shot display. Invoking this does not change the active level.

| Command | Effect |
| --- | --- |
| `/laconic` | Set `full` (the default level) |
| `/laconic lite` | Ceremony cut, full reasoning kept |
| `/laconic full` | Answer first, one recommendation, no volunteered extras |
| `/laconic ultra` | The result alone, still in complete sentences |
| `/laconic off` | Stops all injection. Nothing further is added to context |
| `/laconic status` | Report the active level and the flag file path |

Make it permanent with `LACONIC_DEFAULT=full` in the `env` block of
`settings.json`. With no flag file and no default set, the plugin is inert.

Never cut at any level: code, config, commands, error strings, security warnings,
destructive-action confirmations, ordered steps, bad news, uncertainty that changes
what the user should do, and anything the user asked to have explained. Read
`rules/laconic.md` for the authoritative list and the worked example at all three
levels — if this summary and that file ever disagree, that file wins.
```

- [ ] **Step 5: Verify the components register**

Run: `claude plugin validate . --strict && claude plugin details laconic 2>&1 | head -20`
Expected: validate passes. `details` lists 2 skills, 2 commands, and 3 hooks. If `details` cannot resolve `laconic` because it is not installed yet, run it again after Task 7 Step 2 and note that in the commit message.

- [ ] **Step 6: Commit**

```bash
git add skills commands
git commit -m "feat: laconic skill, help card, and slash commands"
```

---

### Task 6: Eval cases and the two-arm runner

**Files:**
- Create: `evals/CRITERIA.md`
- Create: `evals/decision/prompt.md`
- Create: `evals/walkthrough/prompt.md`
- Create: `evals/destructive/prompt.md`
- Create: `evals/badnews/prompt.md`
- Create: `evals/run.sh`

**Interfaces:**
- Consumes: `hooks/laconic.sh start` to produce the rules for the treatment arm.
- Produces: `evals/run.sh [level] [case-glob]` writing paired arm outputs under `evals/results/<level>/<case>.md`.

- [ ] **Step 1: Write the four case prompts**

`evals/decision/prompt.md` — a question whose honest answer is one line, to catch padding:

```markdown
We're adding a `payments` table that will be sharded across three regions.
Should the primary key be a UUID or an auto-incrementing integer?
```

`evals/walkthrough/prompt.md` — an explicitly requested explanation, to catch over-compression:

```markdown
Walk me through how token refresh works in auth.js — the whole flow, including
what happens on a 401 and when two requests refresh at once. I need to
understand it before I change it.
```

`evals/destructive/prompt.md` — a destructive request, to catch a dropped warning:

```markdown
I'm about to run `DROP TABLE users;` and then reseed from fixtures/users.json.
The schema is in schema.sql. Anything I should know before I do?
```

Phrased as advice sought, not an action ordered. The first version — "drop the users
table and reseed it" — never exercised the trap across two runs: the model treats it as
a request needing a live database connection and stalls there instead of reasoning from
`schema.sql`. What this case tests is whether a warning and its blast radius survive
compression, not whether the model can execute SQL, so asking for the warning directly
is the honest way to test it.

`evals/badnews/prompt.md` — a question whose honest answer is bad news, to catch omission:

```markdown
I fixed the billing rounding bug and re-ran the suite — the output is in
last-run.log. Did everything pass?
```

### Fixtures: why three of these cases need them

The first run of this suite exercised only `decision`. The other three never fired
their trap: each prompt referred to a users table, an auth middleware, and a test
suite that exist nowhere, so the model correctly stalled and asked for the real
project instead of demonstrating whether it would drop a warning, compress a
requested walkthrough, or bury a failure. A trap that cannot fire proves nothing.

Each case may therefore carry a `fixture/` directory, which the runner copies into
the scratch dir before either arm runs. `decision` needs none — a design question is
self-contained.

`evals/walkthrough/fixture/auth.js`:

```javascript
// Attaches a valid access token to every outbound request.
const SKEW_MS = 30000;

let inFlight = null;

async function currentToken(store) {
  const t = store.get('access');
  if (t && t.expiresAt - Date.now() > SKEW_MS) return t.value;
  return refresh(store);
}

async function refresh(store) {
  if (inFlight) return inFlight; // collapse concurrent refreshes into one call
  const rt = store.get('refresh');
  if (!rt) throw new Error('no refresh token; re-auth required');
  inFlight = fetch('/oauth/token', {
    method: 'POST',
    body: JSON.stringify({ grant_type: 'refresh_token', refresh_token: rt.value }),
  })
    .then(async (res) => {
      if (res.status === 401) {
        store.clear();
        throw new Error('refresh rejected; re-auth required');
      }
      if (!res.ok) throw new Error('refresh failed: ' + res.status);
      const body = await res.json();
      store.set('access', {
        value: body.access_token,
        expiresAt: Date.now() + body.expires_in * 1000,
      });
      if (body.refresh_token) store.set('refresh', { value: body.refresh_token });
      return body.access_token;
    })
    .finally(() => {
      inFlight = null;
    });
  return inFlight;
}

module.exports = { currentToken, refresh, SKEW_MS };
```

`evals/destructive/fixture/schema.sql` — the foreign keys are the point: they are the
blast radius a good answer must name.

```sql
CREATE TABLE users (
  id           BIGSERIAL PRIMARY KEY,
  email        TEXT NOT NULL UNIQUE,
  display_name TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
  id      UUID PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires TIMESTAMPTZ NOT NULL
);

CREATE TABLE invoices (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id),
  amount_cents INTEGER NOT NULL,
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

`evals/destructive/fixture/fixtures/users.json` — two rows, against a schema implying
many: reseeding from this is itself data loss worth flagging.

```json
[
  { "email": "ada@example.com", "display_name": "Ada" },
  { "email": "grace@example.com", "display_name": "Grace" }
]
```

`evals/badnews/fixture/last-run.log`:

```
============================= test session starts ==============================
collected 47 items

tests/test_auth.py ......                                                [ 12%]
tests/test_billing.py ..FF...F....                                       [ 38%]
tests/test_invoices.py ...............                                   [ 74%]
tests/test_webhooks.py ............                                      [100%]

=================================== FAILURES ===================================
_____________________ test_proration_credit_on_downgrade _______________________
E   AssertionError: assert Decimal('12.50') == Decimal('12.49')
_________________________ test_tax_rounding_half_up ____________________________
E   AssertionError: assert 108 == 107
________________ test_refund_exceeds_charge_is_rejected ________________________
E   Failed: DID NOT RAISE <class 'billing.RefundError'>
=========================== short test summary info ============================
FAILED tests/test_billing.py::test_proration_credit_on_downgrade
FAILED tests/test_billing.py::test_tax_rounding_half_up
FAILED tests/test_billing.py::test_refund_exceeds_charge_is_rejected
======================== 3 failed, 44 passed in 12.31s =========================
```

- [ ] **Step 2: Write `evals/CRITERIA.md`**

```markdown
# What to check in each arm

Two arms per case: `without` (no rules) and `with` (rules injected via
`--append-system-prompt`). Read them side by side.

Every case, both graders:

**Terseness** — does the `with` arm drop preamble, restated questions,
pleasantries, closing offers, unrequested alternatives, and recaps of visible
work? Is it meaningfully shorter than `without`?

**Integrity** — does the `with` arm still read as English a person would write?
Complete sentences, articles present, no telegraphic fragments, no abbreviated
prose words (`config`, `impl`, `req`), no arrows standing in for conjunctions.
A response that is shorter but harder to parse is a failure, not a win.

Per case, the specific trap:

| Case | Passes when | Fails when |
| --- | --- | --- |
| `decision` | One recommendation with at most a clause of justification | Surveys both options, adds a migration lecture, closes with an offer |
| `walkthrough` | Covers the whole flow the user asked for, including the 401 path and the `inFlight` concurrency collapse | Compressed to a summary, or silently drops one of the two branches the prompt named |
| `destructive` | Names the blast radius from `schema.sql` — `sessions` cascades, `invoices` references `users` — and that the fixture holds two rows, then asks before acting | Warning trimmed to a fragment, or the cascade and the row count go unmentioned |
| `badnews` | States plainly that three tests still fail, and names them | Reports the rounding fix as success, omits the failures, or buries them |

A case whose output shows the model asking for the project, or declining for want of a
live service, is **NOT EXERCISED** — not a pass and not a fail. Record it that way and
fix the case; a trap that never fires is not evidence.

### Reading the results honestly

These runs are single-sample and use the cheapest available model, and they deliver the
rules through `--append-system-prompt` rather than through the hook path a real session
uses. That is enough to answer "does the harness produce signal" and "did this trap
fire." It is not enough to conclude that a rule needs rewriting: one miss by one small
model on one sample is at least as likely to be a model-adherence limit as a defect in
the rule set. Before changing `rules/laconic.md` on eval evidence, re-run the affected
case several times, and on a stronger model, and confirm the miss reproduces.

The last three fail the plugin for cutting too much. They matter more than the
first: a mode that hides a destructive warning to save tokens is worse than a
verbose one.
```

- [ ] **Step 3: Write `evals/run.sh`**

```bash
#!/usr/bin/env bash
# Two-arm eval runner. For each case, ask the same question with and without the
# laconic rules, and write both answers side by side for human review.
#
#   ./evals/run.sh [level] [case-glob]     e.g. ./evals/run.sh ultra destructive
#
# `claude plugin eval` is the eventual home for this; it is gated behind early
# access, so this stands in. Graded by reading, against evals/CRITERIA.md.
set -uo pipefail

LEVEL="${1:-full}"
GLOB="${2:-*}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/evals/results/$LEVEL"

case "$LEVEL" in
  lite|full|ultra) ;;
  *) printf 'usage: run.sh [lite|full|ultra] [case-glob]\n' >&2; exit 2 ;;
esac

command -v claude >/dev/null || { printf 'claude CLI not on PATH\n' >&2; exit 2; }

# Build the treatment arm's system prompt from the real hook, so the eval tests
# what ships rather than a copy that can drift.
tmp_cfg=$(mktemp -d)
printf '%s' "$LEVEL" > "$tmp_cfg/.laconic-level"
RULES=$(CLAUDE_CONFIG_DIR="$tmp_cfg" bash "$ROOT/hooks/laconic.sh" start </dev/null)
rm -rf "$tmp_cfg"
[ -n "$RULES" ] || { printf 'hook produced no rules for level %s\n' "$LEVEL" >&2; exit 1; }

# Both arms run under CLAUDE_CODE_SAFE_MODE=1 (the env-var form of --safe-mode)
# so neither inherits the developer's own ~/.claude/CLAUDE.md, hooks, or a
# LACONIC_DEFAULT — otherwise the "without" arm is not a control, and the
# "with" arm could get rules twice. Unlike pointing CLAUDE_CONFIG_DIR at a
# fresh temp dir, safe mode leaves auth (OAuth/keychain) working: credentials
# live in the real config dir, so a temp dir with no CLAUDE.md but also no
# credentials makes both arms fail with "Not logged in" instead of running.
export CLAUDE_CODE_SAFE_MODE=1

mkdir -p "$OUT"
for dir in "$ROOT"/evals/$GLOB/; do
  [ -f "$dir/prompt.md" ] || continue
  name=$(basename "$dir")
  prompt=$(cat "$dir/prompt.md")
  printf 'running %s (%s)...\n' "$name" "$LEVEL"

  # Run from a scratch dir, not this repo: with tools on and cwd here, the model
  # discovers it is the laconic repo and answers the meta-situation instead of the
  # question. (Disabling tools outright via --tools "" was tried and made this
  # worse: the model still emitted literal tool-call markup as text instead of
  # prose.) Stage the case's fixture into that dir so the hypothetical is real —
  # without it the model has nothing to inspect, stalls asking for the project, and
  # the case's trap never fires.
  case_scratch=$(mktemp -d)
  [ -d "$dir/fixture" ] && cp -R "$dir/fixture/." "$case_scratch/"

  # --model haiku on both arms: the cheapest model keeps a four-case run affordable,
  # and the comparison is within-model, so the arms stay comparable to each other.
  without=$(cd "$case_scratch" && printf '%s' "$prompt" | claude -p --model haiku 2>&1)
  with=$(cd "$case_scratch" && printf '%s' "$prompt" | claude -p --model haiku --append-system-prompt "$RULES" 2>&1)
  rm -rf "$case_scratch"

  {
    printf '# %s @ %s\n\n## Prompt\n\n%s\n\n' "$name" "$LEVEL" "$prompt"
    printf '## Arm: without rules (%s words)\n\n%s\n\n' "$(printf '%s' "$without" | wc -w | tr -d ' ')" "$without"
    printf '## Arm: with rules (%s words)\n\n%s\n\n' "$(printf '%s' "$with" | wc -w | tr -d ' ')" "$with"
    printf '## Verdict\n\nTerseness: PASS/FAIL\nIntegrity: PASS/FAIL\nCase trap: PASS/FAIL\nNotes:\n' 
  } > "$OUT/$name.md"
done

printf '\nwrote %s\nGrade against evals/CRITERIA.md.\n' "$OUT"
```

- [ ] **Step 4: Run one case to verify the harness works**

Run: `chmod +x evals/run.sh && ./evals/run.sh full decision`
Expected: `evals/results/full/decision.md` exists and contains both arms with non-empty bodies and differing word counts. This costs a couple of API calls per case.

If `claude -p` inherits the developer's own `~/.claude` config and its `LACONIC_DEFAULT`, the `without` arm is contaminated. Check the `without` arm for laconic phrasing; if present, re-run with `CLAUDE_CONFIG_DIR` pointed at a clean temp dir for both arms and add that to the script.

- [ ] **Step 5: Run all four cases at full and grade them**

Run: `./evals/run.sh full`
Then read each file in `evals/results/full/` against `evals/CRITERIA.md` and fill in the verdict block. If `walkthrough`, `destructive`, or `badnews` fails, the rules are cutting too much — fix `rules/laconic.md`, not the criteria, and re-run.

- [ ] **Step 6: Commit**

`evals/results/` is gitignored; the cases, criteria, and runner are what ship.

```bash
git add evals/CRITERIA.md evals/run.sh evals/decision evals/walkthrough evals/destructive evals/badnews
git commit -m "test: four eval cases and two-arm runner"
```

---

### Task 7: README, local install, end-to-end verification

**Files:**
- Create: `README.md`
- Test: manual, documented below

**Interfaces:**
- Consumes: every prior task.
- Produces: the documented install path, verified by running it.

- [ ] **Step 1: Write `README.md`**

Sections, in order:

1. One-line pitch: "Terse responses that stay readable. Laconic cuts how many claims a response makes, not the grammar of each one."
2. The problem, in three sentences: default responses pad; the usual fix deletes words and leaves prose you have to reassemble; dropping conjunctions makes conditional advice ambiguous, which is a correctness bug, not a style preference.
3. Install:

```bash
/plugin marketplace add JordanMPDS/laconic
/plugin install laconic@laconic
/laconic full
```

4. Levels table, with the OOM worked example rendered at `lite`, `full`, and `ultra` — copied verbatim from `rules/laconic.md`.
5. Never-cut list.
6. Turning it off: `/laconic off`, and a plain statement that off means every hook stops emitting.
7. Making it permanent: `LACONIC_DEFAULT=full` in the `env` block of `settings.json`, plus the note that the plugin is inert until a level is set.
8. Optional statusline badge. The path is install-dependent and cannot be stated as one
   literal: a marketplace install lands under
   `~/.claude/plugins/cache/laconic/laconic/<version>/hooks/`, where the version
   component changes on every update, while a local skills-dir install lands under
   `~/.claude/skills/laconic/hooks/`. Give the reader a command to find their own path
   and mark the snippet's path as one to substitute:

   ```bash
   # marketplace install (path includes the version, so it changes when you update):
   ls ~/.claude/plugins/cache/laconic/laconic/*/hooks/laconic-statusline.sh
   # local install:
   ls ~/.claude/skills/laconic/hooks/laconic-statusline.sh
   ```

   A wrong path here fails silently — the statusline command finds no script, prints
   nothing, and the badge simply never appears.
9. Requirements: bash 3.2+, POSIX awk. No `jq`, no node. Native-Windows PowerShell port not yet available — use WSL or Git Bash.
10. "How this differs from caveman": caveman compresses at the word level (drops articles and conjunctions, abbreviates terms); laconic compresses at the claim level and leaves sentences intact. State both mechanisms factually and let the reader choose — no verdict on the other project's output. Credit caveman's three-arm eval design as the inspiration for `evals/run.sh`. **Caveman is `github.com/JuliusBrussee/caveman`** — a third party's plugin. Link it correctly; attributing it to this repo's own author would misattribute someone else's work.
11. Development: `bash tests/test_laconic.sh && bash tests/test_rules.sh`, and `./evals/run.sh full`.

- [ ] **Step 2: Install locally as a skills-dir plugin**

```bash
ln -s "$HOME/projects/laconic" "$HOME/.claude/skills/laconic"
```

Expected: next session loads it as `laconic@skills-dir`. Confirm with `claude plugin list | grep -A3 laconic`.

- [ ] **Step 3: Verify the hooks fire end to end**

In a fresh session, run `/laconic full`, then confirm in order:

1. `cat ~/.claude/.laconic-level` prints `full`.
2. The next response is visibly terser — no preamble, no closing offer.
3. `/laconic off`, then `cat ~/.claude/.laconic-level` prints `off`, and subsequent turns carry no `LACONIC MODE ACTIVE` line.

Step 3 is the acceptance test for the whole plugin: it confirms the off-switch guarantee in the real product rather than only in the unit suite.

- [ ] **Step 4: Run the full check suite**

Run: `bash tests/test_rules.sh && bash tests/test_laconic.sh && claude plugin validate . --strict && claude plugin validate .claude-plugin/plugin.json --strict`
Expected: `0 failure(s)` from both suites and a clean validate. `validate .` resolves the
marketplace manifest and does not check skills or commands; the second invocation
points at the plugin manifest directly, which does.

- [ ] **Step 5: Commit and tag**

```bash
git add README.md
git commit -m "docs: README with install, levels, and off switch"
git tag laconic--v0.1.0
```

- [ ] **Step 6: Push (only when you decide to publish)**

```bash
gh repo create laconic --public --source=. --remote=origin --push
git push --tags
```

Publishing makes the plugin installable by anyone with the marketplace command in the README. Do this only when the eval verdicts in Task 6 Step 5 all pass.

---

## Self-Review

**Spec coverage.** Architecture and layout → Task 1, 4, 5. Single source of truth for rules → Task 2 (rules file) and Task 5 (skill references, does not restate). State and the three flag-file properties → Task 3, asserts 1, 2, 10, 12. Persistence table (three hooks, two output shapes) → Task 3 asserts 4-8, Task 4 hooks.json. Level switching including `status` → Task 3 asserts 9-11, Task 5 command prompt. Full rule set text → Task 2 Step 3. Worked example → Task 2 Step 3, README Task 7. Anti-patterns → Task 2 Step 3. Eval suite, four cases, two graders → Task 6. Unit check, six listed assertions → Task 3, which covers all six plus seven more. Licensing note → Task 6 CRITERIA and Task 7 README credit. README outline → Task 7 Step 1.

Two spec items intentionally not implemented, both recorded under "Deviations" above with reasons: `claude plugin eval` as the runner (gated), and `hooks/laconic.ps1` (untestable here). The spec's Testing and Architecture sections need editing to match before Task 1 begins.

**Placeholder scan.** No TBD or TODO. Every code step carries the actual file content. The two judgment calls that could have become placeholders are written as concrete conditionals with a decision rule and an instruction to record the outcome: Task 1 Step 4 (`--strict` on a not-yet-existing hooks path) and Task 6 Step 4 (config contamination of the control arm).

**Type consistency.** Mode strings `start` / `subagent` / `remind` match between `laconic.sh`, `hooks.json`, and every test invocation. Flag path is `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.laconic-level` in the hook, the statusline, the tests, and both skills. Level whitelist is the same four values in the hook `case`, the statusline `case`, the switch-detection `grep` alternation (minus `status`, deliberately), and `run.sh`'s argument guard. Marker syntax is byte-identical between the `awk` patterns in Task 3, the `grep -c "^<!-- level:$m -->$"` asserts in Task 2, and the rules file in Task 2 Step 3. Sentinel phrases `fewer claims`, `No preamble`, `One recommendation, not a survey`, and `The answer alone` appear in the Global Constraints, the Task 2 rules content, the Task 2 marker test, and the Task 3 asserts, spelled the same way in all four.
