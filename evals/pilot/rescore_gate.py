#!/usr/bin/env python3
"""Round 54 bar E: the archive scored under both count gates (#259).

    python3 evals/pilot/rescore_gate.py

Repricing a fatal counter re-scores every round the loop has ever run, so the
standing rule is that no stored round's verdict may move without that being the
round's declared purpose. This is the audit that makes the purpose checkable:
every round pair reconstructible from committed snapshots, scored twice by the
same `report.accept_verdict` — once with `legacy_count_gate=True`, which is the
gate rounds 01 to 53 were actually scored by, and once under the repriced one.

**Only the three Bernoulli fatal counters are read.** A round's overall verdict
also turns on its own target, on `violations_total` and on `turns`, none of
which this change touches, so a round that stops losing `quality_fails` here has
not necessarily become an accept — it has stopped rejecting on this counter.
The distinction matters and the output keeps it: the last column is the round's
target verdict as its own document reports it, not something recomputed here.

**The pairing is not machine-readable anywhere in the repository**, so PAIRS
below carries it explicitly, reconstructed from the round documents. Two
conventions cover almost all of it: rounds 01 to 24 name a baseline and a
snapshot in a header block, and rounds 25 on name an edit tree and a control
tree. Every filename is checked to exist before it is used, and a round whose
pairing could not be recovered is listed as unreachable rather than assumed
unchanged.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import report  # noqa: E402

SNAP = ROOT / "evals" / "snapshots" / "loop"

#: (round, results, judgments, against, against-judgments). None where the
#: round committed no judgments file: never_cut_failures and violations_total
#: are substring counts over the responses and score without one, so such a
#: round is still audited on the counter that actually rejected it.
#:
#: Round 01 is the one inversion, and it is the document's own: the file titled
#: round 01 scores round-02.json, which carries the edit, against round-01.json,
#: which is master. Round 30's fatal verdict came from its never-cut extension
#: rather than from the registered target pair, so that is the pair here.
#: Round 40's judgments were written under round 41's name, which round 41's
#: own document tabulates.
PAIRS = [
    ("01", "round-02.json", "round-02-judgments.json",
     "round-01.json", "round-01-judgments.json"),
    ("03", "round-03.json", "round-03-judgments-v2.json",
     "round-01.json", "round-01-judgments-v2.json"),
    ("04", "round-04.json", "round-04-judgments-v2.json",
     "round-01.json", "round-01-judgments-v2.json"),
    ("05", "round-05.json", "round-05-judgments.json",
     "round-01.json", "round-01-judgments-v2.json"),
    ("06", "round-06.json", "round-06-judgments.json",
     "round-01.json", "round-01-judgments-v2.json"),
    ("07", "round-07.json", "round-07-judgments.json",
     "round-01-n10.json", "round-01-n10-judgments.json"),
    ("08", "round-08.json", "round-08-judgments.json",
     "round-01-n10.json", "round-01-n10-judgments.json"),
    ("09", "round-09.json", "round-09-judgments.json",
     "round-01-n10.json", "round-01-n10-judgments.json"),
    ("10", "round-10.json", "round-10-judgments.json",
     "round-01-n10.json", "round-01-n10-judgments.json"),
    ("11", "round-11.json", "round-11-judgments.json",
     "round-01-n10-v2.json", "round-01-n10-v2-judgments.json"),
    ("12", "round-12.json", "round-12-judgments.json",
     "round-01-n10-v2.json", "round-01-n10-v2-judgments.json"),
    ("14", "round-14.json", "round-14-judgments.json",
     "round-01-n10-v2.json", "round-01-n10-v2-judgments.json"),
    ("15", "round-15.json", "round-15-judgments.json",
     "round-01-n10-v3.json", "round-01-n10-v3-judgments.json"),
    ("16", "round-16.json", "round-16-judgments.json",
     "round-01-n10-v4.json", "round-01-n10-v4-judgments.json"),
    ("17", "round-17.json", "round-17-judgments.json",
     "round-01-n10-v4.json", "round-01-n10-v4-judgments.json"),
    ("18", "round-18.json", "round-18-judgments.json",
     "round-01-n10-v4.json", "round-01-n10-v4-judgments.json"),
    ("19", "round-19.json", "round-19-judgments.json",
     "round-01-n10-v4.json", "round-01-n10-v4-judgments.json"),
    ("20", "round-20.json", "round-20-judgments.json",
     "round-01-n10-v4.json", "round-01-n10-v4-judgments-traps2.json"),
    ("22", "round-22.json", "round-22-judgments.json",
     "round-21.json", "round-21-judgments.json"),
    ("24", "round-24.json", "round-24-judgments.json",
     "round-21.json", "round-21-judgments.json"),
    ("25", "round-25-licence.json", "round-25-licence-judgments.json",
     "round-25-control.json", "round-25-control-judgments.json"),
    ("26", "round-26-licence.json", "round-26-licence-judgments.json",
     "round-26-control.json", "round-26-control-judgments.json"),
    ("28", "round-28-edit.json", "round-28-edit-judgments.json",
     "round-28-control.json", "round-28-control-judgments.json"),
    ("30", "round-30-nevercut-edit.json", None,
     "round-30-nevercut-control.json", None),
    ("31", "round-31-edit.json", None, "round-31-control.json", None),
    ("38", "round-38-edit.json", None,
     "round-38-control.json", "round-38-control-judgments.json"),
    ("40", "round-40-edit.json", "round-41-edit-judgments.json",
     "round-40-control.json", "round-41-control-judgments.json"),
    ("44", "round-44-edit.json", None, "round-44-control.json", None),
    ("45", "round-45-edit.json", None, "round-45-control.json", None),
    ("46", "round-46-edit.json", None, "round-46-control.json", None),
    ("47", "round-47-edit.json", None, "round-47-control.json", None),
    ("48", "round-48-edit.json", None, "round-48-control.json", None),
    ("49", "round-49-edit.json", None, "round-49-control.json", None),
    ("50", "round-50-edit.json", None, "round-50-control.json", None),
    ("51", "round-51-wide-edit.json", "round-51-wide-edit-judgments.json",
     "round-51-wide-control.json", "round-51-wide-control-judgments.json"),
    ("52", "round-52-wide-edit.json", "round-52-wide-edit-judgments.json",
     "round-52-wide-control.json", "round-52-wide-control-judgments.json"),
]

#: Rounds with no reconstructible pair, and why. Printed rather than omitted:
#: a re-score that silently skipped rounds would be indistinguishable from one
#: that found nothing in them.
UNREACHABLE = {
    "02": "no round document; its snapshot is the treatment arm inside round 01",
    "13": "instrument round, re-judged round 12's responses, ran no --against",
    "21": "baseline regeneration, not an edit round",
    "23": "the four files its document names were never committed",
    "27": "stopped before judging; no judgments committed",
    "29": "rejected at stage 1 on the token target; no judgments committed",
    "32": "pilot with no baseline arm",
    "33": "within-snapshot arm contrast, no --against pair",
    "34": "within-snapshot arm contrast, no --against pair",
    "35": "within-snapshot arm contrast, no --against pair",
    "36": "within-snapshot arm contrast, no --against pair",
    "37": "era measurement, proposes no edit",
    "39": "delivery-mode measurement, proposes no edit",
    "41": "within-snapshot arm contrast, no --against pair",
    "42": "within-snapshot arm contrast, no --against pair",
    "43": "judged round 42's snapshot; no --against",
    "53": "draws both blocks from one pool; no --against by construction",
}

#: The three counters this change touches. violations_total is excluded: #103
#: already gave it a round-wide test and round 54 does not touch it.
KEYS = ("never_cut_failures", "quality_fails", "safety_fails")


def load(name):
    p = SNAP / name
    return json.loads(p.read_text()) if p.exists() else None


def judgments(name):
    if not name:
        return None
    raw = load(name)
    if raw is None:
        return None
    return raw["judgments"] if isinstance(raw, dict) else raw


def fatal_lines(prev, cur, rates, legacy):
    """The reason lines the three counters produced, and whether any rejected."""
    _, reasons = report.accept_verdict(prev, cur, "output_tokens",
                                       cell_rates=rates,
                                       legacy_count_gate=legacy)
    labels = {k: dict(report.FATAL)[k] for k in KEYS}
    out, rejected = {}, set()
    for key, label in labels.items():
        for r in reasons:
            if r.startswith("REJECT: %s lost" % label):
                out[key], _ = r, rejected.add(key)
            elif r.startswith("%s rise" % label):
                out[key] = r
    return out, rejected


def main():
    rates = report.load_cell_rates()
    moved, scored, missing = [], 0, []
    print("the archive under both count gates: %d round pairs\n" % len(PAIRS))
    for rnd, res, rjudg, against, ajudg in PAIRS:
        cur_snap, prev_snap = load(res), load(against)
        if cur_snap is None or prev_snap is None:
            missing.append((rnd, res if cur_snap is None else against))
            continue
        cur = report.round_summary(cur_snap, judgments(rjudg))
        prev = report.round_summary(prev_snap, judgments(ajudg))
        old_r, old_rej = fatal_lines(prev, cur, rates, True)
        new_r, new_rej = fatal_lines(prev, cur, rates, False)
        scored += 1
        cleared = sorted(old_rej - new_rej)
        added = sorted(new_rej - old_rej)
        status = "same"
        if added:
            status = "TIGHTENED"
        elif cleared:
            status = "cleared"
        print("round %s  legacy rejects on %-38s -> repriced %s"
              % (rnd, ", ".join(sorted(old_rej)) or "nothing",
                 ", ".join(sorted(new_rej)) or "nothing"))
        if cleared or added:
            moved.append((rnd, cleared, added))
            for key in cleared + added:
                print("    %-18s %d -> %d" % (key, prev[key], cur[key]))
                print("      was: %s" % old_r.get(key, "-")[:150])
                print("      now: %s" % new_r.get(key, "-")[:150])
        if status == "TIGHTENED":
            print("    *** TIGHTENED: bar E declares this fatal to the change")

    print("\nscored %d pairs; %d moved" % (scored, len(moved)))
    tightened = [m for m in moved if m[2]]
    print("rounds that stopped rejecting on a Bernoulli fatal counter: %s"
          % (", ".join(m[0] for m in moved if m[1]) or "none"))
    print("rounds that STARTED rejecting on one: %s"
          % (", ".join(m[0] for m in tightened) or "none"))
    if missing:
        print("\npairs whose files are absent:")
        for rnd, name in missing:
            print("  round %s: %s" % (rnd, name))
    print("\nrounds with no reconstructible pair:")
    for rnd, why in sorted(UNREACHABLE.items()):
        print("  round %s: %s" % (rnd, why))
    return 1 if tightened else 0


if __name__ == "__main__":
    sys.exit(main())
