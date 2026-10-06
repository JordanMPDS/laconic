"""unread_asks on every accepted round since 28, from committed snapshots only.

Per-cell one_turn / unread_asks come from the shipped report.aggregate (which
calls the shipped asks_back); only the fixture filter and the tests are here.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import report  # noqa: E402

SNAP = ROOT / "evals" / "snapshots" / "loop"

# (round, label, control file(s), treatment file(s)). Merged files are used
# where a round committed one (they are the union of the per-model shards).
PAIRS = [
    ("28", "primary (design-*, sonnet)", ["round-28-control"], ["round-28-edit"]),
    ("28", "replication", ["round-28-repl-control"], ["round-28-repl-edit"]),
    ("28", "holdout", ["round-28-holdout-control"], ["round-28-holdout"]),
    ("55", "primary (conditional+general)", ["round-55-control"], ["round-55-edit"]),
    ("55", "wide (Bar A, 22 cases)", ["round-55-wide-control"], ["round-55-wide-edit"]),
    ("55", "holdout", ["round-55-holdout-control"], ["round-55-holdout"]),
    ("56", "55's edit on design-* (cost round)", ["round-56-control"], ["round-56-edit"]),
    ("71", "primary", ["round-71-control-1", "round-71-control-2"], ["round-71-edit-1", "round-71-edit-2"]),
    ("71", "replication", ["round-71-repl-control-1", "round-71-repl-control-2"], ["round-71-repl-edit-1", "round-71-repl-edit-2"]),
    ("71", "wide (Bar A)", ["round-71-wide-control"], ["round-71-wide-edit"]),
    ("71", "holdout", ["round-71-holdout-control"], ["round-71-holdout-edit"]),
    ("73", "primary", ["round-73-control-1", "round-73-control-2"], ["round-73-edit-1", "round-73-edit-2"]),
    ("73", "replication", ["round-73-repl-control-1", "round-73-repl-control-2"], ["round-73-repl-edit-1", "round-73-repl-edit-2"]),
    ("73", "wide (Bar A)", ["round-73-wide-control"], ["round-73-wide-edit"]),
    ("73", "holdout", ["round-73-holdout-control"], ["round-73-holdout-edit"]),
    ("81", "primary (opus, pilot deep/register)", ["round-81-control-opus"], ["round-81-edit-opus"]),
    ("81", "replication", ["round-81-rep-control-opus"], ["round-81-rep-edit-opus"]),
    ("81", "bound (walkthrough, code-fidelity)", ["round-81-control-bound"], ["round-81-edit-bound"]),
    ("81", "holdout", ["round-81-holdout-control"], ["round-81-holdout-edit"]),
    ("97", "primary (opus, pilot subset-*)", ["round-97-control"], ["round-97-edit"]),
    ("97", "replication", ["round-97-rep-control"], ["round-97-rep-edit"]),
    ("97", "spillover", ["round-97-spill-control"], ["round-97-spill-edit"]),
    ("97", "holdout", ["round-97-holdout-control"], ["round-97-holdout-edit"]),
    ("104", "primary (opus, pilot explain)", ["round-104-control"], ["round-104-edit"]),
    ("104", "replication", ["round-104-rep-control"], ["round-104-rep-edit"]),
    ("104", "walkthrough", ["round-104-walkthrough-control"], ["round-104-walkthrough-edit"]),
    ("104", "holdout", ["round-104-holdout-control"], ["round-104-holdout-edit"]),
]


def cases_dir(md):
    """The snapshot's own case tree, mapped back into this checkout."""
    p = Path(md.get("cases_dir") or "evals/cases")
    return ROOT / "evals" / p.name


def cells(names, arm="laconic"):
    """{model: [asks, one_turn]} under three filters.

    shipped: report.py's own filter, CASES/<case>/fixture.
    own:     the fixture check resolved against the snapshot's cases_dir, so
             pilot and holdout cases (holdout-design) are counted too.
    design:  shipped filter, design-* cases only.
    """
    out = {k: defaultdict(lambda: [0, 0]) for k in ("shipped", "own", "design")}
    meta = []
    for n in names:
        snap = json.loads((SNAP / f"{n}.json").read_text())
        md = snap.get("metadata", {})
        meta.append((n, md.get("rules_cksum"), md.get("claude_cli_version")))
        own = cases_dir(md)
        for (case, a, model), v in report.aggregate(snap).items():
            if a != arm:
                continue
            pair = (v.get("unread_asks", 0), v["one_turn"])
            hits = {"shipped": (report.CASES / case / "fixture").is_dir(),
                    "own": (own / case / "fixture").is_dir(),
                    "design": case.startswith("design-")
                    and (report.CASES / case / "fixture").is_dir()}
            for k, ok in hits.items():
                if ok:
                    out[k][model][0] += pair[0]
                    out[k][model][1] += pair[1]
    return out, meta


def hyper(k, n1, n2, t):
    """P(X = k) treatment asks, given t asks over n1 control + n2 treatment."""
    return math.comb(n2, k) * math.comb(n1, t - k) / math.comb(n1 + n2, t)


def fisher_greater(ac, nc, at, nt):
    """One-sided Fisher: treatment rate > control rate."""
    t = ac + at
    if nc == 0 or nt == 0 or t == 0:
        return None
    return min(1.0, sum(hyper(k, nc, nt, t) for k in range(at, min(t, nt) + 1)))


