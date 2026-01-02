"""Tests for Parquet export functionality."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from lavendertown.export.parquet import (
    export_findings_to_parquet,
    export_findings_to_parquet_bytes,
    read_findings_from_parquet,
)
from lavendertown.models import GhostFinding


@pytest.fixture
def sample_findings() -> list[GhostFinding]:
    """Provide sample findings for testing."""
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
            ghost_type="type",
            column="col2",
            severity="error",
            description="Column col2 has inconsistent types",
            row_indices=[1, 3],
            metadata={"expected_type": "int", "actual_type": "str"},
        ),
    ]


@pytest.fixture
def findings_with_complex_metadata() -> list[GhostFinding]:
    """Provide findings with complex metadata."""
    return [
        GhostFinding(
            ghost_type="outlier",
            column="col3",
            severity="info",
            description="Column col3 has outliers",
            row_indices=[10, 11, 12],
            metadata={
                "outlier_count": 3,
                "threshold": 1.5,
                "nested": {"key": "value", "list": [1, 2, 3]},
            },
        ),
        GhostFinding(
            ghost_type="drift",
            column="col4",
            severity="warning",
            description="Distribution drift detected",
            row_indices=None,
            metadata={"drift_type": "distribution", "ks_p_value": 0.001},
        ),
    ]


class TestParquetExport:
    """Tests for Parquet export functionality."""

    def test_export_findings_to_parquet_file(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test exporting findings to Parquet file."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        export_findings_to_parquet(sample_findings, str(filepath))

        assert filepath.exists()
        assert filepath.stat().st_size > 0

    def test_export_findings_to_parquet_bytes(
        self, sample_findings: list[GhostFinding]
    ) -> None:
        """Test exporting findings to Parquet bytes."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        parquet_bytes = export_findings_to_parquet_bytes(sample_findings)
        assert isinstance(parquet_bytes, bytes)
        assert len(parquet_bytes) > 0

    def test_export_parquet_compression_options(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test different compression options."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        compressions = ["snappy", "gzip", "brotli", "zstd", "lz4"]
        for compression in compressions:
            filepath = tmp_path / f"findings_{compression}.parquet"
            export_findings_to_parquet(
                sample_findings, str(filepath), compression=compression
            )
            assert filepath.exists()

    def test_export_parquet_invalid_compression(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test that invalid compression raises ValueError."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        with pytest.raises(ValueError, match="Invalid compression"):
            export_findings_to_parquet(
                sample_findings, str(filepath), compression="invalid"
            )

    def test_export_parquet_with_complex_metadata(
        self, findings_with_complex_metadata: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test exporting findings with complex metadata."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings_complex.parquet"
        export_findings_to_parquet(findings_with_complex_metadata, str(filepath))
        assert filepath.exists()

    def test_export_parquet_empty_findings(self, tmp_path: Path) -> None:
        """Test exporting empty findings list."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings_empty.parquet"
        export_findings_to_parquet([], str(filepath))
        assert filepath.exists()

    def test_export_parquet_pyarrow_not_installed(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test that ImportError is raised when PyArrow is not installed."""
        with patch("lavendertown.export.parquet._PYARROW_AVAILABLE", False):
            filepath = tmp_path / "findings.parquet"
            with pytest.raises(ImportError, match="PyArrow is required"):
                export_findings_to_parquet(sample_findings, str(filepath))


class TestParquetImport:
    """Tests for Parquet import functionality."""

    def test_read_findings_from_parquet(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test reading findings from Parquet file."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        export_findings_to_parquet(sample_findings, str(filepath))

        loaded_findings = read_findings_from_parquet(str(filepath))

        assert len(loaded_findings) == len(sample_findings)
        for original, loaded in zip(sample_findings, loaded_findings):
            assert original.ghost_type == loaded.ghost_type
            assert original.column == loaded.column
            assert original.severity == loaded.severity
            assert original.description == loaded.description
            assert original.row_indices == loaded.row_indices
            assert original.metadata == loaded.metadata

    def test_read_findings_with_none_indices(
        self, findings_with_complex_metadata: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test reading findings with None row_indices."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        export_findings_to_parquet(findings_with_complex_metadata, str(filepath))

        loaded_findings = read_findings_from_parquet(str(filepath))

        assert len(loaded_findings) == len(findings_with_complex_metadata)
        # Check that None indices are preserved
        assert loaded_findings[1].row_indices is None

    def test_read_findings_from_parquet_file_not_found(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing file."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "nonexistent.parquet"
        with pytest.raises(FileNotFoundError):
            read_findings_from_parquet(str(filepath))

    def test_read_parquet_pyarrow_not_installed(self, tmp_path: Path) -> None:
        """Test that ImportError is raised when PyArrow is not installed."""
        with patch("lavendertown.export.parquet._PYARROW_AVAILABLE", False):
            filepath = tmp_path / "findings.parquet"
            with pytest.raises(ImportError, match="PyArrow is required"):
                read_findings_from_parquet(str(filepath))


class TestParquetRoundTrip:
    """Tests for round-trip Parquet export/import."""

    def test_round_trip_simple_findings(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test round-trip export and import of simple findings."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        export_findings_to_parquet(sample_findings, str(filepath))
        loaded_findings = read_findings_from_parquet(str(filepath))

        assert len(loaded_findings) == len(sample_findings)
        for original, loaded in zip(sample_findings, loaded_findings):
            assert original.to_dict() == loaded.to_dict()

    def test_round_trip_complex_metadata(
        self, findings_with_complex_metadata: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test round-trip export and import of findings with complex metadata."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        filepath = tmp_path / "findings.parquet"
        export_findings_to_parquet(findings_with_complex_metadata, str(filepath))
        loaded_findings = read_findings_from_parquet(str(filepath))

        assert len(loaded_findings) == len(findings_with_complex_metadata)
        for original, loaded in zip(findings_with_complex_metadata, loaded_findings):
            assert original.to_dict() == loaded.to_dict()

    def test_round_trip_large_findings_list(self, tmp_path: Path) -> None:
        """Test round-trip with a large number of findings."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        # Create 100 findings
        large_findings = [
            GhostFinding(
                ghost_type="type",
                column=f"col_{i % 10}",
                severity="info" if i % 2 == 0 else "warning",
                description=f"Finding {i}",
                row_indices=[i, i + 1] if i % 3 == 0 else None,
                metadata={"index": i, "value": f"test_{i}"},
            )
            for i in range(100)
        ]

        filepath = tmp_path / "findings_large.parquet"
        export_findings_to_parquet(large_findings, str(filepath))
        loaded_findings = read_findings_from_parquet(str(filepath))

        assert len(loaded_findings) == 100
        for original, loaded in zip(large_findings, loaded_findings):
            assert original.to_dict() == loaded.to_dict()
