"""CSV exporter for ghost findings."""

from __future__ import annotations

import csv
from io import StringIO

from lavendertown.models import GhostFinding


def export_to_csv(findings: list[GhostFinding]) -> str:
    """Export findings to CSV format (flattened for analyst-friendly viewing).

    Args:
        findings: List of GhostFinding objects to export

    Returns:
        CSV string representation of findings
    """
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "ghost_type",
            "column",
            "severity",
            "description",
            "row_count",
            "metadata_json",
        ]
    )

    # Write rows
    for finding in findings:
        row_count = len(finding.row_indices) if finding.row_indices else 0

        # Serialize metadata to JSON string
        import json

        metadata_json = (
            json.dumps(finding.metadata, default=str) if finding.metadata else ""
        )

        writer.writerow(
            [
                finding.ghost_type,
                finding.column,
                finding.severity,
                finding.description,
                row_count,
                metadata_json,
            ]
        )

    return output.getvalue()


def export_to_csv_file(findings: list[GhostFinding], filepath: str) -> None:
    """Export findings to a CSV file.

    Args:
        findings: List of GhostFinding objects to export
        filepath: Path to output CSV file
    """
    csv_str = export_to_csv(findings)

    with open(filepath, "w", newline="") as f:
        f.write(csv_str)


def export_summary_to_csv(findings: list[GhostFinding]) -> str:
    """Export summary statistics to CSV format.

    Args:
        findings: List of GhostFinding objects

    Returns:
        CSV string with summary statistics
    """
    output = StringIO()
    writer = csv.writer(output)

    # Write summary header
    writer.writerow(["metric", "value"])

    # Total findings
    writer.writerow(["total_findings", len(findings)])

    # By type
    type_counts: dict[str, int] = {}
    for finding in findings:
        type_counts[finding.ghost_type] = type_counts.get(finding.ghost_type, 0) + 1

    for ghost_type, count in sorted(type_counts.items()):
        writer.writerow([f"type_{ghost_type}", count])

    # By severity
    severity_counts: dict[str, int] = {}
    for finding in findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

    for severity, count in sorted(severity_counts.items()):
        writer.writerow([f"severity_{severity}", count])

    # By column
    column_counts: dict[str, int] = {}
    for finding in findings:
        column_counts[finding.column] = column_counts.get(finding.column, 0) + 1

    for column, count in sorted(column_counts.items()):
        writer.writerow([f"column_{column}", count])

    return output.getvalue()


def export_summary_to_csv_file(findings: list[GhostFinding], filepath: str) -> None:
    """Export summary statistics to a CSV file.

    Args:
        findings: List of GhostFinding objects
        filepath: Path to output CSV file
    """
    csv_str = export_summary_to_csv(findings)

    with open(filepath, "w", newline="") as f:
        f.write(csv_str)
