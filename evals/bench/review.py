#!/usr/bin/env python3
"""The failure inventory: what failed, and which rule was supposed to prevent it.

Offline, no calls. This is the loop's read step - the input a rule edit gets
proposed from. Every entry carries the failing excerpt verbatim and the line
from rules/laconic.md that governs it.

A failure with no governing rule ranks first. That the rule set is silent where
the benchmark expects it to speak is a more useful finding than another
instance of a rule being disobeyed, and it is the only class of finding that
points at writing a rule rather than editing one.

Only the treatment arm is reviewed. No control carries rules in its system
prompt, so a control's failure is not actionable and reviewing it would pad the
inventory with entries no rule edit can fix.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
import report as bench_report  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RULES = ROOT / "rules" / "laconic.md"

CLASS_ORDER = ("unruled", "never-cut", "quality", "readability", "preference")

# Failure kind -> a phrase appearing in the rule meant to prevent it. An
# explicit table rather than inference: a wrong attribution aims the next rule
# edit at the wrong line, and there are only four kinds to enumerate. A kind
# absent from this table has no governing rule by definition, which is what
# puts quality and preference failures in the "unruled" class.
RULE_PHRASES = {
    "never_cut": "verbatim",
    "symbol_connectors": "arrow",
    "abbreviated_prose": "shorten words",
    "sentence_initial_lowercase": "articles",
}


def governing_rule(rules_text, kind):
    """(line number, line) of the rule governing this failure kind, or None."""
    phrase = RULE_PHRASES.get(kind)
    if not phrase:
        return None
    for i, line in enumerate(rules_text.splitlines(), 1):
        if phrase in line.lower():
            return (i, line.strip())
    return None


def _case_expect(case):
    p = CASES / case / "expect.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _optimizable(case):
    """A rule-adherence case may not be an optimization target: tuning the
    rules against a case that grades adherence to those rules is circular.
    Read from the case's own grading field rather than a list kept here, so the
    two cannot drift."""
    return bench_report.case_grading(case) != "rule-adherence"


def _finding(cls, case, model, rep, excerpt, rule):
    return {"class": cls, "case": case, "model": model, "rep": rep,
            "excerpt": excerpt, "rule": rule, "optimizable": _optimizable(case)}


def findings(snap, judg, prefs, rules_text):
    """Ranked failures over the treatment arm of one round."""
    out = []
    for r in bench_run.usable(snap.get("runs", [])):
        if r["arm"] != "laconic":
            continue
        case = r["case"]
        expect = _case_expect(case)
        # The graded response is what the model said plus, for a case whose
        # deliverable is a file, what it wrote (#150).
        text = metrics.graded_text(r, expect)

        for kw in metrics.never_cut_missing(text, expect.get("never_cut", [])):
            out.append(_finding("never-cut", case, r["model"], r["rep"],
                                "missing: %s" % kw,
                                governing_rule(rules_text, "never_cut")))

        scored = metrics.score(text)
        for kind in ("symbol_connectors", "abbreviated_prose",
                     "sentence_initial_lowercase"):
            if not scored[kind]:
                continue
            rule = governing_rule(rules_text, kind)
            out.append(_finding("readability" if rule else "unruled", case,
                                r["model"], r["rep"],
                                "; ".join(scored["spans"][:3]), rule))

    # A judge failure is classed quality whether or not a rule governs it. Only
    # a rule-class failure - never-cut, readability - can be "unruled", because
    # only there does a missing rule mean the rule set is silent where the
    # benchmark checks. Classing every wrong answer as unruled would bury that
    # signal under the largest category in the run.
    for j in judg or []:
        if j.get("arm") != "laconic" or j.get("verdict") != "fail":
            continue
        out.append(_finding("quality", j["case"], j["model"], j["rep"],
                            j.get("quote") or j.get("reason", ""), None))

    for p in prefs or []:
        if p.get("order") != 0 or p.get("winner_arm") in (None, "tie", "laconic"):
            continue
        out.append(_finding("preference", p["case"], p["model"], p["rep"],
                            p.get("reason", ""), None))

    return sorted(out, key=lambda f: (CLASS_ORDER.index(f["class"]), f["case"],
                                      f["model"], f["rep"]))


def render(found):
    lines = ["# Failure inventory", ""]
    if not found:
        lines += ["No failures. Nothing to propose from this round."]
        return "\n".join(lines)
    for cls in CLASS_ORDER:
        rows = [f for f in found if f["class"] == cls]
        if not rows:
            continue
        # Findings and responses are different counts: one response missing two
        # never-cut keywords is two findings here and one failure in report.py.
        # Both are printed so the difference reads as arithmetic rather than as
        # two modules disagreeing.
        responses = len(set((f["case"], f["model"], f["rep"]) for f in rows))
        lines += ["## %s (%d finding(s) across %d response(s))"
                  % (cls, len(rows), responses), ""]
        for f in rows:
            rule = ("rules/laconic.md:%d - %s" % f["rule"]) if f["rule"] \
                else "**no governing rule**"
            flag = "" if f["optimizable"] else \
                " _(rule-adherence case: not an optimization target)_"
            lines += ["- `%s`/%s rep%d%s" % (f["case"], f["model"], f["rep"], flag),
                      "  - excerpt: %s" % f["excerpt"],
                      "  - rule: %s" % rule]
        lines.append("")
    return "\n".join(lines)


def main():
    global CASES
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--judgments")
    ap.add_argument("--preferences")
    ap.add_argument("--rules", default=str(RULES))
    ap.add_argument("--cases-dir", default=str(CASES))
    args = ap.parse_args()

    CASES = Path(args.cases_dir)
    bench_report.CASES = CASES

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s" % args.results)
    judg = (bench_run.load_snapshot(args.judgments) or {}).get("judgments", []) \
        if args.judgments else []
    prefs = (bench_run.load_snapshot(args.preferences) or {}).get("comparisons", []) \
        if args.preferences else []
    print(render(findings(snap, judg, prefs, Path(args.rules).read_text())))


if __name__ == "__main__":
    main()
