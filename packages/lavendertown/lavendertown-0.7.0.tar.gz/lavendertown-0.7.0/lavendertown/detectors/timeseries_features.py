"""Time-series feature extraction using tsfresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    from tsfresh import extract_features, select_features
    from tsfresh.utilities.dataframe_functions import impute

    TSFRESH_AVAILABLE = True
except ImportError:
    TSFRESH_AVAILABLE = False
    extract_features = None  # type: ignore[assignment]
    select_features = None  # type: ignore[assignment]
    impute = None  # type: ignore[assignment]

from lavendertown.detectors.base import detect_dataframe_backend


def extract_tsfresh_features(
    df: object,
    datetime_column: str,
    value_column: str,
    kind: str | None = None,
    feature_selection: bool = True,
    **kwargs: object,
) -> object | None:
    """Extract time-series features using tsfresh.

    Extracts 700+ time-series features from the given time-series data.
    Features include statistical, temporal, and frequency domain features.

    Args:
        df: DataFrame with time-series data (Pandas or Polars)
        datetime_column: Name of datetime column
        value_column: Name of value column to extract features from
        kind: Optional kind column name (for multiple time-series)
        feature_selection: Whether to perform feature selection (default: True)
        **kwargs: Additional arguments passed to tsfresh.extract_features

    Returns:
        DataFrame with extracted features, or None if tsfresh not available

    Raises:
        ImportError: If tsfresh is not installed
        ValueError: If required columns are not found
    """
    if not TSFRESH_AVAILABLE:
        raise ImportError(
            "tsfresh is required for time-series feature extraction. "
            "Install with: pip install lavendertown[timeseries]"
        )

    backend = detect_dataframe_backend(df)

    import pandas as pd

    # Convert to pandas for tsfresh (it requires pandas)
    if backend == "pandas":
        ts_df = df[[datetime_column, value_column]].copy()
        ts_df[datetime_column] = pd.to_datetime(ts_df[datetime_column])
    else:
        import polars as pl

        ts_df = (
            df.select([pl.col(datetime_column), pl.col(value_column)])
            .with_columns(pl.col(datetime_column).str.to_datetime())
            .to_pandas()
        )
        ts_df[datetime_column] = pd.to_datetime(ts_df[datetime_column])

    # Sort by datetime
    ts_df = ts_df.sort_values(by=datetime_column).dropna()

    if len(ts_df) == 0:
        return None

    # Prepare data for tsfresh
    # tsfresh expects: id, time, kind (optional), value columns
    import pandas as pd

    tsfresh_df = pd.DataFrame(
        {
            "id": 0,  # Single time-series
            "time": range(len(ts_df)),
            value_column: ts_df[value_column].values,
        }
    )

    if kind is not None:
        tsfresh_df["kind"] = kind

    # Extract features
    extracted_features = extract_features(
        tsfresh_df,
        column_id="id",
        column_sort="time",
        column_value=value_column,
        **kwargs,
    )

    # Impute missing values
    extracted_features = impute(extracted_features)

    # Feature selection if requested
    if feature_selection:
        try:
            # Create a dummy target (tsfresh needs this for feature selection)
            # In practice, this would be anomaly labels
            y = pd.Series([0] * len(extracted_features))
            extracted_features = select_features(extracted_features, y)
        except Exception:
            # If feature selection fails, continue without it
            pass

    return extracted_features


def get_feature_importance(
    features_df: object, method: str = "variance"
) -> dict[str, float]:
    """Get feature importance scores.

    Args:
        features_df: DataFrame with extracted features
        method: Method for importance calculation ("variance", "mean", "std")

    Returns:
        Dictionary mapping feature names to importance scores
    """
    import pandas as pd

    if not isinstance(features_df, pd.DataFrame):
        return {}

    if method == "variance":
        importances = features_df.var().to_dict()
    elif method == "mean":
        importances = features_df.mean().abs().to_dict()
    elif method == "std":
        importances = features_df.std().to_dict()
    else:
        importances = features_df.var().to_dict()

    # Sort by importance
    return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
