# LavenderTown Examples

This directory contains example scripts demonstrating various ways to use LavenderTown for data quality analysis.

## Quick Start

### CSV Upload App

The simplest way to get started - a complete Streamlit app for uploading and analyzing CSV files:

```bash
streamlit run examples/app.py
```

This app allows you to:
- Upload CSV files via drag-and-drop with enhanced UI
- See animated progress indicators during file processing
- Automatic encoding detection (UTF-8, Latin-1, ISO-8859-1, CP1252)
- Preview your data
- Analyze data quality interactively
- Export findings as JSON or CSV

**New in v0.6.0:** The upload component includes polished animations, automatic encoding detection, and enhanced visual feedback.

## Example Scripts

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the simplest way to use LavenderTown with a Pandas DataFrame.

**Run it:**
```bash
streamlit run examples/basic_usage.py
```

**What it shows:**
- Creating an Inspector with sample data
- Detecting various data quality issues
- Using the Streamlit UI to visualize findings

**Key features:**
- Minimal code required
- Sample data with common quality issues
- Interactive visualization

### 2. Programmatic Usage (`programmatic_usage.py`)

Shows how to use LavenderTown programmatically without the Streamlit UI, perfect for scripts and automated workflows.

**Run it:**
```bash
# Make sure you're in the project root
PYTHONPATH=. python examples/programmatic_usage.py
```

**What it shows:**
- Getting findings programmatically
- Filtering findings by type and severity
- Processing findings in your own code
- Working without Streamlit

**Example Output:**
```
============================================================
Data Quality Analysis Results
============================================================

Total findings: 2

By severity:
  INFO: 2

============================================================
Detailed Findings
============================================================

INFO Issues:
------------------------------------------------------------

Column: price
Type: null
Description: Column 'price' has 1 null values (12.5% of 8 rows)
Affected rows: [2]
Count: 1
Metadata: {'null_count': 1, 'total_count': 8, 'null_percentage': 0.125, 'threshold': 0.1}

Column: quantity
Type: null
Description: Column 'quantity' has 1 null values (12.5% of 8 rows)
Affected rows: [3]
Count: 1
Metadata: {'null_count': 1, 'total_count': 8, 'null_percentage': 0.125, 'threshold': 0.1}
```

**Key features:**
- No Streamlit dependency for this use case
- Direct access to findings data
- Easy integration into existing workflows

### 3. Drift Detection (`drift_detection.py`)

Demonstrates dataset comparison and drift detection capabilities.

**Run it:**
```bash
streamlit run examples/drift_detection.py
```

**What it shows:**
- Comparing two datasets
- Detecting schema changes (new/removed columns, type changes)
- Detecting distribution changes (null percentages, value ranges)
- Visualizing drift findings

**Key features:**
- Side-by-side dataset comparison
- Schema drift detection
- Distribution drift detection
- Detailed drift analysis

### 4. Polars Example (`polars_example.py`)

Shows how to use LavenderTown with Polars DataFrames for better performance.

**Run it:**
```bash
streamlit run examples/polars_example.py
```

**Prerequisites:**
```bash
pip install lavendertown[polars]
```

**What it shows:**
- Creating a Polars DataFrame
- Automatic backend detection
- Performance benefits of Polars
- Working with larger datasets

**Key features:**
- Polars DataFrame support
- Automatic backend detection
- Performance optimization tips

### 5. Time-Series Anomaly Detection (`timeseries_example.py`)

Demonstrates detecting anomalies in time-series data using statistical methods.

**Run it:**
```bash
streamlit run examples/timeseries_example.py
```

**Prerequisites:**
```bash
pip install lavendertown[timeseries]  # For seasonal decomposition
```

**What it shows:**
- Z-score anomaly detection
- Moving average deviation detection
- Seasonal decomposition (requires statsmodels)
- Configurable sensitivity and window size

**Key features:**
- Multiple detection methods
- Automatic datetime column detection
- Interactive parameter tuning
- Time-series visualization

### 6. ML-Assisted Anomaly Detection (`ml_anomaly_example.py`)

Shows how to use machine learning algorithms to detect complex anomalies.

**Run it:**
```bash
streamlit run examples/ml_anomaly_example.py
```

**Prerequisites:**
```bash
pip install lavendertown[ml]
```

**What it shows:**
- Isolation Forest algorithm
- Local Outlier Factor (LOF)
- One-Class SVM
- Multi-dimensional anomaly detection

**Key features:**
- Three ML algorithms to choose from
- Configurable contamination rate
- Works with multi-column data
- Automatic feature normalization

### 7. Cross-Column Validation Rules (`cross_column_rules_example.py`)

Demonstrates validating relationships between multiple columns.

**Run it:**
```bash
streamlit run examples/cross_column_rules_example.py
```

**What it shows:**
- Equality checks between columns
- Comparison rules (greater than, less than)
- Arithmetic validation (sum equals)
- Conditional logic (if-then rules)
- Referential integrity checks

**Key features:**
- Six operation types
- Business logic validation
- Data consistency checks
- Integration with RuleSet system

### 8. Collaboration Features (`collaboration_example.py`)

Shows how to use annotations and shareable reports for team collaboration.

**Run it:**
```bash
streamlit run examples/collaboration_example.py
```

**What it shows:**
- Adding annotations to findings
- Tagging and status tracking
- Creating shareable reports
- Importing/exporting reports

**Key features:**
- Team collaboration on findings
- Status tracking (reviewed, fixed, false positive)
- Report sharing and export
- Finding annotations with comments

## Usage Patterns

### Pattern 1: Quick Analysis with UI

For interactive analysis and exploration:

```python
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("data.csv")
inspector = Inspector(df)
inspector.render()  # Opens Streamlit UI
```

