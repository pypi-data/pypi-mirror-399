# Command-Line Interface

LavenderTown includes a powerful CLI with beautiful, interactive output for batch processing and automation. The CLI features progress bars, formatted tables, and color-coded messages for an enhanced user experience.

## Installation

The CLI is installed automatically with LavenderTown:

```bash
pip install lavendertown
```

For the best CLI experience with enhanced formatting, install with the `cli` extra:

```bash
pip install lavendertown[cli]
```

This includes:
- **Rich**: Beautiful terminal output with progress bars, tables, and color-coded messages
- **python-dotenv**: Configuration management via `.env` files
- **orjson**: Fast JSON serialization (2-3x faster than standard library)

Verify installation:

```bash
lavendertown --help
```

## Commands

### Analyze

Analyze a single CSV file:

```bash
lavendertown analyze data.csv
```

**Options:**
- `--rules PATH`: Path to rules JSON file
- `--output-format [json|csv]`: Output format (default: `json`)
- `--output-dir DIRECTORY`: Output directory
- `--output-file PATH`: Specific output file path
- `--backend [pandas|polars]`: DataFrame backend (default: `pandas`)
- `--quiet`: Suppress progress output
- `--verbose`: Verbose output

**Examples:**
```bash
# Analyze with JSON output
lavendertown analyze data.csv --output-format json --output-dir results/

# Analyze with custom rules
lavendertown analyze data.csv --rules my_rules.json --output-format csv

# Analyze with Polars backend
lavendertown analyze data.csv --backend polars --verbose
```

### Analyze Batch

Process multiple files in a directory:

```bash
lavendertown analyze-batch data/ --output-dir results/
```

**Options:**
- Same as `analyze` command
- Processes all CSV files in the specified directory

**Example:**
```bash
# Process all CSVs in data/ directory
lavendertown analyze-batch data/ --output-dir results/ --backend polars
```

### Compare

Compare two datasets for drift detection:

```bash
lavendertown compare baseline.csv current.csv
```

**Options:**
- `--comparison-type [full|schema_only|distribution_only]`: Type of comparison
- `--output-format [json|csv]`: Output format
- `--output-file PATH`: Output file path
- `--backend [pandas|polars]`: DataFrame backend

**Example:**
```bash
# Full comparison
lavendertown compare baseline.csv current.csv --comparison-type full --output-format json

# Schema-only comparison
lavendertown compare baseline.csv current.csv --comparison-type schema_only
```

### Export Rules

Export rules to Pandera or Great Expectations:

```bash
lavendertown export-rules rules.json --format pandera --output-file schema.py
```

**Options:**
- `--format [pandera|great_expectations]`: Export format
- `--output-file PATH`: Output file path

**Examples:**
```bash
# Export to Pandera
lavendertown export-rules rules.json --format pandera --output-file schema.py

# Export to Great Expectations
lavendertown export-rules rules.json --format great_expectations --output-file suite.json
```

### Share

Share a report file:

```bash
lavendertown share report.json
```

### Import Report

Import a shareable report:

```bash
lavendertown import-report report.json
```

## Output Formats

### JSON

Structured JSON output with all finding details. When `orjson` is installed (via `lavendertown[cli]`), JSON serialization is 2-3x faster than the standard library:

```json
{
  "findings": [
    {
      "ghost_type": "null",
      "column": "price",
      "severity": "info",
      "description": "Column 'price' has 1 null values (12.5% of 8 rows)",
      "row_indices": [2],
      "metadata": {
        "null_count": 1,
        "total_count": 8,
        "null_percentage": 0.125
      }
    }
  ]
}
```

### CSV

Tabular CSV output:

```csv
ghost_type,column,severity,description,row_indices
null,price,info,"Column 'price' has 1 null values (12.5% of 8 rows)","[2]"
```

## Automation Examples

### Daily Quality Checks

```bash
#!/bin/bash
# daily_quality_check.sh

DATE=$(date +%Y%m%d)
INPUT_DIR="/data/daily"
OUTPUT_DIR="/reports/quality/$DATE"

lavendertown analyze-batch "$INPUT_DIR" --output-dir "$OUTPUT_DIR" --backend polars
```

### Drift Monitoring

```bash
#!/bin/bash
# monitor_drift.sh

BASELINE="/data/baseline/production.csv"
CURRENT="/data/current/staging.csv"
OUTPUT="/reports/drift/$(date +%Y%m%d).json"

lavendertown compare "$BASELINE" "$CURRENT" --output-file "$OUTPUT" --comparison-type full
```

### CI/CD Integration

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Check

on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install lavendertown
      - run: lavendertown analyze data.csv --output-format json
```

## Enhanced Output

When installed with the `[cli]` extra, the CLI provides enhanced visual output:

- **Progress bars**: Real-time progress indicators for batch processing
- **Formatted tables**: Beautiful tables for displaying findings summaries
- **Color-coded messages**: Green for success, yellow for warnings, red for errors
- **Status indicators**: Clear visual feedback during long-running operations

Example output with Rich formatting:

```
[cyan]Loading data from data.csv...
[green]Analyzing 1000 rows...
[green]Found 5 data quality issues
[green]Results saved to data_findings.json
```

Use `--quiet` to suppress enhanced output if needed for automation scripts.

## Best Practices

1. **Install CLI extras**: Use `pip install lavendertown[cli]` for best experience
2. **Use output directories**: Organize results in dedicated directories
3. **Specify output format**: Choose JSON for structured data, CSV for tabular
4. **Use Polars for large files**: Better performance with `--backend polars`
5. **Automate with scripts**: Create shell scripts for regular checks
6. **Integrate with CI/CD**: Add quality checks to your pipeline
7. **Use --quiet for automation**: Suppress progress output in CI/CD pipelines

## Next Steps

- Learn about [Basic Usage](basic-usage.md) for programmatic usage
- See [API Reference](../api-reference/cli.md) for detailed CLI documentation

