"""Streamlit entry point for the Automotive Supply Chain Risk Control Tower."""

from html import escape
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
from packaging.version import Version

from src.charts import (
    component_exposure_chart,
    region_exposure_chart,
    risk_level_mix_chart,
    score_breakdown_chart,
    weekly_event_volume_chart,
)
from src.data_loader import load_event_files


APP_TITLE = "Automotive Supply Chain Risk Intelligence Control Tower"
APP_BUILD = "2026.06.12.6"
DATA_PATHS = [
    Path(__file__).parent / "data" / "real_events.csv",
    Path(__file__).parent / "data" / "simulated_events.csv",
]
RISK_LEVELS = ["Critical", "High", "Medium", "Low"]
DATA_TYPES = ["Real", "Simulated"]
DISCLAIMER = (
    "This is a student-built supply chain risk intelligence prototype. "
    "Real events are manually reviewed and scored using a simplified risk model. "
    "The dashboard is for learning and portfolio demonstration, not enterprise "
    "decision-making."
)
STRETCH_WIDTH = (
    {"width": "stretch"}
    if Version(st.__version__) >= Version("1.58.0")
    else {"use_container_width": True}
)


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
    """Read the manually reviewed Real data and optional Simulated test data."""
    return load_event_files(DATA_PATHS)


def filter_events(
    events: pd.DataFrame,
    start_date,
    end_date,
    data_types: List[str],
    levels: List[str],
    regions: List[str],
    risk_types: List[str],
    components: List[str],
) -> pd.DataFrame:
    """Apply dashboard-wide filters."""
    filtered = events[
        events["date"].dt.date.between(start_date, end_date)
        & events["data_type"].isin(data_types)
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
            "data_type",
            "confidence_level",
            "source_name",
            "source_url",
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
            "data_type": "Data Type",
            "confidence_level": "Confidence",
            "source_name": "Source",
            "source_url": "Evidence",
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
    st.info(DISCLAIMER)


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
    left.plotly_chart(weekly_event_volume_chart(events), **STRETCH_WIDTH)
    middle.plotly_chart(risk_level_mix_chart(events), **STRETCH_WIDTH)
    right.plotly_chart(region_exposure_chart(events), **STRETCH_WIDTH)

    st.subheader("High-Risk Alerts")
    alerts = events[events["risk_level"].isin(["High", "Critical"])].head(8)
    if alerts.empty:
        st.success("No high or critical events match the current filters.")
    else:
        st.dataframe(
            format_event_table(alerts),
            hide_index=True,
            column_config={
                "Evidence": st.column_config.LinkColumn(
                    "Evidence",
                    display_text="Open source",
                )
            },
            **STRETCH_WIDTH,
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
        hide_index=True,
        column_config={
            "Evidence": st.column_config.LinkColumn(
                "Evidence",
                display_text="Open source",
            )
        },
        **STRETCH_WIDTH,
    )

    if not feed.empty:
        st.subheader("Event Detail")
        selected = event_selector(feed, "feed_event")
        st.markdown(f"**{selected['event_title']}**")
        st.write(selected["event_summary"])
        st.caption(
            f"Source: {selected['source_name']} | "
            f"Data type: {selected['data_type']} | "
            f"Confidence: {selected['confidence_level']} | "
            f"Industry: {selected['affected_industry']} | "
            f"Country: {selected['country']}"
        )
        if selected["source_url"]:
            st.link_button("Open source evidence", selected["source_url"])


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
        level = escape(str(event["risk_level"]))
        title = escape(str(event["event_title"]))
        country = escape(str(event["country"]))
        component = escape(str(event["affected_component"]))
        risk_type = escape(str(event["risk_type"]))
        summary = escape(str(event["event_summary"]))
        source_name = escape(str(event["source_name"]))
        source_url = escape(str(event["source_url"]), quote=True)
        data_type = escape(str(event["data_type"]))
        confidence = escape(str(event["confidence_level"]))
        source_line = (
            f'<a href="{source_url}" target="_blank" rel="noopener noreferrer">'
            f"Source: {source_name}</a>"
            if source_url
            else f"Source: {source_name}"
        )
        st.markdown(
            f"""
            <div class="alert-card">
                <strong>{level} · {event['total_risk_score']}/25</strong><br>
                <strong>{title}</strong><br>
                {country} · {component} · {risk_type} · {data_type}<br>
                <span class="small-note">{summary}</span><br>
                <span class="small-note">Confidence: {confidence}</span><br>
                {source_line}
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
        score_breakdown_chart(selected), **STRETCH_WIDTH
    )
    with explanation_column:
        st.subheader(selected["event_title"])
        st.write(selected["event_summary"])
        st.caption(
            f"Source: {selected['source_name']} | "
            f"Source date: {selected['source_date']:%Y-%m-%d} | "
            f"Last reviewed: {selected['last_reviewed']:%Y-%m-%d} | "
            f"Confidence: {selected['confidence_level']}"
        )
        if selected["source_url"]:
            st.link_button("Open source evidence", selected["source_url"])
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
    left.plotly_chart(region_exposure_chart(events), **STRETCH_WIDTH)
    right.plotly_chart(component_exposure_chart(events), **STRETCH_WIDTH)

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
        hide_index=True,
        **STRETCH_WIDTH,
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
    if selected["source_url"]:
        st.link_button("Open source evidence", selected["source_url"])

    action_labels = [
        "Reviewed event action",
        "Risk-type action",
        "Component action",
        "Escalation action",
    ]
    for number, action in enumerate(selected["recommended_actions"], start=1):
        label = (
            action_labels[number - 1]
            if number <= len(action_labels)
            else f"Action {number}"
        )
        st.markdown(
            f"""
            <div class="action-card">
                <strong>{escape(label)}</strong><br>
                {escape(str(action))}
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

    st.subheader("Weekly Update Workflow")
    st.markdown(
        """
        1. Search for new events.
        2. Verify source credibility.
        3. Classify risk type.
        4. Score the five risk factors.
        5. Add recommended actions.
        6. Review for exaggeration or uncertainty.
        7. Update the CSV weekly.
        """
    )

    st.subheader("Data Types")
    st.write(
        "**Real** events are manually entered from linked public sources. "
        "**Simulated** events are a small testing-only dataset used to demonstrate "
        "edge cases and dashboard behavior."
    )

    st.subheader("Prototype Limitations")
    st.write(
        "Real events are manually reviewed rather than automatically scraped. "
        "Scores are simplified analyst judgments, and public reporting does not "
        "establish a company's actual supplier, inventory, cost, or vehicle-program "
        "exposure. Source links and confidence labels should be reviewed before use."
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
    selected_data_types = st.multiselect(
        "Data Type",
        DATA_TYPES,
        default=["Real"],
    )
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
    st.caption("Primary data: manually reviewed public-source events")
    st.caption("Optional data: simulated testing scenarios")
    st.caption(f"Build: {APP_BUILD}")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered_events = filter_events(
    all_events,
    start_date,
    end_date,
    selected_data_types,
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
