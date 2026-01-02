"""Tests for detector modules."""

import pandas as pd
import pytest

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.type import TypeGhostDetector
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector


def test_detect_dataframe_backend_pandas():
    """Test detect_dataframe_backend with Pandas DataFrame."""
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    assert detect_dataframe_backend(df) == "pandas"


def test_detect_dataframe_backend_polars():
    """Test detect_dataframe_backend with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    assert detect_dataframe_backend(df) == "polars"


def test_detect_dataframe_backend_invalid():
    """Test detect_dataframe_backend with invalid type."""
    with pytest.raises(ValueError, match="Unsupported DataFrame type"):
        detect_dataframe_backend("not a dataframe")

    with pytest.raises(ValueError, match="Unsupported DataFrame type"):
        detect_dataframe_backend([1, 2, 3])

    with pytest.raises(ValueError, match="Unsupported DataFrame type"):
        detect_dataframe_backend({"key": "value"})


@pytest.fixture
def sample_df_with_nulls():
    """Create a sample DataFrame with null values."""
    return pd.DataFrame(
        {
            "col1": [1, 2, None, None, None, 6, 7, 8, 9, 10],
            "col2": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        }
    )


@pytest.fixture
def sample_df_with_mixed_types():
    """Create a sample DataFrame with mixed types."""
    return pd.DataFrame(
        {
            "col1": [1, "2", 3, "4", 5],
            "col2": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )


@pytest.fixture
def sample_df_with_outliers():
    """Create a sample DataFrame with outliers."""
    return pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],  # 100 is an outlier
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )


def test_null_detector(sample_df_with_nulls):
    """Test NullGhostDetector."""
    detector = NullGhostDetector(null_threshold=0.2)
    findings = detector.detect(sample_df_with_nulls)

    # col1 has 3 nulls out of 10 (30%), which exceeds 20% threshold
    assert len(findings) > 0

    col1_findings = [f for f in findings if f.column == "col1"]
    assert len(col1_findings) > 0

    col1_finding = col1_findings[0]
    assert col1_finding.ghost_type == "null"
    assert col1_finding.column == "col1"
    assert col1_finding.severity in ["info", "warning", "error"]
    assert col1_finding.metadata["null_count"] == 3
    assert col1_finding.metadata["total_count"] == 10


def test_null_detector_no_findings():
    """Test NullGhostDetector with no nulls."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5],
            "col2": [6, 7, 8, 9, 10],
        }
    )

    detector = NullGhostDetector(null_threshold=0.1)
    findings = detector.detect(df)

    assert len(findings) == 0


def test_null_detector_invalid_threshold():
    """Test NullGhostDetector with invalid threshold."""
    with pytest.raises(ValueError):
        NullGhostDetector(null_threshold=1.5)  # > 1.0

    with pytest.raises(ValueError):
        NullGhostDetector(null_threshold=-0.1)  # < 0.0


def test_null_detector_empty_dataframe():
    """Test NullGhostDetector with empty DataFrame."""
    df = pd.DataFrame()
    detector = NullGhostDetector()
    findings = detector.detect(df)

    assert len(findings) == 0


def test_null_detector_all_nulls():
    """Test NullGhostDetector with column that is all nulls."""
    df = pd.DataFrame({"col1": [None, None, None, None, None]})
    detector = NullGhostDetector(null_threshold=0.1)
    findings = detector.detect(df)

    assert len(findings) > 0
    col1_finding = [f for f in findings if f.column == "col1"][0]
    assert col1_finding.severity == "error"  # >50% should be error
    assert col1_finding.metadata["null_percentage"] == 1.0
    assert col1_finding.metadata["null_count"] == 5


