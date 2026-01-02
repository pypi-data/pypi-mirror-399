"""Property-based tests for detectors using Hypothesis.

These tests use Hypothesis to generate diverse test cases and ensure
detectors handle edge cases correctly without crashing.
"""

from __future__ import annotations

import datetime
from typing import Any

import hypothesis.strategies as st
import pandas as pd
import pytest
from hypothesis import assume, given, settings, HealthCheck

try:
    import polars as pl
except ImportError:
    pl = None

from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown.detectors.type import TypeGhostDetector


# Hypothesis strategies for generating test data
def numeric_strategy() -> st.SearchStrategy[float | int | None]:
    """Strategy for generating numeric values including None."""
    return st.one_of(
        st.integers(min_value=-1000, max_value=1000),
        st.floats(
            allow_nan=False, allow_infinity=False, min_value=-1000.0, max_value=1000.0
        ),
        st.none(),
    )


def string_strategy() -> st.SearchStrategy[str | None]:
    """Strategy for generating string values including None."""
    return st.one_of(
        st.text(min_size=0, max_size=50),
        st.none(),
    )


def datetime_strategy() -> st.SearchStrategy[datetime.datetime | None]:
    """Strategy for generating datetime values including None."""
    return st.one_of(
        st.datetimes(
            min_value=datetime.datetime(2000, 1, 1),
            max_value=datetime.datetime(2024, 12, 31),
        ),
        st.none(),
    )


@st.composite
def dataframe_strategy(draw: st.DrawFn) -> pd.DataFrame:
    """Strategy for generating DataFrames with various column types and sizes."""
    # Generate number of rows (0 to 100) - reduced to avoid health check issues
    n_rows = draw(st.integers(min_value=0, max_value=100))

    # Generate number of columns (1 to 5) - reduced to avoid health check issues
    n_cols = draw(st.integers(min_value=1, max_value=5))

    # Generate column names
    column_names = [f"col_{i}" for i in range(n_cols)]

    # Generate data for each column
    data: dict[str, list[Any]] = {}
    for col in column_names:
        # Choose a strategy for this column
        col_type = draw(st.sampled_from(["numeric", "string", "datetime", "mixed"]))

        if col_type == "numeric":
            col_data = draw(
                st.lists(numeric_strategy(), min_size=n_rows, max_size=n_rows)
            )
        elif col_type == "string":
            col_data = draw(
                st.lists(string_strategy(), min_size=n_rows, max_size=n_rows)
            )
        elif col_type == "datetime":
            col_data = draw(
                st.lists(datetime_strategy(), min_size=n_rows, max_size=n_rows)
            )
        else:  # mixed
            col_data = draw(
                st.lists(
                    st.one_of(numeric_strategy(), string_strategy()),
                    min_size=n_rows,
                    max_size=n_rows,
                )
            )

        data[col] = col_data

    # Create DataFrame
    df = pd.DataFrame(data)

    # Ensure DataFrame has at least one column
    assume(len(df.columns) > 0)

    return df


@pytest.mark.skipif(pl is None, reason="polars not installed")
@st.composite
def polars_dataframe_strategy(draw: st.DrawFn) -> Any:
    """Strategy for generating Polars DataFrames."""
    pdf = draw(dataframe_strategy())
    # Polars requires consistent types, so filter out mixed-type columns
    # Convert mixed columns to string type
    for col in pdf.columns:
        if pdf[col].dtype == "object":
            # Check if it's truly mixed (contains both numeric and string)
            try:
                pd.to_numeric(pdf[col], errors="raise")
                # All numeric, convert to float
                pdf[col] = pd.to_numeric(pdf[col], errors="coerce")
            except (ValueError, TypeError):
                # Mixed or string types, convert all to string
                pdf[col] = pdf[col].astype(str)
    try:
        return pl.from_pandas(pdf)
    except Exception:
        # If conversion fails, assume empty DataFrame
        return pl.DataFrame()


