#!/usr/bin/env python3
"""Score round 127: does correcting the metric record move the later turns? (#583)

PR #582 corrected `deep-metric`'s ANALYSIS.md, which every `*-metric` pilot
reads by symlink: the sample its own rates need is roughly 10,000 sessions per
arm, where it had said 34,000. Turn 3 of `deep-`, `register-` and
`fullexplain-metric` asks for the derivation of that figure, and on the old
record almost every answer recomputed it and said the record was wrong. That
dispute then sat in the model's own context for turns 4 and 5, which are what
rounds 67 and 100 measured.

The two snapshots are the two records, generated at once from one harness:
`old` with `--cases-dir` pointed into a worktree at the commit before #582,
`new` from master. Same rules, same CLI window; only the case text differs.

    python3 evals/pilot/score_record.py OLD.json NEW.json \\
        [--judgments OLD-J.json NEW-J.json] [--seed 127]

A side may be several files joined by "+", snapshots and judgments alike.
    python3 evals/pilot/score_record.py --archive SNAPSHOT.json...
    python3 evals/pilot/score_record.py --selftest

`--archive` runs the dispute detector over stored old-record turn-3 answers and
sets it beside the figure #469 counted, which is how the detector was checked
before the round used it.
"""
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from subagent import fisher_exact  # noqa: E402

SEED = 127
FIVE_TURN = ("deep-metric", "register-metric", "fullexplain-metric")
GRADED = FIVE_TURN + ("explain-metric", "wide-index")
#: The per-arm figure each record states, as the turn-3 question quotes it.
#: The side decides it rather than the case files, because the old record
#: lives in a worktree that is removed once the round is scored.
FIGURES = {"old": "34,000", "new": "10,000"}
#: Equivalence margin on the pooled graded-turn ratio, new over old.
MARGIN = (0.80, 1.25)

# Phrases in which "error" or "wrong" is the vocabulary of a power
# calculation or of turn 5's question, not a charge against the record.
NOT_A_CHARGE = re.compile(
    r"standard error|type[ -]?(?:i|ii|1|2) error|error rates?|false[- ]positive"
    r"|wrong (?:metric|estimator|measure)"
    # A missing derivation is not a charge: the new record shows none either.
    r"|reproduce (?:the |its |their |how |the author's )?(?:steps|working|calculation|derivation|author)",
    re.I)
CUE = re.compile(r"""
    \b(?:does\s*n[o']t|do\s*n[o']t|did\s*n[o']t|ca\s*n[o']t|can\s*not|cannot|never|won't)
        \s+(?:\w+\s+){0,3}?
        (?:reach|reproduce|match|produce|arrive|get\s+(?:to|there|near|close)|come\s+close
           |square|follow|add\s+up|hold)
  | \b(?:no|none|nothing)\b[^.\n]{0,80}?\b(?:reach(?:es)?|reproduces?|produces?|comes?\s+close
           |gets?\s+(?:to|there|near|close)|match(?:es)?|arrives?\s+at|lands?\s+(?:on|near)
           |gives?|do|does|works?)\b
  | \btoo\s+(?:high|low|large|small|big)\b | \btimes\s+(?:too|higher|larger|bigger|what)
  | \boverstat | \bunderstat | \binflat | \bdiscrepan | \binconsisten | \berror\b | \btypo\b
  | \bmistake | \bwrong\b | \bincorrect\b | \bmiscalc | \boff\s+by\b | \bfalls?\s+short\b
  | \bcontradict | \bshould\s+be\s+(?:replaced|corrected|revised)
  | \bonly\s+(?:if|when|comes\s+from)\b
""", re.I | re.X)
REFERS = re.compile(r"document|analysis\.md|\brecord\b|author|\bstated\b|\bits\s+figure"
                    r"|\bthe\s+figure|\bthe\s+file\b", re.I)


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?:])\s+|\n+", text or "") if s.strip()]