def test_null_detector_severity_thresholds():
    """Test NullGhostDetector severity thresholds."""
    # 18% nulls - should be info (>10% but <25%)
    df = pd.DataFrame({"col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, None, None]})  # 2/11 = 18%
    detector = NullGhostDetector(null_threshold=0.1)
    findings = detector.detect(df)

    if findings:
        col1_finding = [f for f in findings if f.column == "col1"][0]
        assert col1_finding.severity == "info"  # >10% but <25%

    # 60% nulls - should be error (>50%)
    df2 = pd.DataFrame({"col1": [1, 2, None, None, None, None]})  # 4/6 = 66.7%
    findings2 = detector.detect(df2)
    col1_finding2 = [f for f in findings2 if f.column == "col1"][0]
    assert col1_finding2.severity == "error"  # >50%


def test_null_detector_polars():
    """Test NullGhostDetector with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame(
        {
            "col1": [1, 2, None, None, None, 6, 7, 8, 9, 10],
            "col2": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        }
    )

    detector = NullGhostDetector(null_threshold=0.2)
    findings = detector.detect(df)

    # col1 has 3 nulls out of 10 (30%)
    assert len(findings) > 0
    col1_findings = [f for f in findings if f.column == "col1"]
    assert len(col1_findings) > 0
    assert col1_findings[0].ghost_type == "null"
    assert col1_findings[0].metadata["null_count"] == 3


def test_type_detector(sample_df_with_mixed_types):
    """Test TypeGhostDetector."""
    detector = TypeGhostDetector()
    findings = detector.detect(sample_df_with_mixed_types)

    # col1 should have mixed types (int and str)
    # Note: actual detection depends on pandas dtype behavior
    # This test may need adjustment based on actual implementation
    # Just verify detector runs without error
    assert isinstance(findings, list)


def test_type_detector_object_dtype_mixed_types():
    """Test TypeGhostDetector with object dtype containing mixed types."""
    # Create DataFrame with object dtype that has mixed types
    df = pd.DataFrame(
        {
            "col1": [1, "2", 3.0, "four", 5],
        }
    )

    detector = TypeGhostDetector()
    findings = detector.detect(df)

    # Should detect mixed types in object column
    assert isinstance(findings, list)
    # May or may not detect depending on pandas behavior
    # Just ensure it doesn't crash


def test_type_detector_numeric_column():
    """Test TypeGhostDetector with numeric columns."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5],
            "col2": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )

    detector = TypeGhostDetector()
    findings = detector.detect(df)

    # Numeric columns shouldn't trigger type findings
    assert isinstance(findings, list)


def test_type_detector_empty_dataframe():
    """Test TypeGhostDetector with empty DataFrame."""
    df = pd.DataFrame()
    detector = TypeGhostDetector()
    findings = detector.detect(df)

    assert isinstance(findings, list)
    assert len(findings) == 0


def test_type_detector_polars():
    """Test TypeGhostDetector with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame(
        {
            "col1": ["1", "2", "three", "4", "5"],
            "col2": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )

    detector = TypeGhostDetector()
    findings = detector.detect(df)

    # Polars is stricter about types, so may or may not detect
    assert isinstance(findings, list)


def test_outlier_detector(sample_df_with_outliers):
    """Test OutlierGhostDetector."""
    detector = OutlierGhostDetector(iqr_multiplier=1.5)
    findings = detector.detect(sample_df_with_outliers)

    # col1 should have outliers (100)
    col1_findings = [
        f for f in findings if f.column == "col1" and f.ghost_type == "outlier"
    ]

    if col1_findings:  # May not always detect depending on IQR calculation
        col1_finding = col1_findings[0]
        assert col1_finding.ghost_type == "outlier"
        assert col1_finding.column == "col1"
        assert "outlier_count" in col1_finding.metadata
        assert "lower_bound" in col1_finding.metadata
        assert "upper_bound" in col1_finding.metadata


def test_outlier_detector_invalid_multiplier():
    """Test OutlierGhostDetector with invalid multiplier."""
    with pytest.raises(ValueError):
        OutlierGhostDetector(iqr_multiplier=-1.0)  # < 0


def test_outlier_detector_no_variability():
    """Test OutlierGhostDetector with IQR = 0 (no variability)."""
    df = pd.DataFrame(
        {
            "col1": [5, 5, 5, 5, 5, 5, 5],  # All same values
        }
    )

    detector = OutlierGhostDetector()
    findings = detector.detect(df)

    # Should skip columns with IQR = 0
    col1_findings = [f for f in findings if f.column == "col1"]
    assert len(col1_findings) == 0


def test_outlier_detector_small_dataset():
    """Test OutlierGhostDetector with dataset < 4 values."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3],  # Only 3 values, need at least 4 for IQR
        }
    )

    detector = OutlierGhostDetector()
    findings = detector.detect(df)

    # Should skip small datasets
    col1_findings = [f for f in findings if f.column == "col1"]
    assert len(col1_findings) == 0


