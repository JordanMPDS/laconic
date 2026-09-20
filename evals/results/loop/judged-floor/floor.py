"""The judged floor: the shortest response the suite's own trap has passed.

    python3 evals/results/loop/judged-floor/floor.py
    python3 evals/results/loop/judged-floor/floor.py --demo

Every `expect.json` trap is a **floor** - it names what a correct answer must
contain, and a longer answer passes it too. So no case in this repository has
ever carried a *ceiling*, and three issues want one: [#136] asks for a detector
that flags an over-long answer to a closed question, [#150] and [#305] ask what
part of a long answer was surplus. A ceiling needs a number this repository has
never computed: **how short a passing answer can be.**

That number does not need a labeller and does not need a generation. It is in
the archive already - 21,976 blind trap verdicts joined to the responses that
earned them - and this script reads it out.

**The join is per case and per trap version, not per snapshot.** `judge.py`
stamps each judgments file with `criteria_cksum`, a hash over *every* case's
trap at once, so a correction to one case's trap invalidates the label on all
of them. Two traps have been corrected against the software they describe and
both moved verdicts (`evals/CRITERIA.md`), so the version cannot be ignored -
but the aggregate hash is far too blunt to obey. This script walks the git
history of `evals/cases/`, recomputes the aggregate hash at each commit, and
recovers which trap text *each case* had under each hash. A verdict counts when
the trap for its own case is byte-identical to today's. That recovers 21,976
verdicts where the aggregate hash alone admits 3,788.

**A floor is a minimum over a sample, so it is reported three ways.** The
shortest passing response is one draw of an unstable judge: `judge-self-
disagreement.md` measures 0% to 27% of verdicts moving on a re-run. So `strict`
counts a text only if it passed *every* time it was judged, `any` counts it if
it passed once, and `k=3` is the third-shortest text, which one judge error
cannot set. The shortest passing response per case is also hand-read, in
`floor-labels.json`, because a judge false-pass would otherwise set the floor
for free.

[#136]: https://github.com/JordanMPDS/laconic/issues/136
[#150]: https://github.com/JordanMPDS/laconic/issues/150
[#305]: https://github.com/JordanMPDS/laconic/issues/305
"""
import collections
import glob
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evals", "bench"))
import metrics  # noqa: E402

CASES = os.path.join(ROOT, "evals", "cases")
SNAPSHOTS = os.path.join(ROOT, "evals", "snapshots")
LABELS = os.path.join(HERE, "floor-labels.json")
CLOSED_LABELS = os.path.join(HERE, "..", "closed-question", "labels.json")

# The four families that ask the same closed question about the same three
# fixtures. `confirm-*` asks it cold; the other three ask it after the model's
# own prior turns, which is why their floors are not the same number.
CLOSED = ("confirm", "recall", "deep", "wide")
STEMS = ("index", "metric", "rollback")

# `<name>-judgments.json` grades `<name>.json`. Three historical variants carry
# a suffix after `judgments` - `round-01-judgments-v2`, `round-12-judgments-b`,
# `round-01-n10-v4-judgments-traps2` - and a matcher anchored on
# `-judgments.json` alone drops all of them.
JUDGMENTS_SUFFIX = re.compile(r"-judgments(-[a-z0-9]+)?\.json$")


def words(text):
    """`metrics.score`'s own count: fenced blocks, inline code and URLs out.

    The same count every other detector in this repository uses. These
    responses carry SQL, and charging a response for a `CREATE INDEX` statement
    would charge it for content `rules/laconic.md` protects verbatim.
    """
    return metrics.score(text)["words"]


def aggregate_cksum(traps):
    """`judge.criteria_cksum`'s hash, recomputed from a `{case: trap}` mapping."""
    return str(zlib.crc32(json.dumps(traps, sort_keys=True).encode()))


def traps_at(rev):
    """Every case's trap text as of one revision."""
    listing = subprocess.run(
        ["git", "-C", ROOT, "ls-tree", "-r", "--name-only", rev, "evals/cases/"],
        capture_output=True, text=True, check=True).stdout.split()
    out = {}
    for path in listing:
        if not path.endswith("/expect.json"):
            continue
        blob = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)],
                              capture_output=True, text=True, check=True).stdout
        out[path.split("/")[2]] = json.loads(blob).get("trap", "")
    return out


