# The arrow work: six rounds, five edits, and what is left

Six rounds have been spent on one prohibition — *"No arrows inside a sentence"* —
and none of the five rule edits was accepted. This is the index for that line of
work, so a seventh attempt starts from what the six established rather than from
the issue that opened them.

Issues: [#20] (located them), [#34] (asked whether an enumerated prohibition can
close), [#36] (asked for the instrument), [#164] (asked whether the rule's own
`Wrong:` line is the carrier). **All four are closed.**

## The five edits, in order

| round | the edit | target | verdict |
|---|---|---|---|
| [01](round-01.md) | name the colon-introduced chain in the prohibition | `violations_total` | **reject** — never-cut lost 0 → 1 |
| [03](round-03.md) | "a bullet and a numbered step are prose too", plus a branch-list example | `violations_total` | **reject** — never-cut 0 → 1, quality 0 → 3; **target moved 26 → 20, p = 0.231** |
| [04](round-04.md) | a read-it-aloud substitution test, on top of the enumeration | `violations_total` on `walkthrough`, `ordered-steps` | **reject** — quality 0 → 3, readability 26 → 33, target 21 → 27. **First round scored by `--target-cases`** |
| [30](round-30.md) | close the licence the "use a numbered list instead" remedy grants: a bullet is prose, so moving a chain into one relocates the arrow | `violations_total` on `walkthrough` | **reject** — never-cut 9 → 16, on `destructive`/haiku **2 → 8**. **The target passed decisively: 108 → 58, p = 0.016** |
| [31](round-31.md) | a mapping `Wrong:`/`Right:` pair whose remedy keeps the bullet | `violations_total` on `walkthrough`, sonnet | **reject** — target moved the wrong way, 31 → 33, and round-wide rose 60 → 63 |
| [38](round-38.md) | **no enumeration**: replace both rendered arrow specimens with prose descriptions of the same error | arrows on three cases, two trees simultaneously | **reject** — arrows did not fall: control 36, edit **62**, p = 0.341 |

## What the six established

**1. The instrument [#36] asked for exists and works.** A case-scoped count
target shipped for round 04 and has been used by rounds 04, 30 and 31.
[#36]'s claim that "the loop currently cannot score it on the cases it targets"
is resolved.

**2. `ordered-steps` is no longer a target.**
[`arrows-scope-36.md`](arrows-scope-36.md) re-measured the concentration at
today's rules: `ordered-steps` sits at **2 of 20 responses**, 0.1 to 0.3 arrows
each. Scoping a count target to it adds a cell that has never moved outside its
own noise and votes anyway. The two-case framing in [#36]'s title is half wrong.

**3. `walkthrough` is the residual, and it is still the worst case in the set.**

| scope, at today's rules | responses carrying an arrow |
|---|--:|
| `walkthrough` | 9/40 (22%) |
| `design-*` sonnet | 46/848 (5%) |
| everything else | 5/80 (6%) |

Fisher p = 0.00042 against the design cases; on chains specifically, 37.5 per 100
responses against 2.6.

**4. There is no form-shaped hole to aim at.** Four rule revisions cut the rate
by roughly two thirds and moved neither composition:

| revision | chains per 100 | mappings per 100 | in a list | in prose |
|---|--:|--:|--:|--:|
| `1830906901` | 22.0 | 24.5 | 65% | 35% |
| `136269960` | 2.6 | 4.7 | 61% | 39% |

The shipped section lowers every form evenly rather than closing one. **That is
why a sixth enumeration is the move the evidence argues against** — rounds 01, 03
and 04 each added a position, and each saw arrows appear in the position another
covered.

**5. The rule's own `Wrong:` line is not the carrier.** [#164]'s hypothesis was
that a rendered specimen leaks the form it prohibits, which round 31 appeared to
show propagating into `destructive`/sonnet. Round 38 replaced both specimens with
prose and arrows did not fall — control 36 against edit 62, the point estimate
moving the wrong way. What survives is the narrower reading that a *newly added*
example's recency may matter rather than a standing one's presence, which is
untested.

**6. Round 30 is the one that hurts.** Its target passed at p = 0.016, the
largest movement the loop has measured on a named target, and the round rejected
anyway — on `destructive`/haiku going 2 → 8 on never-cut. An arrow edit that
works on `walkthrough` has twice now damaged a case its hypothesis never named.
That propagation, not the target, is what has actually been blocking this line.

## What a seventh attempt would have to be

Not another position in the enumeration. The three things the evidence leaves
open, in order of what it would cost:

- **A structural move rather than an additive one.** Round 10 remains the only
  accepted edit in the loop's history that worked by *relocating* a rule rather
  than bounding it in prose, and the over-length cluster records four wording
  attempts failing where one relocation succeeded. Nothing has tried that here.
- **A propagation-aware design.** Rounds 30 and 31 both damaged a case outside
  their scope. The skill now pre-registers the cells that carry a demonstrated
  form ([#164] item 2), which makes the damage visible; it does not prevent it.
- **Or accept the residual.** 22% of `walkthrough` responses at a rate that four
  revisions cut by two thirds is not obviously a defect worth a sixth edit, and
  [#34] closed without establishing that an enumerated prohibition can close at
  all.

**A scoped round is affordable if one is wanted**: `violations_total` on
`walkthrough`, both models, is 2 cells and 29 arrows in 40 responses; detecting a
halving wants about 25 reps a side, so 100 generations, no judge calls, both
sides interleaved in one batch.

[#20]: https://github.com/JordanMPDS/laconic/issues/20
[#34]: https://github.com/JordanMPDS/laconic/issues/34
[#36]: https://github.com/JordanMPDS/laconic/issues/36
[#164]: https://github.com/JordanMPDS/laconic/issues/164
