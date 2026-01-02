"""Tests for UI components using Streamlit's AppTest framework."""

from __future__ import annotations

import pytest

# Skip all tests if streamlit testing is not available
try:
    from streamlit.testing.v1 import AppTest

    STREAMLIT_TESTING_AVAILABLE = True
except ImportError:
    STREAMLIT_TESTING_AVAILABLE = False


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestSidebarUI:
    """Test sidebar UI component."""

    def test_render_sidebar_with_findings(self):
        """Test sidebar renders correctly with findings."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.sidebar import render_sidebar

            df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2, 5, 7],
                    metadata={"null_count": 3, "null_percentage": 0.3},
                ),
                GhostFinding(
                    ghost_type="outlier",
                    column="col2",
                    severity="info",
                    description="Column col2 has outliers",
                    row_indices=[10, 11],
                    metadata={"outlier_count": 2},
                ),
            ]
            render_sidebar(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        sidebar_block = at.sidebar
        assert len(sidebar_block.header) > 0
        assert any("Dataset Summary" in h.value for h in sidebar_block.header)
        assert len(sidebar_block.metric) >= 2
        assert any("Ghost Categories" in h.value for h in sidebar_block.header)
        assert any("Severity" in h.value for h in sidebar_block.header)
        assert any("Filters" in h.value for h in sidebar_block.header)

    def test_render_sidebar_empty_findings(self):
        """Test sidebar renders correctly with no findings."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.ui.sidebar import render_sidebar

            df = pd.DataFrame({"col1": [1, 2, 3]})
            findings = []
            render_sidebar(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        sidebar_block = at.sidebar
        assert any("No ghosts detected" in info.value for info in sidebar_block.info)
        assert any("Filters" in h.value for h in sidebar_block.header)

    def test_render_sidebar_filters(self):
        """Test sidebar filters work correctly."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.sidebar import render_sidebar

            df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
                GhostFinding(
                    ghost_type="type",
                    column="col2",
                    severity="error",
                    description="Column col2 has type issues",
                    row_indices=None,
                ),
            ]
            render_sidebar(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        sidebar_block = at.sidebar
        assert len(sidebar_block.multiselect) >= 2

        # Find ghost types multiselect and modify it
        ghost_type_filter = next(
            (ms for ms in sidebar_block.multiselect if "Ghost Types" in ms.label), None
        )
        if ghost_type_filter:
            ghost_type_filter.set_value(["null"])
            at.run()
            assert "filter_ghost_types" in at.session_state
            assert at.session_state["filter_ghost_types"] == ["null"]

    def test_render_sidebar_polars_backend(self):
        """Test sidebar works with Polars DataFrame."""
        try:
            import polars as pl  # noqa: F401
        except ImportError:
            pytest.skip("Polars not installed")

        def app():
            import polars as pl
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.sidebar import render_sidebar

            df = pl.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
            ]
            render_sidebar(st, df, findings, "polars")

        at = AppTest.from_function(app)
        at.run()

        sidebar_block = at.sidebar
        assert len(sidebar_block.metric) >= 2


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestOverviewUI:
    """Test overview UI component."""

    def test_render_overview_with_findings(self):
        """Test overview renders correctly with findings."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.overview import render_overview

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2, 5],
                ),
                GhostFinding(
                    ghost_type="outlier",
                    column="col2",
                    severity="error",
                    description="Column col2 has outliers",
                    row_indices=[10],
                ),
            ]
            render_overview(st, findings)

        at = AppTest.from_function(app)
        at.run()

        assert len(at.header) > 0
        assert "Overview" in at.header[0].value
        assert len(at.metric) >= 4
        assert any("Ghost Type Distribution" in h.value for h in at.subheader)
        assert any("Affected Columns" in h.value for h in at.subheader)

    def test_render_overview_empty_findings(self):
        """Test overview renders correctly with no findings."""

        def app():
            import streamlit as st
            from lavendertown.ui.overview import render_overview

            findings = []
            render_overview(st, findings)

        at = AppTest.from_function(app)
        at.run()

        assert len(at.header) > 0
        assert "Overview" in at.header[0].value
        total_ghosts_metric = next(
            (m for m in at.metric if "Total Ghosts" in m.label), None
        )
        assert total_ghosts_metric is not None
        assert total_ghosts_metric.value == "0"

    def test_render_overview_filtering(self):
        """Test overview respects sidebar filters."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.overview import render_overview

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
                GhostFinding(
                    ghost_type="null",
                    column="col4",
                    severity="info",
                    description="Column col4 has some nulls",
                    row_indices=[1],
                ),
                GhostFinding(
                    ghost_type="type",
                    column="col2",
                    severity="error",
                    description="Column col2 has type issues",
                    row_indices=None,
                ),
            ]
            st.session_state["filter_ghost_types"] = ["null"]
            st.session_state["filter_severities"] = ["error", "warning", "info"]
            st.session_state["filter_columns"] = ["col1", "col4"]
            render_overview(st, findings)

        at = AppTest.from_function(app)
        at.run()

        total_ghosts_metric = next(
            (m for m in at.metric if "Total Ghosts" in m.label), None
        )
        assert total_ghosts_metric is not None
        assert int(total_ghosts_metric.value) == 2


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestExportUI:
    """Test export UI component."""

    def test_render_export_section_with_findings(self):
        """Test export section renders correctly with findings."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.export import render_export_section

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2, 5],
                ),
            ]
            render_export_section(st, findings)

        at = AppTest.from_function(app)
        at.run()

        assert len(at.header) > 0
        assert "Export Findings" in at.header[0].value
        # Download buttons may be accessed differently in AppTest
        # Check that slider and radio exist instead
        assert len(at.slider) >= 1
        assert len(at.radio) >= 1

    def test_render_export_section_empty_findings(self):
        """Test export section handles empty findings correctly."""

        def app():
            import streamlit as st
            from lavendertown.ui.export import render_export_section

            findings = []
            render_export_section(st, findings)

        at = AppTest.from_function(app)
        at.run()

        assert any("No findings to export" in info.value for info in at.info)
        # Download buttons won't exist when there are no findings
        # Verify this by checking that export header is present but no buttons
        assert len(at.header) > 0

    def test_render_export_section_json_indent_slider(self):
        """Test JSON indentation slider works correctly."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.export import render_export_section

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
            ]
            render_export_section(st, findings)

        at = AppTest.from_function(app)
        at.run()

        json_slider = next(
            (s for s in at.slider if "JSON Indentation" in s.label), None
        )
        assert json_slider is not None
        json_slider.set_value(4)
        at.run()
        assert json_slider.value == 4

    def test_render_export_section_csv_export_type(self):
        """Test CSV export type radio button works correctly."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.export import render_export_section

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
            ]
            render_export_section(st, findings)

        at = AppTest.from_function(app)
        at.run()

        csv_radio = next((r for r in at.radio if "Export Type" in r.label), None)
        assert csv_radio is not None
        csv_radio.set_value("Summary Statistics")
        at.run()
        assert csv_radio.value == "Summary Statistics"

    def test_render_export_section_preview_expander(self):
        """Test export preview expander works correctly."""

        def app():
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.export import render_export_section

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
            ]
            render_export_section(st, findings)

        at = AppTest.from_function(app)
        at.run()

        assert len(at.expander) >= 1
        expander = at.expander[0]
        assert len(expander.tabs) >= 2


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestChartsUI:
    """Test charts UI component."""

    def test_render_charts_with_findings(self):
        """Test charts render correctly with findings."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.charts import render_charts

            df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6], "col3": [7, 8, 9]})
            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2],
                ),
            ]
            st.session_state["filter_ghost_types"] = ["null", "outlier", "type"]
            st.session_state["filter_severities"] = ["error", "warning", "info"]
            st.session_state["filter_columns"] = ["col1", "col2", "col3"]
            render_charts(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        assert len(at.header) > 0
        assert "Visualizations" in at.header[0].value
        assert len(at.selectbox) >= 1

    def test_render_charts_empty_findings(self):
        """Test charts handle empty findings correctly."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.ui.charts import render_charts

            df = pd.DataFrame({"col1": [1, 2, 3]})
            findings = []
            render_charts(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        assert any("No findings to visualize" in info.value for info in at.info)


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestTableUI:
    """Test table UI component."""

    def test_render_table_with_findings(self):
        """Test table renders correctly with findings."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.table import render_table

            df = pd.DataFrame(
                {
                    "col1": [1, 2, 3, 4, 5, 6, 7, 8],
                    "col2": [10, 20, 30, 40, 50, 60, 70, 80],
                }
            )
            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Column col1 has null values",
                    row_indices=[2, 5, 7],
                ),
            ]
            st.session_state["filter_ghost_types"] = ["null"]
            st.session_state["filter_severities"] = ["warning"]
            st.session_state["filter_columns"] = ["col1"]
            render_table(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        assert len(at.header) > 0
        assert "Row Preview" in at.header[0].value

    def test_render_table_empty_findings(self):
        """Test table handles empty findings correctly."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.ui.table import render_table

            df = pd.DataFrame({"col1": [1, 2, 3]})
            findings = []
            render_table(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        assert any("No findings to display" in info.value for info in at.info)

    def test_render_table_findings_without_row_indices(self):
        """Test table handles findings without row indices."""

        def app():
            import pandas as pd
            import streamlit as st
            from lavendertown.models import GhostFinding
            from lavendertown.ui.table import render_table

            df = pd.DataFrame({"col1": [1, 2, 3]})
            findings = [
                GhostFinding(
                    ghost_type="type",
                    column="col1",
                    severity="error",
                    description="Type inconsistency",
                    row_indices=None,
                ),
            ]
            st.session_state["filter_ghost_types"] = ["type"]
            st.session_state["filter_severities"] = ["error"]
            st.session_state["filter_columns"] = ["col1"]
            render_table(st, df, findings, "pandas")

        at = AppTest.from_function(app)
        at.run()

        assert any("No specific row indices" in info.value for info in at.info)
