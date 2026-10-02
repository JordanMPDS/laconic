#!/usr/bin/env python3
"""Round 93: #305's narrowing follow-up with an open question, decided on opus.

    python3 evals/pilot/score_subset.py precheck <snap>...
    python3 evals/pilot/score_subset.py compare --control <snap>... --edit <snap>... \
        [--control-judgments <j>] [--edit-judgments <j>]
    python3 evals/pilot/score_subset.py depth --shallow <snap>... --deep <snap>...
    python3 evals/pilot/score_subset.py --selftest

`subset-*` asks "what is left?" over a three-bucket status file, then narrows
to the SPEC bucket. Eight of the SPEC bucket's ten open questions share one
status, so the narrowed answer can count them; #305's defect was naming them
again after the inventory had already named them.

A **re-listing** is a seeded open question the graded turn names that the same
run's turn 1 had already named, by ID (`OQ-14`), by key (`hold_expiry_h`), or
inside an ID range (`OQ-3 to OQ-11`). The whole text is read, code spans
included, because the keys are usually written in backticks.

**precheck** reads master rules only. It fires when at least `FIRE_AT` graded
turns re-list at least `RELIST_AT` of the eight.

**compare** is stage 2. The primary is the mean re-listing count on the graded
turn, edit against control, two-sided permutation; lower is the registered
direction. Three fatal bounds, each one-sided at `ALPHA`: turn 1's inventory
may not get shorter in prose words, may not name fewer of the eight, and the
panel's pass rate on the graded turn may not fall.

**depth** is round 94, at master rules. `deepsubset-*` is `subset-*` with four
turns between the inventory and the narrowing question. It fires when at least
`FIRE_AT` deep graded turns run over `LONG_AT` prose words; the depth contrast
on mean log graded prose words is permuted within stem, two-sided.
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

MODEL = "opus"
SEEDED = {
    "ledger": {3: "posting_batch_size", 7: "idempotency_window_s", 11: "reconcile_interval_s",
               14: "hold_expiry_h", 18: "snapshot_every_n", 21: "fx_quote_ttl_s",
               25: "max_entries_per_txn", 30: "retry_backoff_ms"},
    "scheduler": {2: "lease_ttl_ms", 6: "heartbeat_interval_ms", 10: "max_queue_depth",
                  13: "steal_threshold", 17: "cron_jitter_ms", 20: "dead_letter_after",
                  24: "shard_count", 28: "preempt_grace_s"},
    "gateway": {4: "conn_pool_size", 5: "idle_timeout_s", 12: "rate_burst", 15: "cache_ttl_s",
                19: "circuit_open_ms", 23: "max_header_kb", 26: "retry_budget_pct",
                31: "tls_session_cache"},
}
# Round 96: each IMPL/VAL item, by stem: a description regex matched case-insensitively.
# Lookarounds keep a seeded key (`cron_jitter_ms`) from counting as its item.
ITEMS = {
    "ledger": {
        "IMPL-1": r"multi-?currency", "IMPL-2": r"sweep", "IMPL-3": r"alert",
        "IMPL-4": r"replay", "IMPL-5": r"(?<!_)cach(e|ing)(?!_)", "IMPL-6": r"postgres|in-memory|idempotency (store|table)",
        "IMPL-7": r"adapter", "IMPL-8": r"histogram|posting latency",
        "VAL-1": r"conformance|vectors?\b", "VAL-2": r"audit[- ]trail|ordering", "VAL-3": r"\bCI\b|pull requests?|\bPRs?\b"},
    "scheduler": {
        "IMPL-1": r"reclaim", "IMPL-2": r"steal(?!_)|stealing", "IMPL-3": r"(?<!_)jitter(?!_)",
        "IMPL-4": r"dead[- ]letter|parked|parking", "IMPL-5": r"(?<!_)shard(ing|s)?(?!_)|coordinator",
        "IMPL-6": r"(?<!_)grace(?!_)|preemption", "IMPL-7": r"pause|resume|admin",
        "IMPL-8": r"gauge|queue[- ]depth",
        "VAL-1": r"conformance|vectors?\b", "VAL-2": r"at[- ]most[- ]once", "VAL-3": r"\bCI\b|pull requests?|\bPRs?\b"},
    "gateway": {
        "IMPL-1": r"evict", "IMPL-2": r"(?<!_)burst(?!_)", "IMPL-3": r"response cach|cach(e|ing) (is |has )?(not|n't) (been )?started|\bcache layer",
        "IMPL-4": r"half[- ]open|circuit[- ]breaker", "IMPL-5": r"header (limit|size)|response headers?|headers? (on|in|of) responses",
        "IMPL-6": r"retry budget|unbounded", "IMPL-7": r"resumption|\bTLS\b",
        "IMPL-8": r"histogram|upstream latency",
        "VAL-1": r"conformance|vectors?\b", "VAL-2": r"forwarding", "VAL-3": r"\bCI\b|pull requests?|\bPRs?\b"},
}
ITEM_ID = re.compile(r"\b(IMPL|VAL)-0*(\d+)((?:\s*(?:,\s*and|,|and|&|/)\s*(?:(?:IMPL|VAL)-)?\d+(?!\d))*)")
ITEM_RANGE = re.compile(r"\b(IMPL|VAL)-0*(\d+)\s*(?:–|—|-|to|through)\s*(?:(?:IMPL|VAL)-)?0*(\d+)(?!\d)")
SHORTER_AT = 0.85
RELIST_AT, FIRE_AT = 5, 9
LONG_AT = 150
ALPHA = 0.05
SEED = 93
ID = re.compile(r"\bOQ-0*(\d+)(?!\d)")
# "OQ-3, 7, 11 and 30": bare numbers continuing a list that opened on an ID.
LIST = re.compile(r"\bOQ-\d+((?:\s*(?:,\s*and|,|and|&|/)\s*(?:OQ-)?\d+(?!\d|\.\d))+)")
RANGE = re.compile(r"\bOQ-0*(\d+)\s*(?:–|—|-|\.\.\.?|to|through|thru)\s*(?:OQ-)?0*(\d+)(?!\d)")


def named(text, stem):
    """The seeded open questions `text` names, as a set of their numbers."""
    seeded = SEEDED[stem]
    got = {int(n) for n in ID.findall(text)}
    for tail in LIST.findall(text):
        got.update(int(n) for n in re.findall(r"\d+", tail))
    for a, b in RANGE.findall(text):
        got.update(range(int(a), int(b) + 1))
    got.update(n for n, key in seeded.items() if key in text)
    return got & set(seeded)


def covered(text, stem):
    """The IMPL/VAL items `text` covers, by ID, ID list or range, or by description."""
    got = set()
    for kind, first, tail in ITEM_ID.findall(text):
        got.update("%s-%d" % (kind, int(n)) for n in [first] + re.findall(r"\d+", tail))
    for kind, a, b in ITEM_RANGE.findall(text):
        got.update("%s-%d" % (kind, n) for n in range(int(a), int(b) + 1))
    return {k for k, rx in ITEMS[stem].items() if k in got or re.search(rx, text, re.I)}


def stem_of(r):
    return r["case"].split("-", 1)[1]


def turn_text(r, i):
    return r["turns"][i].get("text") or ""


def relisted(r):
    s = stem_of(r)
    return len(named(r.get("text") or "", s) & named(turn_text(r, 0), s))


def load(paths, family="subset"):
    """Usable laconic `<family>-*` runs on MODEL with every turn, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            fam, _, stem = r.get("case", "").partition("-")
            key = (r.get("case"), r.get("model"), r.get("arm"), r.get("rep"))
            if (key in seen or r.get("arm") != "laconic" or r.get("model") != MODEL
                    or fam != family or stem not in SEEDED or len(r.get("turns") or []) < 2):
                continue
            seen.add(key)
            out.append(r)
    return out


