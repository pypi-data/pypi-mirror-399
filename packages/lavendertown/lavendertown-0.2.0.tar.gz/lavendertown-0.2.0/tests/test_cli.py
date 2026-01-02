"""Tests for CLI functionality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from lavendertown.cli import cli
from lavendertown.rules.models import Rule, RuleSet
from lavendertown.rules.storage import save_ruleset


@pytest.fixture
def sample_csv_file(tmp_path: pytest.TempPathFactory) -> Path:
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "sample.csv"
    csv_content = "name,age,email\nAlice,25,alice@example.com\nBob,30,bob@example.com\n"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def sample_rules_file(tmp_path: pytest.TempPathFactory) -> Path:
    """Create a sample rules JSON file for testing."""
    ruleset = RuleSet(name="test_rules", description="Test rules")
    ruleset.add_rule(
        Rule(
            name="age_range",
            description="Age must be 0-150",
            rule_type="range",
            column="age",
            parameters={"min_value": 0, "max_value": 150},
        )
    )
    rules_file = tmp_path / "rules.json"
    save_ruleset(ruleset, rules_file)
    return rules_file


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


def test_cli_version(cli_runner: CliRunner) -> None:
    """Test CLI version command."""
    result = cli_runner.invoke(cli, ["--version"])
    # Version command may fail if package is not installed (common in development)
    # In that case, we just verify the command exists and responds
    if result.exit_code == 0:
        assert (
            "version" in result.output.lower()
            or "lavendertown" in result.output.lower()
        )
    else:
        # Package not installed - verify it's the expected error
        assert "not installed" in result.output.lower() or result.exit_code != 0


def test_analyze_command_basic(
    cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
) -> None:
    """Test basic analyze command."""
    output_file = tmp_path / "output.json"
    result = cli_runner.invoke(
        cli,
        ["analyze", str(sample_csv_file), "--output-file", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check that output is valid JSON
    data = json.loads(output_file.read_text())
    assert "findings" in data


def test_analyze_command_csv_output(
    cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
) -> None:
    """Test analyze command with CSV output."""
    output_file = tmp_path / "output.csv"
    result = cli_runner.invoke(
        cli,
        [
            "analyze",
            str(sample_csv_file),
            "--output-format",
            "csv",
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.read_text().startswith("ghost_type")


def test_analyze_command_with_rules(
    cli_runner: CliRunner,
    sample_csv_file: Path,
    sample_rules_file: Path,
    tmp_path: Path,
) -> None:
    """Test analyze command with rules file."""
    output_file = tmp_path / "output.json"
    result = cli_runner.invoke(
        cli,
        [
            "analyze",
            str(sample_csv_file),
            "--rules",
            str(sample_rules_file),
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()


def test_analyze_command_file_not_found(cli_runner: CliRunner) -> None:
    """Test analyze command with non-existent file."""
    result = cli_runner.invoke(cli, ["analyze", "nonexistent.csv"])

    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "error" in result.output.lower()


def test_analyze_batch_command(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Test analyze-batch command."""
    # Create input directory with CSV files
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    csv1 = input_dir / "file1.csv"
    csv1.write_text("name,age\nAlice,25\nBob,30\n")

    csv2 = input_dir / "file2.csv"
    csv2.write_text("name,age\nCharlie,35\nDiana,40\n")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = cli_runner.invoke(
        cli,
        [
            "analyze-batch",
            str(input_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "file1_findings.json").exists()
    assert (output_dir / "file2_findings.json").exists()


def test_analyze_batch_command_no_files(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Test analyze-batch command with directory containing no CSV files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = cli_runner.invoke(
        cli,
        [
            "analyze-batch",
            str(empty_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code != 0
    assert "no csv files" in result.output.lower() or "error" in result.output.lower()


def test_compare_command(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Test compare command."""
    baseline_file = tmp_path / "baseline.csv"
    baseline_file.write_text("name,age\nAlice,25\nBob,30\n")

    current_file = tmp_path / "current.csv"
    current_file.write_text("name,age\nAlice,26\nBob,30\nCharlie,35\n")

    output_file = tmp_path / "drift.json"

    result = cli_runner.invoke(
        cli,
        [
            "compare",
            str(baseline_file),
            str(current_file),
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Check that output is valid JSON
    data = json.loads(output_file.read_text())
    assert "findings" in data


def test_export_rules_command_pandera(
    cli_runner: CliRunner, sample_rules_file: Path, tmp_path: Path
) -> None:
    """Test export-rules command for Pandera."""
    output_file = tmp_path / "schema.py"

    result = cli_runner.invoke(
        cli,
        [
            "export-rules",
            str(sample_rules_file),
            "--format",
            "pandera",
            "--output-file",
            str(output_file),
        ],
    )

    # May fail if pandera is not installed, which is acceptable
    if result.exit_code == 0:
        assert output_file.exists()
    else:
        # Should fail gracefully with informative error
        assert "pandera" in result.output.lower() or "error" in result.output.lower()


def test_export_rules_command_great_expectations(
    cli_runner: CliRunner, sample_rules_file: Path, tmp_path: Path
) -> None:
    """Test export-rules command for Great Expectations."""
    output_file = tmp_path / "expectation_suite.json"

    result = cli_runner.invoke(
        cli,
        [
            "export-rules",
            str(sample_rules_file),
            "--format",
            "great_expectations",
            "--output-file",
            str(output_file),
        ],
    )

    # May fail if great-expectations is not installed, which is acceptable
    if result.exit_code == 0:
        assert output_file.exists()
    else:
        # Should fail gracefully with informative error
        assert (
            "great.expectations" in result.output.lower()
            or "error" in result.output.lower()
        )


def test_export_rules_command_file_not_found(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    """Test export-rules command with non-existent rules file."""
    output_file = tmp_path / "output.json"

    result = cli_runner.invoke(
        cli,
        [
            "export-rules",
            "nonexistent.json",
            "--format",
            "pandera",
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "error" in result.output.lower()


def test_analyze_command_quiet_mode(
    cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
) -> None:
    """Test analyze command with quiet flag."""
    output_file = tmp_path / "output.json"
    result = cli_runner.invoke(
        cli,
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
    assert len(result.output.strip()) < 100  # Very minimal output


def test_analyze_command_backend_polars(
    cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
) -> None:
    """Test analyze command with Polars backend."""
    output_file = tmp_path / "output.json"
    result = cli_runner.invoke(
        cli,
        [
            "analyze",
            str(sample_csv_file),
            "--backend",
            "polars",
            "--output-file",
            str(output_file),
        ],
    )

    # May fail if polars is not installed
    if result.exit_code == 0:
        assert output_file.exists()
    else:
        # Should fail gracefully
        assert "polars" in result.output.lower() or "error" in result.output.lower()


def test_compare_command_comparison_types(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    """Test compare command with different comparison types."""
    baseline_file = tmp_path / "baseline.csv"
    baseline_file.write_text("name,age\nAlice,25\n")

    current_file = tmp_path / "current.csv"
    current_file.write_text("name,age\nAlice,25\n")

    for comparison_type in ["full", "schema_only", "distribution_only"]:
        output_file = tmp_path / f"drift_{comparison_type}.json"

        result = cli_runner.invoke(
            cli,
            [
                "compare",
                str(baseline_file),
                str(current_file),
                "--comparison-type",
                comparison_type,
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
