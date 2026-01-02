# Dataset Comparison and Drift Detection - Design Document

## Overview

Dataset comparison allows users to compare two DataFrames and detect changes between them. This is useful for detecting schema drift, data distribution shifts, and other temporal changes in datasets.

## Use Cases

1. **Schema Drift Detection**: Compare schemas between two datasets to detect:
   - New columns
   - Removed columns
   - Column type changes
   - Nullability changes

2. **Distribution Shifts**: Compare data distributions to detect:
   - Statistical distribution changes
   - Value range shifts
   - Cardinality changes
   - Null percentage changes

3. **Data Quality Regression**: Compare quality metrics between datasets:
   - Increase in null percentages
   - New types of data quality issues
   - Changes in outlier patterns

## Proposed API

```python
from lavendertown.drift import compare_datasets

# Compare two datasets
drift_findings = compare_datasets(
    baseline_df=df1,
    current_df=df2,
    comparison_type="full"  # or "schema_only", "distribution_only"
)

# Findings are GhostFinding objects with ghost_type="drift"
for finding in drift_findings:
    print(f"{finding.column}: {finding.description}")
```

## Implementation Phases

### Phase 1: Schema Comparison
- Detect column additions/removals
- Detect column type changes
- Detect nullability changes

### Phase 2: Distribution Comparison
- Compare value distributions
- Detect statistical shifts
- Compare cardinality

### Phase 3: Integration
- UI for dataset comparison
- Visualization of drift
- Export drift findings

## Technical Considerations

- Both DataFrames should support Pandas and Polars
- Efficient comparison algorithms for large datasets
- Configurable thresholds for what constitutes "drift"
- Memory-efficient comparison (streaming/chunked for large datasets)

## Future Enhancements

- Time-series drift detection
- Automated drift monitoring
- Alerting on significant drift
- Drift visualization over time

