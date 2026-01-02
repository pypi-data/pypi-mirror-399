"""Rule-based detector that executes CustomRule instances."""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector
from lavendertown.models import GhostFinding
from lavendertown.rules.base import CustomRule


class RuleBasedDetector(GhostDetector):
    """Detector that executes CustomRule instances and converts violations to findings.

    This detector wraps CustomRule instances and integrates them into the
    standard detection workflow.
    """

    def __init__(self, rule: CustomRule) -> None:
        """Initialize the rule-based detector.

        Args:
            rule: CustomRule instance to execute
        """
        self.rule = rule

    def detect(self, df: object) -> list[GhostFinding]:
        """Execute the rule and return findings.

        Args:
            df: DataFrame to check

        Returns:
            List of GhostFinding objects from rule violations
        """
        return self.rule.check(df)

    def get_name(self) -> str:
        """Get the name of this detector (uses rule name)."""
        return f"Rule: {self.rule.get_name()}"
