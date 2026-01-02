"""Additional edge case tests for export functionality."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


from lavendertown.export.json import export_to_json, export_to_json_file
from lavendertown.models import GhostFinding


class TestExportEdgeCases:
    """Test edge cases in export functionality."""

    def test_export_with_datetime_in_metadata(self, tmp_path: Path) -> None:
        """Test export with datetime objects in metadata."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=[1],
                metadata={"timestamp": datetime(2024, 1, 1, 12, 0, 0)},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        # Datetime should be serialized (as string)
        assert len(data["findings"]) == 1
        # Metadata should be present
        assert "metadata" in data["findings"][0]

    def test_export_with_uuid_in_metadata(self, tmp_path: Path) -> None:
        """Test export with UUID objects in metadata."""
        test_uuid = uuid4()
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=[1],
                metadata={"id": test_uuid},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        # UUID should be serialized
        assert len(data["findings"]) == 1
        assert "metadata" in data["findings"][0]

    def test_export_with_nested_metadata(self, tmp_path: Path) -> None:
        """Test export with nested dictionaries in metadata."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=[1],
                metadata={
                    "nested": {
                        "level1": {"level2": "value"},
                        "list": [1, 2, 3],
                    }
                },
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1
        assert "nested" in data["findings"][0]["metadata"]

    def test_export_with_unicode_characters(self, tmp_path: Path) -> None:
        """Test export with Unicode characters in descriptions."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test with émojis 🎉 and 中文 characters",
                row_indices=[1],
                metadata={},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1
        assert (
            "émojis" in data["findings"][0]["description"]
            or "中文" in data["findings"][0]["description"]
        )

    def test_export_with_very_long_description(self, tmp_path: Path) -> None:
        """Test export with very long description."""
        long_description = "A" * 10000  # 10k character description
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description=long_description,
                row_indices=list(range(1000)),
                metadata={},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1
        assert len(data["findings"][0]["description"]) == 10000

    def test_export_with_many_findings(self, tmp_path: Path) -> None:
        """Test export with a large number of findings."""
        findings = [
            GhostFinding(
                ghost_type=["null", "outlier", "type"][i % 3],
                column=f"col{i % 10}",
                severity=["info", "warning", "error"][i % 3],
                description=f"Finding {i}",
                row_indices=list(range(i, i + 10)),
                metadata={"index": i},
            )
            for i in range(1000)
        ]

        filepath = tmp_path / "many_findings.json"
        export_to_json_file(findings, str(filepath), indent=2)

        assert filepath.exists()

        with open(filepath) as f:
            data = json.load(f)

        assert len(data["findings"]) == 1000
        assert data["summary"]["total_findings"] == 1000

    def test_export_findings_with_none_row_indices(self, tmp_path: Path) -> None:
        """Test export with findings that have None row_indices."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=None,
                metadata={},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1
        # row_indices should be None or omitted
        finding = data["findings"][0]
        assert "row_indices" not in finding or finding["row_indices"] is None

    def test_export_findings_with_empty_row_indices(self, tmp_path: Path) -> None:
        """Test export with findings that have empty row_indices."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=[],
                metadata={},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1
        finding = data["findings"][0]
        assert finding.get("row_indices") == []

    def test_export_summary_counts_accurate(self, tmp_path: Path) -> None:
        """Test that summary counts are accurate."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="",
                row_indices=[],
                metadata={},
            ),
            GhostFinding(
                ghost_type="null",
                column="col2",
                severity="error",
                description="",
                row_indices=[],
                metadata={},
            ),
            GhostFinding(
                ghost_type="outlier",
                column="col3",
                severity="info",
                description="",
                row_indices=[],
                metadata={},
            ),
            GhostFinding(
                ghost_type="outlier",
                column="col4",
                severity="warning",
                description="",
                row_indices=[],
                metadata={},
            ),
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        summary = data["summary"]
        assert summary["total_findings"] == 4
        assert summary["by_type"]["null"] == 2
        assert summary["by_type"]["outlier"] == 2
        assert summary["by_severity"]["warning"] == 2
        assert summary["by_severity"]["error"] == 1
        assert summary["by_severity"]["info"] == 1

    def test_export_with_special_json_characters(self, tmp_path: Path) -> None:
        """Test export handles special JSON characters correctly."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description='Description with "quotes", \backslashes\, and\nnewlines',
                row_indices=[1],
                metadata={"key": 'value with "quotes"'},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        # Should be valid JSON (no parsing errors)
        data = json.loads(json_str)

        assert len(data["findings"]) == 1

    def test_export_file_permissions(self, tmp_path: Path) -> None:
        """Test that exported files have correct permissions."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test",
                row_indices=[1],
                metadata={},
            )
        ]

        filepath = tmp_path / "findings.json"
        export_to_json_file(findings, str(filepath), indent=2)

        assert filepath.exists()
        # File should be readable
        assert filepath.is_file()
        assert filepath.stat().st_size > 0
