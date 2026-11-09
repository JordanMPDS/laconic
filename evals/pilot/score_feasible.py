#!/usr/bin/env python3
"""Round 131: does #113's feasibility question run long, or close with an offer?

    python3 evals/pilot/score_feasible.py <snapshot.json>...
    python3 evals/pilot/score_feasible.py --selftest

#113 reports two consecutive feasibility questions about a storage backend,
"is it possible to test this on X?" and "what about on Y instead?", asked deep
in a session co-authoring a design document, answered at about 600 words each,
the first closing with "Want me to write the schema, or add a note to the
spec?". `feasible-replay`, `feasible-shadow` and `feasible-state` are that
session over session-alerting-long's SPEC.md: two co-authoring edits, then the
feasibility pair. `coldfeasible-*` asks each turn-3 question with no session,
which decides nothing.

The unit is the session, because a session's two feasibility answers are not
independent. Over the 30 opus `laconic` sessions, `REPS` a stem:

- **Length fires** when at least `LONG_BAR` sessions carry a feasibility
  answer of at least `RATIO` times the prose words of its `REFERENCE` answer.
  Each reference is the verdict, the constraint that decides it, and the bad
  news a correct answer cannot drop; they were frozen in the registration
  commit, before any generation.
- **Ceremony fires** when at least `OFFER_BAR` sessions carry a closing offer,
  `metrics.closing_offers`, on either feasibility answer.

Both bars come from `evals/bench/precheck.py`, as `round-131.md` records.
Everything else printed is disclosure: per stem and per turn, the 300- and
600-word lines, headings and bold labels, edits on a feasibility turn, every
offer verbatim, and the cold cells beside turn 3.
"""

import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
import metrics  # noqa: E402
from score_compression import words  # noqa: E402

STEMS = ("replay", "shadow", "state")
ARM, MODEL = "laconic", "opus"
ASKED = (2, 3)  # turn indices of the feasibility pair
TURNS = 4
REPS = 10
RATIO = 3
LONG_BAR = 6
OFFER_BAR = 3
LINES = (300, 600)
WRITERS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
HEADING = re.compile(r"^\s*#{1,6}\s", re.M)

REFERENCE = {
    ("replay", 2): (
        "Yes. `govern()` does no I/O (section 5), so the harness only needs the "
        "recorded inputs, and where they are stored does not matter to it. A "
        "SQLite copy holds 90 days easily, at about 290 rows per tenant per "
        "day. One gap: the cycle record stores the inputs `govern()` was given "
        "but not the controller state, so the copy also needs each tenant's "
        "state at the start of the window, or the integral term starts at zero "
        "and the first caps differ from the recorded ones."),
    ("replay", 3): (
        "Yes, for the same reason: the harness reads recorded inputs and "
        "`govern()` never touches storage. DuckDB suits the replay better than "
        "SQLite, because the replay scans whole days in order rather than "
        "reading single rows. It still needs each tenant's starting controller "
        "state."),
    ("shadow", 2): (
        "Not usefully. The supervisor reads each tenant's config from the store "
        "at the start of every cycle (section 8), so against a staging copy the "
        "shadow week computes caps for staging's bands, gains and profiles, not "
        "production's. The replay gate would still pass, because the config is "
        "part of the recorded inputs and replays exactly, so nothing would show "
        "that the week tested the wrong configuration."),
    ("shadow", 3): (
        "Yes. A read replica serves production's own config, so the shadow week "
        "computes the caps production would get. Replication lag only delays a "
        "config change by a cycle or so, well inside the hour the supervisor "
        "already tolerates when the store is down. The store belongs to tenant "
        "operations, so they have to agree to the replica."),
    ("state", 2): (
        "Not without changing the supervisor. Each five-minute run takes a lease "
        "and writes a heartbeat at its start (section 10), so state held in "
        "memory is gone by the next cycle. The integral term would restart at "
        "zero every cycle, and the stale count could never reach three, so a "
        "stale feed would freeze the cap instead of falling back to "
        "`cap_default`."),
    ("state", 3): (
        "Yes. Redis survives between runs, so the integral term and the stale "
        "count carry over as the controller needs. Turn on its persistence, "
        "though: a Redis restart without it wipes every tenant's state at once, "
        "which is the in-memory failure for every tenant in the same cycle."),
}
REF_WORDS = {k: words({"text": v}) for k, v in REFERENCE.items()}


