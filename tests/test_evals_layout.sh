#!/usr/bin/env bash
# Asserts the evals directory layout the bench harness depends on.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fails=0
fail() { printf 'FAIL %s\n' "$1"; fails=$((fails + 1)); }
ok()   { printf 'ok   %s\n' "$1"; }

for c in decision walkthrough destructive badnews; do
  if [ -f "$ROOT/evals/cases/$c/prompt.md" ]; then
    ok "case $c has prompt.md under evals/cases"
  else
    fail "case $c has prompt.md under evals/cases"
  fi
done

if [ ! -d "$ROOT/evals/decision" ]; then
  ok "old top-level case dirs removed"
else
  fail "old top-level case dirs removed"
fi

if grep -q 'evals/cases/' "$ROOT/evals/run.sh"; then
  ok "run.sh globs evals/cases"
else
  fail "run.sh globs evals/cases"
fi

if grep -q 'evals/scratch' "$ROOT/evals/run.sh"; then
  ok "run.sh writes to evals/scratch"
else
  fail "run.sh writes to evals/scratch"
fi

if grep -qx 'evals/scratch/' "$ROOT/.gitignore"; then
  ok "gitignore excludes evals/scratch"
else
  fail "gitignore excludes evals/scratch"
fi

if grep -qx 'evals/results/' "$ROOT/.gitignore"; then
  fail "gitignore no longer excludes evals/results"
else
  ok "gitignore no longer excludes evals/results"
fi

