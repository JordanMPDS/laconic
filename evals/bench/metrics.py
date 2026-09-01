#!/usr/bin/env python3
"""Deterministic response scoring. No I/O, no network, no dependencies.

Two axes are measured here. Compression comes from the CLI's own token counts
and never touches this module. Readability is measured with the heuristics
below, which are validated by tests/test_metrics.py - they are proxies for
degraded grammar, not a parser.

Every detector runs on code-stripped prose: `->` in Rust and `impl` in a
command are correct usage, and counting them would make the metric worthless.
"""
import math
import re
import statistics

# Surrounding whitespace/newlines are swallowed along with the fence itself
# (not just the ```...``` span) so the removal doesn't leave a lone
# whitespace-only line behind. _paragraph_prose reads a whitespace-only line
# as a paragraph break, which turns the grammatical continuation after a
# fenced code block into a false new "sentence" (see _lowercase_starts).
# Collapsing the surrounding blank lines merges the prose back into one
# paragraph, matching how the fence reads to a person: interruption, not break.
FENCE = re.compile(r"\s*```.*?```\s*", re.S)
INLINE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
ARTICLES = {"the", "a", "an"}
AUX = {
    "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "doesn't", "isn't", "aren't", "wasn't", "weren't", "can't", "couldn't",
    "shouldn't", "won't", "wouldn't", "hasn't", "haven't", "hadn't", "didn't",
}

