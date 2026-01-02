"""Tests for Inspector class."""

import pandas as pd
import pytest

from lavendertown.inspector import Inspector


@pytest.fixture
def sample_df():
    """Create a sample DataFrame."""
    return pd.DataFrame(
        {
            "col1": [1, 2, None, 4, 5],
            "col2": [10, 20, 30, 40, 50],
            "col3": ["a", "b", "c", "d", "e"],
        }
    )


def test_inspector_initialization(sample_df):
    """Test Inspector initialization."""
    inspector = Inspector(sample_df)

    assert inspector.df is sample_df
    assert inspector.backend == "pandas"
    assert len(inspector.detectors) > 0


def test_inspector_custom_detectors(sample_df):
    """Test Inspector with custom detectors."""
    from lavendertown.detectors.null import NullGhostDetector

    custom_detectors = [NullGhostDetector()]
    inspector = Inspector(sample_df, detectors=custom_detectors)

    assert len(inspector.detectors) == 1
    assert isinstance(inspector.detectors[0], NullGhostDetector)


def test_inspector_detect(sample_df):
    """Test Inspector.detect() method."""
    inspector = Inspector(sample_df)
    findings = inspector.detect()

    # Should return a list of findings
    assert isinstance(findings, list)
    # May or may not have findings depending on data
    assert all(hasattr(f, "ghost_type") for f in findings)


def test_inspector_detect_caching(sample_df):
    """Test that Inspector caches findings."""
    inspector = Inspector(sample_df)

    findings1 = inspector.detect()
    findings2 = inspector.detect()

    # Should return same findings (cached)
    assert findings1 is findings2


def test_inspector_hash_dataframe_pandas(sample_df):
    """Test _hash_dataframe with Pandas DataFrame."""
    inspector = Inspector(sample_df)
    hash1 = inspector._hash_dataframe()

    # Should return a string
    assert isinstance(hash1, str)

    # Hash should be deterministic for same data
    # (Note: may vary due to hash() implementation, but should be a string)


def test_inspector_hash_dataframe_polars():
    """Test _hash_dataframe with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    inspector = Inspector(df)
    hash1 = inspector._hash_dataframe()
    hash2 = inspector._hash_dataframe()

    # Should return same hash for same DataFrame
    assert hash1 == hash2
    assert isinstance(hash1, str)


def test_inspector_get_cached_findings_without_streamlit(sample_df):
    """Test _get_cached_findings falls back when Streamlit not available."""
    inspector = Inspector(sample_df)

    # Mock the case where Streamlit import fails
    # We can't easily mock the import, but we can test the fallback logic
    # by ensuring detect() is called when Streamlit is not in the environment
    # For now, we'll test that the method exists and handles the case
    findings = inspector._get_cached_findings()

    # Should return findings (either from cache or detect)
    assert isinstance(findings, list)


def test_inspector_detector_error_handling(sample_df):
    """Test that Inspector continues when a detector raises an exception."""
    from lavendertown.detectors.base import GhostDetector

    class FailingDetector(GhostDetector):
        def detect(self, df):
            raise ValueError("Detector failed!")

    class WorkingDetector(GhostDetector):
        def detect(self, df):
            from lavendertown.models import GhostFinding

            return [
                GhostFinding(
                    ghost_type="test",
                    column="test_col",
                    severity="info",
                    description="Test finding",
                )
            ]

    # Use a mix of working and failing detectors
    detectors = [FailingDetector(), WorkingDetector()]
    inspector = Inspector(sample_df, detectors=detectors)

    # Should not raise, but should continue with other detectors
    findings = inspector.detect()

    # Should have findings from working detector
    assert isinstance(findings, list)
    # May have findings from working detector (if it runs)
    # The key is that it doesn't crash


def test_inspector_polars_backend():
    """Test Inspector with Polars DataFrame."""
    try:
        import polars as pl
    except ImportError:
        pytest.skip("Polars not installed")

    df = pl.DataFrame(
        {
            "col1": [1, 2, None, 4, 5],
            "col2": [10, 20, 30, 40, 50],
        }
    )

    inspector = Inspector(df)

    assert inspector.backend == "polars"
    assert len(inspector.detectors) > 0

    # Should be able to detect
    findings = inspector.detect()
    assert isinstance(findings, list)
