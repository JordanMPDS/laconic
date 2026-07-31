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

# 7. subagent mode behaves like start.
out=$(bash "$SCRIPT" subagent </dev/null)
assert_has "subagent emits rules" "The answer alone" "$out"

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

# 39. subagent mode does not install. Only SessionStart owns the file, so the
# write happens once per session rather than once per spawned agent.
rm -f "$BADGE_DST"
set_level full
bash "$SCRIPT" subagent </dev/null >/dev/null
if [ -f "$BADGE_DST" ]; then fail "subagent must not install the badge"; else ok "subagent installs no badge"; fi

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

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
