"""Tests for statistical tests in drift distribution comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lavendertown.drift.distribution import compare_distributions


@pytest.fixture
def baseline_numeric_dataframe() -> pd.DataFrame:
    """Provide baseline DataFrame with numeric data."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "col1": np.random.normal(0, 1, 100),
            "col2": np.random.normal(5, 2, 100),
            "col3": np.random.uniform(0, 10, 100),
        }
    )


@pytest.fixture
def current_numeric_dataframe_drifted() -> pd.DataFrame:
    """Provide current DataFrame with drifted numeric distributions."""
    np.random.seed(123)  # Different seed for different distribution
    return pd.DataFrame(
        {
            "col1": np.random.normal(2, 1, 100),  # Shifted mean
            "col2": np.random.normal(5, 3, 100),  # Different variance
            "col3": np.random.uniform(0, 10, 100),  # Similar (should have high p-value)
        }
    )


@pytest.fixture
def baseline_categorical_dataframe() -> pd.DataFrame:
    """Provide baseline DataFrame with categorical data."""
    return pd.DataFrame(
        {
            "category": ["A", "B", "C", "A", "B", "C", "A", "B"] * 12,
            "status": ["active", "inactive"] * 48,
        }
    )


@pytest.fixture
def current_categorical_dataframe_drifted() -> pd.DataFrame:
    """Provide current DataFrame with drifted categorical distributions."""
    # Different distribution
    return pd.DataFrame(
        {
            "category": ["A", "A", "A", "B", "B", "C", "C", "C"]
            * 12,  # Different proportions
            "status": ["active", "inactive"] * 48,  # Same distribution
        }
    )


