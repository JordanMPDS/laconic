r"""Candidate hands-back detector `v2`, frozen before its validation sample.

v1 is `report.ASKS_BACK`, `^[^\n]*\?\s*$` — any line that is a whole question.
The first blind validation (60 responses, labels.json) measured it at 80%
precision and 80% recall, with both error classes systematic:

  - every false positive was a closing offer ("Want me to sketch the schema?"),
    which is the opposite of handing a decision back;
  - every false negative was a line-position artifact — the hand-back ended
    with a period, or carried its question mark mid-line.

v2 addresses exactly those two classes and nothing else. It scored 93.1/90.0 on
those same 60, which is in-sample and therefore not an estimate: it was designed
after seeing which responses v1 got wrong.

This file is committed BEFORE the fresh sample is drawn or labelled, so the
out-of-sample figure is measured against a detector that could not have been
adjusted to suit it. Do not edit it to improve a result; write a v3.
"""
import re

# First-person offers to do more work. These are not hand-backs: the answer
# resolved the question and then volunteered further effort.
OFFER = re.compile(r"\b(want me to|shall i|should i (sketch|write|draft|map)|"
                   r"would you like me to|do you want me to)\b", re.I)

# v1, for the fallback below.
LINE_QUESTION = re.compile(r"^[^\n]*\?\s*$", re.M)


def asks_back(text):
    """True when the answer hands a decision back to the user.

    A question anywhere in the closing two paragraphs, minus offers; falling
    back to v1's line-terminal match (also minus offers) for answers whose
    hand-back sits earlier in the response.
    """
    paras = [p for p in text.strip().split("\n\n") if p.strip()]
    for para in paras[-2:]:
        if "?" in para and not OFFER.search(para):
            return True
    return bool(LINE_QUESTION.search(text)) and not OFFER.search(text)
