"""statatest - Pytest-inspired testing and code coverage framework for Stata."""

__version__ = "0.1.0"
__author__ = "Jose Ignacio Gonzalez Rojas"
__email__ = "j.i.gonzalez-rojas@lse.ac.uk"

from statatest.core.config import Config
from statatest.discovery import discover_tests
from statatest.execution import run_tests

__all__ = ["Config", "__version__", "discover_tests", "run_tests"]
