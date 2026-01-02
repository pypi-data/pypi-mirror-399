"""Time-series anomaly detector - detects anomalies in time-series data.

This module provides the TimeSeriesAnomalyDetector class, which identifies
anomalies in time-series data using various statistical methods including
z-score, moving average deviations, and seasonal decomposition.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class TimeSeriesAnomalyDetector(GhostDetector):
    """Detects anomalies in time-series data using statistical methods.

    This detector analyzes time-series data to identify anomalous values or
    patterns. It supports multiple detection methods:
    - Z-score: Detects values that deviate significantly from the mean
    - Moving average: Detects values that deviate from a moving average
    - Seasonal: Detects anomalies after removing seasonal patterns (requires statsmodels)

    The detector automatically detects datetime columns or can use a specified
    datetime column. It analyzes numeric columns as time-series values.

    Attributes:
        datetime_column: Name of the datetime column to use for time ordering.
            If None, attempts to auto-detect a datetime column.
        method: Detection method to use. Options: "zscore", "moving_avg", "seasonal".
            Default is "zscore".
        sensitivity: Sensitivity threshold for anomaly detection. Higher values
            detect fewer anomalies. Default is 3.0 (for z-score, this is the
            number of standard deviations).
        window_size: Window size for moving average method. Default is 10.

    Example:
        Use default z-score method with auto-detected datetime column::

            detector = TimeSeriesAnomalyDetector()
            findings = detector.detect(df)

        Use moving average method with specific datetime column::

            detector = TimeSeriesAnomalyDetector(
                datetime_column="timestamp",
                method="moving_avg",
                window_size=20
            )
            findings = detector.detect(df)
    """

    def __init__(
        self,
        datetime_column: str | None = None,
        method: str = "zscore",
        sensitivity: float = 3.0,
        window_size: int = 10,
    ) -> None:
        """Initialize the time-series anomaly detector.

        Args:
            datetime_column: Name of the datetime column to use for time ordering.
                If None, attempts to auto-detect a datetime column. The column
                must exist in the DataFrame and be convertible to datetime.
            method: Detection method to use. Valid options:
                - "zscore": Z-score method (default)
                - "moving_avg": Moving average deviation method
                - "seasonal": Seasonal decomposition method (requires statsmodels)
            sensitivity: Sensitivity threshold for anomaly detection. For z-score,
                this is the number of standard deviations. For moving average,
                this is a multiplier of the rolling standard deviation. Higher
                values detect fewer anomalies. Default is 3.0.
            window_size: Window size for moving average method. Must be positive.
                Default is 10.

        Raises:
            ValueError: If method is not one of the valid options, or if
                window_size is not positive, or if sensitivity is not positive.
        """
        valid_methods = {"zscore", "moving_avg", "seasonal"}
        if method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}, got {method}")
        if sensitivity <= 0:
            raise ValueError(f"sensitivity must be positive, got {sensitivity}")
        if window_size <= 0:
            raise ValueError(f"window_size must be positive, got {window_size}")

        self.datetime_column = datetime_column
        self.method = method
        self.sensitivity = sensitivity
        self.window_size = window_size

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect time-series anomalies in numeric columns.

        Analyzes numeric columns as time-series data to identify anomalous values.
        The DataFrame must have a datetime column for time ordering. Works with
        both Pandas and Polars DataFrames.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. Must contain at least one datetime column
                and one numeric column.

        Returns:
            List of GhostFinding objects for columns containing time-series
            anomalies. Each finding includes:
            - ghost_type: "timeseries_anomaly"
            - column: Name of the column with anomalies
            - severity: "warning" if >5% anomalies, "info" otherwise
            - description: Human-readable description with anomaly counts,
              percentages, and method used
            - row_indices: List of row indices with anomalous values (Pandas only,
              None for Polars)
            - metadata: Dictionary with anomaly_count, total_count,
              anomaly_percentage, method, sensitivity, and method-specific stats

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts. The finding will still include anomaly
            counts and statistics.
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect time-series anomalies in Pandas DataFrame.

        Internal method that performs time-series anomaly detection using
        Pandas-specific APIs. Includes row indices for each anomaly.

        Args:
            df: pandas.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing anomalies.
        """
        import pandas as pd
        import numpy as np

        findings: list[GhostFinding] = []

        # Detect or use specified datetime column
        datetime_col = self._detect_datetime_column(df)
        if datetime_col is None:
            # No datetime column found, skip time-series detection
            return findings

        # Ensure datetime column is datetime type
        df_sorted = df.copy()
        df_sorted[datetime_col] = pd.to_datetime(df_sorted[datetime_col])
        df_sorted = df_sorted.sort_values(by=datetime_col)

        # Get numeric columns (exclude datetime column)
        numeric_columns = df_sorted.select_dtypes(include=[np.number]).columns.tolist()
        if datetime_col in numeric_columns:
            numeric_columns.remove(datetime_col)

        if not numeric_columns:
            return findings

        # Analyze each numeric column
        for column in numeric_columns:
            column_data = df_sorted[column].dropna()

            if len(column_data) < 3:  # Need at least 3 values
                continue

            anomalies, metadata = self._detect_anomalies_pandas(
                column_data, df_sorted.index
            )

            if len(anomalies) > 0:
                anomaly_count = len(anomalies)
                total_count = len(column_data)
                anomaly_percentage = (
                    anomaly_count / total_count if total_count > 0 else 0.0
                )

                # Determine severity
                if anomaly_percentage > 0.05:  # More than 5% anomalies
                    severity = "warning"
                else:
                    severity = "info"

                finding = GhostFinding(
                    ghost_type="timeseries_anomaly",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {anomaly_count:,} time-series anomalies "
                        f"({anomaly_percentage:.1%} of {total_count:,} values) "
                        f"detected using {self.method} method"
                    ),
                    row_indices=anomalies,
                    metadata={
                        "anomaly_count": anomaly_count,
                        "total_count": total_count,
                        "anomaly_percentage": float(anomaly_percentage),
                        "method": self.method,
                        "sensitivity": float(self.sensitivity),
                        "datetime_column": datetime_col,
                        **metadata,
                    },
                )
                findings.append(finding)

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect time-series anomalies in Polars DataFrame.

        Internal method that performs time-series anomaly detection using
        Polars-specific APIs. Note that row_indices will be None as Polars
        doesn't maintain index concepts.

        Args:
            df: polars.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing anomalies.
            row_indices will be None for all findings.
        """
        import polars as pl

        findings: list[GhostFinding] = []

        # Detect or use specified datetime column
        datetime_col = self._detect_datetime_column(df)
        if datetime_col is None:
            return findings

        # Ensure datetime column is datetime type and sort
        df_sorted = df.with_columns(
            pl.col(datetime_col).str.to_datetime().alias(datetime_col)
        ).sort(datetime_col)

        # Get numeric columns
        numeric_columns = [
            col
            for col, dtype in df_sorted.schema.items()
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
            and col != datetime_col
        ]

        if not numeric_columns:
            return findings

        # Analyze each numeric column
        for column in numeric_columns:
            column_data = df_sorted.select(pl.col(column).drop_nulls())

            if len(column_data) < 3:
                continue

            anomalies, metadata = self._detect_anomalies_polars(
                df_sorted, column, datetime_col
            )

            if len(anomalies) > 0:
                anomaly_count = len(anomalies)
                total_count = len(column_data)
                anomaly_percentage = (
                    anomaly_count / total_count if total_count > 0 else 0.0
                )

                # Determine severity
                if anomaly_percentage > 0.05:
                    severity = "warning"
                else:
                    severity = "info"

                finding = GhostFinding(
                    ghost_type="timeseries_anomaly",
                    column=column,
                    severity=severity,
                    description=(
                        f"Column '{column}' has {anomaly_count:,} time-series anomalies "
                        f"({anomaly_percentage:.1%} of {total_count:,} values) "
                        f"detected using {self.method} method"
                    ),
                    row_indices=None,  # Polars doesn't maintain indices
                    metadata={
                        "anomaly_count": anomaly_count,
                        "total_count": total_count,
                        "anomaly_percentage": float(anomaly_percentage),
                        "method": self.method,
                        "sensitivity": float(self.sensitivity),
                        "datetime_column": datetime_col,
                        **metadata,
                    },
                )
                findings.append(finding)

        return findings

    def _detect_datetime_column(self, df: object) -> str | None:
        """Detect or validate datetime column.

        Args:
            df: DataFrame to check.

        Returns:
            Name of datetime column, or None if not found.
        """
        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            import pandas as pd

            # If specified, validate it exists and is datetime-like
            if self.datetime_column:
                if self.datetime_column in df.columns:
                    # Try to convert to check if it's datetime-like
                    try:
                        pd.to_datetime(df[self.datetime_column].iloc[0])
                        return self.datetime_column
                    except (ValueError, TypeError):
                        pass

            # Auto-detect: look for datetime columns
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    return col
                # Try converting first value
                try:
                    pd.to_datetime(df[col].iloc[0])
                    return col
                except (ValueError, TypeError, IndexError):
                    continue

        elif backend == "polars":
            import polars as pl

            # If specified, validate it exists
            if self.datetime_column:
                if self.datetime_column in df.columns:
                    dtype = df.schema[self.datetime_column]
                    if dtype in [pl.Datetime, pl.Date]:
                        return self.datetime_column
                    # Try converting
                    try:
                        df.select(pl.col(self.datetime_column).str.to_datetime())
                        return self.datetime_column
                    except Exception:
                        pass

            # Auto-detect: look for datetime columns
            for col, dtype in df.schema.items():
                if dtype in [pl.Datetime, pl.Date]:
                    return col

        return None

    def _detect_anomalies_pandas(
        self, column_data: object, original_indices: object
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using the configured method (Pandas).

        Args:
            column_data: Pandas Series with numeric values.
            original_indices: Original DataFrame indices.

        Returns:
            Tuple of (list of anomaly indices, metadata dict).
        """
        if self.method == "zscore":
            return self._detect_zscore_pandas(column_data, original_indices)
        elif self.method == "moving_avg":
            return self._detect_moving_avg_pandas(column_data, original_indices)
        elif self.method == "seasonal":
            return self._detect_seasonal_pandas(column_data, original_indices)
        else:
            return [], {}

    def _detect_zscore_pandas(
        self, column_data: object, original_indices: object
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using z-score method (Pandas).

        Args:
            column_data: Pandas Series with numeric values.
            original_indices: Original DataFrame indices.

        Returns:
            Tuple of (list of anomaly indices, metadata dict).
        """
        import numpy as np
        import pandas as pd

        mean = column_data.mean()
        std = column_data.std()

        if std == 0 or pd.isna(std):
            return [], {
                "mean": float(mean),
                "std": float(std) if not pd.isna(std) else 0.0,
            }

        z_scores = np.abs((column_data - mean) / std)
        anomalies_mask = z_scores > self.sensitivity

        anomaly_indices = original_indices[anomalies_mask].tolist()

        metadata = {
            "mean": float(mean),
            "std": float(std),
            "z_score_threshold": float(self.sensitivity),
        }

        return anomaly_indices, metadata

    def _detect_moving_avg_pandas(
        self, column_data: object, original_indices: object
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using moving average method (Pandas).

        Args:
            column_data: Pandas Series with numeric values.
            original_indices: Original DataFrame indices.

        Returns:
            Tuple of (list of anomaly indices, metadata dict).
        """
        if len(column_data) < self.window_size:
            return [], {"window_size": self.window_size}

        rolling_mean = column_data.rolling(window=self.window_size, center=True).mean()
        rolling_std = column_data.rolling(window=self.window_size, center=True).std()

        # Fill NaN values at edges
        rolling_mean = rolling_mean.bfill().ffill()
        rolling_std = rolling_std.bfill().ffill()

        # Calculate deviations
        import numpy as np

        deviations = column_data - rolling_mean
        threshold = self.sensitivity * rolling_std

        anomalies_mask = np.abs(deviations) > threshold

        anomaly_indices = original_indices[anomalies_mask].tolist()

        metadata = {
            "window_size": self.window_size,
            "sensitivity_multiplier": float(self.sensitivity),
        }

        return anomaly_indices, metadata

    def _detect_seasonal_pandas(
        self, column_data: object, original_indices: object
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using seasonal decomposition (Pandas).

        Args:
            column_data: Pandas Series with numeric values.
            original_indices: Original DataFrame indices.

        Returns:
            Tuple of (list of anomaly indices, metadata dict).
        """
        try:
            from statsmodels.tsa.seasonal import seasonal_decompose
        except ImportError:
            # Fall back to z-score if statsmodels not available
            return self._detect_zscore_pandas(column_data, original_indices)

        import pandas as pd
        import numpy as np

        if len(column_data) < 2 * self.window_size:
            # Not enough data for seasonal decomposition, fall back to z-score
            return self._detect_zscore_pandas(column_data, original_indices)

        # Create a DatetimeIndex for seasonal_decompose
        if not isinstance(column_data.index, pd.DatetimeIndex):
            date_range = pd.date_range(
                start="2000-01-01", periods=len(column_data), freq="D"
            )
            column_data_indexed = pd.Series(column_data.values, index=date_range)
        else:
            column_data_indexed = column_data

        try:
            decomposition = seasonal_decompose(
                column_data_indexed, model="additive", period=self.window_size
            )
            residuals = decomposition.resid.dropna()

            if len(residuals) == 0:
                return [], {}

            # Detect anomalies in residuals using z-score
            mean_residual = residuals.mean()
            std_residual = residuals.std()

            if std_residual == 0 or pd.isna(std_residual):
                return [], {}

            z_scores = np.abs((residuals - mean_residual) / std_residual)
            anomalies_mask = z_scores > self.sensitivity

            # Map back to original indices
            anomaly_indices = original_indices[anomalies_mask].tolist()

            metadata = {
                "window_size": self.window_size,
                "residual_mean": float(mean_residual),
                "residual_std": float(std_residual),
            }

            return anomaly_indices, metadata
        except Exception:
            # If decomposition fails, fall back to z-score
            return self._detect_zscore_pandas(column_data, original_indices)

    def _detect_anomalies_polars(
        self, df: object, column: str, datetime_col: str
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using the configured method (Polars).

        Args:
            df: Polars DataFrame.
            column: Column name to analyze.
            datetime_col: Datetime column name.

        Returns:
            Tuple of (list of anomaly row numbers, metadata dict).
        """

        if self.method == "zscore":
            return self._detect_zscore_polars(df, column)
        elif self.method == "moving_avg":
            return self._detect_moving_avg_polars(df, column)
        elif self.method == "seasonal":
            # Seasonal decomposition is complex in Polars, convert to pandas
            return self._detect_seasonal_polars(df, column)
        else:
            return [], {}

    def _detect_zscore_polars(
        self, df: object, column: str
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using z-score method (Polars).

        Args:
            df: Polars DataFrame.
            column: Column name to analyze.

        Returns:
            Tuple of (list of anomaly row numbers, metadata dict).
        """
        import polars as pl

        stats = df.select(
            [
                pl.col(column).mean().alias("mean"),
                pl.col(column).std().alias("std"),
            ]
        )

        mean_val = stats["mean"][0]
        std_val = stats["std"][0]

        if std_val == 0 or std_val is None:
            return [], {"mean": float(mean_val) if mean_val else 0.0, "std": 0.0}

        # Calculate z-scores and find anomalies
        anomalies_df = df.filter(
            (pl.col(column) - mean_val).abs() / std_val > self.sensitivity
        )

        # For Polars, we return row numbers (0-based)
        anomaly_rows = list(range(len(anomalies_df)))

        metadata = {
            "mean": float(mean_val),
            "std": float(std_val),
            "z_score_threshold": float(self.sensitivity),
        }

        return anomaly_rows, metadata

    def _detect_moving_avg_polars(
        self, df: object, column: str
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using moving average method (Polars).

        Args:
            df: Polars DataFrame.
            column: Column name to analyze.

        Returns:
            Tuple of (list of anomaly row numbers, metadata dict).
        """
        import polars as pl

        if len(df) < self.window_size:
            return [], {"window_size": self.window_size}

        # Calculate rolling mean and std
        df_with_rolling = df.with_columns(
            [
                pl.col(column)
                .rolling_mean(window_size=self.window_size, center=True)
                .alias("rolling_mean"),
                pl.col(column)
                .rolling_std(window_size=self.window_size, center=True)
                .alias("rolling_std"),
            ]
        )

        # Fill nulls at edges
        df_with_rolling = df_with_rolling.with_columns(
            [
                pl.col("rolling_mean").forward_fill().backward_fill(),
                pl.col("rolling_std").forward_fill().backward_fill(),
            ]
        )

        # Calculate deviations and find anomalies
        anomalies_df = df_with_rolling.filter(
            (pl.col(column) - pl.col("rolling_mean")).abs()
            > self.sensitivity * pl.col("rolling_std")
        )

        # For Polars, we return row numbers
        anomaly_rows = list(range(len(anomalies_df)))

        metadata = {
            "window_size": self.window_size,
            "sensitivity_multiplier": float(self.sensitivity),
        }

        return anomaly_rows, metadata

    def _detect_seasonal_polars(
        self, df: object, column: str
    ) -> tuple[list[int], dict[str, float]]:
        """Detect anomalies using seasonal decomposition (Polars).

        Args:
            df: Polars DataFrame.
            column: Column name to analyze.

        Returns:
            Tuple of (list of anomaly row numbers, metadata dict).
        """
        # Convert to pandas for seasonal decomposition, then back
        try:
            df_pandas = df.to_pandas()
            column_data = df_pandas[column].dropna()
            original_indices = df_pandas.index

            anomaly_indices, metadata = self._detect_seasonal_pandas(
                column_data, original_indices
            )

            # Convert indices to row numbers
            anomaly_rows = [int(idx) for idx in anomaly_indices if idx is not None]

            return anomaly_rows, metadata
        except Exception:
            # Fall back to z-score
            return self._detect_zscore_polars(df, column)
