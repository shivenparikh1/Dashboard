"""CSV loading, validation, and enrichment helpers."""

from pathlib import Path
from typing import Union

import pandas as pd

from src.classification import classify_risk_level
from src.recommendations import generate_recommendations
from src.scoring import SCORE_FIELDS, calculate_score_from_values


REQUIRED_COLUMNS = [
    "event_id",
    "date",
    "event_title",
    "event_summary",
    "source_type",
    "region",
    "country",
    "affected_industry",
    "affected_component",
    "risk_type",
    "severity",
    "probability",
    "time_sensitivity",
    "substitution_difficulty",
    "production_impact",
]


def load_events(csv_source: Union[str, Path]) -> pd.DataFrame:
    """Load, validate, score, classify, and enrich event data."""
    events = pd.read_csv(csv_source, parse_dates=["date"])
    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in events.columns
    ]
    if missing_columns:
        raise ValueError(
            "The event file is missing required columns: "
            + ", ".join(missing_columns)
        )

    events = events[REQUIRED_COLUMNS].copy()
    events["date"] = pd.to_datetime(events["date"], errors="raise")

    for field in SCORE_FIELDS:
        events[field] = pd.to_numeric(events[field], errors="raise").astype(int)
        if not events[field].between(1, 5).all():
            raise ValueError(f"All values in {field} must be between 1 and 5.")

    if events["event_id"].duplicated().any():
        raise ValueError("Every event_id must be unique.")

    events["total_risk_score"] = events.apply(
        lambda row: calculate_score_from_values(
            [int(row[field]) for field in SCORE_FIELDS]
        ),
        axis=1,
    )
    events["risk_level"] = events["total_risk_score"].apply(
        lambda score: classify_risk_level(int(score))
    )
    events["recommended_actions"] = events.apply(
        lambda row: generate_recommendations(
            row["risk_type"],
            row["affected_component"],
            row["risk_level"],
        ),
        axis=1,
    )

    return events.sort_values(
        ["total_risk_score", "date"], ascending=[False, False]
    ).reset_index(drop=True)
