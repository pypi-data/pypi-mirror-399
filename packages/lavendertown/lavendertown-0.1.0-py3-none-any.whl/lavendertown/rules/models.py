"""Rule data models for custom data quality checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rule:
    """Represents a custom data quality rule.

    Attributes:
        name: Human-readable rule name
        description: Rule description
        rule_type: Type of rule (range, regex, enum, custom, etc.)
        column: Column to apply rule to (or None for cross-column rules)
        parameters: Rule-specific parameters (e.g., min/max for range rules)
        enabled: Whether the rule is currently enabled
    """

    name: str
    description: str
    rule_type: str
    column: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary for serialization."""
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
        """Create rule from dictionary."""
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

    Attributes:
        name: Name of the rule set
        description: Description of the rule set
        rules: List of rules in this set
    """

    name: str
    description: str
    rules: list[Rule] = field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the set."""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name. Returns True if removed, False if not found."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert rule set to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuleSet":
        """Create rule set from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            rules=[Rule.from_dict(r) for r in data.get("rules", [])],
        )
