#!/usr/bin/env python3
"""Telegraphic-fragment detector for #11. Deterministic, offline, stdlib only.

A fragment is a prose segment with no finite verb - see criterion.md. English
has no closed class of finite verbs, so "has a finite verb" is decided against a
lexicon of base forms, inflected here rather than stored inflected.

Participles are deliberately not evidence. "Waiting queue growing linearly" and
"Connections held for long periods" are exactly the shapes the rule forbids, and
an -ing or -ed form with no auxiliary in front of it is what makes them
fragments. Irregular past tenses are evidence, because they are finite.

This lives under evals/results/ and not in evals/bench/metrics.py on purpose.
It was measured before it was placed: fragments.md reports 15 fragments in 3,810
segments, and no separation between the arm instructed to write telegraphically
and the arm instructed not to. A detector with nothing to detect does not belong
in the module the gate reads.

    python3 evals/results/loop/fragments/detector.py            # self-check
    python3 evals/results/loop/fragments/detector.py SNAPSHOT   # per-arm counts
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "evals" / "bench"))
import metrics  # noqa: E402  - path set above

# Base forms only. Inflection is generated in _forms(), so adding a verb is one
# word rather than five, and the -ing form is never generated.
BASE = """
abort absorb accept access accommodate accomplish account accumulate achieve
acknowledge acquire act activate adapt add address adjust admit adopt advance
advise affect afford aggregate agree aim alert align allocate allow alter amend
amount analyze annotate announce answer anticipate appear append apply
approach approve archive argue arise arrange arrive ask assemble assert assess
assign assist associate assume assure attach attack attempt attend attribute
audit authenticate authorize automate avoid await back backfill balance ban
base batch bear beat become begin behave believe belong benchmark benefit bind
bite block blow board boil boost borrow bother bound branch break breach bring
broadcast browse budget build bump bundle burn burst bury buy bypass cache
calculate call cancel capture care carry cascade cast catch cause cease chain
change charge chase check choose chunk claim clarify clash clean clear click
climb clone close cluster coalesce code coerce collapse collect collide combine
come comment commit communicate compare compensate compile complete complicate
comply compose compress compute conceal concern conclude condition configure
confirm conflict conform confuse connect consider consist constrain construct
consume contain continue contract contribute control convert convey convince
cooperate coordinate copy correct correlate cost count couple cover crash
create cross crush cut cycle damage deal debug decide declare decline decode
decouple decrease decrypt dedupe deduplicate default defer define degrade
delay delegate delete deliver demand demonstrate deny depend deploy deprecate
derive descend describe deserialize deserve design destroy detect determine
develop deviate diagnose differ dig disable disagree disallow discard
disconnect discover discuss dismiss dispatch display dispose distinguish
distribute dive diverge divide document dominate double doubt download drain
draw drift drive drop drown dump duplicate earn ease echo edit educate effect
elect elevate eliminate embed emerge emit employ empty enable enclose encode
encounter encourage encrypt end endure enforce engage enhance enjoy enlarge
enqueue ensure enter entail equal escalate escape establish estimate evaluate
evict evolve exceed exchange exclude excuse execute exercise exhaust exist
exit expand expect expire explain explode exploit explore export expose express
extend extract fail fall fan favor fear feed feel fetch fight figure fill
filter finalize find finish fire fit fix flag flatten flip float flow flush
fly focus fold follow force forget fork form format forward fragment free
freeze fulfill function gain gate gather generate get give glue go govern grab
grant graph greet grow guarantee guard guess guide halt hand handle hang happen
harden harm hash hate have head heal hear help hide highlight hint hire hit
hold hook hope host hurt identify idle ignore illustrate imagine implement
imply import impose improve include incorporate increase incur indicate infer
influence inform inherit inject inline input insert insist inspect install
instantiate instruct integrate intend interact intercept interfere interpret
interrupt intersect introduce invalidate invert invest investigate invoke
involve isolate issue iterate join judge jump justify keep kick kill know
label lack land last latch launch layer lead leak lean learn leave lend
lengthen let level leverage lie lift like limit link list listen live load
locate lock log look loop lose love lower maintain make manage manifest map
mark mask match matter max mean measure meet melt mention merge migrate mind
minimize mirror miss mitigate mix model modify monitor mount move multiply
mutate name narrow navigate need neglect negotiate nest normalize note notice
notify nudge number observe obtain occupy occur offer offset omit open operate
oppose optimize order organize orient originate outlive output overflow
overlap override overrun oversee overwrite own pack pad page paginate paint
pair parse participate partition pass patch pause pay peek perform permit
persist pertain pick pin ping pipe pivot place plan play please plug point
poll pop populate port pose position possess post postpone pour power practice
precede predict prefer prepare prepend present preserve press presume prevent
print prioritize probe proceed process produce program progress prohibit
project promise promote prompt propagate propose protect prove provide
provision publish pull purge push put qualify query queue quit quote race
raise rank rate reach react read realize rearrange reason reassign rebalance
reboot rebuild recall receive recognize recommend reconcile record recover
recreate recur recurse redeploy redirect reduce refactor refer reference
reflect refresh refuse regard regenerate register regress regret reindex
reinstall reject relate relax relay release relieve reload rely remain remedy
remember remind remove rename render renew reorder repair repeat replace
replay replicate reply report represent request require rerun rescue research
reseed reserve reset reshape reside resolve resort respect respond restart
restore restrict result resume retain rethink retire retrieve retry return
reuse reveal revert review revise revoke reward rewrite rise risk roll rotate
round route run rush safeguard sample satisfy save say scale scan schedule
scope score scrape scratch screen scroll seal search seat secure see seed seek
seem segment select sell send separate sequence serialize serve set settle
shape shard share shed shift ship shorten show shrink shut sidestep sign
signal simplify simulate sit skew skip slash sleep slice slide slow smooth
snapshot solve sort sound source span spawn speak specify speed spend spike
spin split spread spring stack stage stall stand start starve state stay steal
stem step stick stop store straddle stream strengthen stress stretch
strike string strip struggle study submit subscribe substitute subtract
succeed suffer suffice suggest suit sum summarize supersede supply support
suppose suppress surface surround survive suspect suspend sustain swallow swap
sweep switch symlink sync synchronize tackle tag tail take talk target teach
tear tell tend terminate test thank think thrash threaten throttle throw tie
tighten time toggle tolerate top touch trace track trade trail train transfer
transform transition translate transmit trap travel traverse treat trigger
trim trip trust try tune turn tweak type unblock uncover undergo underlie
understand undo unify uninstall unite unlink unlock unpack unset unstage
unwind update upgrade upload use validate value vanish vary verify version
view violate visit voice vote wait wake walk want warm warn wash waste watch
weaken wear weigh welcome widen win wipe wire wish withdraw witness wonder
work worry wrap write yield zero
""".split()

# Finite past tenses no suffix rule produces.
IRREGULAR = """
became began bent bit bled blew bought broke brought built burnt came caught
chose cost crept cut dealt did drank drew drove ate fed fell felt fled flew
forgot fought found froze gave got grew had heard held hid hit kept knew laid lay led
left lent let lost made meant met paid put quit rang ran rose said sang sank sat
saw sold sought sent set shone shook shot shut slept slid spent spoke sped spun
stole stood struck stuck swam swept taught tore thought threw told took
understood upheld withdrew woke wore won wrote
""".split()

# A contraction of a finite verb is a finite verb. metrics.AUX carries the
# negated forms ("isn't") but not these, because it is a rate denominator there
# and a presence test here.
CONTRACTION = {
    "it's", "that's", "there's", "here's", "what's", "who's", "he's", "she's",
    "let's", "i'm", "we're", "you're", "they're", "i've", "we've", "you've",
    "they've", "i'll", "we'll", "you'll", "they'll", "it'll", "i'd", "we'd",
    "you'd", "they'd", "he'd", "she'd", "it'd", "there're",
}


def _forms():
    out = set(BASE) | set(IRREGULAR) | set(CONTRACTION) | set(metrics.AUX)
    for b in BASE:
        out.add(b + "s")
        if b.endswith(("s", "sh", "ch", "x", "z", "o")):
            out.add(b + "es")
        if b.endswith("y") and len(b) > 1 and b[-2] not in "aeiou":
            out.add(b[:-1] + "ies")
            out.add(b[:-1] + "ied")
        out.add(b + "d" if b.endswith("e") else b + "ed")
    return out


VERBS = _forms()

HEADING = re.compile(r"^\s*#")
TABLE = re.compile(r"^\s*\|")
QUOTE = re.compile(r"^\s*>")
MARKER = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
# "1." inside a line is a list number, not a sentence boundary. metrics.py masks
# e.g./i.e. for the same reason and the same way.
NUM_DOT = re.compile(r"(?<=\d)\.(?=\s)")
BOLD_ONLY = re.compile(r"^\s*\*\*.*\*\*[\s.:]*$")
# criterion.md's third and fourth exclusions, as one test. A segment that opens
# with a dash is a definition gloss; one that opens with anything else that is
# not a letter, a digit, a bracket or a bold marker is what code stripping left
# behind.
PROSE_START = re.compile(r"^[A-Za-z0-9(\[]|^\*\*")
MIN_WORDS = 4


def _sentences(chunk):
    masked = metrics.ABBREV_DOT.sub(
        lambda m: m.group(0).replace(".", "\x00"), chunk)
    masked = NUM_DOT.sub("\x00", masked)
    for s in metrics.SENTENCE_SPLIT.split(masked):
        s = s.replace("\x00", ".").strip()
        if s:
            yield s


def segments(text):
    """Every prose segment: one sentence, or one bullet or numbered item."""
    prose, _ = metrics.split_text(text)
    out, para = [], []

    def flush():
        if para:
            out.extend(_sentences(" ".join(para)))
            del para[:]

    for line in prose.splitlines():
        if not line.strip():
            flush()
            continue
        if HEADING.match(line) or TABLE.match(line) or QUOTE.match(line):
            flush()
            continue
        m = MARKER.match(line)
        if m:
            flush()
            out.extend(_sentences(line[m.end():].strip()))
            continue
        para.append(line.strip())
    flush()
    return out


def candidates(text):
    """The segments the criterion admits, each with its words."""
    for s in segments(text):
        t = s.rstrip()
        if t.endswith(":") or BOLD_ONLY.match(t) or not PROSE_START.match(t):
            continue
        words = metrics.WORD.findall(s)
        if len(words) < MIN_WORDS:
            continue
        yield s, words


def fragments(text):
    """Every admitted segment carrying no finite verb."""
    return [s for s, words in candidates(text)
            if not any(w.lower() in VERBS for w in words)]


def _self_check():
    """Every case is a segment from evals/snapshots/results.json, or a
    minimal edit of one. Nothing here is invented to make a rule look good."""
    def check(name, cond):
        print(("PASS  " if cond else "FAIL  ") + name)
        assert cond, name

    fires = "Monitoring/alerting for tokens still using old key"
    check("a verbless bullet is a fragment", fragments("- " + fires) == [fires])
    check("a participle is not a finite verb",
          fragments("- Not handling exceptions properly (leaking the connection)")
          == ["Not handling exceptions properly (leaking the connection)"])
    check("an elliptical answer is a fragment (criterion.md)",
          fragments("UUID — specifically UUIDv7 (or ULID), not a random v4.")
          == ["UUID — specifically UUIDv7 (or ULID), not a random v4."])

    check("an irregular past tense is a finite verb",
          fragments("The refresh threw on the second attempt.") == [])
    check("a bare present verb is finite",
          fragments("UUIDs generate independently on each node.") == [])
    check("an -s form is finite",
          fragments("This module only reacts to a 401 from the endpoint.") == [])
    check("a contraction is a finite verb",
          fragments("It's the modern equivalent of that command.") == [])
    check("an imperative is not a fragment",
          fragments("Flip signing to the new key.") == [])

    check("a fenced block is not prose",
          fragments("It works.\n\n```\nMonitoring/alerting for old tokens\n```\n")
          == [])
    check("a verbatim error string in a fence is not prose",
          fragments("```\nError: pool exhausted, 20 of 20 checked out\n```") == [])
    check("an inline code span is stripped, not read",
          fragments("Run `find . -type f -size +100M` next.") == [])
    check("a path in prose does not break the sentence",
          fragments("auth.js is self-contained at 41 lines.") == [])
    check("a heading is not a fragment",
          fragments("## Normal path for the refresh flow") == [])
    check("a bold label is not a fragment",
          fragments("**Normal path in the token module**") == [])
    check("a list lead-in is not a fragment",
          fragments("Two options for the signing key:") == [])
    check("a definition gloss is not a fragment",
          fragments("- `-type f` — only regular files, excluding directories")
          == [])
    check("a table row is not a fragment",
          fragments("| lite | no closing offer at all |") == [])
    check("a blockquote is not a fragment",
          fragments("> Monitoring/alerting for tokens still using old key") == [])
    check("a code-stripping residue is skipped",
          fragments("- `test_a`: `12.50` — off by a cent") == [])
    check("a segment under four prose words is skipped",
          fragments("Two options here.") == [])

    check("a hard-wrapped sentence is one segment, not two",
          fragments("The refresh call collapses concurrent requests\n"
                    "into a single network round trip.") == [])
    check("a numbered item does not split at its number",
          fragments("1. Generate the new signing key first.") == [])
    check("e.g. does not split a sentence",
          fragments("Short tokens, e.g. 15 minutes, keep the window small.") == [])

    # The measured limitation, asserted so it cannot be "fixed" silently. Both
    # of these are real fragments the detector misses, because the head noun of
    # a telegraphic fragment in this domain is usually a verb homograph:
    # BASE carries `use`, `queue` and `race` as verbs, so their noun uses count
    # as finite. Removing them buys these back and costs every sentence that
    # uses them as verbs - fragments.md measures the trade both ways.
    check("known false negative: 'in use' reads as a verb",
          fragments("All 20 connections in use at every checkpoint") == [])
    check("known false negative: 'queue' reads as a verb",
          fragments("- Waiting queue growing linearly over the hour") == [])
    print("\nall checks passed")


def _report(path):
    import collections
    runs = json.load(open(path))["runs"]
    hits = collections.Counter()
    total = collections.Counter()
    found = collections.defaultdict(list)
    for r in runs:
        text = r.get("text", "")
        total[r["arm"]] += sum(1 for _ in candidates(text))
        for s in fragments(text):
            hits[r["arm"]] += 1
            found[r["arm"]].append({"case": r["case"], "model": r["model"],
                                    "segment": s})
    print("%-17s %7s %9s %8s" % ("arm", "flagged", "segments", "rate"))
    for arm in sorted(total):
        print("%-17s %7d %9d %7.2f%%"
              % (arm, hits[arm], total[arm], 100 * hits[arm] / total[arm]))
    return found


if __name__ == "__main__":
    if len(sys.argv) > 1:
        found = _report(sys.argv[1])
        if os.environ.get("DUMP"):
            json.dump(found, sys.stdout, indent=1, sort_keys=True)
    else:
        _self_check()
