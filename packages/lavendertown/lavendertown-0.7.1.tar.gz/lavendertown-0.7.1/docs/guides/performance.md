# Performance Guide

This guide provides comprehensive performance optimization strategies for LavenderTown, including benchmarks, profiling techniques, and best practices for different dataset sizes.

## Performance Targets

From the roadmap success metrics:
- **<2s load for 100k rows** (target)
- **Sub-second for <10k rows** (typical)
- **<5s for 1M rows** (optimized)

## Benchmarking

### Running Benchmarks

The repository includes a benchmark script:

```bash
python benchmarks/benchmark_inspector.py
```

This tests detection performance across different dataset sizes (1k, 10k, 100k, 1M rows).

### Typical Performance

| Dataset Size | Rows | Columns | Pandas (s) | Polars (s) | Status |
|--------------|------|---------|------------|------------|--------|
| Small        | 1k   | 10      | ~0.1       | ~0.1       | ✓ Fast |
| Medium       | 10k  | 10      | ~0.5       | ~0.3       | ✓ Fast |
| Large        | 100k | 10      | ~2-5       | ~0.8-2     | ⚠️ Varies |
| Very Large   | 1M   | 10      | ~20-60     | ~5-15      | ⚠️ Slow |

**Performance factors:**
- Number of columns (more columns = slower)
- Data types (string operations are slower than numeric)
- Number of findings (more issues detected = more processing)
- System resources (CPU, memory, disk I/O)

## Optimization Strategies

### 1. Choose the Right Backend

**Pandas** - Best for:
- Small to medium datasets (<100k rows)
- Familiar API and ecosystem
- Rich feature set

**Polars** - Best for:
- Large datasets (>100k rows)
- Performance-critical workflows
- Memory efficiency

```python
# For large datasets, use Polars
import polars as pl
from lavendertown import Inspector

df = pl.read_csv("large_file.csv")  # Faster CSV reading
inspector = Inspector(df)  # Automatically detects Polars
findings = inspector.detect()  # 2-5x faster than Pandas
```

**Performance comparison:**

```python
import time
import pandas as pd
import polars as pl
from lavendertown import Inspector

# Large dataset
data = {"value": range(1, 1_000_001)}

# Pandas
df_pd = pd.DataFrame(data)
start = time.time()
inspector = Inspector(df_pd)
findings_pd = inspector.detect()
pandas_time = time.time() - start

# Polars
df_pl = pl.DataFrame(data)
start = time.time()
inspector = Inspector(df_pl)
findings_pl = inspector.detect()
polars_time = time.time() - start

print(f"Pandas: {pandas_time:.2f}s")
print(f"Polars: {polars_time:.2f}s")
print(f"Speedup: {pandas_time/polars_time:.2f}x")
```

### 2. Leverage Caching

Use Streamlit's caching to avoid redundant computation:

```python
import streamlit as st
from lavendertown import Inspector
import pandas as pd

@st.cache_data
def analyze_data(df: pd.DataFrame):
    """Cache analysis results."""
    inspector = Inspector(df)
    return inspector.detect()

# First run: computes
# Subsequent runs: uses cache
findings = analyze_data(df)
```

**Cache key considerations:**

```python
@st.cache_data(hash_funcs={pd.DataFrame: lambda x: hash(x.to_string())})
def analyze_with_custom_hash(df):
    """Use custom hash function for DataFrame."""
    inspector = Inspector(df)
    return inspector.detect()
```

### 3. Selective Detector Usage

Only enable detectors you need:

```python
from lavendertown import Inspector
from lavendertown.detectors.null import NullGhostDetector
from lavendertown.detectors.type import TypeGhostDetector

# Instead of all detectors, use only what you need
detectors = [
    NullGhostDetector(null_threshold=0.15),
    # Skip OutlierGhostDetector for faster analysis
]

inspector = Inspector(df, detectors=detectors)
findings = inspector.detect()  # Faster than default
```

### 4. Data Sampling for Exploration

For initial exploration, sample your data:

