# LavenderTown

> A Streamlit-first Python package for detecting and visualizing "data ghosts": type inconsistencies, nulls, invalid values, schema drift, and anomalies in tabular datasets.

LavenderTown helps you quickly identify data quality issues in your datasets through an intuitive, interactive Streamlit interface. Perfect for data scientists, analysts, and engineers who need to understand their data quality before diving into analysis.

## Features

!!! info "Version Information"
    Features are marked with the PyPI version where they were introduced. See [Version Mapping](VERSION_MAPPING.md) for details.

- **Zero-config data quality insights** - Get started with minimal setup *(v0.1.0)*
- **Streamlit-native UI** - No HTML embeds, fully integrated with Streamlit *(v0.1.0)*
- **Interactive ghost detection** - Drill down into problematic rows *(v0.1.0)*
- **Pandas & Polars support** - Works with your existing data pipelines *(Pandas: v0.1.0, Polars: v0.2.0)*
- **Exportable findings** - Download results as JSON, CSV, or Parquet with one click *(JSON/CSV: v0.1.0, Parquet: v0.5.0)*
- **Dataset Comparison** - Detect schema and distribution drift between datasets with statistical tests *(v0.2.0, Statistical tests: v0.5.0)*
- **Custom Rules** - Create and manage custom data quality rules via UI *(v0.2.0)*
- **Enhanced File Upload** - Drag-and-drop interface with animated progress and automatic encoding detection *(v0.6.0)*
- **Modular UI Components** - Flexible component system for customizing the Inspector interface *(v0.7.0)*
- **Interactive Visualizations** - Plotly backend for interactive charts with zoom, pan, and 3D visualizations *(v0.7.0)*
- **Advanced Time-Series Features** - tsfresh integration for 700+ time-series features and ML-based anomaly detection *(v0.7.0)*
- **Enhanced UI Components** - Streamlit Extras integration for improved metric cards, badges, and layouts *(v0.7.0)*
- **Database Backend** - SQLAlchemy support for scalable collaboration features with SQLite and PostgreSQL *(v0.7.0)*
- **High Performance** - Optimized for datasets up to millions of rows with fast JSON serialization *(orjson: v0.4.0)*
- **Enhanced CLI Tool** - Beautiful, interactive CLI with progress bars and formatted output (Click and Typer) *(Click: v0.2.0, Rich: v0.4.0, Typer: v0.5.0)*
- **Ecosystem Integration** - Export rules to Pandera and Great Expectations *(v0.2.0)*
- **Configuration Management** - Environment-based configuration with `.env` file support *(v0.4.0)*
- **Advanced ML Detection** - 40+ ML anomaly detection algorithms via PyOD integration *(scikit-learn: v0.2.0, PyOD: v0.5.0)*
- **Time-Series Analysis** - Change point detection with Ruptures, comprehensive profiling reports *(Time-series: v0.2.0, Change points: v0.5.0, Profiling: v0.5.0)*
- **Statistical Testing** - Kolmogorov-Smirnov and chi-square tests for drift detection *(v0.5.0)*

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

# Enhanced CLI with Rich formatting
pip install lavendertown[cli]

# ML and time-series features
pip install lavendertown[ml]          # PyOD + scikit-learn for 40+ ML algorithms
pip install lavendertown[timeseries]  # Ruptures + statsmodels + tsfresh for time-series analysis
pip install lavendertown[profiling]   # ydata-profiling for comprehensive reports
pip install lavendertown[parquet]     # PyArrow for Parquet export
pip install lavendertown[stats]       # scipy.stats for statistical tests

# Phase 7 features (v0.7.0)
pip install lavendertown[plotly]      # Plotly for interactive visualizations
pip install lavendertown[ui]          # Streamlit Extras for enhanced UI components
pip install lavendertown[database]    # SQLAlchemy for database backend

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

