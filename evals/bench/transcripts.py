#!/usr/bin/env python3
"""What the shipped detectors do on the turns of a real session.

    python3 evals/bench/transcripts.py [--projects ~/.claude/projects]
    python3 evals/bench/transcripts.py --sample 40 --seed 283 --sample-out /tmp/s.json

[#283] asks whether the `Stop` hook of rounds 61 and 62 should ship. Those
rounds measured the benefit side; this measures the cost side, which they could
not, because every benchmark turn is a single prose answer to a design or
walkthrough question in a fixture workspace. A shipped hook fires at the end of
**every** turn of a real session, and most of those are tool-call narrations,
one-line acknowledgements and hand-backs. A block on one costs the user a whole
extra generation to rewrite a sentence that may not have been a violation.

The registration, the strata and the decision bars are in
`evals/results/loop/production-turns-283.md`. This file is the arithmetic.

**It reads private transcripts and writes nothing.** Excerpts are printed only
when `--sample` asks for them, and `--sample-out` is for a path outside the
repository. Nothing here should ever put transcript text into a commit.

## What counts as a turn

A turn runs from a real user message to just before the next one, and the hook
input is the last assistant entry in it that carries text - which is what
`last_assistant_message` holds. Four exclusions, each of which would otherwise
inflate the denominator or the rate:

- A `user` entry whose content is a `tool_result`, or which carries `isMeta`, is
  the harness talking to itself. The CLI does not end a turn on one.
- `isSidechain` entries belong to a subagent, which fires `SubagentStop`. That
  is a different hook and neither round measured it.
- A turn whose **last** assistant entry has no text block never reaches a
  `Stop` hook with anything to read, so it is counted apart rather than scored
  as clean. Taking the last text-bearing entry instead would score the opening
  `I'll start by reading it.` of a turn that then called tools and was cut
  short.
- Entries are deduplicated on `uuid`. A resumed session copies its history into
  a new transcript, so the projects with the most sessions would otherwise be
  the most double-counted.
"""
import argparse
import collections
import json
import os
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics  # noqa: E402
import stop_hook  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PROJECTS = "~/.claude/projects"


def text_of(message):
    """The text blocks of one message, joined; "" when it carries none.

    Content is a bare string on a typed user message and a block list on
    everything else. `thinking` and `tool_use` blocks are not text: the hook
    never sees them.
    """
    content = (message or {}).get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(b.get("text", "") for b in content
                     if isinstance(b, dict) and b.get("type") == "text").strip()


def is_real_user(entry):
    """A person's message, not a tool result and not harness bookkeeping."""
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result"
                       for b in content)
    return bool(content)


def used_tool(entry):
    content = (entry.get("message") or {}).get("content")
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_use" for b in content)


def read_entries(path, seen):
    """Conversation entries from one transcript, in order, deduplicated.

    A malformed line is skipped rather than fatal: a transcript being written
    by a live session has a partial last line, and refusing the whole file for
    it would silently drop the newest sessions - the ones most like what a
    shipped hook would meet.
    """
    out = []
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return out
    with fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            if entry.get("type") not in ("user", "assistant"):
                continue
            if entry.get("isSidechain"):
                continue
            uuid = entry.get("uuid")
            if uuid is not None:
                if uuid in seen:
                    continue
                seen.add(uuid)
            out.append(entry)
    return out


def turns_of(entries, project, session):
    """One record per completed turn, with what the `Stop` hook would have read.

    `text` is None for a turn whose **last** assistant entry carried no text,
    and the caller counts those rather than scoring them. The distinction is
    not bookkeeping: an agentic turn opens with `I'll start by reading the
    backlog.` and then calls tools, so taking the last text-bearing entry
    instead of the last entry would hand the hook that opening line whenever
    the turn was cut short - and score an announcement that was followed by the
    work as though it were the whole answer. A turn that ends on a tool call
    ended because the user interrupted it or the session stopped, and neither
    fires `Stop`.

    An entry carrying only `thinking` is not an ending either: it is the
    preface to the next entry, and the hook never sees it.

    Sidechains are dropped here as well as in `read_entries`, so a caller that
    hands over entries from anywhere else cannot accidentally attribute a
    subagent's last reply to the turn that dispatched it.
    """
    out, current = [], None

    def close():
        if current is not None:
            out.append(current)

    for entry in entries:
        if entry.get("isSidechain"):
            continue
        if is_real_user(entry):
            close()
            current = {"project": project, "session": session, "text": None,
                       "tools": False, "entrypoint": entry.get("entrypoint"),
                       "timestamp": entry.get("timestamp"), "uuid": None}
            continue
        if current is None or entry.get("type") != "assistant":
            continue
        text = text_of(entry.get("message"))
        if used_tool(entry):
            current["tools"] = True
        elif not text:
            continue  # thinking only: not an ending, and not a tool call
        current["text"] = text or None
        current["uuid"] = entry.get("uuid") if text else None
    close()
    return out


