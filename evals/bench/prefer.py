#!/usr/bin/env python3
"""Blind pairwise preference over responses that already exist.

Reads evals/snapshots/results.json and regenerates nothing: every comparison
reuses two responses the benchmark already paid for. One call per comparison.

Three things this shares with judge.py, for the same reasons:

- The judge never sees an arm name, so it cannot favour the plugin under test.
- Each call runs in a fresh temp dir, never the repo root, so the judge cannot
  read rules/laconic.md or the arm labels in results.json.
- "tie" is a first-class verdict. Folding ties into either side would invent a
  preference the judge declined to express, the same failure not_exercised
  exists to prevent in judge.py.

Position bias in an LLM judge is large enough to produce a result on its own,
so A/B order is decided by a checksum of (case, model, rep) rather than by arm,
and --both-orders re-runs a subset with the sides swapped to measure the flip
rate. Below the judge's own noise the headline is not publishable.
"""
import argparse
import collections
import json
import re
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run as bench_run  # noqa: E402
import judge as bench_judge  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "cases"
RESULTS = ROOT / "evals" / "snapshots" / "results.json"
PREFERENCES = ROOT / "evals" / "snapshots" / "preferences.json"

WINNERS = ("A", "B", "tie")

TEMPLATE = """Two assistants answered the same question. You are deciding which
answer better serves the person who asked it.

The question:
---
%s
---

Answer A:
---
%s
---

Answer B:
---
%s
---

Judge which answer better serves the person who asked: correct, complete enough
to act on, and no harder to read than it needs to be. Length is not itself a
virtue or a fault - judge whether what is present earns its place and whether
anything the reader needed is missing.

Reply with a single JSON object and nothing else:
{"winner": "A" | "B" | "tie", "reason": "<one sentence>"}

Use "tie" when neither answer serves the reader better than the other. A tie is
a real verdict, not a way to avoid choosing.
"""


def build_prompt(case_prompt, text_a, text_b):
    return TEMPLATE % (case_prompt.strip(), text_a.strip(), text_b.strip())


def treatment_is_a(case, model, rep, order):
    """Deterministic A/B assignment, reproducible across runs.

    Keyed off the comparison, never off the arm, so the treatment lands in
    position A for about half the comparisons and a re-run reproduces the same
    layout.

    order=1 is the exact inverse of order=0, not a second hash. Hashing the
    order in would put the treatment back in the same position for half the
    flipped subset, and those comparisons would measure nothing - the flip rate
    they exist to produce would be diluted by repeats scored as agreements.
    """
    key = "%s|%s|%d" % (case, model, rep)
    return ((zlib.crc32(key.encode()) & 1) == 0) != bool(order)


def parse_winner(raw):
    out = {"winner": None, "reason": bench_judge.REASON_UNPARSEABLE}
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return out
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return out
    if not isinstance(d, dict) or d.get("winner") not in WINNERS:
        return out
    return {"winner": d["winner"], "reason": d.get("reason", "") or ""}


def winning_arm(winner, treatment, control, t_is_a):
    """Map the judge's position verdict back onto an arm name."""
    if winner == "tie":
        return "tie"
    if winner is None:
        return None
    return (treatment if t_is_a else control) if winner == "A" else \
           (control if t_is_a else treatment)


def pairs_from(snap, treatment, control):
    """Every (case, model, rep) where both arms produced a usable response."""
    by = collections.defaultdict(dict)
    for r in bench_run.usable(snap["runs"]):
        by[(r["case"], r["model"], r["rep"])][r["arm"]] = r["text"]
    out = []
    for key in sorted(by):
        texts = by[key]
        if treatment in texts and control in texts:
            out.append((key, texts[treatment], texts[control]))
    return out


def both_orders_subset(keys, n):
    """Evenly spread across the sorted keys rather than taking a prefix, so the
    flip-rate subset is not one case's worth of comparisons."""
    if n <= 0 or not keys:
        return []
    if n >= len(keys):
        return list(keys)
    stride = len(keys) / float(n)
    return [keys[int(i * stride)] for i in range(n)]


def tally(records, treatment, control):
    c = collections.Counter(r["winner_arm"] for r in records if r["order"] == 0)
    return {treatment: c[treatment], control: c[control], "tie": c["tie"],
            "unparseable": c[None]}


def by_position(records, treatment, control):
    """Treatment win/loss split by the position it was shown in.

    The flip rate says the verdicts move; this says which way. If the treatment
    wins far more often from one side than the other, the headline tally is
    reporting where the answers sat, and the gap between these two rates is the
    number to read instead of it.
    """
    out = {}
    for pos in ("A", "B"):
        c = collections.Counter(r["winner_arm"] for r in records
                                if r["order"] == 0 and r["treatment_position"] == pos)
        out[pos] = (c[treatment], c[control], c["tie"])
    return out


