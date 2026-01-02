"""Charts UI component for column-level visualizations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass

from lavendertown.models import GhostFinding


def render_charts(
    st: object,
    df: object,
    findings: list[GhostFinding],
    backend: str,
) -> None:
    """Render column-level visualizations.

    Args:
        st: Streamlit module
        df: DataFrame being inspected
        findings: List of all ghost findings
        backend: DataFrame backend ("pandas" or "polars")
    """
    st.header("📊 Visualizations")

    # Get filtered findings
    filtered_findings = _get_filtered_findings(st, findings)

    if not filtered_findings:
        st.info("No findings to visualize. Adjust filters to see charts.")
        return

    # Visualization backend selection
    viz_backend_name = _get_visualization_backend(st)

    # Group findings by column
    column_findings = {}
    for finding in filtered_findings:
        column = finding.column
        if column not in column_findings:
            column_findings[column] = []
        column_findings[column].append(finding)

    # Select column to visualize
    if column_findings:
        selected_column = st.selectbox(
            "Select Column to Visualize",
            options=sorted(column_findings.keys()),
            help="Choose a column to see detailed visualizations",
        )

        if selected_column:
            _render_column_charts(
                st,
                df,
                selected_column,
                column_findings[selected_column],
                backend,
                viz_backend_name,
            )


def _get_visualization_backend(st: object) -> str:
    """Get the selected visualization backend.

    Args:
        st: Streamlit module

    Returns:
        Backend name ("altair" or "plotly")
    """
    from lavendertown.ui.visualizations.base import get_backend

    # Check if Plotly is available
    try:
        plotly_backend = get_backend("plotly")
        plotly_available = plotly_backend.is_available()
    except (ImportError, ValueError):
        plotly_available = False

    # Default to Altair
    default_backend = "altair"

    # Show backend selector if Plotly is available
    if plotly_available:
        backend_choice = st.radio(
            "Visualization Backend",
            options=["altair", "plotly"],
            index=0,
            horizontal=True,
            help="Altair: Fast, static charts. Plotly: Interactive charts with zoom/pan.",
        )
        return backend_choice

    return default_backend


def _render_column_charts(
    st: object,
    df: object,
    column: str,
    findings: list[GhostFinding],
    backend: str,
    viz_backend_name: str = "altair",
) -> None:
    """Render charts for a specific column.

    Args:
        st: Streamlit module
        df: DataFrame
        column: Column name to visualize
        findings: Findings for this column
        backend: DataFrame backend
        viz_backend_name: Visualization backend name ("altair" or "plotly")
    """
    from lavendertown.ui.visualizations.base import get_backend

    # Get visualization backend
    try:
        viz_backend = get_backend(viz_backend_name)
    except ValueError:
        st.error(f"Invalid visualization backend: {viz_backend_name}")
        return

    if not viz_backend.is_available():
        st.error(
            f"{viz_backend_name.title()} is not available. "
            f"Install with: pip install lavendertown[{viz_backend_name}]"
        )
        return

    # Import altair for data preparation (needed for both backends)
    try:
        import altair as alt
    except ImportError:
        st.error(
            "Altair is required for visualizations. Install with: pip install altair"
        )
        return

    # Get column data
    if backend == "pandas":
        column_data = df[column].dropna()
        if len(column_data) == 0:
            st.warning(f"Column '{column}' has no non-null values to visualize.")
            return
    else:
        # Polars
        column_data = df.select(column).drop_nulls()[column]
        if len(column_data) == 0:
            st.warning(f"Column '{column}' has no non-null values to visualize.")
            return

    # Determine data type
    if backend == "pandas":
        dtype = df[column].dtype
        is_numeric = dtype in ["int64", "float64", "Int64", "Float64"]
    else:
        dtype = df.schema[column]
        import polars as pl

        is_numeric = dtype in [
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
            pl.Float32,
            pl.Float64,
        ]

    # Null visualization
    null_findings = [f for f in findings if f.ghost_type == "null"]
    if null_findings:
        st.subheader("Null Values")

        # Create null indicator chart
        if backend == "pandas":
            null_data = df[[column]].copy()
            null_data["is_null"] = null_data[column].isna()
        else:
            import polars as pl

            null_data = df.select(
                [pl.col(column), pl.col(column).is_null().alias("is_null")]
            )
            null_data = null_data.to_pandas()

        # Render based on backend
        if viz_backend_name == "plotly":
            from lavendertown.ui.visualizations.plotly_charts import create_null_chart

            plotly_fig = create_null_chart(null_data, column)
            if plotly_fig:
                viz_backend.render_chart(st, plotly_fig, "bar")
        else:
            # Altair
            null_chart = (
                alt.Chart(null_data)
                .mark_bar()
                .encode(
                    x=alt.X("is_null:N", title="Is Null"),
                    y=alt.Y("count():Q", title="Count"),
                    color=alt.Color(
                        "is_null:N", scale=alt.Scale(range=["#ff6b6b", "#51cf66"])
                    ),
                )
                .properties(width=400, height=200)
            )
            viz_backend.render_chart(st, null_chart, "bar")

    # Outlier visualization (for numeric columns)
    outlier_findings = [f for f in findings if f.ghost_type == "outlier"]
    if outlier_findings and is_numeric:
        st.subheader("Outliers")

        # Create histogram with outlier bounds
        if backend == "pandas":
            chart_data = df[[column]].dropna().copy()
        else:
            chart_data = df.select(column).drop_nulls().to_pandas()

        # Get outlier bounds from findings
        for finding in outlier_findings:
            if finding.ghost_type == "outlier" and "lower_bound" in finding.metadata:
                lower_bound = finding.metadata["lower_bound"]
                upper_bound = finding.metadata["upper_bound"]

                histogram = (
                    alt.Chart(chart_data)
                    .mark_bar()
                    .encode(
                        x=alt.X(column, bin=alt.Bin(maxbins=50), title=column),
                        y=alt.Y("count():Q", title="Count"),
                    )
                    .properties(width=600, height=300)
                )

                # Add outlier bounds as vertical lines
                lower_rule = (
                    alt.Chart(pd.DataFrame({"bound": [lower_bound]}))
                    .mark_rule(color="red", strokeDash=[5, 5])
                    .encode(x="bound:Q")
                )

                upper_rule = (
                    alt.Chart(pd.DataFrame({"bound": [upper_bound]}))
                    .mark_rule(color="red", strokeDash=[5, 5])
                    .encode(x="bound:Q")
                )

                outlier_chart = histogram + lower_rule + upper_rule

                # Render based on backend
                if viz_backend_name == "plotly":
                    from lavendertown.ui.visualizations.plotly_charts import (
                        create_outlier_chart,
                    )

                    plotly_fig = create_outlier_chart(
                        chart_data, column, lower_bound, upper_bound
                    )
                    if plotly_fig:
                        viz_backend.render_chart(st, plotly_fig, "histogram")
                else:
                    # Altair
                    viz_backend.render_chart(st, outlier_chart, "histogram")
                break

    # Time-series visualization (for time-series anomaly findings)
    timeseries_findings = [f for f in findings if f.ghost_type == "timeseries_anomaly"]
    if timeseries_findings and is_numeric:
        st.subheader("Time-Series Anomalies")

        for finding in timeseries_findings:
            if (
                finding.ghost_type == "timeseries_anomaly"
                and "datetime_column" in finding.metadata
            ):
                datetime_col = finding.metadata["datetime_column"]

                # Check if datetime column exists
                if (
                    datetime_col not in df.columns
                    if backend == "pandas"
                    else datetime_col not in df.schema
                ):
                    continue

                # Prepare time-series data
                if backend == "pandas":
                    ts_data = df[[datetime_col, column]].copy()
                    ts_data[datetime_col] = pd.to_datetime(ts_data[datetime_col])
                    ts_data = ts_data.sort_values(by=datetime_col).dropna()
                else:
                    import polars as pl

                    ts_data = (
                        df.select([pl.col(datetime_col), pl.col(column)])
                        .with_columns(pl.col(datetime_col).str.to_datetime())
                        .sort(datetime_col)
                        .drop_nulls()
                        .to_pandas()
                    )
                    ts_data[datetime_col] = pd.to_datetime(ts_data[datetime_col])

                if len(ts_data) == 0:
                    continue

                # Mark anomalies
                if finding.row_indices is not None and backend == "pandas":
                    # For Pandas, use row indices
                    ts_data["is_anomaly"] = ts_data.index.isin(finding.row_indices)
                else:
                    # For Polars or when indices not available, mark based on z-score
                    # This is a simplified approach
                    mean_val = ts_data[column].mean()
                    std_val = ts_data[column].std()
                    if std_val > 0:
                        z_scores = (ts_data[column] - mean_val).abs() / std_val
                        ts_data["is_anomaly"] = z_scores > finding.metadata.get(
                            "sensitivity", 3.0
                        )
                    else:
                        ts_data["is_anomaly"] = False

                # Create time-series line chart
                line_chart = (
                    alt.Chart(ts_data)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            f"{datetime_col}:T",
                            title="Time",
                            axis=alt.Axis(format="%Y-%m-%d"),
                        ),
                        y=alt.Y(f"{column}:Q", title=column),
                        color=alt.Color(
                            "is_anomaly:N",
                            scale=alt.Scale(
                                domain=[False, True],
                                range=["#4a90e2", "#e74c3c"],
                            ),
                            legend=alt.Legend(title="Anomaly"),
                        ),
                    )
                    .properties(width=700, height=400)
                )

                # Highlight anomalies with larger points
                anomaly_points = (
                    alt.Chart(ts_data[ts_data["is_anomaly"]])
                    .mark_circle(size=100, color="#e74c3c")
                    .encode(
                        x=alt.X(f"{datetime_col}:T"),
                        y=alt.Y(f"{column}:Q"),
                    )
                )

                timeseries_chart = line_chart + anomaly_points

                # Render based on backend
                if viz_backend_name == "plotly":
                    from lavendertown.ui.visualizations.plotly_charts import (
                        create_timeseries_chart,
                    )

                    anomaly_indices = (
                        finding.row_indices if finding.row_indices is not None else None
                    )
                    plotly_fig = create_timeseries_chart(
                        ts_data, datetime_col, column, anomaly_indices
                    )
                    if plotly_fig:
                        viz_backend.render_chart(st, plotly_fig, "line")
                else:
                    # Altair
                    viz_backend.render_chart(st, timeseries_chart, "line")

                # Show method info
                method = finding.metadata.get("method", "unknown")
                st.caption(
                    f"Detection method: {method} | Sensitivity: {finding.metadata.get('sensitivity', 'N/A')}"
                )
                break

    # ML anomaly visualization
    ml_anomaly_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
    if ml_anomaly_findings and is_numeric:
        st.subheader("ML-Detected Anomalies")

        for finding in ml_anomaly_findings:
            if finding.ghost_type == "ml_anomaly":
                algorithm = finding.metadata.get("algorithm", "unknown")
                columns_analyzed = finding.metadata.get("columns_analyzed", [])
                anomaly_scores = finding.metadata.get("anomaly_scores")

                st.write(f"**Algorithm:** {algorithm}")
                st.write(f"**Columns Analyzed:** {', '.join(columns_analyzed[:5])}")
                if len(columns_analyzed) > 5:
                    st.write(f"*and {len(columns_analyzed) - 5} more columns*")

                # Show anomaly score distribution if available
                if anomaly_scores and len(anomaly_scores) > 0:
                    score_data = pd.DataFrame({"anomaly_score": anomaly_scores})

                    score_chart = (
                        alt.Chart(score_data)
                        .mark_bar()
                        .encode(
                            x=alt.X(
                                "anomaly_score:Q",
                                bin=alt.Bin(maxbins=30),
                                title="Anomaly Score",
                            ),
                            y=alt.Y("count():Q", title="Count"),
                        )
                        .properties(width=600, height=300)
                    )
                    viz_backend.render_chart(st, score_chart, "bar")
                break

    # Type distribution (for object/string columns)
    type_findings = [f for f in findings if f.ghost_type == "type"]
    if type_findings and not is_numeric:
        st.subheader("Type Distribution")

        # For type findings, show metadata about type distribution if available
        for finding in type_findings:
            if "type_distribution" in finding.metadata:
                type_dist = finding.metadata["type_distribution"]

                type_chart_data = pd.DataFrame(
                    [{"type": str(k), "count": v} for k, v in type_dist.items()]
                )

                type_chart = (
                    alt.Chart(type_chart_data)
                    .mark_bar()
                    .encode(
                        x=alt.X("type:N", title="Type"),
                        y=alt.Y("count:Q", title="Count"),
                    )
                    .properties(width=600, height=300)
                )
                viz_backend.render_chart(st, type_chart, "bar")
                break


def _get_filtered_findings(
    st: object, findings: list[GhostFinding]
) -> list[GhostFinding]:
    """Apply sidebar filters to findings."""
    filtered = findings

    if "filter_ghost_types" in st.session_state:
        selected_types = st.session_state["filter_ghost_types"]
        if selected_types:
            filtered = [f for f in filtered if f.ghost_type in selected_types]

    if "filter_severities" in st.session_state:
        selected_severities = st.session_state["filter_severities"]
        if selected_severities:
            filtered = [f for f in filtered if f.severity in selected_severities]

    if "filter_columns" in st.session_state:
        selected_columns = st.session_state["filter_columns"]
        if selected_columns:
            filtered = [f for f in filtered if f.column in selected_columns]

    return filtered