### Pattern 2: Automated Quality Checks

For scripts and automated workflows:

```python
from lavendertown import Inspector
import pandas as pd

# Create sample data (or load from CSV)
data = {
    "product_id": [1, 2, 3, 4, 5],
    "price": [10.99, 25.50, None, 45.00, -5.00],
    "quantity": [100, 50, 75, None, 200],
}
df = pd.DataFrame(data)

inspector = Inspector(df)
findings = inspector.detect()

# Process findings programmatically
errors = [f for f in findings if f.severity == "error"]
warnings = [f for f in findings if f.severity == "warning"]

if errors:
    print(f"Found {len(errors)} error-level issues")
    for error in errors:
        print(f"  - {error.column}: {error.description}")
    # Take action...
```

### Pattern 3: Drift Monitoring

For detecting changes between dataset versions:

```python
from lavendertown import Inspector
import pandas as pd

# Create example datasets (or load from CSV)
baseline = pd.DataFrame({
    "id": [1, 2, 3],
    "value": [10, 20, 30],
})
current = pd.DataFrame({
    "id": [1, 2, 3, 4],  # New row
    "value": [10, 20, 30, 40],  # New row
    "new_col": [1, 2, 3, 4],  # New column
})

inspector = Inspector(current)
drift_findings = inspector.compare_with_baseline(baseline)

for finding in drift_findings:
    if finding.ghost_type == "drift":
        print(f"Drift detected: {finding.column} - {finding.description}")
```

### Pattern 4: Performance-Critical Workflows

For large datasets where performance matters:

```python
from lavendertown import Inspector
import polars as pl

# Create example data (or load from CSV)
data = {
    "id": list(range(1, 1001)),
    "value": [i * 1.5 for i in range(1, 1001)],
    "category": [f"cat_{i % 10}" for i in range(1, 1001)],
}
df = pl.DataFrame(data)

inspector = Inspector(df)  # Automatically detects Polars backend
findings = inspector.detect()  # Use programmatically
# Or use: inspector.render()  # In Streamlit context
```

> **Note:** Install Polars support with `pip install lavendertown[polars]`

### Pattern 5: Time-Series Anomaly Detection

For detecting anomalies in temporal data:

```python
from lavendertown import Inspector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
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

inspector = Inspector(df, detectors=[detector])
inspector.render()
```

> **Note:** Install time-series support with `pip install lavendertown[timeseries]`

### Pattern 6: ML-Assisted Anomaly Detection

For detecting complex anomalies using machine learning:

```python
from lavendertown import Inspector
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
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
    contamination=0.1
)

inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()
```

> **Note:** Install ML support with `pip install lavendertown[ml]`

### Pattern 7: Cross-Column Validation

For validating relationships between columns:

```python
from lavendertown import Inspector
from lavendertown.rules.cross_column import CrossColumnRule
from lavendertown.rules.models import RuleSet
import pandas as pd

# Create data
df = pd.DataFrame({
    "quantity": [10, 20, 30],
    "unit_price": [5.0, 10.0, 15.0],
    "subtotal": [50.0, 200.0, 450.0],  # Some don't match
})

# Create cross-column rule
ruleset = RuleSet(name="validation", description="Cross-column checks")
ruleset.add_rule(
    CrossColumnRule(
        name="subtotal_check",
        description="Subtotal must equal quantity * unit_price",
        source_columns=["quantity", "unit_price"],
        operation="sum_equals",
        target_column="subtotal",
    )
)

# Use with Inspector
inspector = Inspector(df)
inspector.render()  # Rules can be added via UI or programmatically
```

### Pattern 8: Collaboration and Reporting

For team collaboration on findings:

```python
from lavendertown import Inspector
from lavendertown.collaboration.api import (
    add_annotation,
    create_shareable_report,
    export_report,
)
import pandas as pd

df = pd.DataFrame({"value": [1, 2, None, 4, 5]})
inspector = Inspector(df)
findings = inspector.detect()

# Add annotation to a finding
if findings:
    annotation = add_annotation(
        findings[0],
        author="Data Team",
        comment="This needs investigation",
        tags=["critical", "needs-review"],
        status="needs-investigation"
    )

# Create shareable report
report = create_shareable_report(
    title="Q4 Data Quality Report",
    author="Data Team",
    findings=findings
)

# Export report
report_path = export_report(report)
print(f"Report saved to: {report_path}")
```

## Customizing Examples

All examples can be customized to work with your own data:

1. **Replace sample data** with your own DataFrame
2. **Modify detection thresholds** by creating custom detectors
3. **Add custom rules** using the rule authoring UI
4. **Export findings** to integrate with your workflow

## Tips

- **Small datasets (<10k rows)**: Use Pandas, simple and familiar
- **Large datasets (>100k rows)**: Use Polars for better performance
- **Automated checks**: Use programmatic API (`inspector.detect()`)
- **Interactive exploration**: Use Streamlit UI (`inspector.render()`)
- **Production monitoring**: Combine drift detection with automated alerts
- **Time-series data**: Use `TimeSeriesAnomalyDetector` for temporal anomaly detection
- **Complex anomalies**: Use `MLAnomalyDetector` for ML-based detection
- **Business logic**: Use `CrossColumnRule` for multi-column validation
- **Team collaboration**: Use annotations and shareable reports for workflow management

## Next Steps

After exploring these examples:

1. Try the examples with your own data
2. Explore the [full documentation](../README.md)
3. Check out the [architecture docs](../docs/)
4. Contribute your own examples!

## Questions?

- Check the [main README](../README.md) for more information
- Open an issue on [GitHub](https://github.com/eddiethedean/lavendertown/issues)
- Review the [design specification](../docs/LavenderTown_Design_Spec.md)
