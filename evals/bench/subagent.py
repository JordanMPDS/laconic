#!/usr/bin/env python3
"""Subagent arm: does a parent's answer degrade when its subagent ran laconic?

`hooks/hooks.json` injects the rule slice on SubagentStart, so a subagent's
report to its parent is written under laconic. Issue #6 asks whether that
costs the parent context it needs. Nothing measured it.

The measurement is a relay. Stage one already exists: every response in the
committed snapshots was produced by a model that read a fixture with tools and
wrote up what it found, which is exactly what a subagent hands back. Stage two
is added here - hand that report, and nothing else, to a parent model and ask
it to answer the original task. Then grade the parent's answer with the same
blind judge and the same `expect.json` the direct answers are graded with.

The relay prompt is byte-identical in every arm and the parent is never told
which arm produced the report, so the only thing that varies is what the
subagent chose to write down.

Four source arms, so the issue's three options are all measured at once:

    via-baseline   no rules at all          option 1, drop the hook
    via-lite       laconic at lite          option 2, pin subagents to lite
    via-full       laconic at full          what ships today
    via-ultra      laconic at ultra         the sharpest form of the worry

Two things in the output are fair to compare across arms, and they are the
two the issue is actually about:

  * the `quality` cases' trap verdicts, whose criteria come from the fixture
    alone (see evals/CRITERIA.md), and
  * never-cut token survival in the parent's answer, since the parent is
    handed no rules in any arm and can only repeat a token the report kept.

`rule-adherence` rows are printed with their grading label and support
nothing, exactly as in report.py.

    subagent.py generate            # relay calls, resumable, writes a snapshot
    judge.py --results ... --out ...
    subagent.py report --markdown ...
"""
import argparse
import fnmatch
import json
import math
import shutil
import statistics
import sys
import tempfile
import zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import judge as bench_judge  # noqa: E402
import report as bench_report  # noqa: E402
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
SNAPSHOTS = ROOT / "evals" / "snapshots"
RELAY_SNAPSHOT = SNAPSHOTS / "subagent.json"
RELAY_JUDGMENTS = SNAPSHOTS / "subagent-judgments.json"

# arm name -> (source snapshot, which arm inside it holds the reports)
SOURCES = {
    "via-baseline": ("results.json", "baseline"),
    "via-lite": ("levels-lite.json", "laconic"),
    "via-full": ("levels-full.json", "laconic"),
    "via-ultra": ("levels-ultra.json", "laconic"),
}
ARM_ORDER = ["via-baseline", "via-lite", "via-full", "via-ultra"]

# Identical in every arm. The parent is told it cannot see the files, because
# it runs with tools in an empty scratch directory: without the sentence it
# goes looking, finds nothing, and answers "I need the repository" in every
# arm alike, which measures the harness rather than the handoff.
RELAY = """You dispatched a subagent to investigate. It has reported back.

You cannot see the codebase, the logs, or any file yourself. The report below \
is everything you have.

The task you dispatched it for:
---
%s
---

The subagent's report:
---
%s
---

Answer the task now, for the person who asked you. Use only the report. If the \
report is missing something the answer needs, say so explicitly instead of \
guessing.
"""


def relay_prompt(case_prompt, report):
    return RELAY % (case_prompt.strip(), report.strip())


def source_runs(snapshot_dir, arms, models, cases, reps):
    """[(arm, source run)] for every report to be relayed, plus the source
    snapshots' metadata. A missing source snapshot is fatal rather than
    quietly dropped: an arm silently absent from the table is the same defect
    as an ungraded run rendering as a pass."""
    out, meta = [], {}
    for arm in arms:
        fname, src_arm = SOURCES[arm]
        path = Path(snapshot_dir) / fname
        snap = bench_run.load_snapshot(str(path))
        if snap is None:
            sys.exit("no source snapshot at %s (needed for arm %s)" % (path, arm))
        picked = [r for r in bench_run.usable(snap["runs"])
                  if r["arm"] == src_arm and r["model"] in models
                  and r["rep"] < reps and fnmatch.fnmatch(r["case"], cases)]
        if not picked:
            sys.exit("source %s has no usable %s runs matching the selection"
                     % (path, src_arm))
        meta[arm] = {
            "snapshot": fname,
            "source_arm": src_arm,
            "laconic_level": snap["metadata"].get("laconic_level"),
            "rules_cksum": snap["metadata"].get("rules_cksum"),
            "reports": len(picked),
        }
        out += [(arm, r) for r in picked]
    return out, meta


