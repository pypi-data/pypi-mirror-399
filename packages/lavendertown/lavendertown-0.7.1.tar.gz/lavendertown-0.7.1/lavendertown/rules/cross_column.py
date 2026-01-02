"""Cross-column validation rule executors.

This module provides executors for cross-column validation rules that check
relationships between multiple columns, such as equality, comparison,
arithmetic operations, conditional logic, and referential integrity.
"""

from __future__ import annotations

from lavendertown.detectors.base import detect_dataframe_backend
from lavendertown.models import GhostFinding
from lavendertown.rules.base import CustomRule


class CrossColumnRule(CustomRule):
    """Base class for cross-column validation rules.

    Cross-column rules validate relationships between multiple columns in a
    DataFrame. They can check equality, comparisons, arithmetic operations,
    conditional logic, and referential integrity.

    Attributes:
        name: Human-readable rule name.
        description: Description of what the rule checks.
        source_columns: List of column names to check (at least 2 required).
        operation: Type of operation to perform. Valid options:
            - "equals": Column A must equal Column B
            - "greater_than": Column A must be greater than Column B
            - "less_than": Column A must be less than Column B
            - "sum_equals": Sum of source columns must equal target column
            - "conditional": If condition is met, then check another condition
            - "referential": Values in source column must exist in target column
        target_column: Optional target column for operations like sum_equals
            or referential integrity.
        condition: Optional dictionary for conditional rules containing:
            - "if_column": Column to check condition on
            - "if_value": Value to check for
            - "then_column": Column to validate if condition is met
            - "then_value": Expected value in then_column
    """

    def __init__(
        self,
        name: str,
        description: str,
        source_columns: list[str],
        operation: str,
        target_column: str | None = None,
        condition: dict[str, str] | None = None,
    ) -> None:
        """Initialize cross-column rule.

        Args:
            name: Human-readable rule name.
            description: Description of what the rule checks.
            source_columns: List of column names to check. Must have at least 2.
            operation: Type of operation. Must be one of: "equals", "greater_than",
                "less_than", "sum_equals", "conditional", "referential".
            target_column: Optional target column for operations that require it.
            condition: Optional condition dictionary for conditional rules.

        Raises:
            ValueError: If source_columns has fewer than 2 columns, or if operation
                is invalid, or if required columns are missing for specific operations.
        """
        # Referential rules only need 1 source column
        if operation != "referential" and len(source_columns) < 2:
            raise ValueError(
                f"Cross-column rules require at least 2 columns, got {len(source_columns)}"
            )
        if operation == "referential" and len(source_columns) < 1:
            raise ValueError(
                f"Referential rules require at least 1 source column, got {len(source_columns)}"
            )

        valid_operations = {
            "equals",
            "greater_than",
            "less_than",
            "sum_equals",
            "conditional",
            "referential",
        }
        if operation not in valid_operations:
            raise ValueError(
                f"Operation must be one of {valid_operations}, got {operation}"
            )

        if operation in ["sum_equals", "referential"] and target_column is None:
            raise ValueError(
                f"Operation '{operation}' requires a target_column to be specified"
            )

        if operation == "conditional" and condition is None:
            raise ValueError("Operation 'conditional' requires a condition dictionary")

        super().__init__(
            name, description, column=None
        )  # Cross-column rules don't have a single column
        self.source_columns = source_columns
        self.operation = operation
        self.target_column = target_column
        self.condition = condition

    def check(self, df: object) -> list[GhostFinding]:
        """Check cross-column rule against DataFrame.

        Args:
            df: DataFrame to check. Can be pandas.DataFrame or polars.DataFrame.

        Returns:
            List of GhostFinding objects for rule violations. Returns empty list
            if no violations found. Returns a single error finding if columns
            don't exist or rule is misconfigured.
        """
        backend = detect_dataframe_backend(df)

        # Validate columns exist
        missing_columns = []
        for col in self.source_columns:
            if backend == "pandas":
                if col not in df.columns:  # type: ignore[attr-defined]
                    missing_columns.append(col)
            else:
                if col not in df.schema:  # type: ignore[attr-defined]
                    missing_columns.append(col)
        if self.target_column:
            if backend == "pandas":
                if self.target_column not in df.columns:  # type: ignore[attr-defined]
                    missing_columns.append(self.target_column)
            else:
                if self.target_column not in df.schema:  # type: ignore[attr-defined]
                    missing_columns.append(self.target_column)
        if self.condition:
            if_col = self.condition.get("if_column")
            then_col = self.condition.get("then_column")
            if if_col:
                if backend == "pandas":
                    if if_col not in df.columns:  # type: ignore[attr-defined]
                        missing_columns.append(if_col)
                else:
                    if if_col not in df.schema:  # type: ignore[attr-defined]
                        missing_columns.append(if_col)
            if then_col:
                if backend == "pandas":
                    if then_col not in df.columns:  # type: ignore[attr-defined]
                        missing_columns.append(then_col)
                else:
                    if then_col not in df.schema:  # type: ignore[attr-defined]
                        missing_columns.append(then_col)

        if missing_columns:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column="",
                    severity="error",
                    description=(
                        f"Rule '{self.name}': Missing columns: {', '.join(missing_columns)}"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "missing_columns": missing_columns,
                    },
                )
            ]

        if backend == "pandas":
            return self._check_pandas(df)
        elif backend == "polars":
            return self._check_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _check_pandas(self, df: object) -> list[GhostFinding]:
        """Check rule using Pandas API.

        Args:
            df: pandas.DataFrame to check.

        Returns:
            List of GhostFinding objects for violations.
        """

        if self.operation == "equals":
            return self._check_equals_pandas(df)
        elif self.operation == "greater_than":
            return self._check_greater_than_pandas(df)
        elif self.operation == "less_than":
            return self._check_less_than_pandas(df)
        elif self.operation == "sum_equals":
            return self._check_sum_equals_pandas(df)
        elif self.operation == "conditional":
            return self._check_conditional_pandas(df)
        elif self.operation == "referential":
            return self._check_referential_pandas(df)
        else:
            return []

    def _check_polars(self, df: object) -> list[GhostFinding]:
        """Check rule using Polars API.

        Args:
            df: polars.DataFrame to check.

        Returns:
            List of GhostFinding objects for violations.
        """

        if self.operation == "equals":
            return self._check_equals_polars(df)
        elif self.operation == "greater_than":
            return self._check_greater_than_polars(df)
        elif self.operation == "less_than":
            return self._check_less_than_polars(df)
        elif self.operation == "sum_equals":
            return self._check_sum_equals_polars(df)
        elif self.operation == "conditional":
            return self._check_conditional_polars(df)
        elif self.operation == "referential":
            return self._check_referential_polars(df)
        else:
            return []

    def _check_equals_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if two columns are equal (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]
        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations = df_pd[col1] != df_pd[col2]
        violations = violations & df_pd[col1].notna() & df_pd[col2].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,  # Use first column as primary
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"'{col1}' != '{col2}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "equals",
                        "columns": [col1, col2],
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_equals_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if two columns are equal (Polars)."""
        import polars as pl

        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations_df = df.filter(  # type: ignore[attr-defined]
            (pl.col(col1) != pl.col(col2))
            & pl.col(col1).is_not_null()
            & pl.col(col2).is_not_null()
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"'{col1}' != '{col2}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "equals",
                        "columns": [col1, col2],
                        "violation_count": violation_count,
                    },
                )
            ]
        return []

    def _check_greater_than_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if col1 > col2 (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]
        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations = df_pd[col1] <= df_pd[col2]
        violations = violations & df_pd[col1].notna() & df_pd[col2].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"'{col1}' <= '{col2}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "greater_than",
                        "columns": [col1, col2],
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_greater_than_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if col1 > col2 (Polars)."""
        import polars as pl

        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations_df = df.filter(  # type: ignore[attr-defined]
            (pl.col(col1) <= pl.col(col2))
            & pl.col(col1).is_not_null()
            & pl.col(col2).is_not_null()
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"'{col1}' <= '{col2}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "greater_than",
                        "columns": [col1, col2],
                        "violation_count": violation_count,
                    },
                )
            ]
        return []

    def _check_less_than_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if col1 < col2 (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]
        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations = df_pd[col1] >= df_pd[col2]
        violations = violations & df_pd[col1].notna() & df_pd[col2].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"'{col1}' >= '{col2}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "less_than",
                        "columns": [col1, col2],
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_less_than_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if col1 < col2 (Polars)."""
        import polars as pl

        col1, col2 = self.source_columns[0], self.source_columns[1]
        violations_df = df.filter(  # type: ignore[attr-defined]
            (pl.col(col1) >= pl.col(col2))
            & pl.col(col1).is_not_null()
            & pl.col(col2).is_not_null()
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=col1,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"'{col1}' >= '{col2}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "less_than",
                        "columns": [col1, col2],
                        "violation_count": violation_count,
                    },
                )
            ]
        return []

    def _check_sum_equals_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if sum of source columns equals target column (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]
        sum_cols = self.source_columns
        target_col = self.target_column

        if target_col is None:
            return []

        # Calculate sum of source columns
        sum_values = df_pd[sum_cols].sum(axis=1)
        violations = sum_values != df_pd[target_col]
        violations = violations & sum_values.notna() & df_pd[target_col].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=target_col,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"sum({', '.join(sum_cols)}) != '{target_col}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "sum_equals",
                        "source_columns": sum_cols,
                        "target_column": target_col,
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_sum_equals_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check if sum of source columns equals target column (Polars)."""
        import polars as pl

        sum_cols = self.source_columns
        target_col = self.target_column

        if target_col is None:
            return []

        # Calculate sum
        sum_expr = sum([pl.col(col) for col in sum_cols])  # type: ignore[arg-type]
        violations_df = df.filter(  # type: ignore[attr-defined]  # type: ignore[attr-defined]
            (sum_expr != pl.col(target_col))  # type: ignore[union-attr]
            & sum_expr.is_not_null()  # type: ignore[union-attr]
            & pl.col(target_col).is_not_null()  # type: ignore[union-attr]
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=target_col,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"sum({', '.join(sum_cols)}) != '{target_col}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "sum_equals",
                        "source_columns": sum_cols,
                        "target_column": target_col,
                        "violation_count": violation_count,
                    },
                )
            ]
        return []

    def _check_conditional_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check conditional rule: if col1 == X then col2 == Y (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]

        if self.condition is None:
            return []

        if_col = self.condition.get("if_column")
        if_value = self.condition.get("if_value")
        then_col = self.condition.get("then_column")
        then_value = self.condition.get("then_value")

        if not all([if_col, if_value, then_col, then_value]):
            return []

        # Find rows where condition is met
        condition_met = df_pd[if_col] == if_value
        condition_met = condition_met & df_pd[if_col].notna()

        # Check if then condition is violated
        violations = condition_met & (df_pd[then_col] != then_value)
        violations = violations & df_pd[then_col].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=then_col if then_col else "",
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"'{if_col}' == '{if_value}' but '{then_col}' != '{then_value}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "conditional",
                        "condition": self.condition,
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_conditional_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check conditional rule: if col1 == X then col2 == Y (Polars)."""
        import polars as pl

        if self.condition is None:
            return []

        if_col = self.condition.get("if_column")
        if_value = self.condition.get("if_value")
        then_col = self.condition.get("then_column")
        then_value = self.condition.get("then_value")

        if not all([if_col, if_value, then_col, then_value]):
            return []

        # Find violations
        violations_df = df.filter(  # type: ignore[attr-defined]  # type: ignore[attr-defined]
            (pl.col(if_col if if_col else "") == if_value)
            & pl.col(if_col if if_col else "").is_not_null()
            & (pl.col(then_col if then_col else "") != then_value)
            & pl.col(then_col if then_col else "").is_not_null()
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=then_col if then_col else "",
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"'{if_col}' == '{if_value}' but '{then_col}' != '{then_value}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "conditional",
                        "condition": self.condition,
                        "violation_count": violation_count,
                    },
                )
            ]
        return []

    def _check_referential_pandas(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check referential integrity: source column values must exist in target (Pandas)."""
        import pandas as pd

        df_pd: pd.DataFrame = df  # type: ignore[assignment]
        source_col = self.source_columns[0]
        target_col = self.target_column

        if target_col is None:
            return []

        # Get valid values from target column
        valid_values = set(df_pd[target_col].dropna().unique())

        # Find violations
        violations = ~df_pd[source_col].isin(valid_values)
        violations = violations & df_pd[source_col].notna()

        violation_indices = df_pd[violations].index.tolist()

        if len(violation_indices) > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=source_col,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {len(violation_indices)} rows where "
                        f"'{source_col}' values don't exist in '{target_col}'"
                    ),
                    row_indices=violation_indices,
                    metadata={
                        "rule_name": self.name,
                        "operation": "referential",
                        "source_column": source_col,
                        "target_column": target_col,
                        "violation_count": len(violation_indices),
                    },
                )
            ]
        return []

    def _check_referential_polars(self, df: object) -> list[GhostFinding]:  # type: ignore[type-arg]
        """Check referential integrity: source column values must exist in target (Polars)."""
        import polars as pl

        source_col = self.source_columns[0]
        target_col = self.target_column

        if target_col is None:
            return []

        # Get valid values
        valid_values = (
            df.select(pl.col(target_col).drop_nulls()).unique().to_series().to_list()  # type: ignore[attr-defined]
        )

        # Find violations
        violations_df = df.filter(  # type: ignore[attr-defined]  # type: ignore[attr-defined]
            ~pl.col(source_col).is_in(valid_values) & pl.col(source_col).is_not_null()
        )

        violation_count = len(violations_df)

        if violation_count > 0:
            return [
                GhostFinding(
                    ghost_type="rule",
                    column=source_col,
                    severity="warning",
                    description=(
                        f"Rule '{self.name}': {violation_count} rows where "
                        f"'{source_col}' values don't exist in '{target_col}'"
                    ),
                    row_indices=None,
                    metadata={
                        "rule_name": self.name,
                        "operation": "referential",
                        "source_column": source_col,
                        "target_column": target_col,
                        "violation_count": violation_count,
                    },
                )
            ]
        return []
