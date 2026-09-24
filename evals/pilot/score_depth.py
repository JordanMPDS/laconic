#!/usr/bin/env python3
"""Round 82: does [#46]'s design-question essay reproduce on opus, at depth?

    python3 evals/pilot/score_depth.py evals/snapshots/loop/round-82-*.json
    python3 evals/pilot/score_depth.py --selftest

[#46] is a design question asked deep in an Opus session that came back at
about 1,400 words. Every design round since has been single-turn and on
haiku and sonnet; opus was last measured on `design-*` at rules 136269960,
where laconic's longest answer was 368 words. `drift-service` is five
"how would you ..." design turns in one session under the shipped hook
wiring (`--turn-delivery plugin`), and `design-alerting` is #46's own prompt.

The registered readouts, in the order `round-82.md` gives them:

- **R1, the tail.** Share of opus laconic responses over `TAIL_WORDS` prose
  words, pooled over every `drift-service` turn and `design-alerting`.
  Branch A fires at `TAIL_SHARE` or more.
- **R2, depth.** On opus `drift-service`, each session scores the mean log
  prose words over turns 2 to 5 minus turn 1's; D is laconic's mean score
  minus baseline's, tested one-sided by permuting whole sessions between the
  arms. Branch B fires when exp(D) >= `DEPTH_RATIO` and p < `ALPHA`. Turns ask
  different questions, so the baseline's profile is what makes growth
  attributable to depth rather than to which question comes later.
- Everything else prints as disclosure and decides nothing.

[#46]: https://github.com/JordanMPDS/laconic/issues/46
"""
import argparse
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import score_dilution as sd  # noqa: E402
from metrics import WORD, closing_offers, split_text  # noqa: E402

DRIFT, ALERT = "drift-service", "design-alerting"
TAIL_WORDS = 600
TAIL_SHARE = 0.10
DEPTH_RATIO = 1.25
ALPHA = 0.05
SEED = 82
PERMUTATIONS = 20000


def words(text):
    return len(WORD.findall(split_text(text or "")[0]))


def distinct(runs):
    seen, out = set(), []
    for r in runs:
        key = (r["case"], r["arm"], r["model"], r["rep"])
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def responses(runs, arm, model, case=None):
    """[(case, turn index, text, tools used)] for every response of the cell."""
    out = []
    for r in runs:
        if r["arm"] != arm or r["model"] != model:
            continue
        if case and r["case"] != case:
            continue
        if isinstance(r.get("turns"), list):
            out += [(r["case"], i, t.get("text"), (t.get("num_turns") or 0) > 1)
                    for i, t in enumerate(r["turns"])]
        else:
            out.append((r["case"], 0, r.get("text"), sd.grounded(r)))
    return out


def tail(runs):
    rows = responses(runs, "laconic", "opus")
    k = sum(words(t) > TAIL_WORDS for _, _, t, _ in rows)
    return k, len(rows)


def wilson(k, n, z=1.96):
    if not n:
        return 0.0, 1.0
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def session_score(run):
    logs = [math.log(words(t.get("text")) + 1) for t in run["turns"]]
    return sum(logs[1:]) / len(logs[1:]) - logs[0]


def depth(runs, model="opus", seed=SEED, draws=PERMUTATIONS):
    """(D, one-sided p, n laconic, n baseline) or None."""
    pick = lambda arm: [session_score(r) for r in runs  # noqa: E731
                        if r["case"] == DRIFT and r["arm"] == arm
                        and r["model"] == model
                        and isinstance(r.get("turns"), list)
                        and len(r["turns"]) > 1]
    a, b = pick("laconic"), pick("baseline")
    if not a or not b:
        return None
    obs = sum(a) / len(a) - sum(b) / len(b)
    pool, rnd, hits = a + b, random.Random(seed), 0
    for _ in range(draws):
        rnd.shuffle(pool)
        x, y = pool[:len(a)], pool[len(a):]
        hits += sum(x) / len(x) - sum(y) / len(y) >= obs - 1e-12
    return obs, (hits + 1) / (draws + 1), len(a), len(b)


def branch(tail_kn, dep):
    k, n = tail_kn
    if n and k / n >= TAIL_SHARE:
        return "A"
    if dep and math.exp(dep[0]) >= DEPTH_RATIO and dep[1] < ALPHA:
        return "B"
    return "C"


