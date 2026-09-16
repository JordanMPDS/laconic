#!/usr/bin/env python3
"""Score round 70: does a requested report get the same claims in fewer words?

[#150] reports the length-scaling paragraph read as a *length exemption* - once
a report is requested, the smallest-set-of-claims check stops binding - and
audits the result at 230 restated words in 1,335, 17.2%. Round 29 scored that
edit on `output_tokens`, whose floor on the scoped cells is 17.7%, so it could
not have passed however worded. Round 49 scored the identical text on the
`register-*` graded turn, where the carry-forward's 0.44 elasticity made the
10.1% it bought on the licensed stretch worth about three words. Neither round
scored the edit on the quantity the issue is about.

    python3 evals/pilot/score_claims.py <control.json> <edit.json> [seed]

This does. Both snapshots are the laconic arm; the group label is the rules
revision, so the two sides come from two trees generated simultaneously, which
is round 38's design and round 49's shape.

**Target: prose words over turns 2 to 4 of `register-*`, down.** Those three
turns ask in as many words for the complete form - a complete checklist, the
whole argument step by step, a table with the evidence for each row - so they
are the one place in this repository where `rules/laconic.md` licenses length
explicitly and the harm [#150] describes can occur.

**Bound, fatal: fixture-token coverage over the same three turns must not
fall.** Fewer words is bought trivially by saying less, and that failure would
score as a triumph. The bound closes it with a coverage count whose pass
condition is a token present in the response, which is `CRITERIA.md`'s
admission rule for never-cut keywords applied to the whole fixture.

**The token list is mechanical, not hand-picked** - `FIXTURE_TOKEN` over the
fixture text, minus anything the prompt already contains, minus single-character
matches. A hand-picked list is a list picked after reading
responses; this one is a function of the fixture, and `cases_cksum` covers the
fixture, so it cannot drift from the round that registered it. Run with
`--tokens` to print it.

**Every test is stratified by stem, and that is what makes the round
affordable.** The three stems sit at 879.5, 689.0 and 324.5 median words on
round 49's control, so pooling them puts most of the variance in which stem a
draw came from: the pooled permutation carries 0.30 power against [#150]'s
17.2% harm at 30 runs a side, and the within-stem one carries 0.90 at ten runs
per stem. That is round 42's mixture lesson, which round 69 then measured
costing this cluster a factor of 1.9 on every arm-label interaction it has run.
"""
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_register import STEMS, fmt, turn_words  # noqa: E402

SEED = 70
SIDES = ("control", "edit")
FAMILIES = ("register", "deep")
#: The licensed stretch: the three turns that ask for the full form.
MIDDLE = (1, 2, 3)
#: Round 49's bound, carried forward verbatim. The licence has to still fire.
LICENCE_FLOOR = 5.0

#: A number, a clock time, or a backticked identifier. Numbers and identifiers
#: are what a fixture states and prose can drop; ordinary words are not, since
#: an answer restating a claim reuses them too.
FIXTURE_TOKEN = re.compile(
    r"(\b\d{1,2}:\d{2}\b|\b\d[\d,]*(?:\.\d+)?%?\b)|`([^`\n]{2,60})`")


def fixture_tokens(stem):
    """Tokens the fixture states and the prompt does not, longest first.

    Longest first because matching is by substring: `41,199,388` must be
    counted before `41`, or a response that names neither scores for both.
    """
    case = Path(__file__).resolve().parent / f"register-{stem}"
    fixture = case / "fixture"
    text = "\n".join(p.read_text() for p in sorted(fixture.iterdir()) if p.is_file())
    prompt = (case / "prompt.md").read_text()
    found = set()
    for number, ident in FIXTURE_TOKEN.findall(text):
        token = (ident or number).strip()
        if len(token) >= 2 and token not in prompt:
            found.add(token)
    return sorted(found, key=lambda t: (-len(t), t))


def covered(text, tokens):
    """How many of the fixture's tokens the response names.

    Each match consumes its span, so `41.2` inside `41.2 million` is not also
    credited to a shorter token that happens to sit inside a longer one.
    """
    remaining = text
    hits = 0
    for token in tokens:
        if token in remaining:
            hits += 1
            remaining = remaining.replace(token, "\x00" * len(token))
    return hits


def collect(path):
    """Per-run words and coverage out of one snapshot, keyed by family and stem."""
    snap = json.loads(Path(path).read_text())
    words = defaultdict(list)
    coverage = defaultdict(list)
    kept = defaultdict(list)
    n = 0
    tokens = {stem: fixture_tokens(stem) for stem in STEMS}
    for r in bench_run.usable(snap["runs"]):
        if r["arm"] != "laconic" or "-" not in r["case"]:
            continue
        family, stem = r["case"].split("-", 1)
        if family not in FAMILIES or stem not in STEMS:
            continue
        counts = [turn_words(r, i) for i in MIDDLE]
        turns = r.get("turns") or []
        if any(c is None for c in counts) or len(turns) <= max(MIDDLE):
            continue
        n += 1
        words[(family, stem)].append(sum(counts))
        stretch = "\n".join(turns[i].get("text", "") for i in MIDDLE)
        coverage[(family, stem)].append(covered(stretch, tokens[stem]))
        expect = json.loads(
            (Path(__file__).resolve().parent / r["case"] / "expect.json").read_text())
        kw = expect.get("never_cut") or []
        if kw:
            kept[(family, stem)].append(
                not metrics.never_cut_missing(r.get("text", ""), kw))
    return dict(n=n, meta=snap["metadata"], words=words, coverage=coverage,
                kept=kept, tokens=tokens)


