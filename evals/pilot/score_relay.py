#!/usr/bin/env python3
"""Round 126: an explanation of a source just read relays the source (#500).

    python3 evals/pilot/score_relay.py precheck <snapshot.json>
    python3 evals/pilot/score_relay.py words <control.json> <edit.json>
    python3 evals/pilot/score_relay.py bounds <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_relay.py holdout <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_relay.py --selftest

#500 is a bare "explain <stage A> and <stage B>" answered at 620 words after
the model read about 125 lines of a spec: it relayed most of the document,
internal identifiers included. `relay-rollout`, `relay-migration` and
`relay-retention` are that question over three two-part specs. Each fixture
plants identifiers no explanation needs (alert ids, tables, flags, jobs,
channels, run times); `RELAY` lists them.

**Precheck, `precheck`:** at master rules on opus, 10 answers a cell, the
defect fires only when both hold over the 30 answers: at least `HALF` run
`LONG` prose words or more (room for the primary), and at least `HALF` carry
`RELAYED` or more of their fixture's planted identifiers (the room is #500's
mechanism, not thoroughness). Each is P(Binomial(30, p) >= 15) at a true
per-answer rate p, printed by `--selftest`'s `fire_probability`.

**Primary, `words`:** prose words fall on the three cells on opus, by
`score_findings_length`'s statistic: a one-sided stratified permutation of the
side label within each cell, on median log words, seed `SEED`.

**Bounds, `bounds`:** the panel pass rate may not fall in any `BOUNDS` cell,
each one-sided Fisher at alpha 0.05, uncorrected, per `AGENTS.md`.
**Holdout, `holdout`:** `score_findings_length.holdout`, unchanged.
"""

import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_findings_length as sfl  # noqa: E402
from score_choice import fall  # noqa: E402
from score_compression import words  # noqa: E402
from score_settled import stratified  # noqa: E402

SEED = 126
LONG = 300
RELAYED = 2
HALF = 15
STEMS = ("rollout", "migration", "retention")
TARGET = tuple(("relay-" + s, "opus") for s in STEMS)
BOUNDS = TARGET + tuple(("relay-" + s, "sonnet") for s in STEMS) + tuple(
    ("explain-" + s, "opus") for s in ("index", "metric", "rollback")) + (
    ("walkthrough", "opus"),)
# Matched case-insensitively as substrings; a run counts each one once.
RELAY = {
    "relay-rollout": (
        "rank-shadow", "search.requests.v3", "ranker_shadow_log",
        "shadow_overlap_daily", "03:10", "ranker_shadow_daily", "RNK-221",
        "RNK-222", "RNK-230", "RNK-240", "RNK-241", "search-ranking-oncall",
        "rk7-2026q4", "search.ranker_v7_pct", "ssr_v2", "exp_assignments",
        "ab_readout_rk7", "06:00", "search-experiments", "rk7_readout"),
    "relay-migration": (
        "pg-orders-1", "orders_outbox", "outbox-relay", "backfill_orders_v2",
        "01:00", "50,000", "order-diff", "order_diff_results", "ORD-310",
        "ORD-311", "ORD-315", "ORD-410", "ORD-411", "commerce-oncall",
        "orders-migration", "orders.read_from_v2", "orders.write_legacy",
        "CHG-4471"),
    "relay-retention": (
        "active_accounts", "session-revoke", "email_suppress", "acctctl",
        "ID-RB-12", "purge_accounts", "02:30", "5,000", "purge_order.yaml",
        "user-media-prod", "purge=1", "purge_ledger", "PRV-104", "PRV-105",
        "PRV-110", "identity-oncall", "purge_verify", "04:00", "DB-RB-03",
        "61,000"),
}


def relayed(run):
    text = (run.get("text") or "").lower()
    return sum(1 for s in RELAY.get(run.get("case"), ()) if s.lower() in text)


def fire_probability(p, n=30, k=HALF):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i)
               for i in range(k, n + 1))


def precheck(cells):
    rs = [r for c in TARGET for r in cells.get(c, [])]
    print("## Precheck: does #500 fire on opus at master rules?")
    for c in TARGET:
        cr = cells.get(c, [])
        print("   %-24s n=%2d  median prose %5.0f  median relayed %4.1f"
              "  long %2d  relaying %2d" % (
                  "/".join(c), len(cr), sfl.median([words(r) for r in cr]),
                  sfl.median([relayed(r) for r in cr]),
                  sum(words(r) >= LONG for r in cr),
                  sum(relayed(r) >= RELAYED for r in cr)))
    long_ = sum(words(r) >= LONG for r in rs)
    relay = sum(relayed(r) >= RELAYED for r in rs)
    ok = len(rs) == 30 and long_ >= HALF and relay >= HALF
    print("   answers >= %d prose words: %d of %d (need %d)"
          % (LONG, long_, len(rs), HALF))
    print("   answers carrying >= %d planted identifiers: %d of %d (need %d)"
          % (RELAYED, relay, len(rs), HALF))
    if len(rs) != 30:
        print("   expected 30 answers: the precheck is not scored")
    print("## %s" % ("FIRES" if ok else "does not fire"))
    return ok


