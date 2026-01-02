# Design Specification

## Overview

LavenderTown is a Streamlit-first Python package for detecting and visualizing "data ghosts": type inconsistencies, nulls, invalid values, schema drift, and anomalies in tabular datasets.

**Install:** `pip install lavendertown`

## Core Goals

- Zero-config data quality insights
- Streamlit-native UI (no HTML embeds)
- Interactive ghost detection and drill-down
- Pandas & Polars first-class support
- Exportable findings (JSON / CSV / rules)

## Supported Data Inputs

- Pandas DataFrame
- Polars DataFrame
- CSV upload via Streamlit
- Parquet (via Pandas/Polars)

## Ghost Categories

### 1. Structural Ghosts

- Mixed dtypes in a column
- Schema drift between datasets
- Unexpected nullability

### 2. Value Ghosts

- Out-of-range values
- Regex violations
- Enum violations
- Negative / impossible values

### 3. Completeness Ghosts

- Null density thresholds
- Conditional nulls
- Missing value correlations

### 4. Statistical Ghosts

- Outliers (IQR, Z-score, MAD)
- Distribution shifts
- Cardinality explosions

### 5. Advanced Ghosts

- Time-series anomalies
- ML-detected anomalies
- Cross-column validation violations

## UI Layout

### Sidebar

- Dataset summary
- Ghost categories with counts
- Filters & thresholds
- Rule management

### Main Panel

- Overview metrics
- Interactive charts (Altair)
- Filtered row preview
- Ghost explanation panel
- Export options

## Core API

```python
from lavendertown import Inspector

inspector = Inspector(df)
inspector.render()
```

## Extensibility

- Plugin-based ghost detectors
- Custom rules via Python or UI
- Cross-column validation rules
- Export to Pandera / Great Expectations
- Collaboration features (annotations, reports)

## Non-Goals

- ETL orchestration
- Full ML validation (delegated)
- Real-time streaming (batch processing focus)

