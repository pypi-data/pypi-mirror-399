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

### ML and Time-Series Features

For machine learning-based anomaly detection and time-series analysis:

```bash
pip install lavendertown[ml]          # scikit-learn for ML anomaly detection
pip install lavendertown[timeseries]  # statsmodels for time-series analysis
```

### All Optional Dependencies

Install everything at once:

```bash
pip install lavendertown[all]
```

This includes:
- Polars support
- Pandera and Great Expectations exports
- ML anomaly detection (scikit-learn)
- Time-series analysis (statsmodels)

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

