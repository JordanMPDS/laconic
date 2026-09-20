"""Per-turn closing-offer rates on the `drift-service`/`cold-service` pair.

    python3 evals/results/loop/closing-drift/sweep.py

[#113] reports the no-closing-offers rule breaking on one turn of a real `full`
session and holding on the adjacent one, and argues the binary signal is worth
more than the length signal it accompanies: *"did the last sentence offer to do
more work"* needs no interpretation, where word count does.

`evals/results/loop/closing-offers.md` built the detector and could not answer
that, because the only multi-turn corpus then was `recall-*`, `wide-*` and
`deep-*`, which read **0 of 315 in both arms** - those cases ask analytical
questions about a document, so the deliverable is the answer and there is
nothing to offer. `drift-service` and `cold-service` were authored on
2026-09-01 for exactly this gap and have never been read. This script reads
them.

**It buys nothing.** Every number comes from committed snapshots, so it re-runs
in a second and a reader can check any figure in the write-up against it. See
`../closing-drift-113.md`.

The pair is what makes a depth reading possible at all: the two cases share a
fixture and a byte-identical final question, which `cold-service` asks at turn 1
and `drift-service` at turn 5. Question identity is the confound that would
otherwise swallow the contrast - at fixed depth the two different turn-1
questions differ by 36 points on the unruled arm.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SNAPSHOTS = ROOT / "evals" / "snapshots"

sys.path.insert(0, str(ROOT / "evals" / "bench"))
# The detector under test and the same two-sided exact test the subagent report
# uses, both imported rather than copied: a second implementation of either is a
# second thing to keep correct, and the whole point of this sweep is that it
# scores the shipped detector.
from metrics import closing_offers  # noqa: E402
from subagent import fisher_exact  # noqa: E402

CASES = ("drift-service", "cold-service")

# The rules texts that have ever shipped. Every other cksum in the archive is a
# round's edit arm, which was generated to be rejected and is not the product;
# those runs are counted in a stratum of their own rather than pooled in.
MASTER_CKSUMS = {"136269960", "594915793"}


def corpus():
    """Every distinct `drift-service`/`cold-service` run in the archive.

    Deduplicated on (cksum, arm, case, model, the turn texts). A round that
    shards by model writes the same runs into a per-model file and into the
    union file, so a naive walk counts them twice; `closing-offers.md` was
    bitten by the same thing at the archive scale and records why the rate has
    to be computed over distinct responses. The cksum is in the key so two runs
    at different rules texts are never merged, however alike they read.
    """
    seen, out = set(), []
    for path in sorted(SNAPSHOTS.rglob("*.json")):
        name = path.name
        if "judgment" in name or "preference" in name:
            continue
        try:
            snap = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        runs = snap.get("runs")
        if not isinstance(runs, list):
            continue
        meta = snap.get("metadata", {})
        cksum = str(meta.get("rules_cksum"))
        for run in runs:
            if not isinstance(run, dict) or run.get("case") not in CASES:
                continue
            # A single-turn case stores its response at the top level; a
            # multi-turn one stores a list under `turns`. `cold-service` is the
            # single-turn half of the pair by design.
            turns = run["turns"] if isinstance(run.get("turns"), list) else [run]
            sig = tuple((t.get("text") or "")[:160] for t in turns)
            key = (cksum, run["arm"], run["case"], run["model"], sig)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "cksum": cksum,
                "rules": "master" if cksum in MASTER_CKSUMS else "edit-arm",
                "arm": run["arm"],
                "case": run["case"],
                "model": run["model"],
                "level": meta.get("laconic_level"),
                "delivery": run.get("turn_delivery"),
                "date": (run.get("generated_at") or "")[:10],
                "texts": [t.get("text") or "" for t in turns],
                "source": name,
            })
    return out


def fired(run):
    """The detector's verdict on each turn of one run, in order."""
    return [bool(text) and bool(closing_offers(text)) for text in run["texts"]]


def rate(hits, n):
    return "%3d/%-3d %5.1f%%" % (hits, n, 100.0 * hits / n) if n else "    -    "


def exact_upper_95(n):
    """Clopper-Pearson upper bound for 0 successes in n trials."""
    return 1.0 - 0.05 ** (1.0 / n) if n else 1.0


