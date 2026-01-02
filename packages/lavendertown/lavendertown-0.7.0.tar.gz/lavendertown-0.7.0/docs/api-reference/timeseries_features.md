# Time-Series Feature Extraction

!!! info "Version"
    This feature was introduced in **v0.7.0**.

LavenderTown integrates with tsfresh for advanced time-series feature extraction, enabling ML-based anomaly detection with 700+ extracted features.

## Installation

```bash
pip install lavendertown[timeseries]
```

This installs `tsfresh>=0.20.0` along with other time-series dependencies.

## Basic Usage

### Extracting Features

```python
from lavendertown.detectors.timeseries_features import extract_tsfresh_features
import pandas as pd

# Create time-series data
dates = pd.date_range("2024-01-01", periods=100, freq="D")
values = [i + (i % 10) * 0.1 for i in range(100)]
df = pd.DataFrame({"datetime": dates, "value": values})

# Extract features
features = extract_tsfresh_features(
    df,
    datetime_column="datetime",
    value_column="value",
    feature_selection=True  # Optional: perform feature selection
)
```

### Feature Importance

```python
from lavendertown.detectors.timeseries_features import get_feature_importance

# Get feature importance scores
importance = get_feature_importance(features, method="variance")

# Methods available: "variance", "mean", "std"
```

## Integration with TimeSeriesAnomalyDetector

The `TimeSeriesAnomalyDetector` can use tsfresh features for enhanced anomaly detection:

```python
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

# Enable tsfresh features
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    use_tsfresh_features=True  # Enable tsfresh feature extraction
)

findings = detector.detect(df)
```

## Feature Selection

tsfresh can extract 700+ features from time-series data. Feature selection helps identify the most relevant features:

```python
features = extract_tsfresh_features(
    df,
    datetime_column="datetime",
    value_column="value",
    feature_selection=True  # Automatically selects relevant features
)
```

## Supported Data Types

- **Pandas DataFrames**: Full support
- **Polars DataFrames**: Automatically converted to Pandas for tsfresh processing

## Performance Considerations

- Feature extraction can be computationally intensive for large datasets
- Consider using `feature_selection=True` to reduce feature count
- For very large datasets, consider sampling before feature extraction

## Error Handling

If tsfresh is not installed, the functions will raise an `ImportError`:

```python
try:
    features = extract_tsfresh_features(df, "datetime", "value")
except ImportError:
    print("tsfresh is required. Install with: pip install lavendertown[timeseries]")
```

