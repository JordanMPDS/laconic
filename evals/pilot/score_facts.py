#!/usr/bin/env python3
"""Round 119: does a tool-less judge grade the fixture once the trap carries it? (#414)

    python3 evals/pilot/score_facts.py build <out-dir>
    python3 evals/pilot/score_facts.py score <out-dir>
    python3 evals/pilot/score_facts.py --selftest

`build` draws the round's responses and writes two snapshots for `judge.py`:

- `round-119-source.json`: **U**, responses the tool-using panel passed, ten
  per `simplify-*` case from round 118 and five per `subset-*` case from rounds
  96 and 97; and **F**, every response that panel failed on those cases, 15.
- `round-119-mutants.json`: **M**, each U response with one near-miss fixture
  error seeded into it. The token is a number the case's fixture block states
  and its pre-#414 trap does not, chosen at seed 119, and every occurrence of
  it moves by one in its last place (13 to 14, 7.22 to 7.23). A `subset-*`
  mutant renames one of the eight seeded questions to an OQ number its record
  does not have. A mutant whose token turns out to state no fixture fact is
  redrawn at the next seed, and `build` prints every redraw.

Each snapshot is judged twice, with the traps before #414 and after it, and
`score` reads the four files back. Run keys are renumbered per case, so each
run carries `source` (the snapshot and key it came from) and, for M,
`mutation`.

**Bar 1:** the new traps fail at least 24 of the 30 `simplify-*` mutants, and
more of them than the old traps, exact one-sided McNemar, alpha 0.05.
**Bar 2:** the new traps pass at least 41 of U's 45 responses. A fail a hand
read finds to be a genuine fixture contradiction leaves the denominator and is
reported, since the panel that passed it could have missed it.
**Bar 3:** the new traps fail no fewer of F than the old ones do, one-sided
McNemar for a fall, alpha 0.05.
"""
import json
import random
import re
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOOP = ROOT / "evals" / "snapshots" / "loop"
sys.path.insert(0, str(HERE))
import fixture_facts  # noqa: E402

SEED = 119
SIMPLIFY = {"files": ["round-118-control", "round-118-edit", "round-118-rep-control",
                      "round-118-rep-edit"], "cases": ["simplify-quota", "simplify-rates",
                                                       "simplify-routing"], "per": 10}
SUBSET = {"files": ["round-96-control", "round-96-edit", "round-97-control",
                    "round-97-edit", "round-97-rep-control", "round-97-rep-edit"],
          "cases": ["subset-ledger", "subset-gateway", "subset-scheduler"], "per": 5}
# A figure: two or more digits, or a decimal. Single digits are mostly prose
# ("2 zones", "B5"), and a year is no fixture fact.
NUM = re.compile(r"(?<![\w.])(\d{2,}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+)(?![\w])")
OQ = re.compile(r"\bOQ-(\d+)\b")


def figures(text):
    return {m.group(1) for m in NUM.finditer(text)} - {"2026"}


def nudge(tok):
    """`tok` moved by one in its last place: 13 to 14, 7.22 to 7.23, 10,800 to 10,801."""
    digits = tok.replace(",", "")
    if "." in digits:
        places = len(digits.split(".")[1])
        return "%.*f" % (places, float(digits) + 10 ** -places)
    out = str(int(digits) + 1)
    return "{:,}".format(int(out)) if "," in tok else out


def judged(files, cases):
    """[(file, run, verdict)] for every decided panel verdict on `cases`."""
    out = []
    for f in files:
        runs = {(r["case"], r["arm"], r["model"], r["rep"]): r
                for r in json.loads((LOOP / (f + ".json")).read_text())["runs"]}
        for j in json.loads((LOOP / (f + "-judgments.json")).read_text())["judgments"]:
            if j["case"] in cases and j["verdict"] in ("pass", "fail"):
                out.append((f, runs[(j["case"], j["arm"], j["model"], j["rep"])],
                            j["verdict"]))
    return out


def old_trap(case):
    return fixture_facts.base(json.loads((HERE / case / "expect.json").read_text())["trap"])


