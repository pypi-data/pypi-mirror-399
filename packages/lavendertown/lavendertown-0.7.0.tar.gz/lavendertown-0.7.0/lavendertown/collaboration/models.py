"""Collaboration data models for annotations and shareable reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lavendertown.models import GhostFinding
from lavendertown.rules.models import RuleSet


@dataclass
class Annotation:
    """Represents an annotation (comment) on a finding.

    Annotations allow users to add comments, tags, and status updates to
    individual findings. They support collaboration by enabling team members
    to discuss and track the resolution of data quality issues.

    Attributes:
        id: Unique identifier for the annotation.
        finding_id: ID of the finding this annotation is attached to.
            Typically a hash of finding attributes.
        author: Name or identifier of the person who created the annotation.
        timestamp: When the annotation was created.
        comment: Text content of the annotation.
        tags: List of tags for categorizing the annotation.
        status: Optional status update. Valid values: "reviewed", "fixed",
            "false_positive", or None.

    Example:
        Create an annotation::

            annotation = Annotation(
                id="ann_123",
                finding_id="finding_456",
                author="Alice",
                timestamp=datetime.now(),
                comment="This looks like a data entry error",
                tags=["data-entry", "needs-review"],
                status="reviewed"
            )
    """

    id: str
    finding_id: str
    author: str
    timestamp: datetime
    comment: str
    tags: list[str] = field(default_factory=list)
    status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert annotation to dictionary for serialization.

        Returns:
            Dictionary containing all annotation attributes.
        """
        return {
            "id": self.id,
            "finding_id": self.finding_id,
            "author": self.author,
            "timestamp": self.timestamp.isoformat(),
            "comment": self.comment,
            "tags": self.tags,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Annotation":
        """Create annotation from dictionary.

        Args:
            data: Dictionary containing annotation data.

        Returns:
            Annotation instance initialized with data from the dictionary.
        """
        return cls(
            id=data["id"],
            finding_id=data["finding_id"],
            author=data["author"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            comment=data["comment"],
            tags=data.get("tags", []),
            status=data.get("status"),
        )


@dataclass
class ShareableReport:
    """Represents a shareable report containing findings, annotations, and rulesets.

    Shareable reports allow users to export and share their data quality
    analysis results with team members. Reports include findings, annotations,
    and optionally the ruleset used for analysis.

    Attributes:
        id: Unique identifier for the report.
        title: Human-readable title for the report.
        author: Name or identifier of the person who created the report.
        created_at: When the report was created.
        findings: List of GhostFinding objects in the report.
        annotations: List of Annotation objects associated with findings.
        ruleset: Optional RuleSet used for the analysis.
        metadata: Additional metadata about the report (e.g., dataset name,
            analysis date, etc.).

    Example:
        Create a shareable report::

            report = ShareableReport(
                id="report_123",
                title="Q4 Data Quality Report",
                author="Alice",
                created_at=datetime.now(),
                findings=[finding1, finding2],
                annotations=[annotation1],
                ruleset=my_ruleset,
                metadata={"dataset": "sales_data.csv"}
            )
    """

    id: str
    title: str
    author: str
    created_at: datetime
    findings: list[GhostFinding] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    ruleset: RuleSet | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for serialization.

        Returns:
            Dictionary containing all report attributes.
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "findings": [f.to_dict() for f in self.findings],
            "annotations": [a.to_dict() for a in self.annotations],
            "ruleset": self.ruleset.to_dict() if self.ruleset else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ShareableReport":
        """Create report from dictionary.

        Args:
            data: Dictionary containing report data.

        Returns:
            ShareableReport instance initialized with data from the dictionary.
        """
        from lavendertown.models import GhostFinding
        from lavendertown.rules.models import RuleSet

        return cls(
            id=data["id"],
            title=data["title"],
            author=data["author"],
            created_at=datetime.fromisoformat(data["created_at"]),
            findings=[GhostFinding.from_dict(f) for f in data.get("findings", [])],
            annotations=[Annotation.from_dict(a) for a in data.get("annotations", [])],
            ruleset=RuleSet.from_dict(data["ruleset"]) if data.get("ruleset") else None,
            metadata=data.get("metadata", {}),
        )
