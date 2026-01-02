"""Performance benchmarking for LavenderTown Inspector."""

from __future__ import annotations

import time
from typing import Any

import pandas as pd


def create_test_dataframe(rows: int, columns: int = 10) -> pd.DataFrame:
    """Create a test DataFrame with specified dimensions.

    Args:
        rows: Number of rows
        columns: Number of columns

    Returns:
        Test DataFrame with mixed data types
    """
    import numpy as np

    data: dict[str, Any] = {}
    for i in range(columns):
        if i % 3 == 0:
            # Numeric column with some nulls
            data[f"num_col_{i}"] = np.random.randn(rows)
            # Add some nulls
            null_indices = np.random.choice(rows, size=rows // 20, replace=False)
            data[f"num_col_{i}"][null_indices] = np.nan
        elif i % 3 == 1:
            # String column
            data[f"str_col_{i}"] = [f"value_{j}" for j in range(rows)]
        else:
            # Mixed type column (int)
            data[f"int_col_{i}"] = np.random.randint(0, 100, size=rows)

    return pd.DataFrame(data)


def benchmark_detection(df: pd.DataFrame) -> dict[str, float]:
    """Benchmark detection performance.

    Args:
        df: DataFrame to benchmark

    Returns:
        Dictionary with timing results
    """
    from lavendertown import Inspector

    inspector = Inspector(df)

    # Time detection
    start_time = time.time()
    findings = inspector.detect()
    detection_time = time.time() - start_time

    return {
        "detection_time_seconds": detection_time,
        "num_findings": len(findings),
        "num_rows": len(df),
        "num_columns": len(df.columns),
    }


def run_benchmarks() -> None:
    """Run performance benchmarks for various dataset sizes."""
    sizes = [
        (1_000, "1k"),
        (10_000, "10k"),
        (100_000, "100k"),
        (1_000_000, "1M"),
    ]

    print("LavenderTown Performance Benchmarks")
    print("=" * 60)
    print(
        f"{'Size':<10} {'Rows':<10} {'Columns':<10} {'Time (s)':<12} {'Findings':<10}"
    )
    print("-" * 60)

    results: list[dict[str, Any]] = []

    for rows, label in sizes:
        try:
            print(f"Benchmarking {label} rows...", end=" ", flush=True)
            df = create_test_dataframe(rows, columns=10)

            result = benchmark_detection(df)
            result["label"] = label
            results.append(result)

            print(f"✓ {result['detection_time_seconds']:.3f}s")
            print(
                f"  {label:<10} {result['num_rows']:<10,} {result['num_columns']:<10} "
                f"{result['detection_time_seconds']:<12.3f} {result['num_findings']:<10}"
            )
        except MemoryError:
            print(f"✗ Memory error - skipping {label}")
            break
        except Exception as e:
            print(f"✗ Error: {e}")
            break

    print("-" * 60)
    print("\nSummary:")
    print("Target: <2s for 100k rows (from roadmap success metrics)")
    if results:
        for result in results:
            if result["num_rows"] == 100_000:
                if result["detection_time_seconds"] < 2.0:
                    print(
                        f"✓ 100k rows: {result['detection_time_seconds']:.3f}s (target met!)"
                    )
                else:
                    print(
                        f"✗ 100k rows: {result['detection_time_seconds']:.3f}s (target: <2s)"
                    )


if __name__ == "__main__":
    run_benchmarks()