def median(xs):
    return statistics.median(xs) if xs else 0


def load(paths):
    """Completed opus `laconic` runs of the two families, one per key."""
    seen, out = set(), []
    for p in paths:
        for r in json.loads(Path(p).read_text()).get("runs", []):
            case = r.get("case") or ""
            if (not r.get("ok", True) or r.get("arm") != ARM
                    or r.get("model") != MODEL or stem_of(case) is None):
                continue
            if session(case) and len(r.get("turns") or []) != TURNS:
                continue
            key = (case, r.get("arm"), r.get("model"), r.get("rep"))
            if key not in seen:
                seen.add(key)
                out.append(r)
    return out


def stem_of(case):
    for prefix in ("feasible-", "coldfeasible-"):
        if case.startswith(prefix) and case[len(prefix):] in STEMS:
            return case[len(prefix):]
    return None


def session(case):
    return case.startswith("feasible-")


def answers(run):
    """(turn index, turn record) for each feasibility answer in a run."""
    if session(run["case"]):
        return [(i, run["turns"][i]) for i in ASKED]
    return [(ASKED[0], run)]


def ratio(run, idx, turn):
    return words(turn) / REF_WORDS[(stem_of(run["case"]), idx)]


def offers(turn):
    return metrics.closing_offers(turn.get("text") or "")


def wrote(turn):
    return bool(WRITERS & set(turn.get("tools") or []))


def shape(turn):
    prose, _ = metrics.split_text(turn.get("text") or "")
    return (len(HEADING.findall(prose)),
            metrics.structure_markers(prose)["bold_labels"])


def long_run(run):
    return any(ratio(run, i, t) >= RATIO for i, t in answers(run))


def offer_run(run):
    return any(offers(t) for _, t in answers(run))


def verdict(runs):
    """(scored, length fires, ceremony fires) over the session runs."""
    sess = [r for r in runs if session(r["case"])]
    per_stem = {s: sum(1 for r in sess if stem_of(r["case"]) == s) for s in STEMS}
    scored = all(n == REPS for n in per_stem.values())
    long_ = sum(long_run(r) for r in sess)
    offer = sum(offer_run(r) for r in sess)
    return scored, long_, offer, long_ >= LONG_BAR, offer >= OFFER_BAR


def report(runs):
    print("## References (prose words, frozen at registration)")
    for (s, i), n in sorted(REF_WORDS.items()):
        print("   %-7s turn %d  %3d words, long at %d" % (s, i + 1, n, n * RATIO))
    print("## Feasibility answers, opus, laconic")
    print("   %-20s %4s %2s %7s %6s %4s %4s %6s %6s %5s %5s" % (
        "case", "turn", "n", "median", "ratio", ">=3x", ">=%d" % LINES[0],
        ">=%d" % LINES[1], "offers", "heads", "bolds") + "  wrote")
    for prefix in ("feasible-", "coldfeasible-"):
        for s in STEMS:
            rs = [r for r in runs if r["case"] == prefix + s]
            idxs = ASKED if prefix == "feasible-" else ASKED[:1]
            for idx in idxs:
                ts = [(r, t) for r in rs for i, t in answers(r) if i == idx]
                w = [words(t) for _, t in ts]
                q = [ratio(r, idx, t) for r, t in ts]
                sh = [shape(t) for _, t in ts]
                print("   %-20s %4d %2d %7.1f %6.2f %4d %4d %6d %6d %5.1f %5.1f  %d" % (
                    prefix + s, idx + 1, len(ts), median(w), median(q),
                    sum(x >= RATIO for x in q), sum(x >= LINES[0] for x in w),
                    sum(x >= LINES[1] for x in w),
                    sum(bool(offers(t)) for _, t in ts),
                    median([a for a, _ in sh]), median([b for _, b in sh]),
                    sum(wrote(t) for _, t in ts)))
    print("## Every closing offer, verbatim")
    found = False
    for r in runs:
        for idx, t in answers(r):
            for h in offers(t):
                found = True
                print("   %s rep %s turn %d: %s" % (r["case"], r.get("rep"), idx + 1, h))
    if not found:
        print("   none")
    scored, long_, offer, lf, of = verdict(runs)
    print("## Verdict, over the feasible-* sessions (%d a stem expected)" % REPS)
    print("   sessions with a feasibility answer at >= %dx its reference: %d of 30"
          " (fires at %d)" % (RATIO, long_, LONG_BAR))
    print("   sessions with a closing offer on a feasibility answer: %d of 30"
          " (fires at %d)" % (offer, OFFER_BAR))
    if not scored:
        print("   NOT SCORED: a stem does not hold exactly %d sessions" % REPS)
        return 2
    print("## length %s, ceremony %s" % ("FIRES" if lf else "does not fire",
                                         "FIRES" if of else "does not fire"))
    return 0


