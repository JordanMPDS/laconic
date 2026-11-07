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

# The arrow prohibition has to name the constructions the model actually
# reaches for. "No arrows standing in for conjunctions in running prose" left
# two openings the benchmark caught it walking through: a sequence arrow is
# not a conjunction, and a bolded-label line does not read as running prose.
# Every observed violation landed in one of those two.
# Matched against a whitespace-flattened copy: a phrase that happens to
# straddle a line break is still present in the rule the model reads, so a
# test that fails on a re-wrap is testing the line width, not the rule.
shared_flat=$(printf '%s' "$shared" | tr '\n' ' ' | tr -s ' ')
for phrase in "not after a bold label" "runbook" "chain steps"; do
  case "$shared_flat" in
    *"$phrase"*) ok "arrow rule closes the hatch: $phrase" ;;
    *) fail "arrow rule closes the hatch: $phrase" ;;
  esac
done

# Same defect class, same treatment. "including exactly what will be affected"
# did not say *from what is in front of you*, so a response that listed the
# generic checks and offered to go read the schema itself read as compliant -
# destructive/haiku rep2 in the 2026-07-31 benchmark did exactly that, in one
# turn, without opening the file it was pointed at. The bullet now demands the
# read and names the punt as a failure; these two phrases are what carry that.
for phrase in "name the objects from" "is not a confirmation"; do
  case "$shared_flat" in
    *"$phrase"*) ok "destructive rule demands the read: $phrase" ;;
    *) fail "destructive rule demands the read: $phrase" ;;
  esac
done

# The rules text is injected verbatim into the prompt, so an arrow used
# approvingly inside it models the exact habit the rule forbids - the old
# "(`configuration` -> `config`)" gloss sat in the same sentence as the
# prohibition. Inline-code spans are stripped first, the same way
# metrics.py strips them before scoring: the rule has to be able to name the
# glyphs it bans. Outside code, an arrow may appear only on a Wrong example.
# HTML comments are stripped too: the level markers "<!-- level:lite -->" end
# in a literal -> that is structure, not prose.
bad_arrow_lines=$(sed -e 's/`[^`]*`//g' -e 's/<!--.*-->//g' "$RULES" \
                  | grep -n -- '->\|→' | grep -v '^[0-9]*:- Wrong:' || true)
if [ -z "$bad_arrow_lines" ]; then
  ok "rules/laconic.md uses arrows only in lines marked Wrong"
else
  fail "rules/laconic.md uses an arrow outside a Wrong example: $bad_arrow_lines"
fi

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


# The never-cut summaries that remain must not drift. A summary that drops an
# item is the difference between a terse answer and one that omits a security
# warning.
#
# skills/laconic/SKILL.md is deliberately absent from the list below. It is
# checked further down for the opposite property, that it restates nothing and
# points at rules/laconic.md instead. skills/laconic-help/SKILL.md keeps its
# condensed list because it declares that file authoritative on any
# disagreement; README.md keeps one because it is documentation rather than an
# instruction the model follows.
#
# rules/laconic.md is checked against its "## Never cut" section only, not the
# whole file — scoped the same way the level blocks above are (lite_block,
# full_block, ultra_block). A whole-file grep would still pass if the keyword
# survives elsewhere: the word "destructive" also appears in the closing-offer
# carve-out under "Level: lite" ("Asking permission before a destructive action
# is not a closing offer..."), so an unscoped check would not notice the actual
# never-cut bullet being deleted. The other two files carry no such
# collision, so they keep the simpler whole-file check.
never_cut_ln=$(grep -n "^## Never cut" "$RULES" | head -1 | cut -d: -f1)
next_heading_ln=$(sed -n "$((never_cut_ln + 1)),\$p" "$RULES" | grep -n "^## " | head -1 | cut -d: -f1)
if [ -n "$next_heading_ln" ]; then
  never_cut_end_ln=$((never_cut_ln + next_heading_ln - 1))
