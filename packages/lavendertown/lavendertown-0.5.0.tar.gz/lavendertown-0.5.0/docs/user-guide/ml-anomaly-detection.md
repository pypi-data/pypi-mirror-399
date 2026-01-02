# ML Anomaly Detection

LavenderTown uses machine learning algorithms to detect complex anomalies that may not be obvious with statistical methods.

## Overview

ML-based anomaly detection is useful for:
- Multi-dimensional anomaly patterns
- Complex relationships between features
- Subtle anomalies that statistical methods miss
- High-dimensional data

## Basic Usage

```python
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
from lavendertown import Inspector
import pandas as pd

# Create multi-dimensional data
df = pd.DataFrame({
    "feature1": [1, 2, 3, 4, 5, 50],
    "feature2": [10, 11, 12, 13, 14, 100],
    "feature3": [100, 101, 102, 103, 104, 200],
})

# Create ML detector
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1  # Expected 10% anomalies
)

# Use with Inspector
inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()
```

**Note:** Requires `scikit-learn` (`pip install lavendertown[ml]`)

## Algorithms

### Isolation Forest

Good for general anomaly detection:

```python
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1,
    random_state=42
)
```

**Characteristics:**
- Works well with high-dimensional data
- Fast training and prediction
- Good for general-purpose anomaly detection

### Local Outlier Factor (LOF)

Density-based detection:

```python
detector = MLAnomalyDetector(
    algorithm="lof",
    contamination=0.1
)
```

**Characteristics:**
- Detects anomalies based on local density
- Good for clusters with varying densities
- More computationally expensive than Isolation Forest

### One-Class SVM

Boundary-based detection:

```python
detector = MLAnomalyDetector(
    algorithm="one_class_svm",
    contamination=0.1
)
```

**Characteristics:**
- Learns a boundary around normal data
- Good for well-defined normal regions
- Can be slow on large datasets

## Configuration

### Contamination Rate

Expected proportion of anomalies:

```python
# Expect 5% anomalies
detector = MLAnomalyDetector(contamination=0.05)

# Expect 20% anomalies
detector = MLAnomalyDetector(contamination=0.20)
```

**Note:** Contamination should be between 0.0 and 0.5 (0% to 50%)

### Random State

For reproducibility:

```python
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1,
    random_state=42
)
```

## Working with Findings

ML findings include metadata:

```python
findings = inspector.detect()

for finding in findings:
    if finding.ghost_type == "ml_anomaly":
        print(f"Column: {finding.column}")
        print(f"Description: {finding.description}")
        print(f"Algorithm: {finding.metadata.get('algorithm')}")
        print(f"Anomaly score: {finding.metadata.get('anomaly_score')}")
```

## Large Datasets

For datasets with >100k rows, the detector automatically samples:

```python
# Automatically samples if dataset is large
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.1,
    max_samples=10000  # Optional: limit samples
)
```

## Examples

### Multi-Feature Anomaly Detection

```python
import pandas as pd
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
from lavendertown import Inspector

# Load data with multiple features
df = pd.read_csv("customer_data.csv")

# Detect anomalies across all numeric features
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.05  # Expect 5% anomalies
)

inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()

# Review anomalies
for finding in findings:
    print(f"Anomaly in {finding.column}: {finding.description}")
```

### Fraud Detection

```python
# Detect fraudulent transactions
detector = MLAnomalyDetector(
    algorithm="isolation_forest",
    contamination=0.01,  # Expect 1% fraud
    random_state=42
)

inspector = Inspector(transaction_df, detectors=[detector])
findings = inspector.detect()
```

## Best Practices

1. **Choose appropriate algorithm**: Isolation Forest for general use, LOF for density-based, One-Class SVM for boundary-based
2. **Set realistic contamination**: Base on domain knowledge or historical data
3. **Feature selection**: Use relevant numeric features for best results
4. **Normalize features**: ML algorithms work better with normalized data (done automatically)
5. **Validate results**: Review detected anomalies to ensure they're meaningful
6. **Consider sampling**: For very large datasets, sampling can improve performance

## Limitations

- **Numeric data only**: ML detectors work with numeric columns only
- **Requires scikit-learn**: Must install `lavendertown[ml]`
- **Computational cost**: Can be slower than statistical methods
- **Interpretability**: Less interpretable than statistical methods

## Next Steps

- Learn about [Time-Series Anomaly Detection](time-series.md) for temporal data
- See [API Reference](../api-reference/detectors/ml_anomaly.md) for detailed documentation

