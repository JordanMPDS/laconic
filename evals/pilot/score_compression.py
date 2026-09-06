#!/usr/bin/env python3
"""Round 51's target: does the pre-action check compress a diagnostic answer?

    python3 evals/pilot/score_compression.py <edit> --against <control>

[Round 50](../results/loop/round-50.md) registered the check at
`rules/laconic.md:7-10` against the edit rate on `conditional`, read a null,
and disclosed - uncredited, because it was unregistered - that the same edit
moved prose length hard in both strata, at permutation p < 0.00001 on 120 runs
a side with both of its bounds perfect. This script is what lets a round
register that effect instead of narrating it afterwards.

Four cases, all sonnet, all handed a fixture that hides a defect:

- `conditional` is round 50's own cell and the replication. It is the one case
  in the suite that admits an edit, so it is scored **inside the answering
  stratum**: a cell mixing editing and non-editing answers has a median that
  tracks its edit rate rather than its compression, which is [#209] and which
  on this case produces a clean Simpson's reversal.
- `fail-open`, `silent-success` and `stale-cache` are the generalisation. Each
  asks "read them and tell me why X" and ends `Don't edit anything.`, so no run
  should edit and the [#209] mixture cannot arise - if one does, the cell is
  reported mixed and does not score, rather than being quietly pooled.

Words are prose words by `metrics.split_text`, so fenced code and inline spans
are out of the count. That is the same counter every length claim in the loop
is made on, and it is what makes round 50's disclosed table reproducible here.

**Why a permutation on medians and not `report.py --target output_tokens`.**
The gate scopes by case/model cell and needs at least six of them; this scope
has four, one of which `report.py` refuses outright under the [#209] mixture
rule. Round 50 named both obstacles in advance and said such a round "has to
score the answering stratum directly the way this table does".

The bounds are what stop the target being won by saying less rather than by
saying it shorter. `locates_defect` is round 50's content bound, unchanged and
imported rather than reimplemented. The reading rate is the other: laconic's
whole quality axis is whether a file was opened, and an answer that stopped
opening `db.js` would read as excellent compression on every counter here.

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#209]: https://github.com/JordanMPDS/laconic/issues/209
"""
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
import subagent  # noqa: E402

from score_volunteered import edited, grounded, locates_defect  # noqa: E402

SEED = 51

#: `conditional` is scored inside its answering stratum; the other three admit
#: no edit at all. The order is the order the round registered them in.
STRATIFIED = "conditional"
GENERAL = ("fail-open", "silent-success", "stale-cache")
CASES = (STRATIFIED,) + GENERAL

#: At least this many of the three generalisation cases must fall for the
#: round's second registered claim to hold. Registered before the batch ran.
GENERAL_BAR = 2


def words(run):
    """Prose words in the response: fenced blocks, inline code and URLs out."""
    prose, _ = metrics.split_text(run.get("text") or "")
    return len(metrics.WORD.findall(prose))


def rows(runs, case):
    return [r for r in bench_run.usable(runs) if r.get("case") == case]


def cell(runs, case):
    """Everything the round reads off one case's runs on one side.

    `scored` is the stratum the words are counted over: the answering runs on
    `conditional`, every run on the three that forbid an edit. `edits` is
    reported for all four because it is the [#209] guard - a non-zero count on
    a `Don't edit anything.` case means that cell is mixed and must not score.
    """
    rs = rows(runs, case)
    scored = [r for r in rs if not edited(r)] if case == STRATIFIED else rs
    return {
        "n": len(rs),
        "edits": sum(1 for r in rs if edited(r)),
        "grounded": sum(1 for r in rs if grounded(r)),
        "words": [words(r) for r in scored],
        "locates": sum(1 for r in scored if locates_defect(r.get("text", ""))),
        "scored_n": len(scored),
    }


def compare(edit_runs, control_runs, resamples=200000):
    """One row per case: medians, direction, and a permutation p on medians."""
    out = []
    for case in CASES:
        e, c = cell(edit_runs, case), cell(control_runs, case)
        mixed = case != STRATIFIED and (e["edits"] or c["edits"])
        p = None if mixed else metrics.permutation(
            c["words"], e["words"], SEED, resamples, stat=statistics.median)
        out.append({
            "case": case,
            "edit": e,
            "control": c,
            "mixed": bool(mixed),
            "median_edit": metrics.median(e["words"]),
            "median_control": metrics.median(c["words"]),
            "p": p,
        })
    return out


