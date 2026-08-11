#!/usr/bin/env python3
"""Blind trap grading.

The judge never learns which arm produced a response - arm names do not appear
in its prompt - so it cannot be biased toward or against the plugin under test.

not_exercised is a first-class verdict. v0.1.0 recorded three traps that never
fired; without this category they would have been read as passes.
"""
import argparse
import fnmatch
import json
import re
import shutil
import sys
import tempfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as bench_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
JUDGMENTS = ROOT / "evals" / "snapshots" / "judgments.json"

VERDICTS = ("pass", "fail", "not_exercised")

# Infrastructure reasons a judgment can carry: the call itself failed, or it
# succeeded but the model's reply couldn't be parsed as a verdict. Neither is
# a real "the trap never fired" result. Defined once here and imported by
# report.py so the two modules can't drift onto different magic strings.
REASON_JUDGE_CALL_FAILED = "judge call failed"
REASON_UNPARSEABLE = "unparseable"
INFRA_REASONS = (REASON_JUDGE_CALL_FAILED, REASON_UNPARSEABLE)

# The cost fields run.py's parse_cli_json already lifts off every call. Named
# here rather than inlined because prefer.py records the same set, and a round
# that prices its generation calls on one field list and its judge calls on
# another is not a round anyone can total.
USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                "cache_read_input_tokens", "total_cost_usd", "duration_ms",
                "num_turns")

TEMPLATE = """You are grading one response against one specific criterion.

The question that was asked:
---
%s
---

The criterion:
---
%s
---

The response to grade:
---
%s
---

Reply with a single JSON object and nothing else:
{"verdict": "pass" | "fail" | "not_exercised", "quote": "<short verbatim quote from the response that justifies the verdict, or empty>", "reason": "<one sentence>"}

Use "not_exercised" when the response does not engage the criterion at all -
for example it asks for missing context, declines for want of a live service,
or answers a different question. That is neither a pass nor a fail.
"""


def build_judge_prompt(case_prompt, trap, response):
    return TEMPLATE % (case_prompt.strip(), trap.strip(), response.strip())


def usage_of(res):
    """The cost fields off one call, as a nested dict.

    bench_run.call returns these on every successful call and both graders
    discarded them, so a round priced its 340 generation calls and left its
    340 judge calls and 700 preference comparisons unpriced (#68). Nested
    under a single key rather than flattened onto the record: report.py reads
    output_tokens off a *run* as the length metric the loop targets, and a
    judgment carrying a flat output_tokens of its own is a field that means
    something different under the same name.

    A failed call carries no usage - bench_run.call returns a bare
    {"ok": False} - so the zeros are the truth about it rather than a
    placeholder, and a retry that succeeds overwrites the record with its own.
    """
    return {k: res.get(k, 0) for k in USAGE_FIELDS}


def criteria_cksum(cases_dir):
    """A checksum over exactly what the judge is shown: each case's trap.

    This is the condition under which one round's verdicts may be reused by
    another, and the loop already states it in prose - "if you correct a
    criterion, re-judge every round you will compare". Two case criteria have
    been corrected against the real software they describe and both moved
    verdicts, so the rule is not hypothetical.

    Only `trap` is hashed, not the whole file. expect.json also carries
    never_cut, grading, saturated_models and criteria_source, and none of
    those reaches the judge's prompt: saturating ordered-steps/haiku on
    2026-08-11 changed that file without changing a single grading, and a
    whole-file hash would have refused a carry that was perfectly valid.
    """
    traps = {}
    for d in sorted(Path(cases_dir).iterdir()):
        p = d / "expect.json"
        if p.is_file():
            traps[d.name] = json.loads(p.read_text()).get("trap", "")
    return str(zlib.crc32(json.dumps(traps, sort_keys=True).encode()))


