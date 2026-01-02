# LavenderTown

> A Streamlit-first Python package for detecting and visualizing "data ghosts": type inconsistencies, nulls, invalid values, schema drift, and anomalies in tabular datasets.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/lavendertown.svg)](https://pypi.org/project/lavendertown/)
[![Documentation](https://readthedocs.org/projects/lavendertown/badge/?version=latest)](https://lavendertown.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LavenderTown helps you quickly identify data quality issues in your datasets through an intuitive, interactive Streamlit interface. Perfect for data scientists, analysts, and engineers who need to understand their data quality before diving into analysis.

## ✨ Key Features

- 🔍 **Zero-config data quality insights** - Get started with minimal setup
- 📊 **Streamlit-native UI** - Fully integrated interactive dashboard
- 🐼 **Pandas & Polars support** - Works with your existing data pipelines
- 🎯 **Interactive detection** - Drill down into problematic rows
- 📤 **Exportable findings** - JSON, CSV, and Parquet formats
- 🔄 **Drift detection** - Compare datasets for schema and distribution changes
- ⚙️ **Custom rules** - Create and manage data quality rules via UI
- 🤖 **ML-powered detection** - 40+ anomaly detection algorithms
- 📈 **Time-series analysis** - Advanced time-series feature extraction
- 🚀 **High performance** - Optimized for datasets up to millions of rows

**New in v0.7.0:** Modular UI components, Plotly interactive visualizations, tsfresh time-series features, Streamlit Extras UI, and SQLAlchemy database backend.

👉 **[View all features →](https://lavendertown.readthedocs.io/en/latest/)**

## 📦 Installation

```bash
pip install lavendertown
```

For optional features (Polars, ML, time-series, Plotly, etc.), see the [Installation Guide](https://lavendertown.readthedocs.io/en/latest/getting-started/installation.html).

## 🚀 Quick Start

```python
import streamlit as st
from lavendertown import Inspector
import pandas as pd

# Load your data
df = pd.read_csv("your_data.csv")

# Create inspector and render
inspector = Inspector(df)
inspector.render()  # Must be called within a Streamlit app context
```

Save this as `app.py` and run `streamlit run app.py` to see the interactive dashboard.

👉 **[Full Quick Start Guide →](https://lavendertown.readthedocs.io/en/latest/getting-started/quick-start.html)**

## 📚 Documentation

- **[Getting Started](https://lavendertown.readthedocs.io/en/latest/getting-started/installation.html)** - Installation and setup
- **[User Guide](https://lavendertown.readthedocs.io/en/latest/user-guide/basic-usage.html)** - Comprehensive usage documentation
- **[API Reference](https://lavendertown.readthedocs.io/en/latest/api-reference/inspector.html)** - Complete API documentation
- **[Examples](https://lavendertown.readthedocs.io/en/latest/guides/examples.html)** - Code examples and tutorials
- **[Version Mapping](https://lavendertown.readthedocs.io/en/latest/VERSION_MAPPING.html)** - Feature version history

## 👻 Ghost Categories

LavenderTown detects four main categories of data quality issues:

1. **Structural Ghosts** - Mixed dtypes, schema drift, unexpected nullability
2. **Value Ghosts** - Out-of-range values, regex violations, enum violations  
3. **Completeness Ghosts** - Null density thresholds, conditional nulls
4. **Statistical Ghosts** - Outliers (IQR method), distribution shifts

👉 **[Learn more about ghost detection →](https://lavendertown.readthedocs.io/en/latest/user-guide/detectors.html)**

## 💡 Usage Examples

### Programmatic Usage

```python
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("data.csv")
inspector = Inspector(df)
findings = inspector.detect()

for finding in findings:
    print(f"{finding.column}: {finding.description}")
```

### CLI Usage

```bash
# Analyze a CSV file
lavendertown analyze data.csv --output-format json

# Compare datasets for drift
lavendertown compare baseline.csv current.csv
```

👉 **[More examples →](https://lavendertown.readthedocs.io/en/latest/guides/examples.html)**

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/eddiethedean/lavendertown.git
cd lavendertown
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code quality
ruff format . && ruff check . && mypy lavendertown
```

👉 **[Development Guide →](https://lavendertown.readthedocs.io/en/latest/)**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/eddiethedean/lavendertown/blob/main/LICENSE) file for details.

## 🔗 Links

- **📖 Documentation**: https://lavendertown.readthedocs.io/en/latest/
- **📦 PyPI Package**: https://pypi.org/project/lavendertown/
- **🐙 GitHub Repository**: https://github.com/eddiethedean/lavendertown
- **🐛 Issues**: https://github.com/eddiethedean/lavendertown/issues

---

**Made with ❤️ for the data quality community**