class TestNullGhostDetector:
    """Property-based tests for NullGhostDetector."""

    @given(df=dataframe_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_null_detector_never_crashes(self, df: pd.DataFrame) -> None:
        """Test that NullGhostDetector never crashes on any valid DataFrame."""
        detector = NullGhostDetector()
        findings = detector.detect(df)

        # Should always return a list
        assert isinstance(findings, list)

        # Each finding should have required attributes
        for finding in findings:
            assert hasattr(finding, "column")
            assert hasattr(finding, "ghost_type")
            assert hasattr(finding, "description")
            assert hasattr(finding, "severity")

    @given(df=dataframe_strategy())
    @settings(max_examples=30, deadline=5000)
    def test_null_detector_empty_dataframe(self, df: pd.DataFrame) -> None:
        """Test NullGhostDetector with empty DataFrames."""
        if len(df) == 0:
            detector = NullGhostDetector()
            findings = detector.detect(df)
            # Should handle empty DataFrame gracefully
            assert isinstance(findings, list)

    @pytest.mark.skipif(pl is None, reason="polars not installed")
    @given(df=polars_dataframe_strategy())
    @settings(max_examples=30, deadline=5000)
    def test_null_detector_polars(self, df: Any) -> None:
        """Test NullGhostDetector with Polars DataFrames."""
        detector = NullGhostDetector()
        findings = detector.detect(df)
        assert isinstance(findings, list)


class TestTypeGhostDetector:
    """Property-based tests for TypeGhostDetector."""

    @given(df=dataframe_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_type_detector_never_crashes(self, df: pd.DataFrame) -> None:
        """Test that TypeGhostDetector never crashes on any valid DataFrame."""
        detector = TypeGhostDetector()
        findings = detector.detect(df)

        # Should always return a list
        assert isinstance(findings, list)

        # Each finding should have required attributes
        for finding in findings:
            assert hasattr(finding, "column")
            assert hasattr(finding, "ghost_type")
            assert hasattr(finding, "description")
            assert hasattr(finding, "severity")

    @given(df=dataframe_strategy())
    @settings(
        max_examples=30,
        deadline=5000,
        suppress_health_check=[HealthCheck.data_too_large],
    )
    def test_type_detector_empty_dataframe(self, df: pd.DataFrame) -> None:
        """Test TypeGhostDetector with empty DataFrames."""
        if len(df) == 0:
            detector = TypeGhostDetector()
            findings = detector.detect(df)
            # Should handle empty DataFrame gracefully
            assert isinstance(findings, list)

    @pytest.mark.skipif(pl is None, reason="polars not installed")
    @given(df=polars_dataframe_strategy())
    @settings(max_examples=30, deadline=5000)
    def test_type_detector_polars(self, df: Any) -> None:
        """Test TypeGhostDetector with Polars DataFrames."""
        detector = TypeGhostDetector()
        findings = detector.detect(df)
        assert isinstance(findings, list)


class TestOutlierGhostDetector:
    """Property-based tests for OutlierGhostDetector."""

    @given(df=dataframe_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_outlier_detector_never_crashes(self, df: pd.DataFrame) -> None:
        """Test that OutlierGhostDetector never crashes on any valid DataFrame."""
        detector = OutlierGhostDetector()
        findings = detector.detect(df)

        # Should always return a list
        assert isinstance(findings, list)

        # Each finding should have required attributes
        for finding in findings:
            assert hasattr(finding, "column")
            assert hasattr(finding, "ghost_type")
            assert hasattr(finding, "description")
            assert hasattr(finding, "severity")

    @given(df=dataframe_strategy())
    @settings(
        max_examples=30,
        deadline=5000,
        suppress_health_check=[HealthCheck.data_too_large],
    )
    def test_outlier_detector_empty_dataframe(self, df: pd.DataFrame) -> None:
        """Test OutlierGhostDetector with empty DataFrames."""
        if len(df) == 0:
            detector = OutlierGhostDetector()
            findings = detector.detect(df)
            # Should handle empty DataFrame gracefully
            assert isinstance(findings, list)

    @pytest.mark.skipif(pl is None, reason="polars not installed")
    @given(df=polars_dataframe_strategy())
    @settings(max_examples=30, deadline=5000)
    def test_outlier_detector_polars(self, df: Any) -> None:
        """Test OutlierGhostDetector with Polars DataFrames."""
        detector = OutlierGhostDetector()
        findings = detector.detect(df)
        assert isinstance(findings, list)

    @given(df=dataframe_strategy())
    @settings(max_examples=30, deadline=5000)
    def test_outlier_detector_numeric_columns_only(self, df: pd.DataFrame) -> None:
        """Test OutlierGhostDetector only processes numeric columns."""
        detector = OutlierGhostDetector()
        findings = detector.detect(df)

        # All findings should be from numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns
        for finding in findings:
            assert finding.column in numeric_cols or len(numeric_cols) == 0


class TestDetectorEdgeCases:
    """Test detectors with edge case DataFrames."""

    def test_single_column_dataframe(self) -> None:
        """Test detectors with single-column DataFrames."""
        df = pd.DataFrame({"col1": [1, 2, 3, None, 5]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_all_null_column(self) -> None:
        """Test detectors with columns that are entirely null."""
        df = pd.DataFrame({"col1": [None, None, None]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_single_row_dataframe(self) -> None:
        """Test detectors with single-row DataFrames."""
        df = pd.DataFrame({"col1": [1], "col2": ["a"]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_all_identical_values(self) -> None:
        """Test detectors with columns containing all identical values."""
        df = pd.DataFrame({"col1": [5, 5, 5, 5, 5]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_mixed_numeric_string_types(self) -> None:
        """Test detectors with mixed numeric and string types in same column."""
        df = pd.DataFrame({"col1": [1, "2", 3.0, "4", 5]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_very_large_numbers(self) -> None:
        """Test detectors with very large numbers."""
        df = pd.DataFrame({"col1": [1e10, 2e10, 3e10, 4e10, 5e10]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_negative_numbers(self) -> None:
        """Test detectors with negative numbers."""
        df = pd.DataFrame({"col1": [-10, -5, 0, 5, 10]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)

    def test_boolean_column(self) -> None:
        """Test detectors with boolean columns."""
        df = pd.DataFrame({"col1": [True, False, True, False, True]})

        null_detector = NullGhostDetector()
        type_detector = TypeGhostDetector()
        outlier_detector = OutlierGhostDetector()

        assert isinstance(null_detector.detect(df), list)
        assert isinstance(type_detector.detect(df), list)
        assert isinstance(outlier_detector.detect(df), list)
