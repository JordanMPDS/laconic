#!/usr/bin/env python3
"""The true-premise instrument for [#136] and [#305].

    python3 evals/pilot/score_premise.py <snapshot>...
    python3 evals/pilot/score_premise.py --selftest

Every closed question in the scored suite carries a false or partial premise,
so a complete answer is a denial plus the correction the premise forces - 80 to
145 words with nothing in them a reader could call surplus. That is what
`closed-question-136.md` found, and it is why no count endpoint on those cases
can convict one response: precision is decided by the redundancy judgement
[#155] parked at 55.3%.

`settled-*` removes the forcing function. The premise is true, so a bare
confirmation is the complete answer and every word after it is surplus by
construction rather than by judgement. `unsettled-*` is the same question over
the same decision record with the premise made false, generated in the same
pass, so the premise contrast is measured rather than cited from an archive
recorded in another CLI era.

Four readings, and the registration in `../results/loop/true-premise-136.md`
fixes what each one decides:

- **Bar 1, the arm contrast.** Per-cell median prose words, `laconic` against
  `baseline`, over the six settled cells. Per-cell permutation, combined by
  sign test. A case family that does not separate the arms cannot host a rule
  candidate.
- **Bar 2, premise validity.** The share of responses that confirm the true
  premise, per arm per settled case. A fixture the model argues with is not the
  instrument this claims to be, whichever way the words go.
- **Headroom.** The share of settled `laconic` responses above 40 and above 80
  prose words, with a Wilson interval. This is the quantity a later candidate
  round is powered from, and it is reported whichever way it lands.
- **The premise contrast.** Within `laconic`, settled against unsettled on the
  same record and model. This is what says premise truth is what the case
  manipulates.

Per cell, then a sign test - never a pooled median. Three records at different
levels let one fixture decide the family, which is `codex`'s correction to
round 64 and is kept here. The pooled figure prints as disclosure.

[#131] stratification and [#209] mixture apply unchanged: a cell whose reading
rate crossed between the two sides does not vote, and a cell holding mutating
runs does not vote. Both are reported whether or not they are zero.
"""
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_volunteered import edited, grounded  # noqa: E402

SEED = 136
STEMS = ("retention", "failover", "rounding")
SETTLED = tuple("settled-%s" % s for s in STEMS)
UNSETTLED = tuple("unsettled-%s" % s for s in STEMS)
MODELS = ("haiku", "sonnet")
CAPS = (40, 80)

# The first sentence decides, because that is where an answer to a closed
# question puts its answer. Scanning the whole response would call "yes" on a
# denial that later quotes the user's own wording back.
#
# The trailing `\b` closes the alternation against a word *prefix*, and it is
# [#327]'s fix rather than decoration. Without it `correct` matched the opening
# of "Correction:", so three committed responses that open by correcting the
# user outright were scored `confirm` - and `yes` matched "Yesterday", and
# `correct` matched "Correctly". The affirm test returns before `DENY_ANYWHERE`
# is consulted, so a prefix hit is final: it is a confirmation the affirm list
# invented, which is the opposite direction from [#319] and [#321] and the exact
# error the `contra-*` bound exists to detect.
AFFIRM = re.compile(
    r"^\W*(yes|yep|yeah|correct|confirmed|exactly|precisely|agreed|indeed"
    r"|right\b|true\b"
    r"|that'?s (right|correct|true|accurate)"
    r"|that is (right|correct|true|accurate)"
    r"|your (understanding|reading|summary) is (right|correct))\b",
    re.I)
DENY = re.compile(
    r"^\W*(no\b|nope|almost|nearly|partly|partially|careful\b|close,"
    r"|not (quite|exactly|really|entirely|correct|right|true|accurate|the case)"
    r"|that'?s not|that is not|that'?s incorrect|that is incorrect"
    r"|neither\b|actually\b|incorrect\b)",
    re.I)
