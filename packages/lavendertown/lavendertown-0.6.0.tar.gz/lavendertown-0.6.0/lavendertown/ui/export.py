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
    col1, col2, col3 = st.columns(3)

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

    with col3:
        st.subheader("Parquet Export")
        try:
            from lavendertown.export.parquet import export_findings_to_parquet_bytes

            compression = st.selectbox(
                "Compression",
                options=["snappy", "gzip", "brotli", "zstd", "lz4"],
                index=0,
                help="Compression codec for Parquet file",
                key="parquet_compression",
            )

            parquet_bytes = export_findings_to_parquet_bytes(
                findings, compression=compression
            )
            st.download_button(
                label="📥 Download Parquet",
                data=parquet_bytes,
                file_name=f"findings_{compression}.parquet",
                mime="application/octet-stream",
                help="Download findings in Parquet format (efficient for large datasets)",
            )
        except ImportError:
            st.info(
                "📦 Install PyArrow to export Parquet: pip install lavendertown[parquet]"
            )

    # Show preview
    with st.expander("Preview Export"):
        preview_tabs = ["JSON Preview", "CSV Preview"]
        try:
            from lavendertown.export.parquet import export_findings_to_parquet_bytes

            preview_tabs.append("Parquet Info")
        except ImportError:
            pass

        tabs = st.tabs(preview_tabs)

        with tabs[0]:
            st.code(
                json_str[:1000] + "..." if len(json_str) > 1000 else json_str,
                language="json",
            )

        with tabs[1]:
            st.code(
                csv_str[:1000] + "..." if len(csv_str) > 1000 else csv_str,
                language="csv",
            )

        if len(tabs) > 2:
            with tabs[2]:
                try:
                    from lavendertown.export.parquet import (
                        export_findings_to_parquet_bytes,
                    )

                    compression = st.session_state.get("parquet_compression", "snappy")
                    parquet_bytes = export_findings_to_parquet_bytes(
                        findings, compression=compression
                    )
                    st.info(
                        f"✅ Parquet file size: {len(parquet_bytes) / 1024:.2f} KB "
                        f"(compression: {compression})"
                    )
                    st.caption(
                        "Parquet is a columnar format optimized for analytics workloads"
                    )
                except ImportError:
                    pass

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

    # Profiling report section
    st.divider()
    st.header("📊 Data Profiling Report")

    try:
        from lavendertown.profiling import generate_profiling_report_html

        if "df" in st.session_state:
            df = st.session_state["df"]

            col1, col2 = st.columns(2)
            with col1:
                report_title = st.text_input(
                    "Report Title",
                    value="Data Profiling Report",
                    key="profiling_title",
                )
            with col2:
                minimal_mode = st.checkbox(
                    "Minimal Mode (faster)",
                    value=False,
                    help="Generate a faster, minimal report",
                    key="profiling_minimal",
                )

            # Generate and download report
            if st.button("Generate Profiling Report", key="generate_profile"):
                with st.spinner("Generating profiling report..."):
                    try:
                        html_content = generate_profiling_report_html(
                            df, minimal=minimal_mode, title=report_title
                        )
                        st.download_button(
                            label="📥 Download Profiling Report",
                            data=html_content,
                            file_name="profiling_report.html",
                            mime="text/html",
                            help="Download comprehensive data profiling report",
                        )
                        st.success("✅ Profiling report generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating report: {e}")
        else:
            st.info("Upload data first to generate a profiling report.")
    except ImportError:
        st.info(
            "📦 Install ydata-profiling to generate profiling reports: "
            "pip install lavendertown[profiling]"
        )
