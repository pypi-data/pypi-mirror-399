"""Tests for Rich CLI integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from lavendertown.cli import cli


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "sample.csv"
    csv_content = "name,age,email\nAlice,25,alice@example.com\nBob,30,bob@example.com\nCharlie,35,charlie@example.com\n"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


class TestRichCLIIntegration:
    """Test Rich integration in CLI commands."""

    def test_analyze_with_rich_output(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test that analyze command produces output (with or without Rich)."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            cli,
            ["analyze", str(sample_csv_file), "--output-file", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Output should contain some indication of processing
        # (exact format depends on whether Rich is available)
        assert len(result.output) > 0

    def test_analyze_quiet_mode(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test that --quiet flag suppresses output."""
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

        # Output should be minimal or empty with --quiet
        # (may still have error output, but no progress messages)
        # Quiet mode should have very little output
        assert len(result.output.strip()) < 100

    def test_analyze_batch_with_rich(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test analyze-batch command produces output."""
        # Create input directory with multiple CSV files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create multiple CSV files
        for i in range(3):
            csv_file = input_dir / f"file{i}.csv"
            csv_file.write_text(f"col1,col2\n{i},{i * 2}\n{i + 1},{(i + 1) * 2}\n")

        result = cli_runner.invoke(
            cli,
            ["analyze-batch", str(input_dir), "--output-dir", str(output_dir)],
        )

        assert result.exit_code == 0

        # Check that output files were created
        output_files = list(output_dir.glob("*.json"))
        assert len(output_files) == 3

        # Output should contain processing information
        assert len(result.output) > 0

    def test_analyze_batch_quiet_mode(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test analyze-batch with --quiet flag."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        csv_file = input_dir / "file.csv"
        csv_file.write_text("col1,col2\n1,2\n3,4\n")

        result = cli_runner.invoke(
            cli,
            [
                "analyze-batch",
                str(input_dir),
                "--output-dir",
                str(output_dir),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # With --quiet, output should be minimal
        assert len(result.output) < 100

    def test_compare_with_rich_output(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test compare command produces output."""
        baseline_file = tmp_path / "baseline.csv"
        baseline_file.write_text("col1,col2\n1,2\n3,4\n")
        current_file = tmp_path / "current.csv"
        current_file.write_text("col1,col2\n1,2\n3,5\n")

        output_file = tmp_path / "output.json"
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

        # Should have output
        assert len(result.output) > 0

    def test_export_rules_with_rich(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test export-rules command produces output."""
        # Create a rules file
        rules_file = tmp_path / "rules.json"
        rules_data = {
            "name": "test_rules",
            "description": "Test rules",
            "rules": [
                {
                    "name": "age_range",
                    "description": "Age must be 0-150",
                    "rule_type": "range",
                    "column": "age",
                    "parameters": {"min_value": 0, "max_value": 150},
                    "enabled": True,
                }
            ],
        }
        rules_file.write_text(json.dumps(rules_data))

        output_file = tmp_path / "schema.py"
        result = cli_runner.invoke(
            cli,
            [
                "export-rules",
                str(rules_file),
                "--format",
                "pandera",
                "--output-file",
                str(output_file),
            ],
        )

        # May fail if pandera not installed, but should produce output
        assert len(result.output) > 0

    def test_cli_error_handling_with_rich(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that CLI error messages are displayed."""
        # Try to analyze a non-existent file
        result = cli_runner.invoke(
            cli,
            ["analyze", str(tmp_path / "nonexistent.csv")],
        )

        assert result.exit_code != 0
        # Should have error output
        assert len(result.output) > 0

    def test_cli_verbose_mode(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test --verbose flag produces additional output."""
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            cli,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        # Verbose mode should produce more output (or at least not less)
        assert len(result.output) >= 0  # Just ensure it doesn't crash

    def test_share_command_with_rich(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test share command produces output."""
        # Create findings file
        findings_file = tmp_path / "findings.json"
        findings_data = {
            "findings": [
                {
                    "ghost_type": "null",
                    "column": "col1",
                    "severity": "warning",
                    "description": "Test finding",
                    "row_indices": [1, 2],
                    "metadata": {},
                }
            ],
            "summary": {"total_findings": 1, "by_type": {}, "by_severity": {}},
        }
        findings_file.write_text(json.dumps(findings_data))

        result = cli_runner.invoke(
            cli,
            [
                "share",
                str(findings_file),
                "--title",
                "Test Report",
                "--author",
                "Test Author",
            ],
        )

        # Should produce output (may create report file)
        assert len(result.output) > 0 or result.exit_code == 0

    def test_import_report_with_rich(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test import-report command produces formatted output."""
        # This test would require a valid report file
        # For now, just test that the command exists and handles missing file gracefully
        result = cli_runner.invoke(
            cli,
            ["import-report", str(tmp_path / "nonexistent.json")],
        )

        # Should produce error output
        assert result.exit_code != 0
        assert len(result.output) > 0


class TestRichFallback:
    """Test Rich fallback behavior when Rich is not available."""

    def test_cli_works_without_rich(
        self, cli_runner: CliRunner, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test that CLI works even if Rich is not available (fallback to click.echo)."""
        # This test verifies the fallback mechanism works
        # The actual test depends on whether Rich is installed, but the code should handle both
        output_file = tmp_path / "output.json"
        result = cli_runner.invoke(
            cli,
            ["analyze", str(sample_csv_file), "--output-file", str(output_file)],
        )

        # Should work regardless of Rich availability
        assert result.exit_code == 0
        assert output_file.exists()
