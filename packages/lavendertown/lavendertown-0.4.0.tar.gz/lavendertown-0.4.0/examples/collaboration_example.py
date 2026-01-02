"""Collaboration features example.

This example demonstrates how to use LavenderTown's collaboration features
for annotating findings and creating shareable reports.
"""

import pandas as pd
import streamlit as st

from lavendertown import Inspector
from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    export_report,
    get_annotations,
    import_report,
)

st.title("Collaboration Features Example")

st.markdown(
    """
    This example shows how to use LavenderTown's collaboration features:
    - **Annotations**: Add comments and tags to findings
    - **Shareable Reports**: Create and export reports for team sharing
    - **Status Tracking**: Mark findings as reviewed, fixed, or false positive
    """
)

# Create sample data
data = {
    "product_id": [1, 2, 3, 4, 5],
    "price": [10.99, None, 45.00, -5.00, 100.00],
    "quantity": [100, 50, None, 200, 0],
    "category": ["A", "B", "A", "C", "A"],
}

df = pd.DataFrame(data)

# Display the data
st.subheader("Sample Data")
st.dataframe(df)

# Create inspector and get findings
st.subheader("Data Quality Analysis")
inspector = Inspector(df)
findings = inspector.detect()

if findings:
    st.markdown(f"### Found {len(findings)} Issues")

    # Collaboration features
    st.markdown("---")
    st.subheader("Collaboration Features")

    # Select a finding to annotate
    finding_options = {f"{f.column} - {f.description[:50]}...": f for f in findings}
    selected_finding_label = st.selectbox(
        "Select a finding to annotate",
        options=list(finding_options.keys()),
    )
    selected_finding = finding_options[selected_finding_label]

    # Annotation form
    with st.expander("Add Annotation", expanded=True):
        author = st.text_input("Author", value="Data Team")
        comment = st.text_area("Comment", placeholder="Add your comment here...")
        tags = st.text_input(
            "Tags (comma-separated)", placeholder="bug, critical, needs-review"
        )
        status = st.selectbox(
            "Status",
            [None, "reviewed", "fixed", "false_positive", "needs-investigation"],
        )

        if st.button("Add Annotation"):
            if comment:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                annotation = add_annotation(
                    selected_finding,
                    author=author,
                    comment=comment,
                    tags=tag_list,
                    status=status,
                )
                st.success(f"✅ Annotation added by {annotation.author}")
                st.json(annotation.to_dict())
            else:
                st.error("Please enter a comment")

    # View annotations
    st.markdown("### Existing Annotations")
    annotations = get_annotations(selected_finding)

    if annotations:
        for ann in annotations:
            with st.expander(
                f"💬 {ann.author} - {ann.timestamp.strftime('%Y-%m-%d %H:%M')}"
            ):
                st.write(f"**Comment:** {ann.comment}")
                if ann.tags:
                    st.write(f"**Tags:** {', '.join(ann.tags)}")
                if ann.status:
                    st.write(f"**Status:** {ann.status}")
    else:
        st.info("No annotations yet. Add one above!")

    # Create shareable report
    st.markdown("---")
    st.subheader("Create Shareable Report")

    report_title = st.text_input("Report Title", value="Data Quality Report")
    report_author = st.text_input("Report Author", value="Data Team")

    if st.button("Create Shareable Report"):
        # Get all annotations for all findings
        all_annotations = []
        for finding in findings:
            anns = get_annotations(finding)
            all_annotations.extend(anns)

        report = create_shareable_report(
            title=report_title,
            author=report_author,
            findings=findings,
            annotations=all_annotations if all_annotations else None,
        )
        st.success(f"✅ Report created: {report.id}")

        # Export report
        report_path = export_report(report)
        st.info(f"📄 Report saved to: {report_path}")

        # Show report details
        with st.expander("View Report Details"):
            st.write(f"**Title:** {report.title}")
            st.write(f"**Author:** {report.author}")
            st.write(f"**Created:** {report.created_at}")
            st.write(f"**Findings:** {len(report.findings)}")
            st.write(f"**Annotations:** {len(report.annotations)}")
            st.json(report.to_dict())

    # Import report
    st.markdown("---")
    st.subheader("Import Shareable Report")

    report_file = st.file_uploader(
        "Upload a report file (.json)",
        type=["json"],
        help="Upload a previously exported report file",
    )

    if report_file:
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(json.load(report_file), f)
            temp_path = f.name

        try:
            imported_report = import_report(temp_path)
            st.success(f"✅ Report imported: {imported_report.title}")

            with st.expander("View Imported Report"):
                st.write(f"**Title:** {imported_report.title}")
                st.write(f"**Author:** {imported_report.author}")
                st.write(f"**Created:** {imported_report.created_at}")
                st.write(f"**Findings:** {len(imported_report.findings)}")
                st.write(f"**Annotations:** {len(imported_report.annotations)}")
        except Exception as e:
            st.error(f"Error importing report: {e}")
else:
    st.info("No issues found in the data!")

st.info(
    "💡 **Tip:** Collaboration features help teams work together on data quality "
    "issues. Use annotations to discuss findings and shareable reports to "
    "communicate results with stakeholders."
)