else
  never_cut_end_ln=$(wc -l < "$RULES")
fi
rules_never_cut=$(sed -n "${never_cut_ln},${never_cut_end_ln}p" "$RULES")

for kw in "code" "config" "command" "error string" "ecurity warning" "estructive" \
          "rdered" "ad news" "ncertainty" "xplain"; do
  if printf '%s' "$rules_never_cut" | grep -qi -- "$kw"; then
    ok "rules/laconic.md keeps never-cut: $kw"
  else
    fail "rules/laconic.md dropped never-cut item: $kw"
  fi
  for f in skills/laconic-help/SKILL.md README.md; do
    if grep -qi -- "$kw" "$ROOT/$f"; then ok "$f keeps never-cut: $kw"
    else fail "$f dropped never-cut item: $kw"; fi
  done
done

# --- skills/laconic/SKILL.md must point at the rules, not repeat them ---
# It is the instruction the model follows on /laconic, so a stale copy here is
# the highest-consequence copy in the repo: it would be followed in preference
# to the file it contradicts. These checks used to guard a Gemini-format TOML
# command that Claude Code never loaded, while this skill, which is what
# /laconic actually runs, went unchecked (#434).
SKILL="$ROOT/skills/laconic/SKILL.md"
if grep -q 'rules/laconic\.md' "$SKILL"; then
  ok "skills/laconic/SKILL.md points at rules/laconic.md"
else
  fail "skills/laconic/SKILL.md no longer points at rules/laconic.md"
fi

# The read has to be imperative, not a trailing suggestion. On the turn that
# switches the level the hook has emitted only its one-line reminder, so the
# rule set is not in context and an unread pointer leaves that turn ungoverned.
if grep -qE 'Read `?rules/laconic\.md`? in this plugin directory now' "$SKILL"; then
  ok "skills/laconic/SKILL.md demands the read rather than suggesting it"
else
  fail "skills/laconic/SKILL.md lost the imperative read instruction"
fi

# Phrases that only appear in an actual restatement of the rule set. Naming the
# never-cut list is fine; listing its members is the drift risk.
for phrase in "error string" "security warning" "performative agreement"; do
  if grep -qi -- "$phrase" "$SKILL"; then
    fail "skills/laconic/SKILL.md restates the rule set again: $phrase"
  else
    ok "skills/laconic/SKILL.md does not restate: $phrase"
  fi
done

# --- statusline badge: the documented path must be the one the hook installs ---
# The user's settings.json is the one part of the badge nobody can automate,
# since Claude Code reads statusLine from settings and rejects the field in a
# plugin manifest. So the path docs/configuration.md tells them to paste has to
# be exactly the path hooks/laconic.sh writes to, or the badge points at nothing
# and says nothing about it.
STATUSLINE_DOC="$ROOT/docs/configuration.md"
statusline_cmd=$(grep '"command": "bash' "$STATUSLINE_DOC")
if [ -z "$statusline_cmd" ]; then
  fail "docs/configuration.md has no statusline command line to check"
