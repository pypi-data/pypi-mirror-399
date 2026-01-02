# LavenderTown

> A Streamlit-first Python package for detecting and visualizing "data ghosts": type inconsistencies, nulls, invalid values, schema drift, and anomalies in tabular datasets.

LavenderTown helps you quickly identify data quality issues in your datasets through an intuitive, interactive Streamlit interface. Perfect for data scientists, analysts, and engineers who need to understand their data quality before diving into analysis.

## Features

- **Zero-config data quality insights** - Get started with minimal setup
- **Streamlit-native UI** - No HTML embeds, fully integrated with Streamlit
- **Interactive ghost detection** - Drill down into problematic rows
- **Pandas & Polars support** - Works with your existing data pipelines
- **Exportable findings** - Download results as JSON or CSV with one click
- **Dataset Comparison** - Detect schema and distribution drift between datasets
- **Custom Rules** - Create and manage custom data quality rules via UI
- **High Performance** - Optimized for datasets up to millions of rows
- **CLI Tool** - Batch processing and automation from the command line
- **Ecosystem Integration** - Export rules to Pandera and Great Expectations

## Quick Start

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

That's it! Save this code in a file (e.g., `app.py`) and run `streamlit run app.py` to see the interactive data quality dashboard.

## Installation

```bash
pip install lavendertown
```

For optional features:

```bash
# Polars support
pip install lavendertown[polars]

# Ecosystem integrations
pip install lavendertown[pandera]
pip install lavendertown[great_expectations]

# ML and time-series features
pip install lavendertown[ml]
pip install lavendertown[timeseries]

# All optional dependencies
pip install lavendertown[all]
```

## Documentation

- **[Getting Started](getting-started/installation.md)** - Installation and quick start guide
- **[User Guide](user-guide/basic-usage.md)** - Comprehensive usage documentation
- **[API Reference](api-reference/inspector.md)** - Complete API documentation
- **[Examples](guides/examples.md)** - Code examples and tutorials
- **[Design Documentation](design/architecture.md)** - Architecture and design decisions

## Ghost Categories

LavenderTown detects four main categories of data quality issues:

1. **Structural Ghosts** - Mixed dtypes, schema drift, unexpected nullability
2. **Value Ghosts** - Out-of-range values, regex violations, enum violations  
3. **Completeness Ghosts** - Null density thresholds, conditional nulls
4. **Statistical Ghosts** - Outliers (IQR method), distribution shifts

Each finding includes:
- **Ghost type**: Category of the issue
- **Column**: Affected column name
- **Severity**: `info`, `warning`, or `error`
- **Description**: Human-readable explanation
- **Row indices**: Specific rows affected (when applicable)
- **Metadata**: Additional diagnostic information

## Links

- **GitHub Repository**: https://github.com/eddiethedean/lavendertown
- **PyPI Package**: https://pypi.org/project/lavendertown/
- **Issues**: https://github.com/eddiethedean/lavendertown/issues

---

**Made with ❤️ for the data quality community**

