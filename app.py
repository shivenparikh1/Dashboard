"""Streamlit entry point for the Automotive Supply Chain Risk Control Tower."""

from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from src.charts import (
    component_exposure_chart,
    region_exposure_chart,
    risk_level_mix_chart,
    score_breakdown_chart,
    weekly_event_volume_chart,
)
from src.data_loader import load_events


APP_TITLE = "Automotive Supply Chain Risk Intelligence Control Tower"
APP_BUILD = "2026.06.12.1"
DATA_PATH = Path(__file__).parent / "data" / "mock_events.csv"
RISK_LEVELS = ["Critical", "High", "Medium", "Low"]


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
        .stApp { background: #F7F9FC; }
        [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E8F0; }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] { color: #42526A; }
        [data-testid="stMetricValue"] { color: #102A56; }
        div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 6px; }
        h1, h2, h3 { color: #102A56; }
        .alert-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 5px solid #C62828;
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .action-card {
            background: #FFFFFF;
            border: 1px solid #D8E1EC;
            border-left: 5px solid #2463A7;
            border-radius: 6px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .method-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 18px;
        }
        .small-note { color: #5D6B7D; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_events() -> pd.DataFrame:
    """Read and enrich the local mock event data."""
    return load_events(DATA_PATH)


def filter_events(
    events: pd.DataFrame,
    start_date,
    end_date,
    levels: List[str],
    regions: List[str],
    risk_types: List[str],
    components: List[str],
) -> pd.DataFrame:
    """Apply dashboard-wide filters."""
    filtered = events[
        events["date"].dt.date.between(start_date, end_date)
        & events["risk_level"].isin(levels)
        & events["region"].isin(regions)
        & events["risk_type"].isin(risk_types)
        & events["affected_component"].isin(components)
    ]
    return filtered.copy()


def format_event_table(events: pd.DataFrame) -> pd.DataFrame:
    """Return a concise event table for dashboard display."""
    table = events[
        [
            "event_id",
            "date",
            "event_title",
            "risk_level",
            "total_risk_score",
            "risk_type",
            "region",
            "country",
            "affected_component",
        ]
    ].copy()
    table["date"] = table["date"].dt.strftime("%Y-%m-%d")
    return table.rename(
        columns={
            "event_id": "Event ID",
            "date": "Date",
            "event_title": "Event",
            "risk_level": "Risk Level",
            "total_risk_score": "Score",
            "risk_type": "Risk Type",
            "region": "Region",
            "country": "Country",
            "affected_component": "Component",
        }
    )


def event_selector(events: pd.DataFrame, key: str) -> pd.Series:
    """Render a readable event selector and return the selected row."""
    options = events["event_id"].tolist()
    labels = {
        row["event_id"]: (
            f'{row["event_id"]} | {row["risk_level"]} {row["total_risk_score"]} '
            f'| {row["event_title"]}'
        )
        for _, row in events.iterrows()
    }
    selected_id = st.selectbox(
        "Select an event",
        options,
        format_func=lambda event_id: labels[event_id],
        key=key,
    )
    return events.loc[events["event_id"] == selected_id].iloc[0]


def render_header(section_name: str) -> None:
    """Render a consistent page header."""
    st.title(APP_TITLE)
    st.header(section_name)


def render_executive_overview(events: pd.DataFrame) -> None:
    render_header("Executive Overview")
    critical_count = int((events["risk_level"] == "Critical").sum())
    elevated_count = int(events["risk_level"].isin(["High", "Critical"]).sum())
    average_score = events["total_risk_score"].mean()
    regions = events["region"].nunique()

    columns = st.columns(4)
    columns[0].metric("Critical Events", critical_count)
    columns[1].metric("High + Critical", elevated_count)
    columns[2].metric("Average Risk Score", f"{average_score:.1f} / 25")
    columns[3].metric("Regions Exposed", regions)

    left, middle, right = st.columns([1.45, 1, 1])
    left.plotly_chart(weekly_event_volume_chart(events), use_container_width=True)
    middle.plotly_chart(risk_level_mix_chart(events), use_container_width=True)
    right.plotly_chart(region_exposure_chart(events), use_container_width=True)

    st.subheader("High-Risk Alerts")
    alerts = events[events["risk_level"].isin(["High", "Critical"])].head(8)
    if alerts.empty:
        st.success("No high or critical events match the current filters.")
    else:
        st.dataframe(
            format_event_table(alerts),
            use_container_width=True,
            hide_index=True,
        )


def render_event_feed(events: pd.DataFrame) -> None:
    render_header("Risk Event Feed")
    search_text = st.text_input(
        "Search event titles or summaries",
        placeholder="Example: semiconductor, port, quality",
    )
    feed = events.copy()
    if search_text:
        search_mask = (
            feed["event_title"].str.contains(search_text, case=False, na=False)
            | feed["event_summary"].str.contains(search_text, case=False, na=False)
        )
        feed = feed[search_mask]

    st.caption(f"{len(feed)} events shown, newest and highest-risk events first.")
    st.dataframe(
        format_event_table(feed),
        use_container_width=True,
        hide_index=True,
    )

    if not feed.empty:
        st.subheader("Event Detail")
        selected = event_selector(feed, "feed_event")
        st.markdown(f"**{selected['event_title']}**")
        st.write(selected["event_summary"])
        st.caption(
            f"Source type: {selected['source_type']} | "
            f"Industry: {selected['affected_industry']} | "
            f"Country: {selected['country']}"
        )


def render_high_risk_alerts(events: pd.DataFrame) -> None:
    render_header("High-Risk Alerts")
    alerts = events[events["risk_level"].isin(["Critical", "High"])]
    if alerts.empty:
        st.success("No high or critical events match the current filters.")
        return

    st.caption(
        "Events scoring 18 or higher are shown here for operational escalation."
    )
    for _, event in alerts.iterrows():
        st.markdown(
            f"""
            <div class="alert-card">
                <strong>{event['risk_level']} · {event['total_risk_score']}/25</strong><br>
                <strong>{event['event_title']}</strong><br>
                {event['country']} · {event['affected_component']} · {event['risk_type']}<br>
                <span class="small-note">{event['event_summary']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_score_breakdown(events: pd.DataFrame) -> None:
    render_header("Risk Score Breakdown")
    selected = event_selector(events, "score_event")

    score_column, level_column, component_column = st.columns(3)
    score_column.metric("Total Risk Score", f"{selected['total_risk_score']} / 25")
    level_column.metric("Risk Level", selected["risk_level"])
    component_column.metric("Affected Component", selected["affected_component"])

    chart_column, explanation_column = st.columns([1.4, 1])
    chart_column.plotly_chart(
        score_breakdown_chart(selected), use_container_width=True
    )
    with explanation_column:
        st.subheader(selected["event_title"])
        st.write(selected["event_summary"])
        st.markdown(
            f"""
            <div class="method-box">
                <strong>Calculation</strong><br><br>
                Severity ({selected['severity']}) +
                Probability ({selected['probability']}) +
                Time sensitivity ({selected['time_sensitivity']}) +
                Substitution difficulty ({selected['substitution_difficulty']}) +
                Production impact ({selected['production_impact']})
                = <strong>{selected['total_risk_score']}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_exposure(events: pd.DataFrame) -> None:
    render_header("Supplier/Region Exposure")
    st.info(
        "This CSV-only MVP does not include a supplier master. Component exposure "
        "is used as a practical proxy until supplier and site identifiers are added."
    )

    left, right = st.columns(2)
    left.plotly_chart(region_exposure_chart(events), use_container_width=True)
    right.plotly_chart(component_exposure_chart(events), use_container_width=True)

    summary = (
        events.groupby("region")
        .agg(
            Events=("event_id", "count"),
            Average_Score=("total_risk_score", "mean"),
            Critical_Events=("risk_level", lambda values: (values == "Critical").sum()),
            Countries=("country", "nunique"),
        )
        .reset_index()
        .sort_values(["Critical_Events", "Average_Score"], ascending=False)
    )
    summary["Average_Score"] = summary["Average_Score"].round(1)
    st.subheader("Regional Exposure Summary")
    st.dataframe(
        summary.rename(
            columns={
                "region": "Region",
                "Average_Score": "Average Score",
                "Critical_Events": "Critical Events",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_recommended_actions(events: pd.DataFrame) -> None:
    render_header("Recommended Actions")
    selected = event_selector(events, "actions_event")

    st.subheader(selected["event_title"])
    st.caption(
        f"{selected['risk_level']} risk · {selected['total_risk_score']}/25 · "
        f"{selected['country']} · {selected['affected_component']}"
    )
    st.write(selected["event_summary"])

    for number, action in enumerate(selected["recommended_actions"], start=1):
        st.markdown(
            f"""
            <div class="action-card">
                <strong>Action {number}</strong><br>
                {action}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "Recommendations are rule-based decision support. A supply chain owner "
        "should validate feasibility, cost, quality, and regulatory implications."
    )


def render_methodology() -> None:
    render_header("Methodology")
    st.markdown(
        """
        <div class="method-box">
            <h3>Risk scoring model</h3>
            <p>Each event receives five ratings on a 1-to-5 scale.</p>
            <p><strong>Total risk score = Severity + Probability + Time sensitivity
            + Substitution difficulty + Production impact</strong></p>
            <p>The maximum score is 25 and the minimum score is 5.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Risk Levels")
    bands = pd.DataFrame(
        [
            {"Score Range": "5–10", "Risk Level": "Low", "Meaning": "Monitor"},
            {
                "Score Range": "11–17",
                "Risk Level": "Medium",
                "Meaning": "Assign an owner and review",
            },
            {
                "Score Range": "18–22",
                "Risk Level": "High",
                "Meaning": "Mitigate and monitor daily",
            },
            {
                "Score Range": "23–25",
                "Risk Level": "Critical",
                "Meaning": "Escalate immediately",
            },
        ]
    )
    st.table(bands)

    st.subheader("Recommendation Logic")
    st.write(
        "The recommendation engine combines one action for the event's risk type, "
        "one action for the affected component, and one escalation action based on "
        "the calculated risk level."
    )

    st.subheader("MVP Limitations")
    st.write(
        "All records are fictional. Scores are equal-weighted expert judgments, "
        "recommendations are deterministic rules, and the MVP has no live feeds, "
        "supplier master, inventory positions, cost exposure, or alert workflow."
    )


try:
    all_events = get_events()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load event data: {error}")
    st.stop()

with st.sidebar:
    st.markdown("## Control Tower")
    section = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Risk Event Feed",
            "High-Risk Alerts",
            "Risk Score Breakdown",
            "Supplier/Region Exposure",
            "Recommended Actions",
            "Methodology",
        ],
    )
    st.divider()
    st.markdown("### Filters")
    date_range = st.date_input(
        "Event date range",
        value=(all_events["date"].min().date(), all_events["date"].max().date()),
        min_value=all_events["date"].min().date(),
        max_value=all_events["date"].max().date(),
    )
    selected_levels = st.multiselect(
        "Risk level", RISK_LEVELS, default=RISK_LEVELS
    )
    selected_regions = st.multiselect(
        "Region",
        sorted(all_events["region"].unique()),
        default=sorted(all_events["region"].unique()),
    )
    selected_risk_types = st.multiselect(
        "Risk type",
        sorted(all_events["risk_type"].unique()),
        default=sorted(all_events["risk_type"].unique()),
    )
    selected_components = st.multiselect(
        "Affected component",
        sorted(all_events["affected_component"].unique()),
        default=sorted(all_events["affected_component"].unique()),
    )
    st.divider()
    st.caption("Data source: data/mock_events.csv")
    st.caption("All events and organizations are fictional.")
    st.caption(f"Build: {APP_BUILD}")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered_events = filter_events(
    all_events,
    start_date,
    end_date,
    selected_levels,
    selected_regions,
    selected_risk_types,
    selected_components,
)

if filtered_events.empty:
    render_header(section)
    st.warning("No events match the current filters. Broaden the sidebar selections.")
    st.stop()

section_renderers = {
    "Executive Overview": lambda: render_executive_overview(filtered_events),
    "Risk Event Feed": lambda: render_event_feed(filtered_events),
    "High-Risk Alerts": lambda: render_high_risk_alerts(filtered_events),
    "Risk Score Breakdown": lambda: render_score_breakdown(filtered_events),
    "Supplier/Region Exposure": lambda: render_exposure(filtered_events),
    "Recommended Actions": lambda: render_recommended_actions(filtered_events),
    "Methodology": render_methodology,
}
section_renderers[section]()
