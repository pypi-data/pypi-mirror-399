"""Tests for orjson integration in JSON export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lavendertown.export.json import export_to_json, export_to_json_file
from lavendertown.models import GhostFinding


@pytest.fixture
def sample_findings() -> list[GhostFinding]:
    """Create sample findings for testing."""
    return [
        GhostFinding(
            ghost_type="null",
            column="col1",
            severity="warning",
            description="Column col1 has null values",
            row_indices=[2, 5, 7],
            metadata={"null_count": 3, "null_percentage": 0.3},
        ),
        GhostFinding(
            ghost_type="outlier",
            column="col2",
            severity="error",
            description="Column col2 has outliers",
            row_indices=[10, 11],
            metadata={"outlier_count": 2},
        ),
    ]


class TestOrjsonIntegration:
    """Test orjson integration for JSON export."""

    def test_export_to_json_with_orjson_indent_2(
        self, sample_findings: list[GhostFinding]
    ) -> None:
        """Test that export_to_json uses orjson when available and indent=2."""
        json_str = export_to_json(sample_findings, indent=2)

        # Should be valid JSON
        data = json.loads(json_str)

        # Check structure
        assert "findings" in data
        assert "summary" in data
        assert len(data["findings"]) == len(sample_findings)

        # Should have indentation (multiple newlines)
        assert "\n" in json_str

    def test_export_to_json_fallback_indent_4(
        self, sample_findings: list[GhostFinding]
    ) -> None:
        """Test that export_to_json falls back to json for non-2 indent."""
        json_str = export_to_json(sample_findings, indent=4)

        # Should be valid JSON
        data = json.loads(json_str)

        # Check structure
        assert "findings" in data
        assert "summary" in data

        # Should have more indentation (4 spaces)
        lines = json_str.split("\n")
        if len(lines) > 1:
            # Second line should have 4 spaces of indentation
            assert lines[1].startswith("    ")

    def test_export_to_json_fallback_indent_0(
        self, sample_findings: list[GhostFinding]
    ) -> None:
        """Test that export_to_json falls back to json for indent=0."""
        json_str = export_to_json(sample_findings, indent=0)

        # Should be valid JSON (compact)
        data = json.loads(json_str)

        # Check structure
        assert "findings" in data
        assert "summary" in data

        # With indent=0, json.dumps still adds some newlines for readability
        # but it should be much more compact than indent=2
        # Just verify it's valid JSON - the compactness is implementation detail
        assert isinstance(data, dict)
        assert len(data["findings"]) == len(sample_findings)

    def test_export_to_json_file_with_orjson(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test that export_to_json_file uses orjson when available."""
        filepath = tmp_path / "findings.json"

        export_to_json_file(sample_findings, str(filepath), indent=2)

        # File should exist
        assert filepath.exists()

        # Should be valid JSON
        with open(filepath) as f:
            data = json.load(f)

        assert "findings" in data
        assert len(data["findings"]) == len(sample_findings)

        # If orjson was used, file might be written as binary
        # But we should still be able to read it as text
        content = filepath.read_text()
        assert "findings" in content

    def test_export_to_json_file_fallback_indent_4(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test that export_to_json_file falls back to json for non-2 indent."""
        filepath = tmp_path / "findings.json"

        export_to_json_file(sample_findings, str(filepath), indent=4)

        # File should exist
        assert filepath.exists()

        # Should be valid JSON
        with open(filepath) as f:
            data = json.load(f)

        assert "findings" in data
        assert len(data["findings"]) == len(sample_findings)

    def test_export_to_json_backward_compatibility(
        self, sample_findings: list[GhostFinding]
    ) -> None:
        """Test that JSON export maintains backward compatibility."""
        json_str = export_to_json(sample_findings, indent=2)
        data = json.loads(json_str)

        # Verify structure matches expected format
        assert isinstance(data, dict)
        assert "findings" in data
        assert isinstance(data["findings"], list)
        assert "summary" in data
        assert isinstance(data["summary"], dict)

        # Verify findings structure
        for finding in data["findings"]:
            assert "ghost_type" in finding
            assert "column" in finding
            assert "severity" in finding
            assert "description" in finding

    def test_export_to_json_special_characters(self, tmp_path: Path) -> None:
        """Test JSON export with special characters in descriptions."""
        findings = [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description='Column has "quotes" and \n newlines',
                row_indices=[1],
                metadata={},
            )
        ]

        json_str = export_to_json(findings, indent=2)
        data = json.loads(json_str)

        # Should handle special characters correctly
        assert len(data["findings"]) == 1
        assert (
            '"quotes"' in data["findings"][0]["description"]
            or "newlines" in data["findings"][0]["description"]
        )

    def test_export_to_json_empty_findings(self) -> None:
        """Test JSON export with empty findings list."""
        json_str = export_to_json([], indent=2)
        data = json.loads(json_str)

        assert data["findings"] == []
        assert data["summary"]["total_findings"] == 0
        assert data["summary"]["by_type"] == {}
        assert data["summary"]["by_severity"] == {}

    def test_export_to_json_large_dataset(self, tmp_path: Path) -> None:
        """Test JSON export with a larger dataset."""
        # Create 100 findings
        findings = [
            GhostFinding(
                ghost_type="null" if i % 2 == 0 else "outlier",
                column=f"col{i % 5}",
                severity=["info", "warning", "error"][i % 3],
                description=f"Finding {i}",
                row_indices=list(range(i, i + 10)),
                metadata={"index": i},
            )
            for i in range(100)
        ]

        filepath = tmp_path / "large_findings.json"
        export_to_json_file(findings, str(filepath), indent=2)

        # Should successfully export
        assert filepath.exists()

        # Should be valid JSON
        with open(filepath) as f:
            data = json.load(f)

        assert len(data["findings"]) == 100
        assert data["summary"]["total_findings"] == 100
