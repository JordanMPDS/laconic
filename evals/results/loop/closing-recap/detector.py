"""The `closing_recap` prototype, built for [#305] and not promoted.

[#305] reports a response whose final paragraph was 37 words re-asserting a
sentence 270 words above it, and names the gap in plain terms: *"There is no
rule against closing with a recap of your own opening."* Before writing that
rule the loop needs a way to count the shape, and this is the attempt.

**It reached 12% precision on 50 hand-read hits and is parked.** The reasons are
structural rather than a threshold that wants tuning, and they are recorded in
`../closing-recap-305.md`. Nothing here is imported by `evals/bench/metrics.py`
and nothing here has a `POLICY_RANK` entry, because a detector this imprecise
may not name a rule.

The parameters are the ones the sweep varied, kept as arguments so the table in
the write-up can be regenerated rather than quoted:

- `min_paras` - a response with fewer paragraphs has no middle to shrink, which
  is the mechanism [#305] describes.
- `min_words` - a one-line sign-off is not the reported harm.
- `max_share` - a recap is short relative to the body it recaps. [#305]'s was
  37 words after 270.
- `require_no_new_referents` - a paragraph that asserts a new claim usually
  names a new object. This was added to raise precision and lowers it; see the
  write-up.
- `overlap` - the fraction of the closing paragraph's content words that
  already appear in the opening paragraph.
"""
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "bench"))
import metrics  # noqa: E402

# Closed-class words carry no claim, so counting them as shared content would
# score every pair of English paragraphs as overlapping. Deliberately hand-held
# rather than derived from a frequency list: the repository ships no corpus and
# adding one is a dependency.
STOP = {
    "the", "a", "an", "and", "or", "but", "so", "if", "then", "that", "this",
    "these", "those", "is", "are", "was", "were", "be", "been", "being", "it",
    "its", "of", "to", "in", "on", "for", "with", "as", "at", "by", "from",
    "not", "no", "you", "your", "i", "we", "they", "he", "she", "do", "does",
    "did", "have", "has", "had", "will", "would", "can", "could", "should",
    "may", "might", "must", "there", "here", "what", "which", "who", "when",
    "where", "how", "why", "one", "two", "only", "just", "also", "than", "too",
    "very", "more", "most", "much", "any", "all", "both", "each", "other",
    "same", "such", "own", "up", "down", "out", "over", "into", "about",
    "after", "before", "while", "because", "since", "until", "again", "still",
    "now", "get", "gets", "make", "makes", "need", "needs",
}

# A referent is a thing the answer is about: a number, a backticked identifier,
# or a dotted / underscored / internally-capitalised symbol.
BACKTICK = re.compile(r"`([^`]+)`")
SYMBOL = re.compile(
    r"\b(?:[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|[a-z]+[A-Z][A-Za-z]*|[A-Za-z]+_[A-Za-z]+)\b")
NUMERIC = re.compile(r"\S*\d\S*")


def _words(para):
    return metrics.WORD.findall(metrics.INLINE.sub(" ", para))


def _content(para):
    return {w.lower() for w in _words(para)
            if w.lower() not in STOP and len(w) > 2}


def _referents(para):
    bare = metrics.INLINE.sub(" ", para)
    out = {m.group(1).strip().lower() for m in BACKTICK.finditer(para)}
    out |= {m.group(0).lower() for m in SYMBOL.finditer(bare)}
    out |= {t.lower() for t in NUMERIC.findall(bare)}
    return {o for o in out if o}


def closing_recap(text, overlap=0.25, min_words=15, max_share=0.25,
                  min_paras=3, require_no_new_referents=False):
    """The closing paragraph when it reads as a recap of the opening, else None.

    Returns the paragraph rather than a boolean so a caller can show what it
    caught, which is the same contract `metrics.closing_offers` uses and the
    reason the false-positive shapes below were findable at all.
    """
    _, src = metrics.split_text(text)
    paras = metrics._paragraph_prose(src)
    if len(paras) < min_paras:
        return None
    last, first = paras[-1], paras[0]
    last_n = len(_words(last))
    total_n = sum(len(_words(p)) for p in paras)
    if last_n < min_words or not total_n:
        return None
    if last_n / total_n > max_share:
        return None
    if require_no_new_referents:
        earlier = set()
        for p in paras[:-1]:
            earlier |= _referents(p)
        if _referents(last) - earlier:
            return None
    lc = _content(last)
    if not lc:
        return None
    if len(lc & _content(first)) / len(lc) < overlap:
        return None
    return last


def eligible(text, min_words=15, max_share=0.25, min_paras=3):
    """True when the response is structurally able to carry a closing recap.

    The denominator the write-up's rate table is computed over. Without it a
    near-zero rate is ambiguous between "the model does not do this" and "the
    benchmark never produces an answer long enough to do it in", and those call
    for different responses.
    """
    _, src = metrics.split_text(text)
    paras = metrics._paragraph_prose(src)
    if len(paras) < min_paras:
        return False
    last_n = len(_words(paras[-1]))
    total_n = sum(len(_words(p)) for p in paras)
    return bool(total_n) and last_n >= min_words and last_n / total_n <= max_share


def demo():
    """The smallest check that fails if the gating logic breaks."""
    recap = (
        "The migration is done. Every tier closed and the appendix is empty.\n\n"
        "The eight seeded values are waiting on the measurement pass, which is "
        "scheduled for next week and needs the new sampler.\n\n"
        "More middle text about the sampler and the schedule and the rest of "
        "it, at length, so that the body is long enough that the closing is a "
        "small share of it. More words again here.\n\n"
        "So the honest answer: the migration is done. The remaining gap "
        "between done and closed is the appendix, which is empty."
    )
    assert eligible(recap)
    assert closing_recap(recap, overlap=0.25) is not None
    # The threshold is load-bearing: a textbook recap scores 0.50, so the 0.65
    # a first draft would reach for rejects the thing it was built to catch.
    assert closing_recap(recap, overlap=0.65) is None

    two_paras = "The answer is yes.\n\nBecause the pool is leaking connections."
    assert not eligible(two_paras)
    assert closing_recap(two_paras) is None

    # A closing that names something new is not a recap, and the referent gate
    # is what is supposed to say so.
    novel = recap.rsplit("\n\n", 1)[0] + (
        "\n\nSo the honest answer: the migration is done, and `sampler.py` "
        "still owes us the 14 calibration values."
    )
    assert closing_recap(novel, overlap=0.25,
                         require_no_new_referents=True) is None
    print("closing_recap demo: ok")


if __name__ == "__main__":
    demo()
