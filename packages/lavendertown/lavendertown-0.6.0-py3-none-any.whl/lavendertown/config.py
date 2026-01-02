"""Configuration management for LavenderTown.

This module provides configuration management using environment variables and
`.env` files. It automatically loads `.env` files from common locations and
provides access to configuration values.

Example:
    Configuration is automatically loaded when the package is imported::

        import lavendertown

        # Environment variables are now available
        from lavendertown.config import get_config

        log_level = get_config("LAVENDERTOWN_LOG_LEVEL", "WARNING")
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


def _load_dotenv() -> None:
    """Load .env file from common locations if python-dotenv is available.

    Looks for .env files in the following order:
    1. Current working directory
    2. User's home directory (~/.lavendertown/.env)
    3. Project root (where lavendertown package is located)

    Does nothing if python-dotenv is not installed.
    """
    if not _DOTENV_AVAILABLE:
        return

    # Try current directory first
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)

    # Try user home directory
    home_env = Path.home() / ".lavendertown" / ".env"
    if home_env.exists():
        load_dotenv(dotenv_path=home_env, override=False)

    # Try project root (package parent directory)
    package_root = Path(__file__).parent.parent
    load_dotenv(dotenv_path=package_root / ".env", override=False)


def get_config(key: str, default: str | None = None) -> str | None:
    """Get configuration value from environment variable.

    Args:
        key: Environment variable name to retrieve
        default: Default value to return if key is not set

    Returns:
        Configuration value as string, or default if not set

    Example:
        Get log level with default::

            log_level = get_config("LAVENDERTOWN_LOG_LEVEL", "WARNING")
    """
    return os.getenv(key, default)


def get_config_bool(key: str, default: bool = False) -> bool:
    """Get boolean configuration value from environment variable.

    Converts common truthy values (1, true, yes, on) to True,
    everything else to False.

    Args:
        key: Environment variable name to retrieve
        default: Default value to return if key is not set

    Returns:
        Boolean configuration value
    """
    value = os.getenv(key)
    if value is None:
        return default

    return value.lower() in ("1", "true", "yes", "on")


def get_config_int(key: str, default: int | None = None) -> int | None:
    """Get integer configuration value from environment variable.

    Args:
        key: Environment variable name to retrieve
        default: Default value to return if key is not set or invalid

    Returns:
        Integer configuration value, or default if not set or invalid
    """
    value = os.getenv(key)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


# Supported environment variables
# LAVENDERTOWN_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
# LAVENDERTOWN_OUTPUT_DIR: Default output directory for CLI commands

# Load .env file on module import
_load_dotenv()
