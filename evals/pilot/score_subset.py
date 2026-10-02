#!/usr/bin/env python3
"""Round 93: #305's narrowing follow-up with an open question, decided on opus.

    python3 evals/pilot/score_subset.py precheck <snap>...
    python3 evals/pilot/score_subset.py compare --control <snap>... --edit <snap>... \
        [--control-judgments <j>] [--edit-judgments <j>]
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
"""
import json
import math
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
RELIST_AT, FIRE_AT = 5, 9
ALPHA = 0.05
SEED = 93
ID = re.compile(r"\bOQ-0*(\d+)(?!\d)")
RANGE = re.compile(r"\bOQ-0*(\d+)\s*(?:–|—|-|\.\.\.?|to|through|thru)\s*(?:OQ-)?0*(\d+)(?!\d)")


def named(text, stem):
    """The seeded open questions `text` names, as a set of their numbers."""
    seeded = SEEDED[stem]
    got = {int(n) for n in ID.findall(text)}
    for a, b in RANGE.findall(text):
        got.update(range(int(a), int(b) + 1))
    got.update(n for n, key in seeded.items() if key in text)
    return got & set(seeded)


def stem_of(r):
    return r["case"].split("-", 1)[1]


def turn_text(r, i):
    return r["turns"][i].get("text") or ""


def relisted(r):
    s = stem_of(r)
    return len(named(r.get("text") or "", s) & named(turn_text(r, 0), s))


def load(paths):
    """Usable laconic `subset-*` runs on MODEL with both turns, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in bench_run.usable(json.loads(Path(p).read_text())["runs"]):
            fam, _, stem = r.get("case", "").partition("-")
            key = (r.get("case"), r.get("model"), r.get("arm"), r.get("rep"))
            if (key in seen or r.get("arm") != "laconic" or r.get("model") != MODEL
                    or fam != "subset" or stem not in SEEDED or len(r.get("turns") or []) < 2):
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


def compare(control, edit, cj=None, ej=None):
    """Print every bar; return True only if the primary passes and every bound holds."""
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
    for label, f in (("turn-1 inventory log prose words",
                      lambda r: math.log(max(words(r["turns"][0]), 1))),
                     ("turn-1 seeded questions named", lambda r: len(named(turn_text(r, 0), stem_of(r))))):
        c, e = [f(r) for r in control], [f(r) for r in edit]
        p1 = one_sided_fall(c, e)
        ok = p1 is None or p1 >= ALPHA
        holds &= ok
        print("bound, %s: control mean %.2f, edit mean %.2f, one-sided p = %.4f: %s"
              % (label, sum(c) / len(c), sum(e) / len(e), p1, "holds" if ok else "FATAL"))

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


def selftest():
    assert named("OQ-14 and `hold_expiry_h` and OQ-03", "ledger") == {3, 14}
    assert named("OQ-3 to OQ-11 are seeded", "ledger") == {3, 7, 11}
    assert named("OQ-3–11", "ledger") == {3, 7, 11}
    assert named("OQ-9 and OQ-27 are deliberate", "ledger") == set()
    assert named("OQ-140", "ledger") == set()
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
    print("\nselftest ok")


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["precheck"] and len(argv) > 1:
        precheck(load(argv[1:]))
        return
    if argv[:1] == ["compare"]:
        opts, cur = {}, None
        for a in argv[1:]:
            if a.startswith("--"):
                cur = a
                opts.setdefault(cur, [])
            else:
                opts[cur].append(a)
        ok = compare(load(opts["--control"]), load(opts["--edit"]),
                     (opts.get("--control-judgments") or [None])[0],
                     (opts.get("--edit-judgments") or [None])[0])
        sys.exit(0 if ok else 1)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
