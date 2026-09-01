r"""Candidate hands-back detector `v3`, frozen before its validation sample.

v2 is `evals/results/loop/unread-asks/detector_v2.py`: a question anywhere in
the closing two paragraphs, minus first-person offers, falling back to v1's
line-terminal match. Measured out of sample on 80 responses it reads 73.7%
precision and 87.5% recall (`unread-asks-v2/`), and [#153] records the two error
shapes it leaves.

Both shapes are structural, and reading v2's seven errors on batch 2 shows the
same structure from either side:

  - All five false positives carry a question EARLIER in the closing two
    paragraphs and then resolve it, ending on enumeration or a recommendation:
    "Left out: EXIF orientation/GPS stripping, ...", "I'd ship the Postgres
    version first and only reach for Meilisearch if ... demands it."
  - Both false negatives put the hand-back in the FINAL sentence, with no
    question mark: "Which database are you on, and roughly how many products -
    that decides which of the two to actually spec out."

So v3 narrows position and widens form. It looks only at the tail of the final
paragraph, where a genuine hand-back sits, and it fires on interrogative
*content* rather than on punctuation alone.

That is a hypothesis about structure, not a fit to seven strings. It is written
here and committed BEFORE the third sample is drawn or labelled, so the
out-of-sample figure is measured against a detector that could not have been
adjusted to suit it. Do not edit it to improve a result; write a v4.

[#153]: https://github.com/JordanMPDS/laconic/issues/153
"""
import re

# First-person offers to do more work. Carried from v2 unchanged: these are the
# opposite of handing a decision back, and the first validation showed every one
# of v1's false positives was this shape.
OFFER = re.compile(r"\b(want me to|shall i|should i (sketch|write|draft|map)|"
                   r"would you like me to|do you want me to)\b", re.I)

# An interrogative aimed at the reader's own situation, whether or not it is
# punctuated as a question. This is the false-negative half: "Which database are
# you on, and roughly how many products - that decides which of the two to
# actually spec out." is a hand-back written with a full stop.
READER_INTERROGATIVE = re.compile(
    r"\b("
    r"(which|what|whose|how many|how much|how big|where)\b[^.?!]{0,60}\b"
    r"(are|is|do|does|did|have|has)?\s*you(r|'re)?\b"
    r"|what('s| is| are)\s+(your|the current)\b"
    r"|tell me\s+(your|which|what|how)\b"
    r")", re.I)

# A stated dependence on something only the reader knows. The second
# false-negative shape: no question at all, just a fork whose resolution is
# declared to be the reader's.
DEFERS_TO_READER = re.compile(
    r"\b("
    r"that('s| is) the deciding factor"
    r"|that decides which"
    r"|depends on (your|which|whether|what)"
    r"|without knowing (your|which|what)"
    r"|(i|we) can'?t (resolve|tell|say|pin)[^.?!]{0,40}\bwithout\b"
    r"|you'?ll need to (decide|pick|choose|tell)"
    r")", re.I)


def _sentences(paragraph):
    """Rough sentence split. Good enough: only the last two are read."""
    parts = re.split(r"(?<=[.?!])\s+", paragraph.strip())
    return [p for p in parts if p.strip()]


def asks_back(text):
    """True when the answer hands a decision back to the user.

    Scoped to the last two sentences of the final paragraph, because that is
    where v2's seven errors say a real hand-back lives and where its false
    positives' resolved questions do not.
    """
    paras = [p for p in text.strip().split("\n\n") if p.strip()]
    if not paras:
        return False
    tail = " ".join(_sentences(paras[-1])[-2:])
    if not tail:
        return False
    if OFFER.search(tail):
        return False
    if "?" in tail:
        return True
    return bool(READER_INTERROGATIVE.search(tail)
                or DEFERS_TO_READER.search(tail))