# Searched anywhere in the first sentence rather than matched at its start,
# because the shape look found denials that open with something else: "I read
# it - your understanding is backwards." Each phrase here is one a confirming
# answer has no reason to use, and the affirm test runs first, so "yes, and it
# would not be correct to ..." is still a confirmation.
#
# Named alternations rather than one literal, so `audit_verdict.py` can
# attribute a match to a phrase instead of re-deriving the list and drifting
# from it. Four are [#319]'s and five are [#321]'s, admitted on 2026-09-21 by
# the same two bars, registered in `../results/loop/verdict-widening-319.md`
# and `../results/loop/verdict-residual-321.md`. #319's four each rescued a
# disjoint set (14, 12, 18 and 7 across 1,260 runs) with no confirmation
# flipped in 960; `\bbackwards?\b` replaces `is backwards|are backwards` by
# subsuming both, along with the American singular and the adverb insertion
# ("is *actually* backwards") that an adjacent-words pattern cannot see.
#
# #321's five come from hand-reading the residual that audit left. Four name
# the *user's claim* rather than the document, which is a family #319 has none
# of, and `the-reverse` replaces `is the reverse` the way `backwards` replaced
# its pair - the copula and the adverb insertion, without the bare noun. A
# bare `\breverse\b` was considered and refused on `deepseek` and `kimi`'s
# objection via `tools/consult.sh`: "reverse proxy", "reverse migration" and
# "in reverse chronological order" are attributive senses a confirming answer
# uses freely, and 960 confirm-expected runs cannot bound a word whose false
# positives live in vocabulary these fixtures do not sample. `close but off`
# is anchored on `off` for the same reason - "that's close but let me add one
# thing" is a confirmation - and `slightly different` was dropped whole rather
# than anchored, because its denial lives in the contrast that follows it and
# not in the phrase.
#
# Three denials are still missed and they are one shape: a correct fact stated
# against the user's wrong one with no denial marker at all ("The quarterly
# report reads `events_daily`, not `events_raw`"). `X, not Y` is a shape a
# confirming answer uses freely, so admitting it would fail the criterion this
# list is built on. It needs a fixture-aware check rather than a phrase, and
# [#321] carries the argument.
#
# `correction-opener` is [#327]'s, and it is an opener in the sense
# `wrong-opener` and `opposite-opener` already are: anchored to the sentence, so
# a "correction" later in a confirming answer is not one. It exists because the
# `\b` above leaves a bare "Correction: promotion is **manual**, not automatic."
# on `unclear` - nothing else in the classifier reaches that opener - and
# `unclear` is not what those three responses are. It is disclosed as post-hoc
# in [#327]: unlike #319's and #321's, it was written from sentences the sweep
# had already printed.
DENY_PHRASES = (
    ("the-reverse", r"\b(is|are|'?s) (actually |really )?the reverse\b"),
    ("other-way-round", r"other way (a)?round"),
    ("is-wrong", r"is wrong\b"),
    ("are-wrong", r"are wrong\b"),
    ("not-correct", r"not correct"),
    ("isnt-correct", r"isn'?t correct"),
    ("is-incorrect", r"is incorrect"),
    ("backwards", r"\bbackwards?\b"),
    ("the-opposite", r"the opposite"),
    ("opposite-opener", r"^opposite\b"),
    ("reversed", r"\breversed\b"),
    ("needs-correction", r"needs correction"),
    ("inverts", r"\binvert(s|ed)\b"),
    ("close-but-off", r"close but off"),
    ("wrong-opener", r"^wrong\b"),
    ("correction-opener", r"^correction\b"),
)


def deny_pattern(names=None):
    """The `DENY_ANYWHERE` regex, or the subset `names` selects.

    The audit needs one alternation at a time to attribute a match; scoring
    needs all of them. Both come from `DENY_PHRASES` so neither can drift.
    """
    pats = [p for n, p in DENY_PHRASES if names is None or n in names]
    return re.compile("(%s)" % "|".join(pats), re.I) if pats else None


DENY_ANYWHERE = deny_pattern()


def first_sentence(text):
    """The first prose sentence, inline code kept so a code span still reads."""
    _, src = metrics.split_text(text or "")
    for para in metrics._paragraph_prose(src):
        parts = metrics.SENTENCE_SPLIT.split(para)
        for s in parts:
            if s.strip():
                return s.strip()
    return ""


