"""Base classes and protocols for Streamlit UI components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from lavendertown.models import GhostFinding


class UIComponent(Protocol):
    """Protocol for UI components that can be rendered in Streamlit."""

    def render(
        self,
        st: object,
        df: object | None = None,
        findings: list[GhostFinding] | None = None,
        backend: str | None = None,
        **kwargs: object,
    ) -> None:
        """Render the UI component.

        Args:
            st: Streamlit module object
            df: Optional DataFrame being inspected
            findings: Optional list of GhostFinding objects
            backend: Optional DataFrame backend ("pandas" or "polars")
            **kwargs: Additional component-specific arguments
        """
        ...


class BaseComponent(ABC):
    """Base class for UI components with common functionality."""

    def __init__(
        self,
        name: str,
        enabled: bool = True,
        order: int = 0,
    ) -> None:
        """Initialize the component.

        Args:
            name: Component name/identifier
            enabled: Whether the component is enabled by default
            order: Display order (lower numbers appear first)
        """
        self.name = name
        self.enabled = enabled
        self.order = order

    @abstractmethod
    def render(
        self,
        st: object,
        df: object | None = None,
        findings: list[GhostFinding] | None = None,
        backend: str | None = None,
        **kwargs: object,
    ) -> None:
        """Render the UI component.

        Args:
            st: Streamlit module object
            df: Optional DataFrame being inspected
            findings: Optional list of GhostFinding objects
            backend: Optional DataFrame backend ("pandas" or "polars")
            **kwargs: Additional component-specific arguments
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name={self.name!r}, enabled={self.enabled}, order={self.order})"


class ComponentWrapper:
    """Wrapper to convert function-based components to component objects."""

    def __init__(
        self,
        name: str,
        render_func: object,
        enabled: bool = True,
        order: int = 0,
        requires_df: bool = False,
        requires_findings: bool = False,
        requires_backend: bool = False,
    ) -> None:
        """Initialize the wrapper.

        Args:
            name: Component name/identifier
            render_func: Function to call for rendering
            enabled: Whether the component is enabled by default
            order: Display order (lower numbers appear first)
            requires_df: Whether the component requires a DataFrame
            requires_findings: Whether the component requires findings
            requires_backend: Whether the component requires backend info
        """
        self.name = name
        self.render_func = render_func
        self.enabled = enabled
        self.order = order
        self.requires_df = requires_df
        self.requires_findings = requires_findings
        self.requires_backend = requires_backend

    def render(
        self,
        st: object,
        df: object | None = None,
        findings: list[GhostFinding] | None = None,
        backend: str | None = None,
        **kwargs: object,
    ) -> None:
        """Render the component by calling the wrapped function.

        Args:
            st: Streamlit module object
            df: Optional DataFrame being inspected
            findings: Optional list of GhostFinding objects
            backend: Optional DataFrame backend ("pandas" or "polars")
            **kwargs: Additional component-specific arguments
        """
        # Build arguments based on what the function needs
        import inspect

        sig = inspect.signature(self.render_func)
        params = sig.parameters

        call_kwargs: dict[str, object] = {}

        # Add standard parameters if they exist in the function signature
        if "st" in params:
            call_kwargs["st"] = st
        if "df" in params and df is not None:
            call_kwargs["df"] = df
        if "findings" in params and findings is not None:
            call_kwargs["findings"] = findings
        if "backend" in params and backend is not None:
            call_kwargs["backend"] = backend

        # Add any additional kwargs
        call_kwargs.update(kwargs)

        # Call the function
        self.render_func(**call_kwargs)

    def __repr__(self) -> str:
        """String representation."""
        return f"ComponentWrapper(name={self.name!r}, enabled={self.enabled}, order={self.order})"