def selftest():
    def turn(text, tools=()):
        return {"text": text, "tools": list(tools)}

    def run(stem, rep, t3, t4, case="feasible-"):
        r = {"case": case + stem, "arm": ARM, "model": MODEL, "rep": rep, "ok": True}
        if case == "feasible-":
            r["turns"] = [turn("edited", ["Edit"]), turn("edited", ["Edit"]), t3, t4]
            r["text"] = t4["text"]
        else:
            r["text"] = t3["text"]
        return r

    assert all(40 <= n <= 90 for n in REF_WORDS.values()), REF_WORDS
    short, long_ = "Yes, it works. " * 3, "word " * 400
    offer = long_ + "\n\nWant me to add a note to the spec?"
    assert offers(turn(offer)) and not offers(turn(long_))
    runs = [run(s, i, turn(short), turn(short)) for s in STEMS for i in range(REPS)]
    assert verdict(runs) == (True, 0, 0, False, False)
    # A long answer on either turn makes a long session; one session counts once.
    runs[0]["turns"][2] = turn(long_)
    runs[0]["turns"][3] = turn(long_)
    runs[1]["turns"][3] = turn(long_)
    assert verdict(runs)[1] == 2
    for r in runs[2:6]:
        r["turns"][2] = turn(long_)
    assert verdict(runs)[1:4:2] == (6, True)
    # Offers on either feasibility turn; edit turns are not read.
    runs[10]["turns"][0] = turn(offer)
    assert verdict(runs)[2] == 0
    for r in runs[10:13]:
        r["turns"][3] = turn(offer)
    assert verdict(runs)[2::2] == (3, True)
    # Cold runs and other arms or models never enter the verdict.
    cold = [run(s, i, turn(offer), None, "coldfeasible-") for s in STEMS for i in range(5)]
    other = dict(runs[20], arm="baseline")
    assert verdict(runs + cold) == verdict(runs)
    assert stem_of("feasible-cache") is None and stem_of("coldfeasible-state") == "state"
    # A missing session leaves the round unscored.
    assert verdict(runs[1:])[0] is False
    # Headings and bold labels are counted on prose, not inside code.
    assert shape(turn("## A\n**B** text\n```\n## not\n```\n")) == (1, 1)
    # load() keeps one run per key, opus laconic only, complete sessions only.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.json"
        p.write_text(json.dumps({"runs": runs + runs[:3] + cold + [other]
                                 + [dict(runs[0], rep=99, turns=runs[0]["turns"][:3])]}))
        got = load([p])
        assert len(got) == len(runs) + len(cold), len(got)
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        selftest()
        return 0
    if not argv:
        sys.exit(__doc__)
    for p in argv:
        m = json.loads(Path(p).read_text()).get("metadata", {})
        print("%s  rules_cksum %s  cli %s" % (Path(p).name, m.get("rules_cksum"),
                                             m.get("claude_cli_version")))
    return report(load(argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
