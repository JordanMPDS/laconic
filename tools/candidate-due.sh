#!/usr/bin/env bash
# Is a rule candidate owed?
#
# The loop's job is rules/laconic.md, and it can go a long time without touching
# it. A round that measures the instrument is cheaper to justify than a round
# that proposes an edit: it always produces a publishable number, it never
# rejects, and it always suggests the next measurement. So the loop drifts into
# measuring, one defensible round at a time. Round 55 accepted on 2026-09-08 and
# rounds 56 through 63 were all instrument rounds — eight in a row, the reading
# cost, the clause split, two dilution ablations, the demonstration block, two
# mechanism rounds and an assay that did not fire. Every one was worth running
# and none of them proposed a rule the plugin could ship.
#
# The cap: at most one measuring round may sit between two candidate rounds.
# Two in a row is what this refuses, which makes the check a question about the
# previous round alone.
#
#   bash tools/candidate-due.sh            # exit 1 if the next round must test an edit
#   bash tools/candidate-due.sh --selftest
#
# The signal is the round document, because that is where a round states its own
# design and it is committed before any generation. No state file, no label, and
# nothing for a fresh process with no memory of round 63 to reconstruct.
set -uo pipefail

ROUNDS=evals/results/loop
LABEL=rules

# A round document declares its kind two ways, and the repository already uses
# both. An instrument round disclaims the edit in its registration preamble —
# "**This round proposes no rule edit.**" (rounds 32 to 37, 42, 43, 53, 54, 56,
# 57, 63) or "**Registered 2026-09-09, before any run. No rule edit.**" (58 to
# 62). A candidate round carries the edit itself under a "## The edit" heading
# (rounds 44 to 52 and 55, and as far back as round 01). No document in the
# archive has both, and no instrument round has ever had an edit section.
#
# The preamble is everything above the first `##`. A disclaimer further down is
# not a declaration: round 41 says "No rule edit" in its results section, where
# it is a finding rather than a registration, and reads as undeclared here. That
# is the safe direction — an undeclared round blocks and asks, rather than being
# guessed into resetting the cap.
round_kind() { # <path to round-N.md> -> instrument|candidate|undeclared
  local f=$1
  if awk '/^## /{exit} {print}' "$f" | grep -qi 'no rule edit'; then
    printf 'instrument'
  elif grep -qi '^## The edit' "$f"; then
    printf 'candidate'
  else
    printf 'undeclared'
  fi
}

# Numerically, highest first. `round-28-composition.md` and
# `round-63-sentinel.md` are companion documents rather than rounds, and a
# lexical sort would put round 9 above round 63.
round_numbers() {
  ls "$ROUNDS" 2>/dev/null \
    | sed -n 's/^round-\([0-9][0-9]*\)\.md$/\1/p' \
    | sort -rn
}

# `bash tools/candidate-due.sh --selftest` — the classifier driven directly on
# the three shapes the archive contains, then the whole script against a scratch
# tree. The end-to-end half is what catches the failure that matters: a script
# that reports "nothing owed" because it found no rounds is indistinguishable
# from one that found a candidate.
if [ "${1:-}" = "--selftest" ]; then
  failed=0
  check() { # name, expected-grep, actual
    if printf '%s' "$3" | grep -qE "$2"; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted /%s/ in:\n%s\n' "$1" "$2" "$3"
  }
  checkst() { # name, expected-status, actual-status
    if [ "$2" = "$3" ]; then return 0; fi
    failed=$((failed + 1))
    printf 'FAIL %s\n  wanted exit %s, got %s\n' "$1" "$2" "$3"
  }

  tmp=$(mktemp -d) || exit 1
  trap 'rm -rf "$tmp"' EXIT
  r=$tmp/repo
  mkdir -p "$r/tools" "$r/$ROUNDS"
  cp "$0" "$r/tools/candidate-due.sh"
  doc() { # <number> <preamble> <body heading>
    { printf '# Round %s\n\n%s\n\n%s\n\nprose\n' "$1" "$2" "$3"; } \
      > "$r/$ROUNDS/round-$1.md"
  }
  due() { (cd "$r" && bash tools/candidate-due.sh 2>&1); }

  out=$(due); st=$?
  check "no round documents is not silently nothing owed" 'no round document' "$out"
  checkst "and exits 1 rather than passing" 1 "$st"

  doc 55 'Registration.' '## The edit'
  check "an edit section makes it a candidate" '^candidate$' \
    "$(cd "$r" && round_kind "$ROUNDS/round-55.md")"
  out=$(due); st=$?
  check "a candidate round owes nothing" 'no candidate owed' "$out"
  checkst "and exits 0" 0 "$st"

  doc 56 '**This round proposes no rule edit.** It measures one that shipped.' '## Design'
  check "a preamble disclaimer makes it an instrument round" '^instrument$' \
    "$(cd "$r" && round_kind "$ROUNDS/round-56.md")"
  out=$(due); st=$?
  check "one measuring round spends the allowance" 'candidate owed' "$out"
  check "and names the round that must carry it" 'round 57' "$out"
  check "and names the last round that tested one" 'round 55' "$out"
  check "and says where candidates come from" "labelled .$LABEL." "$out"
  checkst "and exits 1 so a caller can branch on it" 1 "$st"

  doc 57 '**Registered 2026-09-09, before any run. No rule edit.**' '## Design'
  out=$(due)
  check "a second measuring round counts the streak" '2 rounds in a row' "$out"
  check "and still points at the last candidate" 'round 55' "$out"

  doc 58 'Registration.' '## The edit'
  out=$(due); st=$?
  check "a candidate round settles it" 'no candidate owed' "$out"
  checkst "and exits 0 again" 0 "$st"

  # Round 41 says "No rule edit" in its results section. That is a finding, not
  # a registration, and guessing from it would reset the cap on a round that
  # never declared anything.
  doc 59 'Registration.' '## Results

