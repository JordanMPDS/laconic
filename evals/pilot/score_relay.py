#!/usr/bin/env python3
"""Round 126: an explanation of a source just read relays the source (#500).

    python3 evals/pilot/score_relay.py precheck <snapshot.json>
    python3 evals/pilot/score_relay.py words <control.json> <edit.json>
    python3 evals/pilot/score_relay.py bounds <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_relay.py holdout <control-judgments.json> <edit-judgments.json>
    python3 evals/pilot/score_relay.py readability <control.json> <edit.json>
    python3 evals/pilot/score_relay.py identifiers <control.json> <edit.json>
    python3 evals/pilot/score_relay.py longer <control.json> <edit.json>
    python3 evals/pilot/score_relay.py nevercut <control.json> <edit.json>
    python3 evals/pilot/score_relay.py unseen <snapshot.json>
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
**Readability, `readability`, from round 132:** the share of the three cells'
answers with no `metrics.score` violation (an arrow, a shortened word, a
lowercase sentence start) may not fall, pooled, one-sided Fisher at alpha 0.05.
A word cap is the edit likeliest to buy length with grammar.

**Round 133** asks for the planted identifiers themselves, which `words` cannot
see because it drops inline code. **Primary, `identifiers`:** the planted
identifiers relayed fall on `NAMED`, the two cells that still relay them at
round 132's rules, by `stratified` on the per-cell mean count, one-sided: the
count is a small integer, and its ties leave a median too coarse to separate.
It also needs the mean over cells of edit mean / control mean at `MIN_FALL` or
under, because the counts are tight enough that significance alone is cheap.
**Bound, `longer`:** prose words may not rise on the three cells on opus, the
same statistic as `words` with the sides swapped, so an answer that trades
`purge_accounts` for a phrase describing it cannot undo round 132 unseen.
**Bound, `nevercut`:** on every `BOUNDS` cell whose case lists never-cut
keywords, the share of answers carrying all of them may not fall, one-sided
Fisher, because `explain-index` needs `date_trunc` verbatim.

**Round 135, `unseen`:** round 126's bar, unchanged, on `UNSEEN`, three specs
written after round 134 that no rule was drafted against. The snapshot holds
two arms. A case is valid only if the no-rules `baseline` arm reaches
`VALID` of its 10 answers on both conditions, since a case that does not
draw the defect without rules cannot show it is gone with them; the reading
needs two valid cases. On the valid cases' `laconic` answers it reads FIRES
on round 126's bar (half the answers on each condition), GONE when each
condition's one-sided 95% Clopper-Pearson upper bound is under `GONE`, and
OPEN otherwise. Each condition is bounded on its own, so an answer that drops
every identifier and relays the spec in paraphrase is still caught by its
length. `REFERENCE` holds one answer per case, written before generation; its
ratio is printed and decides nothing.
"""

