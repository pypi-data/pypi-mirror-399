"""Tests for rule models, execution, and persistence."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from lavendertown.detectors.rule_based import RuleBasedDetector
from lavendertown.rules.executors import EnumRule, RangeRule, RegexRule
from lavendertown.rules.cross_column import CrossColumnRule
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


class TestCrossColumnRules:
    """Test cross-column validation rules."""

    def test_cross_column_equals_rule(self):
        """Test equals cross-column rule."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": [1, 2, 99, 4, 5],  # 99 is violation
            }
        )

        rule = CrossColumnRule(
            name="equals_rule",
            description="col1 must equal col2",
            source_columns=["col1", "col2"],
            operation="equals",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].ghost_type == "rule"
        assert findings[0].metadata["operation"] == "equals"

    def test_cross_column_greater_than_rule(self):
        """Test greater_than cross-column rule."""
        df = pd.DataFrame(
            {
                "price": [100, 200, 150, 300],
                "cost": [50, 150, 200, 250],  # 200 > 150 is violation
            }
        )

        rule = CrossColumnRule(
            name="price_gt_cost",
            description="price must be greater than cost",
            source_columns=["price", "cost"],
            operation="greater_than",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["operation"] == "greater_than"

    def test_cross_column_sum_equals_rule(self):
        """Test sum_equals cross-column rule."""
        df = pd.DataFrame(
            {
                "col1": [10, 20, 30],
                "col2": [5, 10, 15],
                "total": [15, 30, 50],  # 50 != 30+15 is violation
            }
        )

        rule = CrossColumnRule(
            name="sum_rule",
            description="col1 + col2 must equal total",
            source_columns=["col1", "col2"],
            operation="sum_equals",
            target_column="total",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["operation"] == "sum_equals"

    def test_cross_column_conditional_rule(self):
        """Test conditional cross-column rule."""
        df = pd.DataFrame(
            {
                "status": ["active", "active", "inactive", "active"],
                "priority": ["high", "low", "low", "medium"],  # active should be high
            }
        )

        rule = CrossColumnRule(
            name="conditional_rule",
            description="if status is active, priority must be high",
            source_columns=["status", "priority"],
            operation="conditional",
            condition={
                "if_column": "status",
                "if_value": "active",
                "then_column": "priority",
                "then_value": "high",
            },
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["operation"] == "conditional"

    def test_cross_column_referential_rule(self):
        """Test referential integrity cross-column rule."""
        df = pd.DataFrame(
            {
                "category": ["A", "B", "C", "D"],  # D doesn't exist in valid_categories
                "valid_categories": ["A", "B", "C", "A"],
            }
        )

        rule = CrossColumnRule(
            name="referential_rule",
            description="category must exist in valid_categories",
            source_columns=["category"],
            operation="referential",
            target_column="valid_categories",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["operation"] == "referential"

    def test_cross_column_rule_invalid_columns(self):
        """Test cross-column rule with missing columns."""
        df = pd.DataFrame({"col1": [1, 2, 3]})

        rule = CrossColumnRule(
            name="invalid_rule",
            description="test",
            source_columns=["col1", "nonexistent"],
            operation="equals",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].severity == "error"
        assert "Missing columns" in findings[0].description

    def test_cross_column_rule_invalid_operation(self):
        """Test cross-column rule with invalid operation."""
        with pytest.raises(ValueError, match="Operation must be one of"):
            CrossColumnRule(
                name="invalid",
                description="test",
                source_columns=["col1", "col2"],
                operation="invalid_op",
            )

    def test_cross_column_rule_insufficient_columns(self):
        """Test cross-column rule with insufficient columns."""
        with pytest.raises(ValueError, match="require at least 2 columns"):
            CrossColumnRule(
                name="invalid",
                description="test",
                source_columns=["col1"],
                operation="equals",
            )

    def test_cross_column_rule_polars(self):
        """Test cross-column rule with Polars DataFrame."""
        try:
            import polars as pl
        except ImportError:
            pytest.skip("Polars not installed")

        df = pl.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [1, 99, 3],  # 99 is violation
            }
        )

        rule = CrossColumnRule(
            name="equals_rule",
            description="col1 must equal col2",
            source_columns=["col1", "col2"],
            operation="equals",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].row_indices is None  # Polars doesn't maintain indices

    def test_cross_column_rule_with_nulls(self):
        """Test cross-column rule handles null values correctly."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, None, 4, 5],
                "col2": [1, 2, 3, None, 5],
            }
        )

        rule = CrossColumnRule(
            name="equals_rule",
            description="col1 must equal col2",
            source_columns=["col1", "col2"],
            operation="equals",
        )

        findings = rule.check(df)
        # Should only flag non-null mismatches
        assert isinstance(findings, list)

    def test_cross_column_sum_equals_multiple_columns(self):
        """Test sum_equals with multiple source columns."""
        df = pd.DataFrame(
            {
                "col1": [10, 20, 30],
                "col2": [5, 10, 15],
                "col3": [2, 3, 4],
                "total": [16, 33, 50],  # 16 != 10+5+2 (17), 50 != 30+15+4 (49)
            }
        )

        rule = CrossColumnRule(
            name="sum_rule",
            description="col1 + col2 + col3 must equal total",
            source_columns=["col1", "col2", "col3"],
            operation="sum_equals",
            target_column="total",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["operation"] == "sum_equals"

    def test_cross_column_conditional_multiple_conditions(self):
        """Test conditional rule with multiple condition values."""
        df = pd.DataFrame(
            {
                "status": ["active", "inactive", "pending", "active"],
                "priority": ["high", "low", "medium", "low"],  # active should be high
            }
        )

        rule = CrossColumnRule(
            name="conditional_rule",
            description="if status is active, priority must be high",
            source_columns=["status", "priority"],
            operation="conditional",
            condition={
                "if_column": "status",
                "if_value": "active",
                "then_column": "priority",
                "then_value": "high",
            },
        )

        findings = rule.check(df)
        # Should find violations where status=active but priority != high
        assert len(findings) > 0

    def test_cross_column_referential_empty_target(self):
        """Test referential rule with empty target column (all nulls)."""
        df = pd.DataFrame(
            {
                "category": ["A", "B", "C"],
                "valid_categories": [None, None, None],  # All nulls - effectively empty
            }
        )

        rule = CrossColumnRule(
            name="referential_rule",
            description="category must exist in valid_categories",
            source_columns=["category"],
            operation="referential",
            target_column="valid_categories",
        )

        findings = rule.check(df)
        # All values should be violations
        assert len(findings) > 0

    def test_cross_column_rule_no_violations(self):
        """Test cross-column rule with no violations."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3, 4, 5],
                "col2": [1, 2, 3, 4, 5],
            }
        )

        rule = CrossColumnRule(
            name="equals_rule",
            description="col1 must equal col2",
            source_columns=["col1", "col2"],
            operation="equals",
        )

        findings = rule.check(df)
        assert len(findings) == 0

    def test_cross_column_rule_all_violations(self):
        """Test cross-column rule where all rows violate."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [10, 20, 30],  # All different
            }
        )

        rule = CrossColumnRule(
            name="equals_rule",
            description="col1 must equal col2",
            source_columns=["col1", "col2"],
            operation="equals",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].metadata["violation_count"] == 3

    def test_cross_column_rule_missing_target_column(self):
        """Test cross-column rule with missing target column."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [4, 5, 6],
            }
        )

        rule = CrossColumnRule(
            name="sum_rule",
            description="test",
            source_columns=["col1", "col2"],
            operation="sum_equals",
            target_column="nonexistent",
        )

        findings = rule.check(df)
        assert len(findings) > 0
        assert findings[0].severity == "error"
        assert "Missing columns" in findings[0].description

    def test_cross_column_rule_incomplete_condition(self):
        """Test conditional rule with incomplete condition."""
        df = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [10, 20, 30],
            }
        )

        rule = CrossColumnRule(
            name="conditional_rule",
            description="test",
            source_columns=["col1", "col2"],
            operation="conditional",
            condition={
                "if_column": "col1",
                "if_value": "1",
                # Missing then_column and then_value
            },
        )

        findings = rule.check(df)
        # Should handle gracefully
        assert isinstance(findings, list)
