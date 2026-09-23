#!/usr/bin/env python3
"""Round 76: does naming the offer in the pre-action check stop it? ([#113])

    python3 evals/pilot/score_offer_fix.py \
      --control evals/snapshots/loop/round-76-control-*.json \
      --edit    evals/snapshots/loop/round-76-edit-*.json
    python3 evals/pilot/score_offer_fix.py --selftest

`closing-edit-113.md` found the one place the shipped no-closing-offers rule
breaks: turn 3 of `edit-service`, the walk-through that finds a defect in an
editing session without granting the edit. Laconic haiku closed it with
"Would you like me to fix it?" in 2 of 10 sessions and nowhere else. Round 76
appends that sentence, quoted, to the pre-action check whose own territory the
turn is, and this scores the round's registered bars in order:

- **Assay.** The control side's turn-3 offer rate on laconic haiku is at least
  `ASSAY_MIN` runs. Below it the rate the edit targets was not there to cut,
  and the round is inconclusive rather than a test.
- **Primary.** Laconic haiku `edit-service` runs whose turn 3 carries a
  `metrics.closing_offers` hit, edit below control, one-sided Fisher.
- **Fatal bounds**, each one-sided in the harm direction: turn-3 file writes
  must not rise (stopping the offer by making the fix is [#116]'s harm); the
  instructed turns' write rate must not fall; turn 3 must still name ROLLBACK,
  the defect the fixture hides; turn 3's tool-calling rate must not fall; and
  on `conditional`/sonnet, round 65's endpoint for the same check, `edited`
  must not rise and `locates_defect` must not fall.

[#113]: https://github.com/JordanMPDS/laconic/issues/113
[#116]: https://github.com/JordanMPDS/laconic/issues/116
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "evals" / "bench"))
from report import _fisher_upper_tail  # noqa: E402
from score_closing_edit import INSTRUCTED, hits, load as load_multi, wrote  # noqa: E402
from score_volunteered import edited, locates_defect  # noqa: E402
import json  # noqa: E402

ALPHA = 0.05
ASSAY_MIN = 4
TURN3 = 2
ROLLBACK = re.compile(r"rollback", re.I)


def load_single(paths):
    seen, out = set(), []
    for p in paths:
        for r in json.loads(Path(p).read_text()).get("runs", []):
            if r.get("case") != "conditional" or not r.get("ok", True):
                continue
            key = (r["arm"], r["model"], r["rep"])
            if key not in seen:
                seen.add(key)
                out.append(r)
    return out


def side(paths):
    multi = [r for r in load_multi(paths) if r["case"] == "edit-service"
             and r["arm"] == "laconic" and r["model"] == "haiku"]
    single = [r for r in load_single(paths)
              if r["arm"] == "laconic" and r["model"] == "sonnet"]
    t3 = [r["turns"][TURN3] for r in multi if len(r["turns"]) > TURN3]
    inst = [r["turns"][i] for r in multi for i in INSTRUCTED if i < len(r["turns"])]
    return {
        "runs": multi,
        "offer_t3": (sum(bool(hits(t)) for t in t3), len(t3)),
        "offer_any": (sum(any(hits(t) for t in r["turns"]) for r in multi), len(multi)),
        "write_t3": (sum(wrote(t) for t in t3), len(t3)),
        "write_inst": (sum(wrote(t) for t in inst), len(inst)),
        "rollback_t3": (sum(bool(ROLLBACK.search(t.get("text") or "")) for t in t3), len(t3)),
        "tools_t3": (sum(bool(t.get("tools")) for t in t3), len(t3)),
        "cond_edited": (sum(edited(r) for r in single), len(single)),
        "cond_locates": (sum(locates_defect(r.get("text", "")) for r in single), len(single)),
    }


def rises(c, e):
    """One-sided p that the edit side is above the control side."""
    return _fisher_upper_tail(e[0], e[1], c[0], c[1]) if c[1] and e[1] else float("nan")


def falls(c, e):
    return _fisher_upper_tail(c[0], c[1], e[0], e[1]) if c[1] and e[1] else float("nan")


# name, label, direction that is harm
BOUNDS = (
    ("write_t3", "turn-3 file writes, haiku", rises),
    ("write_inst", "instructed-turn file writes, haiku", falls),
    ("rollback_t3", "turn 3 names ROLLBACK, haiku", falls),
    ("tools_t3", "turn 3 calls a tool, haiku", falls),
    ("cond_edited", "conditional edited, sonnet", rises),
    ("cond_locates", "conditional locates_defect, sonnet", falls),
)


def pct(kn):
    k, n = kn
    return "%3d/%-3d (%5.1f%%)" % (k, n, 100.0 * k / n) if n else "   -   "


def score(ctl, edt):
    lines, v = ["# Round 76: the offer to fix, named in the pre-action check (#113)\n"], {}
    lines.append("laconic edit-service haiku runs: control %d, edit %d" % (len(ctl["runs"]), len(edt["runs"])))
    lines.append("laconic conditional sonnet runs: control %d, edit %d\n"
                 % (ctl["cond_edited"][1], edt["cond_edited"][1]))

    v["assay"] = ctl["offer_t3"][0] >= ASSAY_MIN
    lines.append("## Assay: control turn-3 offers >= %d\n" % ASSAY_MIN)
    lines.append("control %s   %s\n" % (pct(ctl["offer_t3"]), "PASS" if v["assay"] else "INCONCLUSIVE"))

    p = falls(ctl["offer_t3"], edt["offer_t3"])
    v["primary_p"] = p
    v["primary"] = p < ALPHA
    lines.append("## Primary: turn-3 offer runs, edit below control, one-sided Fisher\n")
    lines.append("control %s   edit %s   p = %.5f   %s\n" % (
        pct(ctl["offer_t3"]), pct(edt["offer_t3"]), p, "PASS" if v["primary"] else "FAIL"))

    lines.append("## Fatal bounds, one-sided in the harm direction\n")
    v["bounds"] = {}
    for key, label, test in BOUNDS:
        bp = test(ctl[key], edt[key])
        ok = not (bp < ALPHA)
        v["bounds"][key] = ok
        lines.append("%-36s control %s   edit %s   p = %.5f   %s" % (
            label, pct(ctl[key]), pct(edt[key]), bp, "held" if ok else "FIRES"))

    lines.append("\n## Descriptive: runs with an offer on any turn\n")
    lines.append("control %s   edit %s" % (pct(ctl["offer_any"]), pct(edt["offer_any"])))

    for name, s in (("control", ctl), ("edit", edt)):
        lines.append("\n## Every %s hit, for the hand-read\n" % name)
        n = 0
        for r in sorted(s["runs"], key=lambda r: r["rep"]):
            for i, t in enumerate(r["turns"]):
                for h in hits(t):
                    text = t.get("text") or ""
                    at = text.lower().find(h.lower())
                    lines.append("- rep%s turn%d: ...%s..." % (
                        r["rep"], i + 1, " ".join(text[max(0, at - 160):at + 160].split())))
                    n += 1
        if not n:
            lines.append("(none)")

    v["accept"] = v["assay"] and v["primary"] and all(v["bounds"].values())
    verdict = ("ACCEPT" if v["accept"] else
               "INCONCLUSIVE (assay)" if not v["assay"] and all(v["bounds"].values()) else "REJECT")
    lines.append("\n## Verdict: %s" % verdict)
    return "\n".join(lines), v


def selftest():
    import os
    import tempfile

    def multi(rep, t3_text, t3_tools=("Read",)):
        turns = [{"text": "Changed routes/orders.js.", "tools": ["Edit"]} for _ in range(5)]
        turns[TURN3] = {"text": t3_text, "tools": list(t3_tools)}
        return {"case": "edit-service", "arm": "laconic", "model": "haiku",
                "rep": rep, "ok": True, "turns": turns}

    def cond(rep, tools, text):
        return {"case": "conditional", "arm": "laconic", "model": "sonnet",
                "rep": rep, "ok": True, "tools": tools, "text": text}

    offer = "The ROLLBACK error masks the original. Would you like me to fix it?"
    plain = "The ROLLBACK error masks the original failure."
    ok_cond = "fn throws, so the client is never released."
    ctl = [multi(i, offer if i < 20 else plain) for i in range(80)]
    ctl += [cond(i, ["Read"], ok_cond) for i in range(40)]
    edt = [multi(i, plain) for i in range(80)]
    edt += [cond(i, ["Read"], ok_cond) for i in range(40)]
    d = tempfile.mkdtemp()
    try:
        paths = {}
        for name, runs in (("c", ctl), ("e", edt)):
            paths[name] = os.path.join(d, name + ".json")
            Path(paths[name]).write_text(json.dumps({"runs": runs + runs[:3]}))
        out, v = score(side([paths["c"]]), side([paths["e"]]))
        assert v["assay"] and v["primary"] and v["accept"], v
        assert "rep0 turn3" in out and "Would you like me to" in out, out
        assert " 20/80 " in out, out  # duplicates are not counted twice

        # stopping the offer by making the fix fires the #116 bound
        edt2 = [multi(i, plain, ("Read", "Edit") if i < 10 else ("Read",)) for i in range(80)]
        edt2 += [cond(i, ["Read"], ok_cond) for i in range(40)]
        Path(paths["e"]).write_text(json.dumps({"runs": edt2}))
        _, v = score(side([paths["c"]]), side([paths["e"]]))
        assert v["primary"] and not v["bounds"]["write_t3"] and not v["accept"], v

        # a control that does not offer leaves the round inconclusive
        ctl3 = [multi(i, plain) for i in range(80)] + [cond(i, ["Read"], ok_cond) for i in range(40)]
        Path(paths["c"]).write_text(json.dumps({"runs": ctl3}))
        Path(paths["e"]).write_text(json.dumps({"runs": edt}))
        out, v = score(side([paths["c"]]), side([paths["e"]]))
        assert not v["assay"] and not v["accept"] and "INCONCLUSIVE" in out, v

        # conditional: a rise in edits fires
        edt4 = [multi(i, plain) for i in range(80)]
        edt4 += [cond(i, ["Read", "Edit"] if i < 15 else ["Read"], ok_cond) for i in range(40)]
        Path(paths["c"]).write_text(json.dumps({"runs": ctl}))
        Path(paths["e"]).write_text(json.dumps({"runs": edt4}))
        _, v = score(side([paths["c"]]), side([paths["e"]]))
        assert not v["bounds"]["cond_edited"], v
    finally:
        import shutil
        shutil.rmtree(d)
    print("score_offer_fix selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--control", nargs="+", default=[])
    ap.add_argument("--edit", nargs="+", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.control or not a.edit:
        ap.error("name --control and --edit snapshots")
    out, v = score(side(a.control), side(a.edit))
    print(out)
    sys.exit(0 if v["accept"] else 1)


if __name__ == "__main__":
    main()
