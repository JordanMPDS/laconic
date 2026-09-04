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
- **401** means the token is dead.
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

# A bullet is where the forbidden arrow actually lives. rules/laconic.md bans
# arrows "after a bold label", "in a 'quick runbook' line" and "inside a quoted
# flow" - all structural positions - so exempting structural lines exempted the
# rule's own worked examples. It cost loop round 01 a false 7 -> 0 while the
# model kept writing the same chains one list marker to the left; counted
# honestly that round read 26 -> 9. Only a numeric progression stays exempt: it
# quotes a series rather than standing in for a conjunction.
check("prose with no arrow anywhere scores 0 symbol connectors",
      g["symbol_connectors"] == 0)
bullet_arrow = metrics.score("- **401** -> the token is dead.")
check("an arrow after a bold label in a bullet counts",
      bullet_arrow["symbol_connectors"] == 1)
numbered_step_arrow = metrics.score("2. If valid -> return it immediately")
check("an arrow inside a numbered step counts",
      numbered_step_arrow["symbol_connectors"] == 1)
quoted_flow_arrow = metrics.score("> mint the key -> publish it -> retire the old")
check("an arrow inside a quoted flow counts",
      quoted_flow_arrow["symbol_connectors"] == 2)
numeric_progression = metrics.score("The queue climbed (7 -> 11 -> 14) over the hour.")
check("numeric progression arrows score 0 symbol connectors",
      numeric_progression["symbol_connectors"] == 0)
running_prose_arrow = metrics.score("Deploy failed -> restart.")
check("genuine running-prose arrow still scores 1",
      running_prose_arrow["symbol_connectors"] == 1)

# B1: STRUCTURAL required no following whitespace for -*+, so a bolded prose
# paragraph like "**Request A**: ..." matched as a bullet and the whole line
# was skipped by _symbol_hits - an arrow chain in running prose scored 0.
# This is the regression this fix exists to prevent: it MUST still count.
bolded_arrow_chain = metrics.score(
    "**Request A**: Calls `currentToken()` -> token is expired -> calls "
    "`refresh()` -> `inFlight` is null -> starts the fetch."
)
check("a bolded-label prose line with an arrow chain is counted, not mistaken "
      "for a bullet (the regression this whole fix prevents)",
      bolded_arrow_chain["symbol_connectors"] == 4)

# Same root cause, two more false negatives: a bare arrow at line start, and an
# arrow left with only leading whitespace after an inline-code span is erased.
# Neither is a bullet; both must still count their arrow.
bare_arrow_line = metrics.score("-> then drain the queue.")
check("a line starting with a bare arrow (not a markdown bullet) counts its "
      "arrow", bare_arrow_line["symbol_connectors"] == 1)

erased_inline_code_arrow = metrics.score("`pool.max` -> raise it to 40")
check("an arrow stranded after an inline-code span is stripped to leading "
      "whitespace still counts (not mistaken for a '-' bullet)",
      erased_inline_code_arrow["symbol_connectors"] == 1)

# The genuine catch must not weaken: a real ordered-steps arrow chain in
# running prose (not bulleted, not bolded) still scores every arrow.
runbook_arrow_chain = metrics.score(
    "Rough runbook: generate new key pair -> add to JWKS/key store as "
    "non-primary -> let it propagate to all verifiers (respect any cache "
    "TTL) -> cut over signing to the new key -> wait out the old token TTL "
    "-> remove the old key."
)
check("a genuine running-prose arrow chain still scores every arrow",
      runbook_arrow_chain["symbol_connectors"] == 5)

# B3: a sentence legitimately opening with a lowercase filename/dotted
# identifier (not wrapped in backticks) must not be flagged as a grammar
# violation - "auth.js is self-contained" is correct usage, not a broken
# sentence start.
filename_sentence_start = metrics.score(
    "auth.js is self-contained, no callers in this repo."
)
check("a sentence opening with a bare dotted identifier (filename) is not "
      "flagged as a lowercase sentence start",
      filename_sentence_start["sentence_initial_lowercase"] == 0)