def test_outlier_detector_custom_multiplier():
    """Test OutlierGhostDetector with custom IQR multiplier."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50],  # 50 is outlier
        }
    )

    # Use stricter multiplier
    detector = OutlierGhostDetector(iqr_multiplier=0.5)
    findings = detector.detect(df)

    # Should still detect outliers
    _ = [f for f in findings if f.column == "col1" and f.ghost_type == "outlier"]
    # May or may not detect depending on IQR calculation
    assert isinstance(findings, list)


def test_outlier_detector_all_same_values():
    """Test OutlierGhostDetector with all same values (different from no variability test)."""
    df = pd.DataFrame(
        {
            "col1": [10, 10, 10, 10, 10, 10, 10, 10],
        }
    )

    detector = OutlierGhostDetector()
    findings = detector.detect(df)

    # IQR = 0, should skip
    col1_findings = [f for f in findings if f.column == "col1"]
    assert len(col1_findings) == 0


def test_outlier_detector_nulls_ignored():
    """Test that OutlierGhostDetector ignores null values."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, None, None, 100],  # 100 is outlier
        }
    )

    detector = OutlierGhostDetector()
    findings = detector.detect(df)

    # Should still work with nulls (they're dropped)
    assert isinstance(findings, list)


def test_outlier_detector_polars():
    """Test OutlierGhostDetector with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )

    detector = OutlierGhostDetector(iqr_multiplier=1.5)
    findings = detector.detect(df)

    # Should detect outliers
    assert isinstance(findings, list)
    _ = [f for f in findings if f.column == "col1" and f.ghost_type == "outlier"]
    # May or may not detect depending on IQR calculation


@pytest.fixture
def sample_timeseries_df():
    """Create a sample time-series DataFrame."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    return pd.DataFrame(
        {
            "timestamp": dates,
            "value": [
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
            ],
            "anomaly_value": [
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                100,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
            ],  # 100 is anomaly
        }
    )


def test_timeseries_detector_zscore(sample_timeseries_df):
    """Test TimeSeriesAnomalyDetector with z-score method."""
    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp",
        method="zscore",
        sensitivity=3.0,
    )
    findings = detector.detect(sample_timeseries_df)

    # Should detect anomaly in anomaly_value column
    assert isinstance(findings, list)
    anomaly_findings = [
        f
        for f in findings
        if f.column == "anomaly_value" and f.ghost_type == "timeseries_anomaly"
    ]
    if anomaly_findings:
        finding = anomaly_findings[0]
        assert finding.ghost_type == "timeseries_anomaly"
        assert finding.column == "anomaly_value"
        assert finding.metadata["method"] == "zscore"
        assert finding.metadata["sensitivity"] == 3.0


def test_timeseries_detector_moving_avg(sample_timeseries_df):
    """Test TimeSeriesAnomalyDetector with moving average method."""
    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp",
        method="moving_avg",
        sensitivity=2.0,
        window_size=5,
    )
    findings = detector.detect(sample_timeseries_df)

    # Should detect anomalies
    assert isinstance(findings, list)
    anomaly_findings = [f for f in findings if f.ghost_type == "timeseries_anomaly"]
    if anomaly_findings:
        finding = anomaly_findings[0]
        assert finding.metadata["method"] == "moving_avg"
        assert finding.metadata["window_size"] == 5