def trap_history():
    """Map each aggregate `criteria_cksum` in history to per-case trap hashes.

    Returns `(history, today)`. A verdict on case C recorded under cksum K is
    usable when `history[K][C] == today[C]`.
    """
    revs = subprocess.run(
        ["git", "-C", ROOT, "log", "--format=%H", "--", "evals/cases"],
        capture_output=True, text=True, check=True).stdout.split()
    history = {}
    for rev in revs:
        traps = traps_at(rev)
        history.setdefault(aggregate_cksum(traps),
                           {c: zlib.crc32(t.encode()) for c, t in traps.items()})
    today = {}
    for name in sorted(os.listdir(CASES)):
        path = os.path.join(CASES, name, "expect.json")
        if os.path.isfile(path):
            today[name] = json.load(open(path)).get("trap", "")
    live = aggregate_cksum(today)
    today = {c: zlib.crc32(t.encode()) for c, t in today.items()}
    history[live] = today
    return history, today


def results_name(judgments_path):
    """The results file a judgments file grades, whether or not it exists.

    Two naming families, because the oldest pair predates the suffix
    convention: `judgments.json` grades `results.json` and
    `judgments-2026-07-31.json` grades `results-2026-07-31.json`, while
    everything since is `<name>-judgments.json` over `<name>.json`.
    """
    directory, base = os.path.split(judgments_path)
    if base.startswith("judgments"):
        return os.path.join(directory, base.replace("judgments", "results", 1))
    return os.path.join(directory, JUDGMENTS_SUFFIX.sub(".json", base))


def results_path(judgments_path):
    """The results file a judgments file grades, or None if it is not committed.

    Six judgments files have no results file beside them. They graded responses
    that live in another snapshot or were never committed, so the verdicts
    cannot be joined to a word count and are dropped by name.
    """
    candidate = results_name(judgments_path)
    return candidate if os.path.isfile(candidate) else None


def load():
    """Join every usable verdict to the response that earned it.

    Yields `(case, arm, model, sha, words, verdict)` and a drop tally. A
    response judged in several snapshots appears once per verdict, which is what
    lets `strict` see a text that passed once and failed once.
    """
    history, today = trap_history()
    rows, dropped = [], collections.Counter()
    for jpath in sorted(glob.glob(os.path.join(SNAPSHOTS, "**", "*judgments*.json"),
                                  recursive=True)):
        try:
            doc = json.load(open(jpath))
        except Exception:
            continue
        if not isinstance(doc.get("judgments"), list):
            continue
        cksum = str(doc.get("metadata", {}).get("criteria_cksum"))
        if cksum not in history:
            dropped["trap version not in history (%s)" % cksum] += len(doc["judgments"])
            continue
        rpath = results_path(jpath)
        if rpath is None:
            dropped["no results file beside the judgments"] += len(doc["judgments"])
            continue
        texts = {}
        for run in json.load(open(rpath)).get("runs", []):
            if isinstance(run, dict) and run.get("ok") and run.get("text"):
                texts[(run.get("arm"), run.get("case"), run.get("model"),
                       run.get("rep"))] = run["text"]
        for j in doc["judgments"]:
            case = j.get("case")
            if today.get(case) is None or history[cksum].get(case) != today[case]:
                dropped["trap has moved since (%s)" % case] += 1
                continue
            text = texts.get((j.get("arm"), case, j.get("model"), j.get("rep")))
            if text is None:
                dropped["run not in the paired results file"] += 1
                continue
            rows.append((case, j.get("arm"), j.get("model"),
                         hashlib.sha1(text.encode()).hexdigest()[:12],
                         words(text), j.get("verdict"), bool(j.get("carried"))))
    return rows, dropped


