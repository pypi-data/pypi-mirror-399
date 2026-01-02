"""Base class for custom rules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from lavendertown.models import GhostFinding


class CustomRule(ABC):
    """Abstract base class for custom data quality rules.

    Custom rules allow users to define domain-specific data quality checks
    beyond the built-in detectors.
    """

    def __init__(self, name: str, description: str, column: str | None = None):
        """Initialize the custom rule.

        Args:
            name: Human-readable rule name
            description: Rule description
            column: Column to apply rule to (None for cross-column rules)
        """
        self.name = name
        self.description = description
        self.column = column

    @abstractmethod
    def check(self, df: object) -> list[GhostFinding]:
        """Check the rule against a DataFrame.

        Args:
            df: DataFrame to check (Pandas or Polars)

        Returns:
            List of GhostFinding objects for violations
        """
        pass

    def get_name(self) -> str:
        """Get the name of this rule."""
        return self.name
