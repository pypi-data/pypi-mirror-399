"""Tests for collaboration features."""

from __future__ import annotations

import tempfile
from pathlib import Path


from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    export_report,
    get_annotations,
    import_report,
)
from lavendertown.collaboration.models import Annotation, ShareableReport
from lavendertown.collaboration.storage import get_finding_id
from lavendertown.models import GhostFinding
from lavendertown.rules.models import Rule, RuleSet


class TestAnnotation:
    """Test Annotation model."""

    def test_annotation_creation(self):
        """Test creating an Annotation."""
        from datetime import datetime

        annotation = Annotation(
            id="ann_1",
            finding_id="finding_1",
            author="Alice",
            timestamp=datetime.now(),
            comment="This is a test comment",
            tags=["test", "review"],
            status="reviewed",
        )

        assert annotation.id == "ann_1"
        assert annotation.finding_id == "finding_1"
        assert annotation.author == "Alice"
        assert annotation.comment == "This is a test comment"
        assert annotation.tags == ["test", "review"]
        assert annotation.status == "reviewed"

    def test_annotation_serialization(self):
        """Test Annotation serialization."""
        from datetime import datetime

        annotation = Annotation(
            id="ann_1",
            finding_id="finding_1",
            author="Alice",
            timestamp=datetime.now(),
            comment="Test comment",
        )

        annotation_dict = annotation.to_dict()
        assert annotation_dict["id"] == "ann_1"
        assert annotation_dict["comment"] == "Test comment"

        restored = Annotation.from_dict(annotation_dict)
        assert restored.id == annotation.id
        assert restored.comment == annotation.comment


class TestShareableReport:
    """Test ShareableReport model."""

    def test_report_creation(self):
        """Test creating a ShareableReport."""
        from datetime import datetime

        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = ShareableReport(
            id="report_1",
            title="Test Report",
            author="Alice",
            created_at=datetime.now(),
            findings=[finding],
        )

        assert report.id == "report_1"
        assert report.title == "Test Report"
        assert len(report.findings) == 1

    def test_report_serialization(self):
        """Test ShareableReport serialization."""
        from datetime import datetime

        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = ShareableReport(
            id="report_1",
            title="Test Report",
            author="Alice",
            created_at=datetime.now(),
            findings=[finding],
        )

        report_dict = report.to_dict()
        assert report_dict["id"] == "report_1"
        assert len(report_dict["findings"]) == 1

        restored = ShareableReport.from_dict(report_dict)
        assert restored.id == report.id
        assert len(restored.findings) == 1


