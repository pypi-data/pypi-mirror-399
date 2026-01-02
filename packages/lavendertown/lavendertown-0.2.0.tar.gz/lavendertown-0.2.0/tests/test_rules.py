"""Tests for rule models, execution, and persistence."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from lavendertown.detectors.rule_based import RuleBasedDetector
from lavendertown.rules.executors import EnumRule, RangeRule, RegexRule
from lavendertown.rules.models import Rule, RuleSet
from lavendertown.rules.storage import (
    load_ruleset,
    ruleset_from_json,
    ruleset_to_json,
    save_ruleset,
)


class TestRuleModels:
    """Test Rule and RuleSet models."""

    def test_rule_creation(self):
        """Test creating a Rule."""
        rule = Rule(
            name="test_rule",
            description="Test description",
            rule_type="range",
            column="col1",
            parameters={"min_value": 0, "max_value": 100},
            enabled=True,
        )
        assert rule.name == "test_rule"
        assert rule.description == "Test description"
        assert rule.rule_type == "range"
        assert rule.column == "col1"
        assert rule.parameters == {"min_value": 0, "max_value": 100}
        assert rule.enabled is True

    def test_rule_serialization(self):
        """Test Rule serialization to/from dict."""
        rule = Rule(
            name="test_rule",
            description="Test description",
            rule_type="range",
            column="col1",
            parameters={"min_value": 0},
            enabled=True,
        )
        rule_dict = rule.to_dict()
        assert rule_dict["name"] == "test_rule"
        assert rule_dict["rule_type"] == "range"

        rule_restored = Rule.from_dict(rule_dict)
        assert rule_restored.name == rule.name
        assert rule_restored.rule_type == rule.rule_type
        assert rule_restored.parameters == rule.parameters

    def test_ruleset_creation(self):
        """Test creating a RuleSet."""
        ruleset = RuleSet(name="test_set", description="Test rule set")
        assert ruleset.name == "test_set"
        assert ruleset.description == "Test rule set"
        assert len(ruleset.rules) == 0

    def test_ruleset_add_remove_rule(self):
        """Test adding and removing rules from RuleSet."""
        ruleset = RuleSet(name="test_set", description="Test")
        rule = Rule(
            name="rule1",
            description="Rule 1",
            rule_type="range",
            column="col1",
            parameters={},
        )
        ruleset.add_rule(rule)
        assert len(ruleset.rules) == 1

        assert ruleset.remove_rule("rule1") is True
        assert len(ruleset.rules) == 0

        assert ruleset.remove_rule("nonexistent") is False

    def test_ruleset_serialization(self):
        """Test RuleSet serialization to/from dict."""
        ruleset = RuleSet(name="test_set", description="Test")
        rule = Rule(
            name="rule1",
            description="Rule 1",
            rule_type="range",
            column="col1",
            parameters={"min_value": 0},
        )
        ruleset.add_rule(rule)

        ruleset_dict = ruleset.to_dict()
        assert ruleset_dict["name"] == "test_set"
        assert len(ruleset_dict["rules"]) == 1

        ruleset_restored = RuleSet.from_dict(ruleset_dict)
        assert ruleset_restored.name == ruleset.name
        assert len(ruleset_restored.rules) == 1
        assert ruleset_restored.rules[0].name == "rule1"


class TestRuleExecutors:
    """Test rule executor classes."""

    def test_range_rule_within_range(self):
        """Test RangeRule with values within range."""
        df = pd.DataFrame({"age": [25, 30, 35, 40, 45]})
        rule = RangeRule(
            name="age_range",
            description="Age must be between 0 and 150",
            column="age",
            min_value=0.0,
            max_value=150.0,
        )

        findings = rule.check(df)
        assert len(findings) == 0

    def test_range_rule_outside_range(self):
        """Test RangeRule with values outside range."""
        df = pd.DataFrame({"age": [25, 200, 35, -10, 45]})
        rule = RangeRule(
            name="age_range",
            description="Age must be between 0 and 150",
            column="age",
            min_value=0.0,
            max_value=150.0,
        )

        findings = rule.check(df)
        assert len(findings) == 1
        assert findings[0].ghost_type == "rule"
        assert findings[0].column == "age"
        assert findings[0].row_indices is not None
        assert len(findings[0].row_indices) == 2  # 200 and -10

    def test_regex_rule_matching(self):
        """Test RegexRule with matching values."""
        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
        rule = RegexRule(
            name="name_pattern",
            description="Names must start with capital letter",
            column="name",
            pattern="^[A-Z][a-z]+$",
        )

        findings = rule.check(df)
        assert len(findings) == 0

    def test_regex_rule_non_matching(self):
        """Test RegexRule with non-matching values."""
        df = pd.DataFrame({"name": ["Alice", "bob", "CHARLIE"]})
        rule = RegexRule(
            name="name_pattern",
            description="Names must start with capital letter",
            column="name",
            pattern="^[A-Z][a-z]+$",
        )

        findings = rule.check(df)
        assert len(findings) == 1
        assert findings[0].column == "name"
        assert findings[0].row_indices is not None
        assert len(findings[0].row_indices) == 2  # "bob" and "CHARLIE"

    def test_enum_rule_matching(self):
        """Test EnumRule with matching values."""
        df = pd.DataFrame({"status": ["active", "inactive", "active"]})
        rule = EnumRule(
            name="status_enum",
            description="Status must be active or inactive",
            column="status",
            allowed_values=["active", "inactive"],
        )

        findings = rule.check(df)
        assert len(findings) == 0

    def test_enum_rule_non_matching(self):
        """Test EnumRule with non-matching values."""
        df = pd.DataFrame({"status": ["active", "pending", "inactive", "unknown"]})
        rule = EnumRule(
            name="status_enum",
            description="Status must be active or inactive",
            column="status",
            allowed_values=["active", "inactive"],
        )

        findings = rule.check(df)
        assert len(findings) == 1
        assert findings[0].column == "status"
        assert findings[0].row_indices is not None
        assert len(findings[0].row_indices) == 2  # "pending" and "unknown"


class TestRuleBasedDetector:
    """Test RuleBasedDetector wrapper."""

    def test_rule_based_detector(self):
        """Test RuleBasedDetector wraps CustomRule correctly."""
        df = pd.DataFrame({"age": [25, 200, 35]})
        rule = RangeRule(
            name="age_range",
            description="Age must be 0-150",
            column="age",
            min_value=0.0,
            max_value=150.0,
        )

        detector = RuleBasedDetector(rule)
        findings = detector.detect(df)

        assert len(findings) == 1
        assert detector.get_name() == "Rule: age_range"


class TestRuleStorage:
    """Test rule persistence and storage."""

    def test_save_load_ruleset(self):
        """Test saving and loading a RuleSet to/from file."""
        ruleset = RuleSet(name="test_set", description="Test")
        rule = Rule(
            name="rule1",
            description="Test rule",
            rule_type="range",
            column="col1",
            parameters={"min_value": 0},
        )
        ruleset.add_rule(rule)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_ruleset(ruleset, temp_path)
            loaded_ruleset = load_ruleset(temp_path)

            assert loaded_ruleset.name == ruleset.name
            assert len(loaded_ruleset.rules) == 1
            assert loaded_ruleset.rules[0].name == "rule1"
        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_ruleset("/nonexistent/path/rules.json")

    def test_ruleset_json_serialization(self):
        """Test RuleSet JSON string serialization."""
        ruleset = RuleSet(name="test_set", description="Test")
        rule = Rule(
            name="rule1",
            description="Test rule",
            rule_type="range",
            column="col1",
            parameters={"min_value": 0},
        )
        ruleset.add_rule(rule)

        json_str = ruleset_to_json(ruleset)
        assert isinstance(json_str, str)

        loaded_ruleset = ruleset_from_json(json_str)
        assert loaded_ruleset.name == ruleset.name
        assert len(loaded_ruleset.rules) == 1

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        with pytest.raises(ValueError):
            ruleset_from_json("not valid json {")
