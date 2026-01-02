# Examples and Common Patterns

This guide demonstrates common usage patterns and real-world examples for LavenderTown. Each pattern includes complete, runnable code examples you can adapt for your use case.

## Quick Start Pattern

The simplest way to get started with LavenderTown:

```python
import streamlit as st
from lavendertown import Inspector
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Create inspector and render
inspector = Inspector(df)
inspector.render()  # Must be called within Streamlit app context
```

Save this as `app.py` and run `streamlit run app.py` to see the interactive dashboard.

## v0.7.0 Features

### Pattern: Custom UI Layout

Create a minimal or custom UI layout:

```python
import streamlit as st
from lavendertown import Inspector
from lavendertown.ui.layout import ComponentLayout, create_default_layout
from lavendertown.ui.base import ComponentWrapper
from lavendertown.ui.overview import render_overview
from lavendertown.ui.charts import render_charts
import pandas as pd

st.set_page_config(page_title="Custom Layout Demo", layout="wide")

df = pd.DataFrame({
    "col1": [1, 2, 3, None, 5],
    "col2": ["A", "B", "A", "C", "B"],
})

# Create minimal layout (no sidebar, no export)
layout = create_default_layout()
layout.disable_component("sidebar")
layout.disable_component("export_section")
layout.disable_component("rule_management")

inspector = Inspector(df, ui_layout=layout)
inspector.render()
```

### Pattern: Interactive Plotly Visualizations

Use Plotly for interactive charts:

```python
# Install: pip install lavendertown[plotly]
# The UI will show a backend selector when Plotly is available
# Users can switch between Altair and Plotly in the charts section
```

### Pattern: Database Backend for Collaboration

Use SQLAlchemy for scalable storage:

```python
# Install: pip install lavendertown[database]
# Configure via environment variables:
# LAVENDERTOWN_STORAGE_TYPE=database
# LAVENDERTOWN_DATABASE_URL=postgresql://user:pass@localhost/lavendertown

from lavendertown.collaboration.database_storage import DatabaseStorage

storage = DatabaseStorage(database_url="sqlite:///lavendertown.db")
# Use storage.save_report(), storage.load_report(), etc.
```

## Common Usage Patterns

### Pattern 1: Enhanced File Upload with Automatic Encoding Detection

Use the enhanced file upload component for a polished user experience:

```python
import streamlit as st
from lavendertown import Inspector
from lavendertown.ui.upload import render_file_upload

st.title("Data Quality Inspector")

# Upload file with enhanced UI
uploaded_file, df, encoding_used = render_file_upload(
    st,
    accepted_types=[".csv"],
    help_text="Upload a CSV file to analyze for data quality issues",
    show_file_info=True
)

if uploaded_file is not None:
    if df is None:
        st.error("Could not read the CSV file. Please check the file format.")
        st.stop()
    
    # Show success message
    st.success(f"✅ File loaded successfully (encoding: {encoding_used})")
    
    # Display dataset preview
    st.header("Dataset Preview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Run inspection
    inspector = Inspector(df)
    inspector.render()
else:
    st.info("👆 Please upload a CSV file to get started.")
```

**Features:**
- Drag-and-drop interface with enhanced styling
- Animated progress indicators
- Automatic encoding detection (UTF-8, Latin-1, ISO-8859-1, CP1252)
- File size validation and warnings
- Clear error messages

See the [Upload Component API Reference](../api-reference/upload.md) for detailed documentation.

### Pattern 2: Automated Data Quality Checks

For CI/CD pipelines or scheduled jobs:

```python
from lavendertown import Inspector
import pandas as pd
import sys

def check_data_quality(filepath: str, error_threshold: int = 0) -> bool:
    """Check data quality and return True if acceptable."""
    df = pd.read_csv(filepath)
    inspector = Inspector(df)
    findings = inspector.detect()
    
    # Count errors
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    
    print(f"Found {len(errors)} errors and {len(warnings)} warnings")
    
    # Fail if too many errors
    if len(errors) > error_threshold:
        print("❌ Data quality check failed")
        for error in errors:
            print(f"  - {error.column}: {error.description}")
        return False
    
    print("✅ Data quality check passed")
    return True

# Use in your pipeline
if not check_data_quality("data.csv", error_threshold=5):
    sys.exit(1)
```

### Pattern 2: Data Validation Before Processing

Validate data before running expensive operations:

