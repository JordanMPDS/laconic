#!/usr/bin/env python3
"""The mechanical version of v2's whole-sentence rule, and why it is not used.

Kept as a committed negative result rather than deleted, the way
`lexical_probe.py` is. criterion-v2.md decides the mixed-closing seam by
defining the deletion unit as one complete sentence or more. The obvious cheap
way to get that for free is to apply it to detector v1's verdicts, which are
already stored with the quote v1 found: keep a `true` only when the quote begins
and ends at a sentence boundary in the response. No new calls, no re-label.

IT COSTS PRECISION ON BOTH BATCHES, which is the opposite of the intended
effect:

    batch 1        v1 as published      74.2% precision, 88.5% recall
                   v1 + sentence unit   66.7% precision, 38.5% recall
    batch 2 (OOS)  v1 as published      55.3% precision, 84.0% recall
                   v1 + sentence unit   44.4% precision, 32.0% recall

The filter rejects true positives, not false ones. v1's quote is often a
fragment of the restating passage or a light paraphrase of it, so "does this
string start and end a sentence" measures how v1 quotes rather than what the
passage is. 13 of batch 1's 23 true positives and 13 of batch 2's 21 are
discarded this way, against 3 and 7 false positives.

So the whole-sentence rule has to live in the criterion, where the labeller and
the detector both apply it to the response itself. That is what criterion-v2.md
does, and it is why v2 needs a re-label rather than a post-filter.

    python3 sentence_unit_probe.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

BATCHES = [("batch 1", HERE), ("batch 2 (OOS)", HERE.parent / "restatement-b2")]

# A quote that has been stripped of its bullet, number or bold marker still
# starts a sentence; one that has not been stripped of them never matches the
# body, because the body carries them too.
LEAD = re.compile(r"^(?:[-*+>#]+\s*|\d+[.)]\s*|\*\*)+")
END = re.compile(r"[.!?:][\"')\]*`]*$")
TRAIL_CLOSERS = re.compile(r"[\"')\]*`]+$")


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def whole_sentence(quote, body):
    """True when the quote starts a sentence and ends one, inside the body."""
    q = LEAD.sub("", norm(quote)).strip()
    if not q or not END.search(q):
        return False
    b = norm(body)
    i = b.find(q)
    if i < 0:  # paraphrased rather than quoted: the unit cannot be verified
        return False
    if i == 0:
        return True
    return bool(re.search(r"[.!?:]$", TRAIL_CLOSERS.sub("", b[:i].rstrip())))


def text_of(k):
    for sub in ("evals/snapshots/loop", "evals/snapshots"):
        p = ROOT / sub / ("%s.json" % k["snap"])
        if p.exists():
            d = json.loads(p.read_text())
            hit = [r for r in d["runs"]
                   if r["case"] == k["case"] and r["rep"] == k["rep"]
                   and r["arm"] == "laconic" and r["model"] == k["model"]]
            if hit:
                return hit[0]["text"]
    return ""


def confusion(ids, lab, pred):
    tp = fp = fn = tn = 0
    for i in ids:
        p, t = pred[i], lab[i]
        tp += p and t
        fp += p and not t
        fn += (not p) and t
        tn += (not p) and (not t)
    return tp, fp, fn, tn


def show(tag, tp, fp, fn, tn):
    prec = 100.0 * tp / (tp + fp) if tp + fp else float("nan")
    rec = 100.0 * tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
    print("    %-22s TP %2d FP %2d FN %2d TN %2d  precision %5.1f%%  "
          "recall %5.1f%%  F1 %5.1f%%"
          % (tag, tp, fp, fn, tn, prec, rec, f1))


def main():
    for name, d in BATCHES:
        key = {k["id"]: k for k in json.loads((d / "key.json").read_text())}
        lab = json.loads((d / "labels.json").read_text())["labels"]
        ver = json.loads((d / "verdicts.json").read_text())["verdicts"]
        seen, keep = set(), []
        for i in key:
            if i not in ver or i not in lab:
                continue
            t = norm(text_of(key[i]))
            if t in seen:  # the -v2/-v3/-v4 baselines are supersets
                continue
            seen.add(t)
            keep.append(i)
        raw = {i: ver[i]["restates"] for i in keep}
        filt = {i: (ver[i]["restates"]
                    and whole_sentence(ver[i].get("quote", ""), text_of(key[i])))
                for i in keep}
        print("%s  n=%d" % (name, len(keep)))
        show("v1 as published", *confusion(keep, lab, raw))
        show("v1 + sentence unit", *confusion(keep, lab, filt))


if __name__ == "__main__":
    sys.exit(main())