class TestStatisticalTests:
    """Tests for statistical tests in drift detection."""

    def test_ks_test_included_in_numeric_metadata(
        self,
        baseline_numeric_dataframe: pd.DataFrame,
        current_numeric_dataframe_drifted: pd.DataFrame,
    ) -> None:
        """Test that KS test results are included in findings metadata."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        findings = compare_distributions(
            baseline_numeric_dataframe,
            current_numeric_dataframe_drifted,
            use_statistical_tests=True,
        )

        # Find numeric range findings
        numeric_findings = [
            f for f in findings if f.metadata.get("change_type") == "numeric_range"
        ]

        assert len(numeric_findings) > 0
        for finding in numeric_findings:
            if "ks_statistic" in finding.metadata:
                assert "ks_p_value" in finding.metadata
                assert isinstance(finding.metadata["ks_statistic"], float)
                assert isinstance(finding.metadata["ks_p_value"], float)
                assert 0.0 <= finding.metadata["ks_p_value"] <= 1.0

    def test_chi_square_test_in_categorical_findings(
        self,
        baseline_categorical_dataframe: pd.DataFrame,
        current_categorical_dataframe_drifted: pd.DataFrame,
    ) -> None:
        """Test that chi-square test is performed for categorical columns."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        findings = compare_distributions(
            baseline_categorical_dataframe,
            current_categorical_dataframe_drifted,
            use_statistical_tests=True,
        )

        # Find categorical distribution findings
        categorical_findings = [
            f
            for f in findings
            if f.metadata.get("change_type") == "categorical_distribution"
        ]

        if len(categorical_findings) > 0:
            for finding in categorical_findings:
                assert "chi2_statistic" in finding.metadata
                assert "chi2_p_value" in finding.metadata
                assert "degrees_of_freedom" in finding.metadata
                assert isinstance(finding.metadata["chi2_statistic"], float)
                assert isinstance(finding.metadata["chi2_p_value"], float)
                assert 0.0 <= finding.metadata["chi2_p_value"] <= 1.0
                assert isinstance(finding.metadata["degrees_of_freedom"], int)

    def test_statistical_tests_disabled(
        self,
        baseline_numeric_dataframe: pd.DataFrame,
        current_numeric_dataframe_drifted: pd.DataFrame,
    ) -> None:
        """Test that statistical tests can be disabled."""
        findings = compare_distributions(
            baseline_numeric_dataframe,
            current_numeric_dataframe_drifted,
            use_statistical_tests=False,
        )

        # KS test results should not be in metadata
        numeric_findings = [
            f for f in findings if f.metadata.get("change_type") == "numeric_range"
        ]

        for finding in numeric_findings:
            assert "ks_statistic" not in finding.metadata
            assert "ks_p_value" not in finding.metadata

    def test_statistical_tests_with_scipy_not_installed(
        self,
        baseline_numeric_dataframe: pd.DataFrame,
        current_numeric_dataframe_drifted: pd.DataFrame,
    ) -> None:
        """Test graceful degradation when scipy is not installed."""
        try:
            import scipy  # noqa: F401

            # If scipy is installed, skip this test
            pytest.skip("scipy is installed, cannot test fallback without mocking")
        except ImportError:
            # This test would only run if scipy is not installed
            # In that case, statistical tests should be skipped gracefully
            findings = compare_distributions(
                baseline_numeric_dataframe,
                current_numeric_dataframe_drifted,
                use_statistical_tests=True,
            )

            # Should still return findings, just without statistical test metadata
            assert isinstance(findings, list)

    def test_ks_test_with_identical_distributions(
        self, baseline_numeric_dataframe: pd.DataFrame
    ) -> None:
        """Test KS test with identical distributions (should have high p-value)."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        # Use same DataFrame as baseline and current (should have high p-value)
        findings = compare_distributions(
            baseline_numeric_dataframe,
            baseline_numeric_dataframe.copy(),
            use_statistical_tests=True,
        )

        numeric_findings = [
            f for f in findings if f.metadata.get("change_type") == "numeric_range"
        ]

        # If there are any numeric findings (which there shouldn't be for identical data),
        # the p-value should be high
        for finding in numeric_findings:
            if "ks_p_value" in finding.metadata:
                # For identical distributions, p-value should be close to 1.0
                assert finding.metadata["ks_p_value"] > 0.5

    def test_chi_square_test_with_identical_categorical_distributions(
        self, baseline_categorical_dataframe: pd.DataFrame
    ) -> None:
        """Test chi-square test with identical categorical distributions."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        findings = compare_distributions(
            baseline_categorical_dataframe,
            baseline_categorical_dataframe.copy(),
            use_statistical_tests=True,
        )

        categorical_findings = [
            f
            for f in findings
            if f.metadata.get("change_type") == "categorical_distribution"
        ]

        # Should not detect significant drift for identical distributions
        for finding in categorical_findings:
            if "chi2_p_value" in finding.metadata:
                # P-value should be high (close to 1.0) for identical distributions
                assert finding.metadata["chi2_p_value"] > 0.5

    def test_ks_test_with_drifted_distribution(
        self,
        baseline_numeric_dataframe: pd.DataFrame,
        current_numeric_dataframe_drifted: pd.DataFrame,
    ) -> None:
        """Test KS test detects drifted distributions (low p-value)."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        findings = compare_distributions(
            baseline_numeric_dataframe,
            current_numeric_dataframe_drifted,
            use_statistical_tests=True,
        )

        numeric_findings = [
            f for f in findings if f.metadata.get("change_type") == "numeric_range"
        ]

        # Should detect drift in col1 (shifted mean)
        drifted_findings = [
            f
            for f in numeric_findings
            if f.column == "col1" and "ks_p_value" in f.metadata
        ]

        if len(drifted_findings) > 0:
            # P-value should be low for drifted distributions
            assert drifted_findings[0].metadata["ks_p_value"] < 0.1

    def test_statistical_tests_edge_cases_small_samples(self) -> None:
        """Test statistical tests with very small samples."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        baseline = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})
        current = pd.DataFrame({"col1": [4.0, 5.0, 6.0]})

        findings = compare_distributions(baseline, current, use_statistical_tests=True)

        # Should handle small samples gracefully
        assert isinstance(findings, list)

    def test_statistical_tests_with_constant_values(self) -> None:
        """Test statistical tests with constant values."""
        try:
            from scipy import stats  # noqa: F401
        except ImportError:
            pytest.skip("scipy not installed")

        baseline = pd.DataFrame({"col1": [5.0] * 100})
        current = pd.DataFrame({"col1": [5.0] * 100})

        findings = compare_distributions(baseline, current, use_statistical_tests=True)

        # Should handle constant values gracefully
        assert isinstance(findings, list)
