#!/usr/bin/env python3
"""How often a Stage 1 precheck bar fires, before it is registered (#467).

    python3 evals/bench/precheck.py --cells 10:3,10,10 --fire-at 0.30 --quiet-at 0.10 --bar 9
    python3 evals/bench/precheck.py --cells 10:3,10,10 --fire-at 14/30 --quiet-at 0.10

A precheck withdraws an edit unrun when master's failures on a few cells fall
below a bar, so the bar decides whether the edit is measured at all. Round
121's "9 of 30, with recall-index contributing 3 of 10" fires on 45% of draws
at the 30% it names: an edit aimed at a defect sitting exactly at the bar is
withdrawn more often than tested. This prints that figure before the bar is
registered rather than after it has withdrawn something.

`--cells` lists each cell as `n` or `n:minimum`. The bar fires when every cell
reaches its minimum and the pooled count reaches `--bar`. Cells are independent
binomials; a rate is one number for every cell, or one per cell, comma
separated, and `a/b` is accepted for a count. `--fire-at` is the lowest rate the
edit is still worth a round at, where the bar has to fire with probability at
least `--power`; `--quiet-at` is a rate at which the defect counts as gone,
where it may fire at most `--quiet`. `--rate` adds columns, such as the
benchmark's observed rate when `--fire-at` sits below it.

With `--bar`, prints that bar and exits 1 when it misses the pair; without it,
prints every bar and exits 1 when none meets the pair. Either way it names the
bars that do, or the smallest multiple of the reps at which one would. A clause comparing master with another arm (round
124's Fisher test against no-rules) is not modelled: it can only stop a bar
firing, so the figure printed is an upper bound on such a bar.
"""
import argparse
import math
import sys

MAX_SCALE = 10


def tails(cells, rates):
    """tails[k] = P(every cell reaches its minimum and the pooled count reaches k).

    The mass below a cell's minimum is dropped, not renormalised, so these are
    joint probabilities and not ones conditioned on the minima holding.
    """
    dist = [1.0]
    for (n, lo), p in zip(cells, rates):
        cell = [0.0] * lo + [math.comb(n, i) * p ** i * (1 - p) ** (n - i)
                             for i in range(lo, n + 1)]
        new = [0.0] * (len(dist) + n)
        for i, a in enumerate(dist):
            for j, b in enumerate(cell):
                new[i + j] += a * b
        dist = new
    out = [0.0] * (len(dist) + 1)
    for k in range(len(dist) - 1, -1, -1):
        out[k] = out[k + 1] + dist[k]
    return out[:-1]


def fire_probability(cells, bar, rates):
    return tails(cells, rates)[bar]


def admissible(cells, fire, quiet, power, quiet_max):
    f, q = tails(cells, fire), tails(cells, quiet)
    return [k for k in range(len(f)) if f[k] >= power and q[k] <= quiet_max]


def _rate(s):
    a, _, b = s.partition("/")
    p = float(a) / float(b) if b else float(a)
    if not 0 <= p <= 1:
        raise ValueError("rate %s is not in [0, 1]" % s)
    return p


def _rates(s, k):
    rates = [_rate(x) for x in s.split(",")]
    if len(rates) == 1:
        return rates * k
    if len(rates) != k:
        raise ValueError("%d rates for %d cells" % (len(rates), k))
    return rates


def _cells(s):
    cells = []
    for part in s.split(","):
        n, _, lo = part.partition(":")
        n, lo = int(n), int(lo or 0)
        if n < 1 or not 0 <= lo <= n:
            raise ValueError("cell %s needs n >= 1 and 0 <= minimum <= n" % part)
        cells.append((n, lo))
    return cells


def _label(rates):
    return "%g" % rates[0] if len(set(rates)) == 1 else ",".join("%g" % p for p in rates)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cells", required=True, help="n[:minimum] per cell, comma separated")
    ap.add_argument("--fire-at", required=True, help="rate the bar must fire at")
    ap.add_argument("--quiet-at", required=True, help="rate the bar must stay quiet at")
    ap.add_argument("--bar", type=int, help="pooled count the bar requires")
    ap.add_argument("--power", type=float, default=0.9,
                    help="least P(fire) at --fire-at (default 0.9)")
    ap.add_argument("--quiet", type=float, default=0.1,
                    help="most P(fire) at --quiet-at (default 0.1)")
    ap.add_argument("--rate", action="append", default=[], help="extra rate column")
    args = ap.parse_args(argv)
    try:
        cells = _cells(args.cells)
        fire, quiet = (_rates(r, len(cells)) for r in (args.fire_at, args.quiet_at))
        extra = [_rates(r, len(cells)) for r in args.rate]
    except (ValueError, ZeroDivisionError) as e:
        ap.error(str(e))
    total = sum(n for n, _ in cells)
    if args.bar is not None and not 0 <= args.bar <= total:
        ap.error("--bar %d is outside 0..%d" % (args.bar, total))

    print("cells %s, %d runs; the pair: P(fire) >= %g at %s, <= %g at %s"
          % (args.cells, total, args.power, _label(fire), args.quiet, _label(quiet)))
    columns = [("fire@" + _label(fire), fire), ("quiet@" + _label(quiet), quiet)]
    columns += [("at " + _label(r), r) for r in extra]
    print("%5s  %s  %10s" % ("bar", "  ".join("%14s" % c for c, _ in columns), "own rate"))
    ok = admissible(cells, fire, quiet, args.power, args.quiet)
    curves = [tails(cells, r) for _, r in columns]
    for k in ([args.bar] if args.bar is not None else range(total + 1)):
        probs = [c[k] for c in curves]
        own = fire_probability(cells, k, [k / total] * len(cells))
        print("%5d  %s  %10.3f%s" % (k, "  ".join("%14.3f" % p for p in probs), own,
                                     "  meets the pair" if k in ok else ""))

    if args.bar is not None:
        print("bar %d %s the pair" % (args.bar, "meets" if args.bar in ok else "misses"))
    if ok:
        print("bars meeting the pair: %d to %d of %d" % (ok[0], ok[-1], total))
    else:
        if curves[0][0] < args.power:
            print("the cell minima alone fire on %.3f of draws at %s, under %g before any "
                  "pooled bar: lower a minimum" % (curves[0][0], _label(fire), args.power))
        # ponytail: scales every cell and minimum by one integer factor; a design
        # that adds reps unevenly has to be checked by hand.
        for m in range(2, MAX_SCALE + 1):
            scaled = [(n * m, lo * m) for n, lo in cells]
            found = admissible(scaled, fire, quiet, args.power, args.quiet)
            if found:
                print("no bar meets the pair at these reps; at %dx (cells %s) bars %d to %d "
                      "of %d do" % (m, ",".join("%d:%d" % c for c in scaled), found[0],
                                    found[-1], total * m))
                break
        else:
            print("no bar meets the pair at up to %dx these reps" % MAX_SCALE)
    return 0 if (args.bar in ok if args.bar is not None else ok) else 1

if __name__ == "__main__":
    sys.exit(main())