def per_text(rows):
    """Collapse to one record per distinct response.

    Snapshots carry arms forward, so the same text appears under several
    verdicts. `passes`/`judged` separates a text that always passed from one
    that passed once.

    **Most of those repeats are copies, not re-draws.** `judge.carry_judgments`
    copies a control arm's verdict forward rather than re-grading it and marks
    the record `carried`, precisely because the judge disagrees with itself on
    identical text. So `fresh_judged` counts only verdicts this file bought,
    and it is the only count from which a re-judge rate may be read.
    """
    out = {}
    for case, arm, model, sha, w, verdict, carried in rows:
        rec = out.setdefault((case, sha), dict(case=case, sha=sha, arm=arm,
                                               model=model, words=w,
                                               passes=0, judged=0,
                                               fresh_passes=0, fresh_judged=0))
        rec["judged"] += 1
        rec["passes"] += 1 if verdict == "pass" else 0
        if not carried:
            rec["fresh_judged"] += 1
            rec["fresh_passes"] += 1 if verdict == "pass" else 0
    return list(out.values())


def floors(texts, k=3):
    """Per case: the strict floor, the generous floor, and the k-th shortest."""
    by_case = collections.defaultdict(list)
    for t in texts:
        by_case[t["case"]].append(t)
    out = {}
    for case, ts in by_case.items():
        strict = sorted((t["words"], t["sha"]) for t in ts
                        if t["passes"] == t["judged"] and t["passes"])
        any_ = sorted((t["words"], t["sha"]) for t in ts if t["passes"])
        allw = sorted(t["words"] for t in ts)
        lac = sorted(t["words"] for t in ts if t["arm"] == "laconic")
        out[case] = dict(
            n=len(ts), passing=len(any_),
            strict=strict[0] if strict else None,
            any=any_[0] if any_ else None,
            kth=strict[k - 1] if len(strict) >= k else None,
            median=statistics.median(allw) if allw else None,
            laconic_median=statistics.median(lac) if lac else None)
    return out


def table(fl):
    print("%-18s %5s %5s %7s %7s %7s %8s %6s"
          % ("case", "n", "pass", "strict", "any", "3rd", "laconic", "ratio"))
    for case in sorted(fl):
        r = fl[case]
        lac = r["laconic_median"]
        strict = r["strict"][0] if r["strict"] else None
        ratio = ("%.1fx" % (lac / strict)) if lac and strict else "-"
        print("%-18s %5d %5d %7s %7s %7s %8s %6s"
              % (case, r["n"], r["passing"],
                 strict if strict is not None else "-",
                 r["any"][0] if r["any"] else "-",
                 r["kth"][0] if r["kth"] else "-",
                 "%.1f" % lac if lac else "-", ratio))


def archive_medians(cases):
    """The laconic median over *every* stored response, not just judged ones.

    The medians beside the floor come from responses that carry a usable
    verdict, which is a fraction of the archive and not a random one. So the
    ratio in that table is internally consistent but is not the figure
    `closed-question-136.md` publishes, which is computed over all 1,953 stored
    responses on the closed cases. Both are printed, because on `deep-*` they
    disagree enough to change the reading.

    De-duplication is `closed-question/sweep.py`'s, deliberately: one `seen` set
    over text hashes across every case and arm, in sorted glob order. A
    per-case set would keep a laconic response whose text a control arm
    produced first, and the two documents would then print different medians for
    the same quantity. This reproduces that table rather than recomputing it.
    """
    seen, by_case = set(), collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(SNAPSHOTS, "**", "*.json"),
                                 recursive=True)):
        try:
            doc = json.load(open(path))
        except Exception:
            continue
        for run in doc.get("runs") or []:
            if not isinstance(run, dict) or not run.get("ok") or not run.get("text"):
                continue
            if run.get("case") not in cases:
                continue
            digest = hashlib.sha1(run["text"].encode()).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            if run.get("arm") == "laconic":
                by_case[run["case"]].append(words(run["text"]))
    return {c: (len(w), statistics.median(w)) for c, w in by_case.items()}


def closed_table(fl):
    """Floors for the four families that ask one question about one fixture.

    Floors only. The medians belong in the table below, which prints both the
    judged-subset one and the whole archive's, because quoting a median beside a
    floor here invited reading the judged figure as the published one.
    """
    print("%-10s" % "stem", end="")
    for fam in CLOSED:
        print(" %10s" % fam, end="")
    print()
    for stem in STEMS:
        print("%-10s" % stem, end="")
        for fam in CLOSED:
            r = fl.get("%s-%s" % (fam, stem))
            print(" %10s" % (r["strict"][0] if r and r["strict"] else "-"), end="")
        print()


