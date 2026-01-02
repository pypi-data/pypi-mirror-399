"""UI components for collaboration features."""

from __future__ import annotations

from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    export_report,
    get_annotations,
)
from lavendertown.collaboration.storage import get_finding_id
from lavendertown.models import GhostFinding
from lavendertown.rules.models import RuleSet


def render_annotation_panel(
    st: object, finding: GhostFinding, author: str = "User"
) -> None:
    """Render UI for viewing and adding annotations to a finding.

    Args:
        st: Streamlit module.
        finding: Finding to display annotations for.
        author: Name of the current user.
    """
    st.subheader("Annotations")

    finding_id = get_finding_id(finding)
    annotations = get_annotations(finding)

    # Display existing annotations
    if annotations:
        for annotation in annotations:
            with st.expander(
                f"💬 {annotation.author} - {annotation.timestamp.strftime('%Y-%m-%d %H:%M')}"
            ):
                st.write(annotation.comment)
                if annotation.tags:
                    st.write(f"**Tags:** {', '.join(annotation.tags)}")
                if annotation.status:
                    status_colors = {
                        "reviewed": "🟢",
                        "fixed": "✅",
                        "false_positive": "🔴",
                    }
                    st.write(
                        f"**Status:** {status_colors.get(annotation.status, '')} {annotation.status}"
                    )
    else:
        st.info("No annotations yet. Add one below.")

    # Add new annotation
    with st.form(f"add_annotation_{finding_id}"):
        comment = st.text_area("Add Comment", placeholder="Enter your comment here...")
        tags_str = st.text_input(
            "Tags (comma-separated)", placeholder="e.g., data-entry, needs-review"
        )
        status = st.selectbox(
            "Status",
            options=[None, "reviewed", "fixed", "false_positive"],
            format_func=lambda x: x or "None",
        )

        if st.form_submit_button("Add Annotation"):
            if comment:
                tags = (
                    [t.strip() for t in tags_str.split(",") if t.strip()]
                    if tags_str
                    else []
                )
                add_annotation(finding, author, comment, tags, status)
                st.success("Annotation added!")
                st.rerun()
            else:
                st.warning("Please enter a comment")


def render_share_panel(
    st: object,
    findings: list[GhostFinding],
    ruleset: RuleSet | None = None,
    author: str = "User",
) -> None:
    """Render UI for sharing reports.

    Args:
        st: Streamlit module.
        findings: List of findings to include in the report.
        ruleset: Optional ruleset used for analysis.
        author: Name of the current user.
    """
    st.subheader("Share Report")

    title = st.text_input("Report Title", placeholder="e.g., Q4 Data Quality Report")
    metadata_text = st.text_area(
        "Additional Notes (optional)", placeholder="Add any additional context..."
    )

    if st.button("Export Report", type="primary"):
        if title:
            metadata = {}
            if metadata_text:
                metadata["notes"] = metadata_text

            report = create_shareable_report(
                title=title,
                author=author,
                findings=findings,
                ruleset=ruleset,
                metadata=metadata,
            )

            report_path = export_report(report)
            st.success(f"Report exported to: {report_path}")

            # Provide download
            with open(report_path, "rb") as f:
                st.download_button(
                    "Download Report",
                    f.read(),
                    file_name=f"{title.replace(' ', '_')}.json",
                    mime="application/json",
                )
        else:
            st.warning("Please enter a report title")
