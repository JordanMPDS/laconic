#!/usr/bin/env python3
"""Round 119: the fixture a criterion grades against, written into the criterion (#414).

    python3 evals/pilot/fixture_facts.py <case>     # print one case's block
    python3 evals/pilot/fixture_facts.py --write    # rewrite every CASES trap
    python3 evals/pilot/fixture_facts.py --check    # exit 1 if a trap is stale

Since #411 a judge sees the question, the criterion and the response, and no
file. `simplify-*` and `verify-*` fail an answer that states something about
the code, tables or data "that the fixture contradicts", and `subset-*` one
that states "a seeded value the record does not give". Until #411 the judges
opened the fixture to check that themselves, in 80 of 80 `simplify-*`
judgments, so from #411 on those clauses had nothing to check against.

So each of those traps ends with a block built here from the fixture itself:
every small file verbatim, what the fixture's own code computes for every
combination its tables hold, and, for the data file no judge could read by
eye, its row count, its rows per combination and how many rows the special
case changes. The code is run with `runpy`, which writes no `__pycache__`
into the fixture (#411's other half). `tests/test_evals_layout.sh` runs
`--check`, so a fixture edit that leaves its trap behind fails the suite.
"""
import csv
import json
import runpy
import sys
from collections import Counter
from pathlib import Path

PILOT = Path(__file__).resolve().parent
MARK = "\n\nThe fixture, for grading."
# The block is evidence for the clauses above it and adds none of its own: a
# trap that fails only a misstated seeded value must not start failing a
# miscounted section because the record is now on the page.
LEAD = (MARK + " The judge cannot open the files, so they are given here as the "
        "evidence the criterion above refers to. An answer need not mention any "
        "of it, and the criterion alone decides what fails.")

# stem: (code, data file, function, special case, keys, value label, date column)
STEMS = {
    "quota": ("limits.py", "accounts.csv", "limit_for", "apply_legacy_cap",
              ("plan", "region"), "requests-per-minute limit", "created"),
    "rates": ("price.py", "orders_2026-09.csv", "price", "apply_remote_correction",
              ("zone", "band"), "price", "date"),
    "routing": ("route.py", "alerts_2026-09.csv", "route", "apply_payments_override",
                ("service", "severity"), "team and channel", "fired_at"),
}
# What the code does where its own text says otherwise. Read off route.py by
# hand, not computed: the docstring is the one place the fixture disagrees
# with itself, and answers quote it (round 118's `simplify-routing` reps 0, 1).
NOTES = {
    "routing": "`apply_payments_override` returns finance-oncall in place of the "
               "owning team, so billing is routed none of those alerts, although "
               "its docstring says \"as well as the owner\".",
}
CASES = (["%s-%s" % (f, s) for f in ("simplify", "verify") for s in STEMS]
         + ["%s-%s" % (f, s) for f in ("subset", "deepsubset")
            for s in ("ledger", "gateway", "scheduler")])


def _fenced(name, text):
    return "`%s`:\n```\n%s\n```" % (name, text.rstrip("\n"))


def _cells(stem, fx):
    """{(key1, key2): (value now, value before the special case)} off the code."""
    g = runpy.run_path(str(fx / STEMS[stem][0]))
    if stem == "quota":
        return {(p, r): (g["limit_for"](p, r), int(g["PLANS"][p] * g["FACTORS"][r]))
                for p in g["PLANS"] for r in g["FACTORS"]}
    if stem == "rates":
        out = {}
        for z in g["ZONES"]:
            for b, lo, _, m in g["BANDS"]:
                plain = (g["ZONES"][z] * m).quantize(g["Decimal"]("0.01"),
                                                     rounding=g["ROUND_HALF_UP"])
                out[(z, b)] = (g["price"](z, lo), plain)
        return out
    return {(s, v): (g["route"](s, v), (g["OWNERS"][s], g["CHANNELS"][v]))
            for s in g["OWNERS"] for v in g["CHANNELS"]}


