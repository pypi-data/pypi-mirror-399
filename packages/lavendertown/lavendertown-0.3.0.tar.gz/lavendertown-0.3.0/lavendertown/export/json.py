"""JSON exporter for ghost findings."""

from __future__ import annotations

import json

from lavendertown.models import GhostFinding


def export_to_json(findings: list[GhostFinding], indent: int = 2) -> str:
    """Export findings to JSON format.

    Args:
        findings: List of GhostFinding objects to export
        indent: JSON indentation level (default: 2)

    Returns:
        JSON string representation of findings
    """
    findings_dict = {
        "findings": [f.to_dict() for f in findings],
        "summary": {
            "total_findings": len(findings),
            "by_type": _count_by_type(findings),
            "by_severity": _count_by_severity(findings),
        },
    }

    return json.dumps(findings_dict, indent=indent, default=str)


def export_to_json_file(
    findings: list[GhostFinding], filepath: str, indent: int = 2
) -> None:
    """Export findings to a JSON file.

    Args:
        findings: List of GhostFinding objects to export
        filepath: Path to output JSON file
        indent: JSON indentation level (default: 2)
    """
    json_str = export_to_json(findings, indent=indent)

    with open(filepath, "w") as f:
        f.write(json_str)


def _count_by_type(findings: list[GhostFinding]) -> dict[str, int]:
    """Count findings by ghost type."""
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.ghost_type] = counts.get(finding.ghost_type, 0) + 1
    return counts


def _count_by_severity(findings: list[GhostFinding]) -> dict[str, int]:
    """Count findings by severity level."""
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts
