"""Distribution comparison logic for drift detection."""

from __future__ import annotations

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.models import GhostFinding


def compare_distributions(
    baseline_df: object,
    current_df: object,
    threshold_percent: float = 10.0,
) -> list[GhostFinding]:
    """Compare data distributions between two DataFrames.

    Detects:
    - Value range shifts (min/max for numeric columns)
    - Null percentage changes
    - Cardinality changes (for categorical columns)
    - Statistical distribution changes

    Args:
        baseline_df: Baseline DataFrame (Pandas or Polars)
        current_df: Current DataFrame (Pandas or Polars)
        threshold_percent: Percentage threshold for considering changes significant

    Returns:
        List of GhostFinding objects for distribution differences
    """
    findings: list[GhostFinding] = []

    baseline_backend = detect_dataframe_backend(baseline_df)
    current_backend = detect_dataframe_backend(current_df)

    # Get common columns
    if baseline_backend == "pandas":
        baseline_columns = set(baseline_df.columns)  # type: ignore[attr-defined]
    else:
        baseline_columns = set(baseline_df.schema.keys())  # type: ignore[attr-defined]

    if current_backend == "pandas":
        current_columns = set(current_df.columns)  # type: ignore[attr-defined]
    else:
        current_columns = set(current_df.schema.keys())  # type: ignore[attr-defined]

    common_columns = baseline_columns & current_columns

    for column in common_columns:
        # Compare null percentages
        null_findings = _compare_null_percentages(
            baseline_df,
            current_df,
            column,
            baseline_backend,
            current_backend,
            threshold_percent,
        )
        findings.extend(null_findings)

        # Compare cardinality (for object/string columns)
        cardinality_findings = _compare_cardinality(
            baseline_df,
            current_df,
            column,
            baseline_backend,
            current_backend,
            threshold_percent,
        )
        findings.extend(cardinality_findings)

        # Compare numeric ranges (for numeric columns)
        range_findings = _compare_numeric_ranges(
            baseline_df,
            current_df,
            column,
            baseline_backend,
            current_backend,
            threshold_percent,
        )
        findings.extend(range_findings)

    return findings


def _compare_null_percentages(
    baseline_df: object,
    current_df: object,
    column: str,
    baseline_backend: str,
    current_backend: str,
    threshold_percent: float,
) -> list[GhostFinding]:
    """Compare null percentages between baseline and current."""
    findings: list[GhostFinding] = []

    # Get null percentages
    if baseline_backend == "pandas":
        baseline_null_pct = baseline_df[column].isna().sum() / len(baseline_df) * 100  # type: ignore[attr-defined,index,arg-type]
    else:
        baseline_null_pct = baseline_df[column].is_null().sum() / len(baseline_df) * 100  # type: ignore[attr-defined,index,arg-type]

    if current_backend == "pandas":
        current_null_pct = current_df[column].isna().sum() / len(current_df) * 100  # type: ignore[attr-defined,index,arg-type]
    else:
        current_null_pct = current_df[column].is_null().sum() / len(current_df) * 100  # type: ignore[attr-defined,index,arg-type]

    # Check for significant change
    null_change = abs(current_null_pct - baseline_null_pct)
    if null_change >= threshold_percent:
        # Determine severity: increase in nulls is worse than decrease
        if current_null_pct > baseline_null_pct:
            severity = "error" if null_change >= 20.0 else "warning"
            change_desc = (
                f"increased from {baseline_null_pct:.1f}% to {current_null_pct:.1f}%"
            )
        else:
            severity = "info"
            change_desc = (
                f"decreased from {baseline_null_pct:.1f}% to {current_null_pct:.1f}%"
            )

        findings.append(
            GhostFinding(
                ghost_type="drift",
                column=column,
                severity=severity,
                description=f"Null percentage {change_desc} (change: {null_change:.1f}%)",
                metadata={
                    "drift_type": "distribution",
                    "change_type": "null_percentage",
                    "baseline_null_pct": float(baseline_null_pct),
                    "current_null_pct": float(current_null_pct),
                    "change": float(null_change),
                },
            )
        )

    return findings


