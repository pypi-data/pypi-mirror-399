"""Overview UI component for high-level metrics and statistics."""

from __future__ import annotations

from lavendertown.models import GhostFinding


def render_overview(st: object, findings: list[GhostFinding]) -> None:
    """Render overview metrics and high-level statistics.

    Args:
        st: Streamlit module
        findings: List of all ghost findings
    """
    st.header("📈 Overview")

    # Get filtered findings based on sidebar filters
    filtered_findings = _get_filtered_findings(st, findings)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Ghosts", len(filtered_findings))

    with col2:
        error_count = sum(1 for f in filtered_findings if f.severity == "error")
        st.metric("Errors", error_count, delta=None)

    with col3:
        warning_count = sum(1 for f in filtered_findings if f.severity == "warning")
        st.metric("Warnings", warning_count, delta=None)

    with col4:
        info_count = sum(1 for f in filtered_findings if f.severity == "info")
        st.metric("Info", info_count, delta=None)

    # Ghost type distribution
    if filtered_findings:
        st.subheader("Ghost Type Distribution")

        ghost_type_counts = {}
        for finding in filtered_findings:
            ghost_type = finding.ghost_type
            ghost_type_counts[ghost_type] = ghost_type_counts.get(ghost_type, 0) + 1

        # Create a simple bar chart using Streamlit
        st.bar_chart(ghost_type_counts)

    # Affected columns summary
    if filtered_findings:
        st.subheader("Affected Columns")

        column_counts = {}
        for finding in filtered_findings:
            column = finding.column
            column_counts[column] = column_counts.get(column, 0) + 1

        # Display as a sorted list
        sorted_columns = sorted(column_counts.items(), key=lambda x: x[1], reverse=True)

        cols = st.columns(min(3, len(sorted_columns)))
        for idx, (column, count) in enumerate(sorted_columns[:9]):  # Show top 9
            with cols[idx % 3]:
                st.metric(column, count)


def _get_filtered_findings(
    st: object, findings: list[GhostFinding]
) -> list[GhostFinding]:
    """Apply sidebar filters to findings.

    Args:
        st: Streamlit module
        findings: List of all findings

    Returns:
        Filtered list of findings
    """
    filtered = findings

    # Filter by ghost type
    if "filter_ghost_types" in st.session_state:
        selected_types = st.session_state["filter_ghost_types"]
        if selected_types:
            filtered = [f for f in filtered if f.ghost_type in selected_types]

    # Filter by severity
    if "filter_severities" in st.session_state:
        selected_severities = st.session_state["filter_severities"]
        if selected_severities:
            filtered = [f for f in filtered if f.severity in selected_severities]

    # Filter by column
    if "filter_columns" in st.session_state:
        selected_columns = st.session_state["filter_columns"]
        if selected_columns:
            filtered = [f for f in filtered if f.column in selected_columns]

    return filtered