else
  # Run the documented line, as the shell Claude Code hands it to would, against
  # the copy the hook installed, with CLAUDE_CONFIG_DIR set and unset. A glob on
  # the text passed the old $HOME/.claude line, which found nothing whenever the
  # variable moved the hook's install directory (#432).
  cmd_json=$(printf '%s' "${statusline_cmd#*\"command\": }" | sed 's/[[:space:]]*$//')
  cmd=$(printf '%s' "$cmd_json" | sed -e 's/^"//' -e 's/"$//' -e 's/\\"/"/g')
  SL_TMP=$(mktemp -d)
  mkdir -p "$SL_TMP/proj"
  sl_env() { # <config dir, empty for unset> <command...>
    local cfg=$1; shift
    if [ -n "$cfg" ]; then
      env HOME="$SL_HOME" CLAUDE_PROJECT_DIR="$SL_TMP/proj" CLAUDE_CONFIG_DIR="$cfg" "$@"
    else
      env -u CLAUDE_CONFIG_DIR HOME="$SL_HOME" CLAUDE_PROJECT_DIR="$SL_TMP/proj" "$@"
    fi
  }
  for label in set unset; do
    SL_HOME="$SL_TMP/home-$label"
    cfg=""; [ "$label" = set ] && cfg="$SL_TMP/cfg"
    dir=${cfg:-$SL_HOME/.claude}
    mkdir -p "$dir"
    printf 'full' > "$dir/.laconic-level"
    sl_env "$cfg" bash "$ROOT/hooks/laconic.sh" start </dev/null >/dev/null 2>&1
    case "$(sl_env "$cfg" sh -c "$cmd" </dev/null 2>/dev/null)" in
      *'[LACONIC]'*)
        ok "the documented statusline command renders the installed badge (CLAUDE_CONFIG_DIR $label)" ;;
      *)
        fail "the documented statusline command finds no badge where the hook installed it (CLAUDE_CONFIG_DIR $label): $cmd" ;;
    esac
  done
  rm -rf "$SL_TMP"
  # The badge script's header repeats the line for whoever reads the copy in
  # their configuration directory; it must not drift from the doc.
  if grep -qF -- "\"command\": $cmd_json" "$ROOT/hooks/laconic-statusline.sh"; then
    ok "hooks/laconic-statusline.sh repeats the documented statusline command"
  else
    fail "hooks/laconic-statusline.sh header differs from the documented statusline command: $cmd_json"
  fi
  # A versioned install path breaks on the next plugin update, and
  # ${CLAUDE_PLUGIN_ROOT} is rejected outright for statusLine commands. Both
  # fail silently, which is why they are gated rather than left to review.
  for bad in 'plugins/cache' 'CLAUDE_PLUGIN_ROOT'; do
    case "$statusline_cmd" in
      *"$bad"*) fail "statusline command still routes through: $bad" ;;
      *)        ok "statusline command avoids: $bad" ;;
    esac
  done
fi

# No PowerShell statusline line, because nothing installs its target: only
# hooks/laconic.ps1 writes laconic-statusline.ps1, and Claude Code never runs
# the port (#423). On Windows it runs the bash line above through Git Bash.
if grep -q '"command": "powershell' "$STATUSLINE_DOC"; then
  fail "docs/configuration.md offers a PowerShell statusline line whose script nothing installs (#423)"
else
  ok "docs/configuration.md offers no PowerShell statusline line (#423)"
fi

# --- pre-sliced rule files: the committed copies must match what the hook emits ---
# rules/dist/*.md exist for agents that take a static instructions file instead of
# running a hook. Nothing regenerates them automatically, so an edit to
# rules/laconic.md would otherwise leave them stale — and a stale copy is the worst
# kind here, because a user who pasted one into .cursor/rules/ has no way to tell
# it drifted from the rules the plugin actually delivers.
DIST_TMP=$(mktemp -d)
if bash "$ROOT/tools/build-rules.sh" "$DIST_TMP" >/dev/null 2>&1; then
  for level in lite full ultra; do
    if cmp -s "$DIST_TMP/laconic-$level.md" "$ROOT/rules/dist/laconic-$level.md"; then
      ok "rules/dist/laconic-$level.md is current"
    else
      fail "rules/dist/laconic-$level.md is stale — run tools/build-rules.sh"
    fi
  done
else
  fail "tools/build-rules.sh did not run"
fi
rm -rf "$DIST_TMP"