def against(figure):
    """A different figure set against the record's: "9,600 per arm, not 34,000"."""
    f = re.escape(figure)
    return re.compile(r"\b(?:not|rather\s+than|instead\s+of)\s+(?:about\s+|roughly\s+|the\s+)?%s"
                      r"|\b(?:ca\s*n[o']t|cannot|could\s*n[o']t)\s+get\s+(?:to\s+)?(?:about\s+)?%s"
                      % (f, f), re.I)


def charges(text, figure):
    """The sentences of `text` that charge the record's `figure` with being wrong.

    A sentence counts when it carries a cue and names either the figure or the
    record. Both records are read with the same code; only `figure` differs.
    """
    out = []
    for s in sentences(text):
        if figure not in s and figure.replace(",", "") not in s and not REFERS.search(s):
            continue
        bare = NOT_A_CHARGE.sub(" ", s)
        if CUE.search(bare) or against(figure).search(bare):
            out.append(s.strip())
    return out


def old_detector(text):
    """#469's count: recomputes to 9,000-12,999, or says it falls short of 34,000."""
    nums = [int(n.replace(",", "")) for n in re.findall(r"\b\d{1,2},?\d{3}\b", text or "")]
    return any(9000 <= n <= 12999 for n in nums) or bool(re.search(r"short of 34", text or ""))


def archive(paths):
    seen, rows = set(), defaultdict(lambda: [0, 0, 0, 0])
    for path in paths:
        for r in bench_run.usable(json.loads(Path(path).read_text())["runs"]):
            turns = r.get("turns") or []
            if r["case"] not in FIVE_TURN + ("work-metric", "deepexplain-metric") or len(turns) < 3:
                continue
            key = (r["case"], r["model"], r["arm"], r.get("session_id") or turns[2]["text"][:80])
            if key in seen:
                continue
            seen.add(key)
            t3 = turns[2]["text"]
            row = rows[(r["arm"], r["model"])]
            row[0] += 1
            row[1] += old_detector(t3)
            row[2] += bool(charges(t3, "34,000"))
            row[3] += old_detector(t3) and bool(charges(t3, "34,000"))
    print("%-16s %-7s %6s %10s %10s %6s" % ("arm", "model", "n", "#469", "charges", "both"))
    tot = [0, 0, 0, 0]
    for (arm, model), row in sorted(rows.items()):
        print("%-16s %-7s %6d %10d %10d %6d" % (arm, model, *row))
        tot = [a + b for a, b in zip(tot, row)]
    print("%-16s %-7s %6d %10d %10d %6d" % ("all", "", *tot))


def logged(xs):
    return [math.log(max(x, 1)) for x in xs]


def stratified_shift(old, new):
    """Mean over cells of the difference in mean log words, new minus old."""
    shifts = [sum(logged(new[c])) / len(new[c]) - sum(logged(old[c])) / len(old[c])
              for c in old if old[c] and new.get(c)]
    return sum(shifts) / len(shifts) if shifts else None


def stratified_test(old, new, seed, resamples=50000):
    """Two-sided permutation of the record label inside each cell, and a
    bootstrap 90% interval on the same statistic, resampling inside each cell."""
    obs = stratified_shift(old, new)
    if obs is None:
        return None, None, None
    rng = random.Random(seed)
    cells = [c for c in old if old[c] and new.get(c)]
    hits = 0
    for _ in range(resamples):
        o, n = {}, {}
        for c in cells:
            pool = old[c] + new[c]
            rng.shuffle(pool)
            o[c], n[c] = pool[:len(old[c])], pool[len(old[c]):]
        if abs(stratified_shift(o, n)) >= abs(obs) - 1e-12:
            hits += 1
    boots = []
    for _ in range(5000):
        o = {c: [rng.choice(old[c]) for _ in old[c]] for c in cells}
        n = {c: [rng.choice(new[c]) for _ in new[c]] for c in cells}
        boots.append(stratified_shift(o, n))
    boots.sort()
    ci = (math.exp(boots[int(0.05 * len(boots))]), math.exp(boots[int(0.95 * len(boots)) - 1]))
    return math.exp(obs), (hits + 1) / (resamples + 1), ci