def scan(root, include_tmp=False):
    """Every turn under a `~/.claude/projects` tree.

    `-tmp*` project directories are the benchmark's own generation workspaces -
    47,585 of the 47,609 directories on the machine this was written for. They
    are excluded by default because rounds 61 and 62 already measured exactly
    those responses, and letting them in would report the benchmark back to
    itself as if it were production.
    """
    root = Path(os.path.expanduser(root))
    seen, out = set(), []
    for project in sorted(p for p in root.iterdir() if p.is_dir()):
        if not include_tmp and project.name.startswith("-tmp"):
            continue
        for path in sorted(project.glob("*.jsonl")):
            entries = read_entries(path, seen)
            out.extend(turns_of(entries, project.name, path.stem))
    return out


def score_turns(turns, level):
    """Attach the detector set to every turn that has text.

    One `Stop` hook firing per turn at most, so a turn is blocked or it is not
    however many detectors fired on it - which is the rate the shipping bar is
    written against.
    """
    for t in turns:
        if t["text"] is None:
            t["decisions"] = None
            continue
        t["decisions"] = sorted(metrics.decisions(t["text"], level))
        t["words"] = metrics.score(t["text"])["words"]
    return turns


def rate(hits, total):
    return "%d/%d (%.1f%%)" % (hits, total, 100.0 * hits / total) if total \
        else "%d/%d (-)" % (hits, total)


def wilson(hits, total):
    """95% Wilson interval, because the bar is written on a lower bound.

    Normal approximation on a proportion near 0 gives a lower bound below zero
    and a bar that can be met by arithmetic rather than by evidence.
    """
    if not total:
        return (0.0, 0.0)
    z, p, n = 1.96, hits / float(total), float(total)
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def group_table(turns, key, title):
    rows = collections.defaultdict(lambda: [0, 0])
    for t in turns:
        row = rows[key(t)]
        row[1] += 1
        if t["decisions"]:
            row[0] += 1
    print("\n| %s | turns | blocked |\n|---|--:|--:|" % title)
    for name in sorted(rows, key=lambda n: -rows[n][1]):
        hits, total = rows[name]
        print("| %s | %d | %s |" % (name, total, rate(hits, total)))


def report(turns, level, excluded):
    """The tables the registration names, in the order it names them.

    `excluded` is passed in whole rather than as a count because its
    composition is decision-relevant: turns that end on a tool call are
    dropped, and structured-output agents end every turn that way. A reader
    who cannot see which population left cannot tell a faithful denominator
    from a convenient one.
    """
    scored = [t for t in turns if t["decisions"] is not None]
    blocked = [t for t in scored if t["decisions"]]
    lo, hi = wilson(len(blocked), len(scored))
    print("# Production turns, level %s\n" % level)
    print("- %d turns scored across %d sessions and %d projects."
          % (len(scored), len({(t["project"], t["session"]) for t in scored}),
             len({t["project"] for t in scored})))
    print("- %d turns ended on a tool call rather than on text and are "
          "excluded; a `Stop` hook does not fire on one." % len(excluded))
    by_entry = collections.Counter(t["entrypoint"] or "(unrecorded)"
                                   for t in excluded)
    if by_entry:
        print("  Excluded by entrypoint: %s."
              % ", ".join("%s %d" % kv for kv in by_entry.most_common()))
    stamps = sorted(t["timestamp"] for t in scored if t["timestamp"])
    if stamps:
        print("- %s to %s." % (stamps[0][:10], stamps[-1][:10]))
    print("\n**Block rate: %s, 95%% [%.1f%%, %.1f%%].**"
          % (rate(len(blocked), len(scored)), 100 * lo, 100 * hi))

    per = collections.Counter(d for t in blocked for d in t["decisions"])
    print("\n| detector | turns it fired on | share of all turns |\n|---|--:|--:|")
    for name, count in per.most_common():
        print("| %s | %d | %.1f%% |" % (name, count, 100.0 * count / len(scored)))
    absent = [n for n in metrics.POLICY_RANK if n not in per]
    if absent:
        print("\nNever fired: %s. `never_cut_missing` cannot fire here at all - "
              "it needs a case's keywords and a real session has none."
              % ", ".join(sorted(absent)))

    group_table(turns=scored, key=lambda t: "tool-bearing" if t["tools"]
                else "prose-only", title="turn shape")
    group_table(turns=scored, key=lambda t: t["entrypoint"] or "(unrecorded)",
                title="entrypoint")
    group_table(turns=scored, key=lambda t: t["project"], title="project")

    buckets = [(0, 20), (20, 60), (60, 200), (200, 10 ** 9)]
    def bucket(t):
        for lo_w, hi_w in buckets:
            if lo_w <= t["words"] < hi_w:
                return "%d-%d words" % (lo_w, hi_w) if hi_w < 10 ** 9 \
                    else "%d+ words" % lo_w
        return "?"
    group_table(turns=scored, key=bucket, title="answer length")


