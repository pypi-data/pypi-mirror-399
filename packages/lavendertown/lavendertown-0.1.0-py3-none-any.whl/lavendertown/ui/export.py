"""Export UI components for downloading findings."""

from __future__ import annotations

from lavendertown.export.csv import export_summary_to_csv, export_to_csv
from lavendertown.export.json import export_to_json
from lavendertown.models import GhostFinding


def render_export_section(st: object, findings: list[GhostFinding]) -> None:
    """Render export section with download buttons.

    Args:
        st: Streamlit module
        findings: List of ghost findings to export
    """
    st.header("💾 Export Findings")

    if not findings:
        st.info("No findings to export. Upload data and run inspection first.")
        return

    # Export options
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("JSON Export")
        json_indent = st.slider(
            "JSON Indentation",
            min_value=0,
            max_value=4,
            value=2,
            help="Number of spaces for JSON formatting",
            key="json_indent",
        )

        json_str = export_to_json(findings, indent=json_indent)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="findings.json",
            mime="application/json",
            help="Download findings in JSON format",
        )

    with col2:
        st.subheader("CSV Export")
        export_type = st.radio(
            "Export Type",
            options=["Full Findings", "Summary Statistics"],
            help="Choose between full findings or summary statistics",
            key="csv_export_type",
        )

        if export_type == "Full Findings":
            csv_str = export_to_csv(findings)
            file_name = "findings.csv"
        else:
            csv_str = export_summary_to_csv(findings)
            file_name = "findings_summary.csv"

        st.download_button(
            label="📥 Download CSV",
            data=csv_str,
            file_name=file_name,
            mime="text/csv",
            help=f"Download {export_type.lower()} in CSV format",
        )

    # Show preview
    with st.expander("Preview Export"):
        preview_tab1, preview_tab2 = st.tabs(["JSON Preview", "CSV Preview"])

        with preview_tab1:
            st.code(
                json_str[:1000] + "..." if len(json_str) > 1000 else json_str,
                language="json",
            )

        with preview_tab2:
            st.code(
                csv_str[:1000] + "..." if len(csv_str) > 1000 else csv_str,
                language="csv",
            )