def correction_is_the_length(fl):
    """Re-read `closed-question-136.md`'s dominant false-positive class.

    Eleven of that sample's thirty hits were labelled `not a violation` on the
    ground that *"the premise is false, so the answer is a denial plus the
    qualification the trap requires ... Nothing is deletable."* The judged floor
    tests that sentence: if a shorter response passed the same trap, the words
    above it are not the qualification the trap requires.
    """
    if not os.path.isfile(CLOSED_LABELS):
        return []
    labels = json.load(open(CLOSED_LABELS))["labels"]
    out = []
    for lab in labels:
        if lab.get("shape") != "correction-is-the-length":
            continue
        r = fl.get(lab["case"])
        floor = r["strict"][0] if r and r["strict"] else None
        out.append((lab["case"], lab["words"], floor,
                    None if floor is None else lab["words"] - floor))
    return out


def verify_labels(fl):
    """Check the hand-read floor labels still name the response they read.

    A floor set by a judge false-pass is free, so each case's shortest passing
    response is read in full and recorded. If the archive gains a shorter
    passing response later, the label no longer covers the floor and this says
    so rather than reporting a validated number.
    """
    if not os.path.isfile(LABELS):
        return None
    labels = {r["case"]: r for r in json.load(open(LABELS))["labels"]}
    stale, sound, code, unsound = [], [], [], []
    for case, r in sorted(fl.items()):
        if not r["strict"]:
            continue
        sha = r["strict"][1]
        lab = labels.get(case)
        if lab is None or lab["sha"] != sha:
            stale.append(case)
        elif lab["label"] == "sound":
            sound.append(case)
        elif lab["label"] == "sound-code":
            code.append(case)
        else:
            unsound.append((case, lab["label"]))
    return sound, code, unsound, stale


def main():
    rows, dropped = load()
    texts = per_text(rows)
    fl = floors(texts)

    print("## What joined\n")
    print("%d verdicts on %d distinct responses, over %d cases"
          % (len(rows), len(texts), len(fl)))
    print("%d verdicts dropped:" % sum(dropped.values()))
    for reason, n in dropped.most_common():
        print("   %-46s %6d" % (reason[:46], n))

    print("\n## The judged floor, per case\n")
    table(fl)

    print("\n## The closed question, one fixture and four families\n")
    closed_table(fl)

    print("\n## The same floors against the whole archive's laconic median\n")
    closed = ["%s-%s" % (f, s) for f in CLOSED for s in STEMS] + ["quota-merge"]
    arch = archive_medians(set(closed))
    print("%-18s %7s %7s %8s %8s %8s"
          % ("case", "floor", "judged", "ratio", "all", "ratio"))
    for case in sorted(closed):
        r, a = fl.get(case), arch.get(case)
        if not r or not r["strict"] or not a:
            continue
        floor_w = r["strict"][0]
        print("%-18s %7d %7.1f %8.2fx %8.1f %7.2fx"
              % (case, floor_w, r["laconic_median"],
                 r["laconic_median"] / floor_w, a[1], a[1] / floor_w))

    print("\n## What repeats do and do not say about the judge\n")
    repeated = [t for t in texts if t["judged"] > 1]
    unmarked = [t for t in texts if t["fresh_judged"] > 1]
    moved = [t for t in unmarked if 0 < t["fresh_passes"] < t["fresh_judged"]]
    differ = sum(1 for c in fl.values()
                 if c["strict"] and c["any"] and c["strict"] != c["any"])
    print("%d of %d responses carry more than one verdict; %d of those carry "
          "two that are not marked `carried`, and %d of *those* disagree"
          % (len(repeated), len(texts), len(unmarked), len(moved)))
    print("**That is not a re-judge rate and must not be quoted as one.** The "
          "`carried` marker was added to judge.py after the early files were\n"
          "written, so an unmarked repeat may be a copy rather than a second "
          "grading. `judge-self-disagreement.md` measures the real quantity at\n"
          "0% to 27% between cases, by re-running the judge on purpose.")
    print("\nstrict and any name the same response on %d of %d cases, so the "
          "hand read below and the k=3 column are what a false pass has to get "
          "past." % (len(fl) - differ, len(fl)))

    print("\n## `the correction is the length`, re-read against the floor\n")
    hits = correction_is_the_length(fl)
    if hits:
        print("%-18s %7s %7s %8s" % ("case", "words", "floor", "above"))
        for case, w, floor, above in hits:
            print("%-18s %7d %7s %8s" % (case, w, floor, above))
        above = [a for _, _, _, a in hits if a is not None]
        print("\n%d of %d hits sit above a passing response to the same trap, "
              "by %d to %d words (median %.0f)"
              % (sum(1 for a in above if a > 0), len(hits), min(above),
                 max(above), statistics.median(above)))

    print("\n## The hand read of each floor response\n")
    checked = verify_labels(fl)
    if checked is None:
        print("floor-labels.json absent: the floor is unaudited")
    else:
        sound, code, unsound, stale = checked
        print("%d floors read and sound, of which %d are carried by code the "
              "prose count excludes; %d judge errors, %d unlabelled or moved"
              % (len(sound) + len(code), len(code), len(unsound), len(stale)))
        for case in code:
            print("   prose floor understates the response: %s" % case)
        for case, label in unsound:
            print("   judge error, floor not usable: %-18s %s" % (case, label))
        for case in stale:
            print("   unlabelled or moved: %s" % case)
    return 0


