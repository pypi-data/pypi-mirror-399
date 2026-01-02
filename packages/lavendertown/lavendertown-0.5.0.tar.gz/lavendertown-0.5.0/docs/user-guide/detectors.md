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

### ChangePointDetector (New in Phase 6)

Detects change points in time-series data using the Ruptures library.

```python
from lavendertown.detectors.changepoint import ChangePointDetector
from lavendertown import Inspector

# PELT algorithm (default)
cp_detector = ChangePointDetector(
    datetime_column="timestamp",
    algorithm="pelt",
    penalty=10.0
)

inspector = Inspector(df, detectors=[cp_detector])
findings = inspector.detect()
```

**Configuration:**
- `datetime_column`: Name of datetime column (None for auto-detect)
- `algorithm`: Change point algorithm ("pelt", "binseg", "dynp", "window")
- `min_size`: Minimum segment length (default: 2)
- `penalty`: Penalty value for number of change points (default: 10.0)
- `jump`: Minimum distance between change points (default: 1)

**Algorithms:**
- `pelt`: Pruned Exact Linear Time (default, fast and efficient)
- `binseg`: Binary segmentation
- `dynp`: Dynamic programming
- `window`: Window-based detection

**Note:** Requires `lavendertown[timeseries]` (`pip install lavendertown[timeseries]`)

### MLAnomalyDetector

Uses machine learning algorithms to detect complex anomalies. Supports both scikit-learn and PyOD algorithms (Phase 6).

```python
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
from lavendertown import Inspector

# Isolation Forest (scikit-learn)
ml_detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1  # Expected 10% anomalies
)

inspector = Inspector(df, detectors=[ml_detector])
findings = inspector.detect()
```

**Configuration:**
- `algorithm`: ML algorithm (see below for available algorithms)
- `contamination`: Expected proportion of anomalies (0.0 to 0.5)
- `random_state`: Random seed for reproducibility

**Scikit-learn Algorithms:**
- `isolation_forest`: Good for general anomaly detection
- `lof`: Local Outlier Factor (density-based)
- `one_class_svm`: Boundary-based detection

**PyOD Algorithms (Phase 6 - requires `lavendertown[ml]`):**
With PyOD installed, you can use 40+ additional algorithms:
- `abod`: Angle-Based Outlier Detection
- `cblof`: Clustering-Based Local Outlier Factor
- `hbos`: Histogram-based Outlier Score
- `knn`: K-Nearest Neighbors
- `mcd`: Minimum Covariance Determinant
- `pca`: Principal Component Analysis
- `iforest`: Isolation Forest (PyOD version)
- `ocsvm`: One-Class SVM (PyOD version)
- And many more! See PyOD documentation for the full list

**Example with PyOD:**
```python
# Use PyOD algorithm
ml_detector = MLAnomalyDetector(
    algorithm="abod",  # PyOD algorithm
    contamination=0.1
)
```

**Note:** Requires `lavendertown[ml]` which includes both scikit-learn and PyOD

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
from lavendertown.detectors.changepoint import ChangePointDetector
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector

detectors = [
    NullGhostDetector(null_threshold=0.15),
    OutlierGhostDetector(multiplier=2.0),
    TimeSeriesAnomalyDetector(method="zscore"),
    ChangePointDetector(algorithm="pelt"),  # Phase 6
    MLAnomalyDetector(algorithm="abod", contamination=0.1)  # Phase 6 PyOD
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

