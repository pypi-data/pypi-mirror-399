"""Core data models for ghost findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GhostFinding:
    """Represents a single data quality issue (ghost) detected in a dataset.

    Attributes:
        ghost_type: Category of ghost (null, type, range, outlier, etc.)
        column: Name of the affected column
        severity: Severity level (info, warning, error)
        description: Human-readable description of the issue
        row_indices: Optional list of row indices affected
        metadata: Additional context information as key-value pairs
    """

    ghost_type: str
    column: str
    severity: str
    description: str
    row_indices: list[int] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate severity values."""
        valid_severities = {"info", "warning", "error"}
        if self.severity not in valid_severities:
            raise ValueError(
                f"Severity must be one of {valid_severities}, got {self.severity}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert finding to dictionary for serialization."""
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
        """Create finding from dictionary."""
        return cls(
            ghost_type=data["ghost_type"],
            column=data["column"],
            severity=data["severity"],
            description=data["description"],
            row_indices=data.get("row_indices"),
            metadata=data.get("metadata", {}),
        )
