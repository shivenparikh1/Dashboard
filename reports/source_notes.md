# Portfolio Report Source Notes

## Report Scope

The report analyzes the fictional event portfolio in `data/mock_events.csv`.
It is a static decision-support artifact for the project demonstration and must
not be treated as live automotive supply chain intelligence.

## Canonical Sources

1. `src/scoring.py` defines the additive five-factor score.
2. `src/classification.py` defines the Low, Medium, High, and Critical bands.
3. `src/data_loader.py` validates, scores, classifies, and enriches each event.
4. `src/recommendations.py` defines risk-type, component, and escalation actions.
5. `data/mock_events.csv` contains the 30 fictional source events.
6. `docs/scoring_methodology.md` documents model assumptions and limitations.

## Metric Definitions

- Elevated events are events classified as High or Critical.
- Region exposure is the count of elevated events grouped by event region.
- Component exposure is the sum of total risk scores by affected component.
- Critical factor averages are unweighted means across the seven Critical events.

## Reproduce The Report

From the project root:

```bash
python reports/generate_portfolio_report.py
```

The generated HTML is `reports/automotive_risk_portfolio_report.html`, and its
static chart assets are stored in `reports/assets/`.

## Material Limitations

The mock data has no supplier identifier, supplier tier, plant, part number,
vehicle program, inventory coverage, production volume, recovery time, cost, or
revenue-at-risk measure. Component score is a prioritization proxy only.
