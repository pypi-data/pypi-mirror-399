"""Schema comparison logic for drift detection."""

from __future__ import annotations

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.models import GhostFinding


def compare_schemas(
    baseline_df: object,
    current_df: object,
) -> list[GhostFinding]:
    """Compare schemas between two DataFrames.

    Detects:
    - New columns
    - Removed columns
    - Column type changes
    - Nullability changes

    Args:
        baseline_df: Baseline DataFrame (Pandas or Polars)
        current_df: Current DataFrame (Pandas or Polars)

    Returns:
        List of GhostFinding objects for schema differences
    """
    findings: list[GhostFinding] = []

    baseline_backend = detect_dataframe_backend(baseline_df)
    current_backend = detect_dataframe_backend(current_df)

    if baseline_backend == "pandas":
        baseline_schema = _get_pandas_schema(baseline_df)
    else:
        baseline_schema = _get_polars_schema(baseline_df)

    if current_backend == "pandas":
        current_schema = _get_pandas_schema(current_df)
    else:
        current_schema = _get_polars_schema(current_df)

    baseline_columns = set(baseline_schema.keys())
    current_columns = set(current_schema.keys())

    # Detect new columns
    new_columns = current_columns - baseline_columns
    for column in new_columns:
        findings.append(
            GhostFinding(
                ghost_type="drift",
                column=column,
                severity="info",
                description=f"New column '{column}' added to dataset",
                metadata={
                    "drift_type": "schema",
                    "change_type": "column_added",
                    "column_type": str(current_schema[column]["dtype"]),
                },
            )
        )

    # Detect removed columns
    removed_columns = baseline_columns - current_columns
    for column in removed_columns:
        findings.append(
            GhostFinding(
                ghost_type="drift",
                column=column,
                severity="warning",
                description=f"Column '{column}' removed from dataset",
                metadata={
                    "drift_type": "schema",
                    "change_type": "column_removed",
                    "baseline_type": str(baseline_schema[column]["dtype"]),
                },
            )
        )

    # Detect type changes and nullability changes for common columns
    common_columns = baseline_columns & current_columns
    for column in common_columns:
        baseline_info = baseline_schema[column]
        current_info = current_schema[column]

        # Type change
        if baseline_info["dtype"] != current_info["dtype"]:
            findings.append(
                GhostFinding(
                    ghost_type="drift",
                    column=column,
                    severity="error",
                    description=(
                        f"Column '{column}' type changed from "
                        f"{baseline_info['dtype']} to {current_info['dtype']}"
                    ),
                    metadata={
                        "drift_type": "schema",
                        "change_type": "type_change",
                        "baseline_type": str(baseline_info["dtype"]),
                        "current_type": str(current_info["dtype"]),
                    },
                )
            )

        # Nullability change (more lenient -> stricter is warning, stricter -> more lenient is info)
        baseline_nullable = baseline_info.get("nullable", True)
        current_nullable = current_info.get("nullable", True)

        if baseline_nullable != current_nullable:
            if baseline_nullable and not current_nullable:
                # Became stricter (no longer nullable)
                severity = "warning"
                change_desc = "became non-nullable"
            else:
                # Became more lenient (now nullable)
                severity = "info"
                change_desc = "became nullable"

            findings.append(
                GhostFinding(
                    ghost_type="drift",
                    column=column,
                    severity=severity,
                    description=f"Column '{column}' {change_desc}",
                    metadata={
                        "drift_type": "schema",
                        "change_type": "nullability_change",
                        "baseline_nullable": baseline_nullable,
                        "current_nullable": current_nullable,
                    },
                )
            )

    return findings


def _get_pandas_schema(df: object) -> dict[str, dict[str, object]]:
    """Get schema information from Pandas DataFrame.

    Returns:
        Dictionary mapping column names to schema info (dtype, nullable)
    """
    schema: dict[str, dict[str, object]] = {}

    for column in df.columns:  # type: ignore[attr-defined]
        dtype = df[column].dtype  # type: ignore[attr-defined,index]
        nullable = df[column].isna().any()  # type: ignore[attr-defined,index]  # Simplified: has any nulls means nullable
        schema[column] = {"dtype": dtype, "nullable": nullable}

    return schema


def _get_polars_schema(df: object) -> dict[str, dict[str, object]]:
    """Get schema information from Polars DataFrame.

    Returns:
        Dictionary mapping column names to schema info (dtype, nullable)
    """
    schema: dict[str, dict[str, object]] = {}

    polars_schema = df.schema  # type: ignore[attr-defined]

    for column, dtype in polars_schema.items():
        # Polars has nullable information in dtype
        nullable = dtype.is_nested() or dtype == dtype  # Simplified check
        # For more accurate nullable check, we could check for null values
        try:
            has_nulls = df[column].is_null().any()  # type: ignore[attr-defined,index]
            nullable = has_nulls
        except Exception:
            nullable = True  # Default to nullable if check fails

        schema[column] = {"dtype": dtype, "nullable": nullable}

    return schema