def demo():
    """Self-check on the two joins that have silently dropped data before."""
    assert aggregate_cksum({"a": "x"}) == aggregate_cksum({"a": "x"})
    assert aggregate_cksum({"a": "x"}) != aggregate_cksum({"a": "y"})

    # Every naming family that exists under evals/snapshots/. The suffixed
    # variants are the ones a matcher anchored on `-judgments.json` alone drops,
    # and the `judgments.json` pair is the one a suffix rule cannot reach at all.
    for name, want in (
            ("s/design-discrimination-judgments.json", "s/design-discrimination.json"),
            ("s/round-01-judgments-v2.json", "s/round-01.json"),
            ("s/round-12-judgments-b.json", "s/round-12.json"),
            ("s/round-01-n10-v4-judgments-traps2.json", "s/round-01-n10-v4.json"),
            ("s/judgments.json", "s/results.json"),
            ("s/judgments-2026-07-31.json", "s/results-2026-07-31.json")):
        assert results_name(name) == want, (name, results_name(name))

    # strict counts a text only when every verdict on it passed; any counts one.
    rows = [("c", "laconic", "sonnet", "aa", 10, "pass", False),
            ("c", "laconic", "sonnet", "aa", 10, "fail", False),
            ("c", "laconic", "sonnet", "bb", 20, "pass", False),
            ("c", "laconic", "sonnet", "cc", 30, "pass", False),
            ("c", "laconic", "sonnet", "dd", 40, "pass", False)]
    fl = floors(per_text(rows), k=2)["c"]
    assert fl["any"] == (10, "aa"), fl["any"]
    assert fl["strict"] == (20, "bb"), fl["strict"]
    assert fl["kth"] == (30, "cc"), fl["kth"]
    assert fl["passing"] == 4, fl["passing"]

    # A carried verdict is a copy of one already counted, so it may not be read
    # as the judge reproducing itself. Two copies of a pass leave fresh_judged
    # at 1 and cannot make a re-judge rate.
    t = per_text([("c", "laconic", "sonnet", "aa", 10, "pass", False),
                  ("c", "laconic", "sonnet", "aa", 10, "pass", True)])[0]
    assert t["judged"] == 2 and t["fresh_judged"] == 1, t

    # A case with no passing response reports no floor rather than zero.
    fl = floors(per_text([("d", "laconic", "sonnet", "aa", 10, "fail", False)]))["d"]
    assert fl["strict"] is None and fl["any"] is None

    print("floor.py demo ok")
    return 0


if __name__ == "__main__":
    sys.exit(demo() if "--demo" in sys.argv[1:] else main())
