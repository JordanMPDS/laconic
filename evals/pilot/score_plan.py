#!/usr/bin/env python3
"""Round 102: is the build plan the depth a design answer leaves out? (#46)

    python3 evals/pilot/score_plan.py --control <snap> --edit <snap> \
        [--control-judgments <j> --edit-judgments <j>]
    python3 evals/pilot/score_plan.py --selftest

The edit adds one sentence to the design bullet under `## Level: full`: "The
build plan is the depth you left out, not the approach."

**Primary, opus.** Prose words on the eight `design-*` cases, read stratum only
(a run that called at least one tool). The statistic is the mean over cases of
the edit's mean log words minus the control's, permuted within case, one-sided
in the registered direction (down), seed `SEED`. It passes at p < `ALPHA` with
the ratio exp(shift) at or below `TARGET`.

**Deterministic bounds, fatal, read with the primary:**

- unread design answers (no tool call) must not rise, opus and sonnet pooled,
  one-sided Fisher at `ALPHA`;
- sonnet's design prose ratio, the same statistic, must not exceed `MARGIN`
  as a point estimate;
- `walkthrough`'s substring never-cut misses must not rise on opus, one-sided
  Fisher at `ALPHA`.

**Judged bounds, fatal, bought only after the primary passes:** panel fails on
the design cases must not rise, on opus pooled, on sonnet pooled and per opus
case; and panel fails on `ordered-steps` and `walkthrough` must not rise on
opus, per case and pooled. All one-sided Fisher at `ALPHA`, uncorrected.

Disclosed, deciding nothing: per-case medians on both models, the sentinel
prose ratio, numbered-item and heading counts, and the share of design answers
whose first question mark falls in the first half of the answer.
"""
import json
import math
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_compression import words  # noqa: E402
from score_structure import fisher_one_sided_fall  # noqa: E402

DESIGN = ("design-alerting", "design-audit-log", "design-cache", "design-rate-limit",
          "design-realtime", "design-retry", "design-search", "design-upload")
SENTINEL = ("ordered-steps", "walkthrough")
ALPHA, TARGET, MARGIN, SEED = 0.05, 0.90, 1.10, 102
NUMBERED = re.compile(r"^\s*(?:\d+[.)]|#{1,6}\s|\*\*\d)", re.M)
CASES = Path(__file__).resolve().parents[1] / "cases"


def load(path):
    return [r for r in bench_run.usable(json.loads(Path(path).read_text())["runs"])
            if r.get("arm") == "laconic"]


def read(r):
    return bool(r.get("tools")) or (r.get("num_turns") or 0) > 1


def pick(runs, model, cases, stratum=None):
    return [r for r in runs if r.get("model") == model and r.get("case") in cases
            and (stratum is None or read(r) == stratum)]


def shift(control, edit):
    """Mean over cases of edit's mean log prose words minus control's."""
    out = []
    for c in sorted({r["case"] for r in control} & {r["case"] for r in edit}):
        a = [math.log(max(words(r), 1)) for r in control if r["case"] == c]
        b = [math.log(max(words(r), 1)) for r in edit if r["case"] == c]
        out.append(sum(b) / len(b) - sum(a) / len(a))
    return sum(out) / len(out) if out else None


def shift_p(control, edit, resamples=20000):
    """(shift, one-sided p that the edit is lower), labels shuffled within case."""
    obs = shift(control, edit)
    if obs is None:
        return None, None
    rng = random.Random(SEED)
    pools = [([r for r in control if r["case"] == c] + [r for r in edit if r["case"] == c],
              sum(r["case"] == c for r in control))
             for c in sorted({r["case"] for r in control} & {r["case"] for r in edit})]
    hits = 0
    for _ in range(resamples):
        a, b = [], []
        for pool, n in pools:
            rng.shuffle(pool)
            a += pool[:n]
            b += pool[n:]
        if shift(a, b) <= obs + 1e-12:
            hits += 1
    return obs, (hits + 1) / (resamples + 1)


