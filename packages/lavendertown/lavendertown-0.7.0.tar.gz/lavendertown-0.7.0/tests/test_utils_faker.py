"""Tests for Faker helper utilities."""

from __future__ import annotations

import pandas as pd
import pytest

from lavendertown.utils.faker_helpers import (
    generate_dataframe_with_issues,
    generate_realistic_dataframe,
)


class TestGenerateRealisticDataframe:
    """Tests for generate_realistic_dataframe function."""

    def test_generate_basic_dataframe(self) -> None:
        """Test generating a basic realistic DataFrame."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_realistic_dataframe(
            10, {"name": "name", "email": "email", "age": "int"}, seed=42
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert set(df.columns) == {"name", "email", "age"}
        assert df["name"].dtype == "object"
        assert pd.api.types.is_integer_dtype(df["age"])

    def test_generate_with_different_column_types(self) -> None:
        """Test generating DataFrame with various column types."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        columns = {
            "name": "name",
            "email": "email",
            "birth_date": "date",
            "created_at": "datetime",
            "address": "address",
            "city": "city",
            "phone": "phone",
            "description": "text",
            "value": "float",
            "active": "bool",
        }

        df = generate_realistic_dataframe(20, columns, seed=42)

        assert len(df) == 20
        assert set(df.columns) == set(columns.keys())
        assert pd.api.types.is_string_dtype(df["name"])
        assert pd.api.types.is_string_dtype(df["email"])
        assert pd.api.types.is_bool_dtype(df["active"])

    def test_generate_with_seed_reproducibility(self) -> None:
        """Test that same seed produces same data."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df1 = generate_realistic_dataframe(
            10, {"name": "name", "email": "email"}, seed=42
        )
        df2 = generate_realistic_dataframe(
            10, {"name": "name", "email": "email"}, seed=42
        )

        pd.testing.assert_frame_equal(df1, df2)

    def test_generate_different_seeds_produce_different_data(self) -> None:
        """Test that different seeds produce different data."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df1 = generate_realistic_dataframe(
            10, {"name": "name", "email": "email"}, seed=42
        )
        df2 = generate_realistic_dataframe(
            10, {"name": "name", "email": "email"}, seed=123
        )

        # Data should be different (not equal)
        assert not df1.equals(df2)

    def test_generate_empty_dataframe(self) -> None:
        """Test generating empty DataFrame."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_realistic_dataframe(0, {"name": "name"}, seed=42)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["name"]

    def test_generate_invalid_n_rows(self) -> None:
        """Test that ValueError is raised for invalid n_rows."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        with pytest.raises(ValueError, match="n_rows must be non-negative"):
            generate_realistic_dataframe(-1, {"name": "name"}, seed=42)

    def test_generate_invalid_column_type(self) -> None:
        """Test that ValueError is raised for invalid column type."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        with pytest.raises(ValueError, match="Invalid column types"):
            generate_realistic_dataframe(10, {"col1": "invalid_type"}, seed=42)

    def test_generate_faker_not_installed(self) -> None:
        """Test that ImportError is raised when Faker is not installed."""
        try:
            import faker  # noqa: F401

            # If Faker is installed, skip this test
            pytest.skip("Faker is installed, cannot test fallback without mocking")
        except ImportError:
            # This would only run if Faker is not installed
            with pytest.raises(ImportError, match="Faker is required"):
                generate_realistic_dataframe(10, {"name": "name"}, seed=42)

    def test_generate_large_dataframe(self) -> None:
        """Test generating a large DataFrame."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_realistic_dataframe(
            1000, {"name": "name", "email": "email", "age": "int"}, seed=42
        )

        assert len(df) == 1000
        assert len(df.columns) == 3


class TestGenerateDataframeWithIssues:
    """Tests for generate_dataframe_with_issues function."""

    def test_generate_without_issues(self) -> None:
        """Test generating DataFrame without injected issues."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(20, issue_types=None, seed=42)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20
        assert "name" in df.columns
        assert "email" in df.columns
        assert "age" in df.columns

    def test_generate_with_nulls(self) -> None:
        """Test generating DataFrame with null values injected."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(100, issue_types=["nulls"], seed=42)

        assert isinstance(df, pd.DataFrame)
        # Should have some null values in email column
        assert df["email"].isna().sum() > 0

    def test_generate_with_outliers(self) -> None:
        """Test generating DataFrame with outliers injected."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(100, issue_types=["outliers"], seed=42)

        assert isinstance(df, pd.DataFrame)
        # Should have some outliers in salary column
        max_salary = df["salary"].max()
        mean_salary = df["salary"].mean()
        # Outliers should be much larger than mean
        assert max_salary > mean_salary * 5

    def test_generate_with_type_inconsistency(self) -> None:
        """Test generating DataFrame with type inconsistencies."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(
            100, issue_types=["type_inconsistency"], seed=42
        )

        assert isinstance(df, pd.DataFrame)
        # Should have some invalid values in age column
        # (age should be numeric, but some values will be strings)
        age_column = df["age"]
        # Check if there are string values (type inconsistency)
        has_strings = age_column.astype(str).str.contains("[a-zA-Z]", regex=True).any()
        assert has_strings

    def test_generate_with_multiple_issues(self) -> None:
        """Test generating DataFrame with multiple issue types."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(
            100, issue_types=["nulls", "outliers"], seed=42
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        # Should have both nulls and outliers
        assert df["email"].isna().sum() > 0
        max_salary = df["salary"].max()
        mean_salary = df["salary"].mean()
        assert max_salary > mean_salary * 5

    def test_generate_with_seed_reproducibility(self) -> None:
        """Test that same seed produces same issues."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df1 = generate_dataframe_with_issues(100, issue_types=["nulls"], seed=42)
        df2 = generate_dataframe_with_issues(100, issue_types=["nulls"], seed=42)

        # Should produce same pattern of nulls
        pd.testing.assert_frame_equal(df1, df2)

    def test_generate_invalid_issue_type(self) -> None:
        """Test that invalid issue types are handled."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        # Invalid issue types should be ignored or handled gracefully
        df = generate_dataframe_with_issues(
            20, issue_types=["invalid_issue_type"], seed=42
        )

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20

    def test_generate_empty_issue_types_list(self) -> None:
        """Test generating with empty issue types list."""
        try:
            from faker import Faker  # noqa: F401
        except ImportError:
            pytest.skip("Faker not installed")

        df = generate_dataframe_with_issues(20, issue_types=[], seed=42)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20
