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

FENCE = re.compile(r"```.*?```", re.S)
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
ABBREV_DOT = re.compile(r"\b(e\.g|i\.e|etc|vs|cf|al|Dr|Mr|Mrs|Ms|Prof|Inc|Ltd|Fig|approx|Ave|St)\.", re.I)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# Lines that are structural markdown, not paragraph flow. Bullets legitimately
# start lowercase, so checking them would fire on correct writing.
STRUCTURAL = re.compile(r"^\s*([-*+>|#]|\d+[.)])")


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
            if not s or s.startswith("`"):
                continue
            if s[0].islower():
                hits.append(s[:40])
    return hits


def score(text):
    prose, sentences_src = split_text(text)
    words = WORD.findall(prose)
    total = len(words)
    lowered = [w.lower() for w in words]

    symbols = SYMBOLS.findall(prose)
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