def rise_p(a, n1, c, n2):
    """P(edit count >= c | no difference): the tail a rise-is-harm bound reads."""
    if not n1 or not n2:
        return 1.0
    return fisher_one_sided_fall(c, n2, a, n1)


def bound(name, a, n1, c, n2, out):
    p = rise_p(a, n1, c, n2)
    held = p >= ALPHA
    print("  %-46s control %3d/%-3d edit %3d/%-3d p = %.4f  %s"
          % (name, a, n1, c, n2, p, "held" if held else "FAILS"))
    out.append(held)


def never_cut(runs):
    kw = {c: json.loads((CASES / c / "expect.json").read_text()).get("never_cut", [])
          for c in {r["case"] for r in runs}}
    return sum(bool(metrics.never_cut_missing(r.get("text") or "", kw[r["case"]]))
               for r in runs)


def fork_first(r):
    t = r.get("text") or ""
    i = t.find("?")
    return 0 <= i < len(t) / 2


def disclose(control, edit):
    print("\nper case, median prose words (control / edit), numbered items median:")
    for model in ("opus", "sonnet"):
        for c in DESIGN + SENTINEL:
            a, b = pick(control, model, (c,)), pick(edit, model, (c,))
            if not a or not b:
                continue
            print("  %-6s %-18s n=%2d/%-2d  %6.1f / %6.1f   %4.1f / %4.1f"
                  % (model, c, len(a), len(b), metrics.median([words(r) for r in a]),
                     metrics.median([words(r) for r in b]),
                     metrics.median([len(NUMBERED.findall(r.get("text") or "")) for r in a]),
                     metrics.median([len(NUMBERED.findall(r.get("text") or "")) for r in b])))
        a, b = pick(control, model, DESIGN), pick(edit, model, DESIGN)
        if a and b:
            print("  %-6s design answers with a question in the first half: %d/%d against %d/%d"
                  % (model, sum(map(fork_first, a)), len(a), sum(map(fork_first, b)), len(b)))
    a, b = pick(control, "opus", SENTINEL), pick(edit, "opus", SENTINEL)
    if a and b:
        s = shift(a, b)
        print("  opus sentinel prose ratio %.3f" % math.exp(s))


def fails(path):
    out = {}
    for j in json.loads(Path(path).read_text())["judgments"]:
        if j.get("arm") == "laconic" and j.get("verdict") in ("pass", "fail"):
            out[(j["case"], j["model"], j["rep"])] = j["verdict"] == "fail"
    return out


def judged(control, edit, cj, ej, held):
    print("\njudged bounds:")
    fc, fe = fails(cj), fails(ej)

    def count(runs, f):
        keyed = [f[(r["case"], r["model"], r["rep"])] for r in runs
                 if (r["case"], r["model"], r["rep"]) in f]
        return sum(keyed), len(keyed)

    def one(name, model, cases):
        a, n1 = count(pick(control, model, cases), fc)
        c, n2 = count(pick(edit, model, cases), fe)
        bound(name, a, n1, c, n2, held)

    one("design fails, opus pooled", "opus", DESIGN)
    one("design fails, sonnet pooled", "sonnet", DESIGN)
    for c in DESIGN:
        one("design fails, opus %s" % c, "opus", (c,))
    one("sentinel fails, opus pooled", "opus", SENTINEL)
    for c in SENTINEL:
        one("sentinel fails, opus %s" % c, "opus", (c,))


