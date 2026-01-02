"""Logging configuration for LavenderTown.

This module provides centralized logging configuration for LavenderTown.
It sets up loggers with appropriate handlers and formatters, and provides
utilities for managing log levels across the package.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Creates or retrieves a logger with the specified name and configures it
    if not already configured. Loggers are configured with a StreamHandler
    that outputs to stderr, using WARNING level by default.

    Args:
        name: Logger name, typically ``__name__`` from the calling module.
            Loggers with the same name share the same instance.

    Returns:
        Configured logging.Logger instance. The logger will have a
        StreamHandler attached (if not already configured), outputting
        to stderr with WARNING level.

    Example:
        Get a logger for a module::

            from lavendertown.logging_config import get_logger

            logger = get_logger(__name__)
            logger.warning("Something went wrong")
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        logger.setLevel(logging.WARNING)  # Default to WARNING level

        # Create console handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.WARNING)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False  # Prevent propagation to root logger

    return logger


def set_log_level(level: int | str) -> None:
    """Set the logging level for all LavenderTown loggers.

    Configures the logging level for the main "lavendertown" logger and all
    its handlers. This affects all loggers in the lavendertown package
    hierarchy.

    Args:
        level: Logging level. Can be a string ("DEBUG", "INFO", "WARNING",
            "ERROR", "CRITICAL") or an integer from the logging module
            (logging.DEBUG, logging.INFO, etc.).

    Example:
        Enable debug logging::

            from lavendertown.logging_config import set_log_level

            set_log_level("DEBUG")
            # Now all lavendertown loggers will output DEBUG messages
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    logger = logging.getLogger("lavendertown")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
