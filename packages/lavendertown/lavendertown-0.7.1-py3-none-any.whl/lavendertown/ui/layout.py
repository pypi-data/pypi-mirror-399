"""UI layout and composition system for modular Streamlit components."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lavendertown.models import GhostFinding
    from lavendertown.ui.base import UIComponent


class ComponentLayout:
    """Manages the layout and composition of UI components."""

    def __init__(
        self,
        components: list[UIComponent] | None = None,
        show_dividers: bool = True,
    ) -> None:
        """Initialize the layout.

        Args:
            components: List of UI components to render (in order)
            show_dividers: Whether to show dividers between components
        """
        self.components: list[UIComponent] = components or []
        self.show_dividers = show_dividers

    def add_component(
        self,
        component: UIComponent,
        position: int | None = None,
    ) -> None:
        """Add a component to the layout.

        Args:
            component: Component to add
            position: Optional position to insert at (None = append)
        """
        if position is None:
            self.components.append(component)
        else:
            self.components.insert(position, component)

    def remove_component(self, name: str) -> bool:
        """Remove a component by name.

        Args:
            name: Component name to remove

        Returns:
            True if component was found and removed, False otherwise
        """
        for i, comp in enumerate(self.components):
            if hasattr(comp, "name") and comp.name == name:
                self.components.pop(i)
                return True
        return False

    def get_component(self, name: str) -> UIComponent | None:
        """Get a component by name.

        Args:
            name: Component name to find

        Returns:
            Component if found, None otherwise
        """
        for comp in self.components:
            if hasattr(comp, "name") and comp.name == name:
                return comp
        return None

    def enable_component(self, name: str) -> bool:
        """Enable a component by name.

        Args:
            name: Component name to enable

        Returns:
            True if component was found and enabled, False otherwise
        """
        comp = self.get_component(name)
        if comp and hasattr(comp, "enabled"):
            comp.enabled = True
            return True
        return False

    def disable_component(self, name: str) -> bool:
        """Disable a component by name.

        Args:
            name: Component name to disable

        Returns:
            True if component was found and disabled, False otherwise
        """
        comp = self.get_component(name)
        if comp and hasattr(comp, "enabled"):
            comp.enabled = False
            return True
        return False

    def render(
        self,
        st: object,
        df: object | None = None,
        findings: list[GhostFinding] | None = None,
        backend: str | None = None,
        **kwargs: object,
    ) -> None:
        """Render all components in the layout.

        Args:
            st: Streamlit module object
            df: Optional DataFrame being inspected
            findings: Optional list of GhostFinding objects
            backend: Optional DataFrame backend ("pandas" or "polars")
            **kwargs: Additional arguments to pass to components
        """
        # Sort components by order
        sorted_components = sorted(
            self.components,
            key=lambda c: getattr(c, "order", 999),
        )

        for i, component in enumerate(sorted_components):
            # Skip disabled components
            if hasattr(component, "enabled") and not component.enabled:
                continue

            # Render the component
            component.render(st, df=df, findings=findings, backend=backend, **kwargs)

            # Add divider if enabled and not the last component
            if self.show_dividers and i < len(sorted_components) - 1:
                st.divider()  # type: ignore[attr-defined]


def create_default_layout() -> ComponentLayout:
    """Create the default component layout.

    Returns:
        ComponentLayout with default components configured
    """
    from lavendertown.ui.base import ComponentWrapper
    from lavendertown.ui.charts import render_charts
    from lavendertown.ui.export import render_export_section
    from lavendertown.ui.overview import render_overview
    from lavendertown.ui.table import render_table

    layout = ComponentLayout(show_dividers=True)

    # Add components in default order
    layout.add_component(
        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            order=10,
            requires_findings=True,
        )
    )

    layout.add_component(
        ComponentWrapper(
            name="charts",
            render_func=render_charts,
            order=20,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )

    layout.add_component(
        ComponentWrapper(
            name="table",
            render_func=render_table,
            order=30,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )

    layout.add_component(
        ComponentWrapper(
            name="export",
            render_func=render_export_section,
            order=40,
            requires_findings=True,
        )
    )

    return layout