def score(control, edit, cj=None, ej=None):
    """Return (primary_passes, bounds_held, judged_or_not)."""
    a, b = pick(control, "opus", DESIGN, True), pick(edit, "opus", DESIGN, True)
    s, p = shift_p(a, b)
    ratio = math.exp(s) if s is not None else None
    primary = s is not None and p < ALPHA and ratio <= TARGET
    print("primary, opus design prose words (read stratum, n %d / %d): ratio %s, "
          "one-sided p %s: %s" % (len(a), len(b), "%.3f" % ratio if ratio else "-",
                                  "%.4f" % p if p is not None else "-",
                                  "PASSES" if primary else "does not pass"))
    held = []
    print("\ndeterministic bounds:")
    ca = pick(control, "opus", DESIGN) + pick(control, "sonnet", DESIGN)
    ea = pick(edit, "opus", DESIGN) + pick(edit, "sonnet", DESIGN)
    bound("unread design answers, opus and sonnet", sum(not read(r) for r in ca),
          len(ca), sum(not read(r) for r in ea), len(ea), held)
    sa, sb = pick(control, "sonnet", DESIGN), pick(edit, "sonnet", DESIGN)
    ss = shift(sa, sb)
    if ss is not None:
        ok = math.exp(ss) <= MARGIN
        print("  %-46s ratio %.3f against %.2f  %s"
              % ("sonnet design prose words", math.exp(ss), MARGIN,
                 "held" if ok else "FAILS"))
        held.append(ok)
    wa, wb = pick(control, "opus", ("walkthrough",)), pick(edit, "opus", ("walkthrough",))
    bound("walkthrough never-cut misses, opus", never_cut(wa), len(wa),
          never_cut(wb), len(wb), held)
    disclose(control, edit)
    if cj and ej:
        judged(control, edit, cj, ej, held)
    ok = all(held)
    print("\n%s" % ("ACCEPT at this stage" if primary and ok else
                    "REJECT" if not primary or not ok else ""))
    return primary, ok, bool(cj and ej)


def selftest():
    def run(case, model, rep, n, tools=("Read",), text=None):
        return {"ok": True, "arm": "laconic", "case": case, "model": model, "rep": rep,
                "text": text or " ".join(["word"] * n), "tools": list(tools),
                "num_turns": 2 if tools else 1}

    def side(scale, reps=10, unread=0):
        out = []
        for c in DESIGN:
            for i in range(reps):
                out.append(run(c, "opus", i, int((200 + 7 * i) * scale),
                               tools=() if i < unread else ("Read",)))
                out.append(run(c, "sonnet", i, 250 + 5 * i))
        for i in range(reps):
            out.append(run("walkthrough", "opus", i, 0, text="returns 401 " + "w " * 150))
            out.append(run("ordered-steps", "opus", i, 120))
        return out

    # the Fisher rise tail against a direct hypergeometric sum
    from math import comb
    a, n1, c, n2 = 2, 20, 7, 20
    direct = sum(comb(n1, a + c - x) * comb(n2, x) for x in range(c, min(n2, a + c) + 1)) \
        / comb(n1 + n2, a + c)
    assert abs(rise_p(a, n1, c, n2) - direct) < 1e-12
    assert rise_p(3, 20, 3, 20) > 0.5
    assert score(side(1.0), side(0.80))[:2] == (True, True)
    assert score(side(1.0), side(0.95))[0] is False          # under the 0.90 margin
    assert score(side(1.0), side(1.10))[0] is False          # the wrong direction
    assert score(side(1.0), side(0.80, unread=5))[1] is False  # unread rises
    son = side(0.80)
    for r in son:
        if r["model"] == "sonnet":
            r["text"] = " ".join(["word"] * 400)
    assert score(side(1.0), son)[1] is False                 # sonnet lengthens
    cut = side(0.80)
    for r in cut:
        if r["case"] == "walkthrough":
            r["text"] = "w " * 150
    assert score(side(1.0), cut)[1] is False                 # never-cut misses rise
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    args = dict(zip(argv[::2], argv[1::2]))
    if "--control" not in args or "--edit" not in args:
        sys.exit(__doc__)
    score(load(args["--control"]), load(args["--edit"]),
          args.get("--control-judgments"), args.get("--edit-judgments"))


if __name__ == "__main__":
    main(sys.argv[1:])
