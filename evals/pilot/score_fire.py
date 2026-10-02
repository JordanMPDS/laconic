#!/usr/bin/env python3
"""Round 91: which open `rules` issue still fires at master rules?

    python3 evals/pilot/score_fire.py evals/snapshots/loop/round-91-*.json
    python3 evals/pilot/score_fire.py --selftest

Rounds 88, 89 and 90 each bought a candidate whose defect was absent from its
own control under the CLI of the day. This reads one cell per issue, laconic
only, on the model the issue was observed on, and says whether each defect
clears the threshold registered in `round-91.md`. Every counter is an existing
deterministic one; nothing here is judged.

The ranking is the margin, observed over threshold in the issue's own units,
because the four counters share no scale. Ties go to the larger n.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
from score_closing_edit import hits  # noqa: E402
from score_compression import words  # noqa: E402
from score_volunteered import edited  # noqa: E402

MODEL = "opus"
SETTLED = ("settled-failover", "settled-retention", "settled-rounding")
TURN_3 = 2  # edit-service's walk-through turn, the one #113 breaks on

# issue: (cases, threshold k, what is counted, per-run predicate)
ISSUES = {
    "#305": (SETTLED, 9, "settled answers over 80 prose words",
             lambda r: words(r) > 80),
    "#116": (("conditional",), 5, "conditional runs that edited a file",
             edited),
    "#113": (("edit-service",), 3, "edit-service turn 3 closing offers",
             lambda r: len(r.get("turns") or []) > TURN_3
             and bool(hits(r["turns"][TURN_3]))),
    "#46": (("design-alerting",), 2, "design-alerting over 600 prose words",
            lambda r: words(r) > 600),
}


def load(paths):
    """Usable laconic runs on MODEL, one per generation key."""
    seen, out = set(), []
    for p in paths:
        for r in json.loads(Path(p).read_text())["runs"]:
            key = (r.get("case"), r.get("model"), r.get("arm"), r.get("rep"))
            if (key in seen or not r.get("ok") or r.get("arm") != "laconic"
                    or r.get("model") != MODEL):
                continue
            seen.add(key)
            out.append(r)
    return out


def score(runs):
    """One row per issue: (issue, k, n, threshold, fires, margin, label, median)."""
    rows = []
    for issue, (cases, need, label, pred) in ISSUES.items():
        rs = [r for r in runs if r.get("case") in cases]
        k = sum(1 for r in rs if pred(r))
        rows.append((issue, k, len(rs), need, bool(rs) and k >= need,
                     k / need, label, metrics.median([words(r) for r in rs])))
    return sorted(rows, key=lambda x: (-x[5], -x[2]))


def main(paths):
    rows = score(load(paths))
    print("%-6s %-38s %8s %6s %6s %6s %s"
          % ("issue", "counted", "k/n", "need", "margin", "median", "fires"))
    for issue, k, n, need, fires, margin, label, med in rows:
        print("%-6s %-38s %8s %6d %6.2f %6.1f %s"
              % (issue, label, "%d/%d" % (k, n), need, margin, med,
                 "FIRES" if fires else "no"))
    if any(n == 0 for _, _, n, *_ in rows):
        print("\nwarning: an issue has no runs; check the snapshot list")
    firing = [r[0] for r in rows if r[4]]
    print("\nround 92 takes: %s" % (firing[0] if firing else "none fires"))


def selftest():
    def run(case, text, tools=(), turns=None):
        r = {"case": case, "model": MODEL, "arm": "laconic", "ok": True,
             "text": text, "tools": list(tools)}
        if turns is not None:
            r["turns"] = [{"text": t, "tools": []} for t in turns]
        return r

    long_, short = "word " * 90, "Yes."
    offer = "It rolls back. Would you like me to fix it?"
    runs = ([run("settled-failover", long_)] * 9 + [run("settled-rounding", short)]
            + [run("conditional", short, ["Edit"])] * 4
            + [run("edit-service", "", turns=["a", "b", offer, "c", "d"])] * 6
            + [run("design-alerting", "word " * 700)])
    rows = {r[0]: r for r in score(runs)}
    assert rows["#305"][1:5] == (9, 10, 9, True), rows["#305"]
    assert rows["#116"][1:5] == (4, 4, 5, False), rows["#116"]
    assert rows["#113"][1:5] == (6, 6, 3, True), rows["#113"]
    assert rows["#46"][1:5] == (1, 1, 2, False), rows["#46"]
    assert score(runs)[0][0] == "#113"  # margin 2.0 beats #305's 1.0
    other = dict(runs[0], model="sonnet", rep=99)
    assert other not in load_list([other])
    print("selftest ok")


def load_list(runs):
    """load() over in-memory runs, for the selftest."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"runs": runs}, f)
    try:
        return load([f.name])
    finally:
        Path(f.name).unlink()


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:]:
        main(sys.argv[1:])
    else:
        sys.exit(__doc__)
