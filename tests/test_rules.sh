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


# The four never-cut summaries must not drift. A summary that drops an item is the
# difference between a terse answer and one that omits a security warning.
#
# rules/laconic.md is checked against its "## Never cut" section only, not the
# whole file — scoped the same way the level blocks above are (lite_block,
# full_block, ultra_block). A whole-file grep would still pass if the keyword
# survives elsewhere: the word "destructive" also appears in the closing-offer
# carve-out under "Level: lite" ("Asking permission before a destructive action
# is not a closing offer..."), so an unscoped check would not notice the actual
# never-cut bullet being deleted. The other three files carry no such
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
  for f in commands/laconic.toml skills/laconic-help/SKILL.md README.md; do
    if grep -qi -- "$kw" "$ROOT/$f"; then ok "$f keeps never-cut: $kw"
    else fail "$f dropped never-cut item: $kw"; fi
  done
done

# --- statusline badge: the README copy is a second copy of a real script ---
# The README tells the user to write the badge into their own configuration
# directory rather than reference it inside the plugin, because a plugin install
# path carries a version that changes on every update and ${CLAUDE_PLUGIN_ROOT}
# is not substituted for statusLine commands. That makes the README block a
# second copy of hooks/laconic-statusline.sh — the only copy a user ever runs,
# and the one no other test touches. Assert the two are byte-identical, so a fix
# to the script cannot silently leave every installed badge on the old logic.
BADGE="$ROOT/hooks/laconic-statusline.sh"
readme_badge=$(awk '
  index($0, "cat > ~/.claude/laconic-statusline.sh <<") == 1 { f = 1; next }
  f && $0 == "LACONIC_BADGE" { f = 0; next }
  f
' "$ROOT/README.md")
if [ -z "$readme_badge" ]; then
  fail "README has no statusline badge block to compare"
elif [ "$readme_badge" = "$(cat "$BADGE")" ]; then
  ok "README badge block matches hooks/laconic-statusline.sh"
else
  fail "README badge block has drifted from hooks/laconic-statusline.sh"
fi

# The whole point of the section is a path that survives a plugin update, so the
# command the user actually pastes must not route through one that does not. A
# versioned install path breaks on the next update; ${CLAUDE_PLUGIN_ROOT} is
# rejected outright for statusLine commands. Both fail silently, which is why
# they are asserted rather than left to review. Scoped to the "command" line so
# the script's own comment warning against the variable does not trip it.
statusline_cmd=$(grep '"command": "bash' "$ROOT/README.md")
if [ -z "$statusline_cmd" ]; then
  fail "README has no statusline command line to check"
else
  for bad in 'plugins/cache' 'CLAUDE_PLUGIN_ROOT'; do
    case "$statusline_cmd" in
      *"$bad"*) fail "statusline command still routes through: $bad" ;;
      *)        ok "statusline command avoids: $bad" ;;
    esac
  done
fi

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
