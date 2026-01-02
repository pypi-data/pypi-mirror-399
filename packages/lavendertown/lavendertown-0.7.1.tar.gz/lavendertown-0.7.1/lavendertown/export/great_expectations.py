"""Great Expectations exporter for LavenderTown rules."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lavendertown.rules.models import RuleSet

try:
    from great_expectations.core import ExpectationSuite
    from great_expectations.expectations.expectation_configuration import (
        ExpectationConfiguration,
    )
except ImportError:
    ExpectationSuite = None  # type: ignore[assignment,misc]
    ExpectationConfiguration = None  # type: ignore[assignment,misc]


def export_ruleset_to_great_expectations(
    ruleset: RuleSet,
    suite_name: str | None = None,
) -> ExpectationSuite:
    """Export a RuleSet to a Great Expectations ExpectationSuite.

    Converts LavenderTown rules to Great Expectations expectations:
    - Range rules -> expect_column_values_to_be_between()
    - Regex rules -> expect_column_values_to_match_regex()
    - Enum rules -> expect_column_values_to_be_in_set()

    Args:
        ruleset: RuleSet to export
        suite_name: Name for the expectation suite (defaults to ruleset name)

    Returns:
        Great Expectations ExpectationSuite object

    Raises:
        ImportError: If great_expectations is not installed
        ValueError: If unsupported rule types are encountered or no valid rules found

    Example:
        >>> from lavendertown.rules.models import RuleSet, Rule
        >>> ruleset = RuleSet(
        ...     name="test",
        ...     description="Test rules",
        ...     rules=[
        ...         Rule(
        ...             name="age_range",
        ...             description="Age must be 0-150",
        ...             rule_type="range",
        ...             column="age",
        ...             parameters={"min_value": 0, "max_value": 150},
        ...         )
        ...     ],
        ... )
        >>> suite = export_ruleset_to_great_expectations(ruleset)
        >>> type(suite)
        <class 'great_expectations.core.expectation_suite.ExpectationSuite'>
    """
    if ExpectationSuite is None or ExpectationConfiguration is None:
        raise ImportError(
            "great_expectations is required for Great Expectations export. "
            "Install it with: pip install lavendertown[great_expectations]"
        )

    if not ruleset.rules:
        raise ValueError("Cannot export empty RuleSet to ExpectationSuite")

    suite_name = suite_name or ruleset.name or "lavendertown_suite"

    # Create expectation configurations
    expectations: list[ExpectationConfiguration] = []

    for rule in ruleset.rules:
        if not rule.enabled:
            continue

        if rule.column is None:
            raise ValueError(
                f"Rule '{rule.name}' has no column - cross-column rules are not supported in Great Expectations export"
            )

        expectation_config = None

        if rule.rule_type == "range":
            min_val = rule.parameters.get("min_value")
            max_val = rule.parameters.get("max_value")

            if min_val is not None or max_val is not None:
                expectation_config = ExpectationConfiguration(
                    type="expect_column_values_to_be_between",
                    kwargs={
                        "column": rule.column,
                        "min_value": min_val,
                        "max_value": max_val,
                        "strict_min": False,
                        "strict_max": False,
                    },
                    meta={"description": rule.description, "rule_name": rule.name},
                )

        elif rule.rule_type == "regex":
            pattern = rule.parameters.get("pattern")
            if pattern:
                expectation_config = ExpectationConfiguration(
                    type="expect_column_values_to_match_regex",
                    kwargs={
                        "column": rule.column,
                        "regex": str(pattern),
                    },
                    meta={"description": rule.description, "rule_name": rule.name},
                )

        elif rule.rule_type == "enum":
            allowed_values = rule.parameters.get("allowed_values")
            if allowed_values and isinstance(allowed_values, list):
                expectation_config = ExpectationConfiguration(
                    type="expect_column_values_to_be_in_set",
                    kwargs={
                        "column": rule.column,
                        "value_set": allowed_values,
                    },
                    meta={"description": rule.description, "rule_name": rule.name},
                )

        if expectation_config:
            expectations.append(expectation_config)

    if not expectations:
        raise ValueError(
            "No valid rules found to export. All rules may be disabled or unsupported."
        )

    # Create and return ExpectationSuite
    suite = ExpectationSuite(
        name=suite_name,
        expectations=expectations,
        meta={"description": ruleset.description, "source": "lavendertown"},
    )

    return suite


def export_ruleset_to_great_expectations_json(
    ruleset: RuleSet,
    suite_name: str | None = None,
    indent: int = 2,
) -> str:
    """Export a RuleSet to a Great Expectations ExpectationSuite as JSON string.

    Args:
        ruleset: RuleSet to export
        suite_name: Name for the expectation suite (defaults to ruleset name)
        indent: JSON indentation level

    Returns:
        JSON string representation of the ExpectationSuite

    Raises:
        ImportError: If great_expectations is not installed
        ValueError: If unsupported rule types are encountered
    """
    suite = export_ruleset_to_great_expectations(ruleset, suite_name=suite_name)
    return json.dumps(suite.to_json_dict(), indent=indent, default=str)


def export_ruleset_to_great_expectations_file(
    ruleset: RuleSet,
    filepath: str,
    suite_name: str | None = None,
    indent: int = 2,
) -> None:
    """Export a RuleSet to a Great Expectations ExpectationSuite and save as JSON file.

    Args:
        ruleset: RuleSet to export
        filepath: Path to save the JSON file
        suite_name: Name for the expectation suite (defaults to ruleset name)
        indent: JSON indentation level

    Raises:
        ImportError: If great_expectations is not installed
        ValueError: If unsupported rule types are encountered
    """
    json_str = export_ruleset_to_great_expectations_json(
        ruleset, suite_name=suite_name, indent=indent
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)
