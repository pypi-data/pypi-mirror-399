"""Null ghost detector - detects null density violations."""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class NullGhostDetector(GhostDetector):
    """Detects columns with high null density.

    Identifies columns that exceed a configurable null percentage threshold.
    """

    def __init__(self, null_threshold: float = 0.1) -> None:
        """Initialize the null detector.

        Args:
            null_threshold: Fraction of nulls that triggers a finding (0.0 to 1.0).
                           Default is 0.1 (10% nulls).
        """
        if not 0.0 <= null_threshold <= 1.0:
            raise ValueError(
                f"null_threshold must be between 0.0 and 1.0, got {null_threshold}"
            )
        self.null_threshold = null_threshold

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect null density violations.

        Args:
            df: DataFrame to analyze

        Returns:
            List of GhostFinding objects for columns exceeding null threshold
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect nulls in Pandas DataFrame."""

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
        """Detect nulls in Polars DataFrame."""

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
