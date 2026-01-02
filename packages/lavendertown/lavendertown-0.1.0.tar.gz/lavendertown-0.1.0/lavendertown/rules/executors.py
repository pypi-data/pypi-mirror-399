"""Rule executors for common rule types."""

from __future__ import annotations

import re

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.models import GhostFinding
from lavendertown.rules.base import CustomRule


class RangeRule(CustomRule):
    """Rule for checking numeric values within a range."""

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
            name: Rule name
            description: Rule description
            column: Column to check
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
        """
        super().__init__(name, description, column)
        self.min_value = min_value
        self.max_value = max_value

        if min_value is None and max_value is None:
            raise ValueError("At least one of min_value or max_value must be specified")

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values are within the specified range."""
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

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

            violation_indices = sorted(set(violations))
        else:
            import polars as pl

            column_data = df.select(pl.col(self.column or "").drop_nulls())  # type: ignore[attr-defined,arg-type]
            conditions = []

            if self.min_value is not None:
                conditions.append(pl.col(self.column or "") < self.min_value)  # type: ignore[arg-type]
            if self.max_value is not None:
                conditions.append(pl.col(self.column or "") > self.max_value)  # type: ignore[arg-type]

            if conditions:
                # Check for violations (Polars doesn't preserve original indices easily)
                # Polars doesn't preserve original indices easily, so we'll return None
                violation_indices = None
            else:
                violation_indices = None

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
                    column=self.column or "",
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
            findings.append(
                GhostFinding(
                    ghost_type="rule",
                    column=self.column or "",
                    severity="error",
                    description=f"{self.description} - Found values outside specified range",
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
    """Rule for checking string values against a regex pattern."""

    def __init__(self, name: str, description: str, column: str, pattern: str):
        """Initialize regex rule.

        Args:
            name: Rule name
            description: Rule description
            column: Column to check
            pattern: Regex pattern to match against
        """
        super().__init__(name, description, column)
        self.pattern = pattern
        self.compiled_pattern = re.compile(pattern)

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values match the regex pattern."""
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

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
                    column=self.column or "",
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
    """Rule for checking values against an allowed set."""

    def __init__(
        self, name: str, description: str, column: str, allowed_values: list[str]
    ):
        """Initialize enum rule.

        Args:
            name: Rule name
            description: Rule description
            column: Column to check
            allowed_values: List of allowed values
        """
        super().__init__(name, description, column)
        self.allowed_values = set(allowed_values)

    def check(self, df: object) -> list[GhostFinding]:
        """Check if values are in the allowed set."""
        findings: list[GhostFinding] = []

        backend = detect_dataframe_backend(df)

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
                    column=self.column or "",
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
