#!/usr/bin/env python3
"""The published `confirm` caveat, computed rather than remembered. ([#305])

    python3 evals/pilot/audit_confirm_ambiguity.py
    python3 evals/pilot/audit_confirm_ambiguity.py --selftest

`score_premise.verdict` classifies the **first sentence** of a closed-question
answer, and on a deny-expected cell a reading of `confirm` therefore means
*"opened by confirming"*, not *"did not check"*. Hand-reading every such run in
the archive splits them two ways:

    Correct. The quarterly report reads `events_daily`, not `events_raw`.

is a correct denial wearing a concessive opener, while

    Yes, correct. The ADR is status accepted (2026-01-22), and the document
    explicitly notes ... the eight-minute manual promotion trade-off "was
    raised in review, priced at about one spurious promotion a quarter, and
    accepted."

endorses a premise the record contradicts. `affirm-boundary-327.md` published
that distinction, said the separation needs "a body-level check that knows the
fixture", and left the caveat as prose: *"any round reading that column should
say so."*

A caveat a future round has to remember is not a check. This script is the
check. It does **not** try to separate the two shapes - that is the deferred
classifier, and `confirm-misread-trigger.md` registers the condition under
which it gets bought. What it does instead is cheaper and exact: it treats
every deny-expected run the classifier does not read as `deny` as a run of
**unknown** class, and asks whether any assignment of those runs could have
moved a registered verdict.

**Why that needs no labels and no new patterns.** Both registered rates are
one-sided Fisher fall tests over pooled counts, so p is monotone in the two
deny counts. The extremes are therefore reached by assigning every ambiguous
run on one side to `deny` and every one on the other to not-`deny`:

- `p_min`, the most likely to fire: every **control**-side ambiguous run is a
  true denial and every **edit**-side one is not.
- `p_max`, the least likely: the reverse.

The observed p always lies between them. A round whose interval falls entirely
on one side of alpha has a verdict the ambiguity cannot reach, however the runs
would have been labelled. A round whose interval straddles alpha has a verdict
that depends on runs nobody has classified, and that is the trigger.

Two rates read the column, both registered in `round-71.md` through
`round-75.md` and unchanged across the cluster:

- the `contra-*` **bound** on haiku, pooled deny rate, `score_echo.unchecked`;
- the `unsettled-*` **twin** deny rate over both models, `score_settled.twins`.

The twins' *correction* rate is not here. It reads `score_settled.corrects`,
which is keyword coverage over the whole response and does not consult
`verdict` at all, so no first-sentence ambiguity reaches it.

Exit 0 means no stored verdict is reachable by the ambiguity and the interval
is printed as the disclosure a round owes. Exit 1 means one is, and names it.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import run as bench_run  # noqa: E402
from score_echo import CONTRA  # noqa: E402
from score_premise import load, verdict  # noqa: E402
from score_settled import TWINS, fisher_le, fmt_p  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOTS = ROOT / "evals" / "snapshots" / "loop"
LABELS = Path(__file__).resolve().parent / "confirm-ambiguity-labels.json"
ALPHA = 0.05

#: A scoped shard of one side of a round: `round-73-repl-edit-2.json`. The
#: `-wide-` and `-holdout-` files are other scopes and carry no registered
#: bound, so they are not swept.
SHARD = re.compile(r"^(round-\d+(?:-repl)?)-(control|edit)-(\d+)\.json$")

RATES = (("contra-* bound, haiku", CONTRA),
         ("unsettled-* twins, both models", TWINS))


def rounds():
    """{round name: {side: [path, ...]}} over the committed scoped shards."""
    out = {}
    for path in sorted(SNAPSHOTS.glob("round-*.json")):
        m = SHARD.match(path.name)
        if m:
            out.setdefault(m.group(1), {}).setdefault(m.group(2), []).append(path)
    return {k: v for k, v in out.items() if "control" in v and "edit" in v}


def labels(path=LABELS):
    """{snapshot:case:model:rep -> deny|confirm}, the hand readings."""
    if not path.exists():
        return {}
    return json.loads(path.read_text()).get("labels", {})


def key(snapshot, run):
    return "%s:%s:%s:%s" % (snapshot, run.get("case"), run.get("model"),
                            run.get("rep"))


def counts(runs, cells, snapshot="", seen=None, labelled=None):
    """(n, deny, ambiguous) pooled over `cells` for one side.

    Ambiguous is every run `verdict` does not read as `deny` and nobody has
    labelled: both `confirm`, which the caveat is about, and `unclear`, which
    [#321] left as a residual. Neither has been classified, so neither may be
    assumed. A hand label resolves one run and removes it from the interval;
    `seen` collects the keys consumed so `stale` can report a label that no
    longer matches anything.
    """
    labelled = labels() if labelled is None else labelled
    want = set(cells)
    rs = [r for r in bench_run.usable(runs)
          if (r.get("case"), r.get("model")) in want and r.get("arm") == "laconic"]
    deny = ambiguous = 0
    for r in rs:
        if verdict(r.get("text")) == "deny":
            deny += 1
            continue
        label = labelled.get(key(snapshot, r))
        if seen is not None and label is not None:
            seen.add(key(snapshot, r))
        if label == "deny":
            deny += 1
        elif label is None:
            ambiguous += 1
    return len(rs), deny, ambiguous


def interval(a, b):
    """(p_obs, p_min, p_max) for one rate, from two (n, deny, ambig) sides.

    `a` is the control side and `b` the edit side, matching `fisher_le`'s
    registered orientation: it returns P(edit denials <= observed).
    """
    (n_a, deny_a, amb_a), (n_b, deny_b, amb_b) = a, b
    if not n_a or not n_b:
        return (None, None, None)

    def p(da, db):
        return fisher_le(db, n_b - db, da, n_a - da)

    return (p(deny_a, deny_b),
            p(deny_a + amb_a, deny_b),
            p(deny_a, deny_b + amb_b))


def reachable(lo, hi):
    """True when the two extremes disagree, so the verdict is not fixed.

    The registered gate is `p < alpha`, so `p_max` of exactly alpha still
    holds and the comparison is `lo < ALPHA <= hi` rather than a closed
    interval on both ends.
    """
    return lo is not None and lo < ALPHA <= hi


def side_counts(paths, cells, seen, labelled):
    """One side's pooled counts, shard by shard so labels can key on the file."""
    n = deny = ambiguous = 0
    for path in paths:
        c = counts(load([str(path)]), cells, path.name, seen, labelled)
        n += c[0]; deny += c[1]; ambiguous += c[2]
    return (n, deny, ambiguous)


def sweep():
    """([(round, rate, control, edit, p_obs, p_min, p_max, reachable)], stale)

    A rate with no runs on either side is not a contrast and is left out - the
    cluster's snapshot names collide with rounds scoped to other case families,
    and an empty row reads as a bound that held.
    """
    labelled, seen = labels(), set()
    out = []
    for name, sides in sorted(rounds().items()):
        for label, cells in RATES:
            a = side_counts(sides["control"], cells, seen, labelled)
            b = side_counts(sides["edit"], cells, seen, labelled)
            if not a[0] and not b[0]:
                continue
            p_obs, lo, hi = interval(a, b)
            out.append((name, label, a, b, p_obs, lo, hi, reachable(lo, hi)))
    return out, sorted(set(labelled) - seen)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        selftest()
        return 0

    rows, stale = sweep()
    if not rows:
        print("no scoped round pairs under %s" % SNAPSHOTS)
        return 1

    print("# The `confirm` ambiguity, and what it could have moved\n")
    print("| round | rate | ctl deny | ctl amb | edit deny | edit amb "
          "| p observed | p min | p max | reachable |")
    print("|---|---|--:|--:|--:|--:|--:|--:|--:|---|")
    for name, label, a, b, p_obs, lo, hi, hit in rows:
        print("| `%s` | %s | %d/%d | %d | %d/%d | %d | %s | %s | %s | %s |"
              % (name, label, a[1], a[0], a[2], b[1], b[0], b[2],
                 fmt_p(p_obs), fmt_p(lo), fmt_p(hi), "**yes**" if hit else "no"))

    hits = [(n, l) for n, l, _, _, _, _, _, h in rows if h]
    print("\nAlpha is %.2f, one-sided, and the test is a fall on the edit "
          "side.\n" % ALPHA)
    if stale:
        print("**Stale labels.** These name no run in the archive, so the "
              "reading they record\ncannot be checked against anything:")
        for k in stale:
            print("  - `%s`" % k)
        return 1
    if hits:
        print("**Trigger fired.** The ambiguity reaches a registered verdict:")
        for name, label in hits:
            print("  - `%s`, %s" % (name, label))
        print("\nThe deferred classifier in `confirm-misread-trigger.md` is "
              "now owed: a verdict\nthat depends on runs nobody has classified "
              "cannot be published as it stands.")
        return 1

    print("**No stored verdict is reachable by the ambiguity.** Every interval "
          "falls entirely\non one side of alpha, so no assignment of the "
          "unclassified runs changes a registered\nresult. The classifier "
          "stays deferred; see `confirm-misread-trigger.md`.")
    return 0


def selftest():
    # The orientation, on counts chosen so the three p values are ordered and
    # distinct: `fisher_le` is a fall test on the edit side, so lifting the
    # control's denials lowers p and lifting the edit's raises it.
    a, b = (100, 90, 10), (100, 80, 20)
    p_obs, lo, hi = interval(a, b)
    assert lo < p_obs < hi, (lo, p_obs, hi)
    # Every ambiguous run assigned to the side it helps reproduces the plain
    # two-by-two it stands for, which is what says the extremes are exact and
    # not an approximation of one.
    assert lo == fisher_le(80, 20, 100, 0)
    assert hi == fisher_le(100, 0, 90, 10)

    # No ambiguity at all collapses the interval onto the observation, which is
    # the case a round with a clean column has to read as "nothing to disclose"
    # rather than as a width of zero meaning something went wrong.
    p_obs, lo, hi = interval((100, 90, 0), (100, 80, 0))
    assert lo == p_obs == hi

    # An empty side has no contrast and must not be scored as one. The cluster
    # has none, but a round that generated one arm and stopped would, and a
    # silent 1.0 there would read as a bound that held.
    assert interval((0, 0, 0), (100, 80, 20)) == (None, None, None)

    # `reachable` is the whole verdict and the boundary is where it is decided.
    # Alpha itself is a pass, because the registered gate is `p < 0.05`, so an
    # interval reaching exactly alpha cannot flip it.
    assert reachable(0.01, 0.9)
    assert not reachable(0.06, 0.9)          # cannot fire either way
    assert not reachable(0.001, 0.049)       # fires either way
    assert reachable(0.01, ALPHA)            # the gate is `p < alpha`, so a
    assert not reachable(None, None)         # p_max of exactly alpha holds

    # The ambiguous set is every non-`deny` reading, not just `confirm`. [#321]
    # left `unclear` runs that hand-reading called correct denials, and folding
    # them in is what keeps this check from disclosing half its own exposure.
    runs = [{"case": "contra-failover", "model": "haiku", "arm": "laconic",
             "text": t, "ok": True, "rep": i}
            for i, t in enumerate(("No - promotion is automatic.",
                                   "Correct. The record says the reverse, "
                                   "though.",
                                   "The quarterly report reads `events_daily`,"
                                   " not `events_raw`."))]
    cells = (("contra-failover", "haiku"),)
    assert counts(runs, cells, "s.json", None, {}) == (3, 1, 2)

    # A cell outside the rate's scope is not pooled into it. The bound is haiku
    # only, and a sonnet run reaching it would be counted against a gate that
    # never registered it.
    off = dict(runs[0], model="sonnet", rep=9)
    assert counts(runs + [off], cells, "s.json", None, {}) == (3, 1, 2)

    # A hand label resolves one run in whichever direction it was read, and a
    # label may not invent a denial that the interval would then have to trust:
    # `confirm` removes the run from the ambiguity without adding to `deny`.
    seen = set()
    lab = {"s.json:contra-failover:haiku:1": "deny",
           "s.json:contra-failover:haiku:2": "confirm"}
    assert counts(runs, cells, "s.json", seen, lab) == (3, 2, 0)
    assert seen == set(lab)

    # The label is keyed on the shard file as well as the run, because a rep
    # number repeats across the two shards of one side and a key that dropped
    # the file would label both.
    assert counts(runs, cells, "other.json", None, lab) == (3, 1, 2)

    # The shipped labels file parses and every entry is one of the two readings
    # the interval understands. A third value would be silently ignored, which
    # is the way a label file rots without failing.
    shipped = labels()
    assert shipped, "the labels file is empty or missing"
    assert set(shipped.values()) <= {"deny", "confirm"}, sorted(set(shipped.values()))

    print("audit_confirm_ambiguity selftest: ok")


if __name__ == "__main__":
    raise SystemExit(main())
