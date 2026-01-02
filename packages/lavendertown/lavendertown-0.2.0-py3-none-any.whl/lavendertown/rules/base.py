"""Base class for custom rules.

This module provides the CustomRule abstract base class, which allows users
to define domain-specific data quality checks beyond the built-in detectors.
Custom rules can validate ranges, patterns, enumerations, or any other
domain-specific constraints.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from lavendertown.models import GhostFinding


class CustomRule(ABC):
    """Abstract base class for custom data quality rules.

    Custom rules allow users to define domain-specific data quality checks
    beyond the built-in detectors. They implement a check() method that
    analyzes a DataFrame and returns GhostFinding objects for any violations.

    Rules can be single-column (applying to a specific column) or cross-column
    (applying logic across multiple columns or the entire DataFrame). They
    should handle both Pandas and Polars DataFrames by detecting the backend
    and using the appropriate API.

    Subclasses must implement the check() method. Common rule types are
    provided in lavendertown.rules.executors (RangeRule, RegexRule, EnumRule).

    Attributes:
        name: Human-readable name of the rule.
        description: Description of what the rule checks.
        column: Column name to apply the rule to, or None for cross-column rules.

    Example:
        Implement a custom rule::

            from lavendertown.rules.base import CustomRule
            from lavendertown.models import GhostFinding
            from lavendertown.detectors.base import detect_dataframe_backend

            class PositiveValueRule(CustomRule):
                def __init__(self, column: str):
                    super().__init__("positive_values", "Check for positive values", column)

                def check(self, df):
                    backend = detect_dataframe_backend(df)
                    findings = []
                    # Check for negative values
                    # ... detection logic ...
                    return findings
    """

    def __init__(self, name: str, description: str, column: str | None = None):
        """Initialize the custom rule.

        Args:
            name: Human-readable rule name. Should be unique within a rule set.
            description: Rule description explaining what the rule checks.
                This description may be included in finding descriptions.
            column: Column name to apply the rule to. Use None for cross-column
                rules that don't apply to a specific column.
        """
        self.name = name
        self.description = description
        self.column = column

    @abstractmethod
    def check(self, df: object) -> list[GhostFinding]:
        """Check the rule against a DataFrame.

        This is the main method that subclasses must implement. It should
        analyze the DataFrame according to the rule's logic and return
        findings for any violations.

        Args:
            df: DataFrame to check. Can be a pandas.DataFrame or
                polars.DataFrame. The rule should use
                ``detect_dataframe_backend()`` to determine which API to use.

        Returns:
            List of GhostFinding objects representing rule violations.
            All findings should have ghost_type="rule". Returns an empty
            list if no violations are found.

        Note:
            Rules should handle both Pandas and Polars DataFrames. Use
            ``detect_dataframe_backend()`` to determine the backend and
            use the appropriate API.
        """
        pass

    def get_name(self) -> str:
        """Get the name of this rule.

        Returns:
            The rule's name as specified during initialization.
        """
        return self.name
