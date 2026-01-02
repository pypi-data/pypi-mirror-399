"""Integration tests for Phase 5 features."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from lavendertown import config
from lavendertown.cli import cli
from lavendertown.export.json import export_to_json, export_to_json_file
from lavendertown.models import GhostFinding


class TestPhase5Integration:
    """Integration tests for Phase 5 features working together."""

    @pytest.fixture
    def sample_findings(self) -> list[GhostFinding]:
        """Create sample findings for testing."""
        return [
            GhostFinding(
                ghost_type="null",
                column="col1",
                severity="warning",
                description="Test finding",
                row_indices=[1, 2],
                metadata={},
            )
        ]

    @pytest.fixture
    def sample_csv_file(self, tmp_path: Path) -> Path:
        """Create a sample CSV file."""
        csv_file = tmp_path / "sample.csv"
        csv_file.write_text("col1,col2\n1,2\n3,4\n")
        return csv_file

    def test_config_and_cli_integration(
        self, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test that config module works with CLI."""
        # Set config via environment variable
        with patch.dict(os.environ, {"LAVENDERTOWN_LOG_LEVEL": "DEBUG"}):
            log_level = config.get_config("LAVENDERTOWN_LOG_LEVEL", "WARNING")
            assert log_level == "DEBUG"

            # CLI should still work
            runner = CliRunner()
            output_file = tmp_path / "output.json"
            result = runner.invoke(
                cli,
                ["analyze", str(sample_csv_file), "--output-file", str(output_file)],
            )
            assert result.exit_code == 0

    def test_orjson_and_export_integration(
        self, sample_findings: list[GhostFinding], tmp_path: Path
    ) -> None:
        """Test that orjson integration works with export functions."""
        # Test export_to_json
        json_str = export_to_json(sample_findings, indent=2)
        data = json.loads(json_str)
        assert len(data["findings"]) == 1

        # Test export_to_json_file
        filepath = tmp_path / "findings.json"
        export_to_json_file(sample_findings, str(filepath), indent=2)
        assert filepath.exists()

        # Verify file contents
        with open(filepath) as f:
            file_data = json.load(f)
        assert len(file_data["findings"]) == 1

    def test_cli_with_orjson_export(
        self, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test CLI uses orjson for JSON export when available."""
        runner = CliRunner()
        output_file = tmp_path / "output.json"
        result = runner.invoke(
            cli,
            [
                "analyze",
                str(sample_csv_file),
                "--output-file",
                str(output_file),
                "--output-format",
                "json",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        assert "findings" in data
        assert "summary" in data

    def test_rich_cli_with_config(self, sample_csv_file: Path, tmp_path: Path) -> None:
        """Test Rich CLI output with configuration."""
        runner = CliRunner()
        output_file = tmp_path / "output.json"

        # CLI should work with or without Rich
        result = runner.invoke(
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
        assert output_file.exists()

    def test_all_phase5_features_together(
        self, sample_csv_file: Path, tmp_path: Path
    ) -> None:
        """Test all Phase 5 features working together."""
        # Set config
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            config_value = config.get_config("TEST_VAR")
            assert config_value == "test_value"

            # Use CLI (which uses Rich if available)
            runner = CliRunner()
            output_file = tmp_path / "output.json"
            result = runner.invoke(
                cli,
                ["analyze", str(sample_csv_file), "--output-file", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify export (uses orjson if available)
            with open(output_file) as f:
                data = json.load(f)
            assert "findings" in data
