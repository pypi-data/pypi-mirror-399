"""Tests for drift detection functionality."""

from __future__ import annotations

import pandas as pd
import pytest

from lavendertown.drift.compare import compare_datasets


@pytest.fixture
def baseline_pandas_df() -> pd.DataFrame:
    """Create a baseline Pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5],
            "col2": ["a", "b", "c", None, "e"],
            "col3": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )


@pytest.fixture
def current_pandas_df() -> pd.DataFrame:
    """Create a current Pandas DataFrame for testing."""
    return pd.DataFrame(
        {
            "col1": [1, 2, 3, 4, 5],
            "col2": ["a", "b", "c", None, "e"],
            "col3": [1.1, 2.2, 3.3, 4.4, 5.5],
        }
    )


class TestSchemaComparison:
    """Test schema comparison functionality."""

    def test_no_drift_identical_schemas(self, baseline_pandas_df, current_pandas_df):
        """Test that identical schemas produce no findings."""
        findings = compare_datasets(
            baseline_pandas_df, current_pandas_df, comparison_type="schema_only"
        )
        assert len(findings) == 0

    def test_new_column_detection(self, baseline_pandas_df):
        """Test detection of new columns."""
        current_df = baseline_pandas_df.copy()
        current_df["new_col"] = [10, 20, 30, 40, 50]

        findings = compare_datasets(
            baseline_pandas_df, current_df, comparison_type="schema_only"
        )
        assert len(findings) == 1
        assert findings[0].ghost_type == "drift"
        assert findings[0].column == "new_col"
        assert findings[0].severity == "info"
        assert "New column" in findings[0].description
        assert findings[0].metadata["change_type"] == "column_added"

    def test_removed_column_detection(self, baseline_pandas_df):
        """Test detection of removed columns."""
        current_df = baseline_pandas_df.drop(columns=["col2"])

        findings = compare_datasets(
            baseline_pandas_df, current_df, comparison_type="schema_only"
        )
        assert len(findings) == 1
        assert findings[0].ghost_type == "drift"
        assert findings[0].column == "col2"
        assert findings[0].severity == "warning"
        assert "removed" in findings[0].description.lower()
        assert findings[0].metadata["change_type"] == "column_removed"

    def test_type_change_detection(self, baseline_pandas_df):
        """Test detection of column type changes."""
        current_df = baseline_pandas_df.copy()
        current_df["col1"] = current_df["col1"].astype(float)

        findings = compare_datasets(
            baseline_pandas_df, current_df, comparison_type="schema_only"
        )
        assert len(findings) == 1
        assert findings[0].ghost_type == "drift"
        assert findings[0].column == "col1"
        assert findings[0].severity == "error"
        assert "type changed" in findings[0].description.lower()
        assert findings[0].metadata["change_type"] == "type_change"

    def test_multiple_schema_changes(self, baseline_pandas_df):
        """Test multiple schema changes at once."""
        current_df = baseline_pandas_df.copy()
        current_df["new_col"] = [10, 20, 30, 40, 50]
        current_df = current_df.drop(columns=["col2"])
        current_df["col1"] = current_df["col1"].astype(float)

        findings = compare_datasets(
            baseline_pandas_df, current_df, comparison_type="schema_only"
        )
        assert len(findings) == 3
        # Should have one of each: new column, removed column, type change
        change_types = {f.metadata["change_type"] for f in findings}
        assert "column_added" in change_types
        assert "column_removed" in change_types
        assert "type_change" in change_types


class TestDistributionComparison:
    """Test distribution comparison functionality."""

    def test_no_drift_identical_distributions(
        self, baseline_pandas_df, current_pandas_df
    ):
        """Test that identical distributions produce no findings."""
        findings = compare_datasets(
            baseline_pandas_df, current_pandas_df, comparison_type="distribution_only"
        )
        assert len(findings) == 0

    def test_null_percentage_increase(self, baseline_pandas_df):
        """Test detection of increased null percentage."""
        current_df = baseline_pandas_df.copy()
        current_df.loc[0:2, "col2"] = None  # Increase nulls from 20% to 60%

        findings = compare_datasets(
            baseline_pandas_df,
            current_df,
            comparison_type="distribution_only",
            distribution_threshold=5.0,
        )
        # Should detect null percentage change
        null_findings = [
            f for f in findings if f.metadata.get("change_type") == "null_percentage"
        ]
        assert len(null_findings) > 0
        assert null_findings[0].column == "col2"
        assert "increased" in null_findings[0].description.lower()

    def test_numeric_range_shift(self, baseline_pandas_df):
        """Test detection of numeric range shifts."""
        current_df = baseline_pandas_df.copy()
        current_df["col3"] = [10.0, 20.0, 30.0, 40.0, 50.0]  # Shift range significantly

        findings = compare_datasets(
            baseline_pandas_df,
            current_df,
            comparison_type="distribution_only",
            distribution_threshold=5.0,
        )
        # Should detect range shift
        range_findings = [
            f for f in findings if f.metadata.get("change_type") == "numeric_range"
        ]
        assert len(range_findings) > 0
        assert range_findings[0].column == "col3"
        assert "range shifted" in range_findings[0].description.lower()

    def test_cardinality_change(self, baseline_pandas_df):
        """Test detection of cardinality changes."""
        current_df = baseline_pandas_df.copy()
        current_df["col2"] = ["x", "y", "z", "w", "v"]  # Different unique values

        findings = compare_datasets(
            baseline_pandas_df,
            current_df,
            comparison_type="distribution_only",
            distribution_threshold=5.0,
        )
        # Should detect cardinality change
        cardinality_findings = [
            f for f in findings if f.metadata.get("change_type") == "cardinality"
        ]
        assert len(cardinality_findings) > 0
        assert cardinality_findings[0].column == "col2"


class TestFullComparison:
    """Test full comparison (schema + distribution)."""

    def test_full_comparison(self, baseline_pandas_df):
        """Test full comparison detects both schema and distribution changes."""
        current_df = baseline_pandas_df.copy()
        current_df["new_col"] = [10, 20, 30, 40, 50]  # Schema change
        current_df.loc[0:2, "col2"] = None  # Distribution change

        findings = compare_datasets(
            baseline_pandas_df,
            current_df,
            comparison_type="full",
            distribution_threshold=5.0,
        )
        assert len(findings) >= 2
        # Should have schema findings
        schema_findings = [
            f for f in findings if f.metadata.get("drift_type") == "schema"
        ]
        assert len(schema_findings) > 0
        # Should have distribution findings
        dist_findings = [
            f for f in findings if f.metadata.get("drift_type") == "distribution"
        ]
        assert len(dist_findings) > 0

    def test_schema_only_comparison(self, baseline_pandas_df):
        """Test schema-only comparison."""
        current_df = baseline_pandas_df.copy()
        current_df["new_col"] = [10, 20, 30, 40, 50]
        current_df.loc[0:2, "col2"] = None

        findings = compare_datasets(
            baseline_pandas_df, current_df, comparison_type="schema_only"
        )
        # Should only have schema findings
        assert all(f.metadata.get("drift_type") == "schema" for f in findings)

    def test_distribution_only_comparison(self, baseline_pandas_df):
        """Test distribution-only comparison."""
        current_df = baseline_pandas_df.copy()
        current_df["new_col"] = [10, 20, 30, 40, 50]
        current_df.loc[0:2, "col2"] = None

        findings = compare_datasets(
            baseline_pandas_df,
            current_df,
            comparison_type="distribution_only",
            distribution_threshold=5.0,
        )
        # Should only have distribution findings
        assert all(f.metadata.get("drift_type") == "distribution" for f in findings)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframes(self):
        """Test comparison with empty DataFrames."""
        baseline_df = pd.DataFrame()
        current_df = pd.DataFrame()

        findings = compare_datasets(baseline_df, current_df)
        # Should handle gracefully
        assert isinstance(findings, list)

    def test_empty_baseline(self, baseline_pandas_df):
        """Test comparison with empty baseline."""
        baseline_df = pd.DataFrame()
        current_df = baseline_pandas_df.copy()

        findings = compare_datasets(baseline_df, current_df)
        # Should detect all columns as new
        assert len(findings) > 0
        assert all(f.metadata.get("change_type") == "column_added" for f in findings)

    def test_empty_current(self, baseline_pandas_df):
        """Test comparison with empty current."""
        baseline_df = baseline_pandas_df.copy()
        current_df = pd.DataFrame()

        findings = compare_datasets(baseline_df, current_df)
        # Should detect all columns as removed
        assert len(findings) > 0
        assert all(f.metadata.get("change_type") == "column_removed" for f in findings)

    def test_polars_support(self):
        """Test Polars DataFrame support."""
        try:
            import polars as pl

            baseline_df = pl.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
            current_df = pl.DataFrame(
                {"col1": [1, 2, 3], "col2": ["a", "b", "c"], "col3": [10, 20, 30]}
            )

            findings = compare_datasets(
                baseline_df, current_df, comparison_type="schema_only"
            )
            assert len(findings) == 1
            assert findings[0].column == "col3"

        except ImportError:
            pytest.skip("Polars not installed")