def longer_won(records, lengths, treatment, control):
    """How often the judge picked the longer of the two answers.

    An LLM judge is documented to favour length, and the treatment is the short
    arm by construction, so this bias runs against it. Measured per run rather
    than cited, because it is the number that decides how a loss may be read:
    a treatment loss no larger than the length effect is not a preference
    result. Ties and unparseable verdicts have no winner to compare, and equal
    lengths have no longer answer, so both are excluded from the denominator.
    """
    won = total = 0
    for r in records:
        if r["order"] != 0 or r["winner_arm"] in (None, "tie"):
            continue
        key = (r["case"], r["model"], r["rep"])
        t_len, c_len = lengths.get((key, treatment)), lengths.get((key, control))
        if t_len is None or c_len is None or t_len == c_len:
            continue
        total += 1
        win_len, lose_len = (t_len, c_len) if r["winner_arm"] == treatment else (c_len, t_len)
        if win_len > lose_len:
            won += 1
    return won, total


def response_lengths(snap):
    """{((case, model, rep), arm): length} from a results.json snapshot."""
    return {((r["case"], r["model"], r["rep"]), r["arm"]): len(r["text"])
            for r in bench_run.usable(snap["runs"])}


def _dedupe(records):
    """One record per (case, model, rep, order), a decided one winning.

    Order is preserved by first appearance, so a repaired file still reads in
    the sequence it was generated in.
    """
    at, out = {}, []
    for r in records:
        key = (r["case"], r["model"], r["rep"], r["order"])
        if key not in at:
            at[key] = len(out)
            out.append(r)
        elif out[at[key]]["winner_arm"] is None:
            out[at[key]] = r
    return out


def flip_rate(records):
    """Comparisons run in both orders whose verdict did not survive the flip.

    Returns (flipped, both, undecided). A comparison whose judge call failed
    carries winner_arm None, and None != "baseline" is true, so counting it as
    a flip manufactures position bias out of an API error - round 09 lost its
    whole reversed-order pass that way and scored 95% from zero decided pairs
    (#55). A pair with an undecided side leaves both counters and is disclosed
    separately.
    """
    by = collections.defaultdict(dict)
    for r in records:
        by[(r["case"], r["model"], r["rep"])][r["order"]] = r["winner_arm"]
    both = [v for v in by.values() if 0 in v and 1 in v]
    decided = [v for v in both if v[0] is not None and v[1] is not None]
    flipped = [v for v in decided if v[0] != v[1]]
    return len(flipped), len(decided), len(both) - len(decided)


