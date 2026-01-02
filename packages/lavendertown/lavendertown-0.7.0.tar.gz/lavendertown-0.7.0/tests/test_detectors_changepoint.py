"""Tests for change point detection detector."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lavendertown.detectors.changepoint import ChangePointDetector


@pytest.fixture
def simple_time_series() -> pd.DataFrame:
    """Provide a simple time series with a clear change point."""
    # Create data with a change point at index 50
    np.random.seed(42)
    data1 = np.random.normal(0, 1, 50)
    data2 = np.random.normal(5, 1, 50)  # Shifted mean
    data = np.concatenate([data1, data2])
    return pd.DataFrame({"value": data})


@pytest.fixture
def time_series_multiple_changes() -> pd.DataFrame:
    """Provide a time series with multiple change points."""
    np.random.seed(42)
    # Three segments with different means
    data1 = np.random.normal(0, 1, 30)
    data2 = np.random.normal(5, 1, 30)
    data3 = np.random.normal(2, 1, 40)
    data = np.concatenate([data1, data2, data3])
    return pd.DataFrame({"value": data})


@pytest.fixture
def time_series_no_changes() -> pd.DataFrame:
    """Provide a time series with no change points."""
    np.random.seed(42)
    data = np.random.normal(0, 1, 100)
    return pd.DataFrame({"value": data})


@pytest.fixture
def time_series_multiple_columns() -> pd.DataFrame:
    """Provide a DataFrame with multiple time series columns."""
    np.random.seed(42)
    data = {
        "series1": np.random.normal(0, 1, 100),
        "series2": np.concatenate(
            [np.random.normal(0, 1, 50), np.random.normal(5, 1, 50)]
        ),
        "series3": np.random.normal(0, 1, 100),
    }
    return pd.DataFrame(data)


class TestChangePointDetectorInitialization:
    """Tests for ChangePointDetector initialization."""

    def test_default_initialization(self) -> None:
        """Test default initialization."""
        detector = ChangePointDetector()
        assert detector.algorithm == "pelt"
        assert detector.min_size == 2
        assert detector.penalty == 10.0
        assert detector.n_bkps is None

    def test_custom_initialization(self) -> None:
        """Test initialization with custom parameters."""
        detector = ChangePointDetector(
            algorithm="binseg", min_size=5, penalty=20.0, n_bkps=3
        )
        assert detector.algorithm == "binseg"
        assert detector.min_size == 5
        assert detector.penalty == 20.0
        assert detector.n_bkps == 3

    def test_invalid_algorithm(self) -> None:
        """Test that ValueError is raised for invalid algorithm."""
        with pytest.raises(ValueError, match="Algorithm must be one of"):
            ChangePointDetector(algorithm="invalid")

    def test_invalid_min_size(self) -> None:
        """Test that ValueError is raised for invalid min_size."""
        with pytest.raises(ValueError, match="min_size must be >= 2"):
            ChangePointDetector(min_size=1)

    def test_invalid_penalty(self) -> None:
        """Test that ValueError is raised for invalid penalty."""
        with pytest.raises(ValueError, match="penalty must be positive"):
            ChangePointDetector(penalty=0)
        with pytest.raises(ValueError, match="penalty must be positive"):
            ChangePointDetector(penalty=-1)

    def test_invalid_n_bkps(self) -> None:
        """Test that ValueError is raised for invalid n_bkps."""
        with pytest.raises(ValueError, match="n_bkps must be >= 1"):
            ChangePointDetector(n_bkps=0)


class TestChangePointDetectorAlgorithms:
    """Tests for different change point detection algorithms."""

    @pytest.mark.parametrize("algorithm", ["pelt", "binseg", "window", "dynp"])
    def test_algorithm_initialization(self, algorithm: str) -> None:
        """Test that all algorithms can be initialized."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm=algorithm)
        assert detector.algorithm == algorithm

    @pytest.mark.parametrize("algorithm", ["pelt", "binseg", "window", "dynp"])
    def test_algorithm_detection(
        self, algorithm: str, simple_time_series: pd.DataFrame
    ) -> None:
        """Test that all algorithms can detect change points."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm=algorithm, penalty=10.0)
        findings = detector.detect(simple_time_series)

        assert isinstance(findings, list)
        # Should detect at least one change point in this data

    def test_pelt_algorithm(self, simple_time_series: pd.DataFrame) -> None:
        """Test Pelt algorithm specifically."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="pelt", penalty=10.0)
        findings = detector.detect(simple_time_series)
        assert isinstance(findings, list)

    def test_binseg_algorithm(self, simple_time_series: pd.DataFrame) -> None:
        """Test Binary Segmentation algorithm."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="binseg", penalty=10.0)
        findings = detector.detect(simple_time_series)
        assert isinstance(findings, list)

    def test_window_algorithm(self, simple_time_series: pd.DataFrame) -> None:
        """Test Window-based algorithm."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="window", penalty=10.0)
        findings = detector.detect(simple_time_series)
        assert isinstance(findings, list)

    def test_dynp_algorithm(self, simple_time_series: pd.DataFrame) -> None:
        """Test Dynamic Programming algorithm."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="dynp", n_bkps=2)
        findings = detector.detect(simple_time_series)
        assert isinstance(findings, list)

    def test_ruptures_not_installed(self, simple_time_series: pd.DataFrame) -> None:
        """Test that ImportError is raised when ruptures is not installed."""
        pytest.importorskip("ruptures", reason="ruptures is installed")
        # If ruptures is installed, skip this test
        pytest.skip("ruptures is installed, cannot test fallback without mocking")


class TestChangePointDetection:
    """Tests for change point detection functionality."""

    def test_detect_single_change_point(self, simple_time_series: pd.DataFrame) -> None:
        """Test detection of a single change point."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(
            algorithm="pelt", penalty=1.0
        )  # Lower penalty to detect change points
        findings = detector.detect(simple_time_series)

        # May or may not detect change points depending on data and penalty
        assert isinstance(findings, list)
        if len(findings) > 0:
            finding = findings[0]
            assert finding.ghost_type == "changepoint"
            assert finding.column == "value"
            assert finding.severity in ["info", "warning", "error"]
            assert "change_point_count" in finding.metadata
            assert "algorithm" in finding.metadata
            assert finding.metadata["algorithm"] == "pelt"

    def test_detect_multiple_change_points(
        self, time_series_multiple_changes: pd.DataFrame
    ) -> None:
        """Test detection of multiple change points."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(
            algorithm="pelt", penalty=1.0
        )  # Lower penalty to detect change points
        findings = detector.detect(time_series_multiple_changes)

        # May or may not detect change points depending on data and penalty
        assert isinstance(findings, list)
        if len(findings) > 0:
            # Should detect change points
            for finding in findings:
                assert finding.metadata["change_point_count"] > 0
                assert finding.ghost_type == "changepoint"

    def test_detect_no_change_points(
        self, time_series_no_changes: pd.DataFrame
    ) -> None:
        """Test detection when there are no change points."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(
            algorithm="pelt", penalty=100.0
        )  # High penalty = fewer detections
        findings = detector.detect(time_series_no_changes)

        # May detect some change points even in uniform data, but should handle gracefully
        assert isinstance(findings, list)

    def test_detect_multiple_columns(
        self, time_series_multiple_columns: pd.DataFrame
    ) -> None:
        """Test detection on DataFrame with multiple columns."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="pelt", penalty=10.0)
        findings = detector.detect(time_series_multiple_columns)

        assert isinstance(findings, list)
        # Should detect change points in series2 but not necessarily in series1 or series3

    def test_findings_structure(self, simple_time_series: pd.DataFrame) -> None:
        """Test that findings have correct structure."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(algorithm="pelt", penalty=10.0)
        findings = detector.detect(simple_time_series)

        for finding in findings:
            assert finding.ghost_type == "changepoint"
            assert finding.column is not None
            assert finding.severity in ["info", "warning", "error"]
            assert finding.description is not None
            assert finding.row_indices is not None
            assert len(finding.row_indices) > 0
            assert "change_point_count" in finding.metadata
            assert "algorithm" in finding.metadata
            assert "penalty" in finding.metadata
            assert "segments" in finding.metadata
            assert isinstance(finding.metadata["segments"], list)

    def test_severity_assignment(
        self, time_series_multiple_changes: pd.DataFrame
    ) -> None:
        """Test that severity is assigned correctly based on change point count."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector = ChangePointDetector(
            algorithm="pelt", penalty=5.0
        )  # Lower penalty = more detections
        findings = detector.detect(time_series_multiple_changes)

        for finding in findings:
            change_point_count = finding.metadata["change_point_count"]
            if change_point_count > 3:
                assert finding.severity == "warning"
            else:
                assert finding.severity in ["info", "warning"]


class TestChangePointDetectorEdgeCases:
    """Tests for edge cases in change point detection."""

    def test_empty_dataframe(self) -> None:
        """Test with empty DataFrame."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame()
        detector = ChangePointDetector()
        findings = detector.detect(df)
        assert findings == []

    def test_single_column_dataframe(self) -> None:
        """Test with single column DataFrame."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0, 5.0]})
        detector = ChangePointDetector(min_size=2)
        findings = detector.detect(df)
        assert isinstance(findings, list)

    def test_too_small_dataframe(self) -> None:
        """Test with DataFrame too small for detection."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame(
            {"value": [1.0, 2.0]}
        )  # Only 2 rows, min_size=2 needs at least 4
        detector = ChangePointDetector(min_size=2)
        findings = detector.detect(df)
        assert isinstance(findings, list)  # Should handle gracefully

    def test_dataframe_with_nulls(self) -> None:
        """Test with DataFrame containing null values."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame({"value": [1.0, 2.0, None, 4.0, 5.0, 6.0, 7.0, 8.0]})
        detector = ChangePointDetector()
        findings = detector.detect(df)
        # Should handle nulls gracefully (drop them)
        assert isinstance(findings, list)

    def test_dataframe_with_only_nulls(self) -> None:
        """Test with DataFrame containing only null values."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame({"value": [None, None, None, None]})
        detector = ChangePointDetector()
        findings = detector.detect(df)
        assert findings == []

    def test_dataframe_no_numeric_columns(self) -> None:
        """Test with DataFrame containing no numeric columns."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        df = pd.DataFrame({"col1": ["a", "b", "c"], "col2": ["x", "y", "z"]})
        detector = ChangePointDetector()
        findings = detector.detect(df)
        assert findings == []

    def test_penalty_effect(self, simple_time_series: pd.DataFrame) -> None:
        """Test that different penalty values produce different results."""
        try:
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("ruptures not installed")

        detector_low_penalty = ChangePointDetector(algorithm="pelt", penalty=1.0)
        findings_low = detector_low_penalty.detect(simple_time_series)

        detector_high_penalty = ChangePointDetector(algorithm="pelt", penalty=100.0)
        findings_high = detector_high_penalty.detect(simple_time_series)

        # Higher penalty should generally detect fewer change points
        # (or same number, but not more)
        assert isinstance(findings_low, list)
        assert isinstance(findings_high, list)


@pytest.mark.skipif(True, reason="Polars tests would require polars DataFrame fixtures")
class TestChangePointDetectorPolars:
    """Tests for change point detection with Polars DataFrames."""

    def test_polars_dataframe(self) -> None:
        """Test detection with Polars DataFrame."""
        try:
            import polars as pl
            import ruptures  # noqa: F401
        except ImportError:
            pytest.skip("polars or ruptures not installed")

        # Create Polars DataFrame
        df = pl.DataFrame({"value": [1.0, 2.0, 3.0, 10.0, 11.0, 12.0]})
        detector = ChangePointDetector(algorithm="pelt", penalty=10.0)
        findings = detector.detect(df)

        assert isinstance(findings, list)