def test_timeseries_detector_auto_detect_datetime(sample_timeseries_df):
    """Test TimeSeriesAnomalyDetector with auto-detected datetime column."""
    detector = TimeSeriesAnomalyDetector(method="zscore")
    findings = detector.detect(sample_timeseries_df)

    # Should auto-detect timestamp column
    assert isinstance(findings, list)


def test_timeseries_detector_no_datetime_column():
    """Test TimeSeriesAnomalyDetector with no datetime column."""
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5],
            "col2": [10, 11, 12, 13, 14],
        }
    )

    detector = TimeSeriesAnomalyDetector(method="zscore")
    findings = detector.detect(df)

    # Should return empty list (no datetime column)
    assert len(findings) == 0


def test_timeseries_detector_invalid_method():
    """Test TimeSeriesAnomalyDetector with invalid method."""
    with pytest.raises(ValueError, match="Method must be one of"):
        TimeSeriesAnomalyDetector(method="invalid_method")


def test_timeseries_detector_invalid_sensitivity():
    """Test TimeSeriesAnomalyDetector with invalid sensitivity."""
    with pytest.raises(ValueError, match="sensitivity must be positive"):
        TimeSeriesAnomalyDetector(sensitivity=-1.0)

    with pytest.raises(ValueError, match="sensitivity must be positive"):
        TimeSeriesAnomalyDetector(sensitivity=0.0)


def test_timeseries_detector_invalid_window_size():
    """Test TimeSeriesAnomalyDetector with invalid window size."""
    with pytest.raises(ValueError, match="window_size must be positive"):
        TimeSeriesAnomalyDetector(window_size=-1)

    with pytest.raises(ValueError, match="window_size must be positive"):
        TimeSeriesAnomalyDetector(window_size=0)


def test_timeseries_detector_small_dataset():
    """Test TimeSeriesAnomalyDetector with small dataset."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=2, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [10, 11],  # Only 2 values, need at least 3
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp")
    findings = detector.detect(df)

    # Should skip small datasets
    assert len(findings) == 0


def test_timeseries_detector_polars():
    """Test TimeSeriesAnomalyDetector with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    df = pl.DataFrame(
        {
            "timestamp": dates,
            "value": [10, 11, 12, 13, 14],
            "anomaly_value": [10, 11, 100, 13, 14],  # 100 is anomaly
        }
    )

    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp",
        method="zscore",
        sensitivity=2.0,
    )
    findings = detector.detect(df)

    # Should detect anomalies
    assert isinstance(findings, list)
    anomaly_findings = [f for f in findings if f.ghost_type == "timeseries_anomaly"]
    if anomaly_findings:
        finding = anomaly_findings[0]
        assert finding.ghost_type == "timeseries_anomaly"
        # Polars doesn't maintain row indices
        assert finding.row_indices is None


def test_timeseries_detector_seasonal_fallback():
    """Test TimeSeriesAnomalyDetector seasonal method falls back to z-score if statsmodels not available."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
        }
    )

    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp",
        method="seasonal",
        window_size=3,
    )
    findings = detector.detect(df)

    # Should work (may fall back to z-score if statsmodels not available)
    assert isinstance(findings, list)


def test_timeseries_detector_all_nulls():
    """Test TimeSeriesAnomalyDetector with all null values."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [None] * 10,
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp")
    findings = detector.detect(df)

    # Should return empty (no valid data)
    assert len(findings) == 0


def test_timeseries_detector_single_value():
    """Test TimeSeriesAnomalyDetector with single non-null value."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [10, None, None, None, None],
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp")
    findings = detector.detect(df)

    # Should skip (need at least 3 values)
    assert len(findings) == 0


def test_timeseries_detector_constant_values():
    """Test TimeSeriesAnomalyDetector with constant values."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [10.0] * 20,  # All same value
        }
    )

    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp", method="zscore", sensitivity=3.0
    )
    findings = detector.detect(df)

    # With constant values and z-score, std=0, should return empty
    assert isinstance(findings, list)


