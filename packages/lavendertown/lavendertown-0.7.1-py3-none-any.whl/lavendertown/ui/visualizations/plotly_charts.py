"""Plotly-specific chart creation utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    import plotly.graph_objects as go
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None  # type: ignore[assignment]
    px = None  # type: ignore[assignment]


def create_null_chart(data: object, column: str) -> object | None:
    """Create a Plotly bar chart for null value visualization.

    Args:
        data: DataFrame with null indicators
        column: Column name

    Returns:
        Plotly figure or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        return None

    import pandas as pd

    # Ensure data is pandas DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    null_counts = data["is_null"].value_counts()
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Not Null", "Null"],
                y=[
                    null_counts.get(False, 0),
                    null_counts.get(True, 0),
                ],
                marker_color=["#51cf66", "#ff6b6b"],
            )
        ]
    )
    fig.update_layout(
        title=f"Null Values in {column}",
        xaxis_title="Value Type",
        yaxis_title="Count",
        height=300,
    )
    return fig


def create_outlier_chart(
    data: object, column: str, lower_bound: float, upper_bound: float
) -> object | None:
    """Create a Plotly histogram with outlier bounds for outlier visualization.

    Args:
        data: DataFrame with column data
        column: Column name
        lower_bound: Lower outlier bound
        upper_bound: Upper outlier bound

    Returns:
        Plotly figure or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        return None

    import pandas as pd

    # Ensure data is pandas DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=data[column],
            nbinsx=50,
            name="Distribution",
            marker_color="#4dabf7",
        )
    )

    # Add outlier bounds as vertical lines
    fig.add_vline(
        x=lower_bound,
        line_dash="dash",
        line_color="red",
        annotation_text="Lower Bound",
    )
    fig.add_vline(
        x=upper_bound,
        line_dash="dash",
        line_color="red",
        annotation_text="Upper Bound",
    )

    fig.update_layout(
        title=f"Outlier Visualization for {column}",
        xaxis_title=column,
        yaxis_title="Count",
        height=400,
    )
    return fig


def create_timeseries_chart(
    data: object, datetime_col: str, value_col: str, anomalies: list[int] | None = None
) -> object | None:
    """Create a Plotly line chart for time-series data with anomaly markers.

    Args:
        data: DataFrame with time-series data
        datetime_col: Name of datetime column
        value_col: Name of value column
        anomalies: Optional list of row indices that are anomalies

    Returns:
        Plotly figure or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        return None

    import pandas as pd

    # Ensure data is pandas DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = go.Figure()

    # Add main time-series line
    fig.add_trace(
        go.Scatter(
            x=data[datetime_col],
            y=data[value_col],
            mode="lines",
            name="Time Series",
            line=dict(color="#4dabf7", width=2),
        )
    )

    # Mark anomalies if provided
    if anomalies is not None and len(anomalies) > 0:
        anomaly_data = data.iloc[anomalies] if hasattr(data, "iloc") else data
        fig.add_trace(
            go.Scatter(
                x=anomaly_data[datetime_col],
                y=anomaly_data[value_col],
                mode="markers",
                name="Anomalies",
                marker=dict(color="red", size=10, symbol="x"),
            )
        )

    fig.update_layout(
        title=f"Time-Series Analysis: {value_col}",
        xaxis_title=datetime_col,
        yaxis_title=value_col,
        height=400,
        hovermode="x unified",
    )
    return fig


def create_outlier_3d_chart(
    data: object, columns: list[str], outliers: list[int] | None = None
) -> object | None:
    """Create a 3D scatter plot for multi-dimensional outlier visualization.

    Args:
        data: DataFrame with numeric columns
        columns: List of 3 column names for x, y, z axes
        outliers: Optional list of row indices that are outliers

    Returns:
        Plotly figure or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        return None

    if len(columns) < 3:
        return None

    import pandas as pd

    # Ensure data is pandas DataFrame
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    fig = go.Figure()

    # Normal points
    normal_data = data
    if outliers is not None and len(outliers) > 0:
        normal_indices = [i for i in range(len(data)) if i not in outliers]
        normal_data = data.iloc[normal_indices] if hasattr(data, "iloc") else data

    fig.add_trace(
        go.Scatter3d(
            x=normal_data[columns[0]],
            y=normal_data[columns[1]],
            z=normal_data[columns[2]],
            mode="markers",
            name="Normal",
            marker=dict(size=5, color="#4dabf7", opacity=0.6),
        )
    )

    # Outlier points
    if outliers is not None and len(outliers) > 0:
        outlier_data = data.iloc[outliers] if hasattr(data, "iloc") else data
        fig.add_trace(
            go.Scatter3d(
                x=outlier_data[columns[0]],
                y=outlier_data[columns[1]],
                z=outlier_data[columns[2]],
                mode="markers",
                name="Outliers",
                marker=dict(size=8, color="red", symbol="x"),
            )
        )

    fig.update_layout(
        title="3D Outlier Visualization",
        scene=dict(
            xaxis_title=columns[0],
            yaxis_title=columns[1],
            zaxis_title=columns[2],
        ),
        height=600,
    )
    return fig


def create_ghost_type_distribution_chart(ghost_counts: dict[str, int]) -> object | None:
    """Create a Plotly bar chart for ghost type distribution.

    Args:
        ghost_counts: Dictionary mapping ghost types to counts

    Returns:
        Plotly figure or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        return None

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(ghost_counts.keys()),
                y=list(ghost_counts.values()),
                marker_color="#4dabf7",
            )
        ]
    )
    fig.update_layout(
        title="Ghost Type Distribution",
        xaxis_title="Ghost Type",
        yaxis_title="Count",
        height=300,
    )
    return fig
