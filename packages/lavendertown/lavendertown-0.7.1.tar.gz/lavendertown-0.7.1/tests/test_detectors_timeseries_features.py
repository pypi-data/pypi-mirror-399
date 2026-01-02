"""Tests for tsfresh time-series feature extraction."""

from __future__ import annotations

import pytest

try:
    import tsfresh  # noqa: F401

    TSFRESH_AVAILABLE = True
except ImportError:
    TSFRESH_AVAILABLE = False


@pytest.mark.skipif(
    not TSFRESH_AVAILABLE,
    reason="tsfresh not available",
)
class TestTsfreshFeatureExtraction:
    """Tests for tsfresh feature extraction."""

    def test_extract_tsfresh_features_pandas(self):
        """Test extracting features from Pandas DataFrame."""
        import pandas as pd
        from lavendertown.detectors.timeseries_features import extract_tsfresh_features

        # Create time-series data
        dates = pd.date_range("2024-01-01", periods=100, freq="D")
        values = [i + (i % 10) * 0.1 for i in range(100)]
        df = pd.DataFrame({"datetime": dates, "value": values})

        features = extract_tsfresh_features(
            df, datetime_column="datetime", value_column="value"
        )

        assert features is not None
        assert len(features) > 0  # Should have extracted features

    def test_extract_tsfresh_features_with_feature_selection(self):
        """Test feature extraction with feature selection."""
        import pandas as pd
        from lavendertown.detectors.timeseries_features import extract_tsfresh_features

        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        values = [i * 0.5 for i in range(50)]
        df = pd.DataFrame({"datetime": dates, "value": values})

        features = extract_tsfresh_features(
            df,
            datetime_column="datetime",
            value_column="value",
            feature_selection=True,
        )

        assert features is not None

    def test_extract_tsfresh_features_empty_dataframe(self):
        """Test feature extraction with empty DataFrame."""
        import pandas as pd
        from lavendertown.detectors.timeseries_features import extract_tsfresh_features

        df = pd.DataFrame({"datetime": [], "value": []})
        features = extract_tsfresh_features(
            df, datetime_column="datetime", value_column="value"
        )

        assert features is None

    def test_get_feature_importance(self):
        """Test getting feature importance."""
        import pandas as pd
        from lavendertown.detectors.timeseries_features import (
            extract_tsfresh_features,
            get_feature_importance,
        )

        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        values = [i * 0.5 for i in range(50)]
        df = pd.DataFrame({"datetime": dates, "value": values})

        features = extract_tsfresh_features(
            df,
            datetime_column="datetime",
            value_column="value",
            feature_selection=False,
        )

        if features is not None and len(features.columns) > 0:
            importance = get_feature_importance(features, method="variance")
            assert isinstance(importance, dict)
            assert len(importance) > 0

    def test_get_feature_importance_methods(self):
        """Test different feature importance methods."""
        import pandas as pd
        from lavendertown.detectors.timeseries_features import (
            extract_tsfresh_features,
            get_feature_importance,
        )

        dates = pd.date_range("2024-01-01", periods=30, freq="D")
        values = [i * 0.3 for i in range(30)]
        df = pd.DataFrame({"datetime": dates, "value": values})

        features = extract_tsfresh_features(
            df,
            datetime_column="datetime",
            value_column="value",
            feature_selection=False,
        )

        if features is not None and len(features.columns) > 0:
            # Test variance method
            importance_var = get_feature_importance(features, method="variance")
            assert isinstance(importance_var, dict)

            # Test mean method
            importance_mean = get_feature_importance(features, method="mean")
            assert isinstance(importance_mean, dict)

            # Test std method
            importance_std = get_feature_importance(features, method="std")
            assert isinstance(importance_std, dict)


class TestTsfreshIntegration:
    """Tests for tsfresh integration with TimeSeriesAnomalyDetector."""

    def test_timeseries_detector_with_tsfresh_parameter(self):
        """Test TimeSeriesAnomalyDetector accepts use_tsfresh_features parameter."""
        from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

        detector = TimeSeriesAnomalyDetector(use_tsfresh_features=False)
        assert detector.use_tsfresh_features is False

        detector2 = TimeSeriesAnomalyDetector(use_tsfresh_features=True)
        assert detector2.use_tsfresh_features is True

    def test_timeseries_detector_default_tsfresh(self):
        """Test TimeSeriesAnomalyDetector defaults to False for tsfresh."""
        from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

        detector = TimeSeriesAnomalyDetector()
        assert detector.use_tsfresh_features is False


class TestTsfreshFallback:
    """Tests for tsfresh fallback when not available."""

    def test_extract_tsfresh_features_raises_when_not_available(self):
        """Test that extract_tsfresh_features raises ImportError when tsfresh not available."""
        if TSFRESH_AVAILABLE:
            pytest.skip("tsfresh is available, cannot test fallback")

        from lavendertown.detectors.timeseries_features import extract_tsfresh_features
        import pandas as pd

        df = pd.DataFrame(
            {"datetime": pd.date_range("2024-01-01", periods=10), "value": range(10)}
        )

        with pytest.raises(ImportError, match="tsfresh is required"):
            extract_tsfresh_features(
                df, datetime_column="datetime", value_column="value"
            )
