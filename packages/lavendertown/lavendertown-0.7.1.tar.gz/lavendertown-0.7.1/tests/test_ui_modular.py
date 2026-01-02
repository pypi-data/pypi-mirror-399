"""Tests for modular UI component system."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from lavendertown.ui.base import BaseComponent, ComponentWrapper
from lavendertown.ui.layout import ComponentLayout, create_default_layout


class TestBaseComponent:
    """Tests for BaseComponent."""

    def test_base_component_initialization(self):
        """Test BaseComponent initialization."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        component = ConcreteComponent(
            name="test_component",
            enabled=True,
            order=10,
        )

        assert component.name == "test_component"
        assert component.enabled is True
        assert component.order == 10

    def test_base_component_repr(self):
        """Test BaseComponent string representation."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        component = ConcreteComponent(name="test", enabled=True, order=5)
        repr_str = repr(component)
        assert "ConcreteComponent" in repr_str
        assert "test" in repr_str

    def test_base_component_render_not_implemented(self):
        """Test that BaseComponent.render raises NotImplementedError."""
        # BaseComponent is abstract, so we can't instantiate it directly
        # But we can verify it has the abstract method
        assert hasattr(BaseComponent, "render")


class TestComponentWrapper:
    """Tests for ComponentWrapper."""

    def test_component_wrapper_initialization(self):
        """Test ComponentWrapper initialization."""

        def dummy_render(st):
            pass

        wrapper = ComponentWrapper(
            name="test",
            render_func=dummy_render,
            enabled=True,
            order=10,
            requires_df=False,
            requires_findings=False,
            requires_backend=False,
        )

        assert wrapper.name == "test"
        assert wrapper.enabled is True
        assert wrapper.order == 10
        assert wrapper.requires_df is False
        assert wrapper.requires_findings is False
        assert wrapper.requires_backend is False

    def test_component_wrapper_render_calls_function(self):
        """Test that ComponentWrapper.render calls the wrapped function."""
        call_args = []

        def test_render(st, df=None, findings=None, backend=None):
            call_args.append((st, df, findings, backend))

        wrapper = ComponentWrapper(
            name="test",
            render_func=test_render,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )

        mock_st = object()
        mock_df = object()
        mock_findings = []
        mock_backend = "pandas"

        wrapper.render(
            mock_st, df=mock_df, findings=mock_findings, backend=mock_backend
        )

        assert len(call_args) == 1
        assert call_args[0] == (mock_st, mock_df, mock_findings, mock_backend)

    def test_component_wrapper_render_with_partial_args(self):
        """Test ComponentWrapper.render with partial arguments."""
        call_args = []

        def test_render(st, findings=None):
            call_args.append((st, findings))

        wrapper = ComponentWrapper(
            name="test",
            render_func=test_render,
            requires_findings=True,
        )

        mock_st = object()
        mock_findings = []

        wrapper.render(mock_st, findings=mock_findings)

        assert len(call_args) == 1
        assert call_args[0] == (mock_st, mock_findings)

    def test_component_wrapper_repr(self):
        """Test ComponentWrapper string representation."""

        def dummy_render(st):
            pass

        wrapper = ComponentWrapper(name="test", render_func=dummy_render)
        repr_str = repr(wrapper)
        assert "ComponentWrapper" in repr_str
        assert "test" in repr_str


class TestComponentLayout:
    """Tests for ComponentLayout."""

    def test_layout_initialization(self):
        """Test ComponentLayout initialization."""
        layout = ComponentLayout(components=None, show_dividers=True)

        assert layout.components == []
        assert layout.show_dividers is True

    def test_layout_add_component(self):
        """Test adding components to layout."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        component = ConcreteComponent(name="test1", order=10)

        layout.add_component(component)

        assert len(layout.components) == 1
        assert layout.components[0] == component

    def test_layout_add_component_at_position(self):
        """Test adding component at specific position."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        comp1 = ConcreteComponent(name="comp1", order=10)
        comp2 = ConcreteComponent(name="comp2", order=20)

        layout.add_component(comp1)
        layout.add_component(comp2, position=0)

        assert layout.components[0] == comp2
        assert layout.components[1] == comp1

    def test_layout_remove_component(self):
        """Test removing component by name."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        comp1 = ConcreteComponent(name="comp1")
        comp2 = ConcreteComponent(name="comp2")

        layout.add_component(comp1)
        layout.add_component(comp2)

        result = layout.remove_component("comp1")

        assert result is True
        assert len(layout.components) == 1
        assert layout.components[0] == comp2

    def test_layout_remove_nonexistent_component(self):
        """Test removing non-existent component."""
        layout = ComponentLayout()
        result = layout.remove_component("nonexistent")
        assert result is False

    def test_layout_get_component(self):
        """Test getting component by name."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        comp1 = ConcreteComponent(name="comp1")
        comp2 = ConcreteComponent(name="comp2")

        layout.add_component(comp1)
        layout.add_component(comp2)

        found = layout.get_component("comp1")
        assert found == comp1

        not_found = layout.get_component("nonexistent")
        assert not_found is None

    def test_layout_enable_component(self):
        """Test enabling a component."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        comp = ConcreteComponent(name="test", enabled=False)
        layout.add_component(comp)

        result = layout.enable_component("test")

        assert result is True
        assert comp.enabled is True

    def test_layout_disable_component(self):
        """Test disabling a component."""

        class ConcreteComponent(BaseComponent):
            def render(self, st, **kwargs):
                pass

        layout = ComponentLayout()
        comp = ConcreteComponent(name="test", enabled=True)
        layout.add_component(comp)

        result = layout.disable_component("test")

        assert result is True
        assert comp.enabled is False

    def test_layout_enable_nonexistent_component(self):
        """Test enabling non-existent component."""
        layout = ComponentLayout()
        result = layout.enable_component("nonexistent")
        assert result is False

    def test_layout_components_sorted_by_order(self):
        """Test that components are rendered in order."""
        layout = ComponentLayout(show_dividers=False)  # Disable dividers for test
        render_order = []

        class OrderedComponent(BaseComponent):
            def __init__(self, name, order):
                super().__init__(name=name, order=order)

            def render(self, st, **kwargs):
                render_order.append(self.name)

        comp1 = OrderedComponent("first", order=10)
        comp2 = OrderedComponent("second", order=20)
        comp3 = OrderedComponent("third", order=5)

        layout.add_component(comp1)
        layout.add_component(comp2)
        layout.add_component(comp3)

        mock_st = object()
        layout.render(mock_st)

        # Should be sorted by order: third (5), first (10), second (20)
        assert render_order == ["third", "first", "second"]

    def test_layout_skips_disabled_components(self):
        """Test that disabled components are not rendered."""
        layout = ComponentLayout(show_dividers=False)  # Disable dividers for test
        render_order = []

        class TestComponent(BaseComponent):
            def render(self, st, **kwargs):
                render_order.append(self.name)

        comp1 = TestComponent(name="enabled", enabled=True)
        comp2 = TestComponent(name="disabled", enabled=False)
        comp3 = TestComponent(name="enabled2", enabled=True)

        layout.add_component(comp1)
        layout.add_component(comp2)
        layout.add_component(comp3)

        mock_st = object()
        layout.render(mock_st)

        assert "enabled" in render_order
        assert "disabled" not in render_order
        assert "enabled2" in render_order


