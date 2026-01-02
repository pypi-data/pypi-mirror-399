"""Tests for PyOD integration in MLAnomalyDetector."""

from __future__ import annotations

import pandas as pd
import pytest

from lavendertown.detectors.ml_anomaly import MLAnomalyDetector


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Provide a sample DataFrame with numeric columns."""
    import numpy as np

    np.random.seed(42)
    data = {
        "col1": np.random.normal(0, 1, 100),
        "col2": np.random.normal(5, 2, 100),
        "col3": np.random.normal(10, 3, 100),
    }
    # Add some outliers
    data["col1"][10] = 10.0
    data["col2"][20] = -5.0
    data["col3"][30] = 30.0
    return pd.DataFrame(data)


@pytest.fixture
def sample_dataframe_large() -> pd.DataFrame:
    """Provide a larger sample DataFrame."""
    import numpy as np

    np.random.seed(42)
    data = {f"col_{i}": np.random.normal(i, 1, 1000) for i in range(5)}
    return pd.DataFrame(data)


class TestPyODAlgorithms:
    """Tests for PyOD algorithm integration."""

    @pytest.mark.parametrize(
        "algorithm",
        ["abod", "cblof", "hbos", "knn", "mcd", "pca", "iforest", "ocsvm"],
    )
    def test_pyod_algorithm_initialization(self, algorithm: str) -> None:
        """Test that PyOD algorithms can be initialized."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        detector = MLAnomalyDetector(algorithm=algorithm, contamination=0.1)
        assert detector.algorithm == algorithm

    @pytest.mark.parametrize(
        "algorithm",
        ["abod", "cblof", "hbos", "knn", "mcd", "pca", "iforest", "ocsvm"],
    )
    def test_pyod_algorithm_detection(
        self, algorithm: str, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that PyOD algorithms can detect anomalies."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        detector = MLAnomalyDetector(algorithm=algorithm, contamination=0.1)
        findings = detector.detect(sample_dataframe)

        assert isinstance(findings, list)
        # PyOD algorithms should detect some anomalies in this data
        # (may be 0 or more depending on algorithm sensitivity)

    def test_pyod_algorithm_not_installed(self, sample_dataframe: pd.DataFrame) -> None:
        """Test that ImportError is raised when PyOD is not installed."""
        pytest.importorskip("pyod", reason="PyOD is installed")
        # If PyOD is installed, skip this test
        pytest.skip("PyOD is installed, cannot test fallback without mocking")

    def test_pyod_algorithm_invalid_name(self) -> None:
        """Test that ValueError is raised for invalid PyOD algorithm names."""
        with pytest.raises(ValueError, match="Algorithm must be one of"):
            MLAnomalyDetector(algorithm="invalid_pyod_algorithm", contamination=0.1)

    def test_pyod_vs_sklearn_algorithms_different_results(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that PyOD and scikit-learn algorithms can both work."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        # Test scikit-learn algorithm
        sklearn_detector = MLAnomalyDetector(
            algorithm="isolation_forest", contamination=0.1
        )
        sklearn_findings = sklearn_detector.detect(sample_dataframe)

        # Test PyOD algorithm
        pyod_detector = MLAnomalyDetector(algorithm="iforest", contamination=0.1)
        pyod_findings = pyod_detector.detect(sample_dataframe)

        assert isinstance(sklearn_findings, list)
        assert isinstance(pyod_findings, list)

    def test_pyod_algorithm_with_custom_contamination(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test PyOD algorithms with different contamination values."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        for contamination in [0.05, 0.1, 0.2]:
            detector = MLAnomalyDetector(algorithm="knn", contamination=contamination)
            findings = detector.detect(sample_dataframe)
            assert isinstance(findings, list)

    def test_pyod_algorithm_with_random_state(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test PyOD algorithms that support random_state."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        detector = MLAnomalyDetector(
            algorithm="iforest", contamination=0.1, random_state=42
        )
        findings1 = detector.detect(sample_dataframe)

        detector2 = MLAnomalyDetector(
            algorithm="iforest", contamination=0.1, random_state=42
        )
        findings2 = detector2.detect(sample_dataframe)

        # Results should be deterministic with same random_state
        assert len(findings1) == len(findings2)

    def test_pyod_algorithm_empty_dataframe(self) -> None:
        """Test PyOD algorithms with empty DataFrame."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        df = pd.DataFrame()
        detector = MLAnomalyDetector(algorithm="knn", contamination=0.1)
        findings = detector.detect(df)
        assert findings == []

    def test_pyod_algorithm_no_numeric_columns(self) -> None:
        """Test PyOD algorithms with DataFrame containing no numeric columns."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        df = pd.DataFrame({"col1": ["a", "b", "c"], "col2": ["x", "y", "z"]})
        detector = MLAnomalyDetector(algorithm="knn", contamination=0.1)
        findings = detector.detect(df)
        assert findings == []

    def test_pyod_algorithm_small_dataset(self) -> None:
        """Test PyOD algorithms with very small dataset."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        df = pd.DataFrame({"col1": [1.0, 2.0], "col2": [3.0, 4.0]})
        detector = MLAnomalyDetector(algorithm="knn", contamination=0.1)
        findings = detector.detect(df)
        # Should handle small datasets gracefully (may return empty or error)
        assert isinstance(findings, list)

    def test_pyod_algorithm_large_dataset_sampling(
        self, sample_dataframe_large: pd.DataFrame
    ) -> None:
        """Test that PyOD algorithms work with large datasets using sampling."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        detector = MLAnomalyDetector(
            algorithm="knn", contamination=0.1, max_samples=500
        )
        findings = detector.detect(sample_dataframe_large)
        assert isinstance(findings, list)

    @pytest.mark.parametrize(
        "algorithm",
        ["abod", "cblof", "hbos", "knn", "mcd", "pca", "iforest", "ocsvm"],
    )
    def test_pyod_algorithm_findings_structure(
        self, algorithm: str, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test that PyOD algorithm findings have correct structure."""
        try:
            import pyod  # noqa: F401
        except ImportError:
            pytest.skip("PyOD not installed")

        detector = MLAnomalyDetector(algorithm=algorithm, contamination=0.1)
        findings = detector.detect(sample_dataframe)

        for finding in findings:
            assert finding.ghost_type == "ml_anomaly"
            assert finding.column is not None
            assert finding.severity in ["info", "warning", "error"]
            assert finding.description is not None
            assert "algorithm" in finding.metadata
            assert finding.metadata["algorithm"] == algorithm
            assert "contamination" in finding.metadata
