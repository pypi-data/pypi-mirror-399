"""Tests for Typer CLI functionality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from lavendertown.cli_typer import app, main

try:
    import typer  # noqa: F401

    _TYPER_AVAILABLE = True
except ImportError:
    _TYPER_AVAILABLE = False


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "sample.csv"
    csv_content = "name,age,email\nAlice,25,alice@example.com\nBob,30,bob@example.com\n"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    if not _TYPER_AVAILABLE:
        pytest.skip("Typer not installed")
    return CliRunner()


@pytest.mark.skipif(not _TYPER_AVAILABLE, reason="Typer not installed")
class TestTyperCLI:
    """Tests for Typer-based CLI commands."""

    def test_analyze_command_basic(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test basic analyze command."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Loading data from" in result.stdout or "Analyzing" in result.stdout

    def test_analyze_command_with_parquet_output(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test analyze command with Parquet output."""
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            pytest.skip("PyArrow not installed")

        output_file = tmp_path / "output.parquet"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--output-format",
                "parquet",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_analyze_command_with_rules(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test analyze command with rules file."""
        # Create a simple rules file
        rules_file = tmp_path / "rules.json"
        rules_content = {
            "name": "test_rules",
            "description": "Test rules",
            "rules": [
                {
                    "name": "age_range",
                    "description": "Age must be 0-150",
                    "rule_type": "range",
                    "column": "age",
                    "parameters": {"min_value": 0, "max_value": 150},
                }
            ],
        }
        rules_file.write_text(json.dumps(rules_content))

        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--rules",
                str(rules_file),
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_analyze_command_quiet_mode(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test analyze command with quiet flag."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Quiet mode should have minimal output
        assert len(result.stdout.strip()) < 200

    def test_analyze_command_verbose_mode(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test analyze command with verbose flag."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_analyze_command_invalid_file(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test analyze command with non-existent file."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(tmp_path / "nonexistent.csv"),
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code != 0

    def test_analyze_command_backend_polars(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test analyze command with Polars backend."""
        try:
            import polars  # noqa: F401
        except ImportError:
            pytest.skip("Polars not installed")

        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            app,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--backend",
                "polars",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_version_command(self, cli_runner: CliRunner) -> None:
        """Test version command."""
        result = cli_runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "LavenderTown version" in result.stdout

    def test_main_function(self) -> None:
        """Test main function entry point."""
        # Should not raise an error when Typer is available
        if _TYPER_AVAILABLE:
            assert callable(main)
        else:
            # Should handle gracefully when Typer is not installed
            import sys
            from io import StringIO

            original_stderr = sys.stderr
            sys.stderr = StringIO()
            try:
                main()
                # Should exit with error code
            except SystemExit:
                pass
            finally:
                sys.stderr = original_stderr


@pytest.mark.skipif(not _TYPER_AVAILABLE, reason="Typer not installed")
class TestTyperCLIHelp:
    """Tests for CLI help functionality."""

    def test_help_command(self, cli_runner: CliRunner) -> None:
        """Test help command."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "LavenderTown" in result.stdout
        assert "analyze" in result.stdout.lower()

    def test_analyze_help(self, cli_runner: CliRunner) -> None:
        """Test analyze command help."""
        result = cli_runner.invoke(app, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "filepath" in result.stdout.lower() or "analyze" in result.stdout.lower()
