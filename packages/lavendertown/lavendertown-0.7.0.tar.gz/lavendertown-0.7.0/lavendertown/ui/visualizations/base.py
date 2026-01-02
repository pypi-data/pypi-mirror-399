"""Base visualization backend abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass


class VisualizationBackend(Protocol):
    """Protocol for visualization backends."""

    def render_chart(
        self,
        st: object,
        chart_data: object,
        chart_type: str,
        **kwargs: object,
    ) -> None:
        """Render a chart using the backend.

        Args:
            st: Streamlit module object
            chart_data: Data for the chart
            chart_type: Type of chart to render
            **kwargs: Additional chart-specific arguments
        """
        ...


class BaseVisualizationBackend(ABC):
    """Base class for visualization backends."""

    def __init__(self, name: str) -> None:
        """Initialize the backend.

        Args:
            name: Backend name/identifier
        """
        self.name = name

    @abstractmethod
    def render_chart(
        self,
        st: object,
        chart_data: object,
        chart_type: str,
        **kwargs: object,
    ) -> None:
        """Render a chart using the backend.

        Args:
            st: Streamlit module object
            chart_data: Data for the chart
            chart_type: Type of chart to render
            **kwargs: Additional chart-specific arguments
        """
        pass

    def is_available(self) -> bool:
        """Check if the backend is available.

        Returns:
            True if backend dependencies are installed, False otherwise
        """
        return True


def get_backend(backend_name: str | None = None) -> VisualizationBackend:
    """Get a visualization backend by name.

    Args:
        backend_name: Name of backend ("altair", "plotly", or None for default)

    Returns:
        VisualizationBackend instance

    Raises:
        ValueError: If backend name is invalid
    """
    if backend_name is None:
        # Default to Altair
        backend_name = "altair"

    backend_name = backend_name.lower()

    if backend_name == "altair":
        from lavendertown.ui.visualizations.altair_backend import AltairBackend

        return AltairBackend()
    elif backend_name == "plotly":
        from lavendertown.ui.visualizations.plotly_backend import PlotlyBackend

        return PlotlyBackend()
    else:
        raise ValueError(f"Unknown visualization backend: {backend_name}")