def mutate(case, text, rng):
    """(mutated text, mutation record), or None when `text` offers no target."""
    fam, stem = case.split("-", 1)
    if fam == "subset":
        rec = (HERE / case / "fixture" / "STATUS.md").read_text()
        spec = rec.split("## SPEC", 1)[1].split("## Implementation", 1)[0]
        ids = {int(n) for n in OQ.findall(rec)}
        seeded = {int(n) for n, w in re.findall(r"\*\*OQ-(\d+) `\w+`\.\*\* (\w+)", spec)
                  if w == "Seeded"}
        have = sorted(seeded & {int(n) for n in OQ.findall(text)})
        if not have:
            return None
        n = rng.choice(have)
        to = next(m for m in (n + 1, n - 1, n + 2, n + 3) if m not in ids)
        new = re.sub(r"\bOQ-%d\b" % n, "OQ-%d" % to, text)
        return new, {"token": "OQ-%d" % n, "to": "OQ-%d" % to,
                     "count": len(re.findall(r"\bOQ-%d\b" % n, text))}
    stated = figures(fixture_facts.block(case)) - figures(old_trap(case))
    have = sorted(figures(text) & stated, key=lambda t: (len(t), t))
    if not have:
        return None
    tok = rng.choice(have)
    pat = r"(?<![\w.])%s(?![\w])" % re.escape(tok)
    return re.sub(pat, nudge(tok), text), {"token": tok, "to": nudge(tok),
                                           "count": len(re.findall(pat, text))}


def snapshot(runs, note):
    return {"metadata": {"note": note, "rules_cksum": None}, "runs": runs}


def build(out, redraw=()):
    """Write the two snapshots; `redraw` names U keys whose first draw failed review."""
    rng = random.Random(SEED)
    source, mutants, log = [], [], []
    for design in (SIMPLIFY, SUBSET):
        pool = judged(design["files"], design["cases"])
        for case in design["cases"]:
            passes = [(f, r) for f, r, v in pool if r["case"] == case and v == "pass"
                      and mutate(case, r["text"], random.Random(0))]
            fails = [(f, r) for f, r, v in pool if r["case"] == case and v == "fail"]
            draw = rng.sample(passes, design["per"])
            for i, (f, r) in enumerate(draw + fails):
                rec = dict(r, rep=i, arm="laconic",
                           source={"snapshot": f, "arm": r["arm"], "rep": r["rep"]},
                           set="U" if i < design["per"] else "F")
                source.append(rec)
                if rec["set"] == "F":
                    continue
                key = "%s/%d" % (case, i)
                mrng = random.Random("%d:%s:%d" % (SEED, key, redraw.count(key)))
                text, m = mutate(case, r["text"], mrng)
                mutants.append(dict(rec, text=text, mutation=m, set="M"))
                log.append("%-18s %s -> %s (x%d)" % (key, m["token"], m["to"], m["count"]))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    note = "round 119 (#414): drawn by evals/pilot/score_facts.py build at seed %d" % SEED
    for name, runs in (("source", source), ("mutants", mutants)):
        (out / ("round-119-%s.json" % name)).write_text(
            json.dumps(snapshot(runs, note), indent=2, sort_keys=True) + "\n")
    print("\n".join(log))
    print("U %d, F %d, M %d" % (sum(r["set"] == "U" for r in source),
                                sum(r["set"] == "F" for r in source), len(mutants)))


def mcnemar_more(b, c):
    """One-sided exact McNemar: P(at least b of the b + c discordant pairs)."""
    n = b + c
    return sum(comb(n, k) for k in range(b, n + 1)) / 2 ** n if n else 1.0


def verdicts(path):
    return {(j["case"], j["rep"]): j for j in json.loads(Path(path).read_text())["judgments"]}