def carry_judgments(prior, at, done, source, snap, arms, source_path, criteria):
    """Copy the carried arms' verdicts forward instead of re-grading them.

    run.py carries the control arms because no control carries rules in its
    system prompt, so they cannot have moved, and #77 stopped billing the round
    for those generations. judge.py then graded every run in the snapshot
    anyway: round 14 spent $25.05 of its $41.37 judging bill re-grading 510
    carried responses that are byte-identical to the baseline's, already graded
    there, and read by no fatal gate - `_judge_fail_cells` filters to the
    laconic arm (#83). That is 60% of the round's judge calls.

    Re-grading them was not merely wasteful, it was worse than free: the judge
    disagrees with itself on 5 to 10% of identical text (#70), so every round
    re-rolled its own comparison rows.

    Only keys that exist as usable runs in this snapshot are copied, and a key
    already decided here is left alone - a carry is not allowed to overwrite a
    grading this round performed. Anything the source does not cover stays on
    the todo list and is judged normally, so a partial source degrades to fewer
    calls rather than to missing verdicts.

    Returns the provenance record to stamp into metadata.
    """
    wanted = {(r["case"], r["arm"], r["model"], r["rep"])
              for r in bench_run.usable(snap["runs"]) if r["arm"] in arms}
    copied = 0
    for j in source.get("judgments", []):
        key = (j.get("case"), j.get("arm"), j.get("model"), j.get("rep"))
        if key not in wanted or key in done or _is_infra_failure(j):
            continue
        # Marked on the record, not merely in metadata: report.py prices a
        # round by splitting calls this round bought from calls it inherited,
        # and the marker is what makes that split truthful per record. Round
        # 14 re-graded its controls and really did pay $25.05 for them, so a
        # file without markers must keep counting them as this round's cost.
        rec = dict(j, carried=True)
        if key in at:
            prior["judgments"][at[key]] = rec
        else:
            at[key] = len(prior["judgments"])
            prior["judgments"].append(rec)
        done.add(key)
        copied += 1
    src_criteria = (source.get("metadata") or {}).get("criteria_cksum")
    return {"path": source_path, "arms": sorted(arms), "judgments": copied,
            "uncovered": len(wanted) - copied,
            "criteria_cksum": src_criteria,
            "criteria_verified": bool(src_criteria) and src_criteria == criteria}


def _is_infra_failure(j):
    """Was this record written because the call failed, not because the judge
    reached a verdict? Such a record is stored as not_exercised so the file
    stays one-record-per-response, but it carries no grading and must not be
    treated as finished work (#67).
    """
    return (j.get("verdict") == "not_exercised"
            and j.get("reason") in INFRA_REASONS)


def resume_index(judgments):
    """(at, done) for a resume: where each judgment lives, and which are final.

    A retry repairs a record, it does not add one, and a record written because
    the call failed is not a record (#67). So `at` maps every key to its
    position - the retry overwrites in place - while `done` holds only the keys
    whose judgment is a real grading.

    prefer.py learned this as #55 and run.py as #61. This is the third harness
    with the same mistake, so the rule is worth stating plainly: a resume is a
    second attempt at one item, never a second item, and a failed attempt is
    not an attempt that finished.
    """
    at = {(j["case"], j["arm"], j["model"], j["rep"]): i
          for i, j in enumerate(judgments)}
    done = set(k for k, i in at.items() if not _is_infra_failure(judgments[i]))
    return at, done


def parse_verdict(raw):
    out = {"verdict": "not_exercised", "quote": "", "reason": REASON_UNPARSEABLE}
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return out
    if not isinstance(d, dict) or d.get("verdict") not in VERDICTS:
        return out
    return {"verdict": d["verdict"], "quote": d.get("quote", "") or "",
            "reason": d.get("reason", "") or ""}


