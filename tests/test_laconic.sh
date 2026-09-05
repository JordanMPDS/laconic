#!/usr/bin/env bash
# Unit checks for hooks/laconic.sh. No framework: explicit asserts, bash 3.2 safe.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/hooks/laconic.sh"
CLAUDE_CONFIG_DIR="$(mktemp -d)"
export CLAUDE_CONFIG_DIR
FLAG="$CLAUDE_CONFIG_DIR/.laconic-level"

# Pin the project directory rather than letting it fall back to $PWD. Without
# this the suite would read whatever .claude/.laconic-level happens to sit in
# the directory it was invoked from, so a developer with a project flag set
# would see unrelated failures.
CLAUDE_PROJECT_DIR="$(mktemp -d)"
export CLAUDE_PROJECT_DIR
PROJECT_FLAG="$CLAUDE_PROJECT_DIR/.claude/.laconic-level"

trap 'rm -rf "$CLAUDE_CONFIG_DIR" "$CLAUDE_PROJECT_DIR"' EXIT
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
set_project_level() { mkdir -p "$(dirname "$PROJECT_FLAG")"; printf '%s' "$1" > "$PROJECT_FLAG"; }
clear_project() { rm -rf "$(dirname "$PROJECT_FLAG")"; }

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

# 7. subagent is not a mode. It was one until issue #6 measured the path and
# found the injected slice bought nothing a parent model could use, so the
# script must now treat it exactly like any other unknown argument: silence.
# Asserted rather than assumed, because the mode gate fails open by design and
# a reinstated mode would otherwise show no symptom.
out=$(bash "$SCRIPT" subagent </dev/null)
assert_lacks "subagent emits no rules" "The answer alone" "$out"
[ -z "$out" ] && ok "subagent emits nothing at all" || fail "subagent emits nothing at all"

# 8. remind is one line, not the whole rule set.
set_level full
out=$(printf '{"prompt":"fix the test"}' | bash "$SCRIPT" remind)
assert_has   "remind names the level" "LACONIC MODE ACTIVE (full)" "$out"
assert_lacks "remind is not the rules" "No preamble" "$out"
# The per-turn reminder itself must not be a telegraphic fragment — the exact
# defect this plugin exists to avoid, repeated on every single turn.
assert_has "reminder text is a full sentence, not a fragment" \
  "Make fewer claims and keep normal grammar" "$out"

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

# 19. The level alternation must not prefix-match: an unrecognized argument that
# merely starts with a real level word must not switch anything. Without a
# trailing boundary, "/laconic fullscreen" would set "full" and "/laconic
# offline" would re-enable the mode right after the user turned it off.
set_level full
run remind '{"prompt":"/laconic fullscreen"}'
assert_has "fullscreen does not switch" "full" "$(cat "$FLAG")"
run remind '{"prompt":"/laconic ultraviolet"}'
assert_has "ultraviolet does not switch" "full" "$(cat "$FLAG")"
run remind '{"prompt":"/laconic offline"}'
assert_has "offline does not switch (re-enable-after-off case)" "full" "$(cat "$FLAG")"

# 20. A real switch still works with the trailing-boundary fix in place.
set_level ultra
run remind '{"prompt":"/laconic full"}'
assert_has "full still switches" "full" "$(cat "$FLAG")"
run remind '{"prompt":"/laconic  lite"}'
assert_has "two-space lite still switches" "lite" "$(cat "$FLAG")"

# 21. A leading space before the slash command still switches (pasted text).
set_level ultra
run remind '{"prompt":" /laconic full"}'
assert_has "leading-space command still switches" "full" "$(cat "$FLAG")"

# --- project-level flag ---
# A repository may run a different level from the machine default. The project
# flag wins; everything the global flag already promised applies to it too.

# 22. The project flag overrides the global one.
clear_project
set_level lite
set_project_level ultra
out=$(bash "$SCRIPT" start </dev/null)
assert_has   "project flag wins over global" "The answer alone" "$out"
assert_lacks "global level not used when project flag is set" \
  "Lite is normal professional prose" "$out"

# 23. Project off beats global full. The off-switch regression, per project:
# a repository where you want full explanations must be able to say so even
# though the machine default is on.
set_level full
set_project_level off
run start
assert_silent "project off overrides global full"

# 24. Global still applies when the project has no flag. The existing behavior
# must survive the new lookup.
clear_project
set_level full
out=$(bash "$SCRIPT" start </dev/null)
assert_has "global level still applies with no project flag" \
  "One recommendation, not a survey" "$out"

# 25. "/laconic <level> project" writes the project flag and leaves the machine
# flag alone.
clear_project
set_level full
run remind '{"prompt":"/laconic ultra project"}'
assert_has "project scope writes the project flag" "ultra" "$(cat "$PROJECT_FLAG")"
assert_has "project scope leaves the global flag alone" "full" "$(cat "$FLAG")"
assert_has "project scope reports the project level" "LACONIC MODE ACTIVE (ultra)" "$out"

