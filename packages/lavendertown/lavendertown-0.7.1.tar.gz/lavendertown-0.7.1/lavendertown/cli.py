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
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

    # Create a mock Console class that mimics click.echo for fallback
    class Console:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def print(self, *args: Any, **kwargs: Any) -> None:
            click.echo(*args)

        def status(self, *args: Any, **kwargs: Any) -> Any:
            class Status:
                def __enter__(self) -> Any:
                    return self

                def __exit__(self, *args: Any) -> None:
                    pass

            return Status()


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

# Create a global console instance for Rich output
_console = Console() if _RICH_AVAILABLE else Console()


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
    type=click.Choice(["json", "csv", "parquet"], case_sensitive=False),
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
            if _RICH_AVAILABLE:
                _console.print(f"[cyan]Loading data from[/cyan] {filepath}...")
            else:
                click.echo(f"Loading data from {filepath}...")

        df = _load_dataframe(filepath, backend=backend)

        if not quiet:
            if _RICH_AVAILABLE:
                _console.print(f"[cyan]Analyzing[/cyan] {len(df):,} rows...")
            else:
                click.echo(f"Analyzing {len(df)} rows...")

        inspector = Inspector(df)

        # Load rules if provided
        findings = inspector.detect()
        ruleset = _load_ruleset_from_file(rules)
        if ruleset and ruleset.rules:
            if verbose:
                if _RICH_AVAILABLE:
                    _console.print(
                        f"[green]Loaded[/green] {len(ruleset.rules)} rules from {rules}"
                    )
                else:
                    click.echo(f"Loaded {len(ruleset.rules)} rules from {rules}")
            # Execute rules and add findings
            from lavendertown.ui.rules import execute_ruleset

            rule_findings = execute_ruleset(None, ruleset, df)  # type: ignore[arg-type]
            findings.extend(rule_findings)

        if not quiet:
            if _RICH_AVAILABLE:
                # Create summary table
                table = Table(
                    title="Analysis Summary",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green", justify="right")

                table.add_row("Total Findings", str(len(findings)))
                if findings:
                    # Count by type
                    type_counts: dict[str, int] = {}
                    severity_counts: dict[str, int] = {}
                    for finding in findings:
                        type_counts[finding.ghost_type] = (
                            type_counts.get(finding.ghost_type, 0) + 1
                        )
                        severity_counts[finding.severity] = (
                            severity_counts.get(finding.severity, 0) + 1
                        )

                    for ghost_type, count in sorted(type_counts.items()):
                        table.add_row(f"  {ghost_type}", str(count))
                    for severity, count in sorted(severity_counts.items()):
                        table.add_row(f"  Severity: {severity}", str(count))

                _console.print(table)
            else:
                click.echo(f"Found {len(findings)} data quality issues")

        # Determine output path
        format_lower = output_format.lower()
        if format_lower == "json":
            extension = ".json"
        elif format_lower == "parquet":
            extension = ".parquet"
        else:
            extension = ".csv"
        output_path = _get_output_path(filepath, output_dir, output_file, extension)

        # Export findings
        if format_lower == "json":
            export_to_json_file(findings, str(output_path))
        elif format_lower == "parquet":
            try:
                from lavendertown.export.parquet import export_findings_to_parquet

                export_findings_to_parquet(findings, str(output_path))
            except ImportError:
                if _RICH_AVAILABLE:
                    _console.print(
                        "[red]Error:[/red] PyArrow is required for Parquet export. "
                        "Install with: pip install lavendertown[parquet]"
                    )
                else:
                    click.echo(
                        "Error: PyArrow is required for Parquet export. "
                        "Install with: pip install lavendertown[parquet]",
                        err=True,
                    )
                sys.exit(1)
        else:
            export_to_csv_file(findings, str(output_path))

        if not quiet:
            if _RICH_AVAILABLE:
                _console.print(
                    f"[green]✓[/green] Results saved to [bold]{output_path}[/bold]"
                )
            else:
                click.echo(f"Results saved to {output_path}")

    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
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
    type=click.Choice(["json", "csv", "parquet"], case_sensitive=False),
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
        if _RICH_AVAILABLE:
            _console.print(
                f"[bold red]Error:[/bold red] No CSV files found in {input_dir}"
            )
        else:
            click.echo(f"No CSV files found in {input_dir}", err=True)
        sys.exit(1)

    if not quiet:
        if _RICH_AVAILABLE:
            _console.print(
                f"[cyan]Found[/cyan] [bold]{len(csv_files)}[/bold] CSV files to process"
            )
        else:
            click.echo(f"Found {len(csv_files)} CSV files to process")

    # Load ruleset if provided
    ruleset = _load_ruleset_from_file(rules)
    if ruleset and not quiet:
        if _RICH_AVAILABLE:
            _console.print(
                f"[green]Loaded[/green] {len(ruleset.rules)} rules from {rules}"
            )
        else:
            click.echo(f"Loaded {len(ruleset.rules)} rules from {rules}")

    if _RICH_AVAILABLE and not quiet:
        # Use Rich progress bar for batch processing
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=_console,
        ) as progress:
            task = progress.add_task("[cyan]Processing files...", total=len(csv_files))

            results_table = Table(title="Batch Processing Results", show_header=True)
            results_table.add_column("File", style="cyan")
            results_table.add_column("Findings", style="green", justify="right")
            results_table.add_column("Status", style="yellow")

            for csv_file in csv_files:
                progress.update(task, description=f"Processing {csv_file.name}...")

                try:
                    df = _load_dataframe(str(csv_file), backend=backend)
                    inspector = Inspector(df)

                    findings = inspector.detect()

                    # Execute rules if provided
                    if ruleset and ruleset.rules:
                        from lavendertown.ui.rules import execute_ruleset

                        rule_findings = execute_ruleset(
                            None,
                            ruleset,
                            df,  # type: ignore[arg-type]
                        )
                        findings.extend(rule_findings)

                    format_lower = output_format.lower()
                    if format_lower == "json":
                        extension = ".json"
                    elif format_lower == "parquet":
                        extension = ".parquet"
                    else:
                        extension = ".csv"
                    output_file = output_path / f"{csv_file.stem}_findings{extension}"

                    if format_lower == "json":
                        export_to_json_file(findings, str(output_file))
                    elif format_lower == "parquet":
                        try:
                            from lavendertown.export.parquet import (
                                export_findings_to_parquet,
                            )

                            export_findings_to_parquet(findings, str(output_file))
                        except ImportError:
                            progress.console.print(
                                "[red]Error:[/red] PyArrow is required for Parquet export. "
                                "Install with: pip install lavendertown[parquet]"
                            )
                            continue
                    else:
                        export_to_csv_file(findings, str(output_file))

                    results_table.add_row(
                        csv_file.name, str(len(findings)), "[green]✓[/green]"
                    )
                    progress.advance(task)

                except Exception as e:
                    results_table.add_row(csv_file.name, "Error", f"[red]✗[/red] {e}")
                    progress.advance(task)
                    continue

            _console.print(results_table)
            _console.print(
                f"\n[green]✓[/green] Batch processing complete. Results in [bold]{output_dir}[/bold]"
            )
    else:
        # Fallback to basic output
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

                    rule_findings = execute_ruleset(
                        None,
                        ruleset,
                        df,  # type: ignore[arg-type]
                    )
                    findings.extend(rule_findings)

                format_lower = output_format.lower()
                if format_lower == "json":
                    extension = ".json"
                elif format_lower == "parquet":
                    extension = ".parquet"
                else:
                    extension = ".csv"
                output_file = output_path / f"{csv_file.stem}_findings{extension}"

                if format_lower == "json":
                    export_to_json_file(findings, str(output_file))
                elif format_lower == "parquet":
                    try:
                        from lavendertown.export.parquet import (
                            export_findings_to_parquet,
                        )

                        export_findings_to_parquet(findings, str(output_file))
                    except ImportError:
                        click.echo(
                            "Error: PyArrow is required for Parquet export. "
                            "Install with: pip install lavendertown[parquet]",
                            err=True,
                        )
                        continue
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
        if _RICH_AVAILABLE:
            _console.print(f"[cyan]Loading baseline:[/cyan] {baseline_file}...")
        else:
            click.echo(f"Loading baseline: {baseline_file}...")
        baseline_df = _load_dataframe(baseline_file, backend=backend)

        if _RICH_AVAILABLE:
            _console.print(f"[cyan]Loading current:[/cyan] {current_file}...")
        else:
            click.echo(f"Loading current: {current_file}...")
        current_df = _load_dataframe(current_file, backend=backend)

        if _RICH_AVAILABLE:
            _console.print("[cyan]Comparing datasets...[/cyan]")
        else:
            click.echo("Comparing datasets...")
        inspector = Inspector(current_df)
        drift_findings = inspector.compare_with_baseline(
            baseline_df=baseline_df,
            comparison_type=comparison_type,
            distribution_threshold=distribution_threshold,
        )

        if _RICH_AVAILABLE:
            _console.print(
                f"[yellow]Found[/yellow] [bold]{len(drift_findings)}[/bold] drift issues"
            )
        else:
            click.echo(f"Found {len(drift_findings)} drift issues")

        # Determine output path
        format_lower = output_format.lower()
        if format_lower == "json":
            extension = ".json"
        elif format_lower == "parquet":
            extension = ".parquet"
        else:
            extension = ".csv"
        output_path = _get_output_path(current_file, output_dir, output_file, extension)

        # Export findings
        if format_lower == "json":
            export_to_json_file(drift_findings, str(output_path))
        elif format_lower == "parquet":
            try:
                from lavendertown.export.parquet import export_findings_to_parquet

                export_findings_to_parquet(drift_findings, str(output_path))
            except ImportError:
                if _RICH_AVAILABLE:
                    _console.print(
                        "[red]Error:[/red] PyArrow is required for Parquet export. "
                        "Install with: pip install lavendertown[parquet]"
                    )
                else:
                    click.echo(
                        "Error: PyArrow is required for Parquet export. "
                        "Install with: pip install lavendertown[parquet]",
                        err=True,
                    )
                sys.exit(1)
        else:
            export_to_csv_file(drift_findings, str(output_path))

        if _RICH_AVAILABLE:
            _console.print(
                f"[green]✓[/green] Results saved to [bold]{output_path}[/bold]"
            )
        else:
            click.echo(f"Results saved to {output_path}")

    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
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
        if _RICH_AVAILABLE:
            _console.print(f"[cyan]Loading rules from[/cyan] {rules_file}...")
        else:
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
                if _RICH_AVAILABLE:
                    _console.print(
                        f"[green]✓[/green] Pandera schema exported to [bold]{output_file}[/bold]"
                    )
                else:
                    click.echo(f"Pandera schema exported to {output_file}")
            except ImportError:
                error_msg = "Error: pandera is required. Install with: pip install lavendertown[pandera]"
                if _RICH_AVAILABLE:
                    _console.print(f"[bold red]{error_msg}[/bold red]")
                else:
                    click.echo(error_msg, err=True)
                sys.exit(1)

        elif export_format == "great_expectations":
            try:
                from lavendertown.export.great_expectations import (
                    export_ruleset_to_great_expectations_file,
                )

                export_ruleset_to_great_expectations_file(ruleset, output_file)
                if _RICH_AVAILABLE:
                    _console.print(
                        f"[green]✓[/green] Great Expectations suite exported to [bold]{output_file}[/bold]"
                    )
                else:
                    click.echo(f"Great Expectations suite exported to {output_file}")
            except ImportError:
                error_msg = "Error: great-expectations is required. Install with: pip install lavendertown[great_expectations]"
                if _RICH_AVAILABLE:
                    _console.print(f"[bold red]{error_msg}[/bold red]")
                else:
                    click.echo(error_msg, err=True)
                sys.exit(1)

    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("findings_file", type=click.Path(exists=True))