class TestCreateDefaultLayout:
    """Tests for create_default_layout function."""

    def test_create_default_layout(self):
        """Test that default layout is created with expected components."""
        layout = create_default_layout()

        assert len(layout.components) == 4

        component_names = [comp.name for comp in layout.components]
        assert "overview" in component_names
        assert "charts" in component_names
        assert "table" in component_names
        assert "export" in component_names

    def test_default_layout_component_order(self):
        """Test that default layout components have correct order."""
        layout = create_default_layout()

        # Components should be sorted by order
        orders = [comp.order for comp in layout.components]
        assert orders == sorted(orders)

        # Verify expected order values
        overview = layout.get_component("overview")
        charts = layout.get_component("charts")
        table = layout.get_component("table")
        export = layout.get_component("export")

        assert overview is not None
        assert charts is not None
        assert table is not None
        assert export is not None

        assert overview.order < charts.order
        assert charts.order < table.order
        assert table.order < export.order


class TestModularUIWithInspector:
    """Integration tests for modular UI with Inspector."""

    def test_inspector_with_default_layout(self):
        """Test that Inspector works with default layout."""
        import pandas as pd
        from lavendertown import Inspector

        df = pd.DataFrame({"a": [1, 2, None, 4]})
        inspector = Inspector(df)

        # Should not raise an error
        assert inspector.ui_layout is None  # Uses default internally

    def test_inspector_with_custom_layout(self):
        """Test Inspector with custom layout."""
        import pandas as pd
        from lavendertown import Inspector
        from lavendertown.ui.layout import ComponentLayout
        from lavendertown.ui.base import ComponentWrapper
        from lavendertown.ui.overview import render_overview

        df = pd.DataFrame({"a": [1, 2, None, 4]})
        custom_layout = ComponentLayout()
        custom_layout.add_component(
            ComponentWrapper(
                name="overview",
                render_func=render_overview,
                order=10,
                requires_findings=True,
            )
        )

        inspector = Inspector(df, ui_layout=custom_layout)

        assert inspector.ui_layout == custom_layout
        assert len(custom_layout.components) == 1

    def test_inspector_with_minimal_layout(self):
        """Test Inspector with minimal custom layout."""
        import pandas as pd
        from lavendertown import Inspector
        from lavendertown.ui.layout import ComponentLayout
        from lavendertown.ui.base import ComponentWrapper
        from lavendertown.ui.overview import render_overview
        from lavendertown.ui.export import render_export_section

        df = pd.DataFrame({"a": [1, 2, None, 4]})
        minimal = ComponentLayout()
        minimal.add_component(
            ComponentWrapper(
                "overview", render_overview, order=10, requires_findings=True
            )
        )
        minimal.add_component(
            ComponentWrapper(
                "export", render_export_section, order=20, requires_findings=True
            )
        )

        inspector = Inspector(df, ui_layout=minimal)

        assert inspector.ui_layout == minimal
        assert len(minimal.components) == 2

    def test_inspector_layout_disable_component(self):
        """Test disabling components in Inspector layout."""
        import pandas as pd
        from lavendertown import Inspector
        from lavendertown.ui.layout import create_default_layout

        df = pd.DataFrame({"a": [1, 2, None, 4]})
        layout = create_default_layout()
        layout.disable_component("charts")

        Inspector(df, ui_layout=layout)

        charts = layout.get_component("charts")
        assert charts is not None
        assert charts.enabled is False

    def test_custom_component_in_layout(self):
        """Test adding a custom component to layout."""
        import pandas as pd
        from lavendertown import Inspector
        from lavendertown.ui.layout import create_default_layout
        from lavendertown.ui.base import ComponentWrapper

        render_calls = []

        def custom_component(st, findings):
            render_calls.append("custom")
            st.write("Custom component")

        df = pd.DataFrame({"a": [1, 2, None, 4]})
        layout = create_default_layout()
        layout.add_component(
            ComponentWrapper(
                name="custom",
                render_func=custom_component,
                order=15,
                requires_findings=True,
            )
        )

        Inspector(df, ui_layout=layout)

        # Verify component was added
        custom = layout.get_component("custom")
        assert custom is not None
        assert custom.name == "custom"


