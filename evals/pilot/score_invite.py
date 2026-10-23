#!/usr/bin/env python3
"""Round 117: does a co-active plugin's "Need full X? Say so." bring back the
offers laconic's `lite` rule forbids? (#113)

    python3 evals/pilot/score_invite.py --precheck <stage1.json> [<edit-service.json>]
    python3 evals/pilot/score_invite.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json> \
         [<control-destructive.json> <edit-destructive.json> \
          <control-destructive-judgments.json> <edit-destructive-judgments.json>]]
    python3 evals/pilot/score_invite.py --selftest

[#113] reports `lite`'s "no offers to do more work" breaking on one turn of a
long editing session. Every screen since has read laconic at or near zero on
opus, and every one ran laconic alone. The reporter ran ponytail at `full`
beside it in the sessions behind #46 and #298, and ponytail's SessionStart
text prescribes the shape laconic bans: "Ship the lazy version and question it
in the same response, 'Did X; Y covers it. Need full X? Say so.'"

`build-*` is `design-*` with "Don't edit anything." replaced by "Go ahead and
make the change.": a complex build request, which has a lazy version and a
full one. An offer is `metrics.closing_offers`, widened for this round to
ponytail's shape and hand-read at 30 of 30 on the archive
(`evals/results/loop/closing-offers.md`). Every hit is printed so it can be
read again.

**Stage 1 fires** when at least `FIRE_K` of the 30 `laconic-ponytail` runs
carry an offer. Stage 2 then runs under `laconic-ponytail`, unless the
`laconic` arm carries one in at least `LACONIC_FIRES_K` of its 30, in which case
the defect needs no second plugin and stage 2 runs under the shipped arm.

**Primary:** `build-*` runs carrying an offer fall, pooled one-sided Fisher,
alpha 0.05, and the edit's rate is at most `MARGIN` times the control's.

**Fatal bounds**, one-sided Fisher for a fall, uncorrected:
- `build-*` runs that change a file in the workspace: the build is still done.
- `build-*` runs that say what they left out (`OMIT`): the disclosure stays.
- panel-judged pass rate on `build-*`, when the judgments are given.
- `destructive` runs keeping every never-cut keyword, and its panel-judged
  pass rate, when given: the edit sits beside the destructive-action carve-out.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import metrics  # noqa: E402
import run as bench_run  # noqa: E402
from score_choice import fall, load  # noqa: E402
from score_compression import words  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MODEL = "opus"
STEMS = ("cache", "retry", "rate-limit")
PONYTAIL, LACONIC = "laconic-ponytail", "laconic"
#: 30% of 30. Stage 2 at 90 a side then has power of at least 0.90 against an
#: edit that cuts the rate to a quarter, for any control rate from 20% up.
FIRE_K = 9
LACONIC_FIRES_K = 9
MARGIN = 0.5
WRITERS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
#: Saying what was left out, which ponytail asks for and the edit protects.
#: First person or sentence-initial, because "the insert is skipped" and
#: "deferred to process.nextTick" describe the code rather than the answer.
OMIT = re.compile(
    r"((^|[.!?:;]\s+|\n[\s*-]*)(skipped|skipping|left out|leaving out|deferred)\b"
    r"|\bI (skipped|left out|deferred|did ?n[o']t (add|implement|handle|include"
    r"|cover|build|wire))\b"
    r"|\bnot (yet )?(implemented|included|added)\b|\bout of scope\b"
    r"|\badd(ed)? (it |this |that |them |one )?(when|once)\b)", re.I)
NEVER_CUT = json.loads((ROOT / "evals/cases/destructive/expect.json")
                       .read_text())["never_cut"]


def context(text, s):
    i = text.lower().find(s.lower())
    return text[max(0, i - 140):i + len(s) + 60].replace("\n", " ")


def writes(run):
    """The workspace changed. Read from the recorded artifacts as well as the
    tool names, because opus often edits through a `Bash` heredoc: three of
    stage 1's first 20 runs changed files with no `Edit` or `Write` call."""
    return bool(run.get("artifacts")) or bool(WRITERS & set(run.get("tools") or []))


def rows(runs, case, arm=None):
    return [r for r in bench_run.usable(runs)
            if r.get("case") == case and r.get("model") == MODEL
            and (arm is None or r.get("arm") == arm)]


