"""Table UI component for row preview and drill-down."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from lavendertown.models import GhostFinding


def render_table(
    st: object,
    df: object,
    findings: list[GhostFinding],
    backend: str,
) -> None:
    """Render filtered row preview table.

    Args:
        st: Streamlit module
        df: DataFrame being inspected
        findings: List of all ghost findings
        backend: DataFrame backend ("pandas" or "polars")
    """
    st.header("🔍 Row Preview")

    # Get filtered findings
    filtered_findings = _get_filtered_findings(st, findings)

    if not filtered_findings:
        st.info("No findings to display. Adjust filters to see problematic rows.")
        return

    # Collect all affected row indices
    all_row_indices = set()
    for finding in filtered_findings:
        if finding.row_indices:
            all_row_indices.update(finding.row_indices)

    if not all_row_indices:
        st.info("No specific row indices available for these findings.")

        # Show summary table of findings instead
        _render_findings_table(st, filtered_findings)
        return

    # Convert to list and sort
    row_indices_list = sorted(list(all_row_indices))

    # Limit display to first 1000 rows for performance
    display_indices = row_indices_list[:1000]

    if len(row_indices_list) > 1000:
        st.warning(f"Showing first 1,000 of {len(row_indices_list):,} affected rows.")

    # Get subset of DataFrame
    if backend == "pandas":
        subset_df = df.iloc[display_indices]
    else:
        import polars as pl

        subset_df = df.filter(pl.int_range(pl.len()).is_in(display_indices))
        subset_df = subset_df.to_pandas()  # Convert to pandas for display

    # Display table
    st.dataframe(subset_df, use_container_width=True)

    # Show findings for selected rows
    st.subheader("Findings Summary")
    _render_findings_table(st, filtered_findings)


def _render_findings_table(st: object, findings: list[GhostFinding]) -> None:
    """Render a summary table of findings.

    Args:
        st: Streamlit module
        findings: List of findings to display
    """
    import pandas as pd

    # Convert findings to DataFrame for display
    findings_data = []
    for finding in findings:
        findings_data.append(
            {
                "Ghost Type": finding.ghost_type,
                "Column": finding.column,
                "Severity": finding.severity,
                "Description": finding.description,
                "Affected Rows": len(finding.row_indices)
                if finding.row_indices
                else "N/A",
            }
        )

    if findings_data:
        findings_df = pd.DataFrame(findings_data)
        st.dataframe(findings_df, use_container_width=True, hide_index=True)
    else:
        st.info("No findings to display.")


def _get_filtered_findings(
    st: object, findings: list[GhostFinding]
) -> list[GhostFinding]:
    """Apply sidebar filters to findings."""
    filtered = findings

    if "filter_ghost_types" in st.session_state:
        selected_types = st.session_state["filter_ghost_types"]
        if selected_types:
            filtered = [f for f in filtered if f.ghost_type in selected_types]

    if "filter_severities" in st.session_state:
        selected_severities = st.session_state["filter_severities"]
        if selected_severities:
            filtered = [f for f in filtered if f.severity in selected_severities]

    if "filter_columns" in st.session_state:
        selected_columns = st.session_state["filter_columns"]
        if selected_columns:
            filtered = [f for f in filtered if f.column in selected_columns]

    return filtered
