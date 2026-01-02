# Time-Series Anomaly Detection

!!! info "Version"
    Time-series anomaly detection was introduced in **v0.2.0**. Change point detection with Ruptures was added in **v0.5.0**. Advanced tsfresh features were added in **v0.7.0**.

!!! info "Version"
    Time-series anomaly detection was introduced in **v0.2.0**. Change point detection with Ruptures was added in **v0.5.0**.

LavenderTown includes specialized detectors for identifying anomalies in time-series data.

## Overview

Time-series anomaly detection helps identify:
- Sudden spikes or drops in values
- Deviations from expected patterns
- Seasonal anomalies
- Trend breaks

## Basic Usage

```python
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
from lavendertown import Inspector
import pandas as pd

# Create time-series data
dates = pd.date_range("2024-01-01", periods=100, freq="D")
values = [100 + i * 0.5 + (i % 7 - 3) * 2 for i in range(100)]
df = pd.DataFrame({"date": dates, "value": values})

# Create time-series detector
detector = TimeSeriesAnomalyDetector(
    datetime_column="date",
    method="zscore",
    sensitivity=3.0
)

# Use with Inspector
inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()
```

## Detection Methods

### Z-Score Method

Detects values that deviate significantly from the mean:

```python
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    method="zscore",
    sensitivity=3.0  # Number of standard deviations
)
```

**Configuration:**
- `sensitivity`: Number of standard deviations (default: 3.0)
- Higher values detect fewer anomalies

### Moving Average Method

Detects values that deviate from a rolling average:

```python
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    method="moving_avg",
    sensitivity=3.0,
    window_size=10  # Rolling window size
)
```

**Configuration:**
- `window_size`: Size of rolling window (default: 10)
- `sensitivity`: Deviation threshold (default: 3.0)

### Seasonal Decomposition

Removes seasonal patterns before detecting anomalies:

```python
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    method="seasonal",
    sensitivity=3.0
)
```

**Note:** Requires `statsmodels` (`pip install lavendertown[timeseries]`)

## Auto-Detection

If you don't specify a datetime column, the detector will attempt to auto-detect it:

```python
detector = TimeSeriesAnomalyDetector(method="zscore")
inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()
```

The detector looks for:
- Columns with datetime type
- Columns named "date", "timestamp", "time", etc.

## Configuration Options

### Sensitivity

Controls how sensitive the detection is:

```python
# More sensitive (detects more anomalies)
detector = TimeSeriesAnomalyDetector(sensitivity=2.0)

# Less sensitive (detects fewer anomalies)
detector = TimeSeriesAnomalyDetector(sensitivity=4.0)
```

### Window Size

For moving average method:

```python
# Smaller window (more responsive to changes)
detector = TimeSeriesAnomalyDetector(method="moving_avg", window_size=5)

# Larger window (smoother, less responsive)
detector = TimeSeriesAnomalyDetector(method="moving_avg", window_size=20)
```

## Working with Findings

Time-series findings include metadata:

```python
findings = inspector.detect()

for finding in findings:
    if finding.ghost_type == "timeseries_anomaly":
        print(f"Column: {finding.column}")
        print(f"Description: {finding.description}")
        print(f"Method: {finding.metadata.get('method')}")
        print(f"Anomaly value: {finding.metadata.get('anomaly_value')}")
        print(f"Expected range: {finding.metadata.get('expected_range')}")
```

## Examples

### Monitoring Sensor Data

```python
import pandas as pd
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
from lavendertown import Inspector

# Load sensor data
df = pd.read_csv("sensor_data.csv", parse_dates=["timestamp"])

# Detect anomalies
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    method="zscore",
    sensitivity=3.0
)

inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()

# Alert on anomalies
for finding in findings:
    if finding.severity == "error":
        print(f"⚠️ Anomaly detected: {finding.description}")
```

### Financial Data Analysis

```python
# Detect unusual price movements
detector = TimeSeriesAnomalyDetector(
    datetime_column="date",
    method="moving_avg",
    window_size=20,  # 20-day moving average
    sensitivity=2.5
)

inspector = Inspector(price_df, detectors=[detector])
findings = inspector.detect()
```

## Best Practices

1. **Choose appropriate method**: Z-score for general use, moving average for trends, seasonal for periodic data
2. **Tune sensitivity**: Start with default (3.0) and adjust based on your data
3. **Handle missing values**: Ensure datetime column has no gaps or handle them appropriately
4. **Consider seasonality**: Use seasonal method for data with periodic patterns
5. **Validate results**: Review detected anomalies to ensure they're meaningful

## Advanced Feature Extraction (v0.7.0)

LavenderTown integrates with tsfresh for advanced time-series feature extraction, enabling ML-based anomaly detection with 700+ extracted features.

### Using tsfresh Features

```python
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

# Enable tsfresh feature extraction
detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    use_tsfresh_features=True  # Enable advanced feature extraction
)

findings = detector.detect(df)
```

### Manual Feature Extraction

```python
from lavendertown.detectors.timeseries_features import extract_tsfresh_features

# Extract 700+ time-series features
features = extract_tsfresh_features(
    df,
    datetime_column="datetime",
    value_column="value",
    feature_selection=True  # Automatically select relevant features
)
```

See the [Time-Series Features API Reference](../api-reference/timeseries_features.md) for detailed documentation.

## Next Steps

- Learn about [ML Anomaly Detection](ml-anomaly-detection.md) for complex patterns
- See [API Reference](../api-reference/detectors/timeseries.md) for detailed documentation
- Explore [Time-Series Features](../api-reference/timeseries_features.md) for advanced feature extraction