def _show(stem, v):
    return "%s %s" % v if stem == "routing" else str(v)


def _rows(stem, fx):
    """The data file's rows, each reduced to the combination the code keys on."""
    code, data = STEMS[stem][:2]
    rows = list(csv.DictReader((fx / data).open()))
    if stem == "rates":
        band_for = runpy.run_path(str(fx / code))["band_for"]
        return rows, [(r["zone"], band_for(float(r["weight_kg"]))) for r in rows]
    a, b = STEMS[stem][4]
    return rows, [(r[a], r[b]) for r in rows]


def _grid(cells, show):
    """One line per first key: `a: b x, b y, ...`, in the tables' own order."""
    return "\n".join("%s: %s" % (a, ", ".join("%s %s" % (b, show((a, b)))
                                                for x, b in cells if x == a))
                     for a in dict.fromkeys(k[0] for k in cells))


def code_block(stem, fx):
    code, data, fn, special, (ka, kb), label, date = STEMS[stem]
    parts = [LEAD]
    for f in sorted(fx.iterdir()):
        if f.name != data and f.is_file():
            parts.append(_fenced(f.name, f.read_text()))
    cells = _cells(stem, fx)
    changed = sorted(k for k, (now, before) in cells.items() if now != before)
    value = lambda k: _show(stem, cells[k][0]) + (
        " (%s before `%s`)" % (_show(stem, cells[k][1]), special) if k in changed else "")
    parts.append("The %s `%s` gives today for each of the %d %s and %s "
                 "combinations the tables hold, %d of them changed by `%s`:\n%s"
                 % (label, fn, len(cells), ka, kb, len(changed), special,
                    _grid(cells, value)))
    rows, keys = _rows(stem, fx)
    n = Counter(keys)
    assert set(n) <= set(cells), "a row the tables do not hold"
    header = next(iter((fx / data).open())).strip()
    line = ("`%s` is not shown. Its header is `%s`, and it has %d rows, every one "
            "a %s and %s the tables hold" % (data, header, len(rows), ka, kb))
    if stem == "rates":
        w = [float(r["weight_kg"]) for r in rows]
        line += ", weighing %s to %s kg" % (min(w), max(w))
    line += (", `%s` %s to %s. `%s` changes %d of them (%s). Rows per combination:\n%s"
             % (date, min(r[date] for r in rows), max(r[date] for r in rows),
                special, sum(n[k] for k in changed),
                ", ".join("%s %s %d" % (a, b, n[(a, b)]) for a, b in changed),
                _grid(cells, lambda k: str(n[k]))))
    parts.append(line)
    if stem in NOTES:
        parts.append(NOTES[stem])
    return "\n\n".join(parts)


def record_block(fx):
    return "\n\n".join([LEAD] + [_fenced(f.name, f.read_text())
                                 for f in sorted(fx.iterdir()) if f.is_file()])


def block(case):
    fam, stem = case.split("-", 1)
    fx = PILOT / case / "fixture"
    return code_block(stem, fx) if stem in STEMS else record_block(fx)


def base(trap):
    """The trap as written by hand, without the block this script appends."""
    return trap.split(MARK, 1)[0]


def check():
    stale = []
    for c in CASES:
        trap = json.loads((PILOT / c / "expect.json").read_text())["trap"]
        if trap != base(trap) + block(c):
            stale.append(c)
    return stale


def write():
    for c in CASES:
        p = PILOT / c / "expect.json"
        raw = p.read_text()
        d = json.loads(raw)
        d["trap"] = base(d["trap"]) + block(c)
        indent = len(raw.splitlines()[1]) - len(raw.splitlines()[1].lstrip())
        p.write_text(json.dumps(d, indent=indent, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if arg == "--write":
        write()
    elif arg == "--check":
        stale = check()
        if stale:
            sys.exit("stale fixture facts in %s; run "
                     "python3 evals/pilot/fixture_facts.py --write" % ", ".join(stale))
        print("%d traps carry their fixture's facts" % len(CASES))
    else:
        print(block(arg))
