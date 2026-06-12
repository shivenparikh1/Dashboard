"""Smoke tests for packages imported during Streamlit app startup."""


def test_dashboard_runtime_imports():
    import pandas  # noqa: F401
    import plotly.express  # noqa: F401
    import plotly.graph_objects  # noqa: F401
    import streamlit  # noqa: F401

    from src import charts  # noqa: F401
