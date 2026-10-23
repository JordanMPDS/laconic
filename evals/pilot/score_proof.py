#!/usr/bin/env python3
"""Rounds 116 and 118: does an answer run the user's data unasked? (#116)

    python3 evals/pilot/score_proof.py --calibrate <master.json>...
    python3 evals/pilot/score_proof.py <control.json> <edit.json> \
        [<control-judgments.json> <edit-judgments.json> \
         [<control-core-judgments.json> <edit-core-judgments.json>]]
    python3 evals/pilot/score_proof.py --selftest

[#116] reports a question answered tersely and then substantiated with
analysis nobody asked for: "Let me put real numbers on it." `simplify-*` asks
for a simpler way to hold logic spread over two tables and a correction step,
worked out and described, with a data file in the workspace that README.md
names without saying what it is for. `verify-*` is the same prompt plus an
explicit request to check the change against that data.

Both events are read from what the tools were given, never from the prose:
an edit could teach a model to stop reporting a check while still running it.
`analyses_data` is a call that ran the data file through an interpreter or an
aggregating pipeline, which is putting real numbers on it. `runs_code` is the
wider event, disclosed: any interpreter other than a bare `--version`, a
subagent, a pipeline over the data file, or a `__pycache__` left in the
workspace, which only an import of the project's own module does. Computing
the proposed table from the code is in it, and is arguably the proposal
rather than proof of it.

**Primary:** the rate at which `simplify-*` answers analyse the data falls,
opus, pooled one-sided Fisher, alpha 0.05, and the edit's rate is at most
`MARGIN` times the control's.

**Fatal bounds**, one-sided Fisher for a fall, uncorrected:
- `verify-*` answers that analyse the data, pooled: an explicit request to
  check is still honoured.
- `simplify-*` answers that call any tool, pooled: the proposal is still read
  from the files.
- panel-judged pass rate on `simplify-*`, pooled, when the judgments are given.
- panel-judged pass rate on the scored-suite cells `quota-merge` and
  `verdict-experiment` on opus, pooled, when their judgments are given.
- panel-judged pass rate on `count-*`, pooled, when the simplify judgments
  carry it (round 118). `count-*` asks how many rows of the data file the
  correction step changes, a fact only the data holds, without asking for a
  run, so an edit that leaves running the data to the user must still count.
  Its `analyses_data` rate is disclosed beside it and decides nothing.

Round 118 also counts a `Grep` call in count mode over the data file as
analysing it, in both events, so an edit cannot move a tally from `Bash` to
the search tool unseen. No round 116 run made one: its 1,375 calls are
1,372 `Bash` and 3 `Read`.
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

MODEL = "opus"
STEMS = ("rates", "routing", "quota")
DATA = {"rates": "orders_2026-09.csv", "routing": "alerts_2026-09.csv",
        "quota": "accounts.csv"}
CORE = ("quota-merge", "verdict-experiment")
#: What `count-*` asks for: the rows of the data file the correction changes.
COUNT = {"rates": 13, "routing": 22, "quota": 62}
#: At 60 a side, 60/60 against 55/60 is one-sided p = 0.03. A sentence added
#: to every session has to buy more than that, so the edit has to halve it.
MARGIN = 0.5

INTERPRETER = re.compile(
    r"(?<![\w.-])(python3?(\.\d+)?|node|perl|ruby|php|Rscript|sqlite3|duckdb"
    r"|g?awk|mawk|jq)(?![\w.-])")
VERSION_ONLY = re.compile(
    r"(?<![\w.-])(python3?(\.\d+)?|node|perl|ruby)\s+(--version|-V)\b")
AGGREGATE = re.compile(r"(?<![\w.-])(sort|uniq|cut|datamash)(?![\w.-])|grep\s+-c")
DELEGATE = {"Agent", "Task"}


def grep_counts(run, data):
    """A `Grep` call in count mode whose path or glob names the data file."""
    for name, inp in zip(run.get("tools") or [], run.get("tool_inputs") or []):
        if name == "Grep" and isinstance(inp, dict) \
                and inp.get("output_mode") == "count" \
                and data in "%s %s" % (inp.get("path") or "", inp.get("glob") or ""):
            return True
    return False

#: A past-tense report of a check. Disclosed beside `runs_code`, to show an
#: answer reporting a result its tools never produced.
CLAIM = re.compile(
    r"\b(I (checked|ran|priced|repriced|verified|tested|confirmed|compared|"
    r"simulated|replayed|recomputed)|came out (the )?same|all \d+ [^.]{0,40}"
    r"(match|matched|came out|route the same|routed the same|kept))", re.I)


def stem_of(run):
    return (run.get("case") or "").split("-", 1)[-1]


def commands(run):
    """(tool name, Bash command or '') per call, in order."""
    names = run.get("tools") or []
    inputs = run.get("tool_inputs") or [None] * len(names)
    out = []
    for name, inp in zip(names, inputs):
        cmd = inp.get("command") if isinstance(inp, dict) else None
        out.append((name, cmd if isinstance(cmd, str) else ""))
    return out


def executes(cmd):
    return bool(INTERPRETER.search(VERSION_ONLY.sub("", cmd)))


def runs_code(run):
    data = DATA.get(stem_of(run), "\0")
    if any("__pycache__" in k for k in run.get("artifacts") or {}):
        return True
    if grep_counts(run, data):
        return True
    for name, cmd in commands(run):
        if name in DELEGATE or executes(cmd):
            return True
        if data in cmd and AGGREGATE.search(cmd):
            return True
    return False


def analyses_data(run):
    data = DATA.get(stem_of(run), "\0")
    return grep_counts(run, data) or any(
        data in cmd and (executes(cmd) or AGGREGATE.search(cmd))
        for _, cmd in commands(run))


def cell(runs, case):
    rows = [r for r in bench_run.usable(runs)
            if r.get("case") == case and r.get("model") == MODEL]
    return {
        "n": len(rows),
        "runs": sum(runs_code(r) for r in rows),
        "data": sum(analyses_data(r) for r in rows),
        "tooled": sum(1 for r in rows if r.get("tools")),
        "claims": sum(1 for r in rows if CLAIM.search(r.get("text") or "")),
        "states": sum(1 for r in rows if re.search(
            r"(?<![\d.,])%d(?!\d|[.,]\d)" % COUNT.get(case.split("-", 1)[-1], -1),
            r.get("text") or "")),
        "claims_unrun": sum(1 for r in rows if not runs_code(r)
                            and CLAIM.search(r.get("text") or "")),
        "words": [words(r) for r in rows],
        "out": [r.get("output_tokens") or 0 for r in rows],
        "cost": sum(r.get("total_cost_usd") or 0.0 for r in rows),
    }


def show(fam, c, label=""):
    print("   %-16s %s n %2d  runs code %2d  on the data %2d  tooled %2d  "
          "claims %2d (%d unrun)  median words %6.1f  output %7.1f  $%.2f"
          % (fam, label, c["n"], c["runs"], c["data"], c["tooled"], c["claims"],
             c["claims_unrun"], metrics.median(c["words"]),
             metrics.median(c["out"]), c["cost"]))


def calibrate(runs):
    print("## Calibration at master rules, %s (chooses nothing)" % MODEL)
    for fam in ("simplify", "verify", "count"):
        for stem in STEMS:
            show("%s-%s" % (fam, stem), cell(runs, "%s-%s" % (fam, stem)))


def pooled(control, edit, fam, key):
    t = [0, 0, 0, 0]
    for stem in STEMS:
        case = "%s-%s" % (fam, stem)
        a, b = cell(control, case), cell(edit, case)
        show(case, a, "control")
        show(case, b, "edit   ")
        t = [t[0] + a[key], t[1] + a["n"], t[2] + b[key], t[3] + b["n"]]
    return t


def primary(control, edit):
    print("## Primary: simplify-* analyses the data, %s, pooled, one-sided"
          % MODEL)
    a, n1, c, n2 = pooled(control, edit, "simplify", "data")
    significant = fall("pooled", a, n1, c, n2)
    halved = bool(n1 and n2) and c / n2 <= MARGIN * a / n1
    print("   edit rate %.3f against %.2f x control %.3f: %s" % (
        c / n2 if n2 else float("nan"), MARGIN, a / n1 if n1 else float("nan"),
        "within the margin" if halved else "outside the margin"))
    return significant and halved


def bounds(control, edit):
    print("## Bound (fatal): verify-* still analyses the data when asked to")
    fired = fall("pooled", *pooled(control, edit, "verify", "data"))
    print("## Bound (fatal): simplify-* still calls a tool")
    t = [0, 0, 0, 0]
    for stem in STEMS:
        a = cell(control, "simplify-" + stem)
        b = cell(edit, "simplify-" + stem)
        t = [t[0] + a["tooled"], t[1] + a["n"], t[2] + b["tooled"], t[3] + b["n"]]
    fired |= fall("pooled", *t)
    return fired


def disclose_count(control, edit):
    """`count-*` analysing the data, when the snapshots carry it. Decides nothing."""
    if not any(r.get("case", "").startswith("count-") for r in control + edit):
        return
    print("## Disclosed: count-* analyses the data (decides nothing)")
    a, n1, c, n2 = pooled(control, edit, "count", "data")
    print("   pooled                       control %3d/%-3d  edit %3d/%-3d"
          % (a, n1, c, n2))
    print("## Disclosed: count-* states the right count, by pattern, no judge")
    s = [sum(cell(side, "count-" + stem)["states"] for stem in STEMS)
         for side in (control, edit)]
    print("   pooled                       control %3d/%-3d  edit %3d/%-3d"
          % (s[0], n1, s[1], n2))


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


def main(argv):
    if argv[:1] == ["--calibrate"] and len(argv) >= 2:
        calibrate([r for p in argv[1:] for r in load(p)])
        return 0
    if len(argv) not in (2, 4, 6):
        sys.exit(__doc__)
    control, edit = load(argv[0]), load(argv[1])
    ok = primary(control, edit)
    fired = bounds(control, edit)
    disclose_count(control, edit)
    if len(argv) >= 4:
        fired |= quality(argv[2], argv[3], "simplify-*",
                         lambda c: c.startswith("simplify-"))
        if any(passes(j, lambda c: c.startswith("count-"))[1]
               for j in argv[2:4]):
            fired |= quality(argv[2], argv[3], "count-*",
                             lambda c: c.startswith("count-"))
    if len(argv) == 6:
        fired |= quality(argv[4], argv[5], "quota-merge and verdict-experiment",
                         lambda c: c in CORE)
    print("## %s" % ("accept basis met" if ok and not fired else "reject"))
    return 0 if ok and not fired else 1


def selftest():
    def run(case, cmds, arts=None, text="A combined table.", tools=None):
        return {"ok": True, "case": case, "model": MODEL, "arm": "laconic",
                "rep": 0, "num_turns": len(cmds) + 1, "text": text,
                "tools": tools or ["Bash"] * len(cmds),
                "tool_inputs": [{"command": c} for c in cmds],
                "artifacts": arts or {}}
    read = ["find . -type f | head -100", "cat price.py README.md zone_rates.csv",
            "wc -l orders_2026-09.csv && head -5 orders_2026-09.csv",
            "for f in limits.py accounts.csv; do cat -n \"$f\"; done",
            "python3 --version"]
    for cmd in read:
        assert not runs_code(run("simplify-rates", [cmd])), cmd
    ran = ["python3 -I -c 'import price'",
           "cd /tmp && python3 - <<'EOF'\nimport csv\nEOF",
           "mkdir -p /tmp/x && cat > /tmp/x/c.py <<'EOF'\nx\nEOF\npython3 /tmp/x/c.py .",
           "awk -F, 'NR>1{n++} END{print n}' orders_2026-09.csv",
           "node -e 'console.log(1)'"]
    for cmd in ran:
        assert runs_code(run("simplify-rates", [cmd])), cmd
    assert runs_code(run("simplify-quota",
                         ["cut -d, -f2- accounts.csv | sort | uniq -c"]))
    assert analyses_data(run("simplify-quota",
                             ["cut -d, -f2- accounts.csv | sort | uniq -c"]))
    assert not runs_code(run("simplify-quota", ["cut -d, -f2 plan_limits.csv"]))
    assert runs_code(run("simplify-rates", ["cat price.py"],
                         arts={"__pycache__/price.cpython-314.pyc": {}}))
    assert runs_code(run("simplify-rates", [""], tools=["Agent"]))
    assert analyses_data(run("simplify-routing",
                             ["python3 -c \"open('alerts_2026-09.csv')\""]))
    assert not analyses_data(run("simplify-routing", ["python3 -c 'import route'"]))
    gc = run("count-routing", [""], tools=["Grep"])
    gc["tool_inputs"] = [{"pattern": "payments", "path": "alerts_2026-09.csv",
                          "output_mode": "count"}]
    assert analyses_data(gc) and runs_code(gc), "a Grep count is a tally"
    gc["tool_inputs"][0]["output_mode"] = "content"
    assert not analyses_data(gc), "a Grep for lines is a peek"
    gc["tool_inputs"][0].update(output_mode="count", path="route.py")
    assert not analyses_data(gc), "counting in the code is not the data"
    said = [run("count-routing", ["python3 c.py"], text=t) for t in
            ("22 alerts.", "It changes 22.", "1,022 rows", "about 22.5", "12")]
    assert cell(said, "count-routing")["states"] == 2
    assert CLAIM.search("I priced all 640 September orders both ways.")
    assert CLAIM.search("All 812 alerts route the same under both.")
    assert not CLAIM.search("To check it, I'd run all 812 alerts through both.")
    hi = [run("simplify-rates", ["python3 c.py"]) for _ in range(20)]
    lo = [run("simplify-rates", ["python3 c.py" if i < 4 else "cat price.py"])
          for i in range(20)]
    assert cell(hi, "simplify-rates")["runs"] == 20
    assert cell(lo, "simplify-rates")["runs"] == 4
    assert cell(lo, "simplify-rates")["tooled"] == 20
    assert fall("selftest", 20, 20, 4, 20)
    assert not fall("selftest", 4, 20, 20, 20)

    def side(k):
        return [run("simplify-" + stem, ["python3 -c \"open('%s')\"" % DATA[stem]
                                         if i < k else "cat README.md"])
                for stem in STEMS for i in range(20)]
    assert primary(side(20), side(4))
    assert not primary(side(20), side(12)), "significant but not halved"
    assert not primary(side(20), side(20))
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
