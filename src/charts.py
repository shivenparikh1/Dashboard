"""Plotly chart builders used by the Streamlit dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


RISK_LEVEL_ORDER = ["Critical", "High", "Medium", "Low"]
RISK_COLORS = {
    "Critical": "#C62828",
    "High": "#EF8A17",
    "Medium": "#E7B63E",
    "Low": "#5B8E46",
}
NAVY = "#123A72"
BLUE = "#2463A7"
LIGHT_BLUE = "#9CBADF"
GRID = "#E7EBF0"


def _apply_common_layout(figure: go.Figure, height: int = 360) -> go.Figure:
    """Apply consistent, quiet dashboard styling."""
    figure.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=45, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#182233", family="Arial, sans-serif"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white"),
    )
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


def weekly_event_volume_chart(events: pd.DataFrame) -> go.Figure:
    """Show weekly event volume split by risk level."""
    weekly = events.copy()
    weekly["week"] = (
        weekly["date"].dt.to_period("W").apply(lambda period: period.start_time)
    )
    weekly = (
        weekly.groupby(["week", "risk_level"], as_index=False)
        .size()
        .rename(columns={"size": "events"})
    )

    figure = px.bar(
        weekly,
        x="week",
        y="events",
        color="risk_level",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_level": list(reversed(RISK_LEVEL_ORDER))},
        labels={"week": "Week", "events": "Events", "risk_level": "Risk level"},
    )
    figure.update_layout(barmode="stack", title="Weekly Risk Event Volume")
    figure.update_xaxes(tickformat="%b %d")
    return _apply_common_layout(figure)


def risk_level_mix_chart(events: pd.DataFrame) -> go.Figure:
    """Show the share of events in each risk band."""
    mix = (
        events["risk_level"]
        .value_counts()
        .reindex(RISK_LEVEL_ORDER, fill_value=0)
        .rename_axis("risk_level")
        .reset_index(name="events")
    )
    figure = px.pie(
        mix,
        names="risk_level",
        values="events",
        hole=0.58,
        color="risk_level",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_level": RISK_LEVEL_ORDER},
    )
    figure.update_traces(
        textinfo="value",
        textposition="inside",
        insidetextorientation="horizontal",
        hovertemplate="%{label}: %{value} events (%{percent})<extra></extra>",
    )
    figure.update_layout(title="Risk Level Mix")
    return _apply_common_layout(figure)


def region_exposure_chart(events: pd.DataFrame) -> go.Figure:
    """Rank regions by the number of high and critical events."""
    elevated = events[events["risk_level"].isin(["High", "Critical"])]
    exposure = (
        elevated.groupby("region", as_index=False)
        .size()
        .rename(columns={"size": "events"})
        .sort_values("events", ascending=True)
    )
    figure = px.bar(
        exposure,
        x="events",
        y="region",
        orientation="h",
        labels={"events": "High + Critical Events", "region": "Region"},
        text="events",
    )
    figure.update_traces(marker_color=NAVY, textposition="outside")
    figure.update_layout(title="Region Exposure", showlegend=False)
    return _apply_common_layout(figure)


def component_exposure_chart(events: pd.DataFrame) -> go.Figure:
    """Rank affected components by accumulated risk score."""
    exposure = (
        events.groupby("affected_component", as_index=False)["total_risk_score"]
        .sum()
        .sort_values("total_risk_score", ascending=True)
        .tail(10)
    )
    figure = px.bar(
        exposure,
        x="total_risk_score",
        y="affected_component",
        orientation="h",
        labels={
            "total_risk_score": "Cumulative Risk Score",
            "affected_component": "Component",
        },
        text="total_risk_score",
    )
    figure.update_traces(marker_color=BLUE, textposition="outside")
    figure.update_layout(title="Component Exposure", showlegend=False)
    return _apply_common_layout(figure, height=430)


def score_breakdown_chart(event: pd.Series) -> go.Figure:
    """Show the five factor ratings for one selected event."""
    labels = [
        "Severity",
        "Probability",
        "Time sensitivity",
        "Substitution difficulty",
        "Production impact",
    ]
    values = [
        event["severity"],
        event["probability"],
        event["time_sensitivity"],
        event["substitution_difficulty"],
        event["production_impact"],
    ]
    figure = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=[BLUE, BLUE, NAVY, NAVY, "#D97706"],
            text=values,
            textposition="inside",
        )
    )
    figure.update_layout(title="Five-Factor Risk Score")
    figure.update_xaxes(range=[0, 5.5], dtick=1, title="Rating (1–5)")
    figure.update_yaxes(autorange="reversed", title="")
    return _apply_common_layout(figure)