@click.option(
    "--title",
    required=True,
    help="Report title",
)
@click.option(
    "--author",
    default="CLI User",
    help="Author name",
)
@click.option(
    "--rules-file",
    type=click.Path(exists=True),
    help="Path to ruleset JSON file (optional)",
)
@click.option(
    "--output-file",
    type=click.Path(),
    help="Output file path (optional, defaults to .lavendertown/reports/)",
)
def share(
    findings_file: str,
    title: str,
    author: str,
    rules_file: str | None,
    output_file: str | None,
) -> None:
    """Export findings as a shareable report.

    Example:
        lavendertown share findings.json --title "Q4 Report" --author "Alice"
    """
    try:
        from lavendertown.collaboration.api import (
            create_shareable_report,
            export_report,
        )
        from lavendertown.models import GhostFinding

        if _RICH_AVAILABLE:
            _console.print(f"[cyan]Loading findings from[/cyan] {findings_file}...")
        else:
            click.echo(f"Loading findings from {findings_file}...")

        # Load findings
        with open(findings_file, "r") as f:
            findings_data = json.load(f)

        findings = [GhostFinding.from_dict(f) for f in findings_data]

        # Load ruleset if provided
        ruleset = None
        if rules_file:
            ruleset = load_ruleset(rules_file)

        # Create report
        report = create_shareable_report(
            title=title,
            author=author,
            findings=findings,
            ruleset=ruleset,
        )

        # Export
        report_path = export_report(report, output_file)
        if _RICH_AVAILABLE:
            _console.print(
                f"[green]✓[/green] Report exported to: [bold]{report_path}[/bold]"
            )
        else:
            click.echo(f"Report exported to: {report_path}")

    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("report_file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Directory to extract findings and ruleset (optional)",
)
def import_report(
    report_file: str,
    output_dir: str | None,
) -> None:
    """Import a shareable report.

    Example:
        lavendertown import-report report.json --output-dir ./imported/
    """
    try:
        from lavendertown.collaboration.api import import_report

        if _RICH_AVAILABLE:
            _console.print(f"[cyan]Importing report from[/cyan] {report_file}...")
        else:
            click.echo(f"Importing report from {report_file}...")

        report = import_report(report_file)

        if _RICH_AVAILABLE:
            panel = Panel.fit(
                f"[bold]Title:[/bold] {report.title}\n"
                f"[bold]Author:[/bold] {report.author}\n"
                f"[bold]Created:[/bold] {report.created_at}\n"
                f"[bold]Findings:[/bold] {len(report.findings)}\n"
                f"[bold]Annotations:[/bold] {len(report.annotations)}",
                title="Report Information",
                border_style="green",
            )
            _console.print(panel)
        else:
            click.echo(f"Report: {report.title}")
            click.echo(f"Author: {report.author}")
            click.echo(f"Created: {report.created_at}")
            click.echo(f"Findings: {len(report.findings)}")
            click.echo(f"Annotations: {len(report.annotations)}")

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Export findings
            findings_file = output_path / "findings.json"
            with open(findings_file, "w") as f:
                json.dump([f.to_dict() for f in report.findings], f, indent=2)
            if _RICH_AVAILABLE:
                _console.print(
                    f"[green]✓[/green] Findings exported to [bold]{findings_file}[/bold]"
                )
            else:
                click.echo(f"Findings exported to {findings_file}")

            # Export ruleset if present
            if report.ruleset:
                ruleset_file = output_path / "ruleset.json"
                with open(ruleset_file, "w") as f:
                    json.dump(report.ruleset.to_dict(), f, indent=2)
                if _RICH_AVAILABLE:
                    _console.print(
                        f"[green]✓[/green] Ruleset exported to [bold]{ruleset_file}[/bold]"
                    )
                else:
                    click.echo(f"Ruleset exported to {ruleset_file}")

    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--output",
    type=click.Path(),
    help="Output HTML file path (default: <filename>_profile.html)",
)
@click.option(
    "--minimal",
    is_flag=True,
    help="Generate minimal report (faster)",
)
@click.option(
    "--title",
    default="Data Profiling Report",
    help="Report title",
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
def profile(
    filepath: str,
    output: str | None,
    minimal: bool,
    title: str,
    backend: str,
    quiet: bool,
) -> None:
    """Generate a comprehensive data profiling report.

    Creates an HTML profiling report with statistics, distributions, correlations,
    and data quality insights using ydata-profiling.

    Example:
        lavendertown profile data.csv --output report.html
    """
    try:
        from lavendertown.profiling import generate_profiling_report

        if not quiet:
            if _RICH_AVAILABLE:
                _console.print(f"[cyan]Loading data from {filepath}...[/cyan]")
            else:
                click.echo(f"Loading data from {filepath}...")

        df = _load_dataframe(filepath, backend=backend)

        if not quiet:
            if _RICH_AVAILABLE:
                _console.print("[cyan]Generating profile report...[/cyan]")
            else:
                click.echo("Generating profile report...")

        # Determine output path
        if output:
            output_path = output
        else:
            input_path = Path(filepath)
            output_path = str(input_path.parent / f"{input_path.stem}_profile.html")

        generate_profiling_report(df, output_path, minimal=minimal, title=title)

        if not quiet:
            if _RICH_AVAILABLE:
                _console.print(
                    f"[green]✓[/green] Profile report saved to [bold]{output_path}[/bold]"
                )
            else:
                click.echo(f"Profile report saved to {output_path}")

    except ImportError:
        if _RICH_AVAILABLE:
            _console.print(
                "[red]Error:[/red] ydata-profiling is required for profiling reports. "
                "Install with: pip install lavendertown[profiling]"
            )
        else:
            click.echo(
                "Error: ydata-profiling is required for profiling reports. "
                "Install with: pip install lavendertown[profiling]",
                err=True,
            )
        sys.exit(1)
    except Exception as e:
        if _RICH_AVAILABLE:
            _console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