# 26. Without the suffix the write still goes to the machine flag, so existing
# muscle memory keeps working.
clear_project
set_level full
run remind '{"prompt":"/laconic lite"}'
assert_has "unscoped switch writes the global flag" "lite" "$(cat "$FLAG")"
if [ -f "$PROJECT_FLAG" ]; then
  fail "unscoped switch must not create a project flag"
else
  ok "unscoped switch creates no project flag"
fi

# 27. Garbage in the project flag is rejected by the whitelist and never echoed,
# exactly as it is in the global flag. It also fails closed rather than falling
# through to a valid global level — a project flag that exists is the answer,
# even when its contents are junk.
clear_project
set_level full
set_project_level 'ultra; rm -rf /'
run start
assert_silent "malformed project level"

# 28. A symlinked project flag is refused, and refusal wins over a valid global
# flag. Falling through would let a planted symlink downgrade the guarantee to
# whatever the machine default happens to be.
clear_project
set_level full
mkdir -p "$(dirname "$PROJECT_FLAG")"
printf 'ultra' > "$CLAUDE_PROJECT_DIR/decoy"
ln -s "$CLAUDE_PROJECT_DIR/decoy" "$PROJECT_FLAG"
run start
assert_silent "symlinked project flag emits nothing"

# 29. The remind-mode write guard applies to the project path too. Without it,
# "/laconic ultra project" would clobber the link target.
run remind '{"prompt":"/laconic lite project"}'
assert_silent "symlinked project flag on remind"
assert_has "symlinked project flag not written through" \
  "ultra" "$(cat "$CLAUDE_PROJECT_DIR/decoy")"
clear_project
rm -f "$CLAUDE_PROJECT_DIR/decoy"

# 30. LACONIC_DEFAULT seeds the machine flag only. Seeding the project flag
# would drop a file into the user's working tree that they never asked for.
clear_project
rm -f "$FLAG"
out=$(LACONIC_DEFAULT=full bash "$SCRIPT" start </dev/null)
assert_has "default still seeds the global flag" "full" "$(cat "$FLAG")"
if [ -f "$PROJECT_FLAG" ]; then
  fail "LACONIC_DEFAULT must not create a project flag"
else
  ok "LACONIC_DEFAULT creates no project flag"
fi

# 31. The scope suffix needs the same trailing boundary the level words have.
# "projectile" must not be read as "project", or an unscoped switch would
# silently write into the repository instead of the machine flag.
clear_project
set_level full
run remind '{"prompt":"/laconic ultra projectile"}'
assert_has "projectile switches the global flag" "ultra" "$(cat "$FLAG")"
if [ -f "$PROJECT_FLAG" ]; then
  fail "projectile must not be read as project scope"
else
  ok "projectile is not project scope"
fi

# 32. Prose naming the scope must not switch anything either.
set_level full
run remind '{"prompt":"can I run /laconic ultra project in one repo only?"}'
assert_has "prose naming the scope does not switch" "full" "$(cat "$FLAG")"
clear_project

# --- statusline badge install ---
# Claude Code reads statusLine from settings and rejects the field in a plugin
# manifest, so the settings.json edit cannot be automated. Owning the script can
# be, and that is what removes the versioned plugin path from the user's
# settings. These asserts cover the part the plugin is responsible for.
BADGE_SRC="$ROOT/hooks/laconic-statusline.sh"
BADGE_DST="$CLAUDE_CONFIG_DIR/laconic-statusline.sh"

# 33. start installs the badge while a level is active, byte for byte.
clear_project
rm -f "$BADGE_DST"
set_level full
bash "$SCRIPT" start </dev/null >/dev/null
if cmp -s "$BADGE_SRC" "$BADGE_DST"; then
  ok "start installs the badge script"
else
  fail "start did not install the badge script"
fi

# 34. A stale copy is refreshed rather than left alone. This is the whole reason
# the plugin owns the file: a user who wired up the badge once must not be stuck
# on the logic that shipped with whichever version they installed first.
printf 'stale\n' > "$BADGE_DST"
bash "$SCRIPT" start </dev/null >/dev/null
if cmp -s "$BADGE_SRC" "$BADGE_DST"; then
  ok "start refreshes a stale badge script"
else
  fail "start left a stale badge script in place"
fi

# 35. Nothing is installed when the plugin is switched off. Writing files for a
# user who turned the mode off is exactly the kind of lingering state /laconic
# off promises not to leave.
rm -f "$BADGE_DST"
set_level off
run start
assert_silent "off installs nothing (still silent)"
if [ -f "$BADGE_DST" ]; then fail "off must not install the badge"; else ok "off installs no badge"; fi

# 36. Same with no flag at all: an inert plugin touches nothing.
rm -f "$FLAG" "$BADGE_DST"
run start
assert_silent "no flag installs nothing (still silent)"
if [ -f "$BADGE_DST" ]; then fail "inert plugin must not install the badge"; else ok "inert plugin installs no badge"; fi

