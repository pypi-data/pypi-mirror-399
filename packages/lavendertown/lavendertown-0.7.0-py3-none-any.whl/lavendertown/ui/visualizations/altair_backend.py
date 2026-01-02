"""Altair visualization backend."""

from __future__ import annotations

from lavendertown.ui.visualizations.base import BaseVisualizationBackend


class AltairBackend(BaseVisualizationBackend):
    """Altair-based visualization backend."""

    def __init__(self) -> None:
        """Initialize Altair backend."""
        super().__init__("altair")

    def is_available(self) -> bool:
        """Check if Altair is available.

        Returns:
            True if Altair is installed, False otherwise
        """
        try:
            import altair  # noqa: F401

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
        """Render a chart using Altair.

        Args:
            st: Streamlit module object
            chart_data: Altair Chart object
            chart_type: Type of chart (unused for Altair, chart is already built)
            **kwargs: Additional arguments (unused)
        """
        if not self.is_available():
            st.error(
                "Altair is required for visualizations. Install with: pip install altair"
            )
            return

        # chart_data should be an Altair Chart object
        st.altair_chart(chart_data, use_container_width=True)  # type: ignore[attr-defined]
