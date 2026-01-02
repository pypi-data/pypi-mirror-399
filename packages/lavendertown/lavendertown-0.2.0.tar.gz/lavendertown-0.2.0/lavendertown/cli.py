"""Command-line interface for LavenderTown.

This module provides a Click-based CLI for running LavenderTown data quality
analysis from the command line. It supports single file analysis, batch
processing, drift detection, and rule export functionality.

The CLI can be accessed via the ``lavendertown`` command after installation,
or by running this module directly with ``python -m lavendertown.cli``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore[assignment]

try:
    import polars as pl
except ImportError:
    pl = None  # type: ignore[assignment]

from lavendertown import Inspector
from lavendertown.export.csv import export_to_csv_file
from lavendertown.export.json import export_to_json_file
from lavendertown.rules.models import RuleSet
from lavendertown.rules.storage import load_ruleset


def _load_dataframe(filepath: str, backend: str = "pandas") -> Any:
    """Load a CSV file into a DataFrame.

    Reads a CSV file and loads it into either a Pandas or Polars DataFrame
    depending on the specified backend.

    Args:
        filepath: Path to the CSV file to load. Must be a valid file path.
        backend: Backend to use for loading. Options: "pandas" or "polars".
            Defaults to "pandas".

    Returns:
        DataFrame object (pandas.DataFrame or polars.DataFrame depending on
        backend).

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        ValueError: If the backend is unsupported or the required library
            (pandas or polars) is not installed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if backend == "pandas":
        if pd is None:
            raise ValueError("pandas is required but not installed")
        return pd.read_csv(filepath)
    elif backend == "polars":
        if pl is None:
            raise ValueError(
                "polars is required but not installed. Install with: pip install lavendertown[polars]"
            )
        return pl.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported backend: {backend}")


def _load_ruleset_from_file(filepath: str | None) -> RuleSet | None:
    """Load a RuleSet from a JSON file.

    Loads a RuleSet configuration from a JSON file using the storage module.
    Returns None if no filepath is provided.

    Args:
        filepath: Path to the rules JSON file, or None if no rules should
            be loaded.

    Returns:
        RuleSet object if filepath is provided and valid, None otherwise.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        ValueError: If the file format is invalid or cannot be parsed as
            a RuleSet.
    """
    if filepath is None:
        return None

    return load_ruleset(filepath)


def _get_output_path(
    input_path: str,
    output_dir: str | None,
    output_file: str | None,
    extension: str,
) -> Path:
    """Determine output file path.

    Determines the output file path based on the input path and optional
    output directory or file specifications. If output_file is provided,
    it takes precedence. Otherwise, the output filename is derived from
    the input filename with the specified extension.

    Args:
        input_path: Path to the input file. Used as a base if output_file
            is not provided.
        output_dir: Optional output directory. If provided, the output file
            will be placed in this directory.
        output_file: Optional explicit output file path. If provided, this
            takes precedence over output_dir and input_path.
        extension: File extension to use (e.g., ".json", ".csv"). Should
            include the leading dot.

    Returns:
        Path object representing the output file path.
    """
    if output_file:
        return Path(output_file)
    elif output_dir:
        input_name = Path(input_path).stem
        return Path(output_dir) / f"{input_name}_findings{extension}"
    else:
        input_path_obj = Path(input_path)
        return input_path_obj.parent / f"{input_path_obj.stem}_findings{extension}"