# 37. A symlinked target is refused, not written through — same discipline the
# flag file gets, and for the same reason.
rm -f "$BADGE_DST"
set_level full
printf 'keep' > "$CLAUDE_CONFIG_DIR/badge-decoy"
ln -s "$CLAUDE_CONFIG_DIR/badge-decoy" "$BADGE_DST"
bash "$SCRIPT" start </dev/null >/dev/null
assert_has "symlinked badge target not written through" "keep" "$(cat "$CLAUDE_CONFIG_DIR/badge-decoy")"
rm -f "$BADGE_DST" "$CLAUDE_CONFIG_DIR/badge-decoy"

# 38. The install never breaks the rule slice, which is the hook's actual job.
# An unwritable config directory must not cost the user their rules.
set_level full
chmod 500 "$CLAUDE_CONFIG_DIR" 2>/dev/null
out=$(bash "$SCRIPT" start </dev/null 2>/dev/null || true)
chmod 700 "$CLAUDE_CONFIG_DIR" 2>/dev/null
assert_has "rules still emitted when the badge cannot be written" \
  "One recommendation, not a survey" "$out"
rm -f "$BADGE_DST"

# 39. remind does not install. Only SessionStart owns the file, so the write
# happens once per session rather than once per prompt — remind runs on every
# turn, and installing there would mean a file comparison per keystroke-batch.
rm -f "$BADGE_DST"
set_level full
printf '{"prompt":"hello"}' | bash "$SCRIPT" remind >/dev/null
if [ -f "$BADGE_DST" ]; then fail "remind must not install the badge"; else ok "remind installs no badge"; fi