# A genuine lowercase-start violation must still be caught even though it
# isn't a dotted identifier.
genuine_lowercase_start = metrics.score(
    "This is fine. then the response starts a new sentence lowercase."
)
check("a genuine lowercase sentence start (not a filename) is still caught",
      genuine_lowercase_start["sentence_initial_lowercase"] >= 1)

# B3: FENCE.sub(" ", text) leaves the removed fenced block as a lone
# whitespace-only line, which _paragraph_prose reads as a paragraph break -
# turning the grammatical continuation after the fence into a false "new
# sentence" that starts lowercase.
fence_orphaned_continuation = metrics.score(
    "Here's the safer sequence:\n"
    "```sql\n"
    "TRUNCATE users RESTART IDENTITY CASCADE;\n"
    "```\n"
    "or if you do want to actually drop/recreate: run the migration by hand."
)
check("prose split by a fenced code block stays one paragraph, so the "
      "continuation after the fence is not flagged as a new lowercase "
      "sentence", fence_orphaned_continuation["sentence_initial_lowercase"] == 0)

fence_orphaned_with_blank_lines = metrics.score(
    "Suggested approach:\n\n"
    "```sql\n"
    "TRUNCATE users RESTART IDENTITY CASCADE;\n"
    "```\n\n"
    "then reseed from the fixture once the schema is back."
)
check("prose split by a fenced code block flanked by blank lines also stays "
      "one paragraph, not a false lowercase sentence start",
      fence_orphaned_with_blank_lines["sentence_initial_lowercase"] == 0)

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

# structure_markers is the denominator issue #20 needed: it has to see the
# three positions the arrow rule names, and it has to ignore a fenced block,
# or a response quoting a bulleted config file would read as a runbook.
struct = metrics.structure_markers(
    "**Recommended order:**\n\n"
    "1. Dump the table.\n"
    "2. Drop it.\n"
    "- then reseed\n"
)
check("structure_markers counts numbered steps", struct["numbered"] == 2)
check("structure_markers counts bullets", struct["bullets"] == 1)
check("structure_markers counts bold labels", struct["bold_labels"] == 1)
check("structure_markers totals the three", struct["total"] == 4)

fenced_struct = metrics.structure_markers(
    metrics.split_text("Plain prose.\n\n```yaml\n- one\n- two\n```\n\nMore prose.")[0]
)
check("structure_markers ignores a bulleted fenced block",
      fenced_struct["total"] == 0)

check("never_cut_missing finds absent keywords",
      metrics.never_cut_missing("the sessions cascade", ["cascade", "invoices"])
      == ["invoices"])
check("never_cut_missing is case-insensitive",
      metrics.never_cut_missing("CASCADE deletes rows", ["cascade"]) == [])

# closing_offers is the [#113] detector. The cases below are the false
# positives the first draft produced on round 35 - a limitation and a request
# for information needed to answer - both of which are never-cut content, plus
# the confirmation the rules carve out explicitly.
check("closing_offers finds an offer to do more work",
      metrics.closing_offers("That is the shape of it. Want me to sketch the migration?")
      == ["Want me to"])
check("closing_offers finds a let-me-know closer",
      metrics.closing_offers("Done. Let me know if you want the trigger SQL too.")
      == ["Let me know if"])
check("closing_offers ignores a stated limitation",
      metrics.closing_offers(
          "The document gives no order counts, so I can't quantify the impact.") == [])
check("closing_offers ignores a request for what is needed to answer",
      metrics.closing_offers(
          "The source is not in this directory. Point me at chargeOrder() and I can read it.")
      == [])
check("closing_offers ignores a destructive confirmation",
      metrics.closing_offers(
          "DROP TABLE users CASCADE drops both constraints and orphans every "
          "dependent row. Should I proceed?") == [])
