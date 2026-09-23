#!/usr/bin/env python3
"""Round 77: does hoisting the reading instruction out of the pre-action
check's broken-thing conditional lower the unread rate on design questions?
([#264])

A candidate round. `laconic-precheck-read` is the shipped `full` slice with
item 1 of the check reworded and every other byte identical; it is generated
beside `laconic` in one interleaved pass, so the two arms share every shard,
every minute and every CLI release. Round 63 generated the same contrast and
never tested it, because its registered gate 1 did not fire; read post hoc it
was 202/420 against 232/420. This round tests it once, directly.

    primary   unread rate, -read below laconic, six design-* cells on sonnet,
              Mantel-Haenszel stratified by case, one-sided, alpha 0.05, one
              look. The within-case permutation is printed beside it.
    bounds    each fatal, each one-sided in the direction of harm:
              - `conditional`/sonnet `edited` rises        (Fisher 0.05)
              - `conditional`/sonnet `locates_defect` falls (Fisher 0.05)
              - sentinel runs that open something rise    (Fisher 0.05)
              - design prose length, all runs, over 1.10x (point estimate)
              - sentinel prose length, all runs, over 1.10x (point estimate)

Everything is deterministic. Nothing here reads a judge verdict.

Round 78 scores `laconic-precheck-scoped` under the same bars with
`--edit-arm laconic-precheck-scoped`. Any other arm in the snapshots, such as
round 78's `-read` on the sentinel, is printed as a disclosure and decides
nothing.

[#264]: https://github.com/JordanMPDS/laconic/issues/264
"""
import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "bench"))
import score_dilution as sd  # noqa: E402
from score_precheck import (DESIGN_CASES, SENTINEL_CASES, SHIP_ARM,  # noqa: E402
                            READ_ARM, LENGTH_MARGIN, contrast_line,
                            per_cell, per_shard, turns)
from score_volunteered import edited, locates_defect  # noqa: E402
from report import _fisher_upper_tail as fisher  # noqa: E402

ALPHA = 0.05


def _count(runs, arm, cases, pred):
    rows = [r for r in runs if r["arm"] == arm and r["case"] in cases
            and r.get("model") == "sonnet"]
    return sum(1 for r in rows if pred(r)), len(rows)


def _ratio(runs, cases, arm=READ_ARM):
    got = sd.blocked_log_words(runs, arm, cases, strata=False, ref=SHIP_ARM)
    return (got[1], got[2], got[3]) if got else None


def verdict(runs, out=print, arm=READ_ARM):
    """Print the round and return (accept, reasons)."""
    reasons = []
    design = [r for r in runs if r["case"] in DESIGN_CASES
              and r.get("model") == "sonnet"]
    out("=== primary: unread rate, %s against %s ===" % (arm, SHIP_ARM))
    z, _ = contrast_line(design, arm, SHIP_ARM, DESIGN_CASES,
                         "unread rate", out)
    # contrast_line prints p for a rise; the claim is a fall.
    p = 0.5 * math.erfc(-z / math.sqrt(2))
    fires = p < ALPHA
    out("  one-sided p for the fall = %.5f - %s"
        % (p, "PASSES" if fires else "does not pass"))
    if not fires:
        reasons.append("primary: p = %.5f" % p)
    per_cell(design, [SHIP_ARM, arm], DESIGN_CASES, out)
    per_shard(design, arm, SHIP_ARM, DESIGN_CASES, out)
    turns(design, [SHIP_ARM, arm], DESIGN_CASES, out)

    out("")
    out("=== fatal bounds ===")
    rows = (
        ("conditional edited (rise)", ["conditional"], edited, True),
        ("conditional locates_defect (fall)", ["conditional"],
         lambda r: locates_defect(r.get("text") or ""), False),
        ("sentinel opened something (rise)", SENTINEL_CASES, sd.grounded, True),
    )
    for label, cases, pred, rise in rows:
        c, cn = _count(runs, SHIP_ARM, cases, pred)
        e, en = _count(runs, arm, cases, pred)
        if not cn or not en:
            out("  %-36s not bought" % label)
            reasons.append("%s: not bought" % label)
            continue
        bp = fisher(e, en, c, cn) if rise else fisher(en - e, en, cn - c, cn)
        held = bp >= ALPHA
        out("  %-36s %d/%d against %d/%d, one-sided p = %.5f, %s"
            % (label, c, cn, e, en, bp, "held" if held else "FIRES"))
        if not held:
            reasons.append("%s: p = %.5f" % (label, bp))
    for label, cases in (("design prose length", DESIGN_CASES),
                         ("sentinel prose length", SENTINEL_CASES)):
        got = _ratio([r for r in runs if r.get("model") == "sonnet"], cases,
                     arm)
        if not got:
            out("  %-36s not bought" % label)
            reasons.append("%s: not bought" % label)
            continue
        ratio, lp, blocks = got
        held = ratio <= LENGTH_MARGIN
        out("  %-36s %.3fx over %d blocks (p = %.4f), margin %.2fx, %s"
            % (label, ratio, blocks, lp, LENGTH_MARGIN,
               "held" if held else "FIRES"))
        if not held:
            reasons.append("%s: %.3fx" % (label, ratio))
    others = sorted({r["arm"] for r in runs} - {SHIP_ARM, arm})
    for other in others:
        out("")
        out("=== disclosure, decides nothing: %s ===" % other)
        for label, cases in (("design", DESIGN_CASES),
                             ("sentinel", SENTINEL_CASES)):
            got = _ratio([r for r in runs if r.get("model") == "sonnet"],
                         cases, other)
            if got:
                out("  %s prose length against %s: %.3fx over %d blocks"
                    " (p = %.4f)" % (label, SHIP_ARM, got[0], got[2], got[1]))
            got = sd.blocked_log_words(
                [r for r in runs if r.get("model") == "sonnet"], other,
                cases, strata=False, ref=arm)
            if got:
                out("  %s prose length against %s: %.3fx over %d blocks"
                    " (p = %.4f)" % (label, arm, got[1], got[3], got[2]))
    accept = not reasons
    out("")
    out("VERDICT: %s" % ("ACCEPT step 1" if accept else
                         "REJECT - " + "; ".join(reasons)))
    return accept, reasons


