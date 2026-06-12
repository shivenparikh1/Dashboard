"""Risk-level classification rules."""

from numbers import Integral


def classify_risk_level(total_risk_score: int) -> str:
    """Classify a valid total score using the documented risk bands."""
    if isinstance(total_risk_score, bool) or not isinstance(total_risk_score, Integral):
        raise ValueError("Total risk score must be an integer from 5 to 25.")
    if total_risk_score < 5 or total_risk_score > 25:
        raise ValueError("Total risk score must be between 5 and 25.")

    if total_risk_score <= 10:
        return "Low"
    if total_risk_score <= 17:
        return "Medium"
    if total_risk_score <= 22:
        return "High"
    return "Critical"