SYMBOLS = re.compile(r"(->|=>|→)")
# Deliberately tight. config, repo, auth, env and db are normal developer
# English; including them would fire on correct prose in every arm.
ABBREV = re.compile(
    r"\b(impl|req|resp|func|val|obj|arg|msg|err)\b|\bw/|\bb/c\b", re.I
)
# Mask only abbreviations that never end sentences. e.g., i.e., vs., etc. mid-sentence
# should not be treated as sentence boundaries. Deliberately excludes etc, al, Inc, Ltd,
# St, Ave because these commonly *do* end sentences, and masking them would hide real
# lowercase-start violations. This list must stay small; adding "helpful" abbreviations
# costs recall without gaining precision on the false-positive side.
ABBREV_DOT = re.compile(r"\b(e\.g|i\.e|cf|vs|approx|Fig|Dr|Mr|Mrs|Ms|Prof)\.", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# A sentence legitimately opening with a bare filename or dotted identifier
# ("auth.js is self-contained", "pool.max controls...") is correct usage, not
# a broken sentence start. _lowercase_starts already skips a sentence opening
# with a backtick-wrapped identifier; this catches the same thing bare.
DOTTED_IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
# Lines that are structural markdown, not paragraph flow. Bullets legitimately
# start lowercase, so checking them would fire on correct writing.
# -, *, +, # and an ordered-list digit only count as structural when followed
# by whitespace (a real marker: "- item", "* item", "1. item") - without that
# requirement "**Request A**: ..." (a bolded prose paragraph) and "-> ..." (an
# arrow, or an arrow left behind when an inline-code span is stripped to a
# leading space) both matched as bullets, hiding whatever followed on the line
# from every other detector. > and | still need no trailing whitespace
# (blockquotes and table rows are structural either way).
STRUCTURAL = re.compile(r"^\s*([-*+#]\s|[>|]|\d+[.)]\s)")


def _paragraph_prose(sentences_src):
    """Structural lines dropped; hard-wrapped lines rejoined into paragraphs.

    Iterating raw lines would flag the continuation of every wrapped sentence
    as a lowercase start. Verified: that bug fired twice on the known-good
    fixture before this was paragraph-aware.
    """
    paras, cur = [], []
    for line in sentences_src.splitlines():
        if not line.strip() or STRUCTURAL.match(line):
            if cur:
                paras.append(" ".join(cur))
                cur = []
            continue
        cur.append(line.strip())
    if cur:
        paras.append(" ".join(cur))
    return paras


def split_text(text):
    """Return (prose, sentences_src).

    prose: fenced blocks, inline code and URLs removed - for word and rate
    counts. sentences_src: fenced blocks removed but inline code kept, so a
    sentence opening with a code span is still recognizable as such.
    """
    no_fence = FENCE.sub(" ", text)
    sentences_src = URL.sub(" ", no_fence)
    prose = URL.sub(" ", INLINE.sub(" ", no_fence))
    return prose, sentences_src


def _lowercase_starts(sentences_src):
    hits = []
    for para in _paragraph_prose(sentences_src):
        # Mask abbreviation periods to prevent false-positive sentence boundaries
        masked = ABBREV_DOT.sub(lambda m: m.group(0).replace(".", "\x00"), para)
        for sentence in SENTENCE_SPLIT.split(masked):
            # Restore masked periods
            s = sentence.replace("\x00", ".").strip()
            if not s or s.startswith("`") or DOTTED_IDENTIFIER.match(s):
                continue
            if s[0].islower():
                hits.append(s[:40])
    return hits


def _is_numeric_progression(line, start, end):
    """True when the arrow at line[start:end] has a digit on both sides once
    surrounding whitespace/punctuation is trimmed, e.g. '7 -> 11'. That is a
    quoted progression, not a conjunction standing in for a word."""
    before = line[:start].rstrip()
    after = line[end:].lstrip()
    return bool(before) and before[-1].isdigit() and bool(after) and after[0].isdigit()


def _symbol_hits(prose):
    """Arrows counted wherever they stand in for a word, structure included.

    This deliberately does *not* skip STRUCTURAL lines, though _lowercase_starts
    does. The two detectors need opposite things from a bullet: a bullet may
    legitimately start lowercase, so checking its capitalization would fire on
    correct writing, but rules/laconic.md forbids arrows "after a bold label",
    "in a 'quick runbook' line" and "inside a quoted flow" - a bulleted or
    numbered runbook is the single most common place the forbidden arrow
    appears, not an exemption from the rule.

    Skipping them cost the loop a round. Round 01's edit scored 7 -> 0 on this
    metric while the model went on writing the same chains one list marker to
    the left, where the old detector could not see them; counted honestly the
    same two rounds read 26 -> 9 (evals/results/loop/round-01.md).

    A numeric progression like '7 -> 11 -> 14' is still exempt: that is a quoted
    progression, not a conjunction. Matched per line rather than on the whole
    text so an unrelated digit and arrow on different lines never look adjacent.
    """
    hits = []
    for line in prose.splitlines():
        hits.extend(m.group(0) for m in _line_arrow_hits(line))
    return hits


def _line_arrow_hits(line):
    """The counted arrows on one line. The single place the skip lives, so
    _symbol_hits and arrow_forms can never disagree about what an arrow is.
    """
    return [m for m in SYMBOLS.finditer(line)
            if not _is_numeric_progression(line, m.start(), m.end())]


def arrow_forms(text):
    """The same arrows _symbol_hits counts, split by the shape they take.

    Two or more on a line is a chain - "a -> b -> c", the sequencing
    rules/laconic.md spends most of its arrow paragraph on. One is a mapping -
    "Database query -> Redis", which the rule names in a single clause of six.

    They are worth separating because they do not move together, and
    violations_total sums them. Across the three edits measured on the 22-case
    set, every one lowered chains and raised mappings:

        form        baseline  r16  r17  r18
        chains            96   61   49   56
        two-term maps     44   56   61   55
        total            140  117  110  111

    Each of those rounds reported a headline that fell about 20% over components
    moving in opposite directions, and none could see it while running. That is
    the same failure #88 found in quality_fails, in a second metric.

    Disclosure only. Nothing here is summed into violations_total, no gate reads
    it, and the detector's own verdict about what counts as an arrow is
    unchanged - chain + mapping always equals symbol_connectors (#34).
    """
    prose, _ = split_text(text)
    out = {"chain": 0, "mapping": 0}
    for line in prose.splitlines():
        n = len(_line_arrow_hits(line))
        if n:
            out["chain" if n >= 2 else "mapping"] += n
    return out


BOLD_LABEL = re.compile(r"\*\*[^*\n]+\*\*")


def structure_markers(prose):
    """How much scaffolding one response carries: bullets, numbered steps and
    bold labels.

    Issue #20 asked whether arrows track the level or the shape of the answer.
    These three are the positions rules/laconic.md names when it forbids an
    arrow "after a bold label", in a "quick runbook" line, or "inside a quoted
    flow", so counting them gives the denominator that question needs. Counted
    on code-stripped prose like every other detector, so a bold label inside a
    fenced block is not scaffolding.
    """
    bullets = numbered = labels = 0
    for line in prose.splitlines():
        if re.match(r"^\s*[-*+]\s", line):
            bullets += 1
        if re.match(r"^\s*\d+[.)]\s", line):
            numbered += 1
        labels += len(BOLD_LABEL.findall(line))
    return {"bullets": bullets, "numbered": numbered, "bold_labels": labels,
            "total": bullets + numbered + labels}


def score(text):
    prose, sentences_src = split_text(text)
    words = WORD.findall(prose)
    total = len(words)
    lowered = [w.lower() for w in words]

    symbols = _symbol_hits(prose)
    abbrevs = [m.group(0) for m in ABBREV.finditer(prose)]
    lows = _lowercase_starts(sentences_src)

    spans = symbols + abbrevs + lows
    return {
        "words": total,
        "article_rate": (sum(1 for w in lowered if w in ARTICLES) / total) if total else 0.0,
        "aux_verb_rate": (sum(1 for w in lowered if w in AUX) / total) if total else 0.0,
        "symbol_connectors": len(symbols),
        "abbreviated_prose": len(abbrevs),
        "sentence_initial_lowercase": len(lows),
        "violations": len(symbols) + len(abbrevs) + len(lows),
        "spans": spans,
    }



def median(xs, default=0):
    """Median, or `default` for an empty sequence.

    Lived in both levels.py and report.py as a byte-identical `_median`. Two
    copies of a two-line function is two places to keep a default in sync.
    """
    return statistics.median(xs) if xs else default


def sign_test(k, n):
    """Two-sided exact binomial p for k successes in n at p=0.5.

    The per-case directions are what decide whether a level boundary does
    anything, and 11 of 22 has to be reported as the coin flip it is rather
    than as a direction. Exact rather than normal-approximated: n is 22.

    Lives here rather than in levels.py because report.py needs only this from
    that module, and importing a 324-line standalone CLI tool for one function
    is a dependency the report does not otherwise have.
    """
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1))
    return min(1.0, 2 * tail / 2 ** n)