def sample(turns, n, seed, out_path):
    """A random draw of firings, for adjudication. Printed, never committed."""
    blocked = [t for t in turns if t["decisions"]]
    rng = random.Random(seed)
    picked = rng.sample(blocked, min(n, len(blocked)))
    records = [{"id": i + 1, "detectors": t["decisions"], "project": t["project"],
                "tools": t["tools"], "words": t["words"], "text": t["text"]}
               for i, t in enumerate(picked)]
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=1)
        print("\nwrote %d sampled firings to %s (outside the repository)"
              % (len(records), out_path))
    else:
        for r in records:
            print("\n--- %d  %s  %s  %d words ---\n%s"
                  % (r["id"], ",".join(r["detectors"]), r["project"], r["words"],
                     r["text"][:1200]))


ADJUDICATE = """Here are the rules an assistant was working under:

---
%s
---

One rule from them, verbatim:

    %s

Below is the whole of one reply that assistant sent. Judge only whether that
one rule is broken by it, reading the rule as the rules above define it,
carve-outs included. Nothing else about the reply is being asked about.

The reply:
---
%s
---

Reply with a single JSON object and nothing else:
{"broken": true | false, "reason": "<one sentence>"}
"""


def adjudicate(sample_path, model, claude_bin, jobs):
    """A blind second opinion on each sampled firing, against the rule itself.

    The judge is told the rule and the reply and nothing else: not that a
    detector fired, not which one, not that a shipping decision hangs on the
    answer. `kimi` argued for this on `tools/consult.sh` and `codex` argued
    against it - a model from the same family as the one under test is not an
    independent adjudicator - so it is reported beside the operator's own
    labels rather than instead of them, and where they disagree the
    disagreement is shown.

    The rule quoted is the one `stop_hook.choose()` would have quoted, so this
    grades the block the user would actually have received rather than the
    finding set behind it.
    """
    import judge as bench_judge
    from concurrent.futures import ThreadPoolExecutor
    rules = (ROOT / "rules" / "dist" / "laconic-full.md").read_text()
    records = json.loads(Path(sample_path).read_text())
    for r in records:
        r["named"] = stop_hook.choose(r["detectors"])

    def one(r):
        prompt = ADJUDICATE % (rules, metrics.POLICY_RULE[r["named"]], r["text"])
        res = bench_judge._call_blind(claude_bin, model, prompt)
        raw = res.get("text", "") if res.get("ok") else ""
        m = re.search(r"\{.*\}", raw, re.S)
        try:
            verdict = json.loads(m.group(0)) if m else {}
        except ValueError:
            verdict = {}
        return dict(r, blind=verdict.get("broken"),
                    blind_reason=verdict.get("reason", ""))

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        out = list(pool.map(one, records))
    Path(sample_path).write_text(json.dumps(out, indent=1))
    hits = sum(1 for r in out if r["blind"] is True)
    undecided = sum(1 for r in out if r["blind"] is None)
    lo, hi = wilson(hits, len(out) - undecided)
    print("\nblind adjudication, %s: %s called a real violation, 95%% [%.1f%%, %.1f%%]"
          % (model, rate(hits, len(out) - undecided), 100 * lo, 100 * hi))
    if undecided:
        print("%d call(s) returned nothing parseable and left the denominator."
              % undecided)
    per = collections.defaultdict(lambda: [0, 0])
    for r in out:
        if r["blind"] is None:
            continue
        per[r["named"]][1] += 1
        per[r["named"]][0] += 1 if r["blind"] else 0
    print("\n| rule the block would quote | judged a real violation |\n|---|--:|")
    for name in sorted(per):
        print("| %s | %s |" % (name, rate(*per[name])))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", default=DEFAULT_PROJECTS)
    ap.add_argument("--level", default="full", choices=tuple(metrics.LEVEL_RANK))
    ap.add_argument("--include-tmp", action="store_true",
                    help="also read the benchmark's own generation workspaces, "
                         "which rounds 61 and 62 already measured")
    ap.add_argument("--sample", type=int, default=0,
                    help="print this many randomly drawn firings to adjudicate")
    ap.add_argument("--seed", type=int, default=283)
    ap.add_argument("--adjudicate", metavar="SAMPLE",
                    help="blind-judge every firing in a sample file written by "
                         "--sample-out, against the rule the block would have "
                         "quoted, and write the verdicts back into it")
    ap.add_argument("--model", default="sonnet", help="the adjudicating model")
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--sample-out", default=None,
                    help="write the sample here instead of printing it. Use a "
                         "path outside the repository: it holds transcript text")
    args = ap.parse_args(argv)

    if args.adjudicate:
        adjudicate(args.adjudicate, args.model, args.claude_bin, args.jobs)
        return

    turns = score_turns(scan(args.projects, args.include_tmp), args.level)
    report([t for t in turns if t["decisions"] is not None], args.level,
           [t for t in turns if t["decisions"] is None])
    if args.sample:
        sample([t for t in turns if t["decisions"] is not None],
               args.sample, args.seed, args.sample_out)


if __name__ == "__main__":
    main()