def bounds(edit_runs, control_runs):
    """The two content bounds, Fisher two-sided, edit against control.

    A bound is directional in what it means and not in how it is tested: one
    that spent half its alpha proving an improvement would be reporting the
    target twice. That is `score_volunteered.compare`'s rule and this keeps it.
    """
    out = []
    ce, cc = cell(edit_runs, STRATIFIED), cell(control_runs, STRATIFIED)
    out.append(("locates_defect | did not edit (%s)" % STRATIFIED,
                ce["locates"], ce["scored_n"], cc["locates"], cc["scored_n"]))
    for case in CASES:
        e, c = cell(edit_runs, case), cell(control_runs, case)
        out.append(("read the fixture (%s)" % case,
                    e["grounded"], e["n"], c["grounded"], c["n"]))
    return [(label, ek, en, ck, cn,
             subagent.fisher_exact(ek, en - ek, ck, cn - ck))
            for label, ek, en, ck, cn in out]


def verdict(cases, bound_rows):
    """(accepted, reasons) under the bars round 51 registered.

    Registered: the `conditional` replication falls at p < 0.05, at least two
    of the three generalisation cases fall at p < 0.05, and no bound falls at
    p < 0.05. A rise anywhere is not a fall; a mixed cell does not score.
    """
    reasons = []
    fell = {r["case"]: (r["p"] is not None and r["p"] < 0.05
                        and r["median_edit"] < r["median_control"])
            for r in cases}
    for r in cases:
        if r["mixed"]:
            reasons.append("%s is mixed (%d edits) and does not score"
                           % (r["case"], r["edit"]["edits"] + r["control"]["edits"]))
    if not fell[STRATIFIED]:
        reasons.append("%s did not fall at p < 0.05" % STRATIFIED)
    n_general = sum(1 for c in GENERAL if fell[c])
    if n_general < GENERAL_BAR:
        reasons.append("%d of 3 generalisation cases fell, bar is %d"
                       % (n_general, GENERAL_BAR))
    for label, ek, en, ck, cn, p in bound_rows:
        if p < 0.05 and en and cn and (ek / en) < (ck / cn):
            reasons.append("bound fell: %s (p = %.4f)" % (label, p))
    return not reasons, reasons


def fmt_p(p):
    if p is None:
        return "-"
    return "< 0.00001" if p < 1e-5 else "%.5f" % p


def render(edit_path, control_path, resamples=200000):
    def runs(path):
        return json.loads(Path(path).read_text())["runs"]

    e_runs, c_runs = runs(edit_path), runs(control_path)
    cases = compare(e_runs, c_runs, resamples)
    bound_rows = bounds(e_runs, c_runs)

    print("edit    %s" % Path(edit_path).name)
    print("control %s\n" % Path(control_path).name)
    print("  %-16s %-10s %-18s %-18s %s"
          % ("case", "stratum", "control median", "edit median", "p"))
    for r in cases:
        stratum = "answered" if r["case"] == STRATIFIED else "all"
        print("  %-16s %-10s %-18s %-18s %s"
              % (r["case"], stratum,
                 "%.1f (n=%d)" % (r["median_control"], r["control"]["scored_n"]),
                 "%.1f (n=%d)" % (r["median_edit"], r["edit"]["scored_n"]),
                 "mixed" if r["mixed"] else fmt_p(r["p"])))

    print("\n  %-42s %-16s %-16s %s" % ("bound", "edit", "control", "p"))
    for label, ek, en, ck, cn, p in bound_rows:
        print("  %-42s %-16s %-16s %.4f"
              % (label,
                 "%d/%d" % (ek, en) if en else "-",
                 "%d/%d" % (ck, cn) if cn else "-", p))

    ok, reasons = verdict(cases, bound_rows)
    print("\n  %s" % ("ACCEPT on the registered bars" if ok else "REJECT"))
    for reason in reasons:
        print("    - %s" % reason)
    return cases, bound_rows, ok


def main():
    if len(sys.argv) != 4 or sys.argv[2] != "--against":
        sys.exit(__doc__)
    _, _, ok = render(sys.argv[1], sys.argv[3])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