# 19 since 2026-08-11: design-rate-limit and design-retry take the scoped
# output_tokens target from six case/model cells to ten. At six, one cell that
# has never moved outside its own noise takes the two-sided sign test from
# p = 0.031 to p = 0.219, which rejected rounds 11 and 14 outright. Eight cells
# does not fix it (7 of 8 is p = 0.070); ten does (9 of 10 is p = 0.021).
#
# 22 since 2026-08-12: design-cache, design-realtime and design-upload, for
# #88. The first five design cases cannot separate the treatment arm from the
# arm told to drop articles and use arrows, because on all five the answer a
# model gives without opening a file is already the fixture's answer. These
# three are built the other way round: the fixture contradicts what the model
# would otherwise say. A fourth candidate, design-pagination, was built and
# discarded - keyset paging is the conventional answer to it, so it had the
# defect it was meant to fix. See design-discrimination.md.
#
# 25 since 2026-09-01: confirm-metric, confirm-index and confirm-rollback, for
# the over-length cluster (#46, #60, #113, #136, #150, #116). Every other case
# asks an open-ended question, so the shape #136 reports - a closed question
# whose correct answer is a single line - was not represented at all. Each of
# the three states a conclusion in its fixture and asks the model to confirm
# it, and each carries a qualification the fixture attaches to that conclusion,
# so the judge grades whether the answer is right while a scoped output_tokens
# target carries the claim about how much was said. With the three verdict-*
# cases they give a six-cell sonnet scope, which is the minimum the two-sided
# sign test can reach alpha on.
#
# 28 since 2026-09-01: recall-metric, recall-index and recall-rollback, the
# multi-turn twins of the three confirm-* cases that #166 made possible. Same
# fixture and same closed question; the only difference is that turn 1 asks the
# open question first, so the model is confirming a conclusion it wrote rather
# than one it read. That makes confirm-* the exact control for recall-*, which
# is the contrast #136 describes and the one round 32 could not construct.
#
# 31 since 2026-09-01: wide-metric, wide-index and wide-rollback, for round 34.
# Round 33 measured ownership - a model confirming a conclusion it wrote rather
# than one it read - at 6 of 6 cells and 29 of 30 paired runs, and found it
# worth only about a third more words, far short of what #136 reports. These
# three hold ownership constant and vary the one thing left: they share their
# prompt byte for byte with the recall-* case of the same stem, and differ only
# in that the fixture is 2.3x to 3.8x larger. The extra material is available to
# the answer but not required by the closed question, so a correct answer is the
# same length as recall-*'s. If it is not, subject size is what the over-length
# cluster is actually about.
#
# 34 since 2026-09-01: deep-metric, deep-index and deep-rollback, for round 35.
# Rounds 33 and 34 measured two of the three mechanisms #136 offers. Ownership
# is real and worth about a third more words; subject size, at +3% of context,
# is worth nothing. These three test the one the issue's own wording points at -
# "a lot of recent context it is proud of" is a claim about the volume of the
# model's OWN prior output, and recall-* supplies exactly one prior answer.
# Each asks five turns where recall-* asks two, sharing its fixture, its final
# question and its trap. The three added turns are deliberately kept off what
# the trap grades, so the closed question stays fresh and the accumulated
# output is the only thing that varies.
#
# 36 since 2026-09-01: drift-service and cold-service, for #113. That issue
# reports a lite rule - no closing offers - breaking on one turn and holding on
# the next, and argues the binary signal is worth more than the length one it
# accompanies. The closing-offer rate is now measurable, but the existing
# multi-turn family reads 0 of 315 because its deliverable is the answer itself
# and there is nothing to offer. These two ask design questions about a service,
# which is the shape that produces offers, and they share a fixture and a
# byte-identical final question: cold-service asks it at turn 1 and
# drift-service asks it at turn 5. That pair is what makes drift readable.
#
# 37 since 2026-09-04: quota-merge, for #116. That issue is about volunteered
# *work* rather than volunteered prose - a comprehension question answered
# correctly and then substantiated with analysis nobody asked for - and until
# now nothing could score it. evals/results/loop/volunteered-work.md found the
# behaviour already in the suite, on `conditional`, at 21% of sonnet runs; but
# `conditional` grades rule-adherence, so no rule edit may be proposed from it.
#
# The obstacle to a scorable one was CRITERIA.md's own rule: every case ends
# "Don't edit anything." or "its verdicts measure whether the model chose to
# act". quota-merge is the first case to drop that clause, and it drops it on
# evidence - judging 80 conditional runs put an editing response's trap pass
# rate at 24/39 against 22/41 for a non-editing one, p = 0.5055, so the
# diagnosis does not migrate into the diff.
#
# So the case can be graded on quality while the behaviour is read off the tool
# list as a syntactic counter, the way closing offers and one_turn are. The
# question is an interrogative whose deliverable is understanding, the fixture
# is one the model could act on instead, and the trap grades two fixture facts:
# that the merge is possible, and that reconcile() is the only writer of the
# day totals billing reads.
count=$(ls -d "$ROOT"/evals/cases/*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$count" = "37" ]; then ok "37 cases present"; else fail "37 cases present (found $count)"; fi

design=$(ls -d "$ROOT"/evals/cases/design-*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$design" -ge 5 ]; then
  ok "at least 5 design cases, so the scoped token target has 10 cells"
else
  fail "at least 5 design cases, so the scoped token target has 10 cells (found $design)"
fi

# Every design case added for #88 records the discrimination check it passed.
# Two numbers, both computed from one snapshot: `headroom`, the share of
# responses that resolve the fixture's contradiction, and `bite`, the pass rate
# among those that do against those that do not. A case where nearly every
# response resolves the fixture cannot detect a rule that stops them resolving
# it, and a case where both groups pass alike is grading something other than
# whether the fixture was read. Five cases reached the design scope without
# either number ever being computed, which is how the scope came to contain
# nothing that could see the round 15 edit.
for dir in "$ROOT"/evals/cases/design-cache "$ROOT"/evals/cases/design-realtime \
           "$ROOT"/evals/cases/design-upload; do
  name=$(basename "$dir")
  if python3 -c "
import json,sys
d=json.load(open('$dir/expect.json'))
c=d.get('discrimination')
sys.exit(0 if isinstance(c,dict) and isinstance(c.get('snapshot'),str) and c['snapshot']
         and all(k in c for k in ('resolves_fixture','pass_when_resolved',
                                  'pass_when_not','fisher'))
         else 1)
"; then
    ok "case $name records its discrimination check"
  else
    fail "case $name records its discrimination check"
  fi
done

for dir in "$ROOT"/evals/cases/*/; do
  name=$(basename "$dir")
  if [ -f "$dir/expect.json" ]; then
    ok "case $name has expect.json"
  else
    fail "case $name has expect.json"
  fi
  if python3 -c "
import json,sys
d=json.load(open('$dir/expect.json'))
sys.exit(0 if isinstance(d.get('never_cut'),list) and isinstance(d.get('trap'),str) and d['trap'] else 1)
"; then
    ok "case $name expect.json has never_cut list and trap text"
  else
    fail "case $name expect.json has never_cut list and trap text"
  fi
done

# --- Never-cut coverage ---
# never_cut_failures is one of the four fatal counters, and a case with an empty
# list contributes 0 to it whatever the response did. So the set of cases that
# carry keywords IS the denominator of every "never-cut held" claim the loop
# prints, and it is not visible anywhere except in 36 separate expect.json
# files. #10 is the issue that got the denominator wrong once already.
#
# quota-merge joined in 2026-09-04 with an empty list, deliberately: the
# admission criterion below wants a token measured against archived responses,
# and a case generated for the first time has none to measure against.
#
# The set is pinned here so that neither direction can happen quietly. Emptying
# a list shrinks the denominator while the round still reports "never-cut held".
# Adding one to a case whose protected content is conceptual inflates the
# denominator with a check that fires on correct answers - which is worse than
# no check, and is why `decision`, `floor` and `ordered-steps` were emptied in
# round 2 of the original build. The admission criterion is in
# evals/CRITERIA.md: a token a correct answer cannot avoid, meaning a literal
# identifier, flag, status code or schema name. Not a concept with synonyms.
#
# The *-index family was measured against 541 archived multi-turn responses
# before being admitted; every other candidate for the multi-turn families was
# rejected by the same sweep. See evals/results/never-cut-coverage.md. Changing
# this list means doing that measurement, not editing the line below.
covered=$(python3 - "$ROOT" <<'PY'
import json
from pathlib import Path
import sys
root = Path(sys.argv[1]) / "evals" / "cases"
names = sorted(d.name for d in root.iterdir()
               if d.is_dir() and json.loads((d / "expect.json").read_text())["never_cut"])
print(" ".join(names))
PY
)
expected="badnews code-fidelity conditional confirm-index deep-index destructive recall-index walkthrough wide-index"
if [ "$covered" = "$expected" ]; then
  ok "9 of 37 cases carry never_cut keywords, and they are the measured set"
else
  fail "never_cut coverage changed: expected [$expected], found [$covered]"
fi

# --- Grading provenance ---
# Every case declares where its trap criteria came from, because that decides
# what its verdicts may be used for. A `quality` case is the only kind that
# supports a comparison between arms, so its criterion must be answerable from
# the task and the fixture alone. `decision` and `floor` were read as evidence
# once, and the claim had to be retracted when it turned out their criteria
# were laconic's own prohibitions restated - the treatment arm was being scored
# against the text it had been handed.
#
# The forbidden list below is the vocabulary of form: length, ceremony,
# structure. A criterion that reaches for any of it is grading how the answer
# was written rather than whether it was right, which is precisely the
# contamination. It is checked against the trap only, not criteria_source -
# that field names rules/laconic.md on purpose for the contaminated cases.
grading_report=$(python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
VALID = ("quality", "safety", "rule-adherence")
FORBIDDEN = ("terse", "concise", "brief", "shorter", "length", "verbose",
             "preamble", "closing offer", "unrequested", "survey", "padded",
             "padding", "hedg", "pleasantr", "recap", "arrow", "article",
             "word count", "one recommendation")

for d in sorted(p for p in (root / "evals" / "cases").iterdir() if p.is_dir()):
    e = json.loads((d / "expect.json").read_text())
    g = e.get("grading")
    print(("ok   " if g in VALID else "FAIL ")
          + "case %s declares a valid grading (%r)" % (d.name, g))
    src = e.get("criteria_source")
    print(("ok   " if isinstance(src, str) and src.strip() else "FAIL ")
          + "case %s records where its criteria came from" % d.name)
    # saturated_models drives a gate exclusion, so a malformed value must fail
    # loudly instead of silently excluding nothing (or everything).
    sat = e.get("saturated_models")
    if sat is not None:
        okv = (isinstance(sat, dict) and sat
               and all(isinstance(m, str) and m
                       and isinstance(r, str) and r.strip()
                       for m, r in sat.items()))
        print(("ok   " if okv else "FAIL ")
              + "case %s saturated_models maps each model to a non-empty reason" % d.name)
    if g != "quality":
        continue
    hits = [w for w in FORBIDDEN if w in e.get("trap", "").lower()]
    print(("ok   " if not hits else "FAIL ")
          + "quality case %s grades the task, not the rule text%s"
          % (d.name, "" if not hits else " (found: %s)" % ", ".join(hits)))
PY
)
printf '%s\n' "$grading_report"
fails=$((fails + $(printf '%s\n' "$grading_report" | grep -c '^FAIL ')))

# At least one case must actually be gradeable on answer quality. Without one,
# the benchmark can say the plugin is shorter and still say nothing about
# whether it is as useful, which is the gap issue #9 exists to close.
nq=$(grep -l '"grading": "quality"' "$ROOT"/evals/cases/*/expect.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$nq" -ge 1 ]; then
  ok "at least one quality-graded case exists (found $nq)"
else
  fail "no quality-graded case exists - no answer-quality claim is possible"
fi

# The holdout exists to be scored once, at ship time. A holdout case the
# default glob reaches is a dev case, and it stops being a holdout the moment
# somebody optimizes against it.
hcount=$(ls -d "$ROOT"/evals/holdout/*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$hcount" -ge 4 ]; then
  ok "at least 4 holdout cases present (found $hcount)"
else
  fail "at least 4 holdout cases present (found $hcount)"
fi

for d in "$ROOT"/evals/holdout/*/; do
  c=$(basename "$d")
  if [ -f "$d/prompt.md" ] && [ -f "$d/expect.json" ]; then
    ok "holdout case $c has prompt.md and expect.json"
  else
    fail "holdout case $c has prompt.md and expect.json"
  fi
done

if ls -d "$ROOT"/evals/cases/holdout-*/ >/dev/null 2>&1; then
  fail "a holdout case has leaked into evals/cases, where the default glob reaches it"
else
  ok "holdout cases stay outside the default case glob"
fi

# Two never-cut items and a requested explanation is the coverage the holdout
# is for. A holdout of four short questions would pass every rule edit that
# compresses by cutting a warning.
hsafety=$(grep -l '"grading": "safety"' "$ROOT"/evals/holdout/*/expect.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$hsafety" -ge 2 ]; then
  ok "holdout covers at least 2 never-cut cases (found $hsafety)"
else
  fail "holdout covers at least 2 never-cut cases (found $hsafety)"
fi

printf '\n%d failure(s)\n' "$fails"
[ "$fails" -eq 0 ]