# The three the recall sample found the first pattern missing. Each is an offer
# to do work; the negative cases above are questions asking for information.
check("closing_offers finds an offer to go read the codebase",
      metrics.closing_offers(
          "Want to explore this deeper, or should I look at the actual codebase?")
      != [])
check("closing_offers finds a conditional offer to implement",
      metrics.closing_offers(
          "If you show me your auth code, I can help wire up the dual-key path.")
      != [])
check("closing_offers finds a would-you-like-to offer",
      metrics.closing_offers("Would you like to dig into any of these approaches?")
      != [])
check("closing_offers still ignores a question asking for information",
      metrics.closing_offers(
          "What is your current token lifetime and infrastructure setup?") == [])

check("closing_offers returns every match, not just the first",
      len(metrics.closing_offers(
          "Want me to draft it? Let me know if that helps.")) == 2)

# preamble(): the unit is a sentence, and one that also asserts is not preamble.
check("preamble finds a pure announcement",
      metrics.preamble("Here's the complete token refresh flow:\n\n## Normal") is not None)
check("preamble finds a let-me opener",
      metrics.preamble("Let me walk through the flow:\n\n1. First") is not None)
check("preamble finds a pleasantry",
      metrics.preamble("Sure! The limiter fails open on Redis errors.") is not None)
check("preamble ignores an announcement that also asserts",
      metrics.preamble(
          "Here's the full flow in auth.js (41 lines total, no other files "
          "reference it - this module is self-contained).") is None)
# Without blanking backticks the terminator matches the dot inside the filename.
# --- the two clauses the recall pass added (#179) -------------------------
# Recall was registered in #179 as step 2 and was not done until 2026-09-04.
# It found 9 genuine misses in 40 hand-read negatives, ALL of them baseline
# responses, and both gaps were traceable to the issue's own text.
#
# Gap 1: criterion 3 - "narrate a tool call the user can already see" - was
# registered and never built. Five misses were exactly that shape.
check("preamble catches a bare tool narration",
      metrics.preamble("Found it. The limiter fails open on Redis errors.") is not None)
check("preamble catches the read-it narration",
      metrics.preamble("I read it. The plan has one structural flaw.") is not None)
check("preamble catches a narration naming the file",
      metrics.preamble("Read `schema.sql`. It has real problems.") is not None)
# The span bound is what separates narration from a sentence that also asserts:
# the assertion runs past 55 characters, so it never reaches the terminator.
check("preamble ignores a narration that also asserts",
      metrics.preamble(
          "I read it and the plan has one structural flaw that will cause an "
          "outage.") is None)

# Gap 2: the announcement clause was anchored at position 0, so a scoping
# lead-in defeated it. Four misses were that shape.
check("preamble catches an announcement behind a scoping lead-in",
      metrics.preamble("For a marketplace listing with phone photos, here's "
                       "the typical architecture:\n\n**Frontend**") is not None)
check("preamble catches a based-on lead-in",
      metrics.preamble("Based on the architecture, here's how I'd approach "
                       "this:\n\n## Recommended") is not None)
# The lead-in openers are a whitelist because `since`/`given`/`without`
# introduce a stated limitation, which #179's criterion protects as never-cut
# content. Allowing any lead-in caught 16 of these and cost precision.
check("preamble ignores an announcement behind a stated limitation",
      metrics.preamble("Since there's no existing codebase here to anchor this "
                       "to, here's the general architecture:\n\n**Frontend**") is None)
check("preamble ignores a without-seeing limitation",
      metrics.preamble("Without seeing your code, here's how payment retry "
                       "logic typically works:\n\n**Core**") is None)

check("preamble is not fooled by a dot inside a backticked filename",
      metrics.preamble(
          "Here's the full flow in `auth.js` (41 lines, self-contained).") is None)
check("preamble ignores a direct answer",
      metrics.preamble("Three tests still fail, not zero.") is None)

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
