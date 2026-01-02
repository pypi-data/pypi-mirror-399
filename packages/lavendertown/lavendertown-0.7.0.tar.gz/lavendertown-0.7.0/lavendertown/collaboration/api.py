"""API functions for collaboration features."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from lavendertown.collaboration.models import Annotation, ShareableReport
from lavendertown.collaboration.storage import (
    get_finding_id,
    load_annotations,
    load_report,
    save_annotation,
    save_report,
)
from lavendertown.models import GhostFinding
from lavendertown.rules.models import RuleSet


def add_annotation(
    finding: GhostFinding,
    author: str,
    comment: str,
    tags: list[str] | None = None,
    status: str | None = None,
) -> Annotation:
    """Add an annotation to a finding.

    Args:
        finding: Finding to annotate.
        author: Name of the person creating the annotation.
        comment: Comment text.
        tags: Optional list of tags.
        status: Optional status update ("reviewed", "fixed", "false_positive").

    Returns:
        Created Annotation instance.
    """
    finding_id = get_finding_id(finding)

    annotation = Annotation(
        id=str(uuid.uuid4()),
        finding_id=finding_id,
        author=author,
        timestamp=datetime.now(),
        comment=comment,
        tags=tags or [],
        status=status,
    )

    save_annotation(annotation)
    return annotation


def get_annotations(finding: GhostFinding) -> list[Annotation]:
    """Get all annotations for a finding.

    Args:
        finding: Finding to get annotations for.

    Returns:
        List of Annotation objects for the finding.
    """
    finding_id = get_finding_id(finding)
    return load_annotations(finding_id)


def create_shareable_report(
    title: str,
    author: str,
    findings: list[GhostFinding],
    annotations: list[Annotation] | None = None,
    ruleset: RuleSet | None = None,
    metadata: dict[str, Any] | None = None,
) -> ShareableReport:
    """Create a shareable report.

    Args:
        title: Report title.
        author: Name of the person creating the report.
        findings: List of findings to include.
        annotations: Optional list of annotations to include.
        ruleset: Optional ruleset used for analysis.
        metadata: Optional additional metadata.

    Returns:
        Created ShareableReport instance.
    """
    import uuid

    report = ShareableReport(
        id=str(uuid.uuid4()),
        title=title,
        author=author,
        created_at=datetime.now(),
        findings=findings,
        annotations=annotations or [],
        ruleset=ruleset,
        metadata=metadata or {},
    )

    return report


def export_report(report: ShareableReport, filepath: str | None = None) -> Path:
    """Export a shareable report to a file.

    Args:
        report: Report to export.
        filepath: Optional path to save the report. If None, saves to
            default reports directory.

    Returns:
        Path where the report was saved.
    """
    return save_report(report, filepath)


def import_report(filepath: str) -> ShareableReport:
    """Import a shareable report from a file.

    Args:
        filepath: Path to the report JSON file.

    Returns:
        ShareableReport instance loaded from the file.
    """
    return load_report(filepath)
