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

printf '\n%d failure(s)\n' "$fails"
[ "$fails" = "0" ]