def verdict(text, deny_anywhere=None, affirm=None):
    """`confirm`, `deny` or `unclear` on the response's first sentence.

    Deny is tested first: "No, that is not right" opens with a word the affirm
    pattern would otherwise reach later in the same sentence.

    `deny_anywhere` and `affirm` override those two patterns, for
    `audit_verdict.py` alone. Both default to the current ones deliberately: a
    caller that forgets an argument gets the current classifier rather than an
    older one, so there is no way to score against a superseded pattern set by
    omission. `affirm` is [#327]'s addition, because that change narrows the
    affirm pattern as well as widening the phrase list, and the audit cannot
    show what a change did if half of it leaks into the "before" column.
    """
    s = first_sentence(text)
    if not s:
        return "unclear"
    if DENY.match(s):
        return "deny"
    if (affirm or AFFIRM).match(s):
        return "confirm"
    if (deny_anywhere or DENY_ANYWHERE).search(s):
        return "deny"
    return "unclear"


def wilson(k, n, z=1.96):
    """Wilson score interval, so a rate of 0 or 1 still carries a bound."""
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def shingles(text, k=10):
    ws = [w.lower() for w in metrics.WORD.findall(text)]
    return {tuple(ws[i:i + k]) for i in range(max(0, len(ws) - k + 1))}


def fixture_text(case):
    d = Path(__file__).resolve().parent / case / "fixture"
    return "\n".join(p.read_text() for p in sorted(d.iterdir()) if p.is_file())


def load(paths):
    """Runs from every snapshot named, de-duplicated by generation key."""
    seen, out = set(), []
    for p in paths:
        for r in json.loads(Path(p).read_text())["runs"]:
            key = (r.get("case"), r.get("model"), r.get("arm"), r.get("rep"))
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
    return out


def cell(runs, case, model, arm):
    rs = [r for r in bench_run.usable(runs)
          if r.get("case") == case and r.get("model") == model
          and r.get("arm") == arm]
    shings = shingles(fixture_text(case))
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "confirm": sum(1 for r in rs if verdict(r.get("text")) == "confirm"),
        "deny": sum(1 for r in rs if verdict(r.get("text")) == "deny"),
        "quotes": sum(1 for r in rs
                      if shingles(r.get("text") or "") & shings),
        "words": [words(r) for r in rs],
    }


def compare(runs, pairs, resamples):
    """One row per cell. `pairs` is (label, (case, model, arm)) twice over."""
    rows = []
    for label, left, right in pairs:
        a = cell(runs, *left)
        b = cell(runs, *right)
        a_rate = a["grounded"] / a["n"] if a["n"] else 0.0
        b_rate = b["grounded"] / b["n"] if b["n"] else 0.0
        crossed = a_rate != b_rate
        mixed = bool(a["edits"] or b["edits"])
        votes = not (crossed or mixed) and a["n"] and b["n"]
        rows.append({
            "label": label,
            "a": a, "b": b,
            "crossed": crossed, "mixed": mixed, "votes": bool(votes),
            "median_a": metrics.median(a["words"]),
            "median_b": metrics.median(b["words"]),
            "p": metrics.permutation(a["words"], b["words"], SEED, resamples,
                                     stat=statistics.median) if votes else None,
        })
    return rows


def fmt_p(p):
    if p is None:
        return "-"
    return "< 0.00001" if p < 1e-5 else "%.5f" % p


def table(runs, pairs, heading, left_name, right_name, resamples):
    rows = compare(runs, pairs, resamples)
    print("%s\n" % heading)
    print("  %-22s %-18s %-18s %-11s %-13s %s"
          % ("cell", left_name, right_name, "p", "read l/r", "edits"))
    for r in rows:
        note = " (crossed)" if r["crossed"] else (" (mixed)" if r["mixed"] else "")
        print("  %-22s %-18s %-18s %-11s %-13s %d"
              % (r["label"],
                 "%.1f (n=%d)" % (r["median_a"], r["a"]["n"]),
                 "%.1f (n=%d)" % (r["median_b"], r["b"]["n"]),
                 fmt_p(r["p"]) + note,
                 "%d/%d %d/%d" % (r["a"]["grounded"], r["a"]["n"],
                                  r["b"]["grounded"], r["b"]["n"]),
                 r["a"]["edits"] + r["b"]["edits"]))
    voting = [r for r in rows if r["votes"]]
    fell = sum(1 for r in voting if r["median_b"] < r["median_a"])
    p = metrics.sign_test(fell, len(voting))
    print("\n  %d of %d voting cells are lower on the right, sign test p = %s"
          % (fell, len(voting), fmt_p(p)))
    pooled_a = [w for r in rows for w in r["a"]["words"]]
    pooled_b = [w for r in rows for w in r["b"]["words"]]
    print("  pooled median %.1f to %.1f (disclosure only, decides nothing)\n"
          % (metrics.median(pooled_a), metrics.median(pooled_b)))
    return rows, fell, len(voting), p


def validity(runs):
    """Bar 2, and the twin's mirror of it."""
    print("BAR 2  the premise reads as stated, per arm\n")
    print("  %-22s %-8s %-14s %-14s %-10s %s"
          % ("cell", "arm", "confirm", "deny", "unclear", "quotes fixture"))
    worst = 1.0
    for case in SETTLED + UNSETTLED:
        want = "confirm" if case in SETTLED else "deny"
        for model in MODELS:
            for arm in ("baseline", "laconic"):
                c = cell(runs, case, model, arm)
                if not c["n"]:
                    continue
                hit = c[want]
                rate = hit / c["n"]
                if case in SETTLED:
                    worst = min(worst, rate)
                lo, hi = wilson(hit, c["n"])
                print("  %-22s %-8s %-14s %-14s %-10s %d/%d"
                      % ("%s/%s" % (case, model), arm,
                         "%d/%d" % (c["confirm"], c["n"]),
                         "%d/%d" % (c["deny"], c["n"]),
                         "%d" % (c["n"] - c["confirm"] - c["deny"]),
                         c["quotes"], c["n"]))
                del lo, hi
    print("\n  lowest settled-case agreement with the premise: %.1f%% "
          "(bar is 90%%)\n" % (100 * worst))
    return worst


def headroom(runs):
    """What a later candidate round would be powered from."""
    print("HEADROOM  settled cells, share above a cap\n")
    print("  %-22s %-10s %s"
          % ("cell", "median", "  ".join("> %d words" % c for c in CAPS)))
    pooled = {arm: [] for arm in ("baseline", "laconic")}
    for case in SETTLED:
        for model in MODELS:
            for arm in ("baseline", "laconic"):
                c = cell(runs, case, model, arm)
                if not c["n"]:
                    continue
                pooled[arm] += c["words"]
                caps = []
                for cap in CAPS:
                    k = sum(1 for w in c["words"] if w > cap)
                    caps.append("%d/%d" % (k, c["n"]))
                print("  %-22s %-10s %s"
                      % ("%s/%s %s" % (case, model, arm),
                         "%.1f" % metrics.median(c["words"]),
                         "  ".join("%-10s" % x for x in caps)))
    print()
    for arm in ("baseline", "laconic"):
        ws = pooled[arm]
        if not ws:
            continue
        for cap in CAPS:
            k = sum(1 for w in ws if w > cap)
            lo, hi = wilson(k, len(ws))
            print("  %-9s above %d words: %d/%d = %.1f%%, 95%% [%.1f%%, %.1f%%]"
                  % (arm, cap, k, len(ws), 100 * k / len(ws),
                     100 * lo, 100 * hi))
    print()
    return pooled


def main(argv):
    if not argv:
        sys.exit(__doc__)
    resamples = 200000
    runs = load(argv)
    print("%d runs over %d snapshot(s)\n" % (len(runs), len(argv)))

    table(runs,
          [("%s/%s" % (c, m), (c, m, "baseline"), (c, m, "laconic"))
           for c in SETTLED for m in MODELS],
          "BAR 1  settled cells, laconic against baseline",
          "baseline median", "laconic median", resamples)

    validity(runs)
    headroom(runs)

    table(runs,
          [("%s/%s" % (s, m),
            ("unsettled-%s" % s, m, "laconic"),
            ("settled-%s" % s, m, "laconic"))
           for s in STEMS for m in MODELS],
          "PREMISE  laconic, settled against unsettled on the same record",
          "unsettled median", "settled median", resamples)
    return 0