def trend_p(runs, iters=20000, seed=113):
    """Permutation p for a monotone trend in turn index, within runs.

    The five turn-responses of one run share a session, so they are not five
    independent draws and a test that shuffles them freely would be testing the
    wrong null. This shuffles the turn *order* inside each run and leaves the
    runs alone, which holds each run's own number of offers fixed and asks only
    whether they sit later or earlier than chance puts them. Two-sided on the
    slope of hits against turn index.
    """
    seq = [fired(r) for r in runs if len(r["texts"]) > 1]
    if not seq:
        return None, None

    def slope(rows):
        num = den = 0.0
        for row in rows:
            mean_i = (len(row) - 1) / 2.0
            for i, hit in enumerate(row):
                num += (i - mean_i) * hit
                den += (i - mean_i) ** 2
        return num / den if den else 0.0

    obs = slope(seq)
    rng = random.Random(seed)
    at_least = 0
    for _ in range(iters):
        shuffled = []
        for row in seq:
            row = list(row)
            rng.shuffle(row)
            shuffled.append(row)
        if abs(slope(shuffled)) >= abs(obs) - 1e-12:
            at_least += 1
    return obs, (at_least + 1) / (iters + 1)


def prior_offer_probe(runs):
    """P(offer at turn k+1 | offer at turn k) against the same given no offer.

    This is the one handle the committed data gives on the mechanism that
    competes with session depth: by turn 5 the model has already had four
    chances to offer, and an offer already made might suppress the next one.
    The adjacent pairs inside a run are not independent of each other, so the
    exact test printed beside this is anti-conservative and `clustering_p`
    below is the reading that carries weight.
    """
    after_hit = after_miss = n_hit = n_miss = 0
    for run in runs:
        row = fired(run)
        for prev, nxt in zip(row, row[1:]):
            if prev:
                n_hit += 1
                after_hit += nxt
            else:
                n_miss += 1
                after_miss += nxt
    return (after_hit, n_hit), (after_miss, n_miss)


def clustering_p(runs, iters=20000, seed=113):
    """Is an offer a property of the run or of the turn?

    Under "each turn-response is its own draw" the per-run hit counts are five
    independent Bernoulli trials and their variance is fixed by the pooled
    rate. This reassigns every observed hit across every turn-response in the
    arm, breaking the run boundaries and holding the total fixed, and asks how
    often the per-run counts spread at least as widely as they actually do.
    It is the clustered answer to the question the adjacent-pair table asks
    anti-conservatively, and it needs no independence assumption to be read.
    """
    rows = [fired(r) for r in runs if len(r["texts"]) > 1]
    flat = [hit for row in rows for hit in row]
    sizes = [len(row) for row in rows]
    if not flat or sum(flat) == 0:
        return None, None, None

    def spread(seq):
        out, at = [], 0
        for size in sizes:
            out.append(sum(seq[at:at + size]))
            at += size
        mean = sum(out) / len(out)
        return sum((c - mean) ** 2 for c in out) / len(out), out

    obs, counts = spread(flat)
    rng = random.Random(seed)
    pool = list(flat)
    at_least = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if spread(pool)[0] >= obs - 1e-12:
            at_least += 1
    return obs, (at_least + 1) / (iters + 1), counts


