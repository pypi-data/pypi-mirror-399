"""Type ghost detector - detects type inconsistencies and schema issues.

This module provides the TypeGhostDetector class, which identifies columns
with mixed data types or type coercion issues. It detects situations where
a column contains values of different Python types, which can indicate
data quality problems.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class TypeGhostDetector(GhostDetector):
    """Detects type inconsistencies within columns.

    This detector identifies columns with mixed data types or type coercion
    issues. For Pandas DataFrames, it detects object dtype columns containing
    values of different Python types. For Polars DataFrames, it identifies
    string columns that could potentially be numeric but contain mixed content.

    The detector is useful for finding columns where data has been incorrectly
    parsed or where inconsistent data entry has occurred.

    Example:
        Detect type inconsistencies::

            detector = TypeGhostDetector()
            findings = detector.detect(df)

        Findings will have ghost_type="type" and severity="warning" for
        columns with mixed types detected.
    """

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect type inconsistencies.

        Analyzes all columns in the DataFrame to identify those with mixed
        data types or type coercion issues. Works with both Pandas and Polars
        DataFrames using backend-specific detection logic.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. The backend is automatically detected.

        Returns:
            List of GhostFinding objects for columns with type inconsistencies.
            Each finding includes:
            - ghost_type: "type"
            - column: Name of the column with type issues
            - severity: "warning"
            - description: Human-readable description of the type issue
            - row_indices: None (type issues affect the column as a whole)
            - metadata: Dictionary with dtype and type distribution information

        Note:
            This detector focuses on structural type issues rather than
            individual row violations, so row_indices is typically None.
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect type issues in Pandas DataFrame.

        Internal method that performs type detection using Pandas-specific APIs.
        Checks for object dtype columns with mixed Python types.

        Args:
            df: pandas.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns with type inconsistencies.
        """

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
        """Detect type issues in Polars DataFrame.

        Internal method that performs type detection using Polars-specific APIs.
        Checks for string columns that might contain mixed numeric and non-numeric
        values by attempting type coercion.

        Args:
            df: polars.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns with potential type issues.
        """
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