import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_findings_length as sfl  # noqa: E402
from score_choice import fall  # noqa: E402
from score_compression import words  # noqa: E402
from score_settled import stratified  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402

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
    "unseen-trust": (
        "hsm-sec-2", "r2-cross-r1.pem", "ca-bundle-2026q4", "baseimg-nightly",
        "02:15", "gw-stable", "int-r1-07", "trust-audit", "trust_audit_results",
        "bundle_rev", "int-r2-01", "PKI-201", "PKI-202", "pki-oncall",
        "pki.issue_from_r2", "ca-bundle-2027q1", "CHG-9120", "tls_chain_root",
        "PKI-301", "PKI-305"),
    "unseen-pricing": (
        "team_v3_2026", "team_v2_2024", "grandfathered=true",
        "billing_subscriptions", "plan_mix_report", "04:30", "plan_mix_daily",
        "pricing-v3", "BIL-120", "BIL-121", "invoice-svc", "billing-oncall",
        "mig-notice-v3", "migrate_v2_to_v3", "2,000", "V3-BRIDGE", "BIL-210",
        "BIL-215", "team-plan-rollout", "quote_override"),
    "unseen-limits": (
        "quota-gate", "rl-redis-3", "rl.would_reject", "rl_rollup",
        "rl_would_reject_15m", "rl_daily_digest", "03:45", "rl-heads-up-v1",
        "API-150", "API-151", "api-oncall", "rl-observe-board",
        "ratelimit.enforce", "rl_exceptions.yaml", "DEVREL-88", "API-210",
        "API-211", "ratelimit-rollout", "CHG-7731"),
}
# Round 135 (#500): written after round 134 and read by no rule's drafter.
UNSEEN = tuple(("unseen-" + s, "opus") for s in ("trust", "pricing", "limits"))
# Of a case's 10 baseline answers, on each condition, for the case to count.
VALID = 5
# A per-answer rate at which round 126's bar fires on 0.017 of draws: below it
# the bar's own design would withdraw an edit, so the defect is not there.
GONE = 0.30
# Frozen before generation. Each explains both parts and the caveat and names
# none of its fixture's planted identifiers; `selftest` checks both.
REFERENCE = {
    "unseen-trust": (
        "In the cross-signing stage, the new root R2 is created and R1 vouches "
        "for it with a cross-certificate, so anything that trusts only R1 can "
        "still validate R2 chains. A trust bundle holding both roots goes out "
        "to every service image and, on their monthly check-in, to the field "
        "gateways. Certificates are still issued from R1, so nothing depends "
        "on R2 yet. The stage passes when every service endpoint accepts R2, "
        "at least 99.5% of gateways have the new bundle, and 50 canary "
        "certificates from R2 have run 14 days without a handshake failure.\n\n"
        "R1's retirement then moves issuance to R2, drops R1 from the bundle "
        "45 days later, and finally revokes the cross-certificate and "
        "destroys R1's key.\n\n"
        "The caveat is in that 99.5%: it counts only gateways that checked in "
        "during the last 30 days, and 2.3% of the fleet goes more than 90 days "
        "between check-ins. Those keep working through the cross-certificate "
        "until the revocation, then cannot reach the control plane to get the "
        "new bundle and need a site visit. The revocation is the one step "
        "that cannot be undone."),
    "unseen-pricing": (
        "During the grandfather period, new customers can buy only Team v3 at "
        "$15 a seat, while existing v2 customers keep renewing at $12 and may "
        "opt in to v3 early. It lasts at least 60 days and passes if v3 "
        "converts within 10% of v2's rate, churns no more than v2's 2.1% a "
        "month, and pricing tickets stay under 150 a week.\n\n"
        "The forced migration then gives each remaining v2 customer 60 days' "
        "notice and moves them to v3 at their next renewal, with three months "
        "of credit for anyone whose bill rises more than 30%. Custom-quote "
        "accounts are left to their account managers.\n\n"
        "The caveat is annual contracts. Their price is fixed for the term, so "
        "they move only when they renew, and they hold 38% of v2 seats. The "
        "migration therefore takes about a year, not 60 days, and the early "
        "revenue uplift and the 90-day retention figure describe monthly "
        "customers only."),
    "unseen-limits": (
        "In observe mode, the new limiter counts every request against its "
        "key's limit of 600 a minute and records the ones it would have "
        "rejected, but serves all of them. Owners of keys that would be "
        "rejected often are warned so they can fix retry loops. It runs at "
        "least 21 days, including a month-end peak, and passes if under 0.5% "
        "of keys would be rejected on more than 1% of their requests and the "
        "limiter adds under 2 ms at p99.\n\n"
        "Enforce mode then turns rejection on, with a 429 for requests over "
        "the limit, one tier a week: free, then paid, then enterprise. Some "
        "keys get custom limits by signed exception, and each tier can be "
        "rolled back to observe mode within a minute.\n\n"
        "The caveat is that observe mode undercounts at peak. The limiter "
        "fails open when Redis is slow, and Redis is slowest exactly when keys "
        "hit their limits, so 8% of month-end requests went uncounted in the "
        "pilot. Its figures are a floor, and the first enforced month-end is "
        "the first real measurement."),
}
NAMED = (("relay-migration", "opus"), ("relay-retention", "opus"))
# The counts are tight enough that round 132's length bullet moved them 1.4
# identifiers at p < 0.00001 without addressing them, so significance alone is
# no bar: the mean over cells of edit mean / control mean has to reach this.
MIN_FALL = 0.75
EVALS = Path(__file__).resolve().parents[1]


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