def main():
    runs = corpus()
    print("# closing-offer rates on the drift-service/cold-service pair")
    print("\n%d distinct runs, from committed snapshots only. No generations.\n"
          % len(runs))

    files = sorted({r["source"] for r in runs})
    dates = sorted({r["date"] for r in runs if r["date"]})
    print("snapshots: %s" % ", ".join(files))
    print("dates:     %s to %s" % (dates[0], dates[-1]))
    print("levels:    %s" % ", ".join(sorted({str(r["level"]) for r in runs})))

    print("\n## Per-turn rates\n")
    print("%-14s %-9s %-7s %-9s %-6s %s"
          % ("case", "arm", "model", "rules", "turn", "fired"))
    cells = defaultdict(lambda: [0, 0])
    for run in runs:
        for i, hit in enumerate(fired(run), 1):
            if not run["texts"][i - 1]:
                continue
            cell = cells[(run["case"], run["arm"], run["model"], run["rules"], i)]
            cell[1] += 1
            cell[0] += hit
    for key in sorted(cells):
        hits, n = cells[key]
        print("%-14s %-9s %-7s %-9s turn%-2d %s" % (key + (rate(hits, n),)))

    drift = [r for r in runs if r["case"] == "drift-service"]
    cold = [r for r in runs if r["case"] == "cold-service"]

    def pooled(rows):
        hits = sum(sum(fired(r)) for r in rows)
        n = sum(len([t for t in r["texts"] if t]) for r in rows)
        return hits, n

    print("\n## Reading 1: the arm contrast on drift-service, pooled over turns\n")
    lac = pooled([r for r in drift if r["arm"] == "laconic"])
    base = pooled([r for r in drift if r["arm"] == "baseline"])
    print("laconic  %s" % rate(*lac))
    print("baseline %s" % rate(*base))
    print("Fisher two-sided p = %.3g" % fisher_exact(
        lac[0], lac[1] - lac[0], base[0], base[1] - base[0]))

    print("\n## Reading 2: the ceiling on a within-session rise\n")
    if lac[0] == 0:
        print("laconic fired 0 times in %d turn-responses across all five depths."
              % lac[1])
        print("Clopper-Pearson 95%% upper bound on the rate: %.2f%%"
              % (100 * exact_upper_95(lac[1])))
        master = pooled([r for r in drift
                         if r["arm"] == "laconic" and r["rules"] == "master"])
        print("At shipped rules only: 0 of %d, upper bound %.2f%%"
              % (master[1], 100 * exact_upper_95(master[1])))
    else:
        print("laconic is not at zero: %s - re-read the write-up." % rate(*lac))

    print("\n## Reading 3: the same question at turn 1 and at turn 5\n")
    for arm in ("baseline", "laconic"):
        c = pooled([r for r in cold if r["arm"] == arm])
        d5 = [(sum(fired(r)[4:5]), 1) for r in drift
              if r["arm"] == arm and len(r["texts"]) >= 5 and r["texts"][4]]
        d5 = (sum(x for x, _ in d5), len(d5))
        print("%-9s cold-service turn 1 %s   drift-service turn 5 %s   p = %.3g"
              % (arm, rate(*c), rate(*d5),
                 fisher_exact(c[0], c[1] - c[0], d5[0], d5[1] - d5[0])))
    print("\nThe two questions are byte-identical; the turn-1 questions of the")
    print("two cases are not, and differ by this much on the unruled arm:")
    bc = pooled([r for r in cold if r["arm"] == "baseline"])
    bd1 = [(fired(r)[0], 1) for r in drift if r["arm"] == "baseline"]
    bd1 = (sum(x for x, _ in bd1), len(bd1))
    print("  cold-service turn 1 %s vs drift-service turn 1 %s   p = %.3g"
          % (rate(*bc), rate(*bd1),
             fisher_exact(bc[0], bc[1] - bc[0], bd1[0], bd1[1] - bd1[0])))

    print("\n## Confound 1: is there a trend across the five turns?\n")
    for arm in ("baseline", "laconic"):
        rows = [r for r in drift if r["arm"] == arm]
        obs, p = trend_p(rows)
        if obs is None:
            continue
        print("%-9s slope %+.4f hits per turn index, permutation p = %.3f"
              % (arm, obs, p))

    print("\n## Confound 2: does an offer already made suppress the next one?\n")
    baserows = [r for r in drift if r["arm"] == "baseline"]
    (ah, nh), (am, nm) = prior_offer_probe(baserows)
    print("baseline, next turn offers given this turn did     %s" % rate(ah, nh))
    print("baseline, next turn offers given this turn did not %s" % rate(am, nm))
    print("unclustered Fisher two-sided p = %.3g (anti-conservative)"
          % fisher_exact(ah, nh - ah, am, nm - am))
    print("\nIt does not suppress the next one - it predicts it. The clustered")
    print("version of that reading:\n")

    print("## Reading 4: an offer is a property of the run, not of the turn\n")
    var, p, counts = clustering_p(baserows)
    hist = {k: counts.count(k) for k in range(6)}
    print("baseline per-run offers over 5 turns: %s"
          % ", ".join("%d offers in %d runs" % (k, v)
                      for k, v in sorted(hist.items()) if v))
    expected = 5 * (base[0] / base[1]) * (1 - base[0] / base[1])
    print("variance of per-run counts %.3f against %.3f if each turn were its"
          % (var, expected))
    print("own draw, permutation p %s"
          % ("= %.4f" % p if p > 1.5 / 20001 else "< 1/20001 (no permutation "
             "of 20,000 spread as widely)"))
    print("\nThe permutation reassigns the same hits across the same")
    print("turn-responses with the run boundaries removed, so it assumes no")
    print("independence it does not have.")


if __name__ == "__main__":
    main()