CLOSING_OFFER = re.compile(
    r"(let me know if"
    r"|want me to\b"
    r"|would you like (to|me)\b"
    r"|shall i (write|add|create|run|do)"
    r"|should i (look|check|review|dig|go)\b"
    r"|hope (this|that) helps"
    r"|happy to (write|add|help|do|run)"
    r"|i can (write|add|draft|put together) .{0,40}\bif you"
    r"|i can (help|walk you through|look at|review|wire|sketch|show you)\b"
    r"|i could (write|add|sketch|draft|implement|wire)\b"
    r"|just say the word"
    r"|if you'?d like,? i)",
    re.I,
)


def closing_offers(text):
    """Offers to do more work, which `lite` prohibits and `full` inherits.

    [#113] is the reason this exists. It reports a `lite` rule breaking on one
    turn and holding on the next, same level, same session, adjacent turns, and
    argues that this is worth more as evidence than as harm: word count is a
    judgement call two readers can disagree about, while "did the answer offer
    to do more work" is binary and needs no interpretation. If ceremony and
    length decay together, the cheap signal measures the expensive one.

    The pattern is deliberately narrow, and the first draft was not. A loose
    version keyed on `i can`, `should i` and `if you want` scored 13 hits across
    the 210 turn-responses of round 35 and **every one was a false positive** -
    either a limitation ("the doc doesn't give order counts, so I can't
    quantify impact") or a request for information needed to answer at all
    ("point me at the `chargeOrder()` source"). Both are never-cut content. The
    rules also carve out confirmation explicitly: "Asking the user to confirm a
    destructive action is never a closing offer; offering to go read something
    for them is."

    Precision was measured before the rate was used, on the standard [#155]
    set: 30 hits drawn at random from the archive, hand-read, **30 of 30
    genuine** offers to do more work. That is the bar [#155]'s restatement
    metric could not clear at 55.3%, and it is why this one is a usable metric
    and that one is parked.

    Recall was then measured, and the first pattern's was not good enough. 40
    responses the detector scored negative were drawn at random from
    `round-21.json` and hand-read: **3 were genuine offers it had missed** -
    "should I look at the actual codebase", "I can help wire up the `kid`-based
    verification directly", "would you like to dig into any of these
    approaches?". All three are offers to do work rather than questions asking
    for information, which is the line this pattern draws.

    The three shapes were added, and every one of the 22 responses that widening
    newly catches was hand-read: 21 are unambiguous and one is borderline ("what
    aspect would you like to change?"), so precision holds. On the same 40-response
    sample the widened pattern misses none.

    **The widening did not move the arm ordering, and it widened the gap**:
    baseline 21.4% to 25.9% against laconic 5.5% to 5.9%, because the misses were
    baseline-skewed (10 added against 1). So the recall limitation understated the
    difference between the arms rather than threatening it.

    Recall is still estimated from 40 responses and is not established precisely.
    The rates remain floors.

    Returns the matched strings, so a caller can count them or show them.
    """
    return [m.group(0) for m in CLOSING_OFFER.finditer(text)]


