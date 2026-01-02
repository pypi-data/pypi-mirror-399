"""Plotly visualization backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.ui.visualizations.base import BaseVisualizationBackend


class PlotlyBackend(BaseVisualizationBackend):
    """Plotly-based visualization backend."""

    def __init__(self) -> None:
        """Initialize Plotly backend."""
        super().__init__("plotly")

    def is_available(self) -> bool:
        """Check if Plotly is available.

        Returns:
            True if Plotly is installed, False otherwise
        """
        try:
            import plotly.graph_objects as go  # noqa: F401

            return True
        except ImportError:
            return False

    def render_chart(
        self,
        st: object,
        chart_data: object,
        chart_type: str,
        **kwargs: object,
    ) -> None:
        """Render a chart using Plotly.

        Args:
            st: Streamlit module object
            chart_data: Plotly figure object or chart configuration dict
            chart_type: Type of chart ("line", "bar", "scatter", "scatter3d", "heatmap")
            **kwargs: Additional chart-specific arguments
        """
        if not self.is_available():
            st.error(
                "Plotly is required for interactive visualizations. "
                "Install with: pip install lavendertown[plotly]"
            )
            return

        import plotly.graph_objects as go
        import plotly.express as px

        # If chart_data is already a Plotly figure, use it directly
        if isinstance(chart_data, (go.Figure, px._chart_types.Figure)):
            st.plotly_chart(chart_data, use_container_width=True)  # type: ignore[attr-defined]
            return

        # Otherwise, create chart based on chart_type
        if chart_type == "line":
            fig = px.line(chart_data, **kwargs)
        elif chart_type == "bar":
            fig = px.bar(chart_data, **kwargs)
        elif chart_type == "scatter":
            fig = px.scatter(chart_data, **kwargs)
        elif chart_type == "scatter3d":
            fig = px.scatter_3d(chart_data, **kwargs)
        elif chart_type == "heatmap":
            fig = px.imshow(chart_data, **kwargs)
        else:
            st.error(f"Unsupported chart type: {chart_type}")
            return

        st.plotly_chart(fig, use_container_width=True)  # type: ignore[attr-defined]
