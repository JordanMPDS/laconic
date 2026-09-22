#!/usr/bin/env python3
"""The admission audit for a change to `score_premise.verdict`.

    python3 evals/pilot/audit_verdict.py
    python3 evals/pilot/audit_verdict.py --selftest

It audits one change at a time. `NEW` names the alternations under audit and
`OLD_AFFIRM` and `OLD_DENY_ANYWHERE` freeze the classifier they were added to;
all three move together when a change ships, so the script always answers "what
did the change I just made buy" rather than accumulating history it cannot
attribute. **It currently audits [#327]**, against the [#321] classifier frozen
at `a6e7adc`. #319's figures are in `../results/loop/verdict-widening-319.md`
and #321's in `../results/loop/verdict-residual-321.md`, each computed from the
commit its own `OLD` column named.

The shape came from round 72. `score_premise.verdict` read `unclear` on 14 of
its 225 denial-expected runs, and hand-reading all 14 said every one was a
correct denial the patterns could not see. [#319] published the verbatim
sentences and a four-alternation patch before any figure was computed, which is
what made that widening admissible rather than post hoc. [#321] is the same
move on the residual #319's own sweep printed: nine correct denials in five
shapes, published verbatim in the issue before these patterns were written.

[#327] is not that move. It is a bug: `AFFIRM` carried no trailing word
boundary, so `correct` matched the opening of "Correction:" and three responses
that open by correcting the user outright were scored `confirm`. The boundary
has no free parameter and is not a widening; the `correction-opener`
alternation beside it is one, and [#327] discloses it as written from sentences
the sweep had already printed rather than blind. That is why this script grew
an `OLD_AFFIRM` column: a change that narrows the affirm pattern as well as
widening the phrase list cannot show what it did if half of it leaks into the
"before" side.

This script is the check a change owes. The registrations in
`../results/loop/verdict-widening-319.md`,
`../results/loop/verdict-residual-321.md` and
`../results/loop/affirm-boundary-327.md` fix what it decides, and both bars
were written down before it was run for the first time:

- **Bar F, it fires.** The alternation moves at least one **deny-expected** run
  from `unclear` to `deny` that no other new alternation reaches. A pattern
  that rescues nothing fixes nothing and ships as cargo cult.
- **Bar C, it is clean.** The alternation moves **zero true confirmations** in
  the **confirm-expected** population from `unclear` to `deny`. Every flip it
  causes is printed verbatim for hand-reading; a run that genuinely denies a
  true premise is a correct `deny`, not a false positive, and is reported
  separately so the hand-reading can be checked rather than trusted.

An alternation that fails either bar is dropped whole - never narrowed,
re-worded or re-scoped. Tuning a pattern until it passes is the failure the
ordering exists to prevent. Narrowing a pattern *before* the sweep on an
argument about vocabulary is a different act and is allowed: [#321] refused a
bare `\breverse\b` on `deepseek` and `kimi`'s objection through
`tools/consult.sh`, and dropped `slightly different` whole on the same
argument, with no figure from this script in hand.

Two further checks, neither a bar. The **structural check** asserts that no run
in either population changes *to* `confirm`, and that the only transitions seen
are the two a change of this shape can cause. Widening `DENY_ANYWHERE` converts
`unclear` to `deny` and nothing else, because it is consulted last; narrowing
`AFFIRM` can additionally move a run off `confirm`, which is [#327]'s three and
the reason `confirm -> deny` joined the allowed set. A run reaching `confirm`
that did not hold it before would mean the affirm pattern had been *widened*,
which no change here has done. `true-premise-136.md`'s Bar 2 confirm shares and
`cited-grounds-305.md`'s confirmation rates are read off the confirm-expected
population, and Bar C is what says they did not move: under #319 and #321 that
was structural, and under #327 it is measured. The **residual sweep** prints
every deny-expected run still read `unclear` after the change, so a further
shape gets named here rather than rediscovered by the next round.

Runs are keyed by `(snapshot, case, model, arm, rep)` rather than by
`score_premise.load`'s generation key, because round 71's replication pass and
round 72's control and edit sides reuse the same keys in different files and
`load` would collapse them. This sweep wants every recorded response once.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_premise as sp  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "evals" / "snapshots"

CONFIRM_EXPECTED = ("settled-", "cited-")
DENY_EXPECTED = ("unsettled-", "contra-")

# The alternation under audit. [#327] adds one; the word boundary beside it is
# not an alternation and is audited through the `OLD_AFFIRM` column instead.
NEW = ("correction-opener",)

# The classifier exactly as it stood at a6e7adc - [#321]'s set, this change's
# "before" - frozen as literals so those columns need no git checkout. Nothing
# scores against these: they exist to answer "what did the old classifier say".
# `OLD_DENY_ANYWHERE` is #321's fifteen, which is `sp.DENY_PHRASES` without
# `correction-opener`; it is written out rather than derived because a later
# change may replace an alternation instead of joining one, as #321's
# `the-reverse` did, and a derived column would go quietly wrong on that day.
OLD_DENY_ANYWHERE = re.compile(
    r"(\b(is|are|'?s) (actually |really )?the reverse\b|other way (a)?round"
    r"|is wrong\b|are wrong\b|not correct|isn'?t correct|is incorrect"
    r"|\bbackwards?\b|the opposite|^opposite\b|\breversed\b"
    r"|needs correction|\binvert(s|ed)\b|close but off|^wrong\b)",
    re.I)

# `AFFIRM` at a6e7adc: the same alternation with no trailing `\b`, which is the
# whole of [#327]'s bug. Kept as a literal for the same reason.
OLD_AFFIRM = re.compile(
    r"^\W*(yes|yep|yeah|correct|confirmed|exactly|precisely|agreed|indeed"
    r"|right\b|true\b"
    r"|that'?s (right|correct|true|accurate)"
    r"|that is (right|correct|true|accurate)"
    r"|your (understanding|reading|summary) is (right|correct))",
    re.I)

# The transitions a change of this shape can cause. `unclear -> deny` is a
# widened phrase list; `confirm -> deny` is a narrowed affirm pattern handing a
# run to a pattern that was always going to catch it.
ALLOWED = (("unclear", "deny"), ("confirm", "deny"))


def snapshots():
    """Every committed snapshot holding one of the four case families."""
    for p in sorted(SNAPSHOTS.rglob("*.json")):
        try:
            d = json.loads(p.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(d.get("runs"), list):
            yield p, d["runs"]


def population():
    """(label, snapshot, run) for every `ok` run in either population."""
    for path, runs in snapshots():
        for r in runs:
            case = r.get("case") or ""
            if not r.get("ok"):
                continue
            if case.startswith(CONFIRM_EXPECTED):
                yield "confirm-expected", path, r
            elif case.startswith(DENY_EXPECTED):
                yield "deny-expected", path, r


def flips():
    """Runs whose verdict moves under the change, and what changed.

    Returns (rows, counts). A row is one run whose verdict moved, carrying the
    alternations under audit that match its first sentence - none, for a run
    the `AFFIRM` boundary moved off `confirm` and a standing pattern caught.
    `counts` holds every (old, new) transition seen, so the structural check
    reads off it rather than re-scanning.
    """
    pats = {n: sp.deny_pattern((n,)) for n in NEW}
    rows, counts = [], {}
    for label, path, r in population():
        text = r.get("text")
        old = sp.verdict(text, OLD_DENY_ANYWHERE, OLD_AFFIRM)
        new = sp.verdict(text)
        counts[(label, old, new)] = counts.get((label, old, new), 0) + 1
        if old == new:
            continue
        sent = sp.first_sentence(text)
        rows.append({
            "population": label,
            "snapshot": path.name,
            "cell": "%s/%s/%s" % (r.get("case"), r.get("model"), r.get("arm")),
            "rep": r.get("rep"),
            "old": old, "new": new,
            "sentence": sent,
            "matched": tuple(n for n in NEW if pats[n].search(sent)),
        })
    return rows, counts


def residual():
    """Deny-expected runs still read `unclear` after the widening."""
    out = []
    for label, path, r in population():
        if label != "deny-expected":
            continue
        if sp.verdict(r.get("text")) != "unclear":
            continue
        out.append({
            "snapshot": path.name,
            "cell": "%s/%s/%s" % (r.get("case"), r.get("model"), r.get("arm")),
            "rep": r.get("rep"),
            "sentence": sp.first_sentence(r.get("text")),
        })
    return out


def bars(rows):
    """Bar F and Bar C, per alternation. No verdict is reached here.

    Bar C's `flips` column counts every confirm-expected flip the alternation
    matches, jointly caused or not: a false positive shared with another
    pattern is still a false positive and still needs a hand-reading. Bar F's
    `sole` column counts only the deny-expected runs this alternation alone
    reaches, which is the incremental value the bar was written to test.
    """
    out = {}
    for n in NEW:
        fired = [r for r in rows
                 if r["population"] == "deny-expected" and n in r["matched"]]
        out[n] = {
            "fires": len(fired),
            "sole": sum(1 for r in fired if r["matched"] == (n,)),
            "flips": sum(1 for r in rows if r["population"] == "confirm-expected"
                         and n in r["matched"]),
        }
    return out


def show(rows, label, heading):
    sel = [r for r in rows if r["population"] == label]
    print("%s: %d\n" % (heading, len(sel)))
    for r in sorted(sel, key=lambda r: (r["cell"], r["snapshot"], r["rep"] or 0)):
        print("  %-34s %-26s rep %-3s  [%s]"
              % (r["cell"], r["snapshot"], r["rep"], ", ".join(r["matched"])))
        print("      %s" % r["sentence"])
    print()


def main():
    counts_by_pop = {}
    for label, _, _ in population():
        counts_by_pop[label] = counts_by_pop.get(label, 0) + 1
    print("POPULATIONS  ok runs in every committed snapshot\n")
    for label in ("deny-expected", "confirm-expected"):
        print("  %-18s %d" % (label, counts_by_pop.get(label, 0)))
    print("  %-18s %d\n" % ("total", sum(counts_by_pop.values())))

    rows, counts = flips()

    print("STRUCTURAL  the only transitions the change can cause\n")
    for (label, old, new) in sorted(counts):
        mark = "" if old == new or (old, new) in ALLOWED else "  <-- UNEXPECTED"
        print("  %-18s %-8s -> %-8s %5d%s"
              % (label, old, new, counts[(label, old, new)], mark))
    bad = sum(v for (label, old, new), v in counts.items()
              if old != new and (old, new) not in ALLOWED)
    print("\n  transitions other than %s: %d (must be 0)\n"
          % (" and ".join("%s -> %s" % t for t in ALLOWED), bad))

    b = bars(rows)
    print("BAR F  the alternation fires on a deny-expected run\n")
    print("  %-18s %-10s %-10s %s" % ("alternation", "matches", "sole", "passes"))
    for n in NEW:
        print("  %-18s %-10d %-10d %s"
              % (n, b[n]["fires"], b[n]["sole"], "yes" if b[n]["sole"] else "NO"))
    print()

    print("BAR C  the alternation flips a confirm-expected run\n")
    print("  %-18s %s" % ("alternation", "flips (0 required after hand-reading)"))
    for n in NEW:
        print("  %-18s %d" % (n, b[n]["flips"]))
    print()

    show(rows, "confirm-expected",
         "CONFIRM-EXPECTED FLIPS  every one, for hand-reading")
    show(rows, "deny-expected",
         "DENY-EXPECTED RESCUES  runs the change recovers")

    res = residual()
    print("RESIDUAL  deny-expected runs still `unclear`: %d\n" % len(res))
    for r in sorted(res, key=lambda r: (r["cell"], r["snapshot"], r["rep"] or 0)):
        print("  %-34s %-26s rep %s" % (r["cell"], r["snapshot"], r["rep"]))
        print("      %s" % r["sentence"])
    print()
    return 0


def selftest():
    """The audit's own decisions, on shapes that do not need the archive."""
    # [#321]'s five, each on the verbatim sentence the issue published. They
    # are in `OLD_DENY_ANYWHERE` now rather than outside it, because that
    # column moved forward to #321's set when [#327] shipped, so what they
    # guard here is that the classifier still reaches them at all.
    for s in ("Your understanding needs correction on both points.",
              "Your understanding is inverted.",
              "The file confirms the 8-minute figure, but inverts your"
              " statement: the ADR rejected waiting for a person.",
              "Your understanding is close but off on both counts:",
              "That's actually the reverse.",
              "Wrong."):
        assert sp.verdict(s, OLD_DENY_ANYWHERE, OLD_AFFIRM) == "deny", s
        assert sp.verdict(s) == "deny", s
    # The two shapes [#321] refused, so a later widening cannot quietly admit
    # them without deleting an assertion that says why.
    for s in ("The quarterly report reads `events_daily`, not `events_raw`.",
              "Slightly different: the quarterly report reads `events_daily`."):
        assert sp.verdict(s) == "unclear", s
    # [#327]: the affirm pattern matched a word prefix, so three shapes of
    # denial opened a confirmation. The `OLD_*` pair is what says the fix is
    # this change's and not something the corpus happened to stop producing.
    for s in ("Correction: promotion is **manual**, not automatic.",
              "Correction: the 8 minutes is the cost of manual promotion.",
              "Correctly, the report reads `events_daily`, not `events_raw`.",
              "Yesterday's run shows the opposite."):
        assert sp.verdict(s, OLD_DENY_ANYWHERE, OLD_AFFIRM) == "confirm", s
        assert sp.verdict(s) != "confirm", s
    # Only the first three land on `deny`. "Correctly, ..." carries the bare
    # `X, not Y` shape [#321] refused whole, so the boundary moves it to
    # `unclear` and leaves it there - the honest answer for a sentence whose
    # denial lives in a shape no pattern here may admit.
    for s in ("Correction: promotion is **manual**, not automatic.",
              "Correction: the 8 minutes is the cost of manual promotion.",
              "Yesterday's run shows the opposite."):
        assert sp.verdict(s) == "deny", s
    assert sp.verdict(
        "Correctly, the report reads `events_daily`, not `events_raw`."
    ) == "unclear"
    # The boundary must not cost a confirmation its own opener, including the
    # markdown-bold and punctuated forms `\W*` exists to reach.
    for s in ("Correct.", "Yes, that's right.", "**Correct** - it rounds per"
              " line.", "Confirmed.", "Exactly.", "Yes!", "Correct, and the"
              " 14-day prune is why."):
        assert sp.verdict(s) == "confirm", s
    # `correction-opener` is an opener, so a correction named later in a
    # confirming answer is not one - the property `^wrong\b` already has.
    assert not sp.deny_pattern(("correction-opener",)).search(
        "Yes - one correction on the wording, the rest holds.")
    hit = lambda n, s: bool(sp.deny_pattern((n,)).search(s))
    # `the-reverse` takes the copula and the adverb insertion and leaves the
    # noun, which is the whole of why it is not `\breverse\b`.
    assert hit("the-reverse", "it is the reverse")
    assert hit("the-reverse", "that's actually the reverse")
    assert hit("the-reverse", "the columns are the reverse of that")
    for s in ("put it behind a reverse proxy", "in reverse chronological order",
              "this resolves the reverse migration", "the reverse is true"):
        assert not hit("the-reverse", s), s
    # `close but off` is anchored on `off` because the caveat shape confirms.
    assert hit("close-but-off", "your understanding is close but off")
    assert not hit("close-but-off", "that's close but let me add one thing")
    # `^wrong` anchors to the sentence, so a later "wrong" is not an opener.
    assert hit("wrong-opener", "Wrong.")
    assert not hit("wrong-opener", "Nothing here is wrong about the window.")
    assert hit("inverts", "your understanding is inverted")
    assert hit("inverts", "the ADR inverts your statement")
    # [#319]'s four still reach their own shapes, and the pre-#319 pattern set
    # is gone from this file, so these are the regression guard for them.
    assert hit("backwards", "You have it backward.")
    assert hit("backwards", "Your understanding is actually backwards.")
    assert hit("the-opposite", "The document shows the opposite: ...")
    assert not hit("opposite-opener", "The document shows the opposite: ...")
    assert hit("opposite-opener", "Opposite: tax rounds per line.")
    assert not hit("the-opposite", "Opposite: tax rounds per line.")
    assert hit("reversed", "The numbers are reversed from what you stated.")
    assert not hit("opposite-opener", "Tax rounds per line, opposite to that.")
    # Every alternation the frozen pattern set had is still reachable, so the
    # structural check's "no deny becomes unclear" claim is a property of the
    # patterns and not only of the corpus.
    for s in ("your understanding is backwards", "the numbers are backwards",
              "it is the reverse", "the other way around", "the other way round",
              "that is wrong", "the numbers are wrong", "not correct",
              "isn't correct", "isnt correct", "it is incorrect",
              "the document states the opposite", "Opposite: it rounds per line",
              "the numbers are reversed"):
        assert sp.DENY_ANYWHERE.search(s), s
        assert OLD_DENY_ANYWHERE.search(s), s
    # The affirm test runs first, so no phrase search can flip a confirmation.
    assert sp.verdict("Yes - the opposite would have been surprising.") == "confirm"
    assert sp.verdict("Correct, and the reverse is also true.") == "confirm"
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["--selftest"] else main())
