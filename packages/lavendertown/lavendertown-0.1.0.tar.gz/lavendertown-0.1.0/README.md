# LavenderTown

> A Streamlit-first Python package for detecting and visualizing "data ghosts": type inconsistencies, nulls, invalid values, schema drift, and anomalies in tabular datasets.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/lavendertown.svg)](https://pypi.org/project/lavendertown/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LavenderTown helps you quickly identify data quality issues in your datasets through an intuitive, interactive Streamlit interface. Perfect for data scientists, analysts, and engineers who need to understand their data quality before diving into analysis.

## ✨ Features

- 🔍 **Zero-config data quality insights** - Get started with minimal setup
- 📊 **Streamlit-native UI** - No HTML embeds, fully integrated with Streamlit
- 🎯 **Interactive ghost detection** - Drill down into problematic rows
- 🐼 **Pandas & Polars support** - Works with your existing data pipelines
- 📤 **Exportable findings** - Download results as JSON or CSV with one click
- 🔄 **Dataset Comparison** - Detect schema and distribution drift between datasets
- ⚙️ **Custom Rules** - Create and manage custom data quality rules via UI
- 🚀 **High Performance** - Optimized for datasets up to millions of rows

## 📦 Installation

Install LavenderTown using pip:

```bash
pip install lavendertown
```

For Polars support, install with the optional dependency:

```bash
pip install lavendertown[polars]
```

## 🚀 Quick Start

### Basic Usage

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

### Using Polars

LavenderTown works seamlessly with Polars DataFrames:

```python
import streamlit as st
from lavendertown import Inspector
import polars as pl

# Load your data with Polars
df = pl.read_csv("your_data.csv")

# Create inspector and render (works with Polars too!)
inspector = Inspector(df)
inspector.render()  # This must be called within a Streamlit app context
```

### Standalone CSV Upload App

For quick analysis without writing code, use the included Streamlit app:

```bash
streamlit run examples/app.py
```

This opens a web interface where you can:
- Upload CSV files via drag-and-drop or file browser
- Preview your data before analysis
- View interactive data quality insights
- Export findings with download buttons

See the [examples directory](https://github.com/eddiethedean/lavendertown/tree/main/examples) and [examples/README.md](https://github.com/eddiethedean/lavendertown/blob/main/examples/README.md) for more usage examples and detailed instructions.

## 📚 Usage Examples

### Dataset Comparison (Drift Detection)

Compare datasets to detect schema and distribution changes:

```python
from lavendertown import Inspector
import pandas as pd

baseline_df = pd.read_csv("baseline.csv")
current_df = pd.read_csv("current.csv")

inspector = Inspector(current_df)
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="full"  # or "schema_only", "distribution_only"
)

# Drift findings have ghost_type="drift"
for finding in drift_findings:
    if finding.ghost_type == "drift":
        print(f"{finding.column}: {finding.description}")
```

### Custom Data Quality Rules

Create custom rules through the Streamlit UI:

1. Click "Manage Rules" in the sidebar
2. Create rules of different types:
   - **Range rules**: Validate numeric values within min/max bounds
   - **Regex rules**: Pattern matching for string columns
   - **Enum rules**: Allow only specific values in a column
3. Rules execute automatically with each analysis
4. Export/import rules as JSON for reuse across projects

### Programmatic Usage

Use LavenderTown in your Python scripts:

```python
from lavendertown import Inspector, GhostFinding
import pandas as pd

df = pd.read_csv("data.csv")
inspector = Inspector(df)

# Get findings programmatically
findings = inspector.detect()

# Filter by severity
errors = [f for f in findings if f.severity == "error"]
warnings = [f for f in findings if f.severity == "warning"]

# Access finding details
for finding in errors:
    print(f"Column: {finding.column}")
    print(f"Type: {finding.ghost_type}")
    print(f"Description: {finding.description}")
    if finding.row_indices:
        print(f"Affected rows: {len(finding.row_indices)}")
```

## 👻 Ghost Categories

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

## 🏗️ Architecture

LavenderTown is built with a plugin-based architecture:

- **Inspector**: Main orchestrator that coordinates detection and rendering
- **Detectors**: Stateless, UI-agnostic modules for detecting specific ghost types
  - `NullGhostDetector`: Detects excessive null values
  - `TypeGhostDetector`: Identifies type inconsistencies
  - `OutlierGhostDetector`: Finds statistical outliers using IQR method
  - `RuleBasedDetector`: Executes custom user-defined rules
- **UI Components**: Streamlit-native visualization components
- **Export Layer**: JSON and CSV export functionality

## 🛠️ Development

### Installation for Development

```bash
git clone https://github.com/eddiethedean/lavendertown.git
cd lavendertown
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type checking
mypy lavendertown/
```

## 📊 Performance

LavenderTown is optimized for performance:

- **Small datasets (<10k rows)**: Near-instantaneous analysis
- **Medium datasets (10k-100k rows)**: Sub-second analysis
- **Large datasets (100k-1M rows)**: Optimized with caching and vectorized operations

Benchmark results and optimization recommendations are documented in [docs/PERFORMANCE.md](https://github.com/eddiethedean/lavendertown/blob/main/docs/PERFORMANCE.md).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/eddiethedean/lavendertown/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the UI
- Powered by [Pandas](https://pandas.pydata.org/) and [Polars](https://www.pola.rs/) for data processing
- Visualizations created with [Altair](https://altair-viz.github.io/)

## 🔗 Links

- **Homepage**: https://github.com/eddiethedean/lavendertown
- **Repository**: https://github.com/eddiethedean/lavendertown
- **Issues**: https://github.com/eddiethedean/lavendertown/issues

---

**Made with ❤️ for the data quality community**
