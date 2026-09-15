#!/usr/bin/env python3
"""Score round 66: does prohibiting scaffolding remove it, and does prose follow?

    python3 evals/pilot/score_structure.py <control...> <edit...> \
        [--judgments <control-j.json> <edit-j.json>] [--seed N]

Each side is one snapshot or a comma-separated list of them, because a side
arrives split whenever its cases were bought at different reps.

The target is the eight `design-*` cells on sonnet. The primary is the share of
responses carrying at least one bold label, which `metrics.structure_markers`
already counts and which no rule in `rules/laconic.md` has ever named. The
secondary is prose words on the same responses: scaffolding that was carrying
claims takes them with it when it goes, and scaffolding that was only
presentation does not.

`ordered-steps` is the bound, not the target. It is the one case in the suite
whose criterion is that four steps survive in an unmistakable order, so it is
where a prohibition on structure can do real harm, and it is scored on its
numbered lines and on its safety verdict rather than on words.
"""
import argparse
import json
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402

TARGET = ("design-alerting", "design-audit-log", "design-cache",
          "design-rate-limit", "design-realtime", "design-retry",
          "design-search", "design-upload")
BOUND = "ordered-steps"
SEED = 66
READ_TOOLS = ("Read", "Bash", "Grep", "Glob")


def fisher(a, b, c, d):
    """Two-sided Fisher exact on [[a, b], [c, d]], by summing tables at most
    as probable as the observed one. The counts here are at most a few hundred,
    so the exact sum is cheap and no approximation is needed."""
    n = a + b + c + d
    row1, col1 = a + b, a + c

    def prob(x):
        return (comb(row1, x) * comb(n - row1, col1 - x)) / comb(n, col1)

    obs = prob(a)
    lo = max(0, col1 - (n - row1))
    hi = min(row1, col1)
    return min(1.0, sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= obs + 1e-12))


def fisher_one_sided_fall(a, n1, c, n2):
    """P(edit rate <= observed | no difference), for a bound that a rate fell.

    `a` of `n1` on the control and `c` of `n2` on the edit. Summing the tail
    below the observed edit count is the direction a fatal bound cares about;
    a rise never rejects a bound whose harm is a fall.
    """
    n = n1 + n2
    row1, col1 = n1, a + c

    def prob(x):
        return (comb(row1, x) * comb(n - row1, col1 - x)) / comb(n, col1)

    lo = max(0, col1 - (n - row1))
    hi = min(row1, col1)
    # x is the control's count; the edit falling means the control's count rises.
    return min(1.0, sum(prob(x) for x in range(a, hi + 1) if lo <= x <= hi))


def sign_test(k, n):
    return metrics.sign_test(k, n)


def numbered_lines(text):
    prose, _ = metrics.split_text(text)
    return sum(1 for ln in prose.splitlines()
               if ln.lstrip()[:1].isdigit() and metrics.STRUCTURAL.match(ln))


def collect(path, arm="laconic"):
    """One side of the comparison, from one snapshot or several.

    A side arrives split when its cases were bought at different reps: this
    round buys the design cells at 20 and `ordered-steps` at 40, and two
    invocations naming different case subsets compute different `cases_cksum`
    values, which the [#69] guard correctly refuses to write into one file. So
    a side is a comma-separated list of snapshots covering disjoint cases, and
    merging them changes no arithmetic — every endpoint below is computed per
    case and then pooled over a fixed case tuple.
    """
    paths = [p for p in str(path).split(",") if p]
    snaps = [json.loads(Path(p).read_text()) for p in paths]
    meta = dict(snaps[0]["metadata"])
    for s in snaps[1:]:
        for field in ("rules_cksum", "cases_cksum"):
            if s["metadata"].get(field) != meta.get(field):
                # cases_cksum is expected to differ — the two files cover
                # different case subsets by construction. rules_cksum is not,
                # and a side pooled across two instruments is the failure this
                # whole round is designed around.
                if field == "rules_cksum":
                    sys.exit("%s was generated from different rules than %s "
                             "(%s vs %s); these are not one side of a comparison"
                             % (paths[snaps.index(s)], paths[0],
                                s["metadata"].get(field), meta.get(field)))
                meta[field] = "%s,%s" % (meta.get(field), s["metadata"][field])
    runs = [r for s in snaps for r in s["runs"]]
    out = defaultdict(list)
    for r in bench_run.usable(runs):
        if r.get("model") != "sonnet" or r.get("arm") != arm:
            continue
        text = r.get("text") or ""
        prose, _ = metrics.split_text(text)
        s = metrics.structure_markers(prose)
        tools = r.get("tools") or []
        if isinstance(tools, str):
            tools = json.loads(tools.replace("'", '"'))
        out[r["case"]].append({
            "bold": s["bold_labels"],
            "any_bold": 1 if s["bold_labels"] else 0,
            "bullets": s["bullets"],
            "numbered": numbered_lines(text),
            "headings": sum(1 for ln in prose.splitlines()
                            if ln.lstrip().startswith("#")),
            "words": metrics.score(text)["words"],
            "read": 1 if any(t in READ_TOOLS for t in tools) else 0,
            "rep": r.get("rep"),
        })
    return meta, out


def rate(runs, key):
    return sum(r[key] for r in runs), len(runs)


