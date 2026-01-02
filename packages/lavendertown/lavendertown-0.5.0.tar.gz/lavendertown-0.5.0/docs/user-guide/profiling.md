# Data Profiling

LavenderTown integrates with ydata-profiling (formerly pandas-profiling) to generate comprehensive HTML profiling reports for your datasets.

## Overview

Data profiling reports provide:

- **Overview statistics**: Shape, missing values, memory usage
- **Column statistics**: Mean, median, quartiles, correlations
- **Distribution visualizations**: Histograms, box plots, scatter plots
- **Correlation analysis**: Pearson, Spearman, Kendall correlations
- **Sample data**: First and last rows
- **Data quality alerts**: Duplicates, missing values, constant values

## Basic Usage

### In Python

```python
from lavendertown.profiling import generate_profiling_report
import pandas as pd

# Load your data
df = pd.read_csv("data.csv")

# Generate profile report
generate_profiling_report(
    df,
    output_path="profile_report.html",
    title="My Data Profile"
)
```

### Using Inspector

The Inspector class can generate profiling reports:

```python
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("data.csv")
inspector = Inspector(df)

# Generate profile (if ydata-profiling is installed)
# This is available via the Streamlit UI or programmatically
```

### From CLI

Generate profiling reports from the command line:

```bash
lavendertown profile data.csv --output-file report.html
```

**Options:**
- `--output-file PATH`: Output HTML file path
- `--output-dir DIRECTORY`: Output directory (default: current directory)
- `--title TEXT`: Report title (default: "LavenderTown Profiling Report")
- `--minimal`: Generate minimal report for faster processing
- `--backend [pandas|polars]`: DataFrame backend
- `--quiet`: Suppress progress output
- `--verbose`: Verbose output

**Examples:**
```bash
# Generate full report
lavendertown profile data.csv --output-file full_report.html

# Generate minimal report (faster)
lavendertown profile data.csv --output-file minimal_report.html --minimal

# Custom title
lavendertown profile data.csv --output-file report.html --title "Customer Data Profile"
```

## Configuration Options

### Minimal Reports

For faster processing on large datasets:

```python
from lavendertown.profiling import generate_profiling_report

generate_profiling_report(
    df,
    output_path="minimal_report.html",
    minimal=True  # Faster, less detailed
)
```

### Custom Titles

```python
generate_profiling_report(
    df,
    output_path="report.html",
    title="Q4 2024 Sales Data Profile"
)
```

### HTML String

Get the HTML report as a string instead of saving to file:

```python
from lavendertown.profiling import generate_profiling_report_html

html_string = generate_profiling_report_html(
    df,
    title="My Profile"
)

# Use HTML string (e.g., in Streamlit app)
import streamlit as st
st.components.v1.html(html_string, height=600, scrolling=True)
```

## Working with Polars

LavenderTown automatically converts Polars DataFrames to Pandas for profiling:

```python
import polars as pl
from lavendertown.profiling import generate_profiling_report

# Load with Polars
df = pl.read_csv("data.csv")

# Generate profile (automatically converts to Pandas)
generate_profiling_report(df, output_path="profile.html")
```

## Use Cases

### Initial Data Exploration

Generate a comprehensive profile when first exploring a dataset:

```python
from lavendertown.profiling import generate_profiling_report

df = pd.read_csv("new_dataset.csv")
generate_profiling_report(df, output_path="initial_profile.html")
```

### Data Quality Documentation

Include profiling reports in data quality documentation:

```python
# Generate profile for documentation
generate_profiling_report(
    df,
    output_path="docs/data_profile.html",
    title="Production Dataset Profile - Q4 2024"
)
```

### Automated Reporting

Integrate profiling into data pipeline reporting:

```python
import pandas as pd
from lavendertown.profiling import generate_profiling_report
from datetime import datetime

# Daily profile generation
df = load_daily_data()
report_path = f"profiles/daily_profile_{datetime.now().strftime('%Y%m%d')}.html"

generate_profiling_report(df, output_path=report_path)
```

## Integration with Data Quality Analysis

Combine profiling with LavenderTown's data quality detection:

```python
from lavendertown import Inspector
from lavendertown.profiling import generate_profiling_report
import pandas as pd

df = pd.read_csv("data.csv")

# 1. Generate comprehensive profile
generate_profiling_report(df, output_path="profile.html")

# 2. Run data quality analysis
inspector = Inspector(df)
findings = inspector.detect()

# 3. Combine insights
print(f"Profile report: profile.html")
print(f"Data quality findings: {len(findings)} issues detected")
```

## Performance Considerations

- **Full reports**: Can take time for large datasets (>100k rows)
- **Minimal reports**: Faster processing, less detail
- **Memory usage**: Profiling requires loading entire dataset into memory
- **Best for**: Datasets under 1M rows for interactive exploration

For very large datasets, consider:
- Using minimal reports
- Sampling the data before profiling
- Profiling specific column subsets

## Installation

Install the profiling dependency:

```bash
pip install lavendertown[profiling]
```

This installs `ydata-profiling` and its dependencies.

## Next Steps

- Learn about [Basic Usage](basic-usage.md) for data quality analysis
- See [Drift Detection](drift-detection.md) for comparing datasets
- Check [API Reference](../api-reference/) for detailed documentation

