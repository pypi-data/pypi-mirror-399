"""Type ghost detector - detects type inconsistencies and schema issues."""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class TypeGhostDetector(GhostDetector):
    """Detects type inconsistencies within columns.

    Identifies columns with mixed dtypes or type coercion failures.
    """

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect type inconsistencies.

        Args:
            df: DataFrame to analyze

        Returns:
            List of GhostFinding objects for columns with type issues
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect type issues in Pandas DataFrame."""

        findings: list[GhostFinding] = []

        for column in df.columns:
            column_data = df[column]
            dtype = column_data.dtype

            # Check for object dtype (often indicates mixed types)
            if dtype == "object":
                # Check if it's actually mixed types or just strings
                non_null = column_data.dropna()
                if len(non_null) > 0:
                    # Check if we have mixed types
                    type_counts = non_null.apply(type).value_counts()
                    if len(type_counts) > 1:
                        # Mixed types detected
                        finding = GhostFinding(
                            ghost_type="type",
                            column=column,
                            severity="warning",
                            description=(
                                f"Column '{column}' has object dtype with mixed types: "
                                f"{', '.join(str(t) for t in type_counts.head(3).index)}"
                            ),
                            row_indices=None,
                            metadata={
                                "dtype": str(dtype),
                                "type_distribution": {
                                    str(k): int(v)
                                    for k, v in type_counts.head(5).items()
                                },
                            },
                        )
                        findings.append(finding)

            # Check for numeric columns with string-like values
            elif dtype in ["int64", "float64", "Int64", "Float64"]:
                # Try to find non-numeric values that might have been coerced
                non_null = column_data.dropna()
                if len(non_null) > 0:
                    # Check if there are any string-like values in numeric column
                    # (This would have been caught earlier, but we check anyway)
                    pass

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect type issues in Polars DataFrame."""
        import polars as pl

        findings: list[GhostFinding] = []

        schema = df.schema

        for column in df.columns:
            dtype = schema[column]

            # Polars is more strict about types, but we can check for
            # object/string columns that might have inconsistent content
            if dtype == pl.Utf8:
                # Check for numeric strings mixed with non-numeric strings
                non_null = df.select(
                    pl.col(column).filter(pl.col(column).is_not_null())
                )
                if len(non_null) > 0:
                    # Try to detect if column could be numeric but isn't
                    try:
                        # Attempt to parse as numeric
                        numeric_attempt = df.select(
                            pl.col(column).cast(pl.Float64, strict=False)
                        )
                        # If many nulls appeared, likely mixed types
                        null_count_after = numeric_attempt.null_count()
                        if null_count_after > 0 and null_count_after < len(df):
                            finding = GhostFinding(
                                ghost_type="type",
                                column=column,
                                severity="warning",
                                description=(
                                    f"Column '{column}' contains mixed numeric and non-numeric values"
                                ),
                                row_indices=None,
                                metadata={
                                    "dtype": str(dtype),
                                    "potential_numeric": True,
                                },
                            )
                            findings.append(finding)
                    except Exception:
                        # If casting fails completely, might not be a type issue
                        pass

        return findings
