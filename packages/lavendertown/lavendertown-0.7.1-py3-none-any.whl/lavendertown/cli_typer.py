"""Command-line interface for LavenderTown using Typer.

This module provides a Typer-based CLI for running LavenderTown data quality
analysis from the command line. It supports single file analysis, batch
processing, drift detection, and rule export functionality.

The CLI can be accessed via the ``lavendertown`` command after installation,
or by running this module directly with ``python -m lavendertown.cli_typer``.

Note: This is a parallel implementation alongside the Click-based CLI for
gradual migration. The Click CLI remains the default for backward compatibility.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

try:
    import typer
    from typer import Option

    _TYPER_AVAILABLE = True
except ImportError:
    _TYPER_AVAILABLE = False
    typer = None  # type: ignore[assignment,misc]
    Option = None  # type: ignore[assignment,misc]

try:
    from rich.console import Console
    from rich.progress import Progress
    from rich.table import Table

    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False
    Console = None  # type: ignore[assignment,misc]
    Progress = None  # type: ignore[assignment,misc]
    Table = None  # type: ignore[assignment,misc]

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
from lavendertown.rules.storage import load_ruleset

# Create app and console instances
if _TYPER_AVAILABLE:
    app = typer.Typer(help="LavenderTown - Data Quality Inspector CLI")
    _console = Console() if _RICH_AVAILABLE else None
else:
    app = None  # type: ignore[assignment]
    _console = None  # type: ignore[assignment]


def _load_dataframe(filepath: str, backend: str = "pandas") -> Any:
    """Load a CSV file into a DataFrame.

    Args:
        filepath: Path to the CSV file to load
        backend: Backend to use ("pandas" or "polars")

    Returns:
        DataFrame object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If backend is unsupported
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
                "polars is required but not installed. "
                "Install with: pip install lavendertown[polars]"
            )
        return pl.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported backend: {backend}")


if _TYPER_AVAILABLE:

    @app.command()
    def analyze(
        filepath: Annotated[Path, typer.Argument(help="Path to CSV file to analyze")],
        rules: Annotated[
            Path | None, Option("--rules", help="Path to rules JSON file")
        ] = None,
        output_format: Annotated[
            str,
            Option(
                "--output-format",
                "-f",
                help="Output format (json, csv, or parquet)",
            ),
        ] = "json",
        output_dir: Annotated[
            Path | None,
            Option("--output-dir", "-o", help="Output directory"),
        ] = None,
        output_file: Annotated[
            Path | None,
            Option("--output-file", help="Output file path (overrides output-dir)"),
        ] = None,
        backend: Annotated[
            str, Option("--backend", help="DataFrame backend (pandas or polars)")
        ] = "pandas",
        quiet: Annotated[bool, Option("--quiet", "-q", help="Suppress output")] = False,
        verbose: Annotated[
            bool, Option("--verbose", "-v", help="Verbose output")
        ] = False,
    ) -> None:
        """Analyze a single CSV file for data quality issues."""
        try:
            if not quiet and _console:
                _console.print(f"[cyan]Loading data from {filepath}...[/cyan]")

            df = _load_dataframe(str(filepath), backend=backend)

            if not quiet and _console:
                _console.print(f"[cyan]Analyzing {len(df):,} rows...[/cyan]")

            inspector = Inspector(df)

            findings = inspector.detect()

            # Load rules if provided
            ruleset = None
            if rules:
                ruleset = load_ruleset(str(rules))
                if ruleset and ruleset.rules:
                    if verbose and _console:
                        _console.print(
                            f"[green]Loaded {len(ruleset.rules)} rules[/green]"
                        )
                    from lavendertown.ui.rules import execute_ruleset

                    rule_findings = execute_ruleset(None, ruleset, df)  # type: ignore[arg-type]
                    findings.extend(rule_findings)

            if not quiet and _console:
                table = Table(title="Analysis Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green", justify="right")
                table.add_row("Total Findings", str(len(findings)))
                _console.print(table)

            # Determine output path
            format_lower = output_format.lower()
            if format_lower == "json":
                extension = ".json"
            elif format_lower == "parquet":
                extension = ".parquet"
            else:
                extension = ".csv"

            if output_file:
                output_path = output_file
            elif output_dir:
                output_path = output_dir / f"{filepath.stem}_findings{extension}"
            else:
                output_path = filepath.parent / f"{filepath.stem}_findings{extension}"

            # Export findings
            if format_lower == "json":
                export_to_json_file(findings, str(output_path))
            elif format_lower == "parquet":
                try:
                    from lavendertown.export.parquet import export_findings_to_parquet

                    export_findings_to_parquet(findings, str(output_path))
                except ImportError:
                    if _console:
                        _console.print(
                            "[red]Error:[/red] PyArrow required. "
                            "Install with: pip install lavendertown[parquet]"
                        )
                    sys.exit(1)
            else:
                export_to_csv_file(findings, str(output_path))

            if not quiet and _console:
                _console.print(
                    f"[green]✓[/green] Results saved to [bold]{output_path}[/bold]"
                )

        except Exception as e:
            if _console:
                _console.print(f"[bold red]Error:[/bold red] {e}")
            else:
                print(f"Error: {e}", file=sys.stderr)
            if verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    # Add version command
    @app.command()
    def version() -> None:
        """Show version information."""
        from lavendertown import __version__

        print(f"LavenderTown version {__version__}")

    # Entry point
    def main() -> None:
        """Main entry point for Typer CLI."""
        if not _TYPER_AVAILABLE:
            print(
                "Error: Typer is required. Install with: pip install lavendertown[cli]",
                file=sys.stderr,
            )
            sys.exit(1)
        app()

else:

    def main() -> None:
        """Fallback if Typer is not available."""
        print(
            "Error: Typer is required. Install with: pip install lavendertown[cli]",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