def precheck(runs):
    print("subset-* graded turn on %s, master rules: %d runs" % (MODEL, len(runs)))
    for stem in SEEDED:
        cell = [r for r in runs if stem_of(r) == stem]
        print("  %-10s n=%2d  re-listed median %.1f, >= %d in %2d   turn-1 names median %.1f"
              "   graded words median %6.1f"
              % (stem, len(cell), metrics.median([relisted(r) for r in cell]), RELIST_AT,
                 sum(relisted(r) >= RELIST_AT for r in cell),
                 metrics.median([len(named(turn_text(r, 0), stem)) for r in cell]),
                 metrics.median([words(r) for r in cell])))
    hits = sum(relisted(r) >= RELIST_AT for r in runs)
    fired = hits >= FIRE_AT
    print("\nre-listing >= %d of 8: %d/%d, fires at >= %d: %s"
          % (RELIST_AT, hits, len(runs), FIRE_AT, "FIRES" if fired else "does not fire"))
    return fired


def verdicts(path):
    if not path:
        return {}
    return {(j["case"], j["rep"]): j.get("verdict")
            for j in json.loads(Path(path).read_text())["judgments"]
            if j.get("arm") == "laconic" and j.get("model") == MODEL}


def one_sided_fall(control, edit):
    """One-sided permutation p that `edit`'s mean fell below `control`'s."""
    p = metrics.permutation(control, edit, SEED)
    if p is None:
        return None
    return p / 2 if sum(edit) / len(edit) < sum(control) / len(control) else 1 - p / 2


