#!/usr/bin/env python3
"""Validates the readability detectors themselves.

If these fail, the metric is broken - not the plugin. A detector that cannot
separate fixture GOOD from fixture BAD measures nothing, and one that fires on
CODE would score correct prose as degraded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals" / "bench"))
import metrics  # noqa: E402

fails = 0


def check(label, cond):
    global fails
    if cond:
        print("ok   %s" % label)
    else:
        print("FAIL %s" % label)
        fails += 1


GOOD = """The deploy failed because the worker ran out of memory. If the usage
sits at a steady ceiling, raise the limit; if it is climbing, you have a leak and
a bigger limit only delays the next kill.

Check these in order:

- run `kubectl top pod` for a few minutes
- compare the peak against the configured limit
- look at the restart count
"""

BAD = """Deploy failed -> worker OOM. Usage steady ceiling -> raise limit.
Usage climbing -> leak, bigger limit just delays next kill.

check kubectl top pod few min. compare peak vs configured limit. check restart
count. impl detail: req handler leaks obj refs, err path never frees.
"""

CODE = """The parser returns an error value rather than raising, so the caller
decides what to do with it.

```rust
impl Parser {
    fn parse(&self) -> Result<Ast, Err> { self.inner() }
}
```

Run `make test -> out.log` to capture the output, and read `impl.rs` for the
detail. The `err` variant is described at https://example.com/docs in section 4.
"""

g = metrics.score(GOOD)
b = metrics.score(BAD)
c = metrics.score(CODE)

check("good prose has no violations", g["violations"] == 0)
check("good prose keeps a normal article rate", g["article_rate"] >= 0.05)
check("good prose aux_verb_rate is non-zero", g["aux_verb_rate"] > 0)
check("good prose bullets do not trip lowercase-start",
      g["sentence_initial_lowercase"] == 0)

check("bad prose is flagged", b["violations"] >= 5)
check("bad prose arrows counted", b["symbol_connectors"] >= 3)
check("bad prose abbreviations counted", b["abbreviated_prose"] >= 3)
check("bad prose lowercase starts counted", b["sentence_initial_lowercase"] >= 2)
check("bad prose article rate collapses", b["article_rate"] < 0.03)
check("bad prose aux_verb_rate is lower than good", b["aux_verb_rate"] < g["aux_verb_rate"])
check("detectors separate good from bad", g["violations"] < b["violations"])
check("article rate separates good from bad by >2x",
      g["article_rate"] > 2 * b["article_rate"])

check("code blocks do not trip detectors", c["violations"] == 0)
check("inline code does not trip detectors", c["symbol_connectors"] == 0)
check("code-block identifiers are not counted as abbreviations",
      c["abbreviated_prose"] == 0)

check("violations are auditable", len(b["spans"]) == b["violations"])

# Direct auxiliary verb counting on a short known string
aux_test = metrics.score("The system was running. It is good.")
check("aux verbs are counted directly", aux_test["aux_verb_rate"] > 0 and aux_test["words"] == 7)

# Test contracted auxiliaries
contraction_test = metrics.score("The process doesn't fail. It isn't broken.")
check("contracted auxiliaries are counted", contraction_test["aux_verb_rate"] > 0)

# Test abbreviation periods don't trip false positives
abbrev_test = metrics.score("We tested it, e.g. running the code.")
check("abbreviation periods don't trip lowercase-start", abbrev_test["sentence_initial_lowercase"] == 0)

check("never_cut_missing finds absent keywords",
      metrics.never_cut_missing("the sessions cascade", ["cascade", "invoices"])
      == ["invoices"])
check("never_cut_missing is case-insensitive",
      metrics.never_cut_missing("CASCADE deletes rows", ["cascade"]) == [])

print("\n%d failure(s)" % fails)
sys.exit(1 if fails else 0)