_BACKTICKED = re.compile(r"`[^`]*`")

PREAMBLE = re.compile(
    r"^\s*(?:\*\*)?("
    r"here'?s (?:the|what|what's|how|a|my|an)[^.\n(\u2014\u2013,;:]{0,55}[:.](?=\s|$)"
    r"|here is (?:the|what|how|a|my|an)[^.\n(\u2014\u2013,;:]{0,55}[:.](?=\s|$)"
    r"|let me (?:walk|break|start|look|check|read|go|explain|take|dig)"
    r"[^.\n(\u2014\u2013,;:]{0,55}[:.](?=\s|$)"
    r"|i'?ll (?:walk|break|start|look|check|read|go through|explain)"
    r"[^.\n(\u2014\u2013,;:]{0,55}[:.](?=\s|$)"
    r"|i'?m going to[^.\n(\u2014\u2013,;:]{0,55}[:.](?=\s|$)"
    r"|(?:sure|great question|absolutely|certainly|of course)[,!.](?=\s|$)"
    r")",
    re.I,
)


def preamble(text, window=160):
    """A pure announcement opening, which `lite` prohibits.

    The rule: "No preamble. Do not restate the question, announce what is about
    to happen, or narrate tool calls the user can already see."

    **The unit is one complete sentence, and a sentence that both announces and
    asserts is not preamble**, because deleting it loses a claim. That rule is
    imported from `deletability.md`, where it was the one part of [#155]'s
    direction B that worked. It does most of the work here:

        Here's the full flow in `auth.js` (41 lines total, no other files
        reference it - this module is self-contained).

    asserts scope and is not preamble, while

        Here's the complete token refresh flow:

    asserts nothing and is. A first pattern that keyed on any `Here's ...`
    opening scored about 60-65% precision against the criterion, which is
    [#155]'s parked territory and the same failure mode - the mixed sentence.
    Requiring a *pure* announcement, with no parenthetical, em-dash aside,
    relative clause or trailing assertion, reads 18 of 18 on a fresh draw.

    Backticked spans are blanked before matching. Without that the terminator
    matches the dot inside a filename, and ``Here's the full flow in `auth.js`
    (41 lines...`` fires despite the parenthetical it was meant to exclude.

    **The archive cannot score arms with this**, and that is a property of the
    corpus rather than the detector: preamble is near zero everywhere except
    `walkthrough`, and the deduplicated baseline arm holds ten responses there.
    See [`preamble.md`](../results/loop/preamble.md) - the whole-archive gap is
    mix-shift, and the one matched comparison is p = 0.0508 on n = 10.

    Returns the matched opening, or None.
    """
    head = " ".join((text or "").strip().split())[:window]
    head = _BACKTICKED.sub(lambda m: "X" * len(m.group(0)), head)
    m = PREAMBLE.search(head)
    return m.group(0) if m else None


def never_cut_missing(text, keywords):
    low = text.lower()
    return [k for k in keywords if k.lower() not in low]
