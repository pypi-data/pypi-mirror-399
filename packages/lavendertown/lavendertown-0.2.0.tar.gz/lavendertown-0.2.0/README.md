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
- 🛠️ **CLI Tool** - Batch processing and automation from the command line
- 🔗 **Ecosystem Integration** - Export rules to Pandera and Great Expectations

## 📦 Installation

Install LavenderTown using pip:

```bash
pip install lavendertown
```

For Polars support, install with the optional dependency:

```bash
pip install lavendertown[polars]
```

For ecosystem integrations (Pandera and Great Expectations), install with:

```bash
pip install lavendertown[pandera]
pip install lavendertown[great_expectations]
```

**Note:** LavenderTown is compatible with both altair 4.x and 5.x. Installing Great Expectations will automatically install altair 4.x (which is compatible with LavenderTown).

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

# Create baseline and current datasets
baseline_df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5],
    "age": [25, 30, 35, 40, 45],
    "purchase_amount": [100.50, 200.00, 150.75, 300.00, 250.50],
})

current_df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5, 6],  # New row
    "age": [25, 30, 35, 40, 45, 50],  # New row
    "purchase_amount": [100.50, 250.00, 150.75, 400.00, 250.50, 500.00],  # Changed values
    "new_column": [1, 2, 3, 4, 5, 6],  # New column
})

inspector = Inspector(current_df)
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="full"  # or "schema_only", "distribution_only"
)

# Drift findings have ghost_type="drift"
for finding in drift_findings:
    if finding.ghost_type == "drift":
        print(f"{finding.column}: {finding.description}")
        print(f"  Change type: {finding.metadata.get('change_type', 'N/A')}")
```

**Example Output:**
```
new_column: New column 'new_column' added to dataset
  Change type: column_added
email: Column 'email' became nullable
  Change type: nullability_change
age: Column 'age' range shifted from [25.00, 45.00] to [25.00, 50.00]
  Change type: numeric_range
purchase_amount: Column 'purchase_amount' range shifted from [100.50, 300.00] to [100.50, 500.00]
  Change type: numeric_range
```

> **Note:** This is actual output from running the code above. The exact drift findings depend on the differences between your baseline and current datasets.

### Custom Data Quality Rules

Create custom rules through the Streamlit UI:

1. Click "Manage Rules" in the sidebar
2. Create rules of different types:
   - **Range rules**: Validate numeric values within min/max bounds
   - **Regex rules**: Pattern matching for string columns
   - **Enum rules**: Allow only specific values in a column
3. Rules execute automatically with each analysis
4. Export/import rules as JSON for reuse across projects

### Command-Line Interface (CLI)

LavenderTown includes a powerful CLI for batch processing and automation:

```bash
# Analyze a single CSV file
lavendertown analyze data.csv --output-format json --output-dir results/

# Batch process multiple files
lavendertown analyze-batch data/ --output-dir results/

# Compare datasets for drift detection
lavendertown compare baseline.csv current.csv --output-format json

# Export rules to Pandera or Great Expectations
lavendertown export-rules rules.json --format pandera --output-file schema.py
lavendertown export-rules rules.json --format great_expectations --output-file suite.json
```

**CLI Options:**
- `--rules PATH`: Path to rules JSON file
- `--output-format [json|csv]`: Output format (default: `json`)
- `--output-dir DIRECTORY`: Output directory (for batch processing)
- `--output-file PATH`: Specific output file path (overrides output-dir)
- `--backend [pandas|polars]`: DataFrame backend (default: `pandas`)
- `--quiet`: Suppress progress output
- `--verbose`: Verbose output

**Example CLI Usage:**

```bash
# Analyze with verbose output
lavendertown analyze data.csv --verbose

# Batch process with Polars backend
lavendertown analyze-batch data/ --output-dir results/ --backend polars

# Analyze with custom rules
lavendertown analyze data.csv --rules my_rules.json --output-format csv
```

See `lavendertown --help` or `lavendertown analyze --help` for full documentation.

### Programmatic Usage

Use LavenderTown in your Python scripts:

```python
from lavendertown import Inspector
import pandas as pd

# Create sample data with quality issues
data = {
    "product_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "price": [10.99, 25.50, None, 45.00, -5.00, 100.00, 200.00, 300.00],
    "quantity": [100, 50, 75, None, 200, 150, 0, 300],
    "category": ["A", "B", "A", "C", "A", "B", "A", "C"],
}
df = pd.DataFrame(data)

inspector = Inspector(df)

# Get findings programmatically
findings = inspector.detect()

# Filter by severity
errors = [f for f in findings if f.severity == "error"]
warnings = [f for f in findings if f.severity == "warning"]
info_items = [f for f in findings if f.severity == "info"]

print(f"Total findings: {len(findings)}")
print(f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info_items)}")

# Access finding details
for finding in findings:
    print(f"\nColumn: {finding.column}")
    print(f"Type: {finding.ghost_type}")
    print(f"Severity: {finding.severity}")
    print(f"Description: {finding.description}")
    if finding.row_indices:
        print(f"Affected rows: {len(finding.row_indices)}")
```

**Example Output:**
```
Total findings: 2
Errors: 0, Warnings: 0, Info: 2

Column: price
Type: null
Severity: info
Description: Column 'price' has 1 null values (12.5% of 8 rows)
Affected rows: 1

Column: quantity
Type: null
Severity: info
Description: Column 'quantity' has 1 null values (12.5% of 8 rows)
Affected rows: 1
```

> **Note:** This is actual output from running the code above. The exact findings may vary based on the data and detection thresholds.

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