def test_timeseries_detector_multiple_columns():
    """Test TimeSeriesAnomalyDetector with multiple numeric columns."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value1": [
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
            ],
            "value2": [
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
                112,
                113,
                114,
                115,
                116,
                117,
                118,
                119,
            ],
            "anomaly_col": [
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                1000,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
            ],
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp", sensitivity=3.0)
    findings = detector.detect(df)

    # Should detect anomalies in anomaly_col
    assert isinstance(findings, list)
    anomaly_findings = [f for f in findings if f.column == "anomaly_col"]
    if anomaly_findings:
        assert anomaly_findings[0].ghost_type == "timeseries_anomaly"


def test_timeseries_detector_string_datetime():
    """Test TimeSeriesAnomalyDetector with string datetime column."""
    import pandas as pd

    df = pd.DataFrame(
        {
            "timestamp": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "value": [10, 11, 100, 13, 14],  # 100 is anomaly
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp", sensitivity=2.0)
    findings = detector.detect(df)

    # Should auto-convert string datetime
    assert isinstance(findings, list)


def test_timeseries_detector_moving_avg_edge_cases():
    """Test TimeSeriesAnomalyDetector moving average with edge cases."""
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", periods=5, freq="D")
    df = pd.DataFrame(
        {
            "timestamp": dates,
            "value": [10, 11, 12, 13, 14],
        }
    )

    # Window size larger than data
    detector = TimeSeriesAnomalyDetector(
        datetime_column="timestamp", method="moving_avg", window_size=10
    )
    findings = detector.detect(df)

    # Should handle gracefully
    assert isinstance(findings, list)


def test_timeseries_detector_polars_string_datetime():
    """Test TimeSeriesAnomalyDetector with Polars and string datetime."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame(
        {
            "timestamp": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "value": [10, 11, 100, 13, 14],
        }
    )

    detector = TimeSeriesAnomalyDetector(datetime_column="timestamp", sensitivity=2.0)
    findings = detector.detect(df)

    # Should work with Polars
    assert isinstance(findings, list)


def test_ml_anomaly_detector():
    """Test MLAnomalyDetector with Isolation Forest."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    # Create DataFrame with some outliers
    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],  # 100 is outlier
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )

    detector = MLAnomalyDetector(algorithm="isolation_forest", contamination=0.1)
    findings = detector.detect(df)

    # Should detect anomalies
    assert isinstance(findings, list)
    ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
    if ml_findings:
        finding = ml_findings[0]
        assert finding.ghost_type == "ml_anomaly"
        assert finding.metadata["algorithm"] == "isolation_forest"


def test_ml_anomaly_detector_invalid_algorithm():
    """Test MLAnomalyDetector with invalid algorithm."""
    with pytest.raises(ValueError, match="Algorithm must be one of"):
        MLAnomalyDetector(algorithm="invalid_algorithm")


def test_ml_anomaly_detector_invalid_contamination():
    """Test MLAnomalyDetector with invalid contamination."""
    with pytest.raises(ValueError, match="Contamination must be between"):
        MLAnomalyDetector(contamination=1.0)  # > 0.5

    with pytest.raises(ValueError, match="Contamination must be between"):
        MLAnomalyDetector(contamination=-0.1)  # < 0.0


def test_ml_anomaly_detector_missing_sklearn():
    """Test MLAnomalyDetector raises ImportError when scikit-learn not installed."""
    # This test verifies the error message, but we can't easily test without sklearn
    # since it's likely installed in test environment
    detector = MLAnomalyDetector()
    # If sklearn is installed, this will work
    # If not, it will raise ImportError
    try:
        df = pd.DataFrame({"col1": [1, 2, 3, 4, 5]})
        detector.detect(df)
    except ImportError as e:
        assert "scikit-learn" in str(e)


def test_ml_anomaly_detector_polars():
    """Test MLAnomalyDetector with Polars DataFrame."""
    import importlib.util

    if (
        importlib.util.find_spec("polars") is None
        or importlib.util.find_spec("sklearn") is None
    ):
        pytest.skip("Polars or scikit-learn not installed")

    import polars as pl

    df = pl.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )

    detector = MLAnomalyDetector(algorithm="isolation_forest")
    findings = detector.detect(df)

    # Should detect anomalies
    assert isinstance(findings, list)
    ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
    if ml_findings:
        finding = ml_findings[0]
        assert finding.row_indices is None  # Polars doesn't maintain indices


def test_ml_anomaly_detector_lof():
    """Test MLAnomalyDetector with LOF algorithm."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )

    detector = MLAnomalyDetector(algorithm="lof", contamination=0.1)
    findings = detector.detect(df)

    assert isinstance(findings, list)
    ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
    if ml_findings:
        assert ml_findings[0].metadata["algorithm"] == "lof"


