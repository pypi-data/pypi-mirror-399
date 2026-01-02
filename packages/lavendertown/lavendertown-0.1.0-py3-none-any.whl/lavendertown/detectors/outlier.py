"""Outlier ghost detector - detects statistical outliers using IQR method."""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class OutlierGhostDetector(GhostDetector):
    """Detects statistical outliers in numeric columns using IQR method.

    Identifies values that fall outside the interquartile range (IQR).
    """

    def __init__(self, iqr_multiplier: float = 1.5) -> None:
        """Initialize the outlier detector.

        Args:
            iqr_multiplier: Multiplier for IQR to determine outlier bounds.
                           Default is 1.5 (standard Tukey's method).
        """
        if iqr_multiplier <= 0:
            raise ValueError(f"iqr_multiplier must be positive, got {iqr_multiplier}")
        self.iqr_multiplier = iqr_multiplier

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect outliers in numeric columns.

        Args:
            df: DataFrame to analyze

        Returns:
            List of GhostFinding objects for columns with outliers
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect outliers in Pandas DataFrame."""
        import numpy as np

        findings: list[GhostFinding] = []

        # Get numeric columns only
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        for column in numeric_columns:
            column_data = df[column].dropna()

            if len(column_data) < 4:  # Need at least 4 values for IQR
                continue

            # Calculate quartiles and IQR
            q1 = column_data.quantile(0.25)
            q3 = column_data.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:  # No variability, skip
                continue

            # Calculate outlier bounds
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr

            # Find outliers
            outliers = (column_data < lower_bound) | (column_data > upper_bound)
            outlier_count = outliers.sum()

            if outlier_count > 0:
                # Get original DataFrame indices for outliers
                outlier_indices = column_data[outliers].index.tolist()

                # Determine severity based on outlier percentage
                outlier_percentage = outlier_count / len(column_data)
                if outlier_percentage > 0.1:  # More than 10% outliers
                    severity = "warning"
                else:
                    severity = "info"

                finding = GhostFinding(
                    ghost_type="outlier",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {outlier_count:,} outliers "
                        f"({outlier_percentage:.1%} of {len(column_data):,} values) "
                        f"outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                    ),
                    row_indices=outlier_indices,
                    metadata={
                        "outlier_count": int(outlier_count),
                        "total_count": int(len(column_data)),
                        "outlier_percentage": float(outlier_percentage),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                        "q1": float(q1),
                        "q3": float(q3),
                        "iqr": float(iqr),
                        "iqr_multiplier": float(self.iqr_multiplier),
                    },
                )
                findings.append(finding)

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect outliers in Polars DataFrame."""
        import polars as pl

        findings: list[GhostFinding] = []

        # Get numeric columns
        numeric_columns = [
            col
            for col, dtype in df.schema.items()
            if dtype
            in [
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
            ]
        ]

        for column in numeric_columns:
            column_data = df.select(pl.col(column).drop_nulls())

            if len(column_data) < 4:  # Need at least 4 values for IQR
                continue

            # Calculate quartiles
            quantiles = column_data.select(
                pl.col(column).quantile(0.25).alias("q1"),
                pl.col(column).quantile(0.75).alias("q3"),
            )
            q1 = quantiles["q1"][0]
            q3 = quantiles["q3"][0]
            iqr = q3 - q1

            if iqr == 0:  # No variability, skip
                continue

            # Calculate outlier bounds
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr

            # Find outliers in original DataFrame
            outliers_df = df.filter(
                (pl.col(column) < lower_bound) | (pl.col(column) > upper_bound)
            )
            outlier_count = len(outliers_df)

            if outlier_count > 0:
                # For Polars, we can't easily get original row indices without adding them
                # So we'll return None for row_indices (Polars doesn't have index concept)
                outlier_indices = None

                total_count = len(column_data)
                outlier_percentage = (
                    outlier_count / total_count if total_count > 0 else 0.0
                )

                # Determine severity
                if outlier_percentage > 0.1:
                    severity = "warning"
                else:
                    severity = "info"

                finding = GhostFinding(
                    ghost_type="outlier",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {outlier_count:,} outliers "
                        f"({outlier_percentage:.1%} of {total_count:,} values) "
                        f"outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                    ),
                    row_indices=outlier_indices,
                    metadata={
                        "outlier_count": int(outlier_count),
                        "total_count": int(total_count),
                        "outlier_percentage": float(outlier_percentage),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound),
                        "q1": float(q1),
                        "q3": float(q3),
                        "iqr": float(iqr),
                        "iqr_multiplier": float(self.iqr_multiplier),
                    },
                )
                findings.append(finding)

        return findings
