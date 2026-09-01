# Checkout experiment `chk-047`: readout, diagnostics and recommendation

Status: analysis complete, awaiting decision on the ticket.
Analyst: growth-analytics. Reviewed by: platform-data (sign-off pending).

## Contents

1. What ran
2. Why the headline number should not be used
3. The substitute does not rescue it
4. Power, in detail
5. Assignment and instrumentation audit
6. Segment breakdowns
7. Sequential looks, and why they are not reported
8. What the previous two checkout experiments found
9. Proxy outcomes considered
10. Other observations, none decisive
11. Recommendation

## 1. What ran

Experiment `chk-047`, single-page checkout against the current two-page flow.
Assignment on session id, 50/50, no stratification. Ran 2026-08-04 to
2026-08-18, fourteen full days, covering two complete weekly cycles.

Session counts at close:

| Arm | Sessions | Purchases | Rate |
| --- | --- | --- | --- |
| control (two-page) | 912 | 4 | 0.44% |
| treatment (single-page) | 934 | 7 | 0.75% |

The treatment removes the shipping-address page and folds its four fields into
the payment page, keeping field order and validation copy identical. No pricing,
inventory or promotion logic differs between arms. The two arms share a build;
the flow is selected at render time from the assignment cookie.

Traffic during the window was ordinary. Daily sessions ranged 108 to 167 with no
day below 100, and the 2026-08-11 marketing send lifted sessions 41% for one day
without changing arm balance (67 treatment, 64 control that day).

## 2. Why the headline number should not be used

The ticket currently reports this as **+70% lift**. Lift here is
`(treatment_rate / control_rate) - 1`, and the denominator of that ratio is
four purchases. Moving a single control purchase in either direction moves the
reported lift from +36% to +125%. The number is a statement about which side
four coin flips landed on, not about the checkout flow.

This is not a matter of adding a confidence interval to the lift figure. A
ratio estimator whose denominator is a count this small has no stable interval
to report — the interval is wide enough to include both "no effect" and
"doubles conversion", which is the same as having measured nothing.

The instability is not a rounding artifact and it is not fixed by more decimal
places. Enumerating the control arm's plausible purchase counts at the observed
base rate gives reported lifts of +125% (3 purchases), +70% (4), +36% (5) and
+14% (6). All four of those outcomes are ordinary draws from the same underlying
rate. The reported figure is picking one of them and printing it as a finding.

## 3. The substitute does not rescue it

The obvious move is to report the absolute difference instead: 0.75% − 0.44% =
**+0.31 percentage points**. That estimator is better behaved — it does not
divide by a small count, so a single purchase moves it by about 0.11 points
rather than by 89 points of lift.

It does not make the experiment readable. At these rates, detecting a 0.3-point
difference at 80% power needs roughly 34,000 sessions per arm. This experiment
has 912 and 934. The absolute difference is a well-behaved estimator of a
quantity this sample cannot resolve, and reporting it with an interval makes
the uncertainty visible rather than removing it. **Neither metric supports a
ship decision on this data.**

The distinction matters because the two problems are different and only one of
them is about the estimator. The ratio is *unstable*: it moves enormously on one
event. The absolute difference is *stable but unresolved*: it moves very little
on one event, and its interval still spans everything from a meaningful loss to
a meaningful gain. Swapping estimators trades a visibly absurd number for a
quietly uninformative one. It does not add information to the sample.

## 4. Power, in detail

The 34,000-per-arm figure comes from a two-proportion test at the observed
control rate of 0.44%, targeting an absolute difference of 0.31 points, alpha
0.05 two-sided, power 0.80. Varying the assumptions does not change the verdict:

| Target effect | Power | Sessions per arm |
| --- | --- | --- |
| +0.31 pp (observed) | 0.80 | ~34,000 |
| +0.31 pp (observed) | 0.90 | ~45,000 |
| +0.50 pp | 0.80 | ~13,500 |
| +1.00 pp | 0.80 | ~3,900 |
| +2.00 pp | 0.80 | ~1,200 |

At the traffic this surface actually receives — roughly 950 sessions per arm per
fortnight — reaching 34,000 per arm takes about 72 weeks. Reaching the 3,900 per
arm that a full percentage point would need takes about eight weeks, which is
feasible; but a full point is more than triple the effect observed, and powering
for an effect that large means the experiment can only detect a change nobody is
predicting.

Put the other way round: this experiment had roughly 8% power against the effect
it went looking for. An experiment with 8% power that returns a positive result
is more likely to be reporting noise than signal, regardless of which estimator
prints the number.

## 5. Assignment and instrumentation audit

Assignment ran on a hash of the session id with a fixed salt. The hash's output
distribution over the window is 50.6%/49.4%, within the expected range for
1,846 draws. There is no evidence of a sample-ratio mismatch: chi-square against
a 50/50 expectation gives p = 0.61.

