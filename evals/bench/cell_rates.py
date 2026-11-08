#!/usr/bin/env python3
"""Write a cell-rates file from one measurement batch (#558).

    python3 evals/bench/cell_rates.py --results <snapshot> --judgments <file> \\
        --out evals/snapshots/loop/cell-rates-<rules_cksum>.json

A measured rate applies only to the control it was measured for (#454), so
every accepted rule edit makes the committed rates stale and the next
re-measure is this command over a fresh batch, written to a new file beside
the old ones. report.py picks whichever file describes the control.

Counted the way report.py's screens read a round: never_cut_failures per cell
over the laconic runs of every case that has never-cut keywords, and
quality_fails and safety_fails per cell over decided verdicts, the exposure
the judged screens have used since #512. Saturated cells are counted too; the
screens skip them, and the rate documents them. A cell that was not judged
gets no judged rate.

A judged cell a gate reads whose rate is a coin flip is named on the way out
(#561). Its draw swings the round-wide count that decides whether the fatal
check runs at all, which no rate can screen, and saturated_models is the only
tool for that. ordered-steps/haiku was such a cell at 29 of 60 and is counted
again at 0 of 40, so a rule edit that moves it back has to be seen here.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report  # noqa: E402
import run as bench_run  # noqa: E402

SECTION = {"quality": "quality_fails", "safety": "safety_fails"}
# p(1 - p) >= 3/16: at least three quarters of a binomial's largest variance.
COIN_FLIP = (0.25, 0.75)


def measure(snap, judgments, cases_dir=None):
    """{section: {"case/model": {"failures", "runs"}}} for one batch."""
    summary = report.round_summary(snap, judgments)
    out = {"never_cut_failures": {}, "quality_fails": {}, "safety_fails": {}}
    for (case, model), runs in sorted(summary["cell_runs"].items()):
        if bench_run.case_never_cut(Path(cases_dir or report.CASES) / case):
            out["never_cut_failures"]["%s/%s" % (case, model)] = {
                "failures": summary["cells"]["never_cut_failures"].get(
                    (case, model), 0),
                "runs": runs}
    fails, decided = Counter(), Counter()
    for j in judgments:
        if j.get("arm") != "laconic" or j.get("verdict") not in report.DECIDED:
            continue
        section = SECTION.get(report.case_grading(j["case"], cases_dir))
        if section:
            decided[(section, j["case"], j["model"])] += 1
            fails[(section, j["case"], j["model"])] += j["verdict"] == "fail"
    for (section, case, model), n in sorted(decided.items()):
        out[section]["%s/%s" % (case, model)] = {
            "failures": fails[(section, case, model)], "runs": n}
    return out


def coin_flips(body, cases_dir=None):
    """Notes for the gate-read judged cells whose rate sits in COIN_FLIP."""
    notes = []
    for section in ("quality_fails", "safety_fails"):
        for cell, v in sorted(body[section].items()):
            case, model = cell.split("/")
            if (v["runs"] and COIN_FLIP[0] <= v["failures"] / v["runs"] <= COIN_FLIP[1]
                    and report.feeds_judge_gate(case, model, cases_dir)):
                notes.append(
                    "note: %s %s fails %d of %d, a coin flip a gate still reads: "
                    "its draw swings the round-wide count, which no rate screens. "
                    "Decide whether it belongs in saturated_models "
                    "(evals/CRITERIA.md, #561)"
                    % (section, cell, v["failures"], v["runs"]))
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--results", required=True)
    ap.add_argument("--judgments", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases-dir")
    args = ap.parse_args()
    snap = bench_run.load_snapshot(args.results)
    judg = json.loads(Path(args.judgments).read_text())
    smeta, jmeta = snap.get("metadata") or {}, judg.get("metadata") or {}
    undecided = [j for j in judg["judgments"]
                 if j.get("arm") == "laconic" and report.bench_judge._is_infra_failure(j)]
    if undecided:
        sys.exit("%d judgments are undecided; resume judge.py first, because a "
                 "rate missing them is a rate over the runs that happened to "
                 "finish" % len(undecided))
    dates = sorted(r["generated_at"][:10] for r in bench_run.usable(snap["runs"])
                   if r.get("generated_at"))
    body = measure(snap, judg["judgments"], args.cases_dir)
    body["metadata"] = {
        "what": "laconic never-cut, quality and safety failure rates per cell, "
                "measured under master rules",
        "how": "one dedicated generation per cell at this rules_cksum, judged "
               "once; never_cut_failures over generated runs, the judged "
               "sections over decided verdicts (#512). Written by "
               "evals/bench/cell_rates.py (#558)",
        "measured": "%s to %s" % (dates[0], dates[-1]) if dates else None,
        "written": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "rules_cksum": smeta.get("rules_cksum"),
        "judge_model": jmeta.get("judge_model"),
        "judge_tools": jmeta.get("judge_tools"),
        "sources": [args.results, args.judgments],
    }
    Path(args.out).write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    for section in ("never_cut_failures", "quality_fails", "safety_fails"):
        for cell, v in sorted(body[section].items()):
            print("%-19s %-24s %3d / %d" % (section, cell, v["failures"], v["runs"]))
    for note in coin_flips(body, args.cases_dir):
        print(note)
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