No rule edit is proposed.'
  check "a disclaimer below the registration block does not declare a kind" \
    '^undeclared$' "$(cd "$r" && round_kind "$ROUNDS/round-59.md")"
  out=$(due); st=$?
  check "an undeclared latest round asks rather than guesses" 'does not say' "$out"
  checkst "and exits 1 until it says" 1 "$st"

  # Companion documents are not rounds, and the numbering is arithmetic.
  rm "$r/$ROUNDS/round-59.md"
  : > "$r/$ROUNDS/round-58-composition.md"
  doc 9 '**This round proposes no rule edit.**' '## Design'
  out=$(due)
  check "a companion document is not a round" 'round 59' "$out"
  check "and round 9 does not outrank round 58" 'no candidate owed' "$out"

  [ "$failed" -eq 0 ] && echo "candidate-due.sh selftest: 19/19 passed" \
    || echo "candidate-due.sh selftest: $failed failed"
  exit $([ "$failed" -eq 0 ] && echo 0 || echo 1)
fi

cd "$(dirname "$0")/.."

mapfile -t nums < <(round_numbers)
if [ "${#nums[@]}" -eq 0 ]; then
  echo "no round document found under $ROUNDS — cannot tell what the last round did."
  exit 1
fi

last=${nums[0]}
next=$((last + 1))
kind=$(round_kind "$ROUNDS/round-$last.md")

if [ "$kind" = undeclared ]; then
  echo "round $last does not say whether it tested a rule candidate."
  echo "A round declares that in its registration: either the preamble disclaims the edit"
  echo "(\"**This round proposes no rule edit.**\") or the document carries a \"## The edit\""
  echo "section holding it. Say which round $last was, then run this again."
  exit 1
fi

# Walk back for the disclosure, not for the decision. The decision is the
# previous round alone, because two in a row is what the cap forbids.
streak=0
prev_candidate=
for n in "${nums[@]}"; do
  case "$(round_kind "$ROUNDS/round-$n.md")" in
    instrument) streak=$((streak + 1)) ;;
    candidate)  prev_candidate=$n; break ;;
    undeclared) break ;;
  esac
done
[ -n "$prev_candidate" ] && since="the last rule candidate was round $prev_candidate" \
  || since="no round before it in the archive tested one"

if [ "$kind" = candidate ]; then
  echo "no candidate owed: round $last tested a rule candidate, so round $next may measure."
  exit 0
fi

echo "candidate owed: round $last measured, and round $next may not."
if [ "$streak" -eq 1 ]; then
  echo "One measuring round is the allowance and round $last spent it; $since."
else
  echo "$streak rounds in a row have measured the instrument, and $since."
fi
echo
echo "At most one measuring round sits between two candidates. Take an open issue"
echo "labelled \`$LABEL\`, register round $next against it, and put an edit to"
echo "rules/laconic.md under a \"## The edit\" heading that the round can accept or"
echo "reject. Every measuring round in that streak was worth running, which is why"
echo "the loop needs a cap rather than an argument."
exit 1
