# Quick Start

Get started with LavenderTown in just a few minutes.

## Basic Usage with Streamlit

The simplest way to use LavenderTown is with Streamlit:

```python
import streamlit as st
from lavendertown import Inspector
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Create inspector and render
inspector = Inspector(df)
inspector.render()  # This must be called within a Streamlit app context
```

Save this code in a file (e.g., `app.py`) and run:

```bash
streamlit run app.py
```

This opens a web interface where you can:
- View interactive data quality insights
- Drill down into specific issues
- Export findings as JSON or CSV
- Create and manage custom rules

## Using Polars

LavenderTown works seamlessly with Polars DataFrames:

```python
import streamlit as st
from lavendertown import Inspector
import polars as pl

# Load your data with Polars
df = pl.read_csv("your_data.csv")

# Create inspector and render (works with Polars too!)
inspector = Inspector(df)
inspector.render()
```

## Standalone CSV Upload App

For quick analysis without writing code, use the included Streamlit app:

```bash
streamlit run examples/app.py
```

This opens a web interface where you can:
- Upload CSV files via drag-and-drop or file browser with enhanced UI
- See animated progress indicators during file processing
- Automatic encoding detection (UTF-8, Latin-1, ISO-8859-1, CP1252)
- Preview your data before analysis
- View interactive data quality insights
- Export findings with download buttons

**New in v0.6.0:** The upload experience includes polished animations, automatic encoding detection, and enhanced visual feedback.

## Programmatic Usage

Use LavenderTown in your Python scripts without Streamlit:

```python
from lavendertown import Inspector
import pandas as pd

# Create sample data with quality issues
data = {
    "product_id": [1, 2, 3, 4, 5],
    "price": [10.99, 25.50, None, 45.00, -5.00],
    "quantity": [100, 50, 75, None, 200],
}
df = pd.DataFrame(data)

inspector = Inspector(df)

# Get findings programmatically
findings = inspector.detect()

# Filter by severity
errors = [f for f in findings if f.severity == "error"]
warnings = [f for f in findings if f.severity == "warning"]

print(f"Total findings: {len(findings)}")
print(f"Errors: {len(errors)}, Warnings: {len(warnings)}")

# Access finding details
for finding in findings:
    print(f"{finding.column}: {finding.description}")
```

## Command-Line Interface

LavenderTown includes a powerful CLI for batch processing:

```bash
# Analyze a single CSV file
lavendertown analyze data.csv --output-format json --output-dir results/

# Batch process multiple files
lavendertown analyze-batch data/ --output-dir results/

# Compare datasets for drift detection
lavendertown compare baseline.csv current.csv --output-format json
```

See the [CLI documentation](../user-guide/cli.md) for more details.

## Next Steps

- Read the [User Guide](../user-guide/basic-usage.md) for comprehensive usage documentation
- Explore [Examples](../guides/examples.md) for more code samples
- Check out the [API Reference](../api-reference/inspector.md) for detailed API documentation

