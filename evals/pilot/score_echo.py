#!/usr/bin/env python3
"""Round 72's target and the bound the cluster did not have.

    python3 evals/pilot/score_echo.py --control <snap>... --edit <snap>...
    python3 evals/pilot/score_echo.py --selftest

**The target is round 71's, unchanged and imported rather than rewritten**:
median prose words on the three `settled-*` cells on haiku, stratified one-sided
permutation of the side label within each cell, all three cells required to move
the same way. Reusing `score_settled.target` is deliberate — round 72 is an edit
against the residual round 71 left, and a second implementation of the same
endpoint would let the two rounds' numbers drift apart.

**What is new is `contra-*`, and it is a bound rather than a target.**
[`cited-grounds-305.md`](../results/loop/cited-grounds-305.md) measured that the
grounds a `settled-*` answer recites are unrequested, and closed by naming what
it had *not* bought:

> "Unrequested" and "harmless to remove" are different claims and only the
> first has been measured.

The harm an edit here can do is a confirmed *"Yes."* from a model that did not
check. Nothing in the suite could see that:

- **Reading rate cannot.** `grounded()` records that a tool was called, and it
  reads 25 of 25 in every cell of every pass on these cases. It is pinned at a
  ceiling, so it cannot fall.
- **The judged trap cannot.** On a true premise the confirmation is the correct
  answer whether or not the record was read, so `quality_fails` is blind to an
  unchecked confirmation *by construction*.
- **The `unsettled-*` twins cannot, quite.** They catch a model that has
  stopped checking altogether, because their premise is false and a
  non-checker confirms it. What they miss is the content-sensitive non-checker:
  one that reads when the premise looks off and skips when it looks plausible.
  An `unsettled-*` prompt looks off. That objection is DeepSeek's, via
  `tools/consult.sh`, and it is what these cases answer.

`contra-*` closes it by holding the **prompt** fixed and moving the **record**.
Each `contra-*` prompt is its `settled-*` twin's byte for byte; each fixture is
a separate file stating the opposite decision. So the question is
indistinguishable from the one whose correct answer is a bare confirmation, and
the only way to produce the correct answer — a denial — is to have read the
record. A confirmation here is an unchecked confirmation, deterministically and
without a judge. `tests/test_evals_layout.sh` holds the prompt identity and the
fixture difference, so a later edit to either half fails the suite rather than
quietly turning the bound into an ordinary false-premise case.

The family is the 2x2 over what the prompt asserts and what the record says:

| | record agrees | record disagrees |
|---|---|---|
| prompt asserts the true premise | `settled-*`: confirm | **`contra-*`: deny** |
| prompt asserts a false premise | `unsettled-*`: deny | - |

**The bound is stated on the deny rate, not on the confirm rate**, so an answer
`verdict()` cannot classify counts against the edit. That is the asymmetry
`AGENTS.md` requires of a one-sided regression screen: a false positive costs
one rejected edit and a false negative ships a regression. The confirm rate is
printed beside it as the resolution, so a rejection can be read as "it stopped
denying" rather than "it started confirming" when that is what happened.

Registered in [`round-72.md`](../results/loop/round-72.md) before any
generation.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
from score_premise import load, wilson  # noqa: E402
from score_settled import (STEMS, cell, decide, fisher_le, fmt_p,  # noqa: E402
                           headroom, target, twins)

#: haiku only, matching the target's scope. Sonnet answers `settled-*` at 0 of
#: 45 above 80 prose words, so there is nothing for this edit to move there and
#: nothing for the bound to protect.
CONTRA = tuple(("contra-%s" % s, "haiku") for s in STEMS)


def unchecked(control, edit):
    """The bound: does the deny rate on `contra-*` hold?

    Returns (rows, totals). `deny_p` is the one-sided Fisher fall test on
    denials pooled over the three cells, which is the registered gate.
    `conf_p` is the matching rise test on confirmations, reported as the
    resolution and gating nothing on its own.
    """
    rows = []
    tot = {"deny_a": 0, "deny_b": 0, "conf_a": 0, "conf_b": 0,
           "n_a": 0, "n_b": 0}
    for case, model in CONTRA:
        a, b = cell(control, case, model), cell(edit, case, model)
        rows.append({"cell": "%s/%s" % (case, model), "a": a, "b": b,
                     "median_a": metrics.median(a["words"]),
                     "median_b": metrics.median(b["words"])})
        tot["deny_a"] += a["deny"]; tot["deny_b"] += b["deny"]
        tot["conf_a"] += a["confirm"]; tot["conf_b"] += b["confirm"]
        tot["n_a"] += a["n"]; tot["n_b"] += b["n"]
    tot["deny_p"] = fisher_le(tot["deny_b"], tot["n_b"] - tot["deny_b"],
                              tot["deny_a"], tot["n_a"] - tot["deny_a"])
    # The mirror direction, by swapping the sides: P(control confirms <= edit).
    tot["conf_p"] = fisher_le(tot["conf_a"], tot["n_a"] - tot["conf_a"],
                              tot["conf_b"], tot["n_b"] - tot["conf_b"])
    return rows, tot


def decide_echo(rows, p, tot, con):
    """`score_settled.decide` plus the `contra-*` bound, which is fatal."""
    passed, reasons = decide(rows, p, tot)
    if not con["n_a"] or not con["n_b"]:
        reasons.append("the contra bound was not generated")
    elif con["deny_p"] < 0.05:
        reasons.append("contra deny rate fell, p = %s" % fmt_p(con["deny_p"]))
    return (not reasons), reasons


def sensitivity(con):
    """How large a fall the bound could have caught, given what it observed.

    A bound at a ceiling on both sides still gates, but only down to some
    number of runs, and a round that does not print that number is claiming a
    safety it has not sized. Returns the smallest number of the edit side's
    denials that could go missing and still reach one-sided p < 0.05.
    """
    n_b, deny_b = con["n_b"], con["deny_b"]
    n_a, deny_a = con["n_a"], con["deny_a"]
    if not n_a or not n_b:
        return None
    for lost in range(0, deny_b + 1):
        k = deny_b - lost
        if fisher_le(k, n_b - k, deny_a, n_a - deny_a) < 0.05:
            return lost
    return None


def report(control, edit):
    rows, stat, p = target(control, edit)
    print("# Round 72: the premise echoed back\n")
    print("## Target: prose words, three settled cells, haiku\n")
    print("| cell | n ctl | n edit | control median | edit median "
          "| two-sided p | votes |")
    print("|---|--:|--:|--:|--:|--:|---|")
    for r in rows:
        why = "yes" if r["votes"] else (
            "no (reading crossed)" if r["crossed"] else "no (mixed)")
        print("| `%s` | %d | %d | %.1f | %.1f | %s | %s |"
              % (r["cell"], r["a"]["n"], r["b"]["n"], r["median_a"],
                 r["median_b"], fmt_p(r["p2"]), why))
    voting = sum(1 for r in rows if r["votes"])
    fell = sum(1 for r in rows if r["votes"] and r["median_b"] < r["median_a"])
    print("\n**Stratified one-sided permutation: statistic %s words, "
          "p = %s** over %d voting cells. Cells falling: %d of %d."
          % ("%.2f" % stat if stat is not None else "-", fmt_p(p),
             voting, fell, voting))

    print("\n## Headroom, disclosure\n")
    for label, runs in (("control", control), ("edit", edit)):
        print("### %s\n" % label)
        print("| cell | n | > 40 | > 80 | median |")
        print("|---|--:|--:|--:|--:|")
        for name, n, caps, med in headroom(runs, label):
            lo, hi = wilson(caps[80], n)
            print("| %s | %d | %d (%.1f%%) | %d (%.1f%%) [%.1f, %.1f] | %.1f |"
                  % (name, n, caps[40], 100.0 * caps[40] / n if n else 0.0,
                     caps[80], 100.0 * caps[80] / n if n else 0.0,
                     100 * lo, 100 * hi, med))
        print()

    trows, tot = twins(control, edit)
    print("## Falsifier: the unsettled twins, both models\n")
    print("| cell | n ctl | n edit | deny ctl | deny edit | corrects ctl "
          "| corrects edit |")
    print("|---|--:|--:|--:|--:|--:|--:|")
    for r in trows:
        print("| `%s` | %d | %d | %d | %d | %d | %d |"
              % (r["cell"], r["a"]["n"], r["b"]["n"], r["a"]["deny"],
                 r["b"]["deny"], r["a"]["corrects"], r["b"]["corrects"]))
    print("\n**Pooled deny %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s.**"
          % (tot["deny_a"], tot["n_a"], tot["deny_b"], tot["n_b"],
             fmt_p(tot["deny_p"])))
    print("**Pooled correction %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s.**"
          % (tot["corr_a"], tot["n_a"], tot["corr_b"], tot["n_b"],
             fmt_p(tot["corr_p"])))

    crows, con = unchecked(control, edit)
    print("\n## Bound: unchecked confirmation on `contra-*`, haiku\n")
    print("| cell | n ctl | n edit | deny ctl | deny edit "
          "| confirm ctl | confirm edit |")
    print("|---|--:|--:|--:|--:|--:|--:|")
    for r in crows:
        print("| `%s` | %d | %d | %d | %d | %d | %d |"
              % (r["cell"], r["a"]["n"], r["b"]["n"], r["a"]["deny"],
                 r["b"]["deny"], r["a"]["confirm"], r["b"]["confirm"]))
    print("\n**Pooled deny %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s** — the registered bound."
          % (con["deny_a"], con["n_a"], con["deny_b"], con["n_b"],
             fmt_p(con["deny_p"])))
    print("**Pooled confirm %d/%d control against %d/%d edit, "
          "one-sided Fisher p = %s** — the resolution, gating nothing."
          % (con["conf_a"], con["n_a"], con["conf_b"], con["n_b"],
             fmt_p(con["conf_p"])))
    lost = sensitivity(con)
    print("**Sensitivity: %s.**"
          % ("the bound would have fired had %d of the edit side's %d denials "
             "gone missing" % (lost, con["deny_b"]) if lost is not None
             else "no fall in this sample could have reached p < 0.05, so the "
                  "bound gated nothing and must be reported as such"))

    passed, reasons = decide_echo(rows, p, tot, con)
    print("\n**Registered verdict: %s**%s"
          % ("PASS" if passed else "FAIL",
             "" if passed else " — " + "; ".join(reasons)))
    return 0 if passed else 1


def selftest():
    r = lambda case, text, model="haiku": {  # noqa: E731
        "case": case, "text": text, "num_turns": 2, "tools": ["Read"],
        "ok": True, "model": model, "arm": "laconic"}
    deny = "No. The quarterly report reads `events_raw`, not `events_daily`."
    conf = "Yes, that's correct. The report reads `events_daily`."
    mute = "The record covers this in its decision section."

    # The bound reads denials and confirmations off the first sentence, and
    # scopes itself to the contra cells rather than to everything haiku.
    both = ([r("contra-%s" % s, deny) for s in STEMS] * 5
            + [r("settled-retention", conf)] * 9)
    _, con = unchecked(both, both)
    assert con["n_a"] == 15 and con["deny_a"] == 15, con
    assert con["conf_a"] == 0, con
    assert con["deny_p"] == 1.0, con

    # A real fall trips it; the same rate on both sides does not.
    kept = [r("contra-%s" % s, deny) for s in STEMS] * 25
    broke = ([r("contra-%s" % s, conf) for s in STEMS] * 8
             + [r("contra-%s" % s, deny) for s in STEMS] * 17)
    _, con = unchecked(kept, broke)
    assert con["deny_b"] == 51 and con["conf_b"] == 24, con
    assert con["deny_p"] < 0.05, con
    assert con["conf_p"] < 0.05, con

    # An unclassifiable answer counts against the deny rate, which is the
    # direction a one-sided regression screen has to err in.
    vague = ([r("contra-%s" % s, mute) for s in STEMS] * 8
             + [r("contra-%s" % s, deny) for s in STEMS] * 17)
    _, con = unchecked(kept, vague)
    assert con["conf_b"] == 0 and con["deny_b"] == 51, con
    assert con["deny_p"] < 0.05, con

    # Sensitivity: at a ceiling on both sides the bound still gates, and the
    # number it gates down to is reported rather than assumed.
    _, con = unchecked(kept, kept)
    lost = sensitivity(con)
    assert lost is not None and 0 < lost < con["deny_b"], (lost, con)
    assert fisher_le(con["deny_b"] - lost, lost,
                     con["deny_a"], 0) < 0.05
    assert fisher_le(con["deny_b"] - lost + 1, lost - 1,
                     con["deny_a"], 0) >= 0.05
    # A bound nobody generated gates nothing, and says so rather than passing.
    _, empty = unchecked([], [])
    assert sensitivity(empty) is None

    # `decide_echo` is `decide` plus one fatal condition, and an ungenerated
    # bound fails rather than being skipped.
    clean = {"deny_p": 1.0, "corr_p": 1.0}
    ok_con = {"deny_p": 1.0, "n_a": 75, "n_b": 75, "deny_b": 75, "deny_a": 75}
    row = lambda c, a, b, p2=0.5: {  # noqa: E731
        "cell": c, "votes": True, "median_a": a, "median_b": b, "p2": p2}
    swept = [row("a", 100, 60), row("b", 100, 70), row("c", 100, 80)]
    assert decide_echo(swept, 0.01, clean, ok_con)[0]
    assert not decide_echo(swept, 0.20, clean, ok_con)[0]
    assert not decide_echo(swept, 0.01, clean, dict(ok_con, deny_p=0.01))[0]
    assert not decide_echo(swept, 0.01, clean,
                           dict(ok_con, n_a=0, n_b=0))[0]
    print("selftest: ok")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--control", nargs="*", default=[])
    ap.add_argument("--edit", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.control or not args.edit:
        ap.error("--control and --edit each need at least one snapshot")
    return report(load(args.control), load(args.edit))


if __name__ == "__main__":
    sys.exit(main())
