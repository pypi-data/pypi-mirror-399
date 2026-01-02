"""JSON exporter for ghost findings."""

from __future__ import annotations

try:
    import orjson
except ImportError:
    orjson = None  # type: ignore[assignment,misc]

import json
from pathlib import Path

from lavendertown.models import GhostFinding


def export_to_json(findings: list[GhostFinding], indent: int = 2) -> str:
    """Export findings to JSON format.

    Uses orjson if available for faster serialization, falls back to
    standard library json otherwise.

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

    if orjson is not None and indent == 2:
        # orjson only supports 2-space indentation natively
        json_bytes = orjson.dumps(
            findings_dict, option=orjson.OPT_INDENT_2, default=str
        )
        return json_bytes.decode("utf-8")
    else:
        # Fall back to standard library json for non-2 indent or if orjson unavailable
        return json.dumps(findings_dict, indent=indent, default=str)


def export_to_json_file(
    findings: list[GhostFinding], filepath: str, indent: int = 2
) -> None:
    """Export findings to a JSON file.

    Uses orjson if available for faster serialization, falls back to
    standard library json otherwise.

    Args:
        findings: List of GhostFinding objects to export
        filepath: Path to output JSON file
        indent: JSON indentation level (default: 2)
    """
    if orjson is not None and indent == 2:
        # Use orjson for faster serialization
        findings_dict = {
            "findings": [f.to_dict() for f in findings],
            "summary": {
                "total_findings": len(findings),
                "by_type": _count_by_type(findings),
                "by_severity": _count_by_severity(findings),
            },
        }
        option = orjson.OPT_INDENT_2
        json_bytes = orjson.dumps(findings_dict, option=option, default=str)
        with open(filepath, "wb") as f:
            f.write(json_bytes)
        return

    # Fall back to standard library json
    json_str = export_to_json(findings, indent=indent)
    Path(filepath).write_text(json_str, encoding="utf-8")


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
