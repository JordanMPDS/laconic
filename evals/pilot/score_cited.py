#!/usr/bin/env python3
"""Is the grounds citation in a `settled-*` answer responsive to being asked?

    python3 evals/pilot/score_cited.py <snapshot>...
    python3 evals/pilot/score_cited.py --selftest

[#305]'s item 1 proposed a rule against closing a response with a recap of its
own opening. Three routes to test it are now closed, and the third closed on
data rather than on argument: on the `settled-*` instrument round 71's edit
side is a **single paragraph** at the median, so there is no closing to cut,
and the words that restate the decision's status are 8% of the response. What
the residual is instead is **grounds citation** - 80% of the words - the model
reading the decision record and reciting its reasoning back to a user who has
just read it.

Whether that is harm is the question this file scores, and it cannot be read
off one arm. The `cited-*` cases are `settled-*` with one sentence added
asking for the record's own words. If a `settled-*` answer is already supplying
what a `cited-*` prompt asks for, the grounds are emitted whether or not they
were wanted, and the surplus is unrequested by measurement. If asking for them
makes the answer materially longer, the `settled-*` grounds are a response to
something in the question and a rule that suppressed them would be buying an
unchecked confirmation.

**Sonnet is the fixture-validity control, not a second target.** Haiku alone
cannot separate "haiku emits grounds regardless" from "the added sentence does
not ask clearly". Sonnet answers `settled-*` at 0 of 45 above 80 prose words,
so it has headroom in the direction the added sentence points: if sonnet
lengthens and haiku does not, the sentence asks and haiku is not listening.

Endpoint is prose words by `metrics.score`, one median per (stem, model) cell.
No judge call is bought and no label is written.

The primary is the same **stratified one-sided permutation** round 71
registered, imported from `score_settled` rather than rewritten: the statistic
is the mean over cells of (settled median - cited median) and the family label
is permuted within each cell, so cell composition is held fixed and no single
fixture can carry the result by being long. One-sided in the direction of
responsiveness - the null it rejects is "asking for the grounds does not make
the answer longer".

[#131] stratification and [#209] mixture apply unchanged, through
`score_settled.votes`: a cell whose reading rate differs between the two
families does not vote, and a cell holding mutating runs does not vote. Both
are reported whether or not they are zero.

[#131]: https://github.com/JordanMPDS/laconic/issues/131
[#209]: https://github.com/JordanMPDS/laconic/issues/209
[#305]: https://github.com/JordanMPDS/laconic/issues/305
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_premise import load, verdict, wilson  # noqa: E402
from score_settled import STEMS, cell, fmt_p, stratified, votes  # noqa: E402

SEED = 305
RESAMPLES = 200000
CAPS = (40, 80)
#: Registered in `../results/loop/cited-grounds-305.md` before any generation.
ALPHA = 0.05


# --- Part 1: where the words in a surviving settled-* answer go -------------
# Round 71 accepted an edit and disclosed that half its responses still run
# past 80 prose words. This decomposes those words by sentence role, which is
# what closes [#305] item 1: the closing recap it targets is 8% of them and
# absent from the median response entirely.

SENTENCE = re.compile(r"(?<=[.!?])\s+")
#: A sentence pointing at the record - a backtick identifier, a figure, or a
#: reporting verb naming the document. This is the recitation.
CITE = re.compile(r"(`[^`]+`|\d|ADR|record|document|states|says|explicitly"
                  r"|according)", re.I)
#: A sentence asserting the decision's standing rather than its content. This
#: is what a closing recap is made of.
STATUS = re.compile(r"\b(closed|accepted|settled|deliberate|revisit|stands"
                    r"|won'?t be|not a (bug|mistake|oversight)|intentional"
                    r"|by design)\b", re.I)


def sentences(text):
    prose, _ = metrics.split_text(text or "")
    return [s.strip() for s in SENTENCE.split(prose.strip()) if s.strip()]


def roles(run):
    """(total, verdict, citation, status, other) prose words for one response.

    The first sentence is the verdict, whatever it says. Every later sentence
    is citation if it points at the record, status if it asserts the decision's
    standing without pointing at the record, and other otherwise - so the three
    are disjoint and sum to the total by construction.
    """
    ss = sentences(run.get("text"))
    if not ss:
        return (0, 0, 0, 0, 0)
    first = len(ss[0].split())
    cite = status = other = 0
    for s in ss[1:]:
        n = len(s.split())
        if CITE.search(s):
            cite += n
        elif STATUS.search(s):
            status += n
        else:
            other += n
    return (first + cite + status + other, first, cite, status, other)


def closing_recap(run):
    """True when the response has more than one paragraph and the last one
    asserts the decision's standing - [#305] item 1's shape, on a fixture where
    the correct last paragraph is empty."""
    ps = [p for p in re.split(r"\n\s*\n", (run.get("text") or "").strip())
          if p.strip()]
    return len(ps) > 1 and bool(STATUS.search(ps[-1]))


def residual(runs, label):
    """One row of the Part 1 table, over the settled-*/haiku runs given."""
    rs = [r for r in bench_run.usable(runs)
          if (r.get("case") or "").startswith("settled-")
          and r.get("model") == "haiku" and r.get("arm") == "laconic"]
    if not rs:
        return None
    parts = [roles(r) for r in rs]
    tot = sum(p[0] for p in parts) or 1
    paras = [len([p for p in re.split(r"\n\s*\n", (r.get("text") or "").strip())
                  if p.strip()]) for r in rs]
    return {
        "label": label, "n": len(rs),
        "median_words": metrics.median([words(r) for r in rs]),
        "median_paras": metrics.median(paras),
        "recap": 100.0 * sum(1 for r in rs if closing_recap(r)) / len(rs),
        "verdict": 100.0 * sum(p[1] for p in parts) / tot,
        "cite": 100.0 * sum(p[2] for p in parts) / tot,
        "status": 100.0 * sum(p[3] for p in parts) / tot,
        "other": 100.0 * sum(p[4] for p in parts) / tot,
    }


def residual_report(control, edit):
    rows = [r for r in (residual(control, "control"), residual(edit, "round-71 edit"))
            if r]
    print("# Where the words go in a surviving settled-*/haiku answer "
          "(#305 item 1)\n")
    print("| | " + " | ".join(r["label"] for r in rows) + " |")
    print("|---|" + "--:|" * len(rows))
    for key, name, fmt in (
            ("n", "responses", "%d"),
            ("median_words", "median prose words", "%.0f"),
            ("median_paras", "median paragraphs", "%.0f"),
            ("recap", "closing paragraph restates the decision's status", "%.1f%%"),
            ("verdict", "share of words: the first sentence", "%.1f%%"),
            ("cite", "share of words: citing grounds from the record", "%.1f%%"),
            ("status", "share of words: restating the status", "%.1f%%"),
            ("other", "share of words: everything else", "%.1f%%")):
        print("| %s | %s |" % (name, " | ".join(fmt % r[key] for r in rows)))


def pairs_for(runs, model):
    """One row per stem: the settled cell, the cited cell, and whether it votes."""
    rows = []
    for stem in STEMS:
        a = cell(runs, "settled-%s" % stem, model)
        b = cell(runs, "cited-%s" % stem, model)
        v, crossed, mixed = votes(a, b)
        rows.append({"stem": stem, "model": model, "settled": a, "cited": b,
                     "votes": v, "crossed": crossed, "mixed": mixed,
                     "median_settled": metrics.median(a["words"]),
                     "median_cited": metrics.median(b["words"])})
    return rows


def arm(runs, model):
    """(rows, statistic, p) for one model. The statistic is mean over voting
    cells of (settled median - cited median), so a negative value means asking
    for the grounds made the answer longer, and p tests that direction."""
    rows = pairs_for(runs, model)
    voting = [(r["cited"]["words"], r["settled"]["words"])
              for r in rows if r["votes"]]
    stat, p = stratified(voting, seed=SEED, resamples=RESAMPLES)
    return rows, stat, p


def floor(rows):
    """The median per-cell stdev of the settled side, over the voting cells.

    The same estimator the scoped token floor and [#49]'s turn floor are built
    from, and it is here for the same reason: a permutation on cells with no
    within-cell spread calls any difference significant. A one-word median
    shift is not the model responding to a request for grounds, and without a
    floor this reads it as one. Measured from the round's own control side,
    never a published constant.
    """
    voting = [r for r in rows if r["votes"]]
    spreads = [statistics.stdev(r["settled"]["words"])
               for r in voting if len(r["settled"]["words"]) > 1]
    return metrics.median(spreads) if spreads else 0.0


def responsive(rows, p):
    """Registered per-model reading: the permutation clears alpha, the shift
    beats the measured floor, and every voting cell moves the same way."""
    voting = [r for r in rows if r["votes"]]
    if not voting or p is None:
        return False
    shift = sum(r["median_cited"] - r["median_settled"] for r in voting) \
        / len(voting)
    return (p < ALPHA
            and shift > floor(rows)
            and all(r["median_cited"] > r["median_settled"] for r in voting))


def decide(haiku_rows, haiku_p, sonnet_rows, sonnet_p):
    """The three-way verdict registered in `cited-grounds-305.md`."""
    h = responsive(haiku_rows, haiku_p)
    s = responsive(sonnet_rows, sonnet_p)
    if h:
        return ("responsive",
                "Haiku lengthens when the grounds are asked for, so a "
                "settled-* answer's grounds are at least partly a response to "
                "the question. No rule edit is proposed against grounds "
                "citation on this instrument.")
    if s:
        return ("unresponsive",
                "Sonnet lengthens and haiku does not, so the added sentence "
                "asks and haiku emits the grounds either way. The residual on "
                "settled-* is unrequested by measurement, and a candidate "
                "round may target it.")
    return ("uninformative",
            "Neither model lengthens, so the prompt manipulation is not shown "
            "to ask for anything. Nothing is concluded about haiku and the "
            "next unit is a sharper ask, not a rule edit.")


def table(rows, stat, p, model):
    out = ["## %s\n" % model,
           "| stem | n settled | n cited | settled median | cited median "
           "| difference | votes |",
           "|---|--:|--:|--:|--:|--:|---|"]
    for r in rows:
        why = "yes"
        if not r["votes"]:
            why = "no (reading rate crossed)" if r["crossed"] else (
                "no (mutating runs)" if r["mixed"] else "no (empty cell)")
        out.append("| %s | %d | %d | %.1f | %.1f | %+.1f | %s |" % (
            r["stem"], r["settled"]["n"], r["cited"]["n"],
            r["median_settled"], r["median_cited"],
            r["median_cited"] - r["median_settled"], why))
    if stat is None:
        out.append("\nNo cell votes, so the permutation is not run.")
    else:
        out.append("\nStratified permutation: mean settled minus cited "
                   "**%+.2f words**, one-sided p = %s, %d of %d cells voting, "
                   "%d rising." % (
                       stat, fmt_p(p),
                       sum(1 for r in rows if r["votes"]), len(rows),
                       sum(1 for r in rows if r["votes"]
                           and r["median_cited"] > r["median_settled"])))
        out.append("Measured floor (median per-cell stdev of the settled "
                   "side): **%.1f words**." % floor(rows))
    return "\n".join(out)


def headroom(rows):
    out = ["| cell | n | > 40 w | > 80 w | median | confirm rate |",
           "|---|--:|--:|--:|--:|---|"]
    for r in rows:
        for fam in ("settled", "cited"):
            c = r[fam]
            k, n = c["confirm"], c["n"]
            lo, hi = wilson(k, n)
            out.append("| %s-%s/%s | %d | %d | %d | %.1f | %d/%d [%.1f, %.1f] |"
                       % (fam, r["stem"], r["model"], n,
                          sum(1 for w in c["words"] if w > CAPS[0]),
                          sum(1 for w in c["words"] if w > CAPS[1]),
                          metrics.median(c["words"]), k, n,
                          100 * lo, 100 * hi))
    return "\n".join(out)


def report(runs):
    hr, hs, hp = arm(runs, "haiku")
    sr, ss, sp = arm(runs, "sonnet")
    print("# Are the grounds in a settled-* answer asked for? (#305, #136)\n")
    print(table(hr, hs, hp, "haiku") + "\n")
    print(table(sr, ss, sp, "sonnet") + "\n")
    print("## Headroom and the confirmation floor\n")
    print(headroom(hr + sr) + "\n")
    kind, why = decide(hr, hp, sr, sp)
    print("## Verdict: **%s**\n" % kind)
    print(why)
    return kind


def selftest():
    def run(case, model, words_, turns=2, tools=None, text=None):
        body = text if text is not None else ("Yes. " + "word " * (words_ - 1))
        return {"case": case, "model": model, "arm": "laconic", "rep": 0,
                "text": body, "num_turns": turns, "tools": tools or ["Read"],
                "ok": True}

    # `stratified` is one-sided on (cited, settled): a cited side that is
    # longer drives the statistic negative and the p-value small.
    a, p = stratified([([200] * 8, [100] * 8)] * 3, seed=SEED, resamples=2000)
    assert a is not None and a < 0, a
    assert p < 0.05, p
    a, p = stratified([([100] * 8, [100] * 8)] * 3, seed=SEED, resamples=2000)
    assert abs(a) < 1e-9 and p > 0.4, (a, p)

    # No cell votes when a family's reading rate crossed, and the row says why.
    runs = []
    for stem in STEMS:
        for i in range(5):
            runs.append(run("settled-%s" % stem, "haiku", 50))
            runs.append(run("cited-%s" % stem, "haiku", 90, turns=1))
    rows = pairs_for(runs, "haiku")
    assert not any(r["votes"] for r in rows)
    assert all(r["crossed"] for r in rows)
    assert "reading rate crossed" in table(rows, None, None, "haiku")

    # A mutating run in either family refuses the cell on its own ([#209]).
    runs = []
    for stem in STEMS:
        for i in range(5):
            runs.append(run("settled-%s" % stem, "haiku", 50))
            runs.append(run("cited-%s" % stem, "haiku", 90,
                            tools=["Read", "Edit"] if i == 0 else ["Read"]))
    rows = pairs_for(runs, "haiku")
    assert not any(r["votes"] for r in rows)
    assert all(r["mixed"] for r in rows)

    # Clean cells vote, and the direction reads as written.
    def batch(settled_w, cited_w, model="haiku", spread=6):
        """Cells carry real within-cell spread, because a permutation on
        identical values calls a one-word difference significant."""
        out = []
        for stem in STEMS:
            for i in range(8):
                j = (i % 4) * spread - spread
                out.append(run("settled-%s" % stem, model, settled_w + j))
                out.append(run("cited-%s" % stem, model, cited_w + j))
        return out

    rows, stat, p = arm(batch(60, 160), "haiku")
    assert all(r["votes"] for r in rows)
    assert stat < 0 and p < 0.05, (stat, p)
    assert responsive(rows, p)

    # The floor is the median per-cell stdev of the settled side, measured.
    rows = pairs_for(batch(60, 61), "haiku")
    import statistics as _st
    want = _st.stdev(rows[0]["settled"]["words"])
    assert abs(floor(rows) - want) < 1e-9, (floor(rows), want)
    assert floor(rows) > 1.0, floor(rows)

    # A shift inside that floor is not responsiveness however small p is.
    assert not responsive(rows, 1e-9), floor(rows)
    # And the same rows clear it once the shift is larger than the floor.
    wide = pairs_for(batch(60, 60 + int(floor(rows)) + 5), "haiku")
    assert responsive(wide, 1e-9), floor(wide)

    rows, stat, p = arm(batch(60, 61), "haiku")
    assert not responsive(rows, p), (stat, p)

    # The three-way verdict, each branch.
    hr, hp = arm(batch(60, 160), "haiku")[0], arm(batch(60, 160), "haiku")[2]
    sr, sp = arm(batch(60, 160, "sonnet"), "sonnet")[0], \
        arm(batch(60, 160, "sonnet"), "sonnet")[2]
    assert decide(hr, hp, sr, sp)[0] == "responsive"

    fr, fp = arm(batch(60, 61), "haiku")[0], arm(batch(60, 61), "haiku")[2]
    assert decide(fr, fp, sr, sp)[0] == "unresponsive"

    nr, np_ = arm(batch(60, 61, "sonnet"), "sonnet")[0], \
        arm(batch(60, 61, "sonnet"), "sonnet")[2]
    assert decide(fr, fp, nr, np_)[0] == "uninformative"

    # A cited side that comes out SHORTER is not responsiveness.
    sr2, sp2 = arm(batch(160, 60), "haiku")[0], arm(batch(160, 60), "haiku")[2]
    assert not responsive(sr2, sp2)

    # One cell falling while two rise fails the consistency requirement even
    # when the pooled permutation clears alpha.
    runs = batch(60, 400)
    runs = [r for r in runs if r["case"] != "cited-rounding"]
    for i in range(8):
        runs.append(run("cited-rounding", "haiku", 20 + (i % 4) * 6))
    rows = pairs_for(runs, "haiku")
    assert all(r["votes"] for r in rows)
    assert sum(1 for r in rows
               if r["median_cited"] > r["median_settled"]) == 2
    assert not responsive(rows, 1e-9)

    # The confirmation floor is read off the same runs, not a second pass.
    runs = batch(60, 160)
    assert "confirm rate" in headroom(pairs_for(runs, "haiku"))
    assert verdict("Yes.") == "confirm"

    # Part 1: the three roles are disjoint and sum to the total.
    t = ("Yes.\n\nThe ADR states tax rounds at the line in `tax.py`. "
         "It happens a third of the time.\n\nThe decision is closed.")
    tot, first, cite, status, other = roles({"text": t})
    assert first == 1, first
    assert cite > 0 and status > 0, (cite, status)
    assert first + cite + status + other == tot, (first, cite, status, other, tot)

    # A trailing status paragraph is the recap shape; a single paragraph is not.
    assert closing_recap({"text": t})
    assert not closing_recap({"text": "Yes. The decision is closed."})
    assert not closing_recap({"text": "Yes.\n\nThe ADR states it at the line."})

    r = residual([{"case": "settled-rounding", "model": "haiku",
                   "arm": "laconic", "ok": True, "num_turns": 2,
                   "text": t}], "x")
    assert r["n"] == 1 and r["median_paras"] == 3, r
    assert abs(r["verdict"] + r["cite"] + r["status"] + r["other"] - 100) < 1e-6
    assert residual([], "x") is None

    print("score_cited.py selftest: passed")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--residual-control", nargs="*", default=[],
                    help="round-71 control snapshots, for the Part 1 table")
    ap.add_argument("--residual-edit", nargs="*", default=[],
                    help="round-71 edit snapshots, for the Part 1 table")
    args = ap.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.residual_control or args.residual_edit:
        residual_report(load(args.residual_control), load(args.residual_edit))
        return 0
    if not args.snapshots:
        ap.error("name at least one snapshot, or pass --selftest")
    report(load(args.snapshots))
    return 0


if __name__ == "__main__":
    sys.exit(main())