def _selftest():
    import random
    rnd = random.Random(77)
    fails = []

    def check(name, ok):
        print("%-4s %s" % ("ok" if ok else "FAIL", name))
        if not ok:
            fails.append(name)

    def run(arm, case, rep, unread, words=50, tools=()):
        return {"arm": arm, "case": case, "model": "sonnet", "rep": rep,
                "ok": True, "text": "word " * words, "generator": "g1",
                "num_turns": 1 if unread else 4, "tools": list(tools)}

    def build(read_rate, sentinel_words=20, cond_edits=0):
        rows = []
        for case in DESIGN_CASES:
            for i in range(100):
                rows.append(run(SHIP_ARM, case, i, rnd.random() < 0.55))
                rows.append(run(READ_ARM, case, i, rnd.random() < read_rate))
        for case in SENTINEL_CASES:
            for i in range(40):
                rows.append(run(SHIP_ARM, case, i, True, 20))
                rows.append(run(READ_ARM, case, i, True, sentinel_words))
        for i in range(80):
            rows.append(run(SHIP_ARM, "conditional", i, False,
                            tools=("Read",)))
            rows.append(run(READ_ARM, "conditional", i, False,
                            tools=("Read", "Edit") if i < cond_edits
                            else ("Read",)))
        return rows

    quiet = []
    ok, why = verdict(build(0.40), out=quiet.append)
    check("a clear fall with every bound flat accepts", ok and not why)
    ok, why = verdict(build(0.55), out=quiet.append)
    check("no effect rejects on the primary",
          not ok and any(w.startswith("primary") for w in why))
    ok, why = verdict(build(0.70), out=quiet.append)
    check("a rise in unread rejects on the primary", not ok)
    ok, why = verdict(build(0.40, sentinel_words=24), out=quiet.append)
    check("sentinel prose 1.2x fires its bound",
          not ok and any("sentinel prose" in w for w in why))
    ok, why = verdict(build(0.40, cond_edits=10), out=quiet.append)
    check("conditional edits 0 to 10 fire their bound",
          not ok and any("edited" in w for w in why))
    # locates_defect reads nothing in these stubs on either side, so the
    # fall bound sits at 0/80 against 0/80 and must hold rather than fire.
    check("an all-zero fall bound holds", "locates_defect (fall)" in
          "\n".join(quiet) and not any("locates" in w for w in why))
    ok, why = verdict([r for r in build(0.40) if r["case"] != "conditional"],
                      out=quiet.append)
    check("an unbought bound rejects rather than passing silently",
          not ok and any("not bought" in w for w in why))
    # Round 78: the same bars on another arm, with -read as a disclosure.
    scoped = [dict(r, arm="laconic-precheck-scoped") if r["arm"] == READ_ARM
              else r for r in build(0.40)]
    extra = [dict(r, arm=READ_ARM, text="word " * 30) for r in scoped
             if r["arm"] == SHIP_ARM and r["case"] in SENTINEL_CASES]
    lines = []
    ok, why = verdict(scoped + extra, out=lines.append,
                      arm="laconic-precheck-scoped")
    check("--edit-arm scores the named arm and a third arm decides nothing",
          ok and not why and any("disclosure" in l for l in lines))
    ok, why = verdict(scoped, out=quiet.append)
    check("the default arm absent from the data rejects rather than passes",
          not ok)
    print("\n%d failure(s)" % len(fails))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--edit-arm", default=READ_ARM,
                    help="the arm the bars score (default %(default)s)")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if not args.snapshots:
        return ap.error("give the round's snapshots, or --selftest")
    runs, versions = sd.load(args.snapshots)
    print("%d usable runs, CLI release(s): %s\n" % (len(runs), ", ".join(versions)))
    accept, _ = verdict(runs, arm=args.edit_arm)
    return 0 if accept else 1


if __name__ == "__main__":
    sys.exit(main())