```python
import pandas as pd
from lavendertown import Inspector

# Load full dataset
full_df = pd.read_csv("large_file.csv")

# Sample for quick analysis
sample_df = full_df.sample(n=10_000, random_state=42)

# Quick analysis on sample
inspector = Inspector(sample_df)
findings = inspector.detect()

# If sample looks good, analyze full dataset
if len([f for f in findings if f.severity == "error"]) == 0:
    inspector_full = Inspector(full_df)
    findings_full = inspector_full.detect()
```

### 5. Column Selection

Analyze only relevant columns:

```python
from lavendertown import Inspector

# Select only columns of interest
relevant_columns = ["price", "quantity", "category"]
df_filtered = df[relevant_columns]

inspector = Inspector(df_filtered)
findings = inspector.detect()  # Faster with fewer columns
```

### 6. Chunked Processing

For very large datasets, process in chunks:

```python
import pandas as pd
from lavendertown import Inspector
from typing import List
from lavendertown.models import GhostFinding

def analyze_in_chunks(filepath: str, chunk_size: int = 10000) -> List[GhostFinding]:
    """Analyze large file in chunks."""
    all_findings = []
    
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        inspector = Inspector(chunk)
        findings = inspector.detect()
        all_findings.extend(findings)
    
    # Deduplicate if needed
    return all_findings

findings = analyze_in_chunks("very_large_file.csv")
```

### 7. Memory Optimization

Reduce memory usage:

```python
import pandas as pd

# Use appropriate data types
df["id"] = df["id"].astype("int32")  # Instead of int64
df["category"] = df["category"].astype("category")  # Categorical for strings
df["price"] = df["price"].astype("float32")  # Instead of float64

# Drop unused columns
df = df.drop(columns=["unused_col1", "unused_col2"])

# Use Polars for better memory efficiency
import polars as pl
df = pl.read_csv("file.csv")  # More memory-efficient
```

## Profiling and Measurement

### Using cProfile

Profile your code to identify bottlenecks:

```python
import cProfile
import pstats
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("data.csv")

profiler = cProfile.Profile()
profiler.enable()

inspector = Inspector(df)
findings = inspector.detect()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Time-Specific Operations

Measure specific operations:

```python
import time
from lavendertown import Inspector
from lavendertown.detectors.null import NullGhostDetector

df = pd.read_csv("data.csv")

# Time detection
start = time.time()
inspector = Inspector(df)
findings = inspector.detect()
detection_time = time.time() - start

print(f"Detection took {detection_time:.2f} seconds")
print(f"Found {len(findings)} issues")
```

### Memory Profiling

Monitor memory usage:

```python
import tracemalloc
from lavendertown import Inspector

tracemalloc.start()

inspector = Inspector(df)
findings = inspector.detect()

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

## Detector-Specific Optimization

### Null Detector

Optimize null detection by setting appropriate thresholds:

```python
from lavendertown.detectors.null import NullGhostDetector

# Higher threshold = faster (checks fewer columns)
detector = NullGhostDetector(null_threshold=0.2)  # Only flag >20% nulls
```

### Outlier Detector

Outlier detection can be expensive. Consider:

```python
from lavendertown.detectors.outlier import OutlierGhostDetector

# Use higher multiplier for fewer outliers detected
detector = OutlierGhostDetector(multiplier=2.5)  # Less sensitive = faster

# Or skip for very large datasets
# detectors = [NullGhostDetector(), TypeGhostDetector()]  # Skip outliers
```

### Time-Series Detector

Optimize time-series analysis:

```python
from lavendertown.detectors.timeseries import TimeSeriesAnomalyDetector

# Use simpler method for faster analysis
detector = TimeSeriesAnomalyDetector(
    method="zscore",  # Faster than "seasonal"
    sensitivity=3.5,  # Higher = fewer checks
    window_size=5  # Smaller window = faster
)
```

### ML Anomaly Detector

Optimize ML detection:

```python
from lavendertown.detectors.ml_anomaly import MLAnomalyDetector

# Use faster algorithm
detector = MLAnomalyDetector(
    algorithm="isolation_forest",  # Faster than "lof" or "one_class_svm"
    contamination=0.1,
    max_samples=5000  # Limit samples for large datasets
)
```

## Best Practices by Dataset Size

### Small Datasets (<10k rows)

- Use default Pandas backend
- Enable all detectors
- No special optimization needed
- Typical time: <1 second

```python
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("small_data.csv")
inspector = Inspector(df)  # Default is fine
inspector.render()
```

