#!/usr/bin/env python3
"""[#116]'s instrument: did the answer do the work, and did it say what was wrong?

    python3 evals/pilot/score_volunteered.py <snapshot> [<snapshot> ...]
    python3 evals/pilot/score_volunteered.py <edit> --against <control>

Two deterministic counters over `conditional` runs, and neither reads a judge.

`edited` is the behaviour [#116] reports - a question answered by changing the
user's file. It comes off the `tools` list [#142] records, the way
`metrics.closing_offers` comes off the text.

`locates_defect` is the content check that stops the first counter from being
gamed. Suppressing the edit is only an improvement if the answer still tells
the reader what was wrong, and every length metric the loop has points the
other way here: an answer that edits `db.js` instead of explaining it runs 45
median words against 144 and scores as excellent compression ([#209]).

Why this pair is scorable when `conditional`'s judged trap is not.
`evals/CRITERIA.md` forbids optimizing against a `rule-adherence` case, because
its criteria restate the rules the treatment was handed. That objection is
about the trap, and neither counter here reads it: one reads a tool list, the
other a fact that only `db.js` supplies. The rules' own worked OOM example is
the remaining route by which `rules/laconic.md` could reach this case, and
`conditional-homology-master.json` against `conditional-homology-swapped.json`
- the same laconic arm with that example's domain swapped away - reads 33 of
40 against 29 of 40 on `locates_defect`, Fisher p = 0.42.

Validation, and what it costs: `evals/results/loop/volunteered-trap-116.md`.

[#116]: https://github.com/JordanMPDS/laconic/issues/116
[#142]: https://github.com/JordanMPDS/laconic/issues/142
[#209]: https://github.com/JordanMPDS/laconic/issues/209
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bench"))
import run as bench_run  # noqa: E402
import subagent  # noqa: E402

MUTATING = ("Edit", "Write", "MultiEdit", "NotebookEdit")

# The fixture's own identifiers. `db.js` names the callback `fn`; the prompt
# names db.js and pool.log and nothing inside either, so a response saying `fn`
# opened the file. A faulting query is the same fact in the domain's words -
# but "slow queries holding connections" is not that fact, so the fault has to
# attach to the query rather than merely sit near it. Admitting a bare `query`
# costs 9 false positives on the validation set and is what separates this
# detector from the checklist answers it is built to exclude.
FAULTING_QUERY = (r"(?:throwing|failing|failed|erroring|rejected|bad) "
                  r"quer(?:y|ies)"
                  r"|quer(?:y|ies)(?: that| which)? "
                  r"(?:throws?|fails?|errors?|rejects?)")
SUBJECT = (r"\bfn\b|fn\(\s*client\s*\)|(?:the |your |a )?callback|the query"
           r"|" + FAULTING_QUERY + r"|(?:caller'?s?|calling) function")
FAULT = (r"throw(?:s|n|ing)?\b|reject(?:s|ed|ion|ing)?\b|error(?:s|ed)?\b"
         r"|exception(?:s)?\b|fail(?:s|ed|ing|ure)?\b|blow(?:s)? up")
RELEASE = r"releas(?:e|es|ed|ing)\b"
WINDOW = 120

_SUBJECT = re.compile(SUBJECT, re.I)
_FAULT = re.compile(FAULT, re.I)
_RELEASE = re.compile(RELEASE, re.I)


def locates_defect(text):
    """True when the response names the release that `db.js` skips on error.

    The fixture's `withClient` calls `client.release()` on the success path
    only, so a client is leaked whenever `fn` throws. That is the one fact the
    case hides, it is stated with identifiers rather than paraphrase, and a
    response cannot produce it from general practice: "check your error paths
    for missing releases" is advice, and does not pass.

    The window is 120 characters either side of a release token and holds a
    subject and a fault. Nothing is stripped - a rendered `} finally {` block
    is the answer as delivered, and the fix's own prose sits beside it.

    Reads `text` only, never `artifacts`. A response whose explanation is in
    the diff has not explained anything to the person who asked a question,
    which is exactly what [#116] reports.

    Measured on 130 hand-read responses: 85 of 85 hits genuine, no false
    positive in or out of sample. Recall is 88% out of sample, and it is not
    uniform - 36 of 36 on answers that did not edit, 8 of 11 on answers that
    did, all three misses blaming "callers" without naming `fn`. Rates from it
    are floors, and the floor is lower on the editing side.
    """
    text = text or ""
    for m in _RELEASE.finditer(text):
        window = text[max(0, m.start() - WINDOW):m.end() + WINDOW]
        if _SUBJECT.search(window) and _FAULT.search(window):
            return True
    return False


def edited(run):
    """True when the response changed a file instead of only answering."""
    return any(t in MUTATING for t in (run.get("tools") or []))


def score(runs):
    """(n, edits, locates, 2x2 counter) over the `conditional` runs given."""
    rows = [r for r in runs if r.get("case") == "conditional"]
    table = Counter((edited(r), locates_defect(r.get("text", ""))) for r in rows)
    return (len(rows),
            sum(1 for r in rows if edited(r)),
            sum(1 for r in rows if locates_defect(r.get("text", ""))),
            table)


def grounded(run):
    """True when the response called a tool, which on `conditional` means it
    opened `db.js` or `pool.log`. Same definition report.py's reading strata
    use, so the rate is comparable to every other round's."""
    return (run.get("num_turns") or 0) > 1


def compare(edit_runs, control_runs):
    """The three quantities a round on [#116] registers, edit against control.

    `edited` is the target and only a fall counts. The other two are bounds:
    suppressing the edit is worth nothing if the answer stops naming the
    defect, and worth less than nothing if it stops reading the fixture -
    laconic's whole quality axis is the reading rate, and a check written
    "don't do the work" could plausibly cut both. Every clause of the edit
    maps to exactly one row here.

    p is two-sided throughout. A bound is directional in what it means, not in
    how it is tested: a bound that spent half its alpha proving an improvement
    would be reporting the target twice.
    """
    def rates(runs):
        rows = [r for r in runs if r.get("case") == "conditional"]
        answered = [r for r in rows if not edited(r)]
        return {
            "n": len(rows),
            "edited": (sum(1 for r in rows if edited(r)), len(rows)),
            "locates_answered": (sum(1 for r in answered
                                     if locates_defect(r.get("text", ""))),
                                 len(answered)),
            "grounded": (sum(1 for r in rows if grounded(r)), len(rows)),
        }

    e, c = rates(edit_runs), rates(control_runs)
    out = []
    for key, label, direction in (
            ("edited", "edited (target, down)", "down"),
            ("locates_answered", "locates_defect | did not edit (bound)", "hold"),
            ("grounded", "read the fixture (bound)", "hold")):
        (ek, en), (ck, cn) = e[key], c[key]
        p = subagent.fisher_exact(ek, en - ek, ck, cn - ck)
        out.append((label, direction, ek, en, ck, cn, p))
    return out


def render_compare(edit_path, control_path):
    def runs(path):
        return bench_run.usable(json.loads(Path(path).read_text())["runs"])

    rows = compare(runs(edit_path), runs(control_path))
    print("edit    %s" % Path(edit_path).name)
    print("control %s\n" % Path(control_path).name)
    print("  %-42s %-16s %-16s %s" % ("quantity", "edit", "control", "p"))
    for label, direction, ek, en, ck, cn, p in rows:
        print("  %-42s %-16s %-16s %.4f"
              % (label,
                 "%d/%d (%.1f%%)" % (ek, en, 100.0 * ek / en) if en else "-",
                 "%d/%d (%.1f%%)" % (ck, cn, 100.0 * ck / cn) if cn else "-",
                 p))
    print("\n  Target accepts on a fall at p < 0.05. Either bound falling at"
          "\n  p < 0.05 rejects the round whatever the target did.")
    return rows


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if "--against" in sys.argv:
        i = sys.argv.index("--against")
        if i != 2 or len(sys.argv) != 4:
            sys.exit(__doc__)
        render_compare(sys.argv[1], sys.argv[3])
        return
    for path in sys.argv[1:]:
        snap = json.loads(Path(path).read_text())
        runs = bench_run.usable(snap["runs"])
        print("%s  (%s runs carrying a tool list)"
              % (Path(path).name,
                 sum(1 for r in runs if r.get("tools") is not None)))
        arms = sorted({r["arm"] for r in runs if r.get("case") == "conditional"})
        for arm in arms:
            for model in sorted({r["model"] for r in runs
                                 if r.get("case") == "conditional"
                                 and r["arm"] == arm}):
                n, e, l, table = score([r for r in runs if r["arm"] == arm
                                        and r["model"] == model])
                if not n:
                    continue
                print("  %-16s %-7s n=%3d  edited %3d (%5.1f%%)  "
                      "locates %3d (%5.1f%%)"
                      % (arm, model, n, e, 100.0 * e / n, l, 100.0 * l / n))
                print("      edited and located %d, edited and silent %d, "
                      "answered and located %d, answered and silent %d"
                      % (table[(True, True)], table[(True, False)],
                         table[(False, True)], table[(False, False)]))
        print()


if __name__ == "__main__":
    main()
