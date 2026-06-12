"""CSV loading, validation, and enrichment helpers."""

from pathlib import Path
from typing import Iterable, Union

import pandas as pd

from src.classification import classify_risk_level
from src.recommendations import generate_recommendations
from src.scoring import SCORE_FIELDS, calculate_score_from_values


REQUIRED_COLUMNS = [
    "event_id",
    "date",
    "event_title",
    "event_summary",
    "source_name",
    "source_url",
    "data_type",
    "source_date",
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
    "total_risk_score",
    "risk_level",
    "recommended_action",
    "confidence_level",
    "last_reviewed",
]


def load_events(csv_source: Union[str, Path]) -> pd.DataFrame:
    """Load and validate one manually maintained risk-event CSV."""
    events = pd.read_csv(
        csv_source,
        parse_dates=["date", "source_date", "last_reviewed"],
        keep_default_na=False,
    )
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
    events["source_date"] = pd.to_datetime(events["source_date"], errors="raise")
    events["last_reviewed"] = pd.to_datetime(
        events["last_reviewed"], errors="raise"
    )

    for field in SCORE_FIELDS:
        events[field] = pd.to_numeric(events[field], errors="raise").astype(int)
        if not events[field].between(1, 5).all():
            raise ValueError(f"All values in {field} must be between 1 and 5.")

    if events["event_id"].duplicated().any():
        raise ValueError("Every event_id must be unique.")

    text_fields = [
        "event_id",
        "event_title",
        "event_summary",
        "source_name",
        "region",
        "country",
        "affected_industry",
        "affected_component",
        "risk_type",
    ]
    for field in text_fields:
        if events[field].str.strip().eq("").any():
            raise ValueError(f"Every event must include a {field}.")

    calculated_scores = events.apply(
        lambda row: calculate_score_from_values(
            [int(row[field]) for field in SCORE_FIELDS]
        ),
        axis=1,
    )
    stored_scores = pd.to_numeric(
        events["total_risk_score"], errors="raise"
    ).astype(int)
    if not calculated_scores.equals(stored_scores):
        raise ValueError(
            "Every total_risk_score must equal the sum of the five risk factors."
        )
    events["total_risk_score"] = stored_scores

    calculated_levels = events["total_risk_score"].apply(
        lambda score: classify_risk_level(int(score))
    )
    if not calculated_levels.equals(events["risk_level"]):
        raise ValueError("Every risk_level must match the documented score bands.")

    valid_data_types = {"Real", "Simulated"}
    if not events["data_type"].isin(valid_data_types).all():
        raise ValueError("data_type must be Real or Simulated.")

    valid_confidence_levels = {"High", "Medium", "Low", "Test"}
    if not events["confidence_level"].isin(valid_confidence_levels).all():
        raise ValueError(
            "confidence_level must be High, Medium, Low, or Test."
        )

    real_events = events["data_type"] == "Real"
    if events.loc[real_events, "source_url"].str.strip().eq("").any():
        raise ValueError("Every Real event must include a source_url.")
    if (
        events.loc[real_events, "source_date"]
        > events.loc[real_events, "last_reviewed"]
    ).any():
        raise ValueError("A Real event cannot be reviewed before its source date.")

    if events["recommended_action"].str.strip().eq("").any():
        raise ValueError("Every event must include a recommended_action.")

    events["recommended_actions"] = events.apply(
        lambda row: list(
            dict.fromkeys(
                [row["recommended_action"]]
                + generate_recommendations(
                    row["risk_type"],
                    row["affected_component"],
                    row["risk_level"],
                )
            )
        ),
        axis=1,
    )

    return events.sort_values(
        ["total_risk_score", "date"], ascending=[False, False]
    ).reset_index(drop=True)


def load_event_files(csv_sources: Iterable[Union[str, Path]]) -> pd.DataFrame:
    """Load multiple schema-compatible event files into one validated portfolio."""
    frames = [load_events(csv_source) for csv_source in csv_sources]
    events = pd.concat(frames, ignore_index=True)
    if events["event_id"].duplicated().any():
        raise ValueError("Every event_id must be unique across all event files.")
    return events.sort_values(
        ["total_risk_score", "date"], ascending=[False, False]
    ).reset_index(drop=True)
