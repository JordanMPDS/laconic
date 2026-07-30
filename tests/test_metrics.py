#!/usr/bin/env python3
"""Validates the readability detectors themselves.

If these fail, the metric is broken - not the plugin. A detector that cannot
separate fixture GOOD from fixture BAD measures nothing, and one that fires on
CODE would score correct prose as degraded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals" / "bench"))
import metrics  # noqa: E402

fails = 0


def check(label, cond):
    global fails
    if cond:
        print("ok   %s" % label)
    else:
        print("FAIL %s" % label)
        fails += 1


GOOD = """The deploy failed because the worker ran out of memory. If the usage
sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and
a bigger limit only delays the next kill.

Check these in order:

- run `kubectl top pod` for a few minutes
- compare the peak against the configured limit
- look at the restart count
- **401** -> the token is dead.
"""

BAD = """Deploy failed -> worker OOM. Usage steady ceiling -> raise limit.
Usage climbing -> leak, bigger limit just delays next kill.

check kubectl top pod few min. compare peak vs configured limit. check restart
count. impl detail: req handler leaks obj refs, err path never frees.
"""

CODE = """The parser returns an error value rather than raising, so the caller
decides what to do with it.

```rust
impl Parser {
    fn parse(&self) -> Result<Ast, Err> { self.inner() }
}
```

Run `make test -> out.log` to capture the output, and read `impl.rs` for the
detail. The `err` variant is described at https://example.com/docs in section 4.
"""

g = metrics.score(GOOD)
b = metrics.score(BAD)
c = metrics.score(CODE)

check("good prose has no violations", g["violations"] == 0)
check("good prose keeps a normal article rate", g["article_rate"] >= 0.05)
check("good prose aux_verb_rate is non-zero", g["aux_verb_rate"] > 0)
check("good prose bullets do not trip lowercase-start",
      g["sentence_initial_lowercase"] == 0)
# NOTE: the check above is tautological against the GOOD fixture - its
# bullets start with "-", and "-".islower() is False regardless of whether
# STRUCTURAL actually filters them. A single-sentence bullet doesn't
# discriminate either: the leading marker survives as the sentence's first
# character even with STRUCTURAL disabled, so it never reads as lowercase.
# A two-sentence bullet does: with STRUCTURAL correctly dropping the whole
# bulleted line, there is no paragraph at all and this scores 0. With
# STRUCTURAL disabled, the line becomes its own paragraph and the sentence
# split lands after "first.", exposing "then confirm..." - genuinely
# lowercase-initial - as its own sentence.
lowercase_after_marker = metrics.score("- run the check first. then confirm the migration.")
check("bullet text starting lowercase after the marker does not trip "
      "lowercase-start (STRUCTURAL drops the whole bulleted line)",
      lowercase_after_marker["sentence_initial_lowercase"] == 0)

check("bad prose is flagged", b["violations"] >= 5)
check("bad prose arrows counted", b["symbol_connectors"] >= 3)
check("bad prose abbreviations counted", b["abbreviated_prose"] >= 3)
check("bad prose lowercase starts counted", b["sentence_initial_lowercase"] >= 2)
check("bad prose article rate collapses", b["article_rate"] < 0.03)
check("bad prose aux_verb_rate is lower than good", b["aux_verb_rate"] < g["aux_verb_rate"])
check("detectors separate good from bad", g["violations"] < b["violations"])
check("article rate separates good from bad by >2x",
      g["article_rate"] > 2 * b["article_rate"])

check("code blocks do not trip detectors", c["violations"] == 0)
check("inline code does not trip detectors", c["symbol_connectors"] == 0)
check("code-block identifiers are not counted as abbreviations",
      c["abbreviated_prose"] == 0)

# The three checks above all survive deleting FENCE entirely: CODE's fenced
# block has an even number of backticks (3 to open + 3 to close), so INLINE's
# `[^`]*` pairing incidentally consumes the whole thing anyway (it just pairs
# adjacent backticks two at a time). A fence with a single stray backtick
# inside breaks that parity: the arrow ends up in the *gap* between two
# INLINE matches, not inside either one, so only FENCE (which matches the
# whole ``` ... ``` span regardless of what's inside it) can strip it.
FENCE_ONLY = """Example:

```
`weird -> marker in the fence.
```

See above.
"""
fence_only = metrics.score(FENCE_ONLY)
check("a fenced block with an odd internal backtick count (INLINE alone "
      "cannot consume it) still has its arrow stripped by FENCE",
      fence_only["symbol_connectors"] == 0)

# The rule forbids arrows "in running prose" specifically - a bullet's arrow
# is structural markdown, not prose, and a numeric progression's arrow isn't
# standing in for a conjunction. Neither should count. A genuine running-prose
# arrow still must.
check("good prose bullet with an arrow does not trip symbol_connectors",
      g["symbol_connectors"] == 0)
bullet_arrow = metrics.score("- **401** -> the token is dead.")
check("arrow inside a bullet scores 0 symbol connectors",
      bullet_arrow["symbol_connectors"] == 0)
numeric_progression = metrics.score("The queue climbed (7 -> 11 -> 14) over the hour.")
check("numeric progression arrows score 0 symbol connectors",
      numeric_progression["symbol_connectors"] == 0)
running_prose_arrow = metrics.score("Deploy failed -> restart.")
check("genuine running-prose arrow still scores 1",
      running_prose_arrow["symbol_connectors"] == 1)

check("violations are auditable", len(b["spans"]) == b["violations"])

# Direct auxiliary verb counting on a short known string
aux_test = metrics.score("The system was running. It is good.")
check("aux verbs are counted directly", aux_test["aux_verb_rate"] > 0 and aux_test["words"] == 7)

# Test contracted auxiliaries
contraction_test = metrics.score("The process doesn't fail. It isn't broken.")
check("contracted auxiliaries are counted", contraction_test["aux_verb_rate"] > 0)

# Test abbreviation periods don't trip false positives
abbrev_test = metrics.score("We tested it, e.g. running the code.")
check("abbreviation periods don't trip lowercase-start", abbrev_test["sentence_initial_lowercase"] == 0)

# Test sentence-ending abbreviations still catch lowercase starts
etc_test = metrics.score("That is impossible, etc. it makes no sense.")
check("sentence-ending abbrevs catch real violations (etc)", etc_test["sentence_initial_lowercase"] >= 1)

st_test = metrics.score("We turned onto Main St. it was getting dark.")
check("sentence-ending abbrevs catch real violations (St)", st_test["sentence_initial_lowercase"] >= 1)

check("never_cut_missing finds absent keywords",
      metrics.never_cut_missing("the sessions cascade", ["cascade", "invoices"])
      == ["invoices"])
check("never_cut_missing is case-insensitive",
      metrics.never_cut_missing("CASCADE deletes rows", ["cascade"]) == [])

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