def generate(args):
    claude_bin = bench_run.require_claude_bin(args.claude_bin)

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad = [a for a in arms if a not in SOURCES]
    if bad:
        sys.exit("unknown arm(s): %s (valid: %s)" % (", ".join(bad), ", ".join(SOURCES)))
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    work, src_meta = source_runs(args.snapshot_dir, arms, models, args.cases, args.reps)

    # One stamp over every source's rules checksum plus the relay prompt
    # itself. judge.py refuses to grade a snapshot against judgments built for
    # a different stamp, and a reworded relay prompt invalidates the verdicts
    # exactly as a rules change does.
    stamp = str(zlib.crc32(("|".join(
        "%s=%s" % (a, src_meta[a]["rules_cksum"]) for a in sorted(src_meta)
    ) + "|relay=" + RELAY).encode()))

    snap = bench_run.load_snapshot(args.snapshot)
    if snap is None:
        snap = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "claude_cli_version": bench_run._cli_version(claude_bin),
                "git_commit": bench_run._git_commit(),
                "parent_model": args.parent_model,
                "reps": args.reps,
                "models": models,
                "sources": src_meta,
                "rules_cksum": stamp,
            },
            "runs": [],
        }
    elif snap["metadata"].get("rules_cksum") != stamp:
        sys.exit("snapshot was generated from different sources or a different "
                 "relay prompt (cksum %s vs %s); move it aside before regenerating"
                 % (snap["metadata"].get("rules_cksum"), stamp))
    done = bench_run.completed_keys(snap)
    todo = [(arm, r) for arm, r in work
            if bench_run.run_key(r["case"], arm, r["model"], r["rep"]) not in done]

    lock = Lock()
    n = [0]

    def one(item):
        arm, r = item
        prompt = relay_prompt((CASES / r["case"] / "prompt.md").read_text(), r["text"])
        # The parent gets an empty directory, never the fixture: the whole
        # question is what survives the handoff, and a parent that can read
        # the files itself is not relaying anything.
        for attempt in range(2):
            scratch = tempfile.mkdtemp()
            try:
                res = bench_run.call(claude_bin, args.parent_model, prompt, None, scratch)
            finally:
                shutil.rmtree(scratch, ignore_errors=True)
            if res.get("ok"):
                break
        res.update({"case": r["case"], "arm": arm, "model": r["model"], "rep": r["rep"],
                    "report_words": metrics.score(r["text"])["words"]})
        with lock:
            n[0] += 1
            snap["runs"].append(res)
            bench_run.save_snapshot(args.snapshot, snap)
            print("[%d/%d] %-14s %-14s %-7s rep%d %s"
                  % (n[0], len(todo), res["case"], arm, res["model"], res["rep"],
                     "ok" if res.get("ok") else "FAILED"))

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(one, todo))

    bad_runs = len([r for r in snap["runs"] if not r.get("ok")])
    print("\nwrote %s (%d relayed answers, %d failed)"
          % (args.snapshot, len(snap["runs"]), bad_runs))


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]].

    Exact rather than chi-square: the per-cell counts here are in the tens
    and several tables have a zero in them, which is where the approximation
    is worst. Sums every table at least as extreme as the observed one, the
    conventional two-sided definition.
    """
    n = a + b + c + d
    if n == 0 or not (a + b) or not (c + d) or not (a + c) or not (b + d):
        return 1.0

    def p(x):
        return math.comb(a + b, x) * math.comb(c + d, a + c - x) / math.comb(n, a + c)

    lo, hi = max(0, a + c - (c + d)), min(a + b, a + c)
    obs = p(a) * (1 + 1e-9)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs))


def _verdict_counts(judg):
    """{(case, arm, model): {verdict: n}}, with judge infrastructure failures
    split out. Folding a judge outage into not_exercised would make a broken
    judge run look like a run of traps that never fired - report.py splits
    them for the same reason."""
    out = defaultdict(lambda: defaultdict(int))
    for j in judg.get("judgments", []):
        key = (j["case"], j["arm"], j["model"])
        if j.get("verdict") == "not_exercised" and j.get("reason") in bench_judge.INFRA_REASONS:
            out[key]["judge_failed"] += 1
        else:
            out[key][j["verdict"]] += 1
    return out


def _never_cut(runs):
    """(checked, failures) over runs whose case carries never-cut tokens.
    Cases with an empty list are excluded from both, so a zero cannot be read
    as "every response verified"."""
    checked = failures = 0
    for r in runs:
        p = CASES / r["case"] / "expect.json"
        tokens = json.loads(p.read_text())["never_cut"] if p.exists() else []
        if not tokens:
            continue
        checked += 1
        if metrics.never_cut_missing(r.get("text", ""), tokens):
            failures += 1
    return checked, failures


def _rate_row(label, pairs):
    return "| %s | %s |" % (label, " | ".join(
        "%d/%d (%.0f%%)" % (k, n, 100 * k / n) if n else "-" for k, n in pairs))


def render(snap, judg, sources):
    meta = snap["metadata"]
    runs = bench_run.usable(snap["runs"])
    arms = [a for a in ARM_ORDER if any(r["arm"] == a for r in runs)]
    models = sorted(set(r["model"] for r in runs))
    quality = sorted(c.name for c in CASES.iterdir()
                     if (c / "expect.json").exists()
                     and bench_report.case_grading(c.name) == "quality")

    out = []
    out.append("_Generated: %s · CLI: %s · commit: %s_" %
               (meta.get("generated_at"), meta.get("claude_cli_version"),
                meta.get("git_commit")))
    out.append("_Parent model: %s · reps: %s · relay+rules cksum: %s_\n" %
               (meta.get("parent_model"), meta.get("reps"), meta.get("rules_cksum")))
    out.append("**Excluded relay calls (call failed, never scored): %d**\n"
               % len([r for r in snap["runs"] if not r.get("ok")]))

    out.append("### Source of each arm's subagent reports\n")
    out.append("| arm | snapshot | source arm | level | rules cksum | reports |\n"
               "|---|---|---|---|---|--:|")
    for arm in arms:
        s = meta.get("sources", {}).get(arm, {})
        out.append("| %s | `%s` | %s | %s | %s | %d |"
                   % (arm, s.get("snapshot"), s.get("source_arm"),
                      s.get("laconic_level") or "-", s.get("rules_cksum"),
                      len([r for r in runs if r["arm"] == arm])))
    out.append("")

    out.append("### Length of the report the parent received (median words)\n")
    out.append("| arm | " + " | ".join(models) + " |")
    out.append("|---|" + "|".join("--:" for _ in models) + "|")
    for arm in arms:
        cells = []
        for m in models:
            vals = [r.get("report_words", 0) for r in runs
                    if r["arm"] == arm and r["model"] == m]
            cells.append("%.0f" % statistics.median(vals) if vals else "-")
        out.append("| %s | %s |" % (arm, " | ".join(cells)))
    out.append("")

    counts = _verdict_counts(judg)

    def trap_rate(arm, model, cases):
        c = defaultdict(int)
        for (case, a, m), v in counts.items():
            if a == arm and m == model and case in cases:
                for k, n in v.items():
                    c[k] += n
        graded = c["pass"] + c["fail"]
        return c["pass"], graded, c

    if counts:
        out.append("### Trap verdicts on the parent's answer, `quality` cases only\n")
        out.append("The headline comparison. These three cases' criteria come from "
                   "the fixture alone, so a pass means the parent's answer was "
                   "*right*; see [CRITERIA.md](../CRITERIA.md). Rate is passes over "
                   "graded answers - `not_exercised` and judge failures are excluded "
                   "from the denominator and counted below.\n")
        out.append("| arm | " + " | ".join(models) + " |")
        out.append("|---|" + "|".join("--:" for _ in models) + "|")
        for arm in arms:
            out.append(_rate_row(arm, [trap_rate(arm, m, quality)[:2] for m in models]))
        out.append("")

        base = ARM_ORDER[0]
        if base in arms:
            out.append("Against `%s`, two-sided Fisher exact:\n" % base)
            out.append("| arm | model | pass | fail | baseline pass | baseline fail | p |\n"
                       "|---|---|--:|--:|--:|--:|--:|")
            for arm in arms:
                if arm == base:
                    continue
                for m in models:
                    k, n, _ = trap_rate(arm, m, quality)
                    bk, bn, _ = trap_rate(base, m, quality)
                    out.append("| %s | %s | %d | %d | %d | %d | %.3f |"
                               % (arm, m, k, n - k, bk, bn - bk,
                                  fisher_exact(k, n - k, bk, bn - bk)))
            out.append("")

        out.append("### Trap verdicts on the parent's answer, all cases\n")
        out.append("Includes `safety` and `rule-adherence` rows, which support no "
                   "comparison on their own. Present so a case is never silently "
                   "missing from the run.\n")
        out.append("| arm | model | pass | fail | not_exercised | judge_failed |\n"
                   "|---|---|--:|--:|--:|--:|")
        allc = sorted(set(case for case, _, _ in counts))
        for arm in arms:
            for m in models:
                _, _, c = trap_rate(arm, m, allc)
                out.append("| %s | %s | %d | %d | %d | %d |"
                           % (arm, m, c["pass"], c["fail"], c["not_exercised"],
                              c["judge_failed"]))
        out.append("")

        out.append("### Trap verdicts by case\n")
        out.append("| case | grading | arm | pass | fail | not_exercised | judge_failed |\n"
                   "|---|---|---|--:|--:|--:|--:|")
        for case in allc:
            for arm in arms:
                c = defaultdict(int)
                for (cs, a, _), v in counts.items():
                    if cs == case and a == arm:
                        for k, n in v.items():
                            c[k] += n
                out.append("| %s | %s | %s | %d | %d | %d | %d |"
                           % (case, bench_report.case_grading(case), arm, c["pass"],
                              c["fail"], c["not_exercised"], c["judge_failed"]))
        out.append("")

    # The other arm-fair measure, and the one that needs no judge at all: the
    # parent is handed no rules in any arm, so it can only repeat a token its
    # report kept. Reported next to the same count taken on the reports
    # themselves, which separates "the subagent dropped it" from "the subagent
    # kept it and the parent dropped it anyway".
    out.append("### Never-cut token survival\n")
    out.append("Five cases carry never-cut tokens (`badnews`, `code-fidelity`, "
               "`conditional`, `destructive`, `walkthrough`); the other six carry "
               "none and are excluded from both columns. Failures are responses "
               "missing at least one token.\n")
    out.append("| arm | stage | " + " | ".join(models) + " |")
    out.append("|---|---|" + "|".join("--:" for _ in models) + "|")
    for arm in arms:
        for stage, pick in (("subagent report", lambda a, m: [
                                {"case": r["case"], "text": src_text(sources, a, r)}
                                for r in runs if r["arm"] == a and r["model"] == m]),
                            ("parent answer", lambda a, m: [
                                r for r in runs if r["arm"] == a and r["model"] == m])):
            cells = []
            for m in models:
                checked, fails = _never_cut(pick(arm, m))
                cells.append("%d/%d" % (fails, checked) if checked else "-")
            out.append("| %s | %s | %s |" % (arm, stage, " | ".join(cells)))
    out.append("")
    return "\n".join(out) + "\n"


def load_sources(snapshot_dir, meta):
    """{(arm, case, model, rep): report text} for the source snapshots named
    in the relay snapshot's own metadata, so the report can never be rendered
    against a different set of sources than it was generated from."""
    out = {}
    for arm, s in (meta.get("sources") or {}).items():
        snap = bench_run.load_snapshot(str(Path(snapshot_dir) / s["snapshot"]))
        if snap is None:
            continue
        for r in bench_run.usable(snap["runs"]):
            if r["arm"] == s["source_arm"]:
                out[(arm, r["case"], r["model"], r["rep"])] = r.get("text", "")
    return out


def src_text(sources, arm, relay_run):
    return sources.get((arm, relay_run["case"], relay_run["model"], relay_run["rep"]), "")


def report(args):
    snap = bench_run.load_snapshot(args.snapshot)
    if snap is None:
        sys.exit("no snapshot at %s - run `subagent.py generate` first" % args.snapshot)
    if not bench_run.usable(snap["runs"]):
        sys.exit("no usable relay calls in %s - every call failed; nothing to report"
                 % args.snapshot)
    # report.py's loader, not load_snapshot: it tolerates an empty-but-present
    # file (/dev/null as a stand-in for "not judged yet") while still raising
    # on a non-empty file that fails to parse, which is corruption rather than
    # absence.
    judg = bench_report._load_judgments(args.judgments)

    # Same gap check report.py makes: a judge run that was interrupted or run
    # with a narrower glob renders identically to a finished one, just with
    # fewer rows, which reads as "those cells never happened".
    judged = set((j["case"], j["arm"], j["model"], j["rep"]) for j in judg["judgments"])
    usable = set((r["case"], r["arm"], r["model"], r["rep"])
                 for r in bench_run.usable(snap["runs"]))
    missing = usable - judged

    md = render(snap, judg, load_sources(args.snapshot_dir, snap["metadata"]))
    if judg["judgments"] and missing:
        md += ("\n**WARNING: judgments cover %d/%d relayed answers (%d missing).** "
               "Re-run judge.py before trusting the verdict tables.\n"
               % (len(usable) - len(missing), len(usable), len(missing)))
    if not judg["judgments"]:
        md += ("\n**No judgments loaded.** Only the never-cut table above is "
               "populated; run judge.py against this snapshot for the trap "
               "verdicts.\n")

    if args.markdown:
        Path(args.markdown).write_text(md)
        print("wrote %s" % args.markdown)
    else:
        print(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("generate", "report"))
    ap.add_argument("--snapshot", default=str(RELAY_SNAPSHOT))
    ap.add_argument("--judgments", default=str(RELAY_JUDGMENTS))
    ap.add_argument("--snapshot-dir", default=str(SNAPSHOTS))
    ap.add_argument("--arms", default=",".join(ARM_ORDER))
    ap.add_argument("--models", default="haiku,sonnet")
    ap.add_argument("--parent-model", default="sonnet")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--cases", default="*")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--markdown")
    args = ap.parse_args()
    (generate if args.mode == "generate" else report)(args)


if __name__ == "__main__":
    main()
