"""Sidebar UI component for dataset summary and filters."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.models import GhostFinding


def render_sidebar(
    st: object,
    df: object,
    findings: list[GhostFinding],
    backend: str,
) -> None:
    """Render the sidebar with dataset summary, ghost counts, and filters.

    Args:
        st: Streamlit module
        df: DataFrame being inspected
        findings: List of all ghost findings
        backend: DataFrame backend ("pandas" or "polars")
    """
    with st.sidebar:
        st.header("📊 Dataset Summary")

        # Basic dataset info
        if backend == "pandas":
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))
        else:
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))

        st.divider()

        # Ghost category counts
        st.header("👻 Ghost Categories")

        ghost_counts = {}
        for finding in findings:
            ghost_type = finding.ghost_type
            ghost_counts[ghost_type] = ghost_counts.get(ghost_type, 0) + 1

        for ghost_type, count in sorted(ghost_counts.items()):
            st.metric(ghost_type.title(), count)

        if not ghost_counts:
            st.info("No ghosts detected! 🎉")

        st.divider()

        # Severity counts
        st.header("⚠️ Severity")

        severity_counts = {}
        for finding in findings:
            severity = finding.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        for severity in ["error", "warning", "info"]:
            count = severity_counts.get(severity, 0)
            if severity == "error":
                st.metric("🔴 Error", count)
            elif severity == "warning":
                st.metric("🟡 Warning", count)
            else:
                st.metric("ℹ️ Info", count)

        st.divider()

        # Filters
        st.header("🔍 Filters")

        # Ghost type filter
        all_types = sorted(set(f.ghost_type for f in findings))
        if all_types:
            selected_types = st.multiselect(
                "Ghost Types",
                options=all_types,
                default=all_types,
                help="Filter findings by ghost type",
            )
            st.session_state["filter_ghost_types"] = selected_types
        else:
            st.session_state["filter_ghost_types"] = []

        # Severity filter
        all_severities = ["error", "warning", "info"]
        selected_severities = st.multiselect(
            "Severity Levels",
            options=all_severities,
            default=all_severities,
            help="Filter findings by severity level",
        )
        st.session_state["filter_severities"] = selected_severities

        # Column filter
        all_columns = sorted(set(f.column for f in findings))
        if all_columns:
            selected_columns = st.multiselect(
                "Columns",
                options=all_columns,
                default=all_columns,
                help="Filter findings by column",
            )
            st.session_state["filter_columns"] = selected_columns
        else:
            st.session_state["filter_columns"] = []

        st.divider()

        # Rules section
        st.header("📋 Rules")
        if "ruleset" in st.session_state:
            from lavendertown.rules.models import RuleSet

            ruleset: RuleSet = st.session_state["ruleset"]
            enabled_count = sum(1 for r in ruleset.rules if r.enabled)
            st.metric("Active Rules", enabled_count)
        else:
            st.metric("Active Rules", 0)

        if st.button("Manage Rules", help="Open rule editor"):
            st.session_state["show_rules_panel"] = True
