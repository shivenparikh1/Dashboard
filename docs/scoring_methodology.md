# Risk Scoring Methodology

## Purpose

The model converts a supply chain risk event into a consistent 5-to-25 priority
score. It is intended for an early-stage analyst control tower where events must
be compared before supplier, inventory, financial, and plant-level data are
available.

The score is a transparent triage aid. It is not a prediction of whether a
specific company will experience a disruption.

## Data Types

### Real

Real events are manually entered from linked public sources. An analyst reviews
the source, summarizes the event, classifies its likely supply chain relevance,
scores the five factors, records confidence, and adds a recommended action.

The presence of a Real event does not establish that a specific automaker has
direct exposure. Public-source evidence and analyst interpretation must be
distinguished from company-specific facts.

### Simulated

Simulated events are fictional testing scenarios. They are stored separately,
clearly labeled, and excluded from the dashboard's default view. They exist only
to test filters, scoring ranges, and interface behavior.

## Five Scoring Factors

Each factor is rated from 1 to 5.

| Factor | What It Measures | Score of 1 | Score of 5 |
|---|---|---|---|
| Severity | Overall seriousness of the event | Minor operational concern | Major disruption requiring leadership attention |
| Probability | Likelihood of a supply effect | Unlikely or weakly connected | Already occurring or highly likely |
| Time sensitivity | Speed of required action | Long planning window | Immediate response required |
| Substitution difficulty | Difficulty of changing the source, part, material, or route | Approved alternative is readily available | No practical short-term alternative |
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

All factors are equally weighted. The minimum score is 5 and the maximum is 25.

The CSV loader recalculates every score and rejects a record if the stored total
does not equal the five-factor sum.

## Risk Levels

| Total Score | Risk Level | Intended Response |
|---|---|---|
| 5-10 | Low | Monitor through the normal review cycle |
| 11-17 | Medium | Assign an owner and confirm a review date |
| 18-22 | High | Begin mitigation and monitor exposure daily |
| 23-25 | Critical | Escalate immediately with cross-functional ownership |

The loader also rejects a record if its stored risk level does not match these
bands.

## Recommendation Logic

Each displayed recommendation set combines:

1. A manually reviewed action written for the specific event.
2. A risk-type action, such as alternate routing for a logistics event.
3. A component action, such as a semiconductor bill-of-material review.
4. An escalation action based on the risk level.

The recommendation engine is deterministic and rule-based. A supply chain owner
must validate cost, feasibility, quality, legal, and regulatory implications
before acting.

## Confidence Levels

| Confidence | Use |
|---|---|
| High | The event is supported by an official or strong direct source and the reported facts are specific |
| Medium | The event is credible, but its automotive exposure or operational effect needs confirmation |
| Low | The signal is preliminary, indirect, or materially uncertain |
| Test | The record is a Simulated testing scenario |

Confidence describes the evidence available for the event entry. It does not
measure the mathematical accuracy of the risk score.

## Weekly Manual Update Workflow

1. Search for new events.
2. Verify source credibility.
3. Classify risk type.
4. Score the five risk factors.
5. Add recommended actions.
6. Review for exaggeration or uncertainty.
7. Update the CSV weekly.

During review, the analyst should:

- Prefer official notices, direct company statements, and established reporting
- Preserve a working source link and source publication date
- Avoid presenting inferred supplier exposure as confirmed fact
- Use cautious language when component, plant, or production effects are unknown
- Lower confidence when only indirect evidence is available
- Record the date of the most recent manual review
- Check for duplicate or resolved events before adding a new row

No website scraping or automatic API ingestion is used in the MVP.

## Example

An event rated:

- Severity: 5
- Probability: 4
- Time sensitivity: 5
- Substitution difficulty: 5
- Production impact: 4

receives a total score of 23 and is classified as Critical.

## Assumptions and Limitations

- Ratings are analyst judgments, not statistical forecasts.
- Equal weighting may not match every organization or vehicle program.
- Public reporting cannot establish direct supplier or bill-of-material exposure.
- The score does not include inventory days, revenue at risk, supplier
  performance, recovery time, contractual protection, or plant-level exposure.
- Events are evaluated independently, so correlated events may understate
  network risk.
- Event status and source reliability are not yet modeled quantitatively.
- Recommendations require human review.

## Future Model Improvements

- Configurable weights by vehicle program or commodity
- Supplier criticality and tier mapping
- Inventory coverage and time-to-impact
- Revenue or production volume at risk
- Event status and recovery tracking
- Quantitative source reliability
- Duplicate detection and related-event clustering
- Historical back-testing against actual disruptions