# --- PowerShell source encoding ---
# Every .ps1 in this repo must start with a UTF-8 BOM. Windows PowerShell 5.1
# decodes a BOM-less script with the ANSI code page, so an em dash becomes the
# three cp1252 characters â, €, and ” — and PowerShell's tokenizer accepts ” as a
# string delimiter, which terminates the enclosing string early and cascades into
# a parser error several functions later. Checked from the Linux job because it
# is a property of the committed bytes, and because a Windows-only check would
# not run on the commit that strips the BOM.
for ps1 in "$ROOT"/hooks/*.ps1 "$ROOT"/tests/*.ps1; do
  [ -f "$ps1" ] || continue
  name=$(basename "$ps1")
  if [ "$(head -c 3 "$ps1" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ]; then
    ok "$name starts with a UTF-8 BOM"
  else
    fail "$name has no UTF-8 BOM (PowerShell 5.1 would mis-decode its non-ASCII characters)"
  fi
done

# --- hooks.json ---
HOOKS="$ROOT/hooks/hooks.json"
if [ -f "$HOOKS" ]; then ok "hooks.json exists"; else fail "hooks.json exists"; fi
if python3 -c "import json,sys;json.load(open('$HOOKS'))" 2>/dev/null; then
  ok "hooks.json is valid JSON"
else
  fail "hooks.json is valid JSON"
fi

# --- command TOMLs ---
# `claude plugin validate . --strict` resolves "." to the marketplace manifest and
# never parses these, so they get zero coverage from the CLI gate. Parse each with
# stdlib tomllib directly.
for toml in "$ROOT"/commands/*.toml; do
  name=$(basename "$toml")
  if python3 -c "import tomllib; tomllib.load(open('$toml', 'rb'))" 2>/dev/null; then
    ok "$name is valid TOML"
  else
    fail "$name is valid TOML"
  fi
done
# Assert the event-to-mode pairing, not just that the event name appears somewhere.
# laconic.sh's mode gate exits 0 silently on any argument other than start/remind,
# so a typo like "starrt" would disable that hook with no other symptom, and a
# substring check for the event name alone would still pass.
for pair in "SessionStart:start" "UserPromptSubmit:remind"; do
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
  # Same pairing on the native-Windows command. A missing commandWindows makes
  # the plugin a total no-op on Windows, and the bash command sitting next to it
  # would still look correct, so this is checked from the Linux job too — the
  # PowerShell suite alone would never run on the commit that dropped the key.
  found_win=$(python3 -c "
import json
d = json.load(open('$HOOKS'))['hooks']
print(' '.join(h.get('commandWindows', '<missing>').split()[-1].strip('\"')
               for g in d.get('$ev', []) for h in g['hooks']))
" 2>/dev/null)
  if [ "$found_win" = "$mode" ]; then
    ok "hooks.json wires $ev -> $mode on Windows"
  else
    fail "hooks.json wires $ev -> $mode on Windows (got: ${found_win:-nothing})"
  fi
done

# SubagentStart must stay absent. The loop above only checks the events that are
# wired, so a reinstated subagent hook would pass every assertion in this file
# without this one. Issue #6 measured that path: no accuracy change in any arm
# and a 6-16% cost increase per subagent call, which is why it was removed.
if python3 -c "
import json, sys
sys.exit(0 if 'SubagentStart' in json.load(open('$HOOKS'))['hooks'] else 1)
" 2>/dev/null; then
  fail "hooks.json must not wire SubagentStart (see issue #6)"
else
  ok "hooks.json does not wire SubagentStart"
fi

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

# --- switch mode: the Cursor acknowledgment (#16) ---
#
# Cursor's beforeSubmitPrompt injects nothing, so this mode does not deliver
# rules. It persists the switch the way remind does and then refuses the turn,
# which is the only channel that event has to the user. The first assertion is
# the one that matters most: an ordinary prompt must produce nothing, because
# anything on stdout here is a decision about whether the user's work is allowed
# to be submitted.
set_level full
clear_project
out=$(printf '{"prompt":"fix the failing test"}' | bash "$SCRIPT" switch)
assert_empty "switch says nothing about an ordinary prompt" "$out"
out=$(printf '{"prompt":"does /laconic off actually work?"}' | bash "$SCRIPT" switch)
assert_empty "switch says nothing about prose mentioning the command" "$out"
assert_has "switch leaves the level alone on prose" "full" "$(cat "$FLAG")"

out=$(printf '{"prompt":"/laconic ultra"}' | bash "$SCRIPT" switch)
assert_has "switch persists the level" "ultra" "$(cat "$FLAG")"
assert_has "switch blocks the /laconic turn" '"continue":false' "$out"
assert_has "switch names the new level" "level set to ultra" "$out"
assert_lacks "switch does not emit the rules" "No preamble" "$out"
if printf '%s' "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)
sys.exit(0 if d["continue"] is False and d["user_message"].strip() else 1)
' 2>/dev/null; then
  ok "the acknowledgment is well-formed JSON in Cursor's shape"
else
  fail "the acknowledgment is well-formed JSON in Cursor's shape"
fi

# Asserted in full rather than by substring, and asserted identically in
# tests/test_laconic.ps1: this is a user-visible sentence that exists in two
# implementations, and a divergence between them would show on one platform only.
ACK='{"continue":false,"user_message":"laconic: level set to ultra. Cursor delivers the rules at session start, so open a new chat for it to take effect."}'
if [ "$out" = "$ACK" ]; then
  ok "the acknowledgment is byte-identical to the PowerShell side"
else
  fail "the acknowledgment is byte-identical to the PowerShell side — got: $out"
fi

# off is the switch that most needs acknowledging, and it is the one the level
# whitelist would otherwise swallow: past that gate an inactive level is
# silence. Asserted separately because it runs a different path from the levels.
out=$(printf '{"prompt":"/laconic off"}' | bash "$SCRIPT" switch)
assert_has "switch acknowledges off" "level set to off" "$out"
assert_has "off persists through switch mode" "off" "$(cat "$FLAG")"

set_level full
out=$(printf '{"prompt":"/laconic lite project"}' | bash "$SCRIPT" switch)
assert_has "switch names the project scope" "for this project" "$out"
assert_has "switch writes the project flag" "lite" "$(cat "$PROJECT_FLAG")"
clear_project

# A refused write must not be acknowledged. The symlink guard already stops the
# write; without the read-back the mode would still tell the user the level had
# changed, which is the one thing an acknowledgment exists not to do.
rm -f "$FLAG"
printf 'keep' > "$CLAUDE_CONFIG_DIR/decoy"
ln -s "$CLAUDE_CONFIG_DIR/decoy" "$FLAG"
run switch '{"prompt":"/laconic ultra"}'
assert_silent "symlinked flag on switch"
assert_has "symlinked flag not written through on switch" "keep" "$(cat "$CLAUDE_CONFIG_DIR/decoy")"
rm -f "$FLAG"

set_level full
out=$(printf '{"prompt":"/laconic fullscreen"}' | bash "$SCRIPT" switch)
assert_empty "switch does not prefix-match a level word" "$out"
assert_has "fullscreen does not switch under switch mode" "full" "$(cat "$FLAG")"
rm -f "$FLAG"

# --- gemini-settings.json: the Gemini CLI hook fragment (#13) ---
#
# Gemini reads a field out of a JSON object rather than raw stdout, so the
# fragment is only useful if it sets LACONIC_JSON_PATH to the exact path Gemini
# looks in. A fragment that dropped the variable would still be valid JSON, would
# still run the hook, and would inject nothing at all.
GEMINI="$ROOT/hooks/gemini-settings.json"
if [ -f "$GEMINI" ]; then ok "gemini-settings.json exists"; else fail "gemini-settings.json exists"; fi
if python3 -c "import json,sys;json.load(open('$GEMINI'))" 2>/dev/null; then
  ok "gemini-settings.json is valid JSON"
else
  fail "gemini-settings.json is valid JSON"
fi

# Same event-to-mode pairing check hooks.json gets, against Gemini's event names.
for pair in "SessionStart:start" "BeforeAgent:remind"; do
  ev=${pair%:*}; mode=${pair#*:}
  found=$(python3 -c "
import json
d = json.load(open('$GEMINI'))['hooks']
print(' '.join(h['command'].split()[-1]
               for g in d.get('$ev', []) for h in g['hooks']))
" 2>/dev/null)
  if [ "$found" = "$mode" ]; then
    ok "gemini-settings.json wires $ev -> $mode"
  else
    fail "gemini-settings.json wires $ev -> $mode (got: ${found:-nothing})"
  fi
done

GEMINI_PATH=$(python3 -c "
import json
d = json.load(open('$GEMINI'))['hooks']
paths = set()
for groups in d.values():
    for g in groups:
        for h in g['hooks']:
            for tok in h['command'].split():
                if tok.startswith('LACONIC_JSON_PATH='):
                    paths.add(tok.split('=', 1)[1])
print(paths.pop() if len(paths) == 1 else '')
" 2>/dev/null)
if [ "$GEMINI_PATH" = "hookSpecificOutput.additionalContext" ]; then
  ok "gemini-settings.json sets the JSON path Gemini reads, on every hook"
else
  fail "gemini-settings.json JSON path (got: ${GEMINI_PATH:-nothing or inconsistent})"
fi

# Gemini's timeouts are milliseconds; hooks.json's are seconds. Copying the 5
# across would give a 5 ms budget and kill the hook before it read the flag.
if python3 -c "
import json, sys
d = json.load(open('$GEMINI'))['hooks']
t = [h.get('timeout', 0) for g in d.values() for e in g for h in e['hooks']]
sys.exit(0 if t and all(x >= 1000 for x in t) else 1)
" 2>/dev/null; then
  ok "gemini-settings.json timeouts are in milliseconds"
else
  fail "gemini-settings.json timeouts are in milliseconds"
fi

# End to end against the fragment's own path rather than a literal, so the
# fragment and the hook cannot drift apart silently. This is a schema check and
# nothing more: per #13, a well-formed object is not evidence that Gemini loads
# it, and no Gemini install has confirmed that yet.
set_level full
for mode in start remind; do
  if LACONIC_JSON_PATH="$GEMINI_PATH" bash "$SCRIPT" "$mode" </dev/null 2>/dev/null \
     | python3 -c "
import json, sys
v = json.load(sys.stdin)['hookSpecificOutput']['additionalContext']
sys.exit(0 if isinstance(v, str) and v.strip() else 1)
" 2>/dev/null; then
    ok "$mode fills additionalContext where Gemini reads it"
  else
    fail "$mode fills additionalContext where Gemini reads it"
  fi
done
rm -f "$FLAG"

# --- codex-config.toml: the Codex CLI hook fragment (#14) ---
#
# Codex injects a hook's raw stdout into model context as a developer message,
# the same way Claude Code does, so this fragment must NOT set
# LACONIC_JSON_PATH. Copying the variable across from gemini-settings.json would
# still run the hook and still deliver something — a JSON object, rendered
# literally into the model's context instead of the rules.
CODEX="$ROOT/hooks/codex-config.toml"
if [ -f "$CODEX" ]; then ok "codex-config.toml exists"; else fail "codex-config.toml exists"; fi
if python3 -c "import tomllib;tomllib.load(open('$CODEX','rb'))" 2>/dev/null; then
  ok "codex-config.toml is valid TOML"
else
  fail "codex-config.toml is valid TOML"
fi

# Same event-to-mode pairing check hooks.json gets, against Codex's event names.
# They are Claude Code's names, which is why the mode is the last token either way.
for pair in "SessionStart:start" "UserPromptSubmit:remind"; do
  ev=${pair%:*}; mode=${pair#*:}
  found=$(python3 -c "
import tomllib
d = tomllib.load(open('$CODEX', 'rb'))['hooks']
print(' '.join(h['command'].split()[-1] for g in d.get('$ev', []) for h in g['hooks']))
" 2>/dev/null)
  if [ "$found" = "$mode" ]; then
    ok "codex-config.toml wires $ev -> $mode"
  else
    fail "codex-config.toml wires $ev -> $mode (got: ${found:-nothing})"
  fi
done

# commandWindows is Codex's own field name, spelled exactly as hooks.json spells
# it, and it has to select the same mode as the bash command beside it. A
# fragment whose Windows line ran a different mode would be wrong on precisely
# the platform nobody testing on Linux would notice.
if python3 -c "
import sys, tomllib
d = tomllib.load(open('$CODEX', 'rb'))['hooks']
hooks = [h for groups in d.values() for g in groups for h in g['hooks']]
sys.exit(0 if hooks and all(
    'laconic.ps1' in h.get('commandWindows', '')
    and h['commandWindows'].split()[-1] == h['command'].split()[-1]
    for h in hooks) else 1)
" 2>/dev/null; then
  ok "codex-config.toml commandWindows runs laconic.ps1 in the same mode"
else
  fail "codex-config.toml commandWindows runs laconic.ps1 in the same mode"
fi

# Codex's timeouts are seconds, like hooks.json's and unlike Gemini's. A 5000
# copied across from the Gemini fragment would be an 83-minute hook budget.
if python3 -c "
import sys, tomllib
d = tomllib.load(open('$CODEX', 'rb'))['hooks']
t = [h.get('timeout', 0) for groups in d.values() for g in groups for h in g['hooks']]
sys.exit(0 if t and all(1 <= x <= 60 for x in t) else 1)
" 2>/dev/null; then
  ok "codex-config.toml timeouts are in seconds"
else
  fail "codex-config.toml timeouts are in seconds"
fi

# Read the parsed commands, not the file text: the comment above them names the
# variable in order to explain why it is absent.
if python3 -c "
import sys, tomllib
d = tomllib.load(open('$CODEX', 'rb'))['hooks']
cmds = [c for groups in d.values() for g in groups for h in g['hooks']
        for c in (h['command'], h.get('commandWindows', ''))]
sys.exit(0 if cmds and not any('LACONIC_JSON_PATH' in c for c in cmds) else 1)
" 2>/dev/null; then
  ok "codex-config.toml leaves stdout raw, which is what Codex reads"
else
  fail "codex-config.toml leaves stdout raw, which is what Codex reads"
fi

# End to end against the fragment's own command rather than a literal, so the
# fragment and the hook cannot drift apart silently. Unlike the Gemini block
# above this is more than a schema check: #14 verified both modes reaching the
# model context on Codex CLI 0.147.0, and what this asserts is that the command
# the fragment ships still produces the bytes that were verified.
set_level full
for mode in start remind; do
  out=$(python3 -c "
import tomllib
d = tomllib.load(open('$CODEX', 'rb'))['hooks']
for groups in d.values():
    for g in groups:
        for h in g['hooks']:
            if h['command'].split()[-1] == '$mode':
                print(h['command'])
" 2>/dev/null \
    | sed "s|/absolute/path/to/laconic|$ROOT|" \
    | while read -r cmd; do eval "$cmd" </dev/null 2>/dev/null; done)
  if [ -n "$out" ]; then
    ok "$mode delivers raw text through the fragment's own command"
  else
    fail "$mode delivers raw text through the fragment's own command"
  fi
done
rm -f "$FLAG"

# --- no Copilot fragment on the events that drop it (#15) ---
#
# Copilot CLI runs shell hooks from .github/hooks/*.json, and its own reference
# says a config-file command hook's output is dropped on userPromptSubmitted and
# is not read at all on sessionStart — which is both of laconic's modes. A
# fragment wiring them would be valid JSON, would load, would run, and would
# deliver nothing, silently. The recipes in circulation do exactly that, so this
# guard exists for whoever transcribes one: see docs/other-agents.md.
#
# Written as "if such a file appears" rather than asserting a shape, because the
# finding is that the file must not exist yet.
COPILOT_BAD=$(python3 -c "
import glob, json, sys
dropped = {'sessionstart', 'userpromptsubmitted', 'userpromptsubmit'}
bad = []
for path in sorted(glob.glob('$ROOT/hooks/copilot*.json')
                   + glob.glob('$ROOT/.github/hooks/*.json')):
    try:
        events = json.load(open(path)).get('hooks', {})
    except Exception:
        bad.append(path + ' (unparseable)')
        continue
    for ev in events:
        if ev.lower() in dropped:
            bad.append(path + ':' + ev)
print(' '.join(bad))
" 2>/dev/null)
if [ -z "$COPILOT_BAD" ]; then
  ok "no Copilot fragment wires an event that drops the hook's output"
else
  fail "Copilot fragment wires a dropped event: $COPILOT_BAD"
fi

# --- cursor-hooks.json: the Cursor hook fragment (#16) ---
#
# Cursor reads additional_context out of a JSON object on sessionStart, and it
# spells the field in snake_case where Gemini nests it under hookSpecificOutput.
# A fragment carrying Gemini's path across would be valid JSON, would load, and
# would inject nothing. There is no per-turn injection to wire at all, so the
# second hook is the switch acknowledgment rather than remind.
CURSOR="$ROOT/hooks/cursor-hooks.json"
if [ -f "$CURSOR" ]; then ok "cursor-hooks.json exists"; else fail "cursor-hooks.json exists"; fi
if python3 -c "import json,sys;json.load(open('$CURSOR'))" 2>/dev/null; then
  ok "cursor-hooks.json is valid JSON"
else
  fail "cursor-hooks.json is valid JSON"
fi

# Cursor requires the schema version and rejects a file without it.
if python3 -c "
import json, sys
sys.exit(0 if json.load(open('$CURSOR')).get('version') == 1 else 1)
" 2>/dev/null; then
  ok "cursor-hooks.json declares version 1"
else
  fail "cursor-hooks.json declares version 1"
fi

# Same event-to-mode pairing check the other fragments get. Cursor's hook list is
# flat — one array of objects per event, with no matcher group in between.
for pair in "sessionStart:start" "beforeSubmitPrompt:switch"; do
  ev=${pair%:*}; mode=${pair#*:}
  found=$(python3 -c "
import json
d = json.load(open('$CURSOR'))['hooks']
print(' '.join(h['command'].split()[-1] for h in d.get('$ev', [])))
" 2>/dev/null)
  if [ "$found" = "$mode" ]; then
    ok "cursor-hooks.json wires $ev -> $mode"
  else
    fail "cursor-hooks.json wires $ev -> $mode (got: ${found:-nothing})"
  fi
done

CURSOR_PATH=$(python3 -c "
import json
d = json.load(open('$CURSOR'))['hooks']
paths = set()
for h in d.get('sessionStart', []):
    for tok in h['command'].split():
        if tok.startswith('LACONIC_JSON_PATH='):
            paths.add(tok.split('=', 1)[1])
print(paths.pop() if len(paths) == 1 else '')
" 2>/dev/null)
if [ "$CURSOR_PATH" = "additional_context" ]; then
  ok "cursor-hooks.json sets the JSON path Cursor reads, unnested and snake_case"
else
  fail "cursor-hooks.json JSON path (got: ${CURSOR_PATH:-nothing or inconsistent})"
fi

# Cursor's timeouts are seconds, like hooks.json's and unlike Gemini's.
if python3 -c "
import json, sys
d = json.load(open('$CURSOR'))['hooks']
t = [h.get('timeout', 0) for hooks in d.values() for h in hooks]
sys.exit(0 if t and all(1 <= x <= 60 for x in t) else 1)
" 2>/dev/null; then
  ok "cursor-hooks.json timeouts are in seconds"
else
  fail "cursor-hooks.json timeouts are in seconds"
fi

# beforeSubmitPrompt is the one laconic hook anywhere that can refuse a user's
# prompt, so it must never fail closed: a hook that crashes or times out has to
# let the turn through. Cursor's default is already false, and it is written out
# here because a default is not a guarantee.
if python3 -c "
import json, sys
d = json.load(open('$CURSOR'))['hooks']
h = d.get('beforeSubmitPrompt', [])
sys.exit(0 if h and all(x.get('failClosed') is False for x in h) else 1)
" 2>/dev/null; then
  ok "cursor-hooks.json fails open on the event that can block a prompt"
else
  fail "cursor-hooks.json fails open on the event that can block a prompt"
fi

# End to end against the fragment's own commands rather than literals, so the
# fragment and the hook cannot drift apart silently. This is a schema check and
# nothing more: per #16, a well-formed object is not evidence that Cursor loads
# it, and no Cursor install has confirmed it.
set_level full
cursor_cmd() { # cursor_cmd <event>
  python3 -c "
import json
d = json.load(open('$CURSOR'))['hooks']
for h in d.get('$1', []):
    print(h['command'])
" 2>/dev/null | sed "s|/absolute/path/to/laconic|$ROOT|"
}

if cursor_cmd sessionStart | while read -r cmd; do eval "$cmd" </dev/null 2>/dev/null; done \
   | python3 -c "
import json, sys
v = json.load(sys.stdin)['additional_context']
sys.exit(0 if isinstance(v, str) and 'fewer claims' in v else 1)
" 2>/dev/null; then
  ok "sessionStart fills additional_context where Cursor reads it"
else
  fail "sessionStart fills additional_context where Cursor reads it"
fi

out=$(cursor_cmd beforeSubmitPrompt \
      | while read -r cmd; do printf '{"prompt":"ship it"}' | eval "$cmd" 2>/dev/null; done)
assert_empty "the fragment's own beforeSubmitPrompt command allows an ordinary prompt" "$out"
out=$(cursor_cmd beforeSubmitPrompt \
      | while read -r cmd; do printf '{"prompt":"/laconic lite"}' | eval "$cmd" 2>/dev/null; done)
assert_has "the fragment's own beforeSubmitPrompt command acknowledges a switch" \
  '"continue":false' "$out"
rm -f "$FLAG"

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

# The badge resolves the flag the same way the hook does. A badge that names a
# level the session is not running is worse than no badge, because nothing else
# would reveal the mismatch.
set_level full
set_project_level ultra
out=$(bash "$BADGE" 2>/dev/null)
assert_has "badge follows the project flag, not the global one" "[LACONIC:ULTRA]" "$out"
set_project_level off
out=$(bash "$BADGE" 2>/dev/null)
assert_empty "badge silent when the project flag is off" "$out"
clear_project
rm -f "$FLAG"

# --- LACONIC_JSON_PATH: the JSON output mode (#13) ---
#
# Raw stdout is what Claude Code consumes and must not move, so the first check
# here is that the raw path is byte-identical with the variable unset. The rest
# cover the failure mode raw stdout never had: the rule slice carries double
# quotes and newlines on every level, so a wrapper that escaped neither would
# ship malformed JSON.
printf 'full' > "$FLAG"

out=$(bash "$SCRIPT" start </dev/null 2>/dev/null)
out_empty=$(LACONIC_JSON_PATH= bash "$SCRIPT" start </dev/null 2>/dev/null)
if [ "$out" = "$out_empty" ]; then
  ok "an empty LACONIC_JSON_PATH is the raw path, byte for byte"
else
  fail "an empty LACONIC_JSON_PATH is the raw path, byte for byte"
fi

json=$(LACONIC_JSON_PATH=hookSpecificOutput.additionalContext \
       bash "$SCRIPT" start </dev/null 2>/dev/null)
if printf '%s' "$json" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
  ok "start emits well-formed JSON when a path is set"
else
  fail "start emits well-formed JSON when a path is set"
fi

# The payload must be the raw slice exactly, minus the single trailing newline:
# the field carries the text, not the line terminator. Both sides go to files,
# because $(...) strips trailing newlines and cannot reconstruct the raw bytes.
bash "$SCRIPT" start </dev/null > "$CLAUDE_CONFIG_DIR/raw.txt" 2>/dev/null
LACONIC_JSON_PATH=hookSpecificOutput.additionalContext \
  bash "$SCRIPT" start </dev/null > "$CLAUDE_CONFIG_DIR/wrapped.json" 2>/dev/null
if python3 -c '
import json, sys
got = json.load(open(sys.argv[1]))["hookSpecificOutput"]["additionalContext"]
raw = open(sys.argv[2]).read()
sys.exit(0 if got == raw[:-1] else 1)
' "$CLAUDE_CONFIG_DIR/wrapped.json" "$CLAUDE_CONFIG_DIR/raw.txt" 2>/dev/null; then
  ok "the JSON payload round-trips to the raw slice"
else
  fail "the JSON payload round-trips to the raw slice"
fi

# The escaping the raw path never needed. The shipped slice contains both, so
# this asserts against real content rather than a synthetic string.
if printf '%s' "$json" | python3 -c '
import json, sys
got = json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]
sys.exit(0 if chr(34) in got and chr(10) in got else 1)
' 2>/dev/null; then
  ok "quotes and newlines survive the JSON round-trip"
else
  fail "quotes and newlines survive the JSON round-trip"
fi

json_remind=$(LACONIC_JSON_PATH=hookSpecificOutput.additionalContext \
              bash "$SCRIPT" remind </dev/null 2>/dev/null)
if printf '%s' "$json_remind" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
  ok "remind emits well-formed JSON when a path is set"
else
  fail "remind emits well-formed JSON when a path is set"
fi

# A single-segment path must not be nested, and a deep one must nest all the way:
# Codex and Copilot do not put the field where Gemini does (#14, #15).
one=$(LACONIC_JSON_PATH=context bash "$SCRIPT" remind </dev/null 2>/dev/null)
case "$one" in
  '{"context":"LACONIC MODE ACTIVE'*) ok "a single-segment path is not nested" ;;
  *) fail "a single-segment path is not nested — got: $one" ;;
esac

deep=$(LACONIC_JSON_PATH=a.b.c bash "$SCRIPT" remind </dev/null 2>/dev/null)
case "$deep" in
  '{"a":{"b":{"c":"'*'}}}') ok "a dotted path nests every segment" ;;
  *) fail "a dotted path nests every segment — got: $deep" ;;
esac

# Backslashes and tabs, which the shipped slice does not contain, so the checks
# above cannot reach them. The hook resolves its rules file from its own
# directory, so a temp tree with a copy of the script and a synthetic rules file
# exercises the escaper against content chosen to break it.
ESCDIR="$(mktemp -d)"
mkdir -p "$ESCDIR/hooks" "$ESCDIR/rules"
cp "$SCRIPT" "$ESCDIR/hooks/laconic.sh"
printf 'back\\slash and "quote" and\ttab\nsecond line\n' > "$ESCDIR/rules/laconic.md"
printf 'full' > "$FLAG"
LACONIC_JSON_PATH=v bash "$ESCDIR/hooks/laconic.sh" start </dev/null \
  > "$ESCDIR/out.json" 2>/dev/null
if python3 -c '
import json, sys
got = json.load(open(sys.argv[1]))["v"]
want = "back\\slash and \"quote\" and\ttab\nsecond line"
sys.exit(0 if got == want else 1)
' "$ESCDIR/out.json" 2>/dev/null; then
  ok "backslashes, quotes and tabs survive the JSON round-trip"
else
  fail "backslashes, quotes and tabs survive the JSON round-trip"
fi
rm -rf "$ESCDIR"
rm -f "$FLAG"
printf 'full' > "$FLAG"

# The level whitelist still gates it. JSON mode must not become a way to emit
# something when no level is active.
rm -f "$FLAG"
out=$(LACONIC_JSON_PATH=hookSpecificOutput.additionalContext \
      bash "$SCRIPT" start </dev/null 2>/dev/null)
assert_empty "no level active emits nothing even with a JSON path set" "$out"

printf 'off' > "$FLAG"
out=$(LACONIC_JSON_PATH=hookSpecificOutput.additionalContext \
      bash "$SCRIPT" start </dev/null 2>/dev/null)
assert_empty "level off emits nothing even with a JSON path set" "$out"
rm -f "$FLAG"

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