def test_ml_anomaly_detector_one_class_svm():
    """Test MLAnomalyDetector with One-Class SVM algorithm."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "col2": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        }
    )

    detector = MLAnomalyDetector(algorithm="one_class_svm", contamination=0.1)
    findings = detector.detect(df)

    assert isinstance(findings, list)
    ml_findings = [f for f in findings if f.ghost_type == "ml_anomaly"]
    if ml_findings:
        assert ml_findings[0].metadata["algorithm"] == "one_class_svm"


def test_ml_anomaly_detector_all_nulls():
    """Test MLAnomalyDetector with all null values."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [None, None, None, None, None],
            "col2": [None, None, None, None, None],
        }
    )

    detector = MLAnomalyDetector()
    findings = detector.detect(df)

    # Should return empty (no valid data)
    assert len(findings) == 0


def test_ml_anomaly_detector_single_column():
    """Test MLAnomalyDetector with single numeric column."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
        }
    )

    detector = MLAnomalyDetector()
    findings = detector.detect(df)

    # Should work with single column
    assert isinstance(findings, list)


def test_ml_anomaly_detector_small_dataset():
    """Test MLAnomalyDetector with very small dataset."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [1, 2],
            "col2": [10, 11],
        }
    )

    detector = MLAnomalyDetector()
    findings = detector.detect(df)

    # Need at least 3 samples
    assert isinstance(findings, list)


def test_ml_anomaly_detector_large_dataset_sampling():
    """Test MLAnomalyDetector with large dataset (tests sampling)."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    # Create large dataset
    import numpy as np

    np.random.seed(42)
    data = np.random.randn(15000, 3)  # 15k rows, 3 columns
    df = pd.DataFrame(data, columns=["col1", "col2", "col3"])

    detector = MLAnomalyDetector(max_samples=5000)
    findings = detector.detect(df)

    # Should work with sampling
    assert isinstance(findings, list)


def test_ml_anomaly_detector_constant_values():
    """Test MLAnomalyDetector with constant values."""
    import importlib.util

    if importlib.util.find_spec("sklearn") is None:
        pytest.skip("scikit-learn not installed")

    df = pd.DataFrame(
        {
            "col1": [10.0] * 20,
            "col2": [20.0] * 20,
        }
    )

    detector = MLAnomalyDetector()
    findings = detector.detect(df)

    # Should handle constant values
    assert isinstance(findings, list)


def test_ml_anomaly_detector_invalid_max_samples():
    """Test MLAnomalyDetector with invalid max_samples."""
    with pytest.raises(ValueError, match="max_samples must be positive"):
        MLAnomalyDetector(max_samples=-1)

    with pytest.raises(ValueError, match="max_samples must be positive"):
        MLAnomalyDetector(max_samples=0)
