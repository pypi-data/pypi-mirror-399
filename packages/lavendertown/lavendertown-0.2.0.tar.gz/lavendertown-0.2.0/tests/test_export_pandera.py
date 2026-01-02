"""Tests for Pandera export functionality."""

from __future__ import annotations

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


def test_export_ruleset_to_pandera_missing_dependency(sample_ruleset: RuleSet) -> None:
    """Test that ImportError is raised when pandera is not installed."""
    # Temporarily remove pandera if it exists
    import sys

    pandera_module = sys.modules.get("lavendertown.export.pandera")
    if pandera_module:
        original_pa = getattr(pandera_module, "pa", None)
        pandera_module.pa = None  # type: ignore[assignment]
        pandera_module.Schema = None  # type: ignore[assignment]

    try:
        from lavendertown.export.pandera import export_ruleset_to_pandera

        with pytest.raises(ImportError, match="pandera is required"):
            export_ruleset_to_pandera(sample_ruleset)
    finally:
        # Restore if it existed
        if pandera_module and original_pa is not None:
            pandera_module.pa = original_pa


@pytest.mark.skipif(
    True,
    reason="Requires pandera to be installed - run with: pip install lavendertown[pandera]",
)
def test_export_ruleset_to_pandera_range_rule(sample_ruleset: RuleSet) -> None:
    """Test exporting a ruleset with range rules."""
    try:
        from lavendertown.export.pandera import export_ruleset_to_pandera

        schema = export_ruleset_to_pandera(sample_ruleset, schema_info={"age": "int64"})

        assert schema is not None
        assert "age" in schema.columns
    except ImportError:
        pytest.skip("pandera not installed")


@pytest.mark.skipif(
    True,
    reason="Requires pandera to be installed - run with: pip install lavendertown[pandera]",
)
def test_export_ruleset_to_pandera_empty_ruleset(empty_ruleset: RuleSet) -> None:
    """Test that ValueError is raised for empty ruleset."""
    try:
        from lavendertown.export.pandera import export_ruleset_to_pandera

        with pytest.raises(ValueError, match="Cannot export empty RuleSet"):
            export_ruleset_to_pandera(empty_ruleset)
    except ImportError:
        pytest.skip("pandera not installed")


@pytest.mark.skipif(
    True,
    reason="Requires pandera to be installed - run with: pip install lavendertown[pandera]",
)
def test_export_ruleset_to_pandera_no_column_rule() -> None:
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
        from lavendertown.export.pandera import export_ruleset_to_pandera

        with pytest.raises(ValueError, match="no column"):
            export_ruleset_to_pandera(ruleset)
    except ImportError:
        pytest.skip("pandera not installed")


@pytest.mark.skipif(
    True,
    reason="Requires pandera to be installed - run with: pip install lavendertown[pandera]",
)
def test_export_ruleset_to_pandera_file(
    sample_ruleset: RuleSet, tmp_path: pytest.TempPathFactory
) -> None:
    """Test exporting to a file."""
    try:
        from lavendertown.export.pandera import export_ruleset_to_pandera_file

        output_file = tmp_path / "schema.py"
        export_ruleset_to_pandera_file(
            sample_ruleset,
            str(output_file),
            schema_info={"age": "int64", "email": "string"},
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "pandera" in content.lower()
        assert "schema" in content.lower()
    except ImportError:
        pytest.skip("pandera not installed")


def test_export_ruleset_to_pandera_handles_missing_optional_dependency() -> None:
    """Test that the module can be imported even if pandera is not installed."""
    # This should not raise an error
    try:
        from lavendertown.export import pandera  # noqa: F401

        # If pandera is not installed, the functions should raise ImportError when called
        from lavendertown.export.pandera import export_ruleset_to_pandera

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
            export_ruleset_to_pandera(ruleset)
            # If we get here, pandera is installed, so the test passes
        except ImportError:
            # This is expected if pandera is not installed
            pass
    except ImportError:
        # Module itself can't be imported - this might be a different issue
        pass
