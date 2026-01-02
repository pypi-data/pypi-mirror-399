# Drift Detection

!!! info "Version"
    Drift detection was introduced in **v0.2.0**. Statistical tests (Kolmogorov-Smirnov, chi-square) were added in **v0.5.0**.

LavenderTown can compare two datasets to detect schema and distribution changes, helping you monitor data quality over time.

## Overview

Drift detection identifies changes between a baseline dataset and a current dataset:

- **Schema changes**: New/removed columns, type changes, nullability changes
- **Distribution changes**: Value range shifts, null percentage changes, cardinality changes

## Basic Usage

```python
from lavendertown import Inspector
import pandas as pd

# Baseline dataset
baseline_df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5],
    "age": [25, 30, 35, 40, 45],
    "purchase_amount": [100.50, 200.00, 150.75, 300.00, 250.50],
})

# Current dataset
current_df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5, 6],  # New row
    "age": [25, 30, 35, 40, 45, 50],  # New row
    "purchase_amount": [100.50, 250.00, 150.75, 400.00, 250.50, 500.00],  # Changed values
    "new_column": [1, 2, 3, 4, 5, 6],  # New column
})

# Detect drift
inspector = Inspector(current_df)
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="full"  # or "schema_only", "distribution_only"
)
```

## Comparison Types

### Full Comparison

Detects both schema and distribution changes:

```python
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="full"
)
```

### Schema Only

Only detects structural changes:

```python
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="schema_only"
)
```

Detects:
- New columns
- Removed columns
- Type changes
- Nullability changes

### Distribution Only

Only detects value distribution changes:

```python
drift_findings = inspector.compare_with_baseline(
    baseline_df=baseline_df,
    comparison_type="distribution_only"
)
```

Detects:
- Numeric range shifts
- Null percentage changes
- Cardinality changes
- Value distribution shifts

**Statistical Tests (Phase 6):**
When `lavendertown[stats]` is installed, distribution comparison includes:
- **Kolmogorov-Smirnov test** for numeric columns (tests if distributions differ)
- **Chi-square test** for categorical columns (tests independence/contingency)
- Test statistics and p-values are included in finding metadata

## Working with Drift Findings

Drift findings are `GhostFinding` objects with `ghost_type="drift"`:

```python
drift_findings = inspector.compare_with_baseline(baseline_df)

for finding in drift_findings:
    if finding.ghost_type == "drift":
        print(f"Column: {finding.column}")
        print(f"Description: {finding.description}")
        print(f"Change type: {finding.metadata.get('change_type')}")
        print(f"Drift type: {finding.metadata.get('drift_type')}")
```

### Finding Metadata

Drift findings include metadata:

- `change_type`: Specific type of change (e.g., "column_added", "type_change")
- `drift_type`: Category ("schema" or "distribution")
- `baseline_value`: Value in baseline dataset
- `current_value`: Value in current dataset
- `ks_statistic`: Kolmogorov-Smirnov test statistic (numeric columns, Phase 6)
- `p_value`: Statistical test p-value (Phase 6)
- `chi2_statistic`: Chi-square test statistic (categorical columns, Phase 6)

## Example Output

```python
# Column: new_column
# Description: New column 'new_column' added to dataset
# Change type: column_added
# Drift type: schema

# Column: purchase_amount
# Description: Column 'purchase_amount' range shifted from [100.50, 300.00] to [100.50, 500.00]
# Change type: numeric_range
# Drift type: distribution
```

## CLI Usage

Detect drift from the command line:

```bash
lavendertown compare baseline.csv current.csv --output-format json
```

Options:
- `--comparison-type [full|schema_only|distribution_only]`: Type of comparison
- `--output-format [json|csv|parquet]`: Output format (Phase 6: Parquet support)
- `--output-file PATH`: Specific output file

**Note:** Parquet export requires `lavendertown[parquet]` (`pip install lavendertown[parquet]`)

## Use Cases

### Data Pipeline Monitoring

Monitor data quality in ETL pipelines:

```python
# After each pipeline run
current_df = load_current_data()
baseline_df = load_baseline_data()

inspector = Inspector(current_df)
drift_findings = inspector.compare_with_baseline(baseline_df)

# Alert on significant changes
for finding in drift_findings:
    if finding.severity == "error":
        send_alert(f"Critical drift detected: {finding.description}")
```

### Version Comparison

Compare dataset versions:

```python
# Compare production vs staging
production_df = load_production_data()
staging_df = load_staging_data()

inspector = Inspector(staging_df)
drift_findings = inspector.compare_with_baseline(production_df)

# Review changes before deployment
for finding in drift_findings:
    print(f"⚠️ {finding.description}")
```

## Best Practices

1. **Establish baselines**: Use stable, validated datasets as baselines
2. **Monitor regularly**: Run drift detection as part of your data quality checks
3. **Set thresholds**: Define what level of drift requires attention
4. **Document changes**: Keep records of expected vs unexpected changes
5. **Automate alerts**: Set up alerts for critical drift findings

## Next Steps

- Learn about [Basic Usage](basic-usage.md) for general data quality analysis
- See [API Reference](../api-reference/inspector.md) for detailed documentation