def median(xs):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def report(runs, out=print):
    runs = distinct(runs)
    k, n = tail(runs)
    lo, hi = wilson(k, n)
    out("R1 tail: opus laconic responses over %d prose words: %d/%d "
        "(%.1f%%), 95%% Wilson [%.1f%%, %.1f%%]; branch A at %.0f%%"
        % (TAIL_WORDS, k, n, 100 * k / n if n else 0, 100 * lo, 100 * hi,
           100 * TAIL_SHARE))
    dep = depth(runs)
    if dep:
        out("R2 depth, opus: exp(D) = %.3f, one-sided permutation p = %.4f "
            "(%d laconic sessions, %d baseline); branch B at >= %.2f and "
            "p < %.2f" % (math.exp(dep[0]), dep[1], dep[2], dep[3],
                          DEPTH_RATIO, ALPHA))
    else:
        out("R2 depth, opus: no sessions on one side")
    out("VERDICT: branch %s" % branch((k, n), dep))

    out("")
    out("disclosure: median / max prose words, unread and closing offers "
        "per turn")
    for model in ("opus", "sonnet"):
        for case in (DRIFT, ALERT):
            for arm in ("laconic", "baseline"):
                rows = responses(runs, arm, model, case)
                if not rows:
                    continue
                for i in sorted({t for _, t, _, _ in rows}):
                    w = [words(x) for _, t, x, _ in rows if t == i]
                    un = sum(not g for _, t, _, g in rows if t == i)
                    co = sum(bool(closing_offers(x or ""))
                             for _, t, x, _ in rows if t == i)
                    out("  %-6s %-15s %-8s turn %d  n=%-3d median %6.1f  "
                        "max %5d  unread %d  offers %d"
                        % (model, case, arm, i + 1, len(w), median(w),
                           max(w), un, co))
    sdep = depth(runs, "sonnet")
    if sdep:
        out("  depth on sonnet (same statistic, decides nothing): "
            "exp(D) = %.3f, p = %.4f" % (math.exp(sdep[0]), sdep[1]))
    out("")
    out("disclosure: ratios of per-turn medians")
    for i in range(5):
        med = lambda arm, model: median(  # noqa: E731
            [words(x) for _, t, x, _ in responses(runs, arm, model, DRIFT)
             if t == i])
        lo_, lb, ls = med("laconic", "opus"), med("baseline", "opus"), \
            med("laconic", "sonnet")
        if lo_ == lo_ and lb == lb and ls == ls and lb and ls:
            out("  turn %d  opus laconic/baseline %.3f   laconic opus/sonnet "
                "%.3f" % (i + 1, lo_ / lb, lo_ / ls))


def _selftest():
    fails = 0

    def check(name, ok):
        nonlocal fails
        print(("ok   " if ok else "FAIL ") + name)
        fails += not ok

    text = lambda n: " ".join(["word"] * n)  # noqa: E731
    turn = lambda n, read=True: {"text": text(n),  # noqa: E731
                                 "num_turns": 2 if read else 1}

    def sess(arm, rep, lens, model="opus"):
        return {"case": DRIFT, "arm": arm, "model": model, "rep": rep,
                "turns": [turn(x) for x in lens]}

    check("words counts prose", words(text(7)) == 7)
    flat = [sess("laconic", r, [100] * 5) for r in range(6)] + \
           [sess("baseline", r, [300] * 5) for r in range(6)]
    check("no tail, no depth is branch C",
          branch(tail(flat), depth(flat, draws=2000)) == "C")
    check("a resumed duplicate is counted once",
          len(distinct(flat + flat[:1])) == 12)
    grow = [sess("laconic", r, [100, 200, 200, 200, 200]) for r in range(8)] + \
           [sess("baseline", r, [300] * 5) for r in range(8)]
    dep = depth(grow, draws=2000)
    check("laconic growing against a flat baseline is branch B",
          branch(tail(grow), dep) == "B" and dep[1] < 0.01)
    both = [sess("laconic", r, [100, 200, 200, 200, 200]) for r in range(8)] + \
           [sess("baseline", r, [100, 200, 200, 200, 200]) for r in range(8)]
    check("growth the baseline shares is not depth",
          branch(tail(both), depth(both, draws=2000)) == "C")
    long_ = [sess("laconic", r, [700, 100, 100, 100, 100]) for r in range(6)]
    check("one long turn in five is 20% and branch A",
          tail(long_) == (6, 30) and branch(tail(long_), None) == "A")
    alert = {"case": ALERT, "arm": "laconic", "model": "opus", "rep": 0,
             "text": text(900), "num_turns": 2}
    check("the single-turn case pools into the tail",
          tail([alert]) == (1, 1))
    check("sonnet never enters the tail",
          tail([sess("laconic", 0, [900] * 5, "sonnet")]) == (0, 0))
    print("%d failure(s)" % fails)
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(1 if _selftest() else 0)
    if not a.snapshots:
        ap.error("name at least one snapshot")
    runs, versions = sd.load(a.snapshots)
    print("CLI versions: %s" % ", ".join(versions))
    report(runs)


if __name__ == "__main__":
    main()
