"""The permutation that refutes the key-level reading of round 28's strata.

Shuffles the edit arm's runs WITHIN each case, destroying any key-level
correspondence with the control arm while preserving every marginal: each
case's edit hands-back share and its failure rate are untouched. If the
observed per-group deltas survive the shuffle they are an effect; if the
shuffle reproduces them they are the artifact of conditioning on the control
arm's own noise.

Reproduces the table in ../round-28-composition.md from the committed
snapshots. Deterministic: seed 28, 2000 shuffles.

    python3 evals/results/loop/round-28-composition/permute.py
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import report  # noqa: E402
import run as bench_run  # noqa: E402

SNAP = ROOT / "evals" / "snapshots" / "loop"
CASES = {"design-alerting", "design-audit-log", "design-cache",
         "design-rate-limit", "design-realtime", "design-retry",
         "design-search", "design-upload"}
GROUPS = ("always resolved", "into resolving", "into hands-back",
          "always handed back")


def load(side):
    snap = json.loads((SNAP / ("round-28-%s.json" % side)).read_text())
    jd = json.loads((SNAP / ("round-28-%s-judgments.json" % side)).read_text())
    jj = jd["judgments"] if isinstance(jd, dict) else jd
    verdict = {(j["case"], j["model"], j["rep"]): j["verdict"] for j in jj
               if j.get("arm") == "laconic"}
    out = {}
    for r in bench_run.usable(snap["runs"]):
        if r["arm"] != "laconic" or r["model"] != "sonnet" or r["case"] not in CASES:
            continue
        k = (r["case"], r["model"], r["rep"])
        if k in verdict:
            out[k] = {"back": report.asks_back(r.get("text", "")),
                      "fail": verdict[k] == "fail"}
    return out


def table(ctrl, edit, keys):
    g = {n: [] for n in GROUPS}
    for k in keys:
        c, e = ctrl[k]["back"], edit[k]["back"]
        name = ("always handed back" if c and e else
                "into resolving" if c and not e else
                "into hands-back" if e and not c else "always resolved")
        g[name].append((ctrl[k]["fail"], edit[k]["fail"]))
    return {n: (len(v), sum(a for a, _ in v), sum(b for _, b in v))
            for n, v in g.items()}


def main():
    random.seed(28)
    ctrl, edit = load("control"), load("edit")
    keys = sorted(set(ctrl) & set(edit))
    obs = table(ctrl, edit, keys)

    print("OBSERVED")
    for n in GROUPS:
        c, a, b = obs[n]
        print("  %-20s n=%3d  control %2d (%5.1f%%)  edit %2d (%5.1f%%)  delta %+d"
              % (n, c, a, 100.0 * a / c, b, 100.0 * b / c, b - a))

    by_case = {}
    for k in keys:
        by_case.setdefault(k[0], []).append(k)
    deltas = {n: [] for n in GROUPS}
    for _ in range(2000):
        shuffled = {}
        for ks in by_case.values():
            vals = [edit[k] for k in ks]
            random.shuffle(vals)
            shuffled.update(zip(ks, vals))
        t = table(ctrl, shuffled, keys)
        for n, (_, a, b) in t.items():
            deltas[n].append(b - a)

    print("\nPERMUTATION (2000 shuffles within case; all marginals preserved)")
    for n in GROUPS:
        c, a, b = obs[n]
        d = sorted(deltas[n])
        lo, hi = d[int(0.025 * len(d))], d[int(0.975 * len(d))]
        verdict = ("INSIDE the null band - artifact"
                   if lo <= (b - a) <= hi else "outside the null band")
        print("  %-20s observed %+3d   null mean %+6.1f  95%% band [%+d, %+d]   %s"
              % (n, b - a, sum(d) / len(d), lo, hi, verdict))


if __name__ == "__main__":
    main()