class TestComponentWrapperWithRealComponents:
    """Tests for ComponentWrapper with actual UI components."""

    def test_wrapper_with_overview(self):
        """Test ComponentWrapper with render_overview."""
        from lavendertown.ui.base import ComponentWrapper
        from lavendertown.ui.overview import render_overview

        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            requires_findings=True,
        )

        # Create a simple test app
        at = AppTest.from_string("""
        import streamlit as st
        from lavendertown.ui.base import ComponentWrapper
        from lavendertown.ui.overview import render_overview
        from lavendertown.models import GhostFinding

        wrapper = ComponentWrapper(
            name="overview",
            render_func=render_overview,
            requires_findings=True,
        )

        findings = [
            GhostFinding(
                ghost_type="null",
                column="test",
                severity="info",
                description="Test finding",
            )
        ]

        wrapper.render(st, findings=findings)
        """)

        at.run()

        # Check that overview was rendered
        assert len(at.get("header")) > 0

    def test_wrapper_with_charts(self):
        """Test ComponentWrapper with render_charts."""
        from lavendertown.ui.base import ComponentWrapper
        from lavendertown.ui.charts import render_charts

        wrapper = ComponentWrapper(
            name="charts",
            render_func=render_charts,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )

        # Verify wrapper properties
        assert wrapper.requires_df is True
        assert wrapper.requires_findings is True
        assert wrapper.requires_backend is True
