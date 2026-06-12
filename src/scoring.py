"""Risk score calculations for supply chain events."""

from numbers import Integral
from typing import Iterable


SCORE_FIELDS = (
    "severity",
    "probability",
    "time_sensitivity",
    "substitution_difficulty",
    "production_impact",
)


def _validate_rating(value: int, field_name: str) -> None:
    """Validate that a risk factor uses the expected 1-to-5 scale."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{field_name} must be an integer from 1 to 5.")
    if value < 1 or value > 5:
        raise ValueError(f"{field_name} must be between 1 and 5.")


def calculate_total_risk_score(
    severity: int,
    probability: int,
    time_sensitivity: int,
    substitution_difficulty: int,
    production_impact: int,
) -> int:
    """Return the sum of the five risk factors after validating each rating."""
    ratings = {
        "severity": severity,
        "probability": probability,
        "time_sensitivity": time_sensitivity,
        "substitution_difficulty": substitution_difficulty,
        "production_impact": production_impact,
    }

    for field_name, value in ratings.items():
        _validate_rating(value, field_name)

    return int(sum(ratings.values()))


def calculate_score_from_values(values: Iterable[int]) -> int:
    """Calculate a score from an ordered collection of five factor ratings."""
    ratings = list(values)
    if len(ratings) != len(SCORE_FIELDS):
        raise ValueError("Exactly five risk factor ratings are required.")
    return calculate_total_risk_score(*ratings)
