#!/usr/bin/env python3
"""Deterministic response scoring. No I/O, no network, no dependencies.

Two axes are measured here. Compression comes from the CLI's own token counts
and never touches this module. Readability is measured with the heuristics
below, which are validated by tests/test_metrics.py - they are proxies for
degraded grammar, not a parser.

Every detector runs on code-stripped prose: `->` in Rust and `impl` in a
command are correct usage, and counting them would make the metric worthless.
"""
import re

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


def never_cut_missing(text, keywords):
    low = text.lower()
    return [k for k in keywords if k.lower() not in low]
