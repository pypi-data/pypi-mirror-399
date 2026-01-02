"""Change point detection detector - detects sudden changes in time-series data.

This module provides the ChangePointDetector class, which identifies change points
in time-series data using the Ruptures library. Change points are locations where
the statistical properties of the data change abruptly.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class ChangePointDetector(GhostDetector):
    """Detects change points in time-series data using Ruptures.

    This detector identifies sudden changes in the statistical properties of
    time-series data. It uses the Ruptures library which provides multiple
    algorithms for change point detection.

    The detector analyzes numeric columns as time series and identifies points
    where the distribution, mean, variance, or other statistical properties
    change significantly.

    Attributes:
        algorithm: Change point detection algorithm to use. Options:
            - "pelt": Pruned Exact Linear Time (default, fast and accurate)
            - "binseg": Binary Segmentation
            - "window": Window-based detection
            - "dynp": Dynamic Programming (slower but optimal)
        min_size: Minimum segment size between change points. Default is 2.
        penalty: Penalty parameter for change point detection. Higher values
            result in fewer change points. Default is 10.0.
        n_bkps: Number of change points to detect (for dynp algorithm).
            If None, uses penalty-based detection. Default is None.

    Example:
        Use default Pelt algorithm::

            detector = ChangePointDetector()
            findings = detector.detect(df)

        Use Binary Segmentation with custom penalty::

            detector = ChangePointDetector(
                algorithm="binseg",
                penalty=20.0,
                min_size=5
            )
            findings = detector.detect(df)
    """

    def __init__(
        self,
        algorithm: str = "pelt",
        min_size: int = 2,
        penalty: float = 10.0,
        n_bkps: int | None = None,
    ) -> None:
        """Initialize change point detector.

        Args:
            algorithm: Change point detection algorithm. Valid options:
                "pelt" (default), "binseg", "window", "dynp"
            min_size: Minimum segment size between change points. Must be >= 2.
                Default is 2.
            penalty: Penalty parameter for change point detection. Higher values
                result in fewer change points. Must be positive. Default is 10.0.
            n_bkps: Number of change points to detect (for dynp algorithm).
                If None, uses penalty-based detection. Must be >= 1 if specified.
                Default is None.

        Raises:
            ValueError: If algorithm is invalid, min_size < 2, penalty <= 0,
                or n_bkps < 1.
            ImportError: If ruptures is not installed (raised during detect).
        """
        valid_algorithms = {"pelt", "binseg", "window", "dynp"}
        if algorithm not in valid_algorithms:
            raise ValueError(
                f"Algorithm must be one of {valid_algorithms}, got {algorithm}"
            )

        if min_size < 2:
            raise ValueError(f"min_size must be >= 2, got {min_size}")

        if penalty <= 0:
            raise ValueError(f"penalty must be positive, got {penalty}")

        if n_bkps is not None and n_bkps < 1:
            raise ValueError(f"n_bkps must be >= 1, got {n_bkps}")

        self.algorithm = algorithm
        self.min_size = min_size
        self.penalty = penalty
        self.n_bkps = n_bkps

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect change points in time-series columns.

        Analyzes numeric columns in the DataFrame as time series and identifies
        change points where statistical properties change abruptly. Works with
        both Pandas and Polars DataFrames.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. The backend is automatically detected.

        Returns:
            List of GhostFinding objects for columns containing change points.
            Each finding includes:
            - ghost_type: "changepoint"
            - column: Name of the column with change points
            - severity: "warning" if multiple change points, "info" otherwise
            - description: Human-readable description with change point locations
            - row_indices: List of change point indices (locations)
            - metadata: Dictionary with change_point_count, algorithm, penalty,
              and segment_info

        Raises:
            ImportError: If ruptures is not installed. Install with:
                pip install lavendertown[timeseries]

        Note:
            For Polars DataFrames, row_indices represent the row positions
            (0-based) where change points occur. The detector treats each
            numeric column as a separate time series.
        """
        try:
            import ruptures  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "ruptures is required for change point detection. "
                "Install with: pip install lavendertown[timeseries]"
            ) from e

        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect change points using Pandas API.

        Args:
            df: pandas.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing change points.
        """
        import numpy as np

        import ruptures

        findings: list[GhostFinding] = []

        # Get numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_columns:
            return findings

        for column in numeric_columns:
            # Get column data, remove NaN values
            series = df[column].dropna()

            if len(series) < self.min_size * 2:  # Need at least 2 segments
                continue

            # Convert to numpy array
            data = series.values.reshape(-1, 1)  # Ruptures expects 2D array

            try:
                # Create change point detection model
                if self.algorithm == "pelt":
                    model = ruptures.Pelt(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "binseg":
                    model = ruptures.Binseg(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "window":
                    model = ruptures.Window(
                        width=min(40, len(data) // 2),
                        cost=ruptures.costs.CostL2(),
                    )
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "dynp":
                    if self.n_bkps is None:
                        # Estimate number of change points based on penalty
                        # This is a heuristic - in practice, users should specify n_bkps
                        n_bkps = max(1, min(5, len(data) // (self.min_size * 2)))
                    else:
                        n_bkps = self.n_bkps

                    model = ruptures.Dynp(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, n_bkps=n_bkps, min_size=self.min_size
                    )

                # Convert change points to indices (change_points includes 0 and len(data))
                # Remove the endpoints (0 and len(data)) as they're not actual change points
                change_point_indices = [
                    int(cp)
                    for cp in change_points[:-1]  # Exclude last (end of series)
                    if cp > 0 and cp < len(series)
                ]

                if change_point_indices:
                    # Map back to original DataFrame indices
                    original_indices = series.index[change_point_indices].tolist()

                    # Calculate segment statistics
                    segments = []
                    prev_idx = 0
                    for idx in change_point_indices:
                        segment_data = series.iloc[prev_idx:idx]
                        segments.append(
                            {
                                "start": int(prev_idx),
                                "end": int(idx),
                                "mean": float(segment_data.mean()),
                                "std": float(segment_data.std()),
                                "length": len(segment_data),
                            }
                        )
                        prev_idx = idx

                    # Add final segment
                    final_segment = series.iloc[prev_idx:]
                    segments.append(
                        {
                            "start": int(prev_idx),
                            "end": len(series),
                            "mean": float(final_segment.mean()),
                            "std": float(final_segment.std()),
                            "length": len(final_segment),
                        }
                    )

                    # Determine severity
                    if len(change_point_indices) > 3:
                        severity = "warning"
                    else:
                        severity = "info"

                    finding = GhostFinding(
                        ghost_type="changepoint",
                        column=column,
                        severity=severity,
                        description=(
                            f"Detected {len(change_point_indices)} change point(s) "
                            f"in column '{column}' at positions {original_indices[:5]}"
                            + (
                                f" (and {len(original_indices) - 5} more)"
                                if len(original_indices) > 5
                                else ""
                            )
                        ),
                        row_indices=original_indices,
                        metadata={
                            "change_point_count": len(change_point_indices),
                            "algorithm": self.algorithm,
                            "penalty": float(self.penalty),
                            "min_size": self.min_size,
                            "n_bkps": self.n_bkps,
                            "segments": segments,
                            "change_point_positions": original_indices,
                        },
                    )
                    findings.append(finding)

            except Exception:
                # Skip columns that cause errors (e.g., constant values, insufficient data)
                continue

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect change points using Polars API.

        Args:
            df: polars.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing change points.
            row_indices will be 0-based positions (not original indices).
        """
        import numpy as np

        import polars as pl

        import ruptures

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

        if not numeric_columns:
            return findings

        for column in numeric_columns:
            # Get column data, remove null values
            series = df[column].drop_nulls()

            if len(series) < self.min_size * 2:  # Need at least 2 segments
                continue

            # Convert to numpy array
            data = np.array(series).reshape(-1, 1)  # Ruptures expects 2D array

            try:
                # Create change point detection model
                if self.algorithm == "pelt":
                    model = ruptures.Pelt(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "binseg":
                    model = ruptures.Binseg(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "window":
                    model = ruptures.Window(
                        width=min(40, len(data) // 2),
                        cost=ruptures.costs.CostL2(),
                    )
                    change_points = model.fit_predict(
                        data, pen=self.penalty, min_size=self.min_size
                    )
                elif self.algorithm == "dynp":
                    if self.n_bkps is None:
                        n_bkps = max(1, min(5, len(data) // (self.min_size * 2)))
                    else:
                        n_bkps = self.n_bkps

                    model = ruptures.Dynp(cost=ruptures.costs.CostL2())
                    change_points = model.fit_predict(
                        data, n_bkps=n_bkps, min_size=self.min_size
                    )

                # Convert change points to indices (0-based positions)
                change_point_indices = [
                    int(cp) for cp in change_points[:-1] if cp > 0 and cp < len(series)
                ]

                if change_point_indices:
                    # Calculate segment statistics
                    segments = []
                    prev_idx = 0
                    for idx in change_point_indices:
                        segment_data = series[prev_idx:idx]
                        segments.append(
                            {
                                "start": int(prev_idx),
                                "end": int(idx),
                                "mean": float(segment_data.mean()),
                                "std": float(segment_data.std()),
                                "length": len(segment_data),
                            }
                        )
                        prev_idx = idx

                    # Add final segment
                    final_segment = series[prev_idx:]
                    segments.append(
                        {
                            "start": int(prev_idx),
                            "end": len(series),
                            "mean": float(final_segment.mean()),
                            "std": float(final_segment.std()),
                            "length": len(final_segment),
                        }
                    )

                    # Determine severity
                    if len(change_point_indices) > 3:
                        severity = "warning"
                    else:
                        severity = "info"

                    finding = GhostFinding(
                        ghost_type="changepoint",
                        column=column,
                        severity=severity,
                        description=(
                            f"Detected {len(change_point_indices)} change point(s) "
                            f"in column '{column}' at positions {change_point_indices[:5]}"
                            + (
                                f" (and {len(change_point_indices) - 5} more)"
                                if len(change_point_indices) > 5
                                else ""
                            )
                        ),
                        row_indices=change_point_indices,
                        metadata={
                            "change_point_count": len(change_point_indices),
                            "algorithm": self.algorithm,
                            "penalty": float(self.penalty),
                            "min_size": self.min_size,
                            "n_bkps": self.n_bkps,
                            "segments": segments,
                            "change_point_positions": change_point_indices,
                        },
                    )
                    findings.append(finding)

            except Exception:
                # Skip columns that cause errors
                continue

        return findings