def primary(control, edit, resamples=sfl.RESAMPLES):
    print("## Primary: prose words fall on relay-*/opus, one-sided")
    pairs = []
    for c in TARGET:
        cw = [words(r) for r in control.get(c, [])]
        ew = [words(r) for r in edit.get(c, [])]
        pairs.append(([math.log(max(w, 1)) for w in cw],
                      [math.log(max(w, 1)) for w in ew]))
        print("   %-24s control n=%2d median %5.0f  edit n=%2d median %5.0f"
              % ("/".join(c), len(cw), sfl.median(cw), len(ew), sfl.median(ew)))
    if any(not c or not e for c, e in pairs):
        print("   a cell is empty on one side: the primary is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples)
    ok = p < sfl.ALPHA
    print("   mean log ratio %.3f (factor %.3f)  one-sided p = %.5f  %s"
          % (obs, math.exp(obs), p, "PASSES" if ok else "fails"))
    return ok


def disclose(control, edit):
    sfl.disclose(control, edit)
    print("## Disclosed, deciding nothing: planted identifiers relayed, median")
    for c in TARGET:
        print("   %-24s control %4.1f  edit %4.1f" % (
            "/".join(c), sfl.median([relayed(r) for r in control.get(c, [])]),
            sfl.median([relayed(r) for r in edit.get(c, [])])))


def bounds(c, e):
    print("## Bounds (fatal): the pass rate may not fall, per cell")
    fired = False
    for cell in BOUNDS:
        fired |= fall("/".join(cell), *sfl.passes(c, [cell]),
                      *sfl.passes(e, [cell]))
    print("## %s" % ("bounds hold" if not fired else "reject"))
    return not fired


def selftest():
    fixtures = Path(__file__).resolve().parent
    for case, planted in RELAY.items():
        doc = next((fixtures / case / "fixture").glob("*.md")).read_text().lower()
        missing = [s for s in planted if s.lower() not in doc]
        assert not missing, (case, missing)

    def run(case, n, ids=0):
        return {"case": case, "text": "word " * n + " ".join(RELAY[case][:ids])}
    long_ = {c: [run(c[0], 400, 3) for _ in range(10)] for c in TARGET}
    assert precheck(long_)
    assert not precheck({c: [run(c[0], 400, 0) for _ in range(10)]
                         for c in TARGET})
    assert not precheck({c: [run(c[0], 200, 3) for _ in range(10)]
                         for c in TARGET})
    assert not precheck({TARGET[0]: long_[TARGET[0]]})
    assert relayed({"case": "relay-rollout",
                    "text": "`RNK-221` and rnk-221 and `ssr_v2`"}) == 2
    assert relayed({"case": "walkthrough", "text": "RNK-221"}) == 0
    assert abs(fire_probability(0.5) - 0.5722) < 1e-3
    assert fire_probability(0.3) < 0.02 and fire_probability(0.7) > 0.98
    for p in (0.3, 0.4, 0.5, 0.6, 0.7):
        print("   fire probability per condition at p = %.1f: %.3f"
              % (p, fire_probability(p)))

    big = {c: [{"text": "word " * (400 + i)} for i in range(20)] for c in TARGET}
    small = {c: [{"text": "word " * (180 + i)} for i in range(20)] for c in TARGET}
    assert primary(big, small, resamples=2000)
    assert not primary(big, big, resamples=2000)
    assert not primary(small, big, resamples=2000)

    def t(cells):
        return {c: Counter(v) for c, v in cells.items()}
    full = t({c: ["pass"] * 20 for c in BOUNDS})
    assert bounds(full, full)
    assert not bounds(full, {**full, **t({("walkthrough", "opus"):
                                          ["pass"] * 3 + ["fail"] * 7})})
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if len(argv) == 2 and argv[0] == "precheck":
        meta, cells = sfl.runs(argv[1])
        print("rules_cksum %s  cli %s" % (meta.get("rules_cksum"),
                                          meta.get("claude_cli_version")))
        return 0 if precheck(cells) else 1
    if len(argv) == 3 and argv[0] == "words":
        (cm, c), (em, e) = sfl.runs(argv[1]), sfl.runs(argv[2])
        for name, m in (("control", cm), ("edit", em)):
            print("%-8s rules_cksum %s  cli %s" % (
                name, m.get("rules_cksum"), m.get("claude_cli_version")))
        if cm.get("rules_cksum") == em.get("rules_cksum"):
            print("!! both sides share rules_cksum: this is not a contrast")
            return 1
        ok = primary(c, e)
        disclose(c, e)
        return 0 if ok else 1
    if len(argv) == 3 and argv[0] in ("bounds", "holdout"):
        fn = bounds if argv[0] == "bounds" else sfl.holdout
        return 0 if fn(sfl.tally(argv[1]), sfl.tally(argv[2])) else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
