"""Rule data models for custom data quality checks.

This module provides data models for representing custom data quality rules
and rule sets. These models support serialization to/from JSON for persistence
and sharing of rules across projects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rule:
    """Represents a custom data quality rule.

    This dataclass stores the configuration for a custom data quality rule,
    including its type, parameters, and whether it's enabled. Rules can be
    serialized to dictionaries for JSON storage.

    Attributes:
        name: Human-readable rule name. Should be unique within a rule set.
        description: Description of what the rule checks.
        rule_type: Type of rule. Common types include "range", "regex", "enum".
            Custom rule types can also be defined.
        column: Column name to apply the rule to, or None for cross-column rules.
        parameters: Dictionary of rule-specific parameters. For example, range
            rules might have {"min_value": 0, "max_value": 100}, while regex
            rules might have {"pattern": "^[A-Z]+$"}. Empty dict by default.
        enabled: Whether the rule is currently enabled. Disabled rules are
            not executed during detection. Defaults to True.

    Example:
        Create a range rule::

            rule = Rule(
                name="price_range",
                description="Check price is between 0 and 1000",
                rule_type="range",
                column="price",
                parameters={"min_value": 0.0, "max_value": 1000.0},
                enabled=True
            )
    """

    name: str
    description: str
    rule_type: str
    column: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary for serialization.

        Converts the Rule instance to a dictionary representation suitable
        for JSON serialization or storage.

        Returns:
            Dictionary containing all rule attributes: name, description,
            rule_type, column, parameters, and enabled.
        """
        return {
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "column": self.column,
            "parameters": self.parameters,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        """Create rule from dictionary.

        Deserializes a dictionary back into a Rule instance. Used for loading
        rules from JSON files.

        Args:
            data: Dictionary containing rule data. Must include "name",
                "description", and "rule_type". Optional fields "column",
                "parameters", and "enabled" will use defaults if not present.

        Returns:
            Rule instance initialized with data from the dictionary.
        """
        return cls(
            name=data["name"],
            description=data["description"],
            rule_type=data["rule_type"],
            column=data.get("column"),
            parameters=data.get("parameters", {}),
            enabled=data.get("enabled", True),
        )


@dataclass
class RuleSet:
    """A collection of rules to apply to a dataset.

    RuleSet groups multiple Rule instances together for convenient management
    and execution. Rule sets can be saved to and loaded from JSON files,
    making it easy to share rule configurations across projects or datasets.

    Attributes:
        name: Name of the rule set. Used for identification and display.
        description: Description of what the rule set validates.
        rules: List of Rule instances in this set. Empty list by default.

    Example:
        Create and use a rule set::

            ruleset = RuleSet(
                name="product_validation",
                description="Validation rules for product data"
            )
            ruleset.add_rule(Rule(name="price_range", ...))
            ruleset.add_rule(Rule(name="category_enum", ...))

            # Save to file
            with open("rules.json", "w") as f:
                json.dump(ruleset.to_dict(), f)
    """

    name: str
    description: str
    rules: list[Rule] = field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the set.

        Args:
            rule: Rule instance to add to the set.
        """
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name.

        Args:
            rule_name: Name of the rule to remove.

        Returns:
            True if the rule was found and removed, False if no rule with
            that name exists in the set.
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert rule set to dictionary for serialization.

        Converts the RuleSet instance to a dictionary representation suitable
        for JSON serialization or storage.

        Returns:
            Dictionary containing rule set attributes: name, description,
            and a list of rule dictionaries.
        """
        return {
            "name": self.name,
            "description": self.description,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuleSet":
        """Create rule set from dictionary.

        Deserializes a dictionary back into a RuleSet instance. Used for
        loading rule sets from JSON files.

        Args:
            data: Dictionary containing rule set data. Must include "name"
                and "description". Optional field "rules" (list of rule
                dictionaries) will use an empty list if not present.

        Returns:
            RuleSet instance initialized with data from the dictionary.
        """
        return cls(
            name=data["name"],
            description=data["description"],
            rules=[Rule.from_dict(r) for r in data.get("rules", [])],
        )
