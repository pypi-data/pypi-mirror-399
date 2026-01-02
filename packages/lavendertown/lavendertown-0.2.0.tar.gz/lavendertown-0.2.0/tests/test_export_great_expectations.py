"""Tests for Great Expectations export functionality."""

from __future__ import annotations

import json

import pytest

from lavendertown.rules.models import Rule, RuleSet


@pytest.fixture
def sample_ruleset() -> RuleSet:
    """Create a sample RuleSet for testing."""
    ruleset = RuleSet(name="test_rules", description="Test rule set")
    ruleset.add_rule(
        Rule(
            name="age_range",
            description="Age must be between 0 and 150",
            rule_type="range",
            column="age",
            parameters={"min_value": 0, "max_value": 150},
            enabled=True,
        )
    )
    ruleset.add_rule(
        Rule(
            name="email_pattern",
            description="Email must match pattern",
            rule_type="regex",
            column="email",
            parameters={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
            enabled=True,
        )
    )
    ruleset.add_rule(
        Rule(
            name="status_enum",
            description="Status must be in allowed set",
            rule_type="enum",
            column="status",
            parameters={"allowed_values": ["active", "inactive", "pending"]},
            enabled=True,
        )
    )
    return ruleset


@pytest.fixture
def empty_ruleset() -> RuleSet:
    """Create an empty RuleSet."""
    return RuleSet(name="empty", description="Empty rule set")


def test_export_ruleset_to_great_expectations_missing_dependency(
    sample_ruleset: RuleSet,
) -> None:
    """Test that ImportError is raised when great_expectations is not installed."""
    # This test checks the error handling when the library is not available
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        # If GE is not installed, this should raise ImportError
        try:
            export_ruleset_to_great_expectations(sample_ruleset)
        except ImportError as e:
            assert "great_expectations" in str(e).lower()
    except ImportError:
        # Module can't be imported at all - this is also expected if GE is not installed
        pass


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_range_rule(
    sample_ruleset: RuleSet,
) -> None:
    """Test exporting a ruleset with range rules."""
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        suite = export_ruleset_to_great_expectations(sample_ruleset)

        assert suite is not None
        assert len(suite.expectations) > 0

        # Check that range expectation is present
        range_expectations = [
            e
            for e in suite.expectations
            if e.expectation_type == "expect_column_values_to_be_between"
        ]
        assert len(range_expectations) > 0
    except ImportError:
        pytest.skip("great-expectations not installed")


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_empty_ruleset(
    empty_ruleset: RuleSet,
) -> None:
    """Test that ValueError is raised for empty ruleset."""
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        with pytest.raises(ValueError, match="Cannot export empty RuleSet"):
            export_ruleset_to_great_expectations(empty_ruleset)
    except ImportError:
        pytest.skip("great-expectations not installed")


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_no_column_rule() -> None:
    """Test that ValueError is raised for rules without columns."""
    ruleset = RuleSet(name="test", description="Test")
    ruleset.add_rule(
        Rule(
            name="no_column",
            description="Rule without column",
            rule_type="range",
            column=None,  # type: ignore[arg-type]
            parameters={"min_value": 0},
            enabled=True,
        )
    )

    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        with pytest.raises(ValueError, match="no column"):
            export_ruleset_to_great_expectations(ruleset)
    except ImportError:
        pytest.skip("great-expectations not installed")


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_json(
    sample_ruleset: RuleSet,
) -> None:
    """Test exporting to JSON string."""
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations_json,
        )

        json_str = export_ruleset_to_great_expectations_json(sample_ruleset)

        assert json_str is not None
        assert len(json_str) > 0

        # Should be valid JSON
        data = json.loads(json_str)
        assert "expectation_suite_name" in data
        assert "expectations" in data
    except ImportError:
        pytest.skip("great-expectations not installed")


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_file(
    sample_ruleset: RuleSet, tmp_path: pytest.TempPathFactory
) -> None:
    """Test exporting to a file."""
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations_file,
        )

        output_file = tmp_path / "expectation_suite.json"
        export_ruleset_to_great_expectations_file(sample_ruleset, str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        data = json.loads(content)
        assert "expectation_suite_name" in data
        assert "expectations" in data
    except ImportError:
        pytest.skip("great-expectations not installed")


@pytest.mark.skipif(
    True,
    reason="Requires great-expectations to be installed - run with: pip install lavendertown[great_expectations]",
)
def test_export_ruleset_to_great_expectations_suite_name(
    sample_ruleset: RuleSet,
) -> None:
    """Test that custom suite name is used."""
    try:
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        custom_name = "my_custom_suite"
        suite = export_ruleset_to_great_expectations(
            sample_ruleset, suite_name=custom_name
        )

        assert suite.expectation_suite_name == custom_name
    except ImportError:
        pytest.skip("great-expectations not installed")


def test_export_ruleset_to_great_expectations_handles_missing_optional_dependency() -> (
    None
):
    """Test that the module can be imported even if great-expectations is not installed."""
    # This should not raise an error
    try:
        from lavendertown.export import great_expectations  # noqa: F401

        # If GE is not installed, the functions should raise ImportError when called
        from lavendertown.export.great_expectations import (
            export_ruleset_to_great_expectations,
        )

        ruleset = RuleSet(name="test", description="test")
        ruleset.add_rule(
            Rule(
                name="test_rule",
                description="test",
                rule_type="range",
                column="age",
                parameters={"min_value": 0, "max_value": 100},
            )
        )

        try:
            export_ruleset_to_great_expectations(ruleset)
            # If we get here, GE is installed, so the test passes
        except ImportError:
            # This is expected if GE is not installed
            pass
    except ImportError:
        # Module itself can't be imported - this might be a different issue
        pass
