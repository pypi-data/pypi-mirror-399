"""File-based storage for annotations and shareable reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from lavendertown.collaboration.models import Annotation, ShareableReport
from lavendertown.models import GhostFinding


def _get_finding_id(finding: GhostFinding) -> str:
    """Generate a unique ID for a finding.

    Args:
        finding: GhostFinding to generate ID for.

    Returns:
        Unique string ID based on finding attributes.
    """
    # Create hash from key attributes
    key = f"{finding.ghost_type}:{finding.column}:{finding.description}"
    return hashlib.md5(key.encode()).hexdigest()


def _get_storage_dir() -> Path:
    """Get the storage directory for collaboration data.

    Returns:
        Path to .lavendertown directory in current working directory.
    """
    storage_dir = Path.cwd() / ".lavendertown"
    storage_dir.mkdir(exist_ok=True)
    (storage_dir / "annotations").mkdir(exist_ok=True)
    (storage_dir / "reports").mkdir(exist_ok=True)
    (storage_dir / "shared_rulesets").mkdir(exist_ok=True)
    return storage_dir


def save_annotation(annotation: Annotation) -> None:
    """Save an annotation to disk.

    Args:
        annotation: Annotation to save.
    """
    storage_dir = _get_storage_dir()
    annotation_file = storage_dir / "annotations" / f"{annotation.finding_id}.json"

    # Load existing annotations for this finding
    annotations = []
    if annotation_file.exists():
        with open(annotation_file, "r") as f:
            annotations = json.load(f)

    # Add new annotation
    annotations.append(annotation.to_dict())

    # Save back
    with open(annotation_file, "w") as f:
        json.dump(annotations, f, indent=2)


def load_annotations(finding_id: str) -> list[Annotation]:
    """Load annotations for a finding.

    Args:
        finding_id: ID of the finding to load annotations for.

    Returns:
        List of Annotation objects for the finding.
    """
    storage_dir = _get_storage_dir()
    annotation_file = storage_dir / "annotations" / f"{finding_id}.json"

    if not annotation_file.exists():
        return []

    with open(annotation_file, "r") as f:
        annotations_data = json.load(f)

    return [Annotation.from_dict(a) for a in annotations_data]


def save_report(report: ShareableReport, filepath: str | None = None) -> Path:
    """Save a shareable report to disk.

    Args:
        report: ShareableReport to save.
        filepath: Optional path to save the report. If None, saves to
            .lavendertown/reports/ directory.

    Returns:
        Path where the report was saved.
    """
    if filepath:
        report_path = Path(filepath)
    else:
        storage_dir = _get_storage_dir()
        report_path = storage_dir / "reports" / f"{report.id}.json"

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    return report_path


def load_report(filepath: str) -> ShareableReport:
    """Load a shareable report from disk.

    Args:
        filepath: Path to the report JSON file.

    Returns:
        ShareableReport instance loaded from the file.
    """
    with open(filepath, "r") as f:
        report_data = json.load(f)

    return ShareableReport.from_dict(report_data)


def get_finding_id(finding: GhostFinding) -> str:
    """Get or generate ID for a finding.

    Args:
        finding: GhostFinding to get ID for.

    Returns:
        Unique string ID for the finding.
    """
    return _get_finding_id(finding)
