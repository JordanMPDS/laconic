"""The `closed_question_overlong` prototype, built for [#136] and not promoted.

[#136] reports an eight-word closed confirmation question - *"you mentioned Lift
is the wrong metric correct?"* - answered in about 400 words across three `##`
sections, and names the defect precisely: two rules in `rules/laconic.md` cover
it already, so this is an explicit rule failing to fire rather than a gap. Its
third proposal is the only one of three never attempted:

> **A detector, cheap and binary.** Flag any response over ~80 words to a prompt
> under ~15 words that ends in `correct?`, `right?`, `is that right?`, or
> `yes or no`. That is narrow enough not to fire on real questions and would
> have caught this turn.

**It reached 26.7% precision on 30 hand-read hits and is parked.** The reason is
structural rather than a threshold wanting tuning, and it is recorded in
`../closed-question-136.md`. Nothing here is imported by `evals/bench/metrics.py`
and nothing here has a `POLICY_RANK` entry, because a detector this imprecise
may not name a rule.

Two settings, because the issue's literal form and the form the suite can carry
are not the same predicate and the difference is a harness artifact:

- `literal` - the graded question ends in a closed marker and the prompt is at
  most 15 words, both as [#136] specifies. Every multi-turn prompt in
  `evals/cases/` ends with the appended instruction `Don't edit anything.`, so
  the marker is never the last thing in the file and the literal predicate fires
  on nothing at all until that instruction is removed. `HARNESS_TAIL` removes it,
  and the write-up says so rather than reporting a zero.
- `widened` - the word cap is dropped and replaced by the condition it proxies
  for: the prompt asks for no explanation. `quota-merge` is the case this adds,
  at 32 words, and its graded turn is as closed as the other twelve.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "bench"))
import metrics  # noqa: E402

TURN = "<!-- turn -->"

# The instruction run.py's cases append so that the diagnosis lands in the
# response rather than in a diff (evals/CRITERIA.md requires it). It is the
# harness talking, not the user, and leaving it in makes every closed question
# in the suite read as open.
#
# `\s+` between the words rather than a space: `confirm-rollback`'s prompt wraps
# as "Don't edit\nanything." and a literal space dropped that case out of the
# population silently, taking 370 of the archive's runs with it.
HARNESS_TAIL = re.compile(r"\s*Don'?t\s+edit\s+anything\.\s*$", re.I)

# The four surface forms [#136] names, plus `true?`, which is the same shape.
# Anchored to the end of the question because "right" and "correct" are ordinary
# words mid-sentence ("the right index", "correct the figure").
CLOSED_MARKER = re.compile(
    r"(?:,\s*)?(?:correct|right|true)\s*\?\s*$"
    r"|\bis that (?:right|correct)\s*\?\s*$"
    r"|\byes or no\s*\??\s*$",
    re.I,
)

# What the word cap proxies for. A prompt asking to be walked through something
# is asking for length, and `rules/laconic.md` protects it outright: "Anything
# the user asked to have explained".
EXPLANATION_ASK = re.compile(r"\b(why|explain|walk me through|how)\b", re.I)

# [#136]'s own numbers: a response over this many prose words, to a prompt under
# the cap. The allowance the rule states is "a word or a line", so this is about
# four times it - the headroom is what the issue buys precision with, and
# `../closed-question-136.md` reports the whole curve from 20 to 200 rather than
# resting on the choice.
LIMIT = 80
MAX_PROMPT_WORDS = 15


def graded_turn(prompt):
    """The last turn of a `prompt.md`, with the harness instruction removed.

    The graded turn is the one the trap reads and the only one a response in the
    archive answers, so it is the only one whose shape can license a length.
    """
    return HARNESS_TAIL.sub("", prompt.split(TURN)[-1].strip()).strip()


def closed_question(prompt, setting="widened"):
    """Is the graded turn a closed confirmation question?

    Prompt-side only, and this half is genuinely binary: a surface marker in a
    fixed position, no interpretation. It is the response half that is not, which
    is the finding in the write-up.
    """
    q = graded_turn(prompt)
    if not CLOSED_MARKER.search(q):
        return False
    if setting == "literal":
        return len(q.split()) <= MAX_PROMPT_WORDS
    return not EXPLANATION_ASK.search(q)


def prose_words(text):
    """`metrics.score`'s own word count: fenced blocks, inline code and URLs out.

    Deliberately not a private count. These answers carry SQL, and a word count
    that charged a response for a `CREATE INDEX` statement would be charging it
    for content the rule file protects verbatim.
    """
    return metrics.score(text)["words"]


def fires(text, prompt, limit=LIMIT, setting="widened"):
    return closed_question(prompt, setting) and prose_words(text) > limit


def demo():
    """The asserts that hold the two settings apart, and the harness artifact."""
    # The reported failure: a closed question, a long answer.
    assert fires("Yes. " + "word " * 400, "you mentioned Lift is the wrong metric correct?")
    # The answer the report says was correct.
    assert not fires("Yes, and the second metric is not a safe substitute either.",
                     "you mentioned Lift is the wrong metric correct?")

    # The harness artifact: byte-identical question, and the appended instruction
    # is the only difference. Without HARNESS_TAIL the literal predicate reads
    # every case in the suite as an open question.
    bare = "the config change was the cause, correct?"
    tailed = bare + " Don't edit anything."
    wrapped = bare + " Don't edit\nanything."
    assert closed_question(wrapped, "literal"), "the wrapped harness tail"
    assert closed_question(bare, "literal") and closed_question(tailed, "literal")
    assert CLOSED_MARKER.search(bare) and not CLOSED_MARKER.search(tailed)

    # Multi-turn: only the graded turn decides.
    five = "what is wrong here? Don't edit anything." + TURN + tailed
    assert closed_question(five)
    assert graded_turn(five) == bare

    # The cap is the only thing separating the settings on the real suite.
    quota = ("We agreed to replace the two rate-limit counters with one sliding "
             "window. So that means we drop `minute_counter` and `hour_counter` "
             "and the reconcile pass, and just key the window on account plus "
             "route — right?")
    assert closed_question(quota, "widened")
    assert not closed_question(quota, "literal")

    # An explanation ask is never this, whatever it ends with.
    assert not closed_question("walk me through the refresh flow - is that right?")
    # And an ordinary sentence carrying the word is not a marker.
    assert not closed_question("is the index on the right column? Don't edit anything.")

    # Code is not prose: the same answer with its SQL inline is under the limit.
    sql = "No. " + "word " * 70 + "```sql\n" + "SELECT 1; " * 80 + "\n```"
    assert prose_words(sql) < LIMIT
    print("detector.demo: ok")


if __name__ == "__main__":
    demo()