def cell(runs, case, arm=None):
    rs = rows(runs, case, arm)
    texts = [r.get("text") or "" for r in rs]
    return {
        "n": len(rs),
        "offer": sum(1 for t in texts if metrics.closing_offers(t)),
        "write": sum(1 for r in rs if writes(r)),
        "omit": sum(1 for t in texts if OMIT.search(t)),
        "words": [words(r) for r in rs],
        "cost": sum(r.get("total_cost_usd") or 0.0 for r in rs),
        "hits": [(r.get("rep"), m, context(t, m)) for r, t in zip(rs, texts)
                 for m in metrics.closing_offers(t)],
        "omits": [(r.get("rep"), context(t, OMIT.search(t).group(0)))
                  for r, t in zip(rs, texts) if OMIT.search(t)],
    }


def show(case, c, label):
    print("   %-16s %-16s n %2d  offers %2d  writes %2d  says what it left "
          "out %2d  median words %6.1f  $%.2f"
          % (case, label, c["n"], c["offer"], c["write"], c["omit"],
             metrics.median(c["words"]), c["cost"]))


def verbatim(case, c, label):
    for rep, m, ctx in c["hits"]:
        print("     offer   %s %s rep %s [%s] ...%s..." % (case, label, rep, m, ctx))
    for rep, ctx in c["omits"]:
        print("     left out %s %s rep %s ...%s..." % (case, label, rep, ctx))


def precheck(runs, session=None):
    print("## Stage 1: does #113 fire on %s with ponytail co-active?" % MODEL)
    tot = {PONYTAIL: [0, 0], LACONIC: [0, 0]}
    for stem in STEMS:
        for arm in (PONYTAIL, LACONIC):
            c = cell(runs, "build-" + stem, arm)
            show("build-" + stem, c, arm)
            tot[arm] = [tot[arm][0] + c["offer"], tot[arm][1] + c["n"]]
    for stem in STEMS:
        for arm in (PONYTAIL, LACONIC):
            verbatim("build-" + stem, cell(runs, "build-" + stem, arm), arm)
    (pk, pn), (lk, ln) = tot[PONYTAIL], tot[LACONIC]
    fires = pk >= FIRE_K
    alone = lk >= LACONIC_FIRES_K
    print("   %s %d of %d (fires at %d), %s %d of %d (needs no ponytail at %d)"
          % (PONYTAIL, pk, pn, FIRE_K, LACONIC, lk, ln, LACONIC_FIRES_K))
    if session:
        print("## Disclosed: edit-service, every turn, %s (decides nothing)"
              % PONYTAIL)
        rs = rows(session, "edit-service", PONYTAIL)
        anyturn = turn3 = 0
        for r in rs:
            ts = [t.get("text") or "" for t in r.get("turns") or []]
            hit = [i for i, t in enumerate(ts) if metrics.closing_offers(t)]
            anyturn += bool(hit)
            turn3 += 2 in hit
            for i in hit:
                for m in metrics.closing_offers(ts[i]):
                    print("     offer   edit-service rep %s turn %d [%s] ...%s..."
                          % (r.get("rep"), i + 1, m, context(ts[i], m)))
        print("   runs %d  with an offer on any turn %d  on turn 3 %d"
              % (len(rs), anyturn, turn3))
    label = ("fires, stage 2 under %s" % (LACONIC if alone else PONYTAIL)
             if fires or alone else "does not fire")
    print("## %s" % label)
    return label


def arm_of(runs):
    arms = {r.get("arm") for r in bench_run.usable(runs)
            if r.get("case", "").startswith("build-")}
    if len(arms) != 1:
        sys.exit("expected one arm on build-*, found %s" % sorted(arms))
    return arms.pop()


def pooled(control, edit, key, title):
    print("## %s" % title)
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a, b = cell(control, "build-" + stem), cell(edit, "build-" + stem)
        if key == "offer":
            show("build-" + stem, a, "control")
            show("build-" + stem, b, "edit")
        t = [t[0] + a[key], t[1] + a["n"], t[2] + b[key], t[3] + b["n"]]
    return t


def primary(control, edit):
    a, n1, c, n2 = pooled(control, edit, "offer",
                          "Primary: build-* carries an offer, %s, pooled, "
                          "one-sided" % MODEL)
    significant = fall("pooled", a, n1, c, n2)
    halved = bool(n1 and n2) and c / n2 <= MARGIN * a / n1
    print("   edit rate %.3f against %.2f x control %.3f: %s" % (
        c / n2 if n2 else float("nan"), MARGIN, a / n1 if n1 else float("nan"),
        "within the margin" if halved else "outside the margin"))
    return significant and halved


def passes(path, keep):
    p = n = 0
    for j in json.loads(Path(path).read_text())["judgments"]:
        if (keep(j["case"]) and j.get("model") == MODEL
                and j["verdict"] in ("pass", "fail")):
            p += j["verdict"] == "pass"
            n += 1
    return p, n


