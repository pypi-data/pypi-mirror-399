"""Rule-based detector that executes CustomRule instances.

This module provides the RuleBasedDetector class, which wraps CustomRule
instances and integrates them into the standard ghost detection workflow.
This allows custom rules to be executed alongside built-in detectors.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector
from lavendertown.models import GhostFinding
from lavendertown.rules.base import CustomRule


class RuleBasedDetector(GhostDetector):
    """Detector that executes CustomRule instances and converts violations to findings.

    This detector wraps CustomRule instances and integrates them into the
    standard detection workflow. It allows custom user-defined rules to be
    executed alongside built-in detectors like NullGhostDetector and
    OutlierGhostDetector.

    When a CustomRule's check() method is called, any violations are returned
    as GhostFinding objects with ghost_type="rule", making them compatible
    with the rest of the LavenderTown infrastructure.

    Attributes:
        rule: The CustomRule instance to execute.

    Example:
        Wrap a custom rule for use with Inspector::

            from lavendertown.detectors.rule_based import RuleBasedDetector
            from lavendertown.rules.executors import RangeRule
            from lavendertown import Inspector

            rule = RangeRule("price_check", "Check price range", "price",
                            min_value=0.0, max_value=1000.0)
            detector = RuleBasedDetector(rule)

            inspector = Inspector(df, detectors=[detector])
            findings = inspector.detect()
    """

    def __init__(self, rule: CustomRule) -> None:
        """Initialize the rule-based detector.

        Args:
            rule: CustomRule instance to execute. The rule's check() method
                will be called during detection, and violations will be
                converted to GhostFinding objects.
        """
        self.rule = rule

    def detect(self, df: object) -> list[GhostFinding]:
        """Execute the rule and return findings.

        Calls the wrapped CustomRule's check() method and returns the resulting
        GhostFinding objects. All findings will have ghost_type="rule".

        Args:
            df: DataFrame to check. Can be a pandas.DataFrame or
                polars.DataFrame. The rule should handle backend detection
                internally.

        Returns:
            List of GhostFinding objects representing rule violations.
            Returns an empty list if no violations are found.
        """
        return self.rule.check(df)

    def get_name(self) -> str:
        """Get the name of this detector (uses rule name).

        Returns a formatted name that includes the rule's name, making it
        clear that this is a rule-based detector.

        Returns:
            String name in the format "Rule: {rule_name}".
        """
        return f"Rule: {self.rule.get_name()}"