### Medium Datasets (10k-100k rows)

- Pandas or Polars (Polars recommended for >50k)
- Use caching if in Streamlit
- Consider disabling expensive detectors if not needed
- Typical time: 0.5-3 seconds

```python
from lavendertown import Inspector
import polars as pl  # Better for medium datasets

df = pl.read_csv("medium_data.csv")
inspector = Inspector(df)
findings = inspector.detect()
```

### Large Datasets (100k-1M rows)

- Use Polars backend
- Sample for initial exploration
- Selective detector usage
- Implement caching
- Consider chunked processing
- Typical time: 2-15 seconds

```python
from lavendertown import Inspector
import polars as pl

# Sample first
df_full = pl.read_csv("large_data.csv")
df_sample = df_full.sample(10000)

# Quick check on sample
inspector = Inspector(df_sample)
sample_findings = inspector.detect()

# If needed, analyze full dataset
# if needs_full_analysis:
#     inspector_full = Inspector(df_full)
#     findings = inspector_full.detect()
```

### Very Large Datasets (>1M rows)

- Always use Polars
- Sample for exploration
- Process in chunks if needed
- Use specific detectors only
- Consider approximate methods
- Typical time: 10-60+ seconds

```python
from lavendertown import Inspector
from lavendertown.detectors.null import NullGhostDetector
import polars as pl

# Sample for exploration
df = pl.read_csv("very_large.csv")
df_sample = df.sample(50000)

# Use only essential detectors
detectors = [NullGhostDetector(null_threshold=0.1)]
inspector = Inspector(df_sample, detectors=detectors)
findings = inspector.detect()
```

## Performance Monitoring

### Track Performance Metrics

```python
import time
from lavendertown import Inspector
import pandas as pd

def analyze_with_metrics(df: pd.DataFrame):
    """Analyze with performance tracking."""
    metrics = {}
    
    # Time detection
    start = time.time()
    inspector = Inspector(df)
    findings = inspector.detect()
    metrics["detection_time"] = time.time() - start
    
    # Count findings
    metrics["total_findings"] = len(findings)
    metrics["errors"] = len([f for f in findings if f.severity == "error"])
    metrics["warnings"] = len([f for f in findings if f.severity == "warning"])
    
    # Dataset info
    metrics["rows"] = len(df)
    metrics["columns"] = len(df.columns)
    
    return findings, metrics

df = pd.read_csv("data.csv")
findings, metrics = analyze_with_metrics(df)

print(f"Analyzed {metrics['rows']:,} rows in {metrics['detection_time']:.2f}s")
print(f"Found {metrics['total_findings']} issues")
```

## Troubleshooting Performance Issues

### Slow Detection

1. **Check dataset size**: Use sampling for very large datasets
2. **Check detectors**: Disable expensive detectors if not needed
3. **Use Polars**: Switch to Polars for large datasets
4. **Profile code**: Identify bottlenecks with cProfile

### Memory Issues

1. **Use Polars**: More memory-efficient than Pandas
2. **Process in chunks**: Don't load entire dataset at once
3. **Optimize data types**: Use appropriate dtypes (int32 vs int64)
4. **Drop unused columns**: Remove columns you don't need

### High CPU Usage

1. **Sample data**: Analyze sample instead of full dataset
2. **Reduce detectors**: Use only necessary detectors
3. **Increase thresholds**: Higher thresholds = less computation
4. **Use faster algorithms**: Choose faster ML/time-series methods

## Future Optimizations

Potential areas for performance improvements:

- **Parallel detector execution**: Run detectors in parallel
- **Incremental analysis**: Update findings incrementally
- **Streaming processing**: Process data in streams
- **Approximate methods**: Faster approximate algorithms
- **GPU acceleration**: Use GPU for certain operations
- **Compiled detectors**: Use Numba or Cython for hot paths

## Summary

1. **Small datasets**: Use defaults, no optimization needed
2. **Medium datasets**: Consider Polars, use caching
3. **Large datasets**: Use Polars, sample first, selective detectors
4. **Very large datasets**: Polars + sampling + chunking + selective detectors

Remember: **Measure first, optimize second**. Profile your specific use case to identify actual bottlenecks before optimizing.
