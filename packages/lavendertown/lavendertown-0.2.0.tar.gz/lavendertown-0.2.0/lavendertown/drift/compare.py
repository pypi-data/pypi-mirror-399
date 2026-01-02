"""Main dataset comparison function for drift detection."""

from __future__ import annotations

from lavendertown.drift.distribution import compare_distributions
from lavendertown.drift.schema import compare_schemas


def compare_datasets(
    baseline_df: object,
    current_df: object,
    comparison_type: str = "full",
    distribution_threshold: float = 10.0,
) -> list:
    """Compare two datasets and detect drift.

    Args:
        baseline_df: Baseline DataFrame (Pandas or Polars)
        current_df: Current DataFrame (Pandas or Polars)
        comparison_type: Type of comparison ("full", "schema_only", "distribution_only")
        distribution_threshold: Percentage threshold for distribution changes (default: 10.0)

    Returns:
        List of GhostFinding objects with ghost_type="drift"
    """
    from lavendertown.models import GhostFinding

    findings: list[GhostFinding] = []

    if comparison_type in ("full", "schema_only"):
        schema_findings = compare_schemas(baseline_df, current_df)
        findings.extend(schema_findings)

    if comparison_type in ("full", "distribution_only"):
        distribution_findings = compare_distributions(
            baseline_df, current_df, threshold_percent=distribution_threshold
        )
        findings.extend(distribution_findings)

    return findings
