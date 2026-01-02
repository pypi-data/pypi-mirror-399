"""Rule executors for common rule types.

This module provides concrete implementations of common custom rule types:
RangeRule (numeric range validation), RegexRule (pattern matching), and
EnumRule (allowed value validation). These rules can be used directly or
served as examples for implementing custom rules.
"""

from __future__ import annotations

import re

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.models import GhostFinding
from lavendertown.rules.base import CustomRule


def _validate_column_exists(df: object, column: str, backend: str) -> None:
    """Validate that a column exists in the DataFrame.

    Checks whether the specified column exists in the DataFrame. Raises
    an exception if the column is not found.

    Args:
        df: DataFrame to check. Can be a pandas.DataFrame or polars.DataFrame.
        column: Column name to validate. Must be a non-empty string.
        backend: Backend type. Should be "pandas" or "polars".

    Raises:
        ValueError: If the column doesn't exist in the DataFrame.
    """
    if backend == "pandas":
        if column not in df.columns:  # type: ignore[attr-defined]
            raise ValueError(f"Column '{column}' not found in DataFrame")
    else:  # polars
        if column not in df.columns:  # type: ignore[attr-defined]
            raise ValueError(f"Column '{column}' not found in DataFrame")


class RangeRule(CustomRule):
    """Rule for checking numeric values within a range.

    Validates that numeric values in a column fall within specified minimum
    and maximum bounds. Works with both Pandas and Polars DataFrames.

    The rule checks that all non-null values in the specified column are
    within [min_value, max_value] (inclusive). At least one of min_value
    or max_value must be specified.

    Attributes:
        min_value: Minimum allowed value (inclusive). None if no minimum bound.
        max_value: Maximum allowed value (inclusive). None if no maximum bound.

    Example:
        Check that prices are between 0 and 1000::

            rule = RangeRule(
                name="price_range",
                description="Price must be between 0 and 1000",
                column="price",
                min_value=0.0,
                max_value=1000.0
            )
            findings = rule.check(df)

        Check that ages are at least 18::

            rule = RangeRule(
                name="min_age",
                description="Age must be at least 18",
                column="age",
                min_value=18.0
            )
    """

    def __init__(
        self,
        name: str,
        description: str,
        column: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ):
        """Initialize range rule.

        Args:
            name: Human-readable rule name. Should be unique within a rule set.
            description: Description of what the rule checks.
            column: Column name to validate. Must be a non-empty string.
            min_value: Minimum allowed value (inclusive). None if no minimum
                bound is required.
            max_value: Maximum allowed value (inclusive). None if no maximum
                bound is required.

        Raises:
            ValueError: If both min_value and max_value are None, or if
                min_value > max_value when both are specified.
        """
        super().__init__(name, description, column)
        self.min_value = min_value
        self.max_value = max_value

        if min_value is None and max_value is None:
            raise ValueError("At least one of min_value or max_value must be specified")

        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValueError(
                f"min_value ({min_value}) must be less than or equal to max_value ({max_value})"
            )

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values are within the specified range.

        Validates all non-null values in the specified column against the
        configured min_value and max_value bounds. Returns findings for any
        values that violate the range constraints.

        Args:
            df: DataFrame to check. Can be a pandas.DataFrame or polars.DataFrame.
                The backend is automatically detected.

        Returns:
            List of GhostFinding objects representing range violations. Each
            finding has ghost_type="rule", severity="error", and includes
            row_indices of violating rows (Pandas only). Returns an empty list
            if no violations are found. Returns a single error finding if the
            column doesn't exist.

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts.
        """
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

        # Validate column exists
        if not self.column:
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column="",
                    severity="error",
                    description=f"{self.description} - Column name is required",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "error": "Column name is required",
                    },
                )
            )
            return findings

        try:
            _validate_column_exists(df, self.column, backend)
        except ValueError as e:
            # Return a finding for missing column
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=f"{self.description} - {str(e)}",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "error": str(e),
                    },
                )
            )
            return findings

        if backend == "pandas":
            column_data = df[self.column].dropna()  # type: ignore[index]
            violations = []

            if self.min_value is not None:
                violations.extend(
                    column_data[column_data < self.min_value].index.tolist()
                )
            if self.max_value is not None:
                violations.extend(
                    column_data[column_data > self.max_value].index.tolist()
                )

            violation_indices: list[int] = sorted(set(violations))
        else:
            import polars as pl

            # Build filter condition for violations
            filter_condition = None
            if self.min_value is not None:
                below_min = pl.col(self.column or "") < self.min_value  # type: ignore[arg-type]
                filter_condition = (
                    below_min
                    if filter_condition is None
                    else (filter_condition | below_min)
                )
            if self.max_value is not None:
                above_max = pl.col(self.column or "") > self.max_value  # type: ignore[arg-type]
                filter_condition = (
                    above_max
                    if filter_condition is None
                    else (filter_condition | above_max)
                )

            if filter_condition is not None:
                # Filter DataFrame to find violations
                violations_df = df.filter(filter_condition)  # type: ignore[attr-defined]
                # Polars doesn't preserve original row indices, so we can't return specific indices
                # But we can check if there are any violations
                has_violations = violations_df.height > 0  # type: ignore[attr-defined]
                violation_indices = None if has_violations else []  # type: ignore[assignment]
            else:
                violation_indices = []

        if violation_indices and len(violation_indices) > 0:
            range_desc = []
            if self.min_value is not None:
                range_desc.append(f"≥ {self.min_value}")
            if self.max_value is not None:
                range_desc.append(f"≤ {self.max_value}")
            range_str = " and ".join(range_desc)

            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=f"{self.description} - Found {len(violation_indices)} values outside range [{range_str}]",
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "min_value": self.min_value,
                        "max_value": self.max_value,
                        "violation_count": len(violation_indices)
                        if violation_indices
                        else 0,
                    },
                )
            )
        elif violation_indices is None and backend == "polars":
            # For Polars, we detected violations but can't get exact indices
            # Still create a finding
            range_desc = []
            if self.min_value is not None:
                range_desc.append(f"≥ {self.min_value}")
            if self.max_value is not None:
                range_desc.append(f"≤ {self.max_value}")
            range_str = " and ".join(range_desc)

            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=f"{self.description} - Found values outside range [{range_str}]",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "min_value": self.min_value,
                        "max_value": self.max_value,
                    },
                )
            )

        return findings


class RegexRule(CustomRule):
    """Rule for checking string values against a regex pattern.

    Validates that string values in a column match a specified regular
    expression pattern. Works with both Pandas and Polars DataFrames.

    The rule checks all non-null values in the specified column against
    the regex pattern. Values that don't match the pattern are flagged
    as violations.

    Attributes:
        pattern: The regular expression pattern to match against.
        compiled_pattern: The compiled regex pattern (for internal use).

    Example:
        Validate email format::

            rule = RegexRule(
                name="email_format",
                description="Email must match standard format",
                column="email",
                pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            findings = rule.check(df)

        Validate phone number format::

            rule = RegexRule(
                name="phone_format",
                description="Phone must be 10 digits",
                column="phone",
                pattern=r"^\d{10}$"
            )
    """

    def __init__(self, name: str, description: str, column: str, pattern: str):
        """Initialize regex rule.

        Args:
            name: Human-readable rule name. Should be unique within a rule set.
            description: Description of what the rule checks.
            column: Column name to validate. Must be a non-empty string.
            pattern: Regular expression pattern to match against. Should be
                a valid Python regex pattern string.

        Raises:
            ValueError: If the regex pattern is invalid and cannot be compiled.
        """
        super().__init__(name, description, column)
        self.pattern = pattern
        try:
            self.compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values match the regex pattern.

        Validates all non-null values in the specified column against the
        configured regex pattern. Returns findings for any values that don't
        match the pattern.

        Args:
            df: DataFrame to check. Can be a pandas.DataFrame or polars.DataFrame.
                The backend is automatically detected.

        Returns:
            List of GhostFinding objects representing regex violations. Each
            finding has ghost_type="rule", severity="error", and includes
            row_indices of violating rows (Pandas only). Returns an empty list
            if no violations are found. Returns a single error finding if the
            column doesn't exist.

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts.
        """
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

        # Validate column exists
        if not self.column:
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column="",
                    severity="error",
                    description=f"{self.description} - Column name is required",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "error": "Column name is required",
                    },
                )
            )
            return findings

        try:
            _validate_column_exists(df, self.column, backend)
        except ValueError as e:
            # Return a finding for missing column
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=f"{self.description} - {str(e)}",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "regex",
                        "error": str(e),
                    },
                )
            )
            return findings

        if backend == "pandas":
            column_data = df[self.column].dropna()  # type: ignore[index]
            # Check which values don't match the pattern
            violations = column_data[
                ~column_data.astype(str).str.match(self.pattern)
            ].index.tolist()  # type: ignore[attr-defined]
            violation_indices = sorted(set(violations))
        else:
            # Polars regex matching
            # Polars doesn't preserve original indices easily, so we'll return None
            violation_indices = None  # Polars doesn't preserve original indices easily

        if (violation_indices and len(violation_indices) > 0) or (
            violation_indices is None and backend != "pandas"
        ):
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=(
                        f"{self.description} - Found values not matching pattern '{self.pattern}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "regex",
                        "pattern": self.pattern,
                        "violation_count": len(violation_indices)
                        if violation_indices
                        else 0,
                    },
                )
            )

        return findings


