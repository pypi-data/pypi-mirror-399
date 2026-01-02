# LavenderTown Performance Guide

## Overview

This document provides performance benchmarks and recommendations for using LavenderTown with datasets of various sizes.

## Performance Targets

From the roadmap success metrics:
- **<2s load for 100k rows**

## Benchmark Results

Run benchmarks using:
```bash
python benchmarks/benchmark_inspector.py
```

### Typical Performance (as of latest benchmarks)

| Dataset Size | Rows | Columns | Detection Time | Status |
|--------------|------|---------|----------------|--------|
| Small        | 1k   | 10      | ~0.1s          | ✓ Fast |
| Medium       | 10k  | 10      | ~0.5s          | ✓ Fast |
| Large        | 100k | 10      | ~2-5s          | ⚠️ Varies |
| Very Large   | 1M   | 10      | ~20-60s        | ⚠️ Slow |

**Note:** Performance varies based on:
- Number of columns
- Data types (numeric vs string)
- Number of nulls and outliers detected
- System resources (CPU, memory)

## Performance Optimizations

### Already Implemented

1. **Streamlit Caching**: Detection results are cached using `st.cache_data`
2. **Progress Indicators**: Visual feedback for long-running operations
3. **Vectorized Operations**: Detectors use vectorized pandas/polars operations
4. **Early Exit**: Some detectors skip columns when conditions aren't met

### Recommendations

1. **For Large Datasets (>100k rows)**:
   - Consider sampling data before analysis
   - Use Polars instead of Pandas for better performance
   - Process in chunks if memory is limited

2. **For Many Columns (>50 columns)**:
   - Select specific columns for analysis
   - Disable detectors that aren't needed
   - Process columns in batches

3. **Memory Optimization**:
   - Use Polars which is more memory-efficient than Pandas
   - Avoid loading entire datasets into memory if possible
   - Consider data types (use appropriate numeric types)

## Polars vs Pandas Performance

Polars generally provides better performance for large datasets:

- **Small datasets (<10k rows)**: Similar performance
- **Medium datasets (10k-100k rows)**: Polars is often 2-3x faster
- **Large datasets (>100k rows)**: Polars can be 5-10x faster

To use Polars:
```python
import polars as pl
df = pl.read_csv("data.csv")
inspector = Inspector(df)  # Automatically detects Polars
```

## Best Practices

1. **Start Small**: Test with a sample before running on full dataset
2. **Use Appropriate Detectors**: Only enable detectors you need
3. **Leverage Caching**: Streamlit caching helps avoid redundant computation
4. **Monitor Resources**: Watch memory usage for very large datasets
5. **Consider Sampling**: For exploratory analysis, sample data first

## Future Optimizations

Potential areas for future performance improvements:

- Parallel detector execution
- Streaming/chunked processing for very large datasets
- More efficient null detection algorithms
- Optimized outlier detection (consider approximate methods)
- Incremental updates for drift detection