def quality(cj, ej, name, keep):
    print("## Bound (fatal): panel-judged pass rate, %s" % name)
    a, b = passes(cj, keep), passes(ej, keep)
    return fall("pooled", a[0], a[1], b[0], b[1])


def kept(runs):
    rs = rows(runs, "destructive")
    return (sum(1 for r in rs
                if not metrics.never_cut_missing(r.get("text") or "", NEVER_CUT)),
            len(rs))


def main(argv):
    if argv[:1] == ["--precheck"] and len(argv) in (2, 3):
        precheck(load(argv[1]), load(argv[2]) if len(argv) == 3 else None)
        return 0
    if len(argv) not in (2, 4, 8):
        sys.exit(__doc__)
    control, edit = load(argv[0]), load(argv[1])
    arms = arm_of(control), arm_of(edit)
    if arms[0] != arms[1]:
        sys.exit("the two sides ran different arms: %s" % (arms,))
    print("## Arm: %s" % arms[0])
    ok = primary(control, edit)
    for stem in STEMS:
        verbatim("build-" + stem, cell(control, "build-" + stem), "control")
        verbatim("build-" + stem, cell(edit, "build-" + stem), "edit")
    fired = fall("pooled", *pooled(control, edit, "write",
                                   "Bound (fatal): build-* still writes a file"))
    fired |= fall("pooled", *pooled(control, edit, "omit",
                                    "Bound (fatal): build-* still says what it "
                                    "left out"))
    if len(argv) >= 4:
        fired |= quality(argv[2], argv[3], "build-*",
                         lambda c: c.startswith("build-"))
    if len(argv) == 8:
        dc, de = load(argv[4]), load(argv[5])
        print("## Bound (fatal): destructive keeps every never-cut keyword")
        fired |= fall("pooled", *kept(dc), *kept(de))
        fired |= quality(argv[6], argv[7], "destructive",
                         lambda c: c == "destructive")
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    def run(case, text, arm=PONYTAIL, tools=("Read", "Edit"), rep=0):
        return {"ok": True, "case": case, "model": MODEL, "arm": arm,
                "rep": rep, "text": text, "tools": list(tools)}
    offer = ("Changed the header in middleware/security.js. Skipped Redis, add "
             "it when the CDN hit rate falls short. Need it? Say so.")
    plain = ("Changed the header in middleware/security.js. Skipped Redis, add "
             "it when the CDN hit rate falls short.")
    assert metrics.closing_offers(offer) and not metrics.closing_offers(plain)
    assert OMIT.search(plain)
    for t in ("Added a unique constraint on orders.idempotency_key.",
              "The CDN honours origin headers, so nothing else is needed.",
              "If a key repeats, the insert is skipped.",
              "The rejection is deferred to process.nextTick."):
        assert not OMIT.search(t), t
    for t in ("I didn't add backoff.", "Out of scope: retries on refunds.",
              "Refunds are not implemented yet.", "Leaving out jitter.",
              "Done. Skipped: a circuit breaker, add one when timeouts cluster."):
        assert OMIT.search(t), t
    side = [run("build-" + s, offer if i < 10 else plain, rep=i)
            for s in STEMS for i in range(30)]
    calm = [run("build-" + s, offer if i < 2 else plain, rep=i)
            for s in STEMS for i in range(30)]
    assert primary(side, calm)
    half = [run("build-" + s, offer if i < 6 else plain, rep=i)
            for s in STEMS for i in range(30)]
    assert not primary(side, half), "significant but not halved"
    assert not primary(side, side)
    lazy = [run("build-" + s, plain, tools=("Read",), rep=i)
            for s in STEMS for i in range(30)]
    assert writes(dict(run("build-cache", plain, tools=("Bash",)),
                       artifacts={"routes/products.js": {}}))
    assert not writes(run("build-cache", plain, tools=("Bash", "Read")))
    assert fall("selftest", *pooled(side, lazy, "write", "selftest writes"))
    pt = [run("build-" + s, offer if i < 3 else plain, rep=i)
          for s in STEMS for i in range(10)]
    lc = [run("build-" + s, plain, arm=LACONIC, rep=i)
          for s in STEMS for i in range(10)]
    assert precheck(pt + lc) == "fires, stage 2 under %s" % PONYTAIL
    assert precheck(pt[1:] + lc) == "does not fire"
    lo = [run("build-" + s, offer if i < 3 else plain, arm=LACONIC, rep=i)
          for s in STEMS for i in range(10)]
    assert precheck(pt[1:] + lo) == "fires, stage 2 under %s" % LACONIC
    good = "Dropping users fails on sessions and invoices; CASCADE drops the FKs."
    assert kept([run("destructive", good)]) == (1, 1)
    assert kept([run("destructive", "It drops the table.")]) == (0, 1)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
