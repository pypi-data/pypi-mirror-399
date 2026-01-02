"""Null ghost detector - detects null density violations.

This module provides the NullGhostDetector class, which identifies columns
with excessive null values. It supports configurable thresholds for null
percentage and automatically assigns severity levels based on the proportion
of nulls in each column.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class NullGhostDetector(GhostDetector):
    """Detects columns with high null density.

    This detector identifies columns that exceed a configurable null percentage
    threshold. It works with both Pandas and Polars DataFrames and automatically
    assigns severity levels based on the proportion of nulls:
    - error: >50% nulls
    - warning: >25% nulls
    - info: >threshold (default 10%) but <=25% nulls

    The detector provides detailed metadata including null counts, percentages,
    and the configured threshold for each finding.

    Attributes:
        null_threshold: Fraction (0.0 to 1.0) of nulls that triggers a finding.
            Default is 0.1 (10%).

    Example:
        Use default threshold (10%)::

            detector = NullGhostDetector()
            findings = detector.detect(df)

        Use custom threshold (5%)::

            detector = NullGhostDetector(null_threshold=0.05)
            findings = detector.detect(df)
    """

    def __init__(self, null_threshold: float = 0.1) -> None:
        """Initialize the null detector.

        Args:
            null_threshold: Fraction of nulls that triggers a finding.
                Must be between 0.0 and 1.0. For example, 0.1 means 10% nulls.
                Default is 0.1 (10% nulls).

        Raises:
            ValueError: If null_threshold is not between 0.0 and 1.0.
        """
        if not 0.0 <= null_threshold <= 1.0:
            raise ValueError(
                f"null_threshold must be between 0.0 and 1.0, got {null_threshold}"
            )
        self.null_threshold = null_threshold

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect null density violations.

        Analyzes all columns in the DataFrame and identifies those with null
        percentages exceeding the configured threshold. Works with both Pandas
        and Polars DataFrames.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. The backend is automatically detected.

        Returns:
            List of GhostFinding objects for columns exceeding the null threshold.
            Each finding includes:
            - ghost_type: "null"
            - column: Name of the column with excessive nulls
            - severity: "error", "warning", or "info" based on null percentage
            - description: Human-readable description with null counts and percentages
            - row_indices: List of row indices with null values (Pandas only,
              None for Polars)
            - metadata: Dictionary with null_count, total_count, null_percentage,
              and threshold

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts. The finding will still include the total
            null count and percentage.
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect nulls in Pandas DataFrame.

        Internal method that performs null detection using Pandas-specific APIs.
        Includes row indices for each null value.

        Args:
            df: pandas.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns with excessive nulls.
        """

        findings: list[GhostFinding] = []

        for column in df.columns:
            null_count = df[column].isna().sum()
            total_count = len(df)
            null_percentage = null_count / total_count if total_count > 0 else 0.0

            if null_percentage > self.null_threshold:
                # Determine severity based on null percentage
                if null_percentage > 0.5:
                    severity = "error"
                elif null_percentage > 0.25:
                    severity = "warning"
                else:
                    severity = "info"

                # Get row indices with null values
                null_indices = df[df[column].isna()].index.tolist()

                finding = GhostFinding(
                    ghost_type="null",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {null_count:,} null values "
                        f"({null_percentage:.1%} of {total_count:,} rows)"
                    ),
                    row_indices=null_indices,
                    metadata={
                        "null_count": int(null_count),
                        "total_count": int(total_count),
                        "null_percentage": float(null_percentage),
                        "threshold": float(self.null_threshold),
                    },
                )
                findings.append(finding)

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect nulls in Polars DataFrame.

        Internal method that performs null detection using Polars-specific APIs.
        Note that row_indices will be None as Polars doesn't maintain index concepts.

        Args:
            df: polars.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns with excessive nulls.
            row_indices will be None for all findings.
        """

        findings: list[GhostFinding] = []

        for column in df.columns:
            null_count = df[column].null_count()
            total_count = len(df)
            null_percentage = null_count / total_count if total_count > 0 else 0.0

            if null_percentage > self.null_threshold:
                # Determine severity based on null percentage
                if null_percentage > 0.5:
                    severity = "error"
                elif null_percentage > 0.25:
                    severity = "warning"
                else:
                    severity = "info"

                # Get row indices with null values
                # For Polars, we can't easily get original row indices without adding them
                # So we'll return None for row_indices (Polars doesn't have index concept)
                null_indices = None

                finding = GhostFinding(
                    ghost_type="null",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {null_count:,} null values "
                        f"({null_percentage:.1%} of {total_count:,} rows)"
                    ),
                    row_indices=null_indices,
                    metadata={
                        "null_count": int(null_count),
                        "total_count": int(total_count),
                        "null_percentage": float(null_percentage),
                        "threshold": float(self.null_threshold),
                    },
                )
                findings.append(finding)

        return findings
