"""Logging configuration for statatest.

This module provides a centralized logging setup using Python's standard
logging module. It replaces rich.Console for output handling.

Usage:
    from statatest.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Test passed")
    logger.error("Test failed: %s", message)
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified module.

    Args:
        name: Module name, typically __name__.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)


def configure_logging(verbose: bool = False) -> None:
    """Configure root logger for statatest.

    Args:
        verbose: If True, set level to DEBUG. Otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger("statatest")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    """Apply ANSI color to text.

    Args:
        text: Text to colorize.
        color: Color code from Colors class.

    Returns:
        Colorized text string.
    """
    return f"{color}{text}{Colors.RESET}"