# --- the loop skill and its ledger ---
# The loop's whole defence against manufacturing a winner is that rejected
# attempts get recorded too. A skill documenting only the accept path would
# leave the ledger looking like an unbroken run of successes, which is the one
# failure mode nobody reviewing a PR can see.
#
# Project-local under .claude/skills, not shipped in skills/: this is a
# maintainer procedure for editing rules/laconic.md, and a plugin user has
# no use for a skill that spends 700 API calls on the benchmark.
LOOP="$ROOT/.claude/skills/laconic-loop/SKILL.md"
if [ -f "$LOOP" ]; then
  ok "laconic-loop skill exists"
  for phrase in "rejected" "holdout" "hypothesis" "flip rate" "rule-adherence"; do
    if grep -qi -- "$phrase" "$LOOP"; then
      ok "loop skill covers: $phrase"
    else
      fail "loop skill covers: $phrase"
    fi
  done
  # This guard used to require the words "a human merges". Autonomous merges
  # were granted on 2026-09-01 and the loop has merged its own rounds since —
  # tools/loop.sh has told each iteration to "branch, pull request, then merge"
  # the whole time — so the skill and this test agreed with each other and with
  # nothing else. What the guard was actually protecting is still worth
  # enforcing, and is not about who clicks the button: a rule change reaches
  # master through a pull request whose checks passed, never a direct push.
  if grep -qi 'pull request' "$LOOP" && grep -qi 'checks pass' "$LOOP"; then
    ok "loop skill routes rule changes through a pull request"
  else
    fail "loop skill no longer routes rule changes through a pull request"
  fi
  # An accept that never ships is the failure this replaced: round 55 accepted
  # on 2026-09-08 and sat merged and unreleased for six days.
  if grep -q 'release-due.sh' "$LOOP"; then
    ok "loop skill ends a round at a release"
  else
    fail "loop skill no longer ends a round at a release"
  fi
  # And a round that ships nothing is the other half: rounds 56 through 63 were
  # eight measuring rounds in a row, every one of them worth running, over which
  # rules/laconic.md did not move.
  if grep -q 'candidate-due.sh' "$LOOP"; then
    ok "loop skill caps measuring rounds"
  else
    fail "loop skill no longer caps measuring rounds"
  fi
else
  fail "laconic-loop skill exists"
fi

# The skill is what a person reads and tools/loop.sh is what an unattended
# iteration reads, so a check that only one of them carries is a check half the
# loop never runs.
LOOPSH="$ROOT/tools/loop.sh"
for tool in release-due candidate-due reclaim-scratch; do
  if grep -q "$tool.sh" "$LOOPSH"; then
    ok "unattended loop runs $tool.sh"
  else
    fail "unattended loop no longer runs $tool.sh"
  fi
done

# #462: the repository is public, so the queue an unattended iteration takes its
# issue from has to be the operator's own. Checked inside PROMPT rather than
# anywhere in the file, because the header comment is not what the child reads.
if sed -n "/^PROMPT='/,/'\$/p" "$LOOPSH" | grep -qF 'gh issue list --author @me'; then
  ok "unattended loop takes issues only from gh issue list --author @me"
else
  fail "unattended loop prompt no longer gates issues on gh issue list --author @me"
fi
if grep -qF 'gh issue list --author @me' "$ROOT/.claude/skills/laconic-loop/SKILL.md"; then
  ok "loop skill names the same issue filter as tools/loop.sh"
else
  fail "loop skill does not name the issue filter tools/loop.sh uses"
fi

# Each of these ships a --selftest and until now nothing ran any of them. An
# enforcement script that is never exercised is the same failure as a rule that
# is never shipped: it passes by not being looked at.
for tool in release-due candidate-due reclaim-scratch; do
  if out=$(bash "$ROOT/tools/$tool.sh" --selftest 2>&1); then
    ok "tools/$tool.sh --selftest passes"
  else
    fail "tools/$tool.sh --selftest passes"
    printf '%s\n' "$out" | sed 's/^/     /'
  fi
done

if grep -q "rules_cksum" "$ROOT/evals/results/loop/LEDGER.md"; then
  ok "ledger records the rules revision each attempt was tested against"
else
  fail "ledger records the rules revision each attempt was tested against"
fi
if grep -qi "including rejected" "$ROOT/evals/results/loop/LEDGER.md"; then
  ok "ledger says rejected attempts belong in it"
else
  fail "ledger no longer says rejected attempts belong in it"
fi

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