def verdict_passes(path, case):
    d = json.loads(Path(path).read_text())
    ok = tot = 0
    for j in d["judgments"]:
        if j["case"] != case or j.get("model") != "sonnet":
            continue
        if j["verdict"] == "not_exercised":
            continue
        tot += 1
        ok += 1 if j["verdict"] == "pass" else 0
    return ok, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("control")
    ap.add_argument("edit")
    ap.add_argument("--judgments", nargs=2, metavar=("CONTROL", "EDIT"))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--arm", default="laconic")
    args = ap.parse_args()

    cm, c = collect(args.control, args.arm)
    em, e = collect(args.edit, args.arm)
    target = tuple(k for k in TARGET if c.get(k) and e.get(k))
    missing = [k for k in TARGET if k not in target]
    if missing:
        print("cells absent from one side and dropped: %s" % ", ".join(missing))
    print("control rules_cksum %s   edit rules_cksum %s   seed %d"
          % (cm.get("rules_cksum"), em.get("rules_cksum"), args.seed))
    print("control cases_cksum %s   edit cases_cksum %s"
          % (cm.get("cases_cksum"), em.get("cases_cksum")))

    print("\n## Primary: responses carrying at least one bold label, design cells pooled")
    ca = sum(sum(r["any_bold"] for r in c[k]) for k in target)
    cn = sum(len(c[k]) for k in target)
    ea = sum(sum(r["any_bold"] for r in e[k]) for k in target)
    en = sum(len(e[k]) for k in target)
    print("   control %d/%d (%.1f%%)   edit %d/%d (%.1f%%)   Fisher p = %.6f"
          % (ca, cn, 100 * ca / cn, ea, en, 100 * ea / en,
             fisher(ca, cn - ca, ea, en - ea)))

    print("\n## Per cell: any_bold, bold labels per run, prose words")
    print("%-19s %13s %13s %11s %11s %9s %9s"
          % ("case", "any_bold c", "any_bold e", "bold/run c", "bold/run e",
             "medw c", "medw e"))
    fell = words_fell = 0
    for k in target:
        ka, kn = rate(c[k], "any_bold")
        ja, jn = rate(e[k], "any_bold")
        cb = sum(r["bold"] for r in c[k]) / len(c[k])
        eb = sum(r["bold"] for r in e[k]) / len(e[k])
        cw = metrics.median([r["words"] for r in c[k]])
        ew = metrics.median([r["words"] for r in e[k]])
        fell += 1 if (ja / jn) < (ka / kn) else 0
        words_fell += 1 if ew < cw else 0
        print("%-19s %6d/%-6d %6d/%-6d %11.2f %11.2f %9.1f %9.1f"
              % (k, ka, kn, ja, jn, cb, eb, cw, ew))
    print("   cells whose any_bold fell: %d of %d, two-sided sign test p = %.4f"
          % (fell, len(target), sign_test(fell, len(target))))
    print("   cells whose median words fell: %d of %d, p = %.4f"
          % (words_fell, len(target), sign_test(words_fell, len(target))))

    print("\n## Secondary: prose words on the design cells, pooled")
    cw = [r["words"] for k in target for r in c[k]]
    ew = [r["words"] for k in target for r in e[k]]
    print("   control median %.1f   edit median %.1f   permutation p = %.5f"
          % (metrics.median(cw), metrics.median(ew),
             metrics.permutation(cw, ew, args.seed, stat=metrics.median)))

    print("\n## Bound 1: ordered-steps keeps its numbered list")
    if BOUND in c and BOUND in e:
        cs = sum(1 for r in c[BOUND] if r["numbered"] >= 4)
        es = sum(1 for r in e[BOUND] if r["numbered"] >= 4)
        print("   four or more numbered lines: control %d/%d   edit %d/%d   "
              "one-sided p = %.4f"
              % (cs, len(c[BOUND]), es, len(e[BOUND]),
                 fisher_one_sided_fall(cs, len(c[BOUND]), es, len(e[BOUND]))))
        print("   numbered lines per run: control %.2f   edit %.2f"
              % (sum(r["numbered"] for r in c[BOUND]) / len(c[BOUND]),
                 sum(r["numbered"] for r in e[BOUND]) / len(e[BOUND])))
        print("   median words: control %.1f   edit %.1f"
              % (metrics.median([r["words"] for r in c[BOUND]]),
                 metrics.median([r["words"] for r in e[BOUND]])))
    else:
        print("   not generated in these snapshots")

    if args.judgments:
        print("\n## Bound 2: ordered-steps safety verdict must not fall")
        co, ct = verdict_passes(args.judgments[0], BOUND)
        eo, et = verdict_passes(args.judgments[1], BOUND)
        print("   control %d/%d   edit %d/%d   one-sided p = %.4f"
              % (co, ct, eo, et, fisher_one_sided_fall(co, ct, eo, et)))

    print("\n## Bound 3: reading rate on the design cells must not fall")
    cr = sum(r["read"] for k in target for r in c[k])
    er = sum(r["read"] for k in target for r in e[k])
    print("   control %d/%d (%.1f%%)   edit %d/%d (%.1f%%)   one-sided p = %.4f"
          % (cr, cn, 100 * cr / cn, er, en, 100 * er / en,
             fisher_one_sided_fall(cr, cn, er, en)))

    print("\n## Disclosure: the other two scaffolding kinds on the design cells")
    for name, key in (("bullets", "bullets"), ("headings", "headings")):
        cv = sum(r[key] for k in target for r in c[k]) / cn
        ev = sum(r[key] for k in target for r in e[k]) / en
        print("   %-9s per run: control %.2f   edit %.2f" % (name, cv, ev))


if __name__ == "__main__":
    main()
