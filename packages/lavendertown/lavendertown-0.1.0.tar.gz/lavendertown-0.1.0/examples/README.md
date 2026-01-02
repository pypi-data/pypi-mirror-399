# LavenderTown Examples

This directory contains example scripts demonstrating various ways to use LavenderTown for data quality analysis.

## Quick Start

### CSV Upload App

The simplest way to get started - a complete Streamlit app for uploading and analyzing CSV files:

```bash
streamlit run examples/app.py
```

This app allows you to:
- Upload CSV files via drag-and-drop
- Preview your data
- Analyze data quality interactively
- Export findings as JSON or CSV

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
python examples/programmatic_usage.py
```

**What it shows:**
- Getting findings programmatically
- Filtering findings by type and severity
- Processing findings in your own code
- Working without Streamlit

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

df = pd.read_csv("data.csv")
inspector = Inspector(df)
findings = inspector.detect()

# Process findings programmatically
errors = [f for f in findings if f.severity == "error"]
if errors:
    print(f"Found {len(errors)} error-level issues")
    # Take action...
```

### Pattern 3: Drift Monitoring

For detecting changes between dataset versions:

```python
from lavendertown import Inspector
import pandas as pd

baseline = pd.read_csv("baseline.csv")
current = pd.read_csv("current.csv")

inspector = Inspector(current)
drift_findings = inspector.compare_with_baseline(baseline)

for finding in drift_findings:
    if finding.ghost_type == "drift":
        print(f"Drift detected: {finding.description}")
```

### Pattern 4: Performance-Critical Workflows

For large datasets where performance matters:

```python
from lavendertown import Inspector
import polars as pl

df = pl.read_csv("large_data.csv")  # Use Polars
inspector = Inspector(df)
inspector.render()  # Faster analysis with Polars
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
