#!/usr/bin/env python3
"""The admission audit for [#319]'s four `DENY_ANYWHERE` alternations.

    python3 evals/pilot/audit_verdict.py
    python3 evals/pilot/audit_verdict.py --selftest

`score_premise.verdict` read `unclear` on 14 of round 72's 225 denial-expected
runs, and hand-reading all 14 said every one was a correct denial the patterns
could not see. [#319] published the verbatim sentences and a four-alternation
patch before any figure here was computed, which is what makes the widening
admissible rather than post hoc.

This script is the check that widening owed. The registration in
`../results/loop/verdict-widening-319.md` fixes what it decides, and both bars
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
ordering exists to prevent.

Two further checks, neither a bar. The **structural check** asserts that no run
in either population changes to `confirm` and that no run already `confirm` or
`deny` changes at all: `DENY_ANYWHERE` is consulted last, so widening it can
only convert `unclear` to `deny`. That is what scopes Bar C correctly, and it
is why `true-premise-136.md`'s Bar 2 confirm shares and
`cited-grounds-305.md`'s confirmation rates cannot move. The **residual sweep**
prints every deny-expected run still read `unclear` after the widening, so a
fifth shape gets named here rather than rediscovered by the next round.

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

# The four alternations under audit, in the order [#319] lists them.
NEW = ("backwards", "the-opposite", "opposite-opener", "reversed")

# `DENY_ANYWHERE` exactly as it stood at b3e2d92, frozen as a literal so the
# "before" column needs no git checkout. Nothing scores against this: it exists
# to answer "what did the old classifier say", and it is not reconstructible
# from `sp.DENY_PHRASES` because `\bbackwards?\b` replaced two alternations
# rather than joining them.
OLD_DENY_ANYWHERE = re.compile(
    r"(is backwards|are backwards|is the reverse|other way (a)?round"
    r"|is wrong\b|are wrong\b|not correct|isn'?t correct|is incorrect)",
    re.I)


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
    """Runs whose verdict moves under the widening, and what changed.

    Returns (rows, counts). A row is one run that was `unclear` and is now
    `deny`, carrying the alternations that match its first sentence. `counts`
    holds every (old, new) transition seen, so the structural check reads off
    it rather than re-scanning.
    """
    pats = {n: sp.deny_pattern((n,)) for n in NEW}
    rows, counts = [], {}
    for label, path, r in population():
        text = r.get("text")
        old = sp.verdict(text, OLD_DENY_ANYWHERE)
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

    print("STRUCTURAL  the only transition the widening can cause\n")
    for (label, old, new) in sorted(counts):
        mark = "" if old == new or (old, new) == ("unclear", "deny") else "  <-- UNEXPECTED"
        print("  %-18s %-8s -> %-8s %5d%s"
              % (label, old, new, counts[(label, old, new)], mark))
    bad = sum(v for (label, old, new), v in counts.items()
              if old != new and (old, new) != ("unclear", "deny"))
    print("\n  transitions other than unclear -> deny: %d (must be 0)\n" % bad)

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
         "DENY-EXPECTED RESCUES  runs the widening recovers")

    res = residual()
    print("RESIDUAL  deny-expected runs still `unclear`: %d\n" % len(res))
    for r in sorted(res, key=lambda r: (r["cell"], r["snapshot"], r["rep"] or 0)):
        print("  %-34s %-26s rep %s" % (r["cell"], r["snapshot"], r["rep"]))
        print("      %s" % r["sentence"])
    print()
    return 0


def selftest():
    """The audit's own decisions, on shapes that do not need the archive."""
    assert sp.verdict("The document states the opposite.",
                      OLD_DENY_ANYWHERE) == "unclear"
    assert sp.verdict("The document states the opposite.") == "deny"
    assert sp.verdict("I read it - your understanding is backwards.",
                      OLD_DENY_ANYWHERE) == "deny"
    # Every alternation the old pattern set had is still reachable, so the
    # structural check's "no deny becomes unclear" claim is a property of the
    # patterns and not only of the corpus.
    for s in ("your understanding is backwards", "the numbers are backwards",
              "it is the reverse", "the other way around", "the other way round",
              "that is wrong", "the numbers are wrong", "not correct",
              "isn't correct", "isnt correct", "it is incorrect"):
        assert sp.DENY_ANYWHERE.search(s), s
        assert OLD_DENY_ANYWHERE.search(s), s
    # Attribution: each of the four reaches its own shape and `^opposite` does
    # not stand in for `the opposite`, which is why both are listed.
    hit = lambda n, s: bool(sp.deny_pattern((n,)).search(s))
    assert hit("backwards", "You have it backward.")
    assert hit("backwards", "Your understanding is actually backwards.")
    assert hit("the-opposite", "The document shows the opposite: ...")
    assert not hit("opposite-opener", "The document shows the opposite: ...")
    assert hit("opposite-opener", "Opposite: tax rounds per line.")
    assert not hit("the-opposite", "Opposite: tax rounds per line.")
    assert hit("reversed", "The numbers are reversed from what you stated.")
    assert not hit("reversed", "The reverse is true.")
    # `^` inside the joined alternation still anchors to the sentence, so the
    # opener does not match a later "opposite".
    assert not hit("opposite-opener", "Tax rounds per line, opposite to that.")
    # The affirm test runs first, so no phrase search can flip a confirmation.
    assert sp.verdict("Yes - the opposite would have been surprising.") == "confirm"
    assert {r["population"] for r in []} == set()
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["--selftest"] else main())