```python
from lavendertown import Inspector
from lavendertown.detectors.null import NullGhostDetector
import pandas as pd

def validate_before_processing(df: pd.DataFrame, max_null_percentage: float = 0.5) -> tuple[bool, list]:
    """Validate data quality before processing."""
    # Use custom null threshold
    null_detector = NullGhostDetector(null_threshold=max_null_percentage)
    inspector = Inspector(df, detectors=[null_detector])
    findings = inspector.detect()
    
    # Check for critical issues
    critical_findings = [
        f for f in findings 
        if f.severity == "error" or 
        (f.ghost_type == "null" and f.metadata.get("null_percentage", 0) > max_null_percentage)
    ]
    
    return len(critical_findings) == 0, critical_findings

# Validate before processing
df = pd.read_csv("large_dataset.csv")
is_valid, issues = validate_before_processing(df, max_null_percentage=0.3)

if not is_valid:
    print(f"Data validation failed with {len(issues)} critical issues")
    # Handle validation failure
else:
    # Proceed with processing
    # process_data(df)  # Your data processing function here
    print("✅ Data validated, proceeding with processing...")
```

### Pattern 3: Dataset Monitoring with Drift Detection

Monitor datasets over time for changes:

```python
from lavendertown import Inspector
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class DatasetMonitor:
    def __init__(self, baseline_path: str):
        self.baseline_path = baseline_path
        self.baseline_df = pd.read_csv(baseline_path)
        
    def check_drift(self, current_df: pd.DataFrame) -> dict:
        """Check for drift between baseline and current dataset."""
        inspector = Inspector(current_df)
        drift_findings = inspector.compare_with_baseline(
            baseline_df=self.baseline_df,
            comparison_type="full"
        )
        
        # Categorize findings
        schema_changes = [f for f in drift_findings if f.metadata.get("drift_type") == "schema"]
        distribution_changes = [f for f in drift_findings if f.metadata.get("drift_type") == "distribution"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_drift_issues": len(drift_findings),
            "schema_changes": len(schema_changes),
            "distribution_changes": len(distribution_changes),
            "findings": [f.to_dict() for f in drift_findings]
        }
    
    def save_report(self, report: dict, output_path: str):
        """Save drift report to JSON."""
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

# Use in monitoring pipeline
monitor = DatasetMonitor("baseline_data.csv")
current_df = pd.read_csv("current_data.csv")
report = monitor.check_drift(current_df)
monitor.save_report(report, f"drift_report_{datetime.now().strftime('%Y%m%d')}.json")

if report["total_drift_issues"] > 0:
    print(f"⚠️ Drift detected: {report['total_drift_issues']} issues found")
```

### Pattern 4: Custom Rule-Based Validation

Create domain-specific validation rules:

```python
from lavendertown import Inspector
from lavendertown.rules.executors import RangeRule, EnumRule
from lavendertown.rules.models import RuleSet
from lavendertown.detectors.rule_based import RuleBasedDetector
import pandas as pd

def create_validation_rules() -> RuleSet:
    """Create a ruleset for e-commerce data validation."""
    ruleset = RuleSet(
        name="ecommerce_validation",
        description="Validation rules for e-commerce transactions"
    )
    
    # Price must be positive
    ruleset.add_rule(RangeRule(
        name="positive_price",
        description="Product price must be positive",
        column="price",
        min_value=0.01,
        max_value=100000.0
    ))
    
    # Quantity must be non-negative integer
    ruleset.add_rule(RangeRule(
        name="valid_quantity",
        description="Quantity must be non-negative",
        column="quantity",
        min_value=0,
        max_value=10000
    ))
    
    # Status must be valid
    ruleset.add_rule(EnumRule(
        name="valid_status",
        description="Order status must be valid",
        column="status",
        allowed_values=["pending", "processing", "shipped", "delivered", "cancelled"]
    ))
    
    return ruleset

# Use rules for validation
df = pd.read_csv("orders.csv")
ruleset = create_validation_rules()
detector = RuleBasedDetector(ruleset)
inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()

# Check for rule violations
rule_violations = [f for f in findings if f.ghost_type == "rule"]
if rule_violations:
    print(f"Found {len(rule_violations)} rule violations")
    for violation in rule_violations:
        print(f"  - {violation.description}")
```

### Pattern 5: Batch Processing Multiple Files

Process multiple data files efficiently:

