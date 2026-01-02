# Basic Usage

This guide covers the fundamental usage patterns for LavenderTown.

## Creating an Inspector

The `Inspector` class is the main entry point for LavenderTown. It accepts a DataFrame (Pandas or Polars) and orchestrates data quality detection.

```python
from lavendertown import Inspector
import pandas as pd

# Load your data
df = pd.read_csv("data.csv")

# Create inspector
inspector = Inspector(df)
```

## Rendering the UI

To display the interactive Streamlit UI, call `render()`:

```python
import streamlit as st

inspector = Inspector(df)
inspector.render()  # Must be called within Streamlit app context
```

The UI provides:
- Overview metrics (total findings, severity breakdown)
- Interactive charts and visualizations
- Detailed findings table with filtering
- Export options (JSON, CSV)
- Custom rule management

## Getting Findings Programmatically

You can also get findings without the UI:

```python
inspector = Inspector(df)
findings = inspector.detect()

# Process findings
for finding in findings:
    print(f"{finding.column}: {finding.description}")
```

## Working with Findings

Each finding is a `GhostFinding` object with the following attributes:

- `ghost_type`: Category of issue (e.g., "null", "type", "outlier")
- `column`: Affected column name
- `severity`: Severity level ("info", "warning", or "error")
- `description`: Human-readable description
- `row_indices`: List of affected row indices (when available)
- `metadata`: Additional diagnostic information

### Filtering Findings

```python
findings = inspector.detect()

# Filter by severity
errors = [f for f in findings if f.severity == "error"]
warnings = [f for f in findings if f.severity == "warning"]

# Filter by type
null_findings = [f for f in findings if f.ghost_type == "null"]
outlier_findings = [f for f in findings if f.ghost_type == "outlier"]

# Filter by column
price_findings = [f for f in findings if f.column == "price"]
```

## Custom Detectors

You can provide custom detectors when creating an Inspector:

```python
from lavendertown.detectors.null import NullGhostDetector

# Create custom detector with specific threshold
null_detector = NullGhostDetector(null_threshold=0.2)  # 20% threshold

# Use with Inspector
inspector = Inspector(df, detectors=[null_detector])
```

## Backend Detection

LavenderTown automatically detects whether you're using Pandas or Polars:

```python
import pandas as pd
import polars as pl

# Pandas DataFrame
df_pandas = pd.DataFrame({"value": [1, 2, 3]})
inspector = Inspector(df_pandas)  # Automatically uses Pandas backend

# Polars DataFrame
df_polars = pl.DataFrame({"value": [1, 2, 3]})
inspector = Inspector(df_polars)  # Automatically uses Polars backend
```

## File Upload Component

LavenderTown includes an enhanced file upload component for Streamlit applications with drag-and-drop support, animated progress indicators, and automatic encoding detection.

### Using the Upload Component

```python
import streamlit as st
from lavendertown.ui.upload import render_file_upload
from lavendertown import Inspector

# Upload file with enhanced UI
uploaded_file, df, encoding_used = render_file_upload(st)

if uploaded_file is not None:
    if df is not None:
        st.success(f"File loaded with {encoding_used} encoding")
        
        # Use with Inspector
        inspector = Inspector(df)
        inspector.render()
    else:
        st.error("Could not read the uploaded file")
```

### Features

- **Drag-and-drop interface**: Enhanced styling for intuitive file uploads
- **Animated progress**: Multi-stage progress indicators for visual feedback
- **Automatic encoding detection**: Tries UTF-8, Latin-1, ISO-8859-1, and CP1252
- **File validation**: Clear error messages for invalid files
- **File size warnings**: Alerts for large files (>10MB)

See the [Upload Component API Reference](../api-reference/upload.md) for detailed documentation.

## Configuration

LavenderTown supports configuration through environment variables and `.env` files. Configuration is automatically loaded when the package is imported.

### Environment Variables

Create a `.env` file in your project root or home directory:

```bash
# .env file
LAVENDERTOWN_LOG_LEVEL=INFO
LAVENDERTOWN_OUTPUT_DIR=./results
```

The package searches for `.env` files in:
1. Current directory
2. Parent directories (up to project root)
3. Home directory (as `.lavendertown.env`)

### Using Configuration

```python
from lavendertown.config import get_config, get_config_bool, get_config_int

# Get configuration values
log_level = get_config("LAVENDERTOWN_LOG_LEVEL", "WARNING")
output_dir = get_config("LAVENDERTOWN_OUTPUT_DIR", "./output")

# Get typed values
debug_mode = get_config_bool("LAVENDERTOWN_DEBUG", False)
max_rows = get_config_int("LAVENDERTOWN_MAX_ROWS", 1000000)
```

Configuration is automatically loaded when you import LavenderTown, so no additional setup is required.

## Next Steps

- Learn about [Detectors](detectors.md) for different detection methods
- Explore [Custom Rules](custom-rules.md) for domain-specific validation
- Check out [Drift Detection](drift-detection.md) for dataset comparison