def compare(control, edit, cj=None, ej=None, coverage=False):
    """Print every bar; return True only if the primary passes and every bound holds.

    `coverage` is round 96's bar 2: turn 1 may not cover fewer IMPL/VAL items, and its
    median prose words may not fall below SHORTER_AT of control's. Round 95's bar 2, a
    one-sided test on mean log prose words, is then disclosed instead of deciding."""
    if not control or not edit:
        print("a side is empty: no verdict")
        return False
    rc, re_ = [relisted(r) for r in control], [relisted(r) for r in edit]
    p = metrics.permutation(rc, re_, SEED)
    mc, me = sum(rc) / len(rc), sum(re_) / len(re_)
    primary = me < mc and p < ALPHA
    print("primary: mean re-listed control %.2f, edit %.2f, two-sided p = %.4f: %s"
          % (mc, me, p, "PASS" if primary else "fail"))
    print("disclosed: graded prose words median control %.1f, edit %.1f"
          % (metrics.median([words(r) for r in control]), metrics.median([words(r) for r in edit])))

    holds = True
    bounds = [("turn-1 inventory log prose words",
               lambda r: math.log(max(words(r["turns"][0]), 1))),
              ("turn-1 seeded questions named", lambda r: len(named(turn_text(r, 0), stem_of(r))))]
    if coverage:
        bounds.insert(1, ("turn-1 IMPL/VAL items covered",
                          lambda r: len(covered(turn_text(r, 0), stem_of(r)))))
    for label, f in bounds:
        c, e = [f(r) for r in control], [f(r) for r in edit]
        p1 = one_sided_fall(c, e)
        ok = p1 is None or p1 >= ALPHA
        disclosed = coverage and label.endswith("prose words")
        if not disclosed:
            holds &= ok
        print("%s, %s: control mean %.2f, edit mean %.2f, one-sided p = %s: %s"
              % ("disclosed" if disclosed else "bound", label, sum(c) / len(c), sum(e) / len(e),
                 "n/a" if p1 is None else "%.4f" % p1,
                 "-" if disclosed else "holds" if ok else "FATAL"))
    if coverage:
        mc1 = metrics.median([words(r["turns"][0]) for r in control])
        me1 = metrics.median([words(r["turns"][0]) for r in edit])
        ok = me1 >= SHORTER_AT * mc1
        holds &= ok
        print("bound, turn-1 median prose words: control %.1f, edit %.1f, ratio %.3f, floor %.2f: %s"
              % (mc1, me1, me1 / mc1, SHORTER_AT, "holds" if ok else "FATAL"))

    vc, ve = verdicts(cj), verdicts(ej)
    if vc and ve:
        def rate(v, runs):
            got = [v.get((r["case"], r["rep"])) for r in runs]
            got = [g for g in got if g in ("pass", "fail")]
            return sum(g == "pass" for g in got), len(got)
        a, n1 = rate(vc, control)
        c, n2 = rate(ve, edit)
        pq = fisher_one_sided_fall(a, n1, c, n2)
        ok = pq >= ALPHA
        holds &= ok
        print("bound, graded-turn quality: control %d/%d, edit %d/%d, one-sided p = %.4f: %s"
              % (a, n1, c, n2, pq, "holds" if ok else "FATAL"))
    else:
        print("bound, quality: not read (no judgments passed)")
    return primary and holds