class TestCollaborationAPI:
    """Test collaboration API functions."""

    def test_add_and_get_annotations(self):
        """Test adding and retrieving annotations."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        # Add annotation
        annotation = add_annotation(
            finding,
            author="Alice",
            comment="This needs review",
            tags=["review"],
            status="reviewed",
        )

        assert annotation.author == "Alice"
        assert annotation.comment == "This needs review"

        # Get annotations
        annotations = get_annotations(finding)
        assert len(annotations) > 0
        assert annotations[0].comment == "This needs review"

    def test_create_shareable_report(self):
        """Test creating a shareable report."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = create_shareable_report(
            title="Test Report",
            author="Alice",
            findings=[finding],
        )

        assert report.title == "Test Report"
        assert len(report.findings) == 1

    def test_export_and_import_report(self):
        """Test exporting and importing a report."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = create_shareable_report(
            title="Test Report",
            author="Alice",
            findings=[finding],
        )

        # Export
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            export_report(report, str(report_path))

            assert report_path.exists()

            # Import
            imported_report = import_report(str(report_path))

            assert imported_report.title == report.title
            assert len(imported_report.findings) == 1

    def test_get_finding_id(self):
        """Test getting finding ID."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        finding_id = get_finding_id(finding)
        assert isinstance(finding_id, str)
        assert len(finding_id) > 0

        # Same finding should have same ID
        finding_id2 = get_finding_id(finding)
        assert finding_id == finding_id2

    def test_multiple_annotations_same_finding(self):
        """Test adding multiple annotations to the same finding."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        # Add multiple annotations
        add_annotation(finding, "Alice", "First comment", ["tag1"])
        add_annotation(finding, "Bob", "Second comment", ["tag2"])
        add_annotation(finding, "Charlie", "Third comment", ["tag3"], "reviewed")

        annotations = get_annotations(finding)
        assert len(annotations) >= 3

        # Check all annotations are present
        comments = [a.comment for a in annotations]
        assert "First comment" in comments
        assert "Second comment" in comments
        assert "Third comment" in comments

    def test_annotation_with_empty_tags(self):
        """Test annotation with empty tags list."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        annotation = add_annotation(finding, "Alice", "Comment", tags=[])
        assert annotation.tags == []

    def test_annotation_with_multiple_tags(self):
        """Test annotation with multiple tags."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        tags = ["data-entry", "needs-review", "urgent", "blocking"]
        annotation = add_annotation(finding, "Alice", "Comment", tags=tags)
        assert annotation.tags == tags

    def test_annotation_different_statuses(self):
        """Test annotations with different status values."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        statuses = ["reviewed", "fixed", "false_positive"]
        for status in statuses:
            annotation = add_annotation(
                finding, "Alice", f"Status: {status}", status=status
            )
            assert annotation.status == status

    def test_report_with_multiple_findings(self):
        """Test shareable report with multiple findings."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="email",
                severity="warning",
                description=f"Finding {i}",
            )
            for i in range(10)
        ]

        report = create_shareable_report(
            title="Multi-Finding Report",
            author="Alice",
            findings=findings,
        )

        assert len(report.findings) == 10

    def test_report_with_ruleset(self):
        """Test shareable report with ruleset."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        ruleset = RuleSet(
            name="Test Ruleset",
            description="Test",
            rules=[
                Rule(
                    name="test_rule",
                    description="Test rule",
                    rule_type="range",
                    column="email",
                    parameters={"min_value": 0},
                )
            ],
        )

        report = create_shareable_report(
            title="Report with Ruleset",
            author="Alice",
            findings=[finding],
            ruleset=ruleset,
        )

        assert report.ruleset is not None
        assert report.ruleset.name == "Test Ruleset"
        assert len(report.ruleset.rules) == 1

    def test_report_with_metadata(self):
        """Test shareable report with custom metadata."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        metadata = {
            "dataset": "sales_data.csv",
            "analysis_date": "2024-01-01",
            "version": "1.0",
            "custom_field": "custom_value",
        }

        report = create_shareable_report(
            title="Report with Metadata",
            author="Alice",
            findings=[finding],
            metadata=metadata,
        )

        assert report.metadata == metadata

    def test_report_serialization_roundtrip(self):
        """Test report serialization and deserialization preserves all data."""
        from datetime import datetime

        finding1 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Finding 1",
            metadata={"key1": "value1"},
        )
        finding2 = GhostFinding(
            ghost_type="outlier",
            column="price",
            severity="error",
            description="Finding 2",
            row_indices=[1, 2, 3],
        )

        annotation = Annotation(
            id="ann_1",
            finding_id="finding_1",
            author="Alice",
            timestamp=datetime.now(),
            comment="Test comment",
            tags=["tag1", "tag2"],
            status="reviewed",
        )

        ruleset = RuleSet(
            name="Test Ruleset",
            description="Test",
            rules=[
                Rule(
                    name="test_rule",
                    description="Test rule",
                    rule_type="range",
                    column="email",
                )
            ],
        )

        metadata = {"dataset": "test.csv", "version": "1.0"}

        original_report = ShareableReport(
            id="report_1",
            title="Test Report",
            author="Alice",
            created_at=datetime.now(),
            findings=[finding1, finding2],
            annotations=[annotation],
            ruleset=ruleset,
            metadata=metadata,
        )

        # Serialize and deserialize
        report_dict = original_report.to_dict()
        restored_report = ShareableReport.from_dict(report_dict)

        assert restored_report.id == original_report.id
        assert restored_report.title == original_report.title
        assert len(restored_report.findings) == 2
        assert len(restored_report.annotations) == 1
        assert restored_report.ruleset is not None
        assert restored_report.metadata == metadata

    def test_export_report_custom_path(self):
        """Test exporting report to custom path."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = create_shareable_report(
            title="Custom Path Report",
            author="Alice",
            findings=[finding],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom_report.json"
            export_report(report, str(custom_path))

            assert custom_path.exists()

            # Verify it can be imported
            imported = import_report(str(custom_path))
            assert imported.title == "Custom Path Report"

    def test_finding_id_consistency(self):
        """Test that finding IDs are consistent across different instances."""
        finding1 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        finding2 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        # Same attributes should produce same ID
        id1 = get_finding_id(finding1)
        id2 = get_finding_id(finding2)
        assert id1 == id2

    def test_finding_id_different_findings(self):
        """Test that different findings produce different IDs."""
        finding1 = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Finding 1",
        )

        finding2 = GhostFinding(
            ghost_type="outlier",
            column="price",
            severity="error",
            description="Finding 2",
        )

        id1 = get_finding_id(finding1)
        id2 = get_finding_id(finding2)
        assert id1 != id2

    def test_report_with_empty_findings(self):
        """Test report with no findings."""
        report = create_shareable_report(
            title="Empty Report",
            author="Alice",
            findings=[],
        )

        assert len(report.findings) == 0
        assert report.title == "Empty Report"

    def test_report_with_empty_annotations(self):
        """Test report with no annotations."""
        finding = GhostFinding(
            ghost_type="null",
            column="email",
            severity="warning",
            description="Test finding",
        )

        report = create_shareable_report(
            title="Report No Annotations",
            author="Alice",
            findings=[finding],
            annotations=[],
        )

        assert len(report.annotations) == 0
        assert len(report.findings) == 1
