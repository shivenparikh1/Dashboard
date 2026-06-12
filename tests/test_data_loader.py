from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import REQUIRED_COLUMNS, load_event_files, load_events


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_DATA = PROJECT_ROOT / "data" / "real_events.csv"
SIMULATED_DATA = PROJECT_ROOT / "data" / "simulated_events.csv"


def test_combined_dataset_uses_real_events_as_the_primary_source():
    events = load_event_files([REAL_DATA, SIMULATED_DATA])

    assert list(events.columns[: len(REQUIRED_COLUMNS)]) == REQUIRED_COLUMNS
    assert len(events) >= 25
    assert (events["data_type"] == "Real").sum() > (
        events["data_type"] == "Simulated"
    ).sum()
    assert set(events["data_type"]) == {"Real", "Simulated"}
    assert (
        events.loc[events["data_type"] == "Real", "source_url"]
        .str.startswith("http")
        .all()
    )


def test_loader_adds_reviewed_and_rule_based_recommendations():
    event = load_events(REAL_DATA).iloc[0]

    assert event["recommended_actions"][0] == event["recommended_action"]
    assert len(event["recommended_actions"]) >= 3


def test_loader_rejects_a_score_that_does_not_match_the_factors(tmp_path):
    events = pd.read_csv(SIMULATED_DATA)
    events.loc[0, "total_risk_score"] = 5
    invalid_file = tmp_path / "invalid_score.csv"
    events.to_csv(invalid_file, index=False)

    with pytest.raises(ValueError, match="must equal the sum"):
        load_events(invalid_file)


def test_loader_requires_a_source_url_for_real_events(tmp_path):
    events = pd.read_csv(REAL_DATA).head(1)
    events.loc[0, "source_url"] = ""
    invalid_file = tmp_path / "missing_source.csv"
    events.to_csv(invalid_file, index=False)

    with pytest.raises(ValueError, match="must include a source_url"):
        load_events(invalid_file)