def blocked_log_shift(shallow, deep):
    """Mean over stems of deep's mean log graded words minus shallow's."""
    shifts = []
    for stem in SEEDED:
        a = [math.log(max(words(r), 1)) for r in shallow if stem_of(r) == stem]
        b = [math.log(max(words(r), 1)) for r in deep if stem_of(r) == stem]
        if a and b:
            shifts.append(sum(b) / len(b) - sum(a) / len(a))
    return sum(shifts) / len(shifts) if shifts else None


def blocked_permutation(shallow, deep, seed=94, resamples=20000):
    """Two-sided p for blocked_log_shift, shuffling the depth label inside each stem."""
    obs = blocked_log_shift(shallow, deep)
    if obs is None:
        return None, None
    rng = random.Random(seed)
    pools = {s: ([r for r in shallow if stem_of(r) == s] + [r for r in deep if stem_of(r) == s],
                 sum(stem_of(r) == s for r in shallow)) for s in SEEDED}
    hits = 0
    for _ in range(resamples):
        a, b = [], []
        for pool, n in pools.values():
            rng.shuffle(pool)
            a += pool[:n]
            b += pool[n:]
        if abs(blocked_log_shift(a, b)) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (resamples + 1)


def depth(shallow, deep):
    """Round 94: does session depth produce #305's length? True when deep fires."""
    print("graded turn on %s, master rules: shallow %d runs, deep %d runs"
          % (MODEL, len(shallow), len(deep)))
    print("  %-10s %-7s %3s %13s %10s %14s %8s" % (
        "stem", "depth", "n", "words median", "> %d" % LONG_AT, "re-listed >= %d" % RELIST_AT,
        "wrote"))
    for stem in SEEDED:
        for label, runs in (("shallow", shallow), ("deep", deep)):
            cell = [r for r in runs if stem_of(r) == stem]
            print("  %-10s %-7s %3d %13.1f %10d %14d %8d" % (
                stem, label, len(cell), metrics.median([words(r) for r in cell]),
                sum(words(r) > LONG_AT for r in cell),
                sum(relisted(r) >= RELIST_AT for r in cell),
                sum(bool(r.get("artifacts")) for r in cell)))
    long_s = sum(words(r) > LONG_AT for r in shallow)
    long_d = sum(words(r) > LONG_AT for r in deep)
    fired = long_d >= FIRE_AT
    print("\ndeep graded turns over %d prose words: %d/%d, fires at >= %d: %s"
          % (LONG_AT, long_d, len(deep), FIRE_AT, "FIRES" if fired else "does not fire"))
    print("disclosed: shallow graded turns over %d prose words: %d/%d"
          % (LONG_AT, long_s, len(shallow)))
    obs, p = blocked_permutation(shallow, deep)
    if obs is not None:
        print("depth contrast, mean log graded words, within stem: deep - shallow %+.3f "
              "(x%.2f), two-sided p = %.4f" % (obs, math.exp(obs), p))
    return fired


