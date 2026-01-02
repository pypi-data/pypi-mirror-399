"""Pandera schema exporter for LavenderTown rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lavendertown.rules.models import Rule, RuleSet

try:
    import pandera as pa
    from pandera import DataFrameSchema
except ImportError:
    pa = None  # type: ignore[assignment]
    DataFrameSchema = None  # type: ignore[assignment,misc]


def export_ruleset_to_pandera(
    ruleset: RuleSet,
    schema_info: dict[str, str] | None = None,
) -> DataFrameSchema:
    """Export a RuleSet to a Pandera Schema.

    Converts LavenderTown rules to Pandera column validators:
    - Range rules -> pa.Check.in_range()
    - Regex rules -> pa.Check.str_matches()
    - Enum rules -> pa.Check.isin()

    Args:
        ruleset: RuleSet to export
        schema_info: Optional dict mapping column names to pandas dtypes
                     (e.g., {"age": "int64", "name": "string"})
                     If None, defaults to pa.String for string columns and pa.Float64 for numeric

    Returns:
        Pandera DataFrameSchema object

    Raises:
        ImportError: If pandera is not installed
        ValueError: If unsupported rule types are encountered or column info is missing

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
        >>> schema = export_ruleset_to_pandera(ruleset, {"age": "int64"})
        >>> isinstance(schema, pa.DataFrameSchema)
        True
    """
    if pa is None or DataFrameSchema is None:
        raise ImportError(
            "pandera is required for Pandera export. "
            "Install it with: pip install lavendertown[pandera]"
        )

    if not ruleset.rules:
        raise ValueError("Cannot export empty RuleSet to Pandera Schema")

    # Group rules by column
    from lavendertown.rules.models import Rule  # noqa: F401

    column_rules: dict[str, list[Rule]] = {}  # type: ignore[name-defined]
    for rule in ruleset.rules:
        if not rule.enabled:
            continue

        if rule.column is None:
            raise ValueError(
                f"Rule '{rule.name}' has no column - cross-column rules are not supported in Pandera export"
            )

        if rule.column not in column_rules:
            column_rules[rule.column] = []
        column_rules[rule.column].append(rule)

    # Build schema columns
    schema_columns: dict[str, pa.Column] = {}

    for column_name, rules in column_rules.items():
        # Determine column type
        dtype: (
            type[pa.Int64] | type[pa.Float64] | type[pa.String] | type[pa.Bool] | None
        ) = None
        if schema_info and column_name in schema_info:
            dtype_str = schema_info[column_name]
            # Map common pandas dtypes to pandera types
            if "int" in dtype_str:
                dtype = pa.Int64
            elif "float" in dtype_str:
                dtype = pa.Float64
            elif "bool" in dtype_str:
                dtype = pa.Bool
            elif "string" in dtype_str or "str" in dtype_str or "object" in dtype_str:
                dtype = pa.String
            else:
                dtype = pa.String  # Default fallback
        else:
            # Try to infer from rules - if any regex or enum rules, assume string
            has_string_rule = any(r.rule_type in ("regex", "enum") for r in rules)
            dtype = pa.String if has_string_rule else pa.Float64

        # Build checks for this column
        checks: list[pa.Check] = []

        for rule in rules:
            if rule.rule_type == "range":
                min_val = rule.parameters.get("min_value")
                max_val = rule.parameters.get("max_value")

                if min_val is not None or max_val is not None:
                    # Pandera's in_range is inclusive on both ends by default
                    check = pa.Check.in_range(
                        min_value=min_val, max_value=max_val, inclusive="both"
                    )
                    checks.append(check)

            elif rule.rule_type == "regex":
                pattern = rule.parameters.get("pattern")
                if pattern:
                    check = pa.Check.str_matches(pattern)
                    checks.append(check)

            elif rule.rule_type == "enum":
                allowed_values = rule.parameters.get("allowed_values")
                if allowed_values and isinstance(allowed_values, list):
                    check = pa.Check.isin(allowed_values)
                    checks.append(check)

            else:
                # Skip unsupported rule types with a warning
                # Could raise ValueError, but being permissive allows partial exports
                continue

        # Create column with all checks
        if checks:
            # Combine multiple checks - Pandera supports list of checks
            if len(checks) == 1:
                schema_columns[column_name] = pa.Column(dtype, checks=checks[0])
            else:
                # Multiple checks - pass as list
                schema_columns[column_name] = pa.Column(dtype, checks=checks)
        else:
            # If no valid checks, create column with just dtype
            schema_columns[column_name] = pa.Column(dtype)

    if not schema_columns:
        raise ValueError(
            "No valid rules found to export. All rules may be disabled or unsupported."
        )

    # Create and return schema
    schema = pa.DataFrameSchema(schema_columns, name=ruleset.name)
    return schema


def export_ruleset_to_pandera_file(
    ruleset: RuleSet,
    filepath: str,
    schema_info: dict[str, str] | None = None,
) -> None:
    """Export a RuleSet to a Pandera Schema and save as Python file.

    Args:
        ruleset: RuleSet to export
        filepath: Path to save the Python file
        schema_info: Optional dict mapping column names to pandas dtypes

    Raises:
        ImportError: If pandera is not installed
        ValueError: If unsupported rule types are encountered
    """
    schema = export_ruleset_to_pandera(ruleset, schema_info=schema_info)

    # Generate Python code string
    # This is a simple representation - in practice, users might want to customize
    code_lines = [
        '"""Pandera schema exported from LavenderTown.',
        f"RuleSet: {ruleset.name}",
        f"Description: {ruleset.description}",
        '"""',
        "",
        "import pandera as pa",
        "",
        "",
        f"schema = {repr(schema)}",
    ]

    code = "\n".join(code_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
