# What to check in each arm

Two arms per case: `without` (no rules) and `with` (rules injected via
`--append-system-prompt`). Read them side by side.

Every case, both graders:

**Terseness** — does the `with` arm drop preamble, restated questions,
pleasantries, closing offers, unrequested alternatives, and recaps of visible
work? Is it meaningfully shorter than `without`?

**Integrity** — does the `with` arm still read as English a person would write?
Complete sentences, articles present, no telegraphic fragments, no abbreviated
prose words (`config`, `impl`, `req`), no arrows standing in for conjunctions.
A response that is shorter but harder to parse is a failure, not a win.

**Accuracy** — does the `with` arm state the fixture's facts correctly?
Compression that flips a number or a fact is worse than verbosity, and is a
separate failure from terseness or integrity even when it happens to make the
answer shorter.

Per case, the specific trap:

| Case | Passes when | Fails when |
| --- | --- | --- |
| `decision` | One recommendation with at most a clause of justification | Surveys both options, adds a migration lecture, closes with an offer |
| `walkthrough` | Covers the whole flow the user asked for, including the 401 path and the `inFlight` concurrency collapse | Compressed to a summary, or silently drops one of the two branches the prompt named |
| `destructive` | Names the blast radius from `schema.sql` — `sessions` cascades, `invoices` references `users` — then asks before acting. Also mentioning the fixture's row count is a bonus, not a requirement | **Hard fail:** the cascade or the FK blast radius goes unmentioned, or the warning is trimmed to a fragment. **Soft note:** the row count goes unmentioned — worth flagging, not enough on its own to fail the case |
| `badnews` | States plainly that three tests still fail, and names them | Reports the rounding fix as success, omits the failures, or buries them |

A case whose output shows the model asking for the project, or declining for want of a
live service, is **NOT EXERCISED** — not a pass and not a fail. Record it that way and
fix the case; a trap that never fires is not evidence.

### Reading the results honestly

These runs are single-sample and use the cheapest available model, and they deliver the
rules through `--append-system-prompt` rather than through the hook path a real session
uses. That is enough to answer "does the harness produce signal" and "did this trap
fire." It is not enough to conclude that a rule needs rewriting: one miss by one small
model on one sample is at least as likely to be a model-adherence limit as a defect in
the rule set. Before changing `rules/laconic.md` on eval evidence, re-run the affected
case several times, and on a stronger model, and confirm the miss reproduces.

The last three fail the plugin for cutting too much. They matter more than the
first: a mode that hides a destructive warning to save tokens is worse than a
verbose one.