def stratified_greater(strata):
    """Exact conditional test of a common odds ratio > 1 across strata.

    The treatment-ask total, conditional on every stratum's margins, is the
    convolution of the per-stratum hypergeometrics.
    """
    dist = {0: 1.0}
    obs = 0
    for ac, nc, at, nt in strata:
        t = ac + at
        if nc == 0 or nt == 0 or t == 0:
            continue
        obs += at
        lo, hi = max(0, t - nc), min(t, nt)
        pk = {k: hyper(k, nc, nt, t) for k in range(lo, hi + 1)}
        new = defaultdict(float)
        for s, ps in dist.items():
            for k, p in pk.items():
                new[s + k] += ps * p
        dist = new
    if len(dist) == 1:
        return None
    return min(1.0, sum(p for s, p in dist.items() if s >= obs))


def fmt(a, n):
    return f"{a}/{n} ({100 * a / n:.1f}%)" if n else f"{a}/0 (-)"


def pstr(p):
    return "-" if p is None else f"{p:.4f}"


def compare(label, c_names, t_names, arm_c="laconic", arm_t="laconic"):
    c, cm = cells(c_names, arm_c)
    t, tm = cells(t_names, arm_t)
    print(f"\n{label}")
    for n, ck, cli in cm + tm:
        print(f"    {n}: rules {ck}, {cli}")
    for filt in ("shipped", "own", "design"):
        models = sorted(set(c[filt]) | set(t[filt]))
        strata = [(*c[filt][m], *t[filt][m]) for m in models]
        strata = [(s[0], s[1], s[2], s[3]) for s in strata]
        ac = sum(s[0] for s in strata); nc = sum(s[1] for s in strata)
        at = sum(s[2] for s in strata); nt = sum(s[3] for s in strata)
        if nc == 0 and nt == 0:
            print(f"  [{filt}] no one-turn responses on fixture cases")
            continue
        print(f"  [{filt}] pooled control {fmt(ac, nc)}  treatment {fmt(at, nt)}  "
              f"Fisher p(T>C) {pstr(fisher_greater(ac, nc, at, nt))}  "
              f"stratified-by-model p {pstr(stratified_greater(strata))}")
        if len(models) > 1:
            for m, s in zip(models, strata):
                print(f"      {m}: control {fmt(s[0], s[1])}  treatment {fmt(s[2], s[3])}  "
                      f"p {pstr(fisher_greater(*s))}")


def selfcheck():
    # Ledger: round 28 target 70/165 to 43/153.
    c, _ = cells(["round-28-control"]); t, _ = cells(["round-28-edit"])
    assert c["shipped"]["sonnet"] == [70, 165] and t["shipped"]["sonnet"] == [43, 153]
    # Fisher sanity: identical arms give p well above 0.5; 2x2 by hand.
    assert abs(fisher_greater(1, 2, 2, 2) - 0.5) < 1e-12
    # Stratification over one stratum equals plain Fisher.
    assert abs(stratified_greater([(30, 112, 44, 137)]) - fisher_greater(30, 112, 44, 137)) < 1e-12


if __name__ == "__main__":
    selfcheck()
    for rnd, label, cn, tn in PAIRS:
        compare(f"round {rnd} - {label}", cn, tn)

    print("\n\n=== drift: master-rules design-* generations against round 28's treatment ===")
    drift = [
        ("round 28 treatment (rules 136269960)", ["round-28-edit"], "laconic"),
        ("round 28 replication treatment", ["round-28-repl-edit"], "laconic"),
        ("round 55 wide control (rules 136269960)", ["round-55-wide-control"], "laconic"),
        ("round 56 control (rules 136269960)", ["round-56-control"], "laconic"),
        ("round 56 edit = master 594915793", ["round-56-edit"], "laconic"),
        ("round 73 wide edit = master 3285158247", ["round-73-wide-edit"], "laconic"),
        ("round 77 laconic arm (master 3285158247)", ["round-77-design-0", "round-77-design-34", "round-77-design-67"], "laconic"),
        ("round 78 laconic arm (master 3285158247)", ["round-78-design-0", "round-78-design-34", "round-78-design-67"], "laconic"),
        ("benchmark-2026-09-24 laconic (master 288018845)", ["benchmark-2026-09-24"], "laconic"),
        ("round 90 laconic arm (master 288018845)", ["round-90-design-0", "round-90-design-34", "round-90-design-67", "round-90-opus"], "laconic"),
        ("round 102 control (master 3660436060)", ["round-102-control"], "laconic"),
    ]
    for label, names, arm in drift:
        d, meta = cells(names, arm)
        clis = sorted(set(m[2] for m in meta))
        per = {m: fmt(*v) for m, v in sorted(d["design"].items())}
        print(f"  {label} [{', '.join(clis)}]: design-* {per}")

    print("\n  sonnet design-*, round 28 treatment vs later master arms, one-sided each way:")
    base, _ = cells(["round-28-edit"])
    b = base["design"]["sonnet"]
    for label, names, arm in drift[2:]:
        d, _ = cells(names, arm)
        if "sonnet" not in d["design"] or d["design"]["sonnet"][1] == 0:
            print(f"    {label}: no sonnet exposure")
            continue
        x = d["design"]["sonnet"]
        print(f"    {label}: {fmt(*x)} vs {fmt(*b)}  p(later>r28) {pstr(fisher_greater(b[0], b[1], x[0], x[1]))}"
              f"  p(later<r28) {pstr(fisher_greater(x[0], x[1], b[0], b[1]))}")