```python
from lavendertown import Inspector
import pandas as pd
from pathlib import Path
import json

def process_directory(input_dir: str, output_dir: str):
    """Process all CSV files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    csv_files = list(input_path.glob("*.csv"))
    
    for csv_file in csv_files:
        print(f"Processing {csv_file.name}...")
        
        # Load and analyze
        df = pd.read_csv(csv_file)
        inspector = Inspector(df)
        findings = inspector.detect()
        
        # Save results
        output_file = output_path / f"{csv_file.stem}_findings.json"
        findings_data = [f.to_dict() for f in findings]
        
        with open(output_file, "w") as f:
            json.dump({
                "file": csv_file.name,
                "findings_count": len(findings),
                "findings": findings_data
            }, f, indent=2)
        
        print(f"  ✓ Found {len(findings)} issues, saved to {output_file}")

# Process all files
process_directory("data/input", "data/results")
```

### Pattern 6: Time-Series Data Quality Monitoring

Monitor time-series data for anomalies:

```python
from lavendertown import Inspector
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector
import pandas as pd

def monitor_timeseries(df: pd.DataFrame, datetime_column: str = "timestamp"):
    """Monitor time-series data for anomalies."""
    # Create time-series detector
    detector = TimeSeriesAnomalyDetector(
        datetime_column=datetime_column,
        method="zscore",
        sensitivity=3.0
    )
    
    inspector = Inspector(df, detectors=[detector])
    findings = inspector.detect()
    
    # Filter time-series anomalies
    anomalies = [f for f in findings if f.ghost_type == "timeseries_anomaly"]
    
    if anomalies:
        print(f"⚠️ Found {len(anomalies)} time-series anomalies")
        for anomaly in anomalies:
            print(f"  - {anomaly.column}: {anomaly.description}")
            print(f"    Value: {anomaly.metadata.get('anomaly_value')}")
    else:
        print("✅ No anomalies detected")
    
    return anomalies

# Monitor sensor data
df = pd.read_csv("sensor_data.csv", parse_dates=["timestamp"])
anomalies = monitor_timeseries(df, datetime_column="timestamp")
```

### Pattern 7: ML-Based Anomaly Detection for Complex Patterns

Use ML to detect complex anomalies:

```python
from lavendertown import Inspector
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector
import pandas as pd

def detect_ml_anomalies(df: pd.DataFrame, contamination: float = 0.1):
    """Use ML to detect complex anomalies."""
    # Create ML detector
    detector = MLAnomalyDetector(
        algorithm="isolation_forest",
        contamination=contamination,
        random_state=42
    )
    
    inspector = Inspector(df, detectors=[detector])
    findings = inspector.detect()
    
    ml_anomalies = [f for f in findings if f.ghost_type == "ml_anomaly"]
    
    if ml_anomalies:
        print(f"🔍 ML detected {len(ml_anomalies)} anomalies")
        # Sort by anomaly score (if available)
        sorted_anomalies = sorted(
            ml_anomalies,
            key=lambda f: f.metadata.get("anomaly_score", 0),
            reverse=True
        )
        
        for anomaly in sorted_anomalies[:10]:  # Top 10
            print(f"  - {anomaly.column}: score={anomaly.metadata.get('anomaly_score', 'N/A')}")
    
    return ml_anomalies

# Detect anomalies in customer data
df = pd.read_csv("customer_features.csv")
anomalies = detect_ml_anomalies(df, contamination=0.05)  # Expect 5% anomalies
```

### Pattern 8: Cross-Column Business Logic Validation

Validate relationships between columns:

```python
from lavendertown import Inspector
from lavendertown.rules.cross_column import CrossColumnRule
from lavendertown.rules.models import RuleSet
from lavendertown.detectors.rule_based import RuleBasedDetector
import pandas as pd

def create_business_rules() -> RuleSet:
    """Create cross-column business validation rules."""
    ruleset = RuleSet(name="business_validation", description="Business logic validation")
    
    # Subtotal must equal quantity * unit_price
    ruleset.add_rule(CrossColumnRule(
        name="subtotal_validation",
        description="Subtotal must equal quantity * unit_price",
        source_columns=["quantity", "unit_price"],
        operation="sum_equals",
        target_column="subtotal"
    ))
    
    # Total must be <= subtotal (after discount)
    ruleset.add_rule(CrossColumnRule(
        name="total_validation",
        description="Total must be less than or equal to subtotal",
        source_columns=["total", "subtotal"],
        operation="less_than"
    ))
    
    # Completed orders must have payment_date
    ruleset.add_rule(CrossColumnRule(
        name="payment_date_required",
        description="Completed orders must have payment date",
        source_columns=["status", "payment_date"],
        operation="conditional",
        condition={
            "if_column": "status",
            "if_value": "completed",
            "then_column": "payment_date",
            "then_value": "not_null"
        }
    ))
    
    return ruleset

# Validate orders
df = pd.read_csv("orders.csv")
ruleset = create_business_rules()
detector = RuleBasedDetector(ruleset)
inspector = Inspector(df, detectors=[detector])
findings = inspector.detect()

business_violations = [f for f in findings if f.ghost_type == "rule"]
if business_violations:
    print(f"⚠️ Found {len(business_violations)} business rule violations")
```

