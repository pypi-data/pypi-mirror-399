# Detectors

LavenderTown includes several built-in detectors for identifying different types of data quality issues.

## Built-in Detectors

### NullGhostDetector

Detects columns with excessive null values.

```python
from lavendertown.detectors.null import NullGhostDetector
from lavendertown import Inspector

# Create detector with custom threshold
null_detector = NullGhostDetector(null_threshold=0.15)  # 15% threshold

inspector = Inspector(df, detectors=[null_detector])
findings = inspector.detect()
```

**Configuration:**
- `null_threshold`: Threshold for null percentage (default: 0.1 = 10%)

**Severity Levels:**
- `error`: >50% nulls
- `warning`: 20-50% nulls
- `info`: 10-20% nulls (or custom threshold)

### TypeGhostDetector

Identifies type inconsistencies within columns.

```python
from lavendertown.detectors.type import TypeGhostDetector
from lavendertown import Inspector

type_detector = TypeGhostDetector()
inspector = Inspector(df, detectors=[type_detector])
findings = inspector.detect()
```

Detects:
- Mixed numeric types (int/float)
- Mixed string/numeric values
- Type inconsistencies across rows

### OutlierGhostDetector

Finds statistical outliers using the Interquartile Range (IQR) method.

```python
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown import Inspector

outlier_detector = OutlierGhostDetector(multiplier=2.0)  # Custom multiplier
inspector = Inspector(df, detectors=[outlier_detector])
findings = inspector.detect()
```

**Configuration:**
- `multiplier`: IQR multiplier for outlier detection (default: 1.5)

### TimeSeriesAnomalyDetector

Detects anomalies in time-series data.

```python
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
from lavendertown import Inspector

# Z-score method
ts_detector = TimeSeriesAnomalyDetector(
    datetime_column="timestamp",
    method="zscore",
    sensitivity=3.0
)

inspector = Inspector(df, detectors=[ts_detector])
findings = inspector.detect()
```

**Configuration:**
- `datetime_column`: Name of datetime column (None for auto-detect)
- `method`: Detection method ("zscore", "moving_avg", "seasonal")
- `sensitivity`: Sensitivity threshold (default: 3.0)
- `window_size`: Window size for moving average (default: 10)

**Methods:**
- `zscore`: Detects values deviating from mean
- `moving_avg`: Detects deviations from rolling average
- `seasonal`: Removes seasonal patterns before detection (requires statsmodels)

### MLAnomalyDetector

Uses machine learning algorithms to detect complex anomalies.

```python
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
from lavendertown import Inspector

# Isolation Forest
ml_detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1  # Expected 10% anomalies
)

inspector = Inspector(df, detectors=[ml_detector])
findings = inspector.detect()
```

**Configuration:**
- `algorithm`: ML algorithm ("isolation_forest", "lof", "one_class_svm")
- `contamination`: Expected proportion of anomalies (0.0 to 0.5)
- `random_state`: Random seed for reproducibility

**Algorithms:**
- `isolation_forest`: Good for general anomaly detection
- `lof`: Local Outlier Factor (density-based)
- `one_class_svm`: Boundary-based detection

**Note:** Requires `scikit-learn` (`pip install lavendertown[ml]`)

## Default Detectors

If you don't specify detectors, Inspector uses the default set:

```python
inspector = Inspector(df)  # Uses NullGhostDetector, TypeGhostDetector, OutlierGhostDetector
```

## Combining Detectors

You can use multiple detectors together:

```python
from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.outlier import OutlierGhostDetector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

detectors = [
    NullGhostDetector(null_threshold=0.15),
    OutlierGhostDetector(multiplier=2.0),
    TimeSeriesAnomalyDetector(method="zscore")
]

inspector = Inspector(df, detectors=detectors)
findings = inspector.detect()
```

## Creating Custom Detectors

You can create custom detectors by extending `GhostDetector`:

```python
from lavendertown.detectors.base import GhostDetector
from lavendertown.models import GhostFinding

class CustomDetector(GhostDetector):
    def detect(self, df):
        findings = []
        # Your detection logic here
        return findings
    
    def get_name(self):
        return "Custom Detector"
```

See the [API Reference](../api-reference/detectors/base.md) for more details.

