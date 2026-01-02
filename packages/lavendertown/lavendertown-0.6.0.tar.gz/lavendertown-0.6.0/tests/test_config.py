"""Tests for configuration management (python-dotenv integration)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from lavendertown import config


class TestConfigModule:
    """Test configuration module functionality."""

    def test_get_config_existing(self) -> None:
        """Test getting existing environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            assert config.get_config("TEST_VAR") == "test_value"

    def test_get_config_missing_with_default(self) -> None:
        """Test getting missing environment variable with default."""
        with patch.dict(os.environ, {}, clear=True):
            assert config.get_config("MISSING_VAR", "default") == "default"

    def test_get_config_missing_no_default(self) -> None:
        """Test getting missing environment variable without default."""
        with patch.dict(os.environ, {}, clear=True):
            assert config.get_config("MISSING_VAR") is None

    def test_get_config_bool_true_values(self) -> None:
        """Test getting boolean config with truthy values."""
        for true_value in (
            "1",
            "true",
            "True",
            "TRUE",
            "yes",
            "Yes",
            "YES",
            "on",
            "On",
            "ON",
        ):
            with patch.dict(os.environ, {"TEST_BOOL": true_value}):
                assert config.get_config_bool("TEST_BOOL") is True

    def test_get_config_bool_false_values(self) -> None:
        """Test getting boolean config with falsy values."""
        for false_value in ("0", "false", "False", "no", "off", "anything_else"):
            with patch.dict(os.environ, {"TEST_BOOL": false_value}):
                assert config.get_config_bool("TEST_BOOL") is False

    def test_get_config_bool_missing_with_default(self) -> None:
        """Test getting boolean config with missing value and default."""
        with patch.dict(os.environ, {}, clear=True):
            assert config.get_config_bool("MISSING_BOOL", True) is True
            assert config.get_config_bool("MISSING_BOOL", False) is False

    def test_get_config_int_valid(self) -> None:
        """Test getting integer config with valid value."""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            assert config.get_config_int("TEST_INT") == 42

    def test_get_config_int_invalid(self) -> None:
        """Test getting integer config with invalid value."""
        with patch.dict(os.environ, {"TEST_INT": "not_a_number"}):
            assert config.get_config_int("TEST_INT") is None

    def test_get_config_int_missing_with_default(self) -> None:
        """Test getting integer config with missing value and default."""
        with patch.dict(os.environ, {}, clear=True):
            assert config.get_config_int("MISSING_INT", 100) == 100
            assert config.get_config_int("MISSING_INT") is None

    def test_get_config_int_negative(self) -> None:
        """Test getting negative integer config."""
        with patch.dict(os.environ, {"TEST_INT": "-42"}):
            assert config.get_config_int("TEST_INT") == -42

    def test_dotenv_loading_graceful_fallback(self) -> None:
        """Test that dotenv loading gracefully handles missing python-dotenv."""
        # This should not raise an error even if dotenv is not available
        # The module should handle the ImportError gracefully
        assert hasattr(config, "_load_dotenv")
        # Calling it should not raise
        config._load_dotenv()


class TestDotenvIntegration:
    """Test python-dotenv integration when available."""

    @pytest.mark.skipif(
        not hasattr(config, "_DOTENV_AVAILABLE")
        or not getattr(config, "_DOTENV_AVAILABLE", False),
        reason="python-dotenv not available",
    )
    def test_load_dotenv_from_current_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading .env file from current directory."""
        # Create a .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=from_env_file\n")

        # Change to the temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            monkeypatch.delenv("TEST_VAR", raising=False)
            config._load_dotenv()
            # After loading, the variable should be available
            assert os.getenv("TEST_VAR") == "from_env_file"
        finally:
            os.chdir(original_cwd)

    @pytest.mark.skipif(
        not hasattr(config, "_DOTENV_AVAILABLE")
        or not getattr(config, "_DOTENV_AVAILABLE", False),
        reason="python-dotenv not available",
    )
    def test_load_dotenv_override_false(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that dotenv doesn't override existing environment variables."""
        # Set an existing env var
        monkeypatch.setenv("EXISTING_VAR", "existing_value")

        # Create .env file with same variable
        env_file = tmp_path / ".env"
        env_file.write_text("EXISTING_VAR=from_env_file\n")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config._load_dotenv()
            # Existing value should not be overridden
            assert os.getenv("EXISTING_VAR") == "existing_value"
        finally:
            os.chdir(original_cwd)