def identifiers(control, edit, resamples=sfl.RESAMPLES):
    print("## Primary (round 133): planted identifiers relayed fall, one-sided")
    pairs = []
    for c in NAMED:
        cr = [relayed(r) for r in control.get(c, [])]
        er = [relayed(r) for r in edit.get(c, [])]
        pairs.append((cr, er))
        print("   %-24s control n=%2d mean %5.2f median %4.1f  edit n=%2d mean"
              " %5.2f median %4.1f" % ("/".join(c), len(cr), statistics.fmean(cr or [0]),
                                      sfl.median(cr), len(er),
                                      statistics.fmean(er or [0]), sfl.median(er)))
    if any(not c or not e for c, e in pairs):
        print("   a cell is empty on one side: the primary is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples,
                        centre=statistics.fmean)
    factor = sum(statistics.fmean(e) / max(statistics.fmean(c), 1e-9)
                 for c, e in pairs) / len(pairs)
    ok = p < sfl.ALPHA and factor <= MIN_FALL
    print("   mean difference %+.2f identifiers  one-sided p = %.5f  factor %.3f"
          " (needs <= %.2f)  %s" % (obs, p, factor, MIN_FALL,
                                    "PASSES" if ok else "fails"))
    return ok


def longer(control, edit, resamples=sfl.RESAMPLES):
    print("## Bound (fatal, round 133): prose words may not rise on relay-*/opus")
    logs = lambda rs: [math.log(max(words(r), 1)) for r in rs]  # noqa: E731
    pairs = [(logs(edit.get(c, [])), logs(control.get(c, []))) for c in TARGET]
    if any(not a or not b for a, b in pairs):
        print("   a cell is empty on one side: the bound is not scored")
        return False
    obs, p = stratified(pairs, seed=SEED, resamples=resamples)
    fired = p < sfl.ALPHA
    print("   mean log ratio %.3f (factor %.3f)  one-sided p = %.5f  %s"
          % (-obs, math.exp(-obs), p, "FIRES" if fired else "holds"))
    return not fired


def never_cut(case):
    for d in ("pilot", "cases"):
        p = EVALS / d / case / "expect.json"
        if p.exists():
            return json.loads(p.read_text()).get("never_cut", [])
    return []


def nevercut(control, edit):
    print("## Bound (fatal, round 133): answers keeping every never-cut keyword")
    fired = False
    for cell in BOUNDS:
        kw = never_cut(cell[0])
        if not kw:
            continue
        a, b = control.get(cell, []), edit.get(cell, [])
        keep = lambda rs: sum(  # noqa: E731
            not metrics.never_cut_missing(r.get("text") or "", kw) for r in rs)
        fired |= fall("/".join(cell), keep(a), len(a), keep(b), len(b))
    return not fired


def bounds(c, e):
    print("## Bounds (fatal): the pass rate may not fall, per cell")
    fired = False
    for cell in BOUNDS:
        fired |= fall("/".join(cell), *sfl.passes(c, [cell]),
                      *sfl.passes(e, [cell]))
    print("## %s" % ("bounds hold" if not fired else "reject"))
    return not fired


def readability(control, edit):
    print("## Bound (fatal): answers with no readability violation, relay-*/opus")
    t = [0, 0, 0, 0]
    for c in TARGET:
        a = [metrics.score(r.get("text") or "") for r in control.get(c, [])]
        b = [metrics.score(r.get("text") or "") for r in edit.get(c, [])]
        ca, cb = sum(not x["violations"] for x in a), sum(not x["violations"] for x in b)
        t = [t[0] + ca, t[1] + len(a), t[2] + cb, t[3] + len(b)]
        print("   %-24s clean control %2d/%-2d edit %2d/%-2d  median article rate"
              " control %.3f edit %.3f" % (
                  "/".join(c), ca, len(a), cb, len(b),
                  sfl.median([x["article_rate"] for x in a]),
                  sfl.median([x["article_rate"] for x in b])))
    return not fall("pooled", *t)


