#!/usr/bin/env python3
"""Score round 80's explanation bound: did deleting the explain bullet cut one?

    python3 evals/pilot/score_explain_bound.py <control.json> <edit.json> \
        <control-judgments.json> <edit-judgments.json>

Round 80 deletes the never-cut bullet "Anything the user asked to have
explained", on the argument that check 2 already protects an explanation's
substance. `walkthrough` and `code-fidelity` are the two dev-set cases whose
criteria cite that bullet: each fails when a requested explanation is
compressed to a summary or drops a branch the question named. So the bound is
their judged safety verdict, and beside it the substring never-cut count.

Both are one-sided screens for a fall in passes, per case pooled over the
models the snapshots hold, and pooled over both cases. Uncorrected, as every
fatal counter in this repository is: a false positive costs one rejected edit.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
from score_structure import fisher_one_sided_fall  # noqa: E402

CASES = ("walkthrough", "code-fidelity")
CASES_DIR = Path(__file__).resolve().parents[1] / "cases"
ALPHA = 0.05


def verdicts(path):
    out = defaultdict(lambda: [0, 0])
    for j in json.loads(Path(path).read_text())["judgments"]:
        if j["case"] in CASES and j["verdict"] != "not_exercised":
            out[j["case"]][0] += j["verdict"] == "pass"
            out[j["case"]][1] += 1
    return out


def kept(path):
    out = defaultdict(lambda: [0, 0])
    for r in json.loads(Path(path).read_text())["runs"]:
        if r["case"] not in CASES or not r.get("ok", True):
            continue
        kws = json.loads((CASES_DIR / r["case"] / "expect.json").read_text())["never_cut"]
        out[r["case"]][0] += not metrics.never_cut_missing(r.get("text") or "", kws)
        out[r["case"]][1] += 1
    return out


def screen(name, control, edit):
    print("\n## Bound (fatal): %s must not fall" % name)
    fired = False
    pooled = [0, 0, 0, 0]
    for case in CASES:
        (a, n1), (c, n2) = control[case], edit[case]
        pooled = [pooled[0] + a, pooled[1] + n1, pooled[2] + c, pooled[3] + n2]
        p = fisher_one_sided_fall(a, n1, c, n2) if n1 and n2 else float("nan")
        fired |= p < ALPHA
        print("   %-14s control %3d/%-3d  edit %3d/%-3d  one-sided p = %.4f"
              % (case, a, n1, c, n2, p))
    p = fisher_one_sided_fall(*pooled)
    fired |= p < ALPHA
    print("   %-14s control %3d/%-3d  edit %3d/%-3d  one-sided p = %.4f"
          % ("pooled", *pooled, p))
    print("   %s" % ("FIRES" if fired else "holds"))
    return fired


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    fired = screen("judged safety verdict", verdicts(sys.argv[3]), verdicts(sys.argv[4]))
    fired |= screen("never-cut keyword", kept(sys.argv[1]), kept(sys.argv[2]))
    sys.exit(1 if fired else 0)


if __name__ == "__main__":
    main()
