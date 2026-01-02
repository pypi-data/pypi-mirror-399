"""Core data models for ghost findings.

This module defines the GhostFinding dataclass, which represents a single
data quality issue detected in a dataset. GhostFindings contain information
about the type of issue, affected column, severity level, description,
and optionally the specific row indices affected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GhostFinding:
    """Represents a single data quality issue (ghost) detected in a dataset.

    GhostFindings are the primary output of data quality detectors. They
    encapsulate all information about a detected issue in a structured format
    that can be displayed in the UI, exported to various formats, or processed
    programmatically.

    Attributes:
        ghost_type: Category of the ghost/issue. Common types include:
            - "null": Excessive null values
            - "type": Type inconsistencies
            - "outlier": Statistical outliers
            - "drift": Schema or distribution drift
            - "rule": Custom rule violations
        column: Name of the affected column. Empty string for issues that
            don't relate to a specific column.
        severity: Severity level of the issue. Valid values:
            - "info": Informational, minor issue
            - "warning": Warning-level issue that may need attention
            - "error": Error-level issue requiring immediate attention
        description: Human-readable description of the issue, suitable for
            display in UI or reports.
        row_indices: Optional list of row indices (0-based) affected by the
            issue. None if specific row indices are not available or not
            applicable. For Polars DataFrames, this may often be None as
            Polars doesn't maintain index concepts.
        metadata: Additional context information as key-value pairs.
            Contains detector-specific metadata such as statistics, thresholds,
            or diagnostic information. Empty dict by default.

    Example:
        Create a finding manually::

            finding = GhostFinding(
                ghost_type="null",
                column="email",
                severity="warning",
                description="Column 'email' has 15 null values (25% of 60 rows)",
                row_indices=[2, 5, 8, 12, 15],
                metadata={"null_count": 15, "null_percentage": 0.25}
            )

        Convert to/from dict for serialization::

            # Serialize
            data = finding.to_dict()

            # Deserialize
            finding = GhostFinding.from_dict(data)
    """

    ghost_type: str
    column: str
    severity: str
    description: str
    row_indices: list[int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate severity values after initialization.

        Ensures that the severity attribute is one of the valid values.
        Called automatically by the dataclass decorator after initialization.

        Raises:
            ValueError: If severity is not one of "info", "warning", or "error".
        """
        valid_severities = {"info", "warning", "error"}
        if self.severity not in valid_severities:
            raise ValueError(
                f"Severity must be one of {valid_severities}, got {self.severity}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert finding to dictionary for serialization.

        Converts the GhostFinding instance to a dictionary representation
        suitable for JSON serialization or caching. All fields are included
        in the dictionary.

        Returns:
            Dictionary containing all finding attributes. Keys match the
            dataclass field names: "ghost_type", "column", "severity",
            "description", "row_indices", and "metadata".

        Example:
            Serialize for JSON export::

                import json
                finding = GhostFinding(...)
                data = finding.to_dict()
                json_str = json.dumps(data)
        """
        return {
            "ghost_type": self.ghost_type,
            "column": self.column,
            "severity": self.severity,
            "description": self.description,
            "row_indices": self.row_indices,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GhostFinding":
        """Create finding from dictionary.

        Deserializes a dictionary back into a GhostFinding instance.
        Used for loading findings from JSON files or retrieving cached
        findings from Streamlit's cache.

        Args:
            data: Dictionary containing finding data. Must include the
                required fields: "ghost_type", "column", "severity", and
                "description". Optional fields "row_indices" and "metadata"
                will use defaults if not present.

        Returns:
            GhostFinding instance initialized with data from the dictionary.

        Raises:
            ValueError: If required fields ("ghost_type", "column", "severity",
                "description") are missing from the dictionary.

        Example:
            Deserialize from JSON::

                import json
                json_str = '{"ghost_type": "null", "column": "email", ...}'
                data = json.loads(json_str)
                finding = GhostFinding.from_dict(data)
        """
        required_fields = ["ghost_type", "column", "severity", "description"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(
                f"Missing required fields in GhostFinding data: {', '.join(missing_fields)}"
            )
        return cls(
            ghost_type=data["ghost_type"],
            column=data["column"],
            severity=data["severity"],
            description=data["description"],
            row_indices=data.get("row_indices"),
            metadata=data.get("metadata", {}),
        )