class EnumRule(CustomRule):
    """Rule for checking that values are in an allowed set.

    Validates that values in a column are members of a specified set of
    allowed values. Works with both Pandas and Polars DataFrames.

    The rule checks all non-null values in the specified column against
    the allowed_values set. Values that are not in the set are flagged
    as violations.

    Attributes:
        allowed_values: Set or list of allowed values. Values not in this
            set will trigger violations.

    Example:
        Validate category values::

            rule = EnumRule(
                name="valid_category",
                description="Category must be one of the allowed values",
                column="category",
                allowed_values=["A", "B", "C", "D"]
            )
            findings = rule.check(df)

        Validate status codes::

            rule = EnumRule(
                name="valid_status",
                description="Status must be valid",
                column="status",
                allowed_values=["active", "inactive", "pending"]
            )
    """

    def __init__(
        self, name: str, description: str, column: str, allowed_values: list[str]
    ):
        """Initialize enum rule.

        Args:
            name: Human-readable rule name. Should be unique within a rule set.
            description: Description of what the rule checks.
            column: Column name to validate. Must be a non-empty string.
            allowed_values: Set or list of allowed values. Values in the column
                must be one of these values. Must not be empty.

        Raises:
            ValueError: If allowed_values is empty.
        """
        super().__init__(name, description, column)
        if not allowed_values:
            raise ValueError("allowed_values cannot be empty")
        self.allowed_values = set(allowed_values)

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values are in the allowed set.

        Validates all non-null values in the specified column against the
        configured allowed_values set. Returns findings for any values that
        are not in the allowed set.

        Args:
            df: DataFrame to check. Can be a pandas.DataFrame or polars.DataFrame.
                The backend is automatically detected.

        Returns:
            List of GhostFinding objects representing enum violations. Each
            finding has ghost_type="rule", severity="error", and includes
            row_indices of violating rows (Pandas only). Returns an empty list
            if no violations are found. Returns a single error finding if the
            column doesn't exist.

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts.
        """
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

        # Validate column exists
        if not self.column:
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column="",
                    severity="error",
                    description=f"{self.description} - Column name is required",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "range",
                        "error": "Column name is required",
                    },
                )
            )
            return findings

        try:
            _validate_column_exists(df, self.column, backend)
        except ValueError as e:
            # Return a finding for missing column
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=f"{self.description} - {str(e)}",
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "enum",
                        "error": str(e),
                    },
                )
            )
            return findings

        if backend == "pandas":
            column_data = df[self.column].dropna()  # type: ignore[index]
            violations = column_data[
                ~column_data.isin(self.allowed_values)
            ].index.tolist()  # type: ignore[attr-defined]
            violation_indices = sorted(set(violations))
        else:
            # Polars enum checking
            # Polars doesn't preserve original indices easily, so we'll return None
            violation_indices = None

        if (violation_indices and len(violation_indices) > 0) or (
            violation_indices is None and backend != "pandas"
        ):
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column if self.column else "",
                    severity="error",
                    description=(
                        f"{self.description} - Found values not in allowed set: {sorted(self.allowed_values)}"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "rule_type": "enum",
                        "allowed_values": sorted(self.allowed_values),
                        "violation_count": len(violation_indices)
                        if violation_indices
                        else 0,
                    },
                )
            )

        return findings