def score(out):
    out = Path(out)
    src = {(r["case"], r["rep"]): r
           for r in json.loads((out / "round-119-source.json").read_text())["runs"]}
    v = {(s, t): verdicts(out / ("round-119-%s-%s-judgments.json" % (s, t)))
         for s in ("source", "mutants") for t in ("old", "new")}

    def tally(s, keys):
        """(new fails, old fails, new-only fails, old-only fails) over `keys`."""
        nf = {k for k in keys if v[(s, "new")][k]["verdict"] == "fail"}
        of = {k for k in keys if v[(s, "old")][k]["verdict"] == "fail"}
        return len(nf), len(of), len(nf - of), len(of - nf)

    def keys(s, fam, kind):
        return [k for k in v[(s, "new")] if k[0].startswith(fam)
                and src[k]["set"] == kind]

    ok = True
    m = keys("mutants", "simplify", "U")
    nf, of, b, c = tally("mutants", m)
    p = mcnemar_more(b, c)
    bar1 = nf >= 24 and nf > of and p < 0.05
    ok &= bar1
    print("Bar 1, simplify-* mutants: new fails %d/%d, old fails %d/%d, "
          "discordant %d/%d, one-sided McNemar p = %.2g -> %s"
          % (nf, len(m), of, len(m), b, c, p, "pass" if bar1 else "FAIL"))
    m = keys("mutants", "subset", "U")
    nf, of, b, c = tally("mutants", m)
    print("disclosed, subset-* mutants: new fails %d/%d, old fails %d/%d, p = %.2g"
          % (nf, len(m), of, len(m), mcnemar_more(b, c)))
    u = keys("source", "", "U")
    nf, of, b, c = tally("source", u)
    print("Bar 2, U: new passes %d/%d, old passes %d/%d (hand-read every new fail: %s)"
          % (len(u) - nf, len(u), len(u) - of, len(u),
             ", ".join("%s/%d" % k for k in u if v[("source", "new")][k]["verdict"] == "fail")
             or "none"))
    f = keys("source", "", "F")
    nf, of, b, c = tally("source", f)
    p = mcnemar_more(c, b)
    bar3 = p >= 0.05
    ok &= bar3
    print("Bar 3, F: new fails %d/%d, old fails %d/%d, one-sided McNemar for a "
          "fall p = %.2g -> %s" % (nf, len(f), of, len(f), p, "pass" if bar3 else "FAIL"))
    for s in ("mutants", "source"):
        for t in ("old", "new"):
            members = {}
            for j in v[(s, t)].values():
                for mem, x in (j.get("panel") or {}).items():
                    members.setdefault(mem, []).append(x["verdict"])
            print("  %-7s %-3s %s" % (s, t, "  ".join(
                "%s %d/%d fail" % (mem, xs.count("fail"), sum(x is not None for x in xs))
                for mem, xs in sorted(members.items()))))
    return ok


def selftest():
    assert nudge("13") == "14" and nudge("7.22") == "7.23" and nudge("10,800") == "10,801"
    assert nudge("0.90") == "0.91" and nudge("45.99") == "46.00"
    assert figures("the 13 parcels at 7.22, 2 zones, B5, 2026, Z6") == {"13", "7.22"}
    t, m = mutate("simplify-rates", "all 640 orders; 13 pay the surcharge of 4.50",
                  random.Random(1))
    assert m["token"] in ("640", "13") and "4.50" in t, "4.50 is in the old trap"
    t, m = mutate("subset-ledger", "OQ-3, OQ-7 and OQ-9", random.Random(1))
    assert m["token"] in ("OQ-3", "OQ-7") and "OQ-9" in t, "OQ-9 is not seeded"
    assert "OQ-4" in t or "OQ-8" in t
    assert mutate("simplify-quota", "nothing to see", random.Random(1)) is None
    assert mcnemar_more(5, 0) == 1 / 32 and mcnemar_more(0, 0) == 1.0
    print("selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["--selftest"]:
        selftest()
    elif cmd == ["build"]:
        build(sys.argv[2], sys.argv[3:])
    elif cmd == ["score"]:
        sys.exit(0 if score(sys.argv[2]) else 1)
    else:
        sys.exit(__doc__)
