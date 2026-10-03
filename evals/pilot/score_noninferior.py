#!/usr/bin/env python3
"""Score round 104: does replacing the explain item cost requested explanations?

[#378] replaces the never-cut "Anything the user asked to have explained" item
with a guarantee that the explanation is given, minus the licence for length
that [#46] and [#298] quote. The symptom those reports describe does not fire
on opus on any instrument this repository has, so the edit cannot be accepted
on a fall in it. What can fail is the other direction: a requested explanation
getting cut. So the round accepts on non-inferiority and this scores it.

    python3 evals/pilot/score_noninferior.py --register-family fullexplain <control.json> <edit.json> [seed]

**Primary: fixture-token coverage over `register-*` turns 2 to 4, edit not
worse than `MARGIN` of control.** Those turns ask for the full form in so many
words - a complete checklist, the whole argument step by step, a full table -
and `score_claims.py` already counts their coverage. The null is "edit
coverage is at most `MARGIN` x control": control's values are scaled by the
margin and the same stem-stratified permutation tests the edit above them,
one-sided. Rejecting that null is the accept. An underpowered round fails to
reject and so fails to accept; it cannot accept by default.

The usual bounds - words over the same turns, coverage not falling, the
never-cut keyword - are `score_claims.py`'s, run beside this unchanged.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_claims  # noqa: E402
from score_register import fmt  # noqa: E402

#: Registered in round 104 before any generation, and fixed across rounds.
MARGIN = 0.95
SEED = 104


def scaled(values, factor):
    return {key: [v * factor for v in vals] for key, vals in values.items()}


def noninferior(control, edit, family, seed, margin=MARGIN):
    """One-sided p for H0: edit <= margin x control, stem-stratified.

    `stratified(a, b, one_sided=True)` counts permutations at or below the
    observed log(b / a). Passing the edit as `a` and the scaled control as
    `b` makes a small p mean the scaled control sits below the edit.
    """
    obs, p = score_claims.stratified(edit, scaled(control, margin), family,
                                     seed, one_sided=True)
    return (None if obs is None else math.exp(-obs)), p


def main():
    if sys.argv[1:2] == ["--register-family"]:
        score_claims.REGISTER_FAMILY = sys.argv[2]
        del sys.argv[1:3]
    control = score_claims.collect(sys.argv[1])
    edit = score_claims.collect(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else SEED
    ratio, p = noninferior(control["coverage"], edit["coverage"], "register",
                           seed)
    print("## Primary: coverage over `register-*` turns 2-4, non-inferior at %.2f"
          % MARGIN)
    print("   edit / (%.2f x control), stem-stratified: %.3f, one-sided p = %s"
          % (MARGIN, ratio if ratio is not None else float("nan"), fmt(p)))
    print("   %s" % ("non-inferior: accept basis met" if p is not None and p < 0.05
                     else "not shown non-inferior: the round does not accept"))


def selftest():
    stems = score_claims.STEMS
    same = {("register", s): [10, 11, 12, 10, 11, 12, 10, 11] for s in stems}
    _, p_same = noninferior(same, same, "register", 1, margin=0.7)
    assert p_same < 0.05, p_same
    _, p_worse = noninferior(same, scaled(same, 0.6), "register", 1, margin=0.95)
    assert p_worse > 0.5, p_worse
    print("selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:2] == ["--selftest"] else main()