def selftest():
    assert named("OQ-14 and `hold_expiry_h` and OQ-03", "ledger") == {3, 14}
    assert named("OQ-3 to OQ-11 are seeded", "ledger") == {3, 7, 11}
    assert named("OQ-3–11", "ledger") == {3, 7, 11}
    assert named("OQ-9 and OQ-27 are deliberate", "ledger") == set()
    assert named("OQ-140", "ledger") == set()
    assert named("OQ-3, 7, 11, 14, 18, 21, 25 and 30 wait", "ledger") == set(SEEDED["ledger"])
    assert named("OQ-2, 6, 10, 13, 17, 20, 24, and 28.", "scheduler") == set(SEEDED["scheduler"])
    assert named("OQ-3, then 7.5 seconds", "ledger") == {3}
    listing = " ".join("OQ-%d" % n for n in SEEDED["ledger"])

    def run(rep, graded, t1=listing, t1_words=300):
        t1_text = t1 + " " + " ".join(["word"] * t1_words)
        return {"ok": True, "arm": "laconic", "model": MODEL, "case": "subset-ledger",
                "rep": rep, "text": graded,
                "turns": [{"text": t1_text}, {"text": graded}]}
    assert relisted(run(0, listing)) == 8
    assert relisted(run(0, listing, t1="nothing named")) == 0
    assert relisted(run(0, "Eight seeded values await the load test.")) == 0
    assert precheck([run(i, listing if i < 9 else "eight seeded") for i in range(30)])
    assert not precheck([run(i, listing if i < 8 else "eight seeded") for i in range(30)])
    ctl = [run(i, listing) for i in range(30)]
    good = [run(i, "Eight seeded values; OQ-9 and OQ-27 deliberate.") for i in range(30)]
    assert compare(ctl, good)
    assert not compare(ctl, ctl)
    assert not compare(ctl, [run(i, "eight", t1_words=20) for i in range(30)])
    assert not compare(ctl, [run(i, "eight", t1="OQ-3 only") for i in range(30)])
    assert covered("IMPL-1 to IMPL-8 are open; VAL-1, 2 and 3 fail", "ledger") == set(ITEMS["ledger"])
    assert covered("`cron_jitter_ms`, `shard_count`, `preempt_grace_s`", "scheduler") == set()
    assert covered("no jitter yet, work stealing not started", "scheduler") == {"IMPL-2", "IMPL-3"}
    inv = "IMPL-1 to IMPL-8 open; VAL-1 to VAL-3 open. " + listing
    ctl = [run(i, listing, t1=inv) for i in range(30)]
    assert compare(ctl, [run(i, "eight", t1=inv, t1_words=280) for i in range(30)], coverage=True)
    assert not compare(ctl, [run(i, "eight", t1=inv, t1_words=200) for i in range(30)], coverage=True)
    assert not compare(ctl, [run(i, "eight", t1=inv.replace("IMPL-1 to IMPL-8", "IMPL-1"))
                             for i in range(30)], coverage=True)

    def deep_run(rep, n_words, stem="ledger"):
        r = run(rep, " ".join(["word"] * n_words))
        r["case"] = "deepsubset-" + stem
        return r
    shallow = [dict(run(i, " ".join(["word"] * 50)), case="subset-" + st)
               for i in range(10) for st in SEEDED]
    assert depth(shallow, [deep_run(i, 300 if i % 3 == 0 else 50, st)
                           for i in range(10) for st in SEEDED])
    assert not depth(shallow, [deep_run(i, 300 if i < 2 else 50, st)
                               for i in range(10) for st in SEEDED])
    obs, p = blocked_permutation(shallow, [deep_run(i, 300, st) for i in range(10) for st in SEEDED])
    assert obs > 1.7 and p < 0.001
    obs, p = blocked_permutation(shallow, [deep_run(i, 50, st) for i in range(10) for st in SEEDED])
    assert obs == 0 and p == 1
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["precheck"] and len(argv) > 1:
        precheck(load(argv[1:]))
        return
    if argv[:1] in (["compare"], ["depth"]):
        opts, cur = {}, None
        for a in argv[1:]:
            if a.startswith("--"):
                cur = a
                opts.setdefault(cur, [])
            else:
                opts[cur].append(a)
        if argv[0] == "depth":
            depth(load(opts["--shallow"]), load(opts["--deep"], "deepsubset"))
            return
        ok = compare(load(opts["--control"]), load(opts["--edit"]),
                     (opts.get("--control-judgments") or [None])[0],
                     (opts.get("--edit-judgments") or [None])[0],
                     "--coverage" in opts)
        sys.exit(0 if ok else 1)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