### Pattern 9: Performance-Optimized Analysis with Polars

Use Polars for better performance on large datasets:

```python
from lavendertown import Inspector
import polars as pl

def analyze_large_dataset(filepath: str):
    """Analyze large dataset using Polars for better performance."""
    # Load with Polars (much faster for large files)
    df = pl.read_csv(filepath)
    
    # Inspector automatically detects Polars backend
    inspector = Inspector(df)
    
    # Get findings programmatically (no UI overhead)
    findings = inspector.detect()
    
    print(f"Analyzed {len(df):,} rows")
    print(f"Found {len(findings)} data quality issues")
    
    # Process findings
    by_severity = {}
    for finding in findings:
        severity = finding.severity
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(finding)
    
    print(f"  Errors: {len(by_severity.get('error', []))}")
    print(f"  Warnings: {len(by_severity.get('warning', []))}")
    print(f"  Info: {len(by_severity.get('info', []))}")
    
    return findings

# Analyze large file
findings = analyze_large_dataset("large_dataset.csv")
```

### Pattern 10: Integration with Existing Workflows

Integrate LavenderTown into existing data pipelines:

```python
from lavendertown import Inspector
import pandas as pd
from typing import Optional

class DataQualityGate:
    """Data quality gate for pipeline integration."""
    
    def __init__(self, max_errors: int = 0, max_warnings: int = 100):
        self.max_errors = max_errors
        self.max_warnings = max_warnings
    
    def validate(self, df: pd.DataFrame) -> tuple[bool, Optional[dict]]:
        """Validate DataFrame and return (is_valid, report)."""
        inspector = Inspector(df)
        findings = inspector.detect()
        
        errors = [f for f in findings if f.severity == "error"]
        warnings = [f for f in findings if f.severity == "warning"]
        
        report = {
            "total_findings": len(findings),
            "errors": len(errors),
            "warnings": len(warnings),
            "error_details": [f.to_dict() for f in errors],
            "warning_details": [f.to_dict() for f in warnings[:10]]  # Top 10
        }
        
        is_valid = (
            len(errors) <= self.max_errors and
            len(warnings) <= self.max_warnings
        )
        
        return is_valid, report

# Use in pipeline
def etl_pipeline(input_file: str, output_file: str):
    """ETL pipeline with quality gate."""
    # Load
    df = pd.read_csv(input_file)
    
    # Quality check
    gate = DataQualityGate(max_errors=5, max_warnings=50)
    is_valid, report = gate.validate(df)
    
    if not is_valid:
        print(f"❌ Quality check failed: {report['errors']} errors, {report['warnings']} warnings")
        # Log report, send alert, etc.
        return False
    
    # Process (replace with your transformation logic)
    # processed_df = transform_data(df)
    processed_df = df  # Placeholder: replace with your transformation
    
    # Save
    processed_df.to_csv(output_file, index=False)
    print("✅ Pipeline completed successfully")
    return True

# Run pipeline
etl_pipeline("input.csv", "output.csv")
```

## Running Example Scripts

The repository includes complete example scripts you can run:

```bash
# Streamlit examples (interactive UI)
streamlit run examples/basic_usage.py
streamlit run examples/drift_detection.py
streamlit run examples/timeseries_example.py
streamlit run examples/ml_anomaly_example.py
streamlit run examples/cross_column_rules_example.py
streamlit run examples/collaboration_example.py

# Python scripts (programmatic usage)
PYTHONPATH=. python examples/programmatic_usage.py
PYTHONPATH=. python examples/polars_example.py
```

## Best Practices

1. **Start with defaults**: Begin with the default Inspector and detectors, then customize as needed
2. **Use appropriate backends**: Pandas for small datasets, Polars for large ones
3. **Cache results**: Use Streamlit's caching for repeated analyses
4. **Set thresholds**: Configure detectors based on your data quality requirements
5. **Automate checks**: Integrate quality checks into your CI/CD pipelines
6. **Monitor over time**: Use drift detection to track data quality trends
7. **Customize rules**: Create domain-specific rules for your use case

## Next Steps

- Explore the [User Guide](../user-guide/basic-usage.md) for detailed feature documentation
- Check the [API Reference](../api-reference/inspector.md) for complete API details
- Review [Performance Guide](../guides/performance.md) for optimization tips