def stem_effect(control, edit, family, log):
    """Mean over stems of the edit-minus-control shift in the stem's median.

    On logged values that mean is a log ratio, so exponentiating it gives the
    factor the edit multiplied a typical response by, with each stem weighted
    equally rather than by its own level.
    """
    shifts = []
    for stem in STEMS:
        c, e = control[(family, stem)], edit[(family, stem)]
        if not c or not e:
            return None
        f = math.log if log else (lambda v: v)
        shifts.append(metrics.median([f(v) for v in e])
                      - metrics.median([f(v) for v in c]))
    return sum(shifts) / len(shifts)


def stratified(control, edit, family, seed, log=True, resamples=50000,
               one_sided=False):
    """Permute the side label inside each stem, preserving the stem's sizes.

    Within-stem because the stems sit a factor of 2.7 apart on this quantity,
    so a permutation that mixed them would build its null out of which stem a
    draw came from rather than out of which side it came from.
    """
    obs = stem_effect(control, edit, family, log)
    if obs is None:
        return None, None
    rng = random.Random(seed)
    pools = {stem: list(control[(family, stem)]) + list(edit[(family, stem)])
             for stem in STEMS}
    sizes = {stem: len(control[(family, stem)]) for stem in STEMS}
    hits = 0
    for _ in range(resamples):
        c, e = {}, {}
        for stem in STEMS:
            pool = pools[stem]
            rng.shuffle(pool)
            c[(family, stem)] = pool[:sizes[stem]]
            e[(family, stem)] = pool[sizes[stem]:]
        shuffled = stem_effect(c, e, family, log)
        if (shuffled <= obs + 1e-12) if one_sided else (abs(shuffled) >= abs(obs) - 1e-12):
            hits += 1
    return obs, (hits + 1) / (resamples + 1)


def main():
    if "--tokens" in sys.argv:
        for stem in STEMS:
            tokens = fixture_tokens(stem)
            print("%-9s %2d  %s" % (stem, len(tokens), "  ".join(tokens)))
        return
    control, edit = collect(sys.argv[1]), collect(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else SEED
    sides = {"control": control, "edit": edit}

    for name, s in sides.items():
        print("%-8s runs %3d   turn_delivery: %s   rules_cksum: %s   "
              "cases_cksum: %s"
              % (name, s["n"], s["meta"].get("turn_delivery"),
                 s["meta"].get("rules_cksum"), s["meta"].get("cases_cksum")))
    if control["meta"].get("rules_cksum") == edit["meta"].get("rules_cksum"):
        print("\n!! the two snapshots agree on rules_cksum - this is not a contrast")

    print("\n## Target: prose words over turns 2-4, `register-*`, laconic, down")
    print("%-9s %5s %9s %9s %8s" % ("stem", "n", "control", "edit", "ratio"))
    for stem in STEMS:
        c, e = control["words"][("register", stem)], edit["words"][("register", stem)]
        mc, me = metrics.median(c), metrics.median(e)
        print("%-9s %5d %9.1f %9.1f %8.3f"
              % (stem, len(c), mc, me, (me / mc) if mc else float("nan")))
    obs, p = stratified(control["words"], edit["words"], "register", seed)
    print("   stem-stratified, mean of stem median log words: ratio %.3f, p = %s"
          % (math.exp(obs) if obs is not None else float("nan"), fmt(p)))

    print("\n## Bound (fatal): fixture-token coverage over turns 2-4, must not fall")
    print("%-9s %6s %9s %9s %8s"
          % ("stem", "of", "control", "edit", "ratio"))
    for stem in STEMS:
        c = control["coverage"][("register", stem)]
        e = edit["coverage"][("register", stem)]
        mc, me = metrics.median(c), metrics.median(e)
        print("%-9s %6d %9.1f %9.1f %8.3f"
              % (stem, len(control["tokens"][stem]), mc, me,
                 (me / mc) if mc else float("nan")))
    obs, p = stratified(control["coverage"], edit["coverage"], "register", seed,
                        one_sided=True)
    print("   stem-stratified, one-sided down: ratio %.3f, p = %s"
          % (math.exp(obs) if obs is not None else float("nan"), fmt(p)))

    print("\n## Bound (fatal): the licence still fires, register / deep over turns 2-4")
    for name, s in sides.items():
        ratios = []
        for stem in STEMS:
            d = metrics.median(s["words"][("deep", stem)] or [0])
            r = metrics.median(s["words"][("register", stem)] or [0])
            ratios.append((stem, (r / d) if d else float("nan")))
        print("   %-8s %s   pooled %.2f"
              % (name, "  ".join("%s %.2f" % t for t in ratios),
                 metrics.median([v for _, v in ratios])))
    print("   floor %.1f" % LICENCE_FLOOR)

    print("\n## Bound (fatal): never-cut keyword on the graded turn")
    for name, s in sides.items():
        for (family, stem), vals in sorted(s["kept"].items()):
            print("   %-8s %-9s %-9s %d/%d"
                  % (name, family, stem, sum(vals), len(vals)))

    print("\n## Disclosure: the `deep-*` control family, same two quantities")
    for stem in STEMS:
        c, e = control["words"][("deep", stem)], edit["words"][("deep", stem)]
        print("   words    %-9s %7.1f %7.1f" % (stem, metrics.median(c or [0]),
                                                metrics.median(e or [0])))
    obs, p = stratified(control["words"], edit["words"], "deep", seed)
    print("   stem-stratified: ratio %.3f, p = %s"
          % (math.exp(obs) if obs is not None else float("nan"), fmt(p)))


if __name__ == "__main__":
    main()