@click.group()
@click.version_option(package_name="lavendertown")
def cli() -> None:
    """LavenderTown - Data Quality Inspector CLI.

    This is the main CLI entry point for LavenderTown. It provides commands
    for analyzing data quality, detecting drift, and exporting rules.

    Available commands:
        - analyze: Analyze a single CSV file
        - analyze-batch: Analyze multiple CSV files in a directory
        - compare: Compare two datasets for drift detection
        - export-rules: Export rules to Pandera or Great Expectations format

    Use ``lavendertown <command> --help`` for help on specific commands.
    """
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--rules",
    type=click.Path(exists=True),
    help="Path to rules JSON file",
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output directory (default: same as input file)",
)
@click.option(
    "--output-file",
    type=click.Path(),
    help="Output file path (overrides output-dir)",
)
@click.option(
    "--backend",
    type=click.Choice(["pandas", "polars"], case_sensitive=False),
    default="pandas",
    help="DataFrame backend",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress progress output",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
def analyze(
    filepath: str,
    rules: str | None,
    output_format: str,
    output_dir: str | None,
    output_file: str | None,
    backend: str,
    quiet: bool,
    verbose: bool,
) -> None:
    """Analyze a single CSV file for data quality issues.

    Loads a CSV file, runs data quality analysis using all built-in detectors,
    optionally applies custom rules, and exports the findings to a file.

    The analysis includes:
    - Null density detection
    - Type inconsistency detection
    - Statistical outlier detection
    - Custom rule violations (if rules file provided)

    Args:
        filepath: Path to the CSV file to analyze. Must exist and be readable.
        rules: Optional path to a JSON file containing custom rules to apply.
        output_format: Format for output file. Options: "json" or "csv".
        output_dir: Optional directory for output file. If not specified,
            output is placed in the same directory as the input file.
        output_file: Optional explicit output file path. Takes precedence
            over output_dir if specified.
        backend: DataFrame backend to use. Options: "pandas" or "polars".
        quiet: If True, suppress progress output messages.
        verbose: If True, show detailed error messages including tracebacks.

    Example:
        Analyze a file and save results as JSON::

            lavendertown analyze data.csv --output-format json --output-dir results/

        Analyze with custom rules::

            lavendertown analyze data.csv --rules my_rules.json --output-format csv

    Exits with code 1 on error, 0 on success.
    """
    try:
        if not quiet:
            click.echo(f"Loading data from {filepath}...")

        df = _load_dataframe(filepath, backend=backend)

        if not quiet:
            click.echo(f"Analyzing {len(df)} rows...")

        inspector = Inspector(df)

        # Load rules if provided
        findings = inspector.detect()
        ruleset = _load_ruleset_from_file(rules)
        if ruleset and ruleset.rules:
            if verbose:
                click.echo(f"Loaded {len(ruleset.rules)} rules from {rules}")
            # Execute rules and add findings
            from lavendertown.ui.rules import execute_ruleset

            rule_findings = execute_ruleset(None, ruleset, df)  # type: ignore[arg-type]
            findings.extend(rule_findings)

        if not quiet:
            click.echo(f"Found {len(findings)} data quality issues")

        # Determine output path
        extension = ".json" if output_format.lower() == "json" else ".csv"
        output_path = _get_output_path(filepath, output_dir, output_file, extension)

        # Export findings
        if output_format.lower() == "json":
            export_to_json_file(findings, str(output_path))
        else:
            export_to_csv_file(findings, str(output_path))

        if not quiet:
            click.echo(f"Results saved to {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help="Output directory for results",
)
@click.option(
    "--rules",
    type=click.Path(exists=True),
    help="Path to rules JSON file",
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option(
    "--backend",
    type=click.Choice(["pandas", "polars"], case_sensitive=False),
    default="pandas",
    help="DataFrame backend",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress progress output",
)
def analyze_batch(
    input_dir: str,
    output_dir: str,
    rules: str | None,
    output_format: str,
    backend: str,
    quiet: bool,
) -> None:
    """Analyze multiple CSV files in a directory.

    Example:
        lavendertown analyze-batch data/ --output-dir results/
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_files = list(input_path.glob("*.csv"))
    if not csv_files:
        click.echo(f"No CSV files found in {input_dir}", err=True)
        sys.exit(1)

    if not quiet:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    # Load ruleset if provided
    ruleset = _load_ruleset_from_file(rules)
    if ruleset and not quiet:
        click.echo(f"Loaded {len(ruleset.rules)} rules from {rules}")

    for i, csv_file in enumerate(csv_files, 1):
        if not quiet:
            click.echo(f"\n[{i}/{len(csv_files)}] Processing {csv_file.name}...")

        try:
            df = _load_dataframe(str(csv_file), backend=backend)
            inspector = Inspector(df)

            findings = inspector.detect()

            # Execute rules if provided
            if ruleset and ruleset.rules:
                from lavendertown.ui.rules import execute_ruleset

                rule_findings = execute_ruleset(None, ruleset, df)  # type: ignore[arg-type]
                findings.extend(rule_findings)

            extension = ".json" if output_format.lower() == "json" else ".csv"
            output_file = output_path / f"{csv_file.stem}_findings{extension}"

            if output_format.lower() == "json":
                export_to_json_file(findings, str(output_file))
            else:
                export_to_csv_file(findings, str(output_file))

            if not quiet:
                click.echo(f"  Found {len(findings)} issues -> {output_file.name}")

        except Exception as e:
            click.echo(f"  Error processing {csv_file.name}: {e}", err=True)
            continue

    if not quiet:
        click.echo(f"\nBatch processing complete. Results in {output_dir}")


@cli.command()
@click.argument("baseline_file", type=click.Path(exists=True))
@click.argument("current_file", type=click.Path(exists=True))
@click.option(
    "--output-format",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    help="Output directory (default: same as current file)",
)
@click.option(
    "--output-file",
    type=click.Path(),
    help="Output file path (overrides output-dir)",
)
@click.option(
    "--backend",
    type=click.Choice(["pandas", "polars"], case_sensitive=False),
    default="pandas",
    help="DataFrame backend",
)
@click.option(
    "--comparison-type",
    type=click.Choice(["full", "schema_only", "distribution_only"]),
    default="full",
    help="Type of comparison",
)
@click.option(
    "--distribution-threshold",
    type=float,
    default=10.0,
    help="Percentage threshold for distribution changes",
)
def compare(
    baseline_file: str,
    current_file: str,
    output_format: str,
    output_dir: str | None,
    output_file: str | None,
    backend: str,
    comparison_type: str,
    distribution_threshold: float,
) -> None:
    """Compare two datasets for drift detection.

    Example:
        lavendertown compare baseline.csv current.csv --output-format json
    """
    try:
        click.echo(f"Loading baseline: {baseline_file}...")
        baseline_df = _load_dataframe(baseline_file, backend=backend)

        click.echo(f"Loading current: {current_file}...")
        current_df = _load_dataframe(current_file, backend=backend)

        click.echo("Comparing datasets...")
        inspector = Inspector(current_df)
        drift_findings = inspector.compare_with_baseline(
            baseline_df=baseline_df,
            comparison_type=comparison_type,
            distribution_threshold=distribution_threshold,
        )

        click.echo(f"Found {len(drift_findings)} drift issues")

        # Determine output path
        extension = ".json" if output_format.lower() == "json" else ".csv"
        output_path = _get_output_path(current_file, output_dir, output_file, extension)

        # Export findings
        if output_format.lower() == "json":
            export_to_json_file(drift_findings, str(output_path))
        else:
            export_to_csv_file(drift_findings, str(output_path))

        click.echo(f"Results saved to {output_path}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("rules_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["pandera", "great_expectations"], case_sensitive=False),
    required=True,
    help="Export format",
)
@click.option(
    "--output-file",
    type=click.Path(),
    required=True,
    help="Output file path",
)
@click.option(
    "--schema-info",
    type=click.Path(exists=True),
    help="Path to JSON file with column schema info (for Pandera only)",
)
def export_rules(
    rules_file: str,
    export_format: str,
    output_file: str,
    schema_info: str | None,
) -> None:
    """Export rules to Pandera or Great Expectations format.

    Example:
        lavendertown export-rules rules.json --format pandera --output-file schema.py
    """
    try:
        click.echo(f"Loading rules from {rules_file}...")
        ruleset = load_ruleset(rules_file)

        if export_format == "pandera":
            try:
                from lavendertown.export.pandera import export_ruleset_to_pandera_file

                schema_info_dict = None
                if schema_info:
                    with open(schema_info, "r") as f:
                        schema_info_dict = json.load(f)

                export_ruleset_to_pandera_file(
                    ruleset, output_file, schema_info=schema_info_dict
                )
                click.echo(f"Pandera schema exported to {output_file}")
            except ImportError:
                click.echo(
                    "Error: pandera is required. Install with: pip install lavendertown[pandera]",
                    err=True,
                )
                sys.exit(1)

        elif export_format == "great_expectations":
            try:
                from lavendertown.export.great_expectations import (
                    export_ruleset_to_great_expectations_file,
                )

                export_ruleset_to_great_expectations_file(ruleset, output_file)
                click.echo(f"Great Expectations suite exported to {output_file}")
            except ImportError:
                click.echo(
                    "Error: great-expectations is required. Install with: pip install lavendertown[great_expectations]",
                    err=True,
                )
                sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
