# Installation

LavenderTown is available on PyPI and can be installed using pip.

## Basic Installation

```bash
pip install lavendertown
```

## Optional Dependencies

LavenderTown supports several optional dependencies for extended functionality:

### Polars Support

For better performance with large datasets:

```bash
pip install lavendertown[polars]
```

### Ecosystem Integrations

Export rules to Pandera or Great Expectations:

```bash
pip install lavendertown[pandera]
pip install lavendertown[great_expectations]
```

**Note:** LavenderTown is compatible with both altair 4.x and 5.x. Installing Great Expectations will automatically install altair 4.x (which is compatible with LavenderTown).

### Enhanced CLI

For the best CLI experience with beautiful terminal output:

```bash
pip install lavendertown[cli]
```

This includes:
- **Rich**: Progress bars, formatted tables, and color-coded messages
- **python-dotenv**: Configuration management via `.env` files
- **orjson**: Fast JSON serialization (2-3x faster than standard library)

### ML and Time-Series Features

For machine learning-based anomaly detection and time-series analysis:

```bash
pip install lavendertown[ml]          # PyOD + scikit-learn for 40+ ML anomaly detection algorithms
pip install lavendertown[timeseries]  # Ruptures for change point detection + statsmodels for time-series analysis
```

**Phase 6 Features:**
- **ML (`lavendertown[ml]`)**: Includes PyOD library with 40+ additional ML anomaly detection algorithms (ABOD, CBLOF, HBOS, KNN, MCD, PCA, and more) beyond scikit-learn's Isolation Forest, LOF, and One-Class SVM
- **Time-Series (`lavendertown[timeseries]`)**: Includes Ruptures library for change point detection in time-series data

### Data Profiling

Generate comprehensive HTML profiling reports:

```bash
pip install lavendertown[profiling]   # ydata-profiling for advanced data profiling
```

### Parquet Export

Export findings to efficient Parquet format:

```bash
pip install lavendertown[parquet]     # PyArrow for Parquet export/import
```

### Statistical Tests

Enhanced drift detection with statistical tests:

```bash
pip install lavendertown[stats]       # scipy.stats for Kolmogorov-Smirnov and chi-square tests
```

### All Optional Dependencies

Install everything at once:

```bash
pip install lavendertown[all]
```

This includes:
- Polars support
- Pandera and Great Expectations exports
- Enhanced CLI (Rich, python-dotenv, orjson, Typer)
- ML anomaly detection (PyOD + scikit-learn)
- Time-series analysis (Ruptures + statsmodels)
- Data profiling (ydata-profiling)
- Parquet export (PyArrow)
- Statistical tests (scipy.stats)

## Development Installation

For contributing to LavenderTown:

```bash
git clone https://github.com/eddiethedean/lavendertown.git
cd lavendertown
pip install -e ".[dev]"
```

This installs LavenderTown in editable mode with development dependencies including pytest, mypy, ruff, and black.

## Requirements

- Python 3.10 or higher
- Streamlit 1.28.0 or higher
- Pandas 1.5.0 or higher
- Altair 4.2.1 or higher (compatible with both 4.x and 5.x)

## Verification

After installation, verify that LavenderTown is working correctly:

```python
from lavendertown import Inspector
import pandas as pd

# Create a simple test DataFrame
df = pd.DataFrame({"value": [1, 2, 3, None, 5]})

# Create inspector
inspector = Inspector(df)

# Get findings
findings = inspector.detect()
print(f"Found {len(findings)} data quality issues")
```

If this runs without errors, LavenderTown is installed correctly!

