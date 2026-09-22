#!/usr/bin/env python3
"""Does laconic's 0-of-525 closing-offer rate survive a session that edits?

    python3 evals/pilot/score_closing_edit.py evals/snapshots/loop/closing-edit-113-*.json
    python3 evals/pilot/score_closing_edit.py --selftest

[#113] reports the no-closing-offers rule breaking on one turn of a long
*editing* session and holding on the next. `closing-drift-113.md` read the
five-turn `drift-service` family and found laconic at 0 of 525 turn-responses
where the unruled baseline fires 23.2%, but every turn of that family ends
"Don't edit anything.", so it excludes the report's regime by construction.
`edit-service` is the same five questions over the same fixture with the
clause replaced by "Go ahead and make the change." (dropped on turn 3, a
walk-through with no change to make). Both are generated in one pass, so the
only thing the pair manipulates is whether the session edits.

The bars are registered in `../results/loop/closing-edit-113.md`, and this
prints them in that order:

- **M, manipulation.** At least 80% of `edit-service` turns 1, 2, 4 and 5
  invoke a file-writing tool. Otherwise the regime was not induced and nothing
  below is about editing.
- **B1, instrument.** The baseline arm fires on at least 10% of `edit-service`
  turn-responses. Otherwise the regime does not elicit offers at all and a
  laconic zero is an instrument floor rather than a finding.
- **Primary.** Laconic `edit-service` runs with at least one detector hit,
  pooled over both models. Every hit is printed verbatim so it can be read by
  hand; the primary fires on one confirmed hit, because `drift-service` is
  already a measured zero and presence is the separation (DeepSeek's
  correction from `tools/consult.sh`).

The run-level Fisher contrast against `drift-service` and the turn-level
Clopper-Pearson bounds are descriptive, and the bound is split into the turns
that carry the edit instruction and turn 3, which carries none (Kimi and
DeepSeek both asked for the split).

[#113]: https://github.com/JordanMPDS/laconic/issues/113
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
from metrics import closing_offers  # noqa: E402
from report import _fisher_upper_tail  # noqa: E402

CASES = ("edit-service", "drift-service")
ARMS = ("laconic", "baseline")
MODELS = ("haiku", "sonnet")
WRITERS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
INSTRUCTED = (0, 1, 3, 4)  # turn indices carrying "Go ahead and make the change."
MANIPULATION_BAR = 0.80
INSTRUMENT_BAR = 0.10


def load(paths):
    runs = []
    for p in paths:
        runs += json.loads(Path(p).read_text()).get("runs", [])
    return distinct(runs)


def distinct(runs):
    """Completed multi-turn runs of the pair, keyed so a resumed or merged file
    cannot count one run twice."""
    seen, out = set(), []
    for r in runs:
        if r.get("case") not in CASES or not isinstance(r.get("turns"), list):
            continue
        key = (r["case"], r["arm"], r["model"], r["rep"])
        if key in seen or not r.get("ok", True):
            continue
        seen.add(key)
        out.append(r)
    return out


def hits(turn):
    return closing_offers(turn.get("text") or "")


def wrote(turn):
    return bool(WRITERS & set(turn.get("tools") or []))


def cp_upper(k, n):
    """Clopper-Pearson 95% upper bound, by bisection on the binomial tail."""
    if n == 0:
        return 1.0
    if k >= n:
        return 1.0
    from math import comb
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        tail = sum(comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(k + 1))
        lo, hi = (mid, hi) if tail > 0.025 else (lo, mid)
    return hi


def pick(runs, case=None, arm=None, model=None):
    return [r for r in runs if (case is None or r["case"] == case)
            and (arm is None or r["arm"] == arm)
            and (model is None or r["model"] == model)]


def turn_rate(runs, idx=None):
    k = n = 0
    for r in runs:
        for i, t in enumerate(r["turns"]):
            if idx is None or i in idx:
                n += 1
                k += bool(hits(t))
    return k, n


def run_rate(runs):
    return sum(any(hits(t) for t in r["turns"]) for r in runs), len(runs)


def pct(k, n):
    return "%3d/%-3d %5.1f%%" % (k, n, 100.0 * k / n) if n else "    -    "


def score(runs):
    lines, verdict = [], {}
    lines.append("# closing offers under an editing session (#113)\n")
    lines.append("%d distinct runs\n" % len(runs))

    lines.append("## Per-turn rates\n")
    lines.append("case           arm       model   " + "  ".join("turn%d        " % (i + 1) for i in range(5)))
    for case in CASES:
        for arm in ARMS:
            for model in MODELS:
                rs = pick(runs, case, arm, model)
                if not rs:
                    continue
                cells = [pct(*turn_rate(rs, {i})) for i in range(5)]
                lines.append("%-14s %-9s %-7s %s" % (case, arm, model, "  ".join(cells)))

    k = n = 0
    for r in pick(runs, "edit-service"):
        for i in INSTRUCTED:
            if i < len(r["turns"]):
                n += 1
                k += wrote(r["turns"][i])
    dk = dn = 0
    for r in pick(runs, "drift-service"):
        for t in r["turns"]:
            dn += 1
            dk += wrote(t)
    m_ok = bool(n) and k / n >= MANIPULATION_BAR
    verdict["M"] = m_ok
    lines.append("\n## M, manipulation: edit-service instructed turns that write a file\n")
    lines.append("edit-service   %s   (bar >= %.0f%%)   %s" % (pct(k, n), 100 * MANIPULATION_BAR, "PASS" if m_ok else "FAIL"))
    lines.append("drift-service  %s   (reference: every turn forbids editing)" % pct(dk, dn))

    bk, bn = turn_rate(pick(runs, "edit-service", "baseline"))
    b_ok = bool(bn) and bk / bn >= INSTRUMENT_BAR
    verdict["B1"] = b_ok
    lines.append("\n## B1, instrument: baseline fires on edit-service\n")
    lines.append("baseline edit-service  %s   (bar >= %.0f%%)   %s" % (pct(bk, bn), 100 * INSTRUMENT_BAR, "PASS" if b_ok else "FAIL"))

    lac = pick(runs, "edit-service", "laconic")
    rk, rn = run_rate(lac)
    verdict["primary_hits"] = rk
    lines.append("\n## Primary: laconic edit-service runs with at least one offer\n")
    lines.append("laconic edit-service runs  %s" % pct(rk, rn))
    lines.append("Every hit, for the hand-read the primary requires:\n")
    for r in sorted(lac, key=lambda r: (r["model"], r["rep"])):
        for i, t in enumerate(r["turns"]):
            for h in hits(t):
                text = t.get("text") or ""
                at = text.lower().find(h.lower())
                lines.append("- %s rep%s turn%d: ...%s..." % (
                    r["model"], r["rep"], i + 1,
                    " ".join(text[max(0, at - 160):at + 160].split())))
    if not rk:
        lines.append("(none)")

    lines.append("\n## Descriptive: run-level contrast, edit-service over drift-service\n")
    for arm in ARMS:
        ek, en = run_rate(pick(runs, "edit-service", arm))
        ck, cn = run_rate(pick(runs, "drift-service", arm))
        p = _fisher_upper_tail(ek, en, ck, cn) if en and cn else float("nan")
        lines.append("%-9s edit %s   drift %s   one-sided Fisher p = %.4g" % (arm, pct(ek, en), pct(ck, cn), p))

    lines.append("\n## Descriptive: laconic turn-level bounds on edit-service\n")
    for label, idx in (("instructed turns 1,2,4,5", set(INSTRUCTED)), ("turn 3, no instruction", {2})):
        tk, tn = turn_rate(lac, idx)
        lines.append("%-26s %s   95%% upper %.2f%%" % (label, pct(tk, tn), 100 * cp_upper(tk, tn)))
    return "\n".join(lines), verdict


def selftest():
    def run(case, arm, model, rep, texts, tools):
        return {"case": case, "arm": arm, "model": model, "rep": rep, "ok": True,
                "turns": [{"text": x, "tools": t} for x, t in zip(texts, tools)]}
    ed = [["Edit"]] * 2 + [["Read"]] + [["Edit"]] * 2
    ro = [["Read"]] * 5
    runs = [
        run("edit-service", "laconic", "haiku", 0, ["Done."] * 4 + ["Done. Want me to add tests?"], ed),
        run("edit-service", "laconic", "sonnet", 0, ["Done."] * 5, ed),
        run("edit-service", "baseline", "haiku", 0, ["Let me know if you need more."] * 5, ed),
        run("drift-service", "laconic", "haiku", 0, ["Use a scope."] * 5, ro),
        run("drift-service", "baseline", "haiku", 0, ["Use a scope."] * 5, ro),
    ]
    runs.append(dict(runs[0]))  # a duplicate key must not count twice
    out, v = score(distinct(runs))
    assert v["M"] is True, v
    assert v["B1"] is True, v
    assert v["primary_hits"] == 1, v
    assert "haiku rep0 turn5" in out and "Want me to" in out, out
    assert "1/2" in out.split("## Primary")[1].splitlines()[2], out
    # an unedited edit-service session fails the manipulation check
    _, v = score(distinct([run("edit-service", "laconic", "haiku", 0, ["x"] * 5, ro)]))
    assert v["M"] is False and v["B1"] is False and v["primary_hits"] == 0
    assert abs(cp_upper(0, 100) - 0.0362) < 0.001, cp_upper(0, 100)
    print("score_closing_edit selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("snapshots", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.snapshots:
        ap.error("name at least one snapshot")
    out, _ = score(load(a.snapshots))
    print(out)


if __name__ == "__main__":
    main()
