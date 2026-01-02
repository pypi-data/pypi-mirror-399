"""Data profiling functionality using ydata-profiling.

This module provides functions to generate comprehensive data profiling reports
using the ydata-profiling library (formerly pandas-profiling).
"""

from __future__ import annotations


try:
    import ydata_profiling  # noqa: F401

    _YDATA_PROFILING_AVAILABLE = True
except ImportError:
    _YDATA_PROFILING_AVAILABLE = False
    ydata_profiling = None  # type: ignore[assignment,misc]


def generate_profiling_report(
    df: object,
    output_path: str,
    minimal: bool = False,
    title: str = "Data Profiling Report",
) -> None:
    """Generate a comprehensive data profiling report.

    Creates an HTML profiling report with statistics, distributions, correlations,
    and data quality insights using ydata-profiling.

    Args:
        df: DataFrame to profile. Can be a pandas.DataFrame or polars.DataFrame.
            Polars DataFrames will be converted to Pandas for profiling.
        output_path: Path to output HTML file.
        minimal: If True, generate a minimal report (faster). Default is False.
        title: Title for the profiling report. Default is "Data Profiling Report".

    Raises:
        ImportError: If ydata-profiling is not installed. Install with:
            pip install lavendertown[profiling]
        ValueError: If DataFrame cannot be converted to Pandas

    Example:
        Generate a profiling report::

            import pandas as pd
            df = pd.read_csv("data.csv")
            generate_profiling_report(df, "report.html")
    """
    if not _YDATA_PROFILING_AVAILABLE:
        raise ImportError(
            "ydata-profiling is required for profiling reports. "
            "Install with: pip install lavendertown[profiling]"
        )

    from ydata_profiling import ProfileReport

    # Convert Polars to Pandas if needed
    pandas_df = _to_pandas(df)

    # Create profile report
    profile = ProfileReport(
        pandas_df,
        title=title,
        minimal=minimal,
        progress_bar=False,  # Disable progress bar for cleaner output
    )

    # Generate report
    profile.to_file(output_path)


def generate_profiling_report_html(
    df: object,
    minimal: bool = False,
    title: str = "Data Profiling Report",
) -> str:
    """Generate a profiling report and return as HTML string.

    Creates a profiling report and returns the HTML content as a string.
    Useful for in-memory operations or embedding in other applications.

    Args:
        df: DataFrame to profile. Can be a pandas.DataFrame or polars.DataFrame.
        minimal: If True, generate a minimal report (faster). Default is False.
        title: Title for the profiling report. Default is "Data Profiling Report".

    Returns:
        HTML string containing the profiling report

    Raises:
        ImportError: If ydata-profiling is not installed
        ValueError: If DataFrame cannot be converted to Pandas

    Example:
        Get HTML string::

            html = generate_profiling_report_html(df)
            # Use html string as needed
    """
    if not _YDATA_PROFILING_AVAILABLE:
        raise ImportError(
            "ydata-profiling is required for profiling reports. "
            "Install with: pip install lavendertown[profiling]"
        )

    from ydata_profiling import ProfileReport

    # Convert Polars to Pandas if needed
    pandas_df = _to_pandas(df)

    # Create profile report
    profile = ProfileReport(
        pandas_df,
        title=title,
        minimal=minimal,
        progress_bar=False,
    )

    # Return HTML string
    html_result = profile.to_html()
    return str(html_result)


def _to_pandas(df: object) -> object:
    """Convert DataFrame to pandas if needed.

    Args:
        df: DataFrame (pandas or polars)

    Returns:
        pandas.DataFrame

    Raises:
        ValueError: If DataFrame type cannot be determined
    """
    # Check if already pandas
    if hasattr(df, "to_dict") and hasattr(df, "iloc"):
        return df

    # Try to convert from polars
    if hasattr(df, "to_pandas"):
        return df.to_pandas()

    raise ValueError("Unable to convert DataFrame to pandas format")