def report(records, treatment, control, lengths=None):
    t = tally(records, treatment, control)
    n = sum(t.values()) - t["unparseable"]
    print("\n| arm | wins |\n|---|--:|")
    for arm in (treatment, control, "tie"):
        pct = (100.0 * t[arm] / n) if n else 0.0
        print("| %s | %d (%.0f%%) |" % (arm, t[arm], pct))
    if t["unparseable"]:
        print("\n%d comparison(s) unparseable and excluded." % t["unparseable"])

    per = collections.defaultdict(collections.Counter)
    for r in records:
        if r["order"] == 0:
            per[r["model"]][r["winner_arm"]] += 1
    print("\n| model | %s | %s | tie |\n|---|--:|--:|--:|" % (treatment, control))
    for model in sorted(per):
        c = per[model]
        print("| %s | %d | %d | %d |" % (model, c[treatment], c[control], c["tie"]))

    pos = by_position(records, treatment, control)
    print("\n| %s shown as | wins | losses | ties | win rate |\n|---|--:|--:|--:|--:|"
          % treatment)
    for side in ("A", "B"):
        w, l, t_ = pos[side]
        rate = (100.0 * w / (w + l)) if (w + l) else 0.0
        print("| %s | %d | %d | %d | %.0f%% |" % (side, w, l, t_, rate))

    if lengths:
        won, total = longer_won(records, lengths, treatment, control)
        if total:
            print("\nThe longer answer won %d of %d decided comparisons (%.0f%%). "
                  "The judge's length bias runs against the short arm, so a %s loss "
                  "no larger than this is not a preference result."
                  % (won, total, 100.0 * won / total, treatment))

    flipped, both, undecided = flip_rate(records)
    if both:
        print("\nOrder flip rate: %d of %d comparisons run in both orders "
              "changed verdict (%.0f%%)." % (flipped, both, 100.0 * flipped / both))
        if flipped * 2 >= both:
            print("At or above 50% the judge is measuring position, not quality - "
                  "do not publish the table above as a preference result.")
    else:
        print("\nNo comparisons were decided in both orders, so the flip rate is "
              "unmeasured and the table above carries no position-bias control.")
    if undecided:
        print("%d pair(s) had an undecided side and left the flip rate; re-run "
              "to fill them before citing preference." % undecided)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sonnet", help="judge model")
    ap.add_argument("--treatment", default="laconic")
    ap.add_argument("--control", default="baseline")
    ap.add_argument("--both-orders", type=int, default=20,
                    help="comparisons to also run flipped, for the flip rate")
    ap.add_argument("--results", default=str(RESULTS))
    ap.add_argument("--out", default=str(PREFERENCES))
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--jobs", type=int, default=6,
                    help="comparisons in flight at once; each is its own subprocess")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be called and spend nothing")
    ap.add_argument("--report-only", action="store_true",
                    help="tally an existing preferences.json without calling")
    args = ap.parse_args()

    snap = bench_run.load_snapshot(args.results)
    if snap is None:
        sys.exit("no snapshot at %s - run run.py first" % args.results)
    prior = bench_run.load_snapshot(args.out) or {"metadata": {}, "comparisons": []}

    if args.report_only:
        if not prior["comparisons"]:
            sys.exit("no comparisons in %s" % args.out)
        m = prior["metadata"]
        report(prior["comparisons"], m.get("treatment", args.treatment),
               m.get("control", args.control), response_lengths(snap))
        return

    pairs = pairs_from(snap, args.treatment, args.control)
    if not pairs:
        sys.exit("no (case, model, rep) has both %s and %s"
                 % (args.treatment, args.control))
    flip_keys = set(both_orders_subset([k for k, _, _ in pairs], args.both_orders))

    work = [(k, t, c, 0) for k, t, c in pairs]
    work += [(k, t, c, 1) for k, t, c in pairs if k in flip_keys]

    if args.dry_run:
        chars = sum(len(t) + len(c) for _, t, c, _ in work)
        print("%d comparisons (%d forward, %d flipped) over %d responses"
              % (len(work), len(pairs), len(work) - len(pairs), 2 * len(pairs)))
        print("~%d tokens of answer text in total, one call each, no regeneration"
              % (chars // 4))
        return

    # Same guard as judge.py: verdicts built against one rules revision must not
    # be topped up from a snapshot generated against another.
    rules_cksum = snap["metadata"].get("rules_cksum")
    prior_cksum = prior.get("metadata", {}).get("rules_cksum")
    if prior_cksum and prior_cksum != rules_cksum:
        sys.exit("preferences were generated from different results (cksum %s vs %s); "
                 "move %s aside before regenerating"
                 % (prior_cksum, rules_cksum, args.out))

    claude_bin = bench_run.resolve_claude_bin(args.claude_bin)
    if not bench_run.claude_bin_usable(claude_bin):
        sys.exit("claude binary not found or not executable: %s "
                 "(set --claude-bin or fix PATH)" % args.claude_bin)

    # Collapse any duplicate keys a pre-#55 resume left behind, keeping a
    # decided record over an undecided one for the same comparison. Without
    # this a file can hold both, and any tally that counts records rather
    # than keys double-counts: round-09-preferences.json held 192 records for
    # 160 comparisons.
    prior["comparisons"] = _dedupe(prior["comparisons"])
    at = {(c["case"], c["model"], c["rep"], c["order"]): i
          for i, c in enumerate(prior["comparisons"])}
    done = set(k for k, i in at.items()
               if prior["comparisons"][i]["winner_arm"] is not None)
    todo = [w for w in work if (w[0][0], w[0][1], w[0][2], w[3]) not in done]

    def judge_one(item):
        """One comparison. Every call is an independent subprocess against an
        independent temp dir, so this runs in a worker thread and touches no
        shared state - the snapshot is written by the main thread only."""
        (case, model, rep), t_text, c_text, order = item
        t_is_a = treatment_is_a(case, model, rep, order)
        a, b = (t_text, c_text) if t_is_a else (c_text, t_text)
        prompt = build_prompt((CASES / case / "prompt.md").read_text(), a, b)
        res = bench_judge._call_blind(claude_bin, args.model, prompt)
        v = parse_winner(res.get("text", "")) if res.get("ok") else \
            {"winner": None, "reason": bench_judge.REASON_JUDGE_CALL_FAILED}
        return {
            "case": case, "model": model, "rep": rep, "order": order,
            "treatment_position": "A" if t_is_a else "B",
            "winner": v["winner"],
            "winner_arm": winning_arm(v["winner"], args.treatment, args.control, t_is_a),
            "reason": v["reason"],
        }

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, rec in enumerate(pool.map(judge_one, todo), 1):
            # Replace the failed record for this comparison rather than
            # appending beside it (#55): a resume is a second attempt at one
            # comparison, not a second comparison.
            key = (rec["case"], rec["model"], rec["rep"], rec["order"])
            if key in at:
                prior["comparisons"][at[key]] = rec
            else:
                at[key] = len(prior["comparisons"])
                prior["comparisons"].append(rec)
            prior["metadata"] = {"judge_model": args.model, "rules_cksum": rules_cksum,
                                 "treatment": args.treatment, "control": args.control}
            bench_run.save_snapshot(args.out, prior)  # after each: resumable if killed
            print("[%d/%d] %-14s %-7s rep%d order%d -> %s"
                  % (i, len(todo), rec["case"], rec["model"], rec["rep"],
                     rec["order"], rec["winner_arm"]), flush=True)

    print("\nwrote %s (%d comparisons)" % (args.out, len(prior["comparisons"])))
    report(prior["comparisons"], args.treatment, args.control, response_lengths(snap))


if __name__ == "__main__":
    main()
