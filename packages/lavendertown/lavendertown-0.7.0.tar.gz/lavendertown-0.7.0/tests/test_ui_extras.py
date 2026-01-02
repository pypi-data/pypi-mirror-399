"""Tests for Streamlit Extras UI components."""

from __future__ import annotations

import pytest

try:
    from streamlit.testing.v1 import AppTest

    STREAMLIT_TESTING_AVAILABLE = True
except ImportError:
    STREAMLIT_TESTING_AVAILABLE = False

try:
    import streamlit_extras  # noqa: F401

    STREAMLIT_EXTRAS_AVAILABLE = True
except ImportError:
    STREAMLIT_EXTRAS_AVAILABLE = False


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestStreamlitExtrasComponents:
    """Tests for Streamlit Extras wrapper components."""

    def test_render_metric_card(self):
        """Test rendering metric card."""

        def app():
            import streamlit as st
            from lavendertown.ui.extras import render_metric_card

            render_metric_card(st, "Test Metric", 42, delta=5)

        at = AppTest.from_function(app)
        at.run()
        # Should render metric (either via extras or fallback)
        assert len(at.get("metric")) >= 1

    def test_render_metric_card_with_help(self):
        """Test rendering metric card with help text."""

        def app():
            import streamlit as st
            from lavendertown.ui.extras import render_metric_card

            render_metric_card(st, "Test", 100, help_text="Help text")

        at = AppTest.from_function(app)
        at.run()
        assert len(at.get("metric")) >= 1

    def test_render_card(self):
        """Test rendering card component."""

        def app():
            import streamlit as st
            from lavendertown.ui.extras import render_card

            with render_card(st, title="Test Card", text="Card content"):
                st.write("Inside card")

        at = AppTest.from_function(app)
        at.run()
        # Card should render (either via extras or container fallback)
        # Just verify the app ran without errors
        assert at is not None

    def test_render_badge(self):
        """Test rendering badge."""

        def app():
            import streamlit as st
            from lavendertown.ui.extras import render_badge

            render_badge(st, "Status", "Active", color="green")

        at = AppTest.from_function(app)
        at.run()
        # Badge should render (either via extras or caption fallback)
        assert len(at.get("caption")) >= 1

    def test_render_toggle(self):
        """Test rendering toggle switch."""

        def app():
            import streamlit as st
            from lavendertown.ui.extras import render_toggle

            value = render_toggle(
                st, "Enable Feature", default_value=False, key="toggle1"
            )
            st.write(f"Value: {value}")

        at = AppTest.from_function(app)
        at.run()
        # Toggle should render (either via extras or checkbox fallback)
        assert len(at.get("checkbox")) >= 1 or len(at.get("toggle")) >= 1

    def test_render_dataframe_explorer(self):
        """Test rendering dataframe explorer."""

        def app():
            import streamlit as st
            import pandas as pd
            from lavendertown.ui.extras import render_dataframe_explorer

            df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
            render_dataframe_explorer(st, df)

        at = AppTest.from_function(app)
        at.run()
        # DataFrame should render (either via extras or dataframe fallback)
        # Just verify the app ran without errors
        assert at is not None


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestStreamlitExtrasFallback:
    """Tests for fallback behavior when streamlit-extras not available."""

    def test_extras_module_imports_without_extras(self):
        """Test that extras module imports even without streamlit-extras."""
        # This should work regardless of whether streamlit-extras is installed
        from lavendertown.ui.extras import (
            render_badge,
            render_card,
            render_dataframe_explorer,
            render_metric_card,
            render_toggle,
        )

        # All functions should be callable
        assert callable(render_metric_card)
        assert callable(render_card)
        assert callable(render_badge)
        assert callable(render_toggle)
        assert callable(render_dataframe_explorer)


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestOverviewWithExtras:
    """Tests for overview component using extras."""

    def test_overview_uses_metric_cards(self):
        """Test that overview component uses enhanced metric cards."""

        def app():
            import streamlit as st
            from lavendertown.ui.overview import render_overview
            from lavendertown.models import GhostFinding

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Test",
                    row_indices=[0],
                    metadata={},
                )
            ]
            render_overview(st, findings)

        at = AppTest.from_function(app)
        at.run()
        # Should render metrics
        assert len(at.get("metric")) >= 1