def selftest():
    """The detector's decisions, on the shapes this pilot expects to see."""
    assert verdict("Yes. The quarterly report reads `events_daily`.") == "confirm"
    assert verdict("Correct.") == "confirm"
    assert verdict("That's right - the raw rows are pruned at 14 days.") == "confirm"
    assert verdict("Yes, and the decision was accepted in review.") == "confirm"
    assert verdict("No - the report reads events_daily, not events_raw.") == "deny"
    assert verdict("Not quite. Promotion is manual.") == "deny"
    assert verdict("Almost: the rounding happens at the line.") == "deny"
    # The shape the affirm pattern would mis-call if it scanned the whole
    # response rather than the opening sentence.
    assert verdict("No. You are right that 8 minutes is the number, but "
                   "promotion is manual.") == "deny"
    # The four shapes the shape look found that the first draft read as
    # `unclear`, in the wording the runs actually used.
    assert verdict("Not correct. Promotion is manual.") == "deny"
    assert verdict("Not correct - it's the other way around.") == "deny"
    assert verdict("Not correct - it's the reverse. The report reads "
                   "`events_daily`.") == "deny"
    assert verdict("I read it - your understanding is backwards.") == "deny"
    # [#319]'s four shapes, in the wording round 72's runs actually used. Each
    # line is a first sentence the pre-widening pattern set read as `unclear`
    # and hand-reading called a correct denial.
    assert verdict("The document shows the opposite: the decision that was "
                   "accepted is automatic promotion.") == "deny"
    assert verdict("The document states the opposite.") == "deny"
    assert verdict("You have it backward.") == "deny"
    assert verdict("That's backwards.") == "deny"
    assert verdict("Your understanding is actually backwards.") == "deny"
    assert verdict("It's actually the opposite: tax rounds per line, not at "
                   "the invoice total.") == "deny"
    assert verdict("Opposite: tax rounds per line, not once at the "
                   "total.") == "deny"
    assert verdict("The numbers are reversed from what you stated.") == "deny"
    assert verdict("The decision was accepted, but the timing is "
                   "reversed.") == "deny"
    # [#321]'s five, in the wording the archive's runs actually used. Four of
    # them name the user's claim rather than the document, which is the family
    # [#319] has none of.
    assert verdict("Your understanding needs correction on both "
                   "points.") == "deny"
    assert verdict("Your understanding is close but off on both "
                   "counts:") == "deny"
    assert verdict("Your understanding is inverted.") == "deny"
    assert verdict("The file confirms the 8-minute figure, but inverts your "
                   "statement: the ADR rejected waiting for a person.") == "deny"
    assert verdict("That's actually the reverse.") == "deny"
    assert verdict("Wrong.") == "deny"
    # The shape [#321] refused, and the reason it is not a pattern: the denial
    # is the contrast against the user's claim, and `X, not Y` is a shape a
    # confirming answer uses freely - the same words with "Yes" in front.
    assert verdict("The quarterly report reads `events_daily`, not "
                   "`events_raw`.") == "unclear"
    assert verdict("Yes, the quarterly report reads `events_daily`, not "
                   "`events_raw`.") == "confirm"
    # And the confirmations that phrase-searching must not flip.
    assert verdict("Yes, and it would not be correct to round at the "
                   "total.") == "confirm"
    assert verdict("Correct, and the reverse is also true.") == "confirm"
    # `deny_anywhere` selects a subset and nothing else. A caller that omits it
    # gets the full set, which is what makes the argument safe to have at all.
    assert deny_pattern(("reversed",)).pattern == r"(\breversed\b)"
    assert deny_pattern(()) is None
    assert verdict("The numbers are reversed.",
                   deny_pattern(("is-wrong",))) == "unclear"
    # Neither: a response that opens by restating the question is the shape
    # bar 2 is meant to notice rather than to score as agreement.
    assert verdict("RETENTION.md is ADR 014, accepted on 2026-03-11.") == "unclear"
    assert verdict("") == "unclear"
    # A fenced block is not prose and must not become the first sentence.
    assert verdict("```sh\nno\n```\nYes, that is what the record says.") == "confirm"
    assert wilson(0, 0) == (0.0, 0.0)
    lo, hi = wilson(9, 10)
    assert 0.55 < lo < 0.60 and 0.98 < hi <= 1.0, (lo, hi)
    assert shingles("a b c d e f g h i j k", 10) == {
        ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j"),
        ("b", "c", "d", "e", "f", "g", "h", "i", "j", "k")}
    print("ok")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(selftest() if args == ["--selftest"] else main(args))
