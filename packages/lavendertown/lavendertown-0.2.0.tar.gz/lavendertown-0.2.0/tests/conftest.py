"""Shared pytest fixtures for LavenderTown tests."""

from __future__ import annotations

import pytest

from lavendertown.models import GhostFinding


@pytest.fixture
def sample_findings() -> list[GhostFinding]:
    """Create a sample list of ghost findings for testing."""
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
            severity="info",
            description="Column col2 has outliers",
            row_indices=[10, 11],
            metadata={"outlier_count": 2, "lower_bound": 1.0, "upper_bound": 100.0},
        ),
        GhostFinding(
            ghost_type="type",
            column="col3",
            severity="error",
            description="Column col3 has mixed types",
            row_indices=None,
            metadata={"dtype": "object", "type_distribution": {"int": 5, "str": 3}},
        ),
        GhostFinding(
            ghost_type="null",
            column="col4",
            severity="info",
            description="Column col4 has some nulls",
            row_indices=[1],
            metadata={"null_count": 1, "null_percentage": 0.1},
        ),
    ]


@pytest.fixture
def empty_findings() -> list[GhostFinding]:
    """Create an empty list of findings."""
    return []


@pytest.fixture
def sample_finding_minimal() -> GhostFinding:
    """Create a minimal GhostFinding with only required fields."""
    return GhostFinding(
        ghost_type="null",
        column="test_col",
        severity="info",
        description="Test finding",
    )


@pytest.fixture
def sample_finding_with_none_indices() -> GhostFinding:
    """Create a GhostFinding with None row_indices."""
    return GhostFinding(
        ghost_type="type",
        column="test_col",
        severity="warning",
        description="Test finding with no row indices",
        row_indices=None,
        metadata={"key": "value"},
    )


@pytest.fixture
def sample_finding_empty_metadata() -> GhostFinding:
    """Create a GhostFinding with empty metadata."""
    return GhostFinding(
        ghost_type="outlier",
        column="test_col",
        severity="error",
        description="Test finding with empty metadata",
        row_indices=[1, 2, 3],
        metadata={},
    )
