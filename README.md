# Automotive Supply Chain Risk Intelligence Control Tower

A portfolio-ready Streamlit dashboard that turns supply chain disruption signals
into prioritized risks and practical response actions for automotive and complex
assembly operations.

> All events, companies, and scenarios in this project are fictional. The data is
> designed for demonstration and learning, not operational decision-making.

## Business Problem

Automotive supply chains are exposed to semiconductor shortages, port delays,
supplier financial stress, labor actions, quality escapes, cyber incidents,
natural disasters, and regulatory changes. These events often arrive through
different channels and are difficult to compare consistently.

This project demonstrates how a supply chain analyst could:

- Organize disruption signals in one event feed
- Apply a transparent risk score
- Identify the events that require immediate attention
- Understand geographic and component exposure
- Recommend a structured first response

The goal is not to predict every disruption. It is to improve prioritization,
communication, and response discipline.

## What the Dashboard Shows

### 1. Executive Overview

Headline metrics summarize critical events, elevated risks, average risk score,
and the number of exposed regions. Charts show event movement, risk mix, and
regional concentration.

### 2. Risk Event Feed

A searchable event table provides the event date, risk type, geography,
component, total score, and risk level, with a detailed summary for each event.

### 3. High-Risk Alerts

High and Critical events are separated for faster operational review.

### 4. Risk Score Breakdown

The five scoring factors are displayed for a selected event so the user can see
why it received its final priority.

### 5. Supplier/Region Exposure

Regional and component views show where elevated risks are concentrated. The MVP
does not include a supplier master, so component exposure is used as an explicit
proxy for supplier exposure.

### 6. Recommended Actions

The app combines risk-type, component, and escalation rules to recommend a
practical first set of mitigation actions.

### 7. Methodology

The dashboard explains the scoring formula, risk bands, recommendation logic,
and current limitations.

## Decision-Ready Portfolio Report

The project also includes a static executive report for a recruiter or
operations stakeholder:

- [`reports/automotive_risk_portfolio_report.html`](reports/automotive_risk_portfolio_report.html)
- Four supporting charts in `reports/assets/`
- Reproducible generation logic in `reports/generate_portfolio_report.py`
- Source and metric notes in `reports/source_notes.md`

The report identifies the main regional and component concentrations, lists the
Critical event queue, and recommends actions for the next 24 hours, 72 hours,
and two weeks.

## Data Inputs

The MVP reads `data/mock_events.csv`, which contains 30 realistic but fictional
risk events.

Each event includes:

- Event date, title, summary, and source type
- Region and country
- Affected industry and component
- Risk type
- Five 1-to-5 factor ratings

The current model is intentionally CSV-based. It has no external API or live
data dependency.

## Scoring Model

Each event receives five ratings:

```text
Total Risk Score =
Severity
+ Probability
+ Time Sensitivity
+ Substitution Difficulty
+ Production Impact
```

| Score | Risk level |
|---|---|
| 5-10 | Low |
| 11-17 | Medium |
| 18-22 | High |
| 23-25 | Critical |

The model is deliberately transparent. A reviewer can trace every total score
back to the five original ratings. More detail is available in
[`docs/scoring_methodology.md`](docs/scoring_methodology.md).

## Project Structure

```text
.
├── app.py
├── data/
│   └── mock_events.csv
├── docs/
│   └── scoring_methodology.md
├── reports/
│   ├── assets/
│   ├── automotive_risk_portfolio_report.html
│   ├── generate_portfolio_report.py
│   └── source_notes.md
├── src/
│   ├── charts.py
│   ├── classification.py
│   ├── data_loader.py
│   ├── recommendations.py
│   └── scoring.py
├── tests/
│   ├── test_recommendations.py
│   └── test_scoring.py
├── requirements.txt
└── README.md
```

## Run the Dashboard

Python 3.9 or later is supported. For Streamlit Community Cloud, select Python
3.12 in Advanced settings to match the platform default used for deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
```

Open the local address shown by Streamlit, usually
`http://localhost:8501`.

When deploying to Streamlit Community Cloud, set the repository to
`shivenparikh1/Dashboard`, the branch to `main`, and the entrypoint to `app.py`.
The root `requirements.txt` selects compatible package versions for both the
Cloud Python 3.14 runtime and local Python 3.9 environments.

## Run the Tests

```bash
pytest
```

The tests cover:

- Score calculation
- Minimum and maximum scores
- Every risk-level boundary
- Invalid factor values
- Risk-type recommendations
- Component-specific recommendations
- Critical-event escalation
- Fallback recommendations

## Regenerate the Portfolio Report

```bash
python reports/generate_portfolio_report.py
```

Open `reports/automotive_risk_portfolio_report.html` in a browser to review the
finished report.

## Limitations

- All data is fictional and manually scored.
- The five risk factors are equally weighted.
- Recommendations are rule-based rather than predictive.
- The MVP has no supplier master, tier mapping, inventory coverage, cost impact,
  vehicle program, plant, or revenue-at-risk data.
- Events are not automatically deduplicated or linked to related disruptions.
- There are no live alerts, workflow assignments, or external data feeds.

## Future Improvements

A production-oriented version could add:

- Supplier, site, tier, and vehicle-program master data
- Inventory days and time-to-production-impact
- Revenue and production volume at risk
- Live news, weather, logistics, and financial feeds
- Source reliability and analyst confidence scores
- Event deduplication and related-event clustering
- Email or collaboration alerts with action ownership
- Historical supplier performance and recovery tracking
- Configurable scoring weights by commodity or program

## Portfolio Value

This project demonstrates the ability to translate a supply chain problem into a
structured analytical product: define data inputs, create a transparent scoring
model, prioritize operational risk, communicate exposure visually, recommend
actions, test the decision logic, and document limitations honestly.
