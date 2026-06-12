# Risk Scoring Methodology

## Purpose

The scoring model converts a supply chain risk event into a consistent 5-to-25
priority score. It is designed for an early-stage control tower where an analyst
needs a transparent way to compare different events before richer supplier,
inventory, financial, and production data are available.

## Five Scoring Factors

Each factor is rated from 1 to 5.

| Factor | What it measures | A score of 1 | A score of 5 |
|---|---|---|---|
| Severity | Overall seriousness of the disruption | Minor operational concern | Major disruption requiring leadership attention |
| Probability | Likelihood that the event will affect supply | Unlikely | Already occurring or highly likely |
| Time sensitivity | How quickly action is required | Long planning window | Immediate response required |
| Substitution difficulty | Difficulty of switching the part, material, route, or source | Easy approved alternative | No practical short-term alternative |
| Production impact | Potential effect on vehicle or assembly output | Minimal production effect | Line stoppage or major production loss |

## Calculation

```text
Total Risk Score =
Severity
+ Probability
+ Time Sensitivity
+ Substitution Difficulty
+ Production Impact
```

All factors are equally weighted in the MVP.

The minimum possible score is 5 and the maximum is 25.

## Risk Levels

| Total score | Risk level | Intended response |
|---|---|---|
| 5-10 | Low | Monitor through the normal review cycle |
| 11-17 | Medium | Assign an owner and confirm a review date |
| 18-22 | High | Begin mitigation and monitor exposure daily |
| 23-25 | Critical | Escalate immediately with cross-functional ownership |

## Recommendation Logic

The recommendation engine combines three rule groups:

1. A risk-type action, such as alternate routing for a logistics event or an
   8D review for a quality event.
2. A component action, such as semiconductor bill-of-material checks or battery
   cell chemistry and homologation review.
3. An escalation action based on the calculated risk level.

This structure keeps the output specific enough to guide a first response while
remaining easy to understand and audit.

## Example

An event rated:

- Severity: 5
- Probability: 4
- Time sensitivity: 5
- Substitution difficulty: 5
- Production impact: 4

receives a total score of 23 and is classified as Critical.

## Assumptions and Limitations

- Ratings are analyst judgments, not predictions from a statistical model.
- Equal weighting may not match every organization or vehicle program.
- The score does not yet include inventory days, revenue at risk, supplier
  performance, recovery time, contractual protection, or plant-level exposure.
- Events are evaluated independently, so correlated events may understate total
  network risk.
- Recommendations are deterministic decision support and require human review.
- All current data is fictional and intended for portfolio demonstration only.

## Future Model Improvements

Future versions could add:

- Configurable weights by vehicle program or commodity
- Supplier criticality and tier mapping
- Inventory coverage and time-to-impact
- Revenue or production volume at risk
- Confidence scores and source reliability
- Event clustering and duplicate detection
- Historical back-testing against actual disruptions
