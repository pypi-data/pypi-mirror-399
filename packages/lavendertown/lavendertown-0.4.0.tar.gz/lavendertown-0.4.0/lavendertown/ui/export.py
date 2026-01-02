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

    # Rule export section (if rules exist)
    if "ruleset" in st.session_state:
        st.divider()
        st.header("📋 Export Rules")

        ruleset = st.session_state["ruleset"]
        if ruleset.rules:
            rule_col1, rule_col2 = st.columns(2)

            # Pandera export
            with rule_col1:
                st.subheader("Pandera Schema")
                try:
                    from lavendertown.export.pandera import export_ruleset_to_pandera

                    # Create a simple representation - for full export, users can use CLI
                    try:
                        schema = export_ruleset_to_pandera(ruleset)
                        schema_repr = str(schema)
                        st.info("✅ Pandera export available")
                        st.code(
                            schema_repr[:500] + "..."
                            if len(schema_repr) > 500
                            else schema_repr,
                            language="python",
                        )
                        st.caption(
                            "Use CLI command 'lavendertown export-rules' for full export"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Pandera export error: {str(e)}")
                except ImportError:
                    st.info(
                        "📦 Install Pandera to export rules: pip install lavendertown[pandera]"
                    )

            # Great Expectations export
            with rule_col2:
                st.subheader("Great Expectations")
                try:
                    from lavendertown.export.great_expectations import (
                        export_ruleset_to_great_expectations_json,
                    )

                    try:
                        ge_json = export_ruleset_to_great_expectations_json(ruleset)
                        st.info("✅ Great Expectations export available")
                        st.code(
                            ge_json[:500] + "..." if len(ge_json) > 500 else ge_json,
                            language="json",
                        )

                        st.download_button(
                            label="📥 Download GE Suite (JSON)",
                            data=ge_json,
                            file_name="expectation_suite.json",
                            mime="application/json",
                            help="Download Great Expectations ExpectationSuite as JSON",
                            key="download_ge_suite",
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Great Expectations export error: {str(e)}")
                except ImportError:
                    st.info(
                        "📦 Install Great Expectations to export rules: pip install lavendertown[great_expectations]"
                    )
        else:
            st.info("No rules defined. Create rules in the Rules panel to export them.")