def verdicts(path):
    out = {}
    if not path:
        return out
    for part in path.split("+"):
        for j in json.loads(Path(part).read_text())["judgments"]:
            out[(j["case"], j["model"], j["arm"], j["rep"])] = j.get("verdict")
    return out


def main(argv):
    if argv[:1] == ["--selftest"]:
        return selftest()
    if argv[:1] == ["--archive"]:
        return archive(argv[1:])
    seed = SEED
    if "--seed" in argv:
        i = argv.index("--seed")
        seed = int(argv[i + 1])
        del argv[i:i + 2]
    jpaths = (None, None)
    if "--judgments" in argv:
        i = argv.index("--judgments")
        jpaths = (argv[i + 1], argv[i + 2])
        del argv[i:i + 3]
    if len(argv) != 2:
        sys.exit(__doc__)
    sides = {}
    for name, path, jp in (("old", argv[0], jpaths[0]), ("new", argv[1], jpaths[1])):
        snaps = [json.loads(Path(p).read_text()) for p in path.split("+")]
        figure = FIGURES[name]
        runs = [r for s in snaps for r in bench_run.usable(s["runs"])]
        sides[name] = {"runs": runs, "figure": figure, "verdicts": verdicts(jp),
                       "meta": snaps[0]["metadata"]}
        print("%-4s figure %-7s runs %3d  rules_cksum %s  cases_cksum %s  turn_delivery %s  cli %s"
              % (name, figure, len(runs), snaps[0]["metadata"].get("rules_cksum"),
                 "+".join(str(x["metadata"].get("cases_cksum")) for x in snaps),
                 snaps[0]["metadata"].get("turn_delivery"),
                 sorted({r.get("claude_cli_version", "?") for r in runs})))

    print("\n## 1. Manipulation check: turn-3 answers that charge the record's figure")
    print("%-20s %12s %12s %9s" % ("cell", "old", "new", "Fisher p"))
    tot = {"old": [0, 0], "new": [0, 0]}
    flagged_new = []
    for case in FIVE_TURN:
        got = {}
        for name, s in sides.items():
            rs = [r for r in s["runs"] if r["case"] == case and len(r.get("turns") or []) >= 3]
            hits = [r for r in rs if charges(r["turns"][2]["text"], s["figure"])]
            got[name] = (len(hits), len(rs))
            tot[name][0] += len(hits)
            tot[name][1] += len(rs)
            if name == "new":
                flagged_new += [(case, r["rep"], charges(r["turns"][2]["text"], s["figure"]))
                                for r in hits]
        (a, n1), (b, n2) = got["old"], got["new"]
        print("%-20s %5d / %-4d %5d / %-4d %9.4f"
              % (case, a, n1, b, n2, fisher_exact(a, n1 - a, b, n2 - b)))
    (a, n1), (b, n2) = tot["old"], tot["new"]
    print("%-20s %5d / %-4d %5d / %-4d %9.4f"
          % ("pooled", a, n1, b, n2, fisher_exact(a, n1 - a, b, n2 - b)))
    print("\n   every flagged new-record answer, with the sentences that flagged it:")
    for case, rep, sents in flagged_new:
        print("   %s rep %s" % (case, rep))
        for s in sents:
            print("      > %s" % s[:400])

    for title, turn_of in (("2. Graded turn: prose words", lambda r: -1),
                           ("5. Turn 3: prose words (disclosed)", lambda r: 2)):
        print("\n## %s, by cell" % title)
        print("%-20s %5s %9s %9s %8s %9s" % ("cell", "n", "old", "new", "ratio", "p"))
        words = {"old": {}, "new": {}}
        cases = GRADED if turn_of(None) == -1 else FIVE_TURN
        for case in cases:
            for name, s in sides.items():
                rs = [r for r in s["runs"] if r["case"] == case]
                if turn_of(None) == 2:
                    rs = [r for r in rs if len(r.get("turns") or []) >= 3]
                words[name][case] = [
                    metrics.score((r["turns"][2]["text"] if turn_of(None) == 2 else r.get("text", "")))["words"]
                    for r in rs]
            a, b = words["old"][case], words["new"][case]
            if not a or not b:
                print("%-20s %5s  (a side is empty)" % (case, ""))
                continue
            ma, mb = metrics.median(a), metrics.median(b)
            print("%-20s %2d/%-2d %9.1f %9.1f %8.3f %9.4f"
                  % (case, len(a), len(b), ma, mb, mb / ma if ma else float("nan"),
                     metrics.permutation(a, b, seed)))
        for label, scope in (("the three five-turn cells", FIVE_TURN),
                             ("all cells", cases)):
            o = {c: words["old"][c] for c in scope if c in words["old"]}
            n = {c: words["new"][c] for c in scope if c in words["new"]}
            ratio, p, ci = stratified_test(o, n, seed)
            if ratio is None:
                continue
            inside = MARGIN[0] <= ci[0] and ci[1] <= MARGIN[1]
            print("   pooled over %s: geometric ratio %.3f, 90%% CI [%.3f, %.3f], p = %.4f, "
                  "%s the %.2f-%.2f margin"
                  % (label, ratio, ci[0], ci[1], p, "inside" if inside else "not inside",
                     *MARGIN))

    print("\n## 3. Graded turn: panel verdicts, pass / decided")
    if not all(s["verdicts"] for s in sides.values()):
        print("   (no judgments passed)")
    else:
        print("%-20s %12s %12s %9s" % ("cell", "old", "new", "Fisher p"))
        tot = {"old": [0, 0], "new": [0, 0]}
        for case in GRADED:
            got = {}
            for name, s in sides.items():
                v = [s["verdicts"].get((r["case"], r["model"], r["arm"], r["rep"]))
                     for r in s["runs"] if r["case"] == case]
                decided = [x for x in v if x in ("pass", "fail")]
                got[name] = (decided.count("pass"), len(decided))
                tot[name][0] += got[name][0]
                tot[name][1] += got[name][1]
            (a, n1), (b, n2) = got["old"], got["new"]
            print("%-20s %5d / %-4d %5d / %-4d %9.4f"
                  % (case, a, n1, b, n2, fisher_exact(a, n1 - a, b, n2 - b)))
        (a, n1), (b, n2) = tot["old"], tot["new"]
        print("%-20s %5d / %-4d %5d / %-4d %9.4f"
              % ("pooled", a, n1, b, n2, fisher_exact(a, n1 - a, b, n2 - b)))

    print("\n## 6. wide-index turn 1: answers that put 15.7 million in pages (disclosed)")
    for name, s in sides.items():
        rs = [r for r in s["runs"] if r["case"] == "wide-index" and r.get("turns")]
        pages = sum(bool(re.search(r"15\.7\s*(?:million|M)\s+(?:heap\s+)?pages", r["turns"][0]["text"]))
                    for r in rs)
        print("   %-4s %d / %d" % (name, pages, len(rs)))


def selftest():
    old = ("ANALYSIS.md doesn't show how it got 34,000. The standard calculation gives "
           "about 9,600 per arm, and no standard set of assumptions reaches 34,000.")
    new = ("The document's 10,000 is the standard two-proportion calculation. Step 1: the "
           "standard error of the difference is 0.0029. It gives about 9,600, which "
           "rounds to roughly 10,000. Type II error is 0.2.")
    assert charges(old, "34,000"), charges(old, "34,000")
    assert not charges(new, "10,000"), charges(new, "10,000")
    assert charges("Its figure is roughly 3.5 times too high.", "10,000")
    assert not charges("You concluded lift is the wrong metric.", "10,000")
    assert not charges("The document doesn't show how it got 10,000, so I can't retrace "
                       "its steps or reproduce the author's working.", "10,000")
    assert charges("ANALYSIS.md gives 34,000 and I can't reproduce that number.", "34,000")
    assert old_detector(old) and not old_detector("nothing numeric here")
    assert stratified_shift({"a": [10, 10]}, {"a": [20, 20]}) - math.log(2) < 1e-9
    print("selftest ok")


if __name__ == "__main__":
    main(sys.argv[1:])