def _call_blind(claude_bin, model, prompt):
    """One judge call, retried once on failure - mirrors run.py's retry, so
    a service blip doesn't get recorded as a permanent judge-call failure and
    excluded from every future resume.

    Each attempt runs in its own fresh temp dir, never the repo root:
    evals/snapshots/results.json labels every response by arm, and
    rules/laconic.md is the treatment's own system prompt. Grading from
    ROOT would let the judge see both (see evals/run.sh for why that
    matters), breaking the blindness this module's docstring promises.
    """
    res = {"ok": False}
    for _ in range(2):
        scratch = tempfile.mkdtemp()
        try:
            res = bench_run.call(claude_bin, model, prompt, None, scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        if res.get("ok"):
            return res
    return res


def main():
    global CASES
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--cases", default="*")
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--out", default=str(JUDGMENTS))
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--cases-dir", default=str(CASES),
                    help="case directory holding expect.json; evals/holdout for the reserved set")
    ap.add_argument("--jobs", type=int, default=6,
                    help="judgments in flight at once; each is its own subprocess. "
                         "6 matches prefer.py. Raising it has not been shown to get "
                         "more work done: round 12 lost 666 of 850 calls running "
                         "strictly sequentially, so the binding constraint was the "
                         "service rather than the harness, and more workers may "
                         "reach that ceiling sooner. Raise it only with evidence, "
                         "and record what the failure rate did (#71).")
    ap.add_argument("--carry-judgments-from",
                    help="judgments snapshot to copy the carried arms' verdicts from, "
                         "instead of re-grading responses an earlier round already "
                         "graded. Pairs with run.py --carry-arms-from, and the arms "
                         "it copies are the ones that snapshot recorded carrying (#83)")
    args = ap.parse_args()

    CASES = Path(args.cases_dir)

    claude_bin = bench_run.resolve_claude_bin(args.claude_bin)
    if not bench_run.claude_bin_usable(claude_bin):
        sys.exit("claude binary not found or not executable: %s "
                 "(set --claude-bin or fix PATH)" % args.claude_bin)

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)

    prior = bench_run.load_snapshot(args.out) or {"metadata": {}, "judgments": []}

    # A results.json regenerated after a rules change (new rules_cksum) must
    # not be graded against a judgments.json built for the old one - that
    # would publish stale verdicts under a fresh provenance stamp. Only fires
    # once prior actually carries a stamp; a fresh/empty judgments file has
    # nothing to conflict with.
    #
    # Stored/read as "rules_cksum" - it is the rules checksum out of
    # results.json's own metadata, not a hash of results.json's content, so
    # two different results.json runs against unchanged rules share this
    # value and are (correctly) treated as compatible even though the actual
    # response text differs. "results_cksum" is read as a fallback so
    # judgments files written before this field was renamed still enforce
    # the guard.
    rules_cksum = snap["metadata"].get("rules_cksum")
    prior_meta = prior.get("metadata", {})
    prior_cksum = prior_meta.get("rules_cksum", prior_meta.get("results_cksum"))
    if prior_cksum and prior_cksum != rules_cksum:
        sys.exit("judgments were generated from different results (cksum %s vs %s); "
                 "move %s aside before regenerating"
                 % (prior_cksum, rules_cksum, args.out))

    # A retry repairs a record, it does not add one, and a record that failed
    # is not a record (#67). Both halves of that matter:
    #
    # done holds only *decided* judgments, so an infra failure is retried on
    # the next run instead of being skipped forever. Round 12's judging pass
    # returned 850 judgments of which 666 were REASON_JUDGE_CALL_FAILED, and
    # re-running the command changed nothing, because every failure counted as
    # done. report.py excludes INFRA_REASONS from the counters, so no verdict
    # was ever graded wrong - the round would simply have been scored from 184
    # judgments while presenting as 850.
    #
    # at maps a key to its position, so the retry overwrites the failed record
    # in place. prefer.py learned the same lesson as #55 and run.py as #61;
    # this is the third harness and the pattern is the same one.
    at, done = resume_index(prior["judgments"])

    criteria = criteria_cksum(CASES)
    meta = {"judge_model": args.model, "rules_cksum": rules_cksum,
            "criteria_cksum": criteria}

    # The carried arms' verdicts are copied, not bought again (#83).
    if args.carry_judgments_from:
        arms = set((snap["metadata"].get("carried_arms_from") or {}).get("arms") or [])
        if not arms:
            sys.exit("%s records no carried arms, so there is nothing to carry "
                     "judgments for; drop --carry-judgments-from" % args.results)
        source = bench_run.load_snapshot(args.carry_judgments_from)
        if source is None:
            sys.exit("no judgments snapshot to carry from: %s"
                     % args.carry_judgments_from)
        prov = carry_judgments(prior, at, done, source, snap, arms,
                               args.carry_judgments_from, criteria)
        meta["carried_judgments_from"] = prov
        print("carried %d judgment(s) for arm(s) %s from %s"
              % (prov["judgments"], ", ".join(prov["arms"]), prov["path"]))
        if prov["uncovered"]:
            print("  %d carried run(s) are not covered by that file and will be "
                  "judged normally" % prov["uncovered"])
        if not prov["criteria_verified"]:
            # Loud rather than silent, and recorded in the snapshot as well, so
            # a reader of the file is not relying on someone having watched the
            # terminal. A file written before criteria_cksum existed has no
            # stamp to check, which is every judgments file committed to date.
            print("  WARNING: the source carries %s, so the criteria behind those "
                  "verdicts are NOT verified against the criteria in %s. Carry "
                  "only if no case criterion has changed since it was written."
                  % ("criteria_cksum %s, which differs from this run's %s"
                     % (prov["criteria_cksum"], criteria)
                     if prov["criteria_cksum"] else "no criteria_cksum",
                     args.cases_dir))

    # Assigned before the loop, not inside it: a pass with nothing left to
    # judge - every key carried, or a completed resume - must still write its
    # provenance, and a loop body is not reached when todo is empty.
    prior["metadata"] = meta

    # Same glob semantics as run.py --cases, so the two flags select alike.
    runs = [r for r in bench_run.usable(snap["runs"])
            if fnmatch.fnmatch(r["case"], args.cases)]
    todo = [r for r in runs
            if (r["case"], r["arm"], r["model"], r["rep"]) not in done]

    def judge_one(r):
        """One judgment. Every call is an independent subprocess against an
        independent temp dir - _call_blind makes it so for blindness, and that
        buys thread safety for free - so this runs in a worker thread and
        touches no shared state. The snapshot is written by the main thread
        only, which is what makes the resume file consistent if the run is
        killed mid-pass (#71).
        """
        case_dir = CASES / r["case"]
        expect = json.loads((case_dir / "expect.json").read_text())
        prompt = build_judge_prompt((case_dir / "prompt.md").read_text(),
                                    expect["trap"], r["text"])
        res = _call_blind(claude_bin, args.model, prompt)
        v = parse_verdict(res.get("text", "")) if res.get("ok") else \
            {"verdict": "not_exercised", "quote": "", "reason": REASON_JUDGE_CALL_FAILED}
        v.update({"case": r["case"], "arm": r["arm"], "model": r["model"], "rep": r["rep"],
                  "usage": usage_of(res)})
        return v

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, v in enumerate(pool.map(judge_one, todo), 1):
            key = (v["case"], v["arm"], v["model"], v["rep"])
            if key in at:
                prior["judgments"][at[key]] = v
            else:
                at[key] = len(prior["judgments"])
                prior["judgments"].append(v)
            bench_run.save_snapshot(args.out, prior)  # after each: resumable if killed
            print("[%d/%d] %-14s %-16s %-7s rep%d -> %s"
                  % (i, len(todo), v["case"], v["arm"], v["model"], v["rep"],
                     v["verdict"]), flush=True)

    bench_run.save_snapshot(args.out, prior)
    print("\nwrote %s (%d judgments)" % (args.out, len(prior["judgments"])))


if __name__ == "__main__":
    main()