def arm_runs(path):
    snap = json.loads(Path(path).read_text())
    out = {}
    for r in snap["runs"]:
        if r.get("ok", True):
            out.setdefault(r.get("arm"), {}).setdefault(
                (r["case"], r["model"]), []).append(r)
    return snap.get("metadata", {}), out


def upper(x, n, alpha=0.05):
    """One-sided Clopper-Pearson upper bound on a rate of x in n."""
    if x >= n:
        return 1.0
    lo, hi = x / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        tail = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i)
                   for i in range(x + 1))
        lo, hi = (mid, hi) if tail > alpha else (lo, mid)
    return hi


def conditions(rs):
    return (sum(words(r) >= LONG for r in rs),
            sum(relayed(r) >= RELAYED for r in rs))


def unseen(arms):
    """Round 135's reading: FIRES, GONE, OPEN, or INVALID."""
    base, lac = arms.get("baseline", {}), arms.get("laconic", {})
    print("## Round 135: does #500 fire on specs no rule was drafted against?")
    for arm, cells in (("baseline", base), ("laconic", lac)):
        for c in UNSEEN:
            cr = cells.get(c, [])
            ref = words({"text": REFERENCE[c[0]]})
            med = sfl.median([words(r) for r in cr]) if cr else 0
            long_, relay = conditions(cr)
            print("   %-8s %-20s n=%2d  median prose %4.0f (%.2fx reference)"
                  "  median relayed %4.1f  long %2d  relaying %2d" % (
                      arm, "/".join(c), len(cr), med, med / ref,
                      sfl.median([relayed(r) for r in cr]) if cr else 0,
                      long_, relay))
    valid = []
    for c in UNSEEN:
        cr = base.get(c, [])
        long_, relay = conditions(cr)
        ok = len(cr) == 10 and long_ >= VALID and relay >= VALID
        print("   %-20s baseline long %2d, relaying %2d of %2d: %s" % (
            "/".join(c), long_, relay, len(cr), "valid" if ok else "INVALID"))
        if ok:
            valid.append(c)
    if len(valid) < 2:
        print("## INVALID: fewer than two cases draw the defect without rules")
        return "INVALID"
    if any(len(lac.get(c, [])) != 10 for c in valid):
        print("## INVALID: a valid case lacks its 10 laconic answers")
        return "INVALID"
    rs = [r for c in valid for r in lac[c]]
    n = len(rs)
    long_, relay = conditions(rs)
    ul, ur = upper(long_, n), upper(relay, n)
    print("   laconic over %d valid answers: >= %d prose words %d (upper %.3f),"
          " >= %d planted identifiers %d (upper %.3f), GONE under %.2f" % (
              n, LONG, long_, ul, RELAYED, relay, ur, GONE))
    if 2 * long_ >= n and 2 * relay >= n:
        verdict = "FIRES"
    elif ul < GONE and ur < GONE:
        verdict = "GONE"
    else:
        verdict = "OPEN"
    print("## %s" % verdict)
    return verdict


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
    prose = {c: [{"text": "The stage runs for a week and passes on latency."}] * 20
             for c in TARGET}
    clipped = {c: [{"text": "stage runs a week \u2192 passes on latency"}] * 20
               for c in TARGET}
    assert metrics.score(clipped[TARGET[0]][0]["text"])["violations"] == 2
    assert readability(prose, prose)
    assert readability(clipped, prose)
    assert not readability(prose, clipped)
    many = {c: [run(c[0], 200, 13) for _ in range(20)] for c in NAMED}
    few = {c: [run(c[0], 200, 3) for _ in range(20)] for c in NAMED}
    assert identifiers(many, few, resamples=2000)
    assert not identifiers(many, many, resamples=2000)
    assert not identifiers(few, many, resamples=2000)
    assert not identifiers(many, {NAMED[0]: few[NAMED[0]]}, resamples=2000)
    most = {c: [run(c[0], 200, 11) for _ in range(20)] for c in NAMED}
    assert not identifiers(many, most, resamples=2000)
    assert longer(big, big, resamples=2000)
    assert longer(big, small, resamples=2000)
    assert not longer(small, big, resamples=2000)
    assert never_cut("explain-index") == ["date_trunc"]
    assert never_cut("walkthrough") == ["401"]
    assert never_cut("relay-rollout") == []
    kept = {("explain-index", "opus"): [{"text": "on date_trunc('day', created_at)"}] * 10,
            ("walkthrough", "opus"): [{"text": "a 401 triggers refresh()"}] * 20}
    dropped = {**kept, ("explain-index", "opus"): [{"text": "on the day"}] * 10}
    assert nevercut(kept, kept)
    assert nevercut(dropped, kept)
    assert not nevercut(kept, dropped)

    for case, planted in RELAY.items():
        prompt = (fixtures / case / "prompt.md").read_text().lower()
        assert not [s for s in planted if s.lower() in prompt], case
    for case, ref in REFERENCE.items():
        assert relayed({"case": case, "text": ref}) == 0, case
    # The counts the registration quotes, against relay-rollout's 163.
    assert {c: words({"text": r}) for c, r in REFERENCE.items()} == {
        "unseen-trust": 177, "unseen-pricing": 146, "unseen-limits": 171}
    assert set(REFERENCE) == {c for c, _ in UNSEEN}
    assert abs(upper(0, 30) - 0.0950) < 1e-3
    assert upper(4, 30) < GONE <= upper(5, 30)

    def arm(n, ids, k=10):
        return {c: [run(c[0], n, ids) for _ in range(k)] for c in UNSEEN}
    drawn = arm(400, 3)
    assert unseen({"baseline": drawn, "laconic": arm(200, 0)}) == "GONE"
    assert unseen({"baseline": drawn, "laconic": drawn}) == "FIRES"
    assert unseen({"baseline": arm(200, 3), "laconic": arm(200, 0)}) == "INVALID"
    assert unseen({"baseline": drawn, "laconic": arm(200, 0, 9)}) == "INVALID"
    some = {c: [run(c[0], 400 if i < 2 else 200, 0) for i in range(10)]
            for c in UNSEEN}
    assert unseen({"baseline": drawn, "laconic": some}) == "OPEN"
    one = {**arm(200, 3), UNSEEN[0]: drawn[UNSEEN[0]]}
    assert unseen({"baseline": one, "laconic": arm(200, 0)}) == "INVALID"
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if len(argv) == 2 and argv[0] == "unseen":
        meta, arms = arm_runs(argv[1])
        print("rules_cksum %s  cli %s" % (meta.get("rules_cksum"),
                                          meta.get("claude_cli_version")))
        return {"GONE": 0, "FIRES": 1, "OPEN": 1}.get(unseen(arms), 2)
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
    if len(argv) == 3 and argv[0] in ("identifiers", "longer", "nevercut"):
        (cm, c), (em, e) = sfl.runs(argv[1]), sfl.runs(argv[2])
        if cm.get("rules_cksum") == em.get("rules_cksum"):
            print("!! both sides share rules_cksum: this is not a contrast")
            return 1
        if argv[0] == "identifiers":
            ok = identifiers(c, e)
            disclose(c, e)
            return 0 if ok else 1
        return 0 if {"longer": longer, "nevercut": nevercut}[argv[0]](c, e) else 1
    if len(argv) == 3 and argv[0] == "readability":
        (_, c), (_, e) = sfl.runs(argv[1]), sfl.runs(argv[2])
        return 0 if readability(c, e) else 1
    if len(argv) == 3 and argv[0] in ("bounds", "holdout"):
        fn = bounds if argv[0] == "bounds" else sfl.holdout
        return 0 if fn(sfl.tally(argv[1]), sfl.tally(argv[2])) else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
