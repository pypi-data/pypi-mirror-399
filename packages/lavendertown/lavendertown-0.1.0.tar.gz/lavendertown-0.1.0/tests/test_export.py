"""Tests for export modules."""

from __future__ import annotations

import json

from lavendertown.export.csv import (
    export_summary_to_csv,
    export_summary_to_csv_file,
    export_to_csv,
    export_to_csv_file,
)
from lavendertown.export.json import export_to_json, export_to_json_file


def test_export_to_json(sample_findings):
    """Test exporting findings to JSON string."""
    json_str = export_to_json(sample_findings)

    # Should be valid JSON
    data = json.loads(json_str)

    # Check structure
    assert "findings" in data
    assert "summary" in data

    # Check findings
    assert len(data["findings"]) == len(sample_findings)
    assert data["findings"][0]["ghost_type"] == "null"
    assert data["findings"][0]["column"] == "col1"

    # Check summary
    assert data["summary"]["total_findings"] == len(sample_findings)
    assert "by_type" in data["summary"]
    assert "by_severity" in data["summary"]


def test_export_to_json_empty_list(empty_findings):
    """Test exporting empty findings list to JSON."""
    json_str = export_to_json(empty_findings)
    data = json.loads(json_str)

    assert data["findings"] == []
    assert data["summary"]["total_findings"] == 0
    assert data["summary"]["by_type"] == {}
    assert data["summary"]["by_severity"] == {}


def test_export_to_json_custom_indent(sample_findings):
    """Test exporting with custom indentation."""
    json_str = export_to_json(sample_findings, indent=4)
    data = json.loads(json_str)

    # Should still be valid JSON
    assert "findings" in data
    # Custom indent should result in more newlines (rough check)
    assert json_str.count("\n") > json_str.count("{")


def test_export_to_json_file(sample_findings, tmp_path):
    """Test exporting findings to JSON file."""
    filepath = tmp_path / "findings.json"

    export_to_json_file(sample_findings, str(filepath))

    # File should exist
    assert filepath.exists()

    # Should contain valid JSON
    with open(filepath) as f:
        data = json.load(f)

    assert len(data["findings"]) == len(sample_findings)
    assert data["summary"]["total_findings"] == len(sample_findings)


def test_export_to_json_file_custom_indent(sample_findings, tmp_path):
    """Test exporting to file with custom indent."""
    filepath = tmp_path / "findings.json"

    export_to_json_file(sample_findings, str(filepath), indent=0)

    # File should exist and be valid JSON
    with open(filepath) as f:
        data = json.load(f)

    assert len(data["findings"]) == len(sample_findings)


def test_export_to_csv(sample_findings):
    """Test exporting findings to CSV string."""
    csv_str = export_to_csv(sample_findings)

    # Should contain header
    assert "ghost_type" in csv_str
    assert "column" in csv_str
    assert "severity" in csv_str
    assert "description" in csv_str
    assert "row_count" in csv_str
    assert "metadata_json" in csv_str

    # Should have correct number of lines (header + findings)
    lines = csv_str.strip().split("\n")
    assert len(lines) == len(sample_findings) + 1  # +1 for header

    # Check first data row
    first_data_line = lines[1]
    assert "null" in first_data_line
    assert "col1" in first_data_line
    assert "warning" in first_data_line


def test_export_to_csv_empty_list(empty_findings):
    """Test exporting empty findings list to CSV."""
    csv_str = export_to_csv(empty_findings)

    # Should only have header
    lines = csv_str.strip().split("\n")
    assert len(lines) == 1
    assert "ghost_type" in lines[0]


def test_export_to_csv_none_row_indices(sample_finding_with_none_indices):
    """Test CSV export with findings that have None row_indices."""
    csv_str = export_to_csv([sample_finding_with_none_indices])

    lines = csv_str.strip().split("\n")
    assert len(lines) == 2  # header + 1 data row

    # Row count should be 0 for None indices
    data_line = lines[1]
    # The row_count column should be 0
    assert ",0," in data_line or data_line.endswith(",0")


def test_export_to_csv_file(sample_findings, tmp_path):
    """Test exporting findings to CSV file."""
    filepath = tmp_path / "findings.csv"

    export_to_csv_file(sample_findings, str(filepath))

    # File should exist
    assert filepath.exists()

    # Should contain data
    content = filepath.read_text()
    assert "ghost_type" in content
    assert "col1" in content


def test_export_summary_to_csv(sample_findings):
    """Test exporting summary statistics to CSV."""
    csv_str = export_summary_to_csv(sample_findings)

    # Should have header
    assert "metric" in csv_str
    assert "value" in csv_str

    # Should contain summary stats
    assert "total_findings" in csv_str
    assert "type_null" in csv_str
    assert "type_outlier" in csv_str
    assert "severity_warning" in csv_str
    assert "severity_error" in csv_str
    assert "severity_info" in csv_str
    assert "column_col1" in csv_str

    # Parse and verify structure (handle line endings)
    lines = csv_str.strip().replace("\r", "").split("\n")
    assert lines[0] == "metric,value"
    assert any("total_findings" in line for line in lines)


def test_export_summary_to_csv_empty_list(empty_findings):
    """Test exporting summary for empty findings."""
    csv_str = export_summary_to_csv(empty_findings)

    lines = csv_str.strip().split("\n")
    # Should have header + total_findings row
    assert len(lines) >= 2
    assert "total_findings,0" in csv_str


def test_export_summary_to_csv_file(sample_findings, tmp_path):
    """Test exporting summary to CSV file."""
    filepath = tmp_path / "summary.csv"

    export_summary_to_csv_file(sample_findings, str(filepath))

    # File should exist
    assert filepath.exists()

    # Should contain summary data
    content = filepath.read_text()
    assert "total_findings" in content
    assert "metric,value" in content
