# Automotive Supply Chain Risk Intelligence Control Tower

A Streamlit dashboard that organizes public supply chain risk signals, applies a
transparent scoring model, and recommends practical first actions for automotive
and complex assembly operations.

> This is a student-built supply chain risk intelligence prototype. Real events
> are manually reviewed and scored using a simplified risk model. The dashboard
> is for learning and portfolio demonstration, not enterprise decision-making.

## Business Problem

Automotive supply chains can be disrupted by supplier fires, labor actions,
semiconductor constraints, logistics interruptions, quality recalls,
cyberattacks, and regulatory changes. These signals arrive from different
sources, use different language, and do not come with a common priority.

This project demonstrates how a supply chain analyst could turn those signals
into a repeatable review process:

- Record the event and preserve its public source
- Classify the affected region, component, and risk type
- Score urgency and potential production impact
- Separate routine monitoring from immediate escalation
- Recommend a practical first response
- Communicate assumptions and uncertainty clearly

The dashboard is designed as an analyst decision-support prototype, not as a
prediction engine.

## Data Inputs

The primary file, `data/real_events.csv`, contains manually entered events from
linked public sources such as government recall data, trade notices, news
organizations, and automotive industry publications.

The initial portfolio contains 23 Real events. A separate
`data/simulated_events.csv` file contains three clearly labeled testing
scenarios. Simulated events are excluded from the default dashboard view and can
be enabled with the Data Type filter.

The project does not automatically scrape websites, call external APIs, or
claim that public reporting proves a company has direct supplier exposure.
Source interpretation and scoring are performed manually.

Each event includes:

- Event identity, title, summary, and relevant dates
- Source name and clickable source URL
- Data Type: `Real` or `Simulated`
- Region, country, industry, and affected component
- Risk type and five factor ratings
- Calculated total score and risk level
- Reviewed action, confidence level, and last-reviewed date

The complete CSV schema is:

```text
event_id, date, event_title, event_summary, source_name, source_url,
data_type, source_date, region, country, affected_industry,
affected_component, risk_type, severity, probability, time_sensitivity,
substitution_difficulty, production_impact, total_risk_score, risk_level,
recommended_action, confidence_level, last_reviewed
```

## Scoring Model

Each event receives five ratings from 1 to 5:

```text
Total Risk Score =
Severity
+ Probability
+ Time Sensitivity
+ Substitution Difficulty
+ Production Impact
```

| Score | Risk Level | Suggested Response |
|---|---|---|
| 5-10 | Low | Monitor |
| 11-17 | Medium | Assign an owner and review |
| 18-22 | High | Begin mitigation and monitor daily |
| 23-25 | Critical | Escalate immediately |

All five factors are equally weighted. The app validates that every stored total
and risk level matches the documented model before displaying the data.

See [docs/scoring_methodology.md](docs/scoring_methodology.md) for factor
definitions, confidence labels, recommendation logic, and review controls.

## Dashboard Features

### Executive Overview

Shows Critical events, High plus Critical events, average score, exposed
regions, weekly event volume, risk mix, and regional concentration.

### Risk Event Feed

Provides a searchable event table with source links, Data Type, confidence,
geography, component, score, and risk level.

### High-Risk Alerts

Separates events scoring 18 or higher for faster operational review.

### Risk Score Breakdown

Explains the five factor ratings behind a selected event and displays its source
date, last review date, and confidence level.

### Supplier/Region Exposure

Shows regional and component concentrations. Because the MVP has no supplier
master, component exposure is clearly labeled as a proxy for supplier exposure.

### Recommended Actions

Combines a manually reviewed event action with rule-based risk-type, component,
and escalation actions.

### Methodology

Explains scoring, risk bands, Data Types, limitations, and the weekly manual
update workflow.

## Weekly Update Workflow

The intended weekly analyst process is:

1. Search for new events.
2. Verify source credibility.
3. Classify risk type.
4. Score the five risk factors.
5. Add recommended actions.
6. Review for exaggeration or uncertainty.
7. Update the CSV weekly.

The workflow is intentionally manual for this MVP. It keeps source selection and
analyst judgment visible and easy to explain during a portfolio review.

## Project Structure

```text
.
├── app.py
├── data/
│   ├── real_events.csv
│   └── simulated_events.csv
├── docs/
│   └── scoring_methodology.md
├── src/
│   ├── charts.py
│   ├── classification.py
│   ├── data_loader.py
│   ├── recommendations.py
│   └── scoring.py
├── tests/
│   ├── test_data_loader.py
│   ├── test_deployment_imports.py
│   ├── test_recommendations.py
│   └── test_scoring.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Run the Dashboard

Python 3.9 or later is supported.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
```

Open the local address shown by Streamlit, usually
`http://localhost:8501`.

For Streamlit Community Cloud, use repository
`shivenparikh1/Dashboard`, branch `main`, and entrypoint `app.py`. The root
`requirements.txt` includes version markers for the local Python 3.9 environment
and Streamlit Cloud's newer Python runtime.

## Run the Tests

```bash
pytest
```

The tests cover:

- Score calculation and all risk-level boundaries
- Invalid score inputs
- Risk-type and component recommendation rules
- Escalation and fallback recommendations
- Required CSV fields and source links
- Stored score reconciliation
- Real and Simulated dataset separation
- Dashboard startup imports

## Limitations

- Real events are manually selected, summarized, classified, and scored.
- Public reporting does not prove direct supplier, plant, inventory, cost, or
  vehicle-program exposure.
- Scores are analyst judgments, not statistical predictions.
- Equal factor weighting may not match every company or commodity.
- Confidence labels are qualitative and do not guarantee source accuracy.
- Event status and related-event deduplication are not yet modeled.
- The MVP has no supplier master, tier mapping, inventory days, revenue at risk,
  action ownership, or workflow notifications.
- There is no automatic scraping, API ingestion, or weekly scheduler.

## Future Improvements

A later version could add:

- Supplier, site, tier, plant, and vehicle-program master data
- Inventory coverage and time-to-production-impact
- Revenue and production volume at risk
- Event status, duplicate detection, and related-event clustering
- Source reliability scoring and a formal analyst approval workflow
- Configurable scoring weights by commodity or program
- Approved news, weather, logistics, financial, and regulatory feeds
- Action owners, due dates, alerts, and recovery tracking

## Portfolio Value

For a supply chain internship recruiter, this project shows the ability to:

- Translate an operational problem into a structured analytical product
- Work with imperfect public information without overstating certainty
- Build an auditable prioritization model
- Connect risk signals to practical mitigation actions
- Communicate exposure through an executive-friendly dashboard
- Test decision logic and document limitations honestly
