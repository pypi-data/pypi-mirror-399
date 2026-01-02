# Visualization Backends

!!! info "Version"
    This feature was introduced in **v0.7.0**.

LavenderTown supports multiple visualization backends for rendering charts. By default, Altair is used, but Plotly can be enabled for interactive visualizations.

## Backend Selection

The visualization backend can be selected in the charts UI component. Available backends:

- **Altair** (default): Fast, static charts with good performance
- **Plotly**: Interactive charts with zoom, pan, and 3D visualizations

## Using Plotly Backend

### Installation

```bash
pip install lavendertown[plotly]
```

### Features

Plotly backend provides:

- **Interactive time-series charts**: Zoom and pan through time-series data
- **3D outlier visualization**: Multi-dimensional scatter plots for outlier analysis
- **Enhanced bar charts**: Interactive ghost type distribution charts
- **Heatmaps**: Correlation analysis visualizations

### Backend API

```python
from lavendertown.ui.visualizations.base import get_backend

# Get Altair backend (default)
altair_backend = get_backend("altair")

# Get Plotly backend
plotly_backend = get_backend("plotly")

# Check if backend is available
if plotly_backend.is_available():
    # Use Plotly for rendering
    pass
```

## Creating Custom Charts

### Plotly Charts

```python
from lavendertown.ui.visualizations.plotly_charts import (
    create_null_chart,
    create_outlier_chart,
    create_timeseries_chart,
    create_outlier_3d_chart,
)

# Create null value chart
null_fig = create_null_chart(data, column_name)

# Create outlier chart with bounds
outlier_fig = create_outlier_chart(data, column_name, lower_bound, upper_bound)

# Create time-series chart with anomalies
ts_fig = create_timeseries_chart(data, datetime_col, value_col, anomalies)

# Create 3D outlier visualization
outlier_3d_fig = create_outlier_3d_chart(data, ["x", "y", "z"], outliers)
```

## Backend Implementation

### AltairBackend

The default backend using Altair for static charts.

```python
from lavendertown.ui.visualizations.altair_backend import AltairBackend

backend = AltairBackend()
backend.render_chart(st, chart, "bar")
```

### PlotlyBackend

Interactive backend using Plotly.

```python
from lavendertown.ui.visualizations.plotly_backend import PlotlyBackend

backend = PlotlyBackend()
if backend.is_available():
    backend.render_chart(st, figure, "line")
```

## Fallback Behavior

If Plotly is not installed, the system automatically falls back to Altair. The UI will show an error message if a requested backend is not available.

