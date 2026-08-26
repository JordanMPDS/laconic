#!/usr/bin/env python3
"""#146: the archive re-scored with the hands-back detector swapped.

Regenerates every table in `../unread-asks.md` under both detectors: the
between-round dispersion, the false-accept rate, the separation across rules
texts, round 20 against its neighbours, and the strata disclosures rounds 25,
26 and 27 published. Stored snapshots only, no model calls.

v1 is the line-terminal regex that shipped until the promotion; v2 is
`detector_v2.py` beside this file, which `report.asks_back` now implements.
Running it against a `report.py` whose detector has moved on will print v2 as
whatever ships, which is the point: the v1 column is what the round docs were
written with and it does not change.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import report  # noqa: E402
import detector_v2  # noqa: E402

SNAP = ROOT / "evals" / "snapshots" / "loop"
CASES = ROOT / "evals" / "cases"

# Independence rules, from unread-asks.md.
EXCLUDE = {
    "round-01-n10", "round-01-n10-v2", "round-01-n10-v3",   # prefixes of -v4
    "round-21", "round-22",                                  # subsets of -n10
    "round-25-arbitration", "round-10-replication",          # biased redraws
}
V1 = report.ASKS_BACK
DETECTORS = {"v1": lambda t: bool(V1.search(t)),
             "v2": detector_v2.asks_back}


def rows(model="sonnet"):
    out = []
    for p in sorted(SNAP.glob("round-*.json")):
        name = p.stem
        if name.endswith(("-judgments", "-preferences")) or name in EXCLUDE:
            continue
        if "holdout" in name:
            continue
        d = json.loads(p.read_text())
        if "runs" not in d:
            continue
        runs = [r for r in d["runs"]
                if r.get("arm") == "laconic" and r.get("ok")
                and r.get("model") == model
                and r["case"].startswith("design-")
                and (CASES / r["case"] / "fixture").is_dir()]
        if not runs:
            continue
        unread = [r for r in runs if r.get("num_turns") == 1]
        row = {"name": name, "cksum": d["metadata"].get("rules_cksum"),
               "date": d["metadata"].get("generated_at", "")[:10],
               "scope": len(set(r["case"] for r in runs)),
               "n": len(runs), "one_turn": len(unread)}
        for k, fn in DETECTORS.items():
            row[k] = sum(1 for r in unread if fn(r.get("text", "")))
        out.append(row)
    return out


def groups(rs):
    """Rounds sharing a rules text AND a case-scope size, two or more."""
    g = defaultdict(list)
    for r in rs:
        g[(r["cksum"], r["scope"])].append(r)
    return {k: v for k, v in sorted(g.items()) if len(v) > 1}


def dispersion(g, det):
    """Chi-square of the per-group rate table, and phi = chi2 / df."""
    chi2 = df = 0.0
    lines = []
    for (ck, scope), rs in g.items():
        tot_a = sum(r[det] for r in rs)
        tot_n = sum(r["one_turn"] for r in rs)
        if not tot_n or not tot_a:
            lines.append((ck, scope, len(rs), tot_a, tot_n, 0.0, len(rs) - 1))
            df += len(rs) - 1
            continue
        p = tot_a / tot_n
        c = sum((r[det] - r["one_turn"] * p) ** 2 / (r["one_turn"] * p * (1 - p))
                for r in rs if r["one_turn"] and 0 < p < 1)
        chi2 += c
        df += len(rs) - 1
        lines.append((ck, scope, len(rs), tot_a, tot_n, c, len(rs) - 1))
    return lines, chi2, df


def fell(a, n_a, b, n_b):
    """One-sided p that the rate FELL from (a of n_a) to (b of n_b).

    report._count_p, the same test the gate scores a count target with, so
    every figure here is comparable with what the round docs published.
    """
    return report._count_p(a, b, n_a, n_b)


def rose(a, n_a, b, n_b):
    """One-sided p that the rate ROSE from (a of n_a) to (b of n_b)."""
    return report._count_p(b, a, n_b, n_a)


def false_accepts(g, det):
    """Ordered pairs at identical rules text and scope that reach alpha."""
    hits, total = [], 0
    for (ck, scope), rs in g.items():
        for x in rs:
            for y in rs:
                if x is y:
                    continue
                total += 1
                p = fell(x[det], x["one_turn"], y[det], y["one_turn"])
                if p < 0.05:
                    hits.append((x["name"], y["name"], p))
    return hits, total


if __name__ == "__main__":
    rs = rows()
    print("%-26s %-11s %-11s %5s %5s %8s %5s %5s"
          % ("snapshot", "cksum", "date", "scope", "n", "one_turn", "v1", "v2"))
    for r in rs:
        print("%-26s %-11s %-11s %5d %5d %8d %5d %5d"
              % (r["name"], r["cksum"], r["date"], r["scope"], r["n"],
                 r["one_turn"], r["v1"], r["v2"]))

    g = groups(rs)
    for det in DETECTORS:
        print("\n=== dispersion, %s ===" % det)
        lines, chi2, df = dispersion(g, det)
        for ck, scope, k, a, n, c, d in lines:
            print("  %-11s scope %d  %d rounds  %3d/%-4d  chi2 %6.2f  df %d"
                  % (ck, scope, k, a, n, c, d))
        print("  pooled: chi2 %.2f on %d df, phi = %.2f"
              % (chi2, df, chi2 / df if df else 0))
        hits, total = false_accepts(g, det)
        print("  false accepts: %d of %d pairs (%.1f%%)"
              % (len(hits), total, 100 * len(hits) / total if total else 0))
        for a, b, p in hits:
            print("    %s -> %s  p = %.4f" % (a, b, p))


# --- what promoting the detector moves in the published disclosures --------

PAIRS = [("round-25", "round-25-control", "round-25-licence"),
         ("round-25 replication", "round-25-control", "round-25-arbitration"),
         ("round-26", "round-26-control", "round-26-licence"),
         ("round-27", "round-27-control", "round-27-edit")]


def strata(snap_name, det_fn):
    """report._quality_strata with the detector swapped."""
    snap = json.loads((SNAP / (snap_name + ".json")).read_text())
    jp = SNAP / (snap_name + "-judgments.json")
    judg = json.loads(jp.read_text())["judgments"] if jp.exists() else []
    old = report.asks_back
    report.asks_back = det_fn
    try:
        return report._quality_strata(judg, snap["runs"])
    finally:
        report.asks_back = old


def covariate(snap_name, det_fn, model="sonnet"):
    """Hands-back counts split on whether the answer read anything."""
    snap = json.loads((SNAP / (snap_name + ".json")).read_text())
    runs = [r for r in snap["runs"]
            if r.get("arm") == "laconic" and r.get("ok")
            and r.get("model") == model and r["case"].startswith("design-")]
    asks = [r for r in runs if det_fn(r.get("text", ""))]
    unread = [r for r in asks if r.get("num_turns") == 1]
    return {"n": len(runs), "asks": len(asks), "unread_asks": len(unread),
            "read_asks": len(asks) - len(unread),
            "one_turn": sum(1 for r in runs if r.get("num_turns") == 1)}


def strata_report():
    for det, fn in DETECTORS.items():
        print("\n=== published disclosures, %s ===" % det)
        for label, ctrl, treat in PAIRS:
            for name in (ctrl, treat):
                s = strata(name, fn)
                c = covariate(name, fn)
                print("  %-22s hands-back fails %2d/%-3d  resolves %3d/%-3d  "
                      "share %3d/%-3d  unread_asks %2d/%-3d"
                      % (name, s["asks"]["fails"], s["asks"]["n"],
                         s["resolves"]["fails"], s["resolves"]["n"],
                         c["asks"], c["n"], c["unread_asks"], c["one_turn"]))
            a, b = covariate(ctrl, fn), covariate(treat, fn)
            print("    %s  share fall p = %.4f ; unread-conditional p = %.4f"
                  % (label,
                     fell(a["asks"], a["n"], b["asks"], b["n"]),
                     fell(a["unread_asks"], a["one_turn"],
                          b["unread_asks"], b["one_turn"])))


def separation(rs):
    """Conditional rate by rules text, eight-case design scope."""
    for det in DETECTORS:
        print("\n=== separation by rules text (scope 8), %s ===" % det)
        by = defaultdict(lambda: [0, 0])
        for r in rs:
            if r["scope"] != 8:
                continue
            by[r["cksum"]][0] += r[det]
            by[r["cksum"]][1] += r["one_turn"]
        for ck, (a, n) in sorted(by.items(), key=lambda kv: -kv[1][0] / max(kv[1][1], 1)):
            print("  %-11s %3d/%-4d  %5.1f%%" % (ck, a, n, 100 * a / n if n else 0))
        pre = by["1830906901"]
        lic = by["3694954268"]
        edit = by["136269960"]
        print("  pre-licence -> licence   rise p = %.2e"
              % rose(pre[0], pre[1], lic[0], lic[1]))
        print("  licence -> round 27 edit p = %.4f"
              % fell(lic[0], lic[1], edit[0], edit[1]))


def round20(rs):
    """Round 20 against its same-week neighbours, decomposed."""
    idx = {r["name"]: r for r in rs}
    nb = [idx["round-18"], idx["round-19"]]
    r20 = idx["round-20"]
    n_nb = sum(r["n"] for r in nb)
    ot_nb = sum(r["one_turn"] for r in nb)
    for det in DETECTORS:
        a_nb = sum(r[det] for r in nb)
        print("\n=== round 20 vs neighbours, %s ===" % det)
        print("  neighbours  one_turn %d/%d  asks %d/%d"
              % (ot_nb, n_nb, a_nb, ot_nb))
        print("  round 20    one_turn %d/%d  asks %d/%d"
              % (r20["one_turn"], r20["n"], r20[det], r20["one_turn"]))
        print("  one_turn rise p = %.2e ; conditional rise p = %.4f"
              % (rose(ot_nb, n_nb, r20["one_turn"], r20["n"]),
                 rose(a_nb, ot_nb, r20[det], r20["one_turn"])))


if __name__ == "__main__":
    separation(rs)
    round20(rs)
    strata_report()