def _compare_cardinality(
    baseline_df: object,
    current_df: object,
    column: str,
    baseline_backend: str,
    current_backend: str,
    threshold_percent: float,
) -> list[GhostFinding]:
    """Compare cardinality (unique value counts) for categorical columns."""
    findings: list[GhostFinding] = []

    # Check if column is object/string type
    if baseline_backend == "pandas":
        baseline_dtype = baseline_df[column].dtype  # type: ignore[attr-defined,index]
        if baseline_dtype not in ["object", "string", "category"]:
            return findings
        baseline_cardinality = baseline_df[column].nunique()  # type: ignore[attr-defined,index]
    else:
        import polars as pl

        baseline_dtype = baseline_df.schema[column]  # type: ignore[attr-defined,index]
        if baseline_dtype not in [pl.Utf8, pl.Object, pl.Categorical]:
            return findings
        baseline_cardinality = baseline_df[column].n_unique()  # type: ignore[attr-defined,index,arg-type]

    if current_backend == "pandas":
        current_cardinality = current_df[column].nunique()  # type: ignore[attr-defined,index]
    else:
        current_cardinality = current_df[column].n_unique()  # type: ignore[attr-defined,index,arg-type]

    # Check for significant change (percentage change)
    if baseline_cardinality > 0:
        cardinality_change_pct = (
            abs(current_cardinality - baseline_cardinality) / baseline_cardinality * 100
        )

        if cardinality_change_pct >= threshold_percent:
            severity = "warning" if cardinality_change_pct >= 50.0 else "info"
            change_desc = (
                f"cardinality changed from {baseline_cardinality} to {current_cardinality} "
                f"({cardinality_change_pct:.1f}% change)"
            )

            findings.append(
                GhostFinding(
                    ghost_type="drift",
                    column=column,
                    severity=severity,
                    description=f"Column '{column}' {change_desc}",
                    metadata={
                        "drift_type": "distribution",
                        "change_type": "cardinality",
                        "baseline_cardinality": int(baseline_cardinality),
                        "current_cardinality": int(current_cardinality),
                        "change_pct": float(cardinality_change_pct),
                    },
                )
            )

    return findings


def _compare_numeric_ranges(
    baseline_df: object,
    current_df: object,
    column: str,
    baseline_backend: str,
    current_backend: str,
    threshold_percent: float,
) -> list[GhostFinding]:
    """Compare numeric ranges (min/max) for numeric columns."""
    findings: list[GhostFinding] = []

    # Check if column is numeric
    if baseline_backend == "pandas":
        import numpy as np

        baseline_dtype = baseline_df[column].dtype  # type: ignore[attr-defined,index]
        if not np.issubdtype(baseline_dtype, np.number):
            return findings

        baseline_data = baseline_df[column].dropna()  # type: ignore[attr-defined,index]
        if len(baseline_data) == 0:
            return findings

        baseline_min = baseline_data.min()  # type: ignore[attr-defined]
        baseline_max = baseline_data.max()  # type: ignore[attr-defined]
        baseline_range = baseline_max - baseline_min
    else:
        import polars as pl

        baseline_dtype = baseline_df.schema[column]  # type: ignore[attr-defined,index]
        if baseline_dtype not in [
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
            pl.Float32,
            pl.Float64,
        ]:
            return findings

        baseline_data = baseline_df[column].drop_nulls()  # type: ignore[attr-defined,index,arg-type]
        if len(baseline_data) == 0:
            return findings

        baseline_min = baseline_data.min()  # type: ignore[attr-defined]
        baseline_max = baseline_data.max()  # type: ignore[attr-defined]
        baseline_range = baseline_max - baseline_min

    if current_backend == "pandas":
        import numpy as np

        current_data = current_df[column].dropna()  # type: ignore[attr-defined,index]
        if len(current_data) == 0:
            return findings

        current_min = current_data.min()  # type: ignore[attr-defined]
        current_max = current_data.max()  # type: ignore[attr-defined]
    else:
        current_data = current_df[column].drop_nulls()  # type: ignore[attr-defined,index,arg-type]
        if len(current_data) == 0:
            return findings

        current_min = current_data.min()  # type: ignore[attr-defined]
        current_max = current_data.max()  # type: ignore[attr-defined]

    # Check for range shifts
    if baseline_range > 0:
        min_shift_pct = abs(current_min - baseline_min) / baseline_range * 100
        max_shift_pct = abs(current_max - baseline_max) / baseline_range * 100

        if min_shift_pct >= threshold_percent or max_shift_pct >= threshold_percent:
            severity = (
                "warning"
                if (min_shift_pct >= 20.0 or max_shift_pct >= 20.0)
                else "info"
            )
            change_desc = (
                f"range shifted from [{baseline_min:.2f}, {baseline_max:.2f}] "
                f"to [{current_min:.2f}, {current_max:.2f}]"
            )

            findings.append(
                GhostFinding(
                    ghost_type="drift",
                    column=column,
                    severity=severity,
                    description=f"Column '{column}' {change_desc}",
                    metadata={
                        "drift_type": "distribution",
                        "change_type": "numeric_range",
                        "baseline_min": float(baseline_min),
                        "baseline_max": float(baseline_max),
                        "current_min": float(current_min),
                        "current_max": float(current_max),
                        "min_shift_pct": float(min_shift_pct),
                        "max_shift_pct": float(max_shift_pct),
                    },
                )
            )

    return findings