Instrumentation was audited on 2026-08-19 against the raw event stream:

- No gaps in the event stream longer than 40 seconds during the window.
- Purchase events reconcile exactly against the payments ledger: 11 purchases in
  the analytics store, 11 settled charges, no orphans on either side.
- The `checkout_started` event fired on both arms at the same point in the flow.
- No duplicate assignment events; no session appears in both arms.

0.3% of sessions lost their assignment event to an ad blocker. Both arms lose
them at the same rate, so this does not bias the comparison, though it does mean
the denominator is very slightly understated on both sides.

Logged-out sessions were excluded by the assignment filter. That was deliberate,
is recorded in the experiment plan, and matches the two prior checkout
experiments, so the exclusion does not break comparability with them.

## 6. Segment breakdowns

Requested by the ticket. They are reported here for completeness and none of
them is readable, for the same reason the headline is not: every cell contains
between zero and four purchases.

| Segment | Control sessions / purchases | Treatment sessions / purchases |
| --- | --- | --- |
| mobile | 556 / 2 | 551 / 4 |
| desktop | 356 / 2 | 383 / 3 |
| returning | 210 / 1 | 205 / 2 |
| new | 702 / 3 | 729 / 5 |
| weekday | 651 / 3 | 673 / 5 |
| weekend | 261 / 1 | 261 / 2 |

Splitting a sample that cannot resolve the headline into six pairs of cells
produces six comparisons that individually resolve less. The arms are balanced
on device mix (61%/59% mobile) and on returning-visitor share (23%/22%), which
is worth knowing as an assignment check and is not worth reading as a finding.

## 7. Sequential looks, and why they are not reported

The dashboard was checked on 2026-08-07, 2026-08-11 and 2026-08-14. On the
2026-08-07 look the treatment arm was behind (1 purchase against 2); on
2026-08-11 it was ahead by the margin now reported. No stopping rule was
registered in the experiment plan, and no alpha spending function was applied.

Those looks are recorded here so the record is complete. They are not a finding
and they must not be reported as one: unplanned interim looks without an alpha
correction inflate the false-positive rate, and in a sample this small the
looks are mostly re-observing the same handful of events.

## 8. What the previous two checkout experiments found

`chk-031` (2026-04) tested a progress indicator on the two-page flow. It ran
five weeks, 3,110 sessions per arm, 22 and 19 purchases, and was reported as
inconclusive — correctly, and on a sample three times this one's.

`chk-039` (2026-06) tested removing the account-creation prompt. It ran six
weeks, 3,800 sessions per arm, 31 and 44 purchases, +0.34 points, and was
shipped. That readout is the closest precedent to this one and it is worth
noting what made it readable: the same absolute effect size, measured on four
times the sample and against a base rate roughly twice as high.

`chk-039` is also why the single-page flow is being tested at all — the account
prompt's removal is what freed the layout room the treatment uses.

## 9. Proxy outcomes considered

If the decision needs to be made before 72 weeks of traffic accumulate, a
higher-frequency proxy is the only route. Three were evaluated against the
event stream for this window:

| Proxy | Control rate | Treatment rate | Sessions/arm for 80% power |
| --- | --- | --- | --- |
| reached payment step | 18.2% | 21.4% | ~2,800 |
| completed address fields | 31.6% | 36.9% | ~1,900 |
| any checkout interaction | 44.1% | 45.0% | ~40,000 |

The first two are resolvable at this traffic within three to five weeks. Neither
is the outcome the business cares about, and using one requires accepting that a
gain in reaching the payment step may not carry through to purchase — which is
exactly what `chk-031` failed to establish. That is a decision for the ticket,
not for this analysis; what this analysis can say is that the proxies are
measurable and the purchase rate is not.

## 10. Other observations, none decisive

- Median time-to-purchase fell from 4m12s to 3m01s. This is a real difference
  and it is measured on 11 purchases total, so it is subject to everything
  above.
- Two support tickets referenced the single-page flow during the window, both
  reporting the same validation-message placement issue. Neither reports a
  failure to complete a purchase.
- Average order value is 4% higher in the treatment arm, on 7 orders against 4.
- The 2026-08-11 marketing send drew unusually price-sensitive traffic; both
  arms received it in proportion.
- Page-load time on the treatment is 180ms faster at the median, which is
  expected from removing a navigation.

## 11. Recommendation

Do not ship on this readout, and do not re-report it with the absolute
difference as though that settled it. Either run to the sample size the effect
needs, or pick a higher-frequency proxy outcome — reaching the payment step,
say — that this traffic volume can actually resolve.

If the ticket needs a one-line summary: the experiment did not fail, it simply
has not run long enough to say anything, and no choice of estimator changes
that.
