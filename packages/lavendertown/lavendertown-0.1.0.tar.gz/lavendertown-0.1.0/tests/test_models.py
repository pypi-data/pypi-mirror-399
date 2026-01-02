"""Tests for models module."""

import pytest

from lavendertown.models import GhostFinding


def test_ghost_finding_creation():
    """Test creating a GhostFinding."""
    finding = GhostFinding(
        ghost_type="null",
        column="test_col",
        severity="warning",
        description="Test finding",
        row_indices=[1, 2, 3],
        metadata={"key": "value"},
    )

    assert finding.ghost_type == "null"
    assert finding.column == "test_col"
    assert finding.severity == "warning"
    assert finding.description == "Test finding"
    assert finding.row_indices == [1, 2, 3]
    assert finding.metadata == {"key": "value"}


def test_ghost_finding_invalid_severity():
    """Test that invalid severity raises ValueError."""
    with pytest.raises(ValueError, match="Severity must be one of"):
        GhostFinding(
            ghost_type="null",
            column="test_col",
            severity="invalid",
            description="Test",
        )


def test_ghost_finding_to_dict():
    """Test converting finding to dictionary."""
    finding = GhostFinding(
        ghost_type="null",
        column="test_col",
        severity="warning",
        description="Test finding",
        row_indices=[1, 2, 3],
        metadata={"key": "value"},
    )

    result = finding.to_dict()

    assert result["ghost_type"] == "null"
    assert result["column"] == "test_col"
    assert result["severity"] == "warning"
    assert result["description"] == "Test finding"
    assert result["row_indices"] == [1, 2, 3]
    assert result["metadata"] == {"key": "value"}


def test_ghost_finding_from_dict():
    """Test creating finding from dictionary."""
    data = {
        "ghost_type": "null",
        "column": "test_col",
        "severity": "warning",
        "description": "Test finding",
        "row_indices": [1, 2, 3],
        "metadata": {"key": "value"},
    }

    finding = GhostFinding.from_dict(data)

    assert finding.ghost_type == "null"
    assert finding.column == "test_col"
    assert finding.severity == "warning"
    assert finding.description == "Test finding"
    assert finding.row_indices == [1, 2, 3]
    assert finding.metadata == {"key": "value"}


def test_ghost_finding_with_none_row_indices():
    """Test GhostFinding with None row_indices."""
    finding = GhostFinding(
        ghost_type="type",
        column="test_col",
        severity="warning",
        description="Test finding",
        row_indices=None,
        metadata={"key": "value"},
    )

    assert finding.row_indices is None
    assert finding.to_dict()["row_indices"] is None


def test_ghost_finding_with_empty_metadata():
    """Test GhostFinding with empty metadata."""
    finding = GhostFinding(
        ghost_type="outlier",
        column="test_col",
        severity="info",
        description="Test finding",
        row_indices=[1, 2],
        metadata={},
    )

    assert finding.metadata == {}
    assert finding.to_dict()["metadata"] == {}


def test_ghost_finding_to_dict_with_various_metadata_types():
    """Test to_dict with various metadata value types."""
    finding = GhostFinding(
        ghost_type="test",
        column="test_col",
        severity="info",
        description="Test",
        metadata={
            "string": "value",
            "int": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        },
    )

    result = finding.to_dict()
    assert result["metadata"]["string"] == "value"
    assert result["metadata"]["int"] == 42
    assert result["metadata"]["float"] == 3.14
    assert result["metadata"]["list"] == [1, 2, 3]
    assert result["metadata"]["nested"] == {"key": "value"}


def test_ghost_finding_from_dict_with_missing_fields():
    """Test from_dict with missing optional fields."""
    data = {
        "ghost_type": "null",
        "column": "test_col",
        "severity": "warning",
        "description": "Test finding",
        # Missing row_indices and metadata
    }

    finding = GhostFinding.from_dict(data)

    assert finding.ghost_type == "null"
    assert finding.row_indices is None
    assert finding.metadata == {}


def test_ghost_finding_from_dict_with_none_values():
    """Test from_dict with None values."""
    data = {
        "ghost_type": "type",
        "column": "test_col",
        "severity": "error",
        "description": "Test finding",
        "row_indices": None,
        "metadata": {},
    }

    finding = GhostFinding.from_dict(data)

    assert finding.row_indices is None
    assert finding.metadata == {}
