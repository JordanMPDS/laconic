"""The stdlib lexical detector for #150, and the evidence that it does not work.

Kept as a committed negative result rather than deleted. The obvious cheap
instrument for "a claim made twice" is lexical: split the response into units,
drop stopwords, and flag a unit whose content words are largely contained in an
earlier one. Containment rather than Jaccard, because a short recap contained in
a long earlier paragraph is exactly the shape being hunted.

IT DOES NOT SEPARATE THE HARM. Run against round 21's longest
verdict-experiment/sonnet response - which closes with "If I were fixing this,
the highest-leverage changes are:" and then restates four of its own numbered
findings - that recap scores 0.21, while the longest walkthrough/sonnet
response, which is dense and repeats nothing, tops out at 0.40 on a passage
that CONTRASTS two kinds of 401 rather than repeating either.

So the ranking is inverted: the dense response scores higher than the redundant
one. The reason is that restatement is semantic - a recap re-asserts the
substance of earlier findings in fresh words - while lexical overlap is
dominated by shared technical vocabulary, which recurs most in the responses
that are working hardest.

This is why the detector for #150 has to be judged rather than computed, unlike
asks_back, which is a regex and costs nothing to re-score across the archive.
"""
import json, re, sys, statistics
from pathlib import Path

STOP = set("""a an the and or but if then than that this these those of in on at to for with
from by as is are was were be been being it its it's has have had do does did not no so such
you your we our they their he she i me my them us can could should would will shall may might
must about into over under out up down off again more most some any each other another both
either neither there here when where which who whom what how why all only just also very
because while during before after between within without across per via which's one two""".split())

def units(text):
    """Sentence-ish units, minus code blocks - code repeats legitimately."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    parts = re.split(r"(?<=[.!?:])\s+|\n(?=[-*\d#])|\n\n", text)
    return [p.strip() for p in parts if len(p.strip()) > 40]

def bag(u):
    return {w for w in re.findall(r"[a-z][a-z'-]{2,}", u.lower()) if w not in STOP}

def score(text, thresh=0.65, minwords=5):
    us = units(text)
    bags = [bag(u) for u in us]
    hits = []
    for i in range(1, len(us)):
        b = bags[i]
        if len(b) < minwords:
            continue
        best, j = 0.0, None
        for k in range(i):
            if not bags[k]:
                continue
            c = len(b & bags[k]) / len(b)          # containment in an EARLIER unit
            if c > best:
                best, j = c, k
        if best >= thresh:
            hits.append((i, j, best, us[i][:110]))
    return us, hits

if __name__ == "__main__":
    d = json.loads(Path('/home/jordan/projects/laconic/evals/snapshots/loop/round-21.json').read_text())
    for case, model, pick in (("verdict-experiment", "sonnet", "max"),
                              ("walkthrough", "sonnet", "max")):
        rs = [r for r in d["runs"] if r["arm"] == "laconic" and r["case"] == case
              and r["model"] == model and r.get("ok")]
        rs.sort(key=lambda r: -r["output_tokens"])
        r = rs[0]
        us, hits = score(r["text"])
        print("=== %s/%s  %d tokens  %d units  %d flagged ===" %
              (case, model, r["output_tokens"], len(us), len(hits)))
        for i, j, c, t in hits:
            print("   unit %2d restates %2d at %.2f: %s" % (i, j, c, t))
        print()
