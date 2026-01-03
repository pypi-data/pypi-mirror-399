"""Core module - domain entities, configuration, and constants.

This module contains the foundational components used across statatest:
- models: Domain entities (TestFile, TestResult, TestSuite, CoverageData)
- config: Configuration dataclasses and loading
- constants: Magic numbers and default values
"""

from statatest.core.config import Config
from statatest.core.constants import (
    COVERAGE_HIGH_THRESHOLD,
    COVERAGE_MEDIUM_THRESHOLD,
    DEFAULT_STATA_EXECUTABLE,
    DEFAULT_TEST_FILE_PATTERNS,
    DEFAULT_TEST_PATHS,
    DEFAULT_TIMEOUT_SECONDS,
    ERROR_MESSAGE_MAX_LENGTH,
)
from statatest.core.models import CoverageData, TestFile, TestResult, TestSuite

__all__ = [
    "COVERAGE_HIGH_THRESHOLD",
    "COVERAGE_MEDIUM_THRESHOLD",
    "DEFAULT_STATA_EXECUTABLE",
    "DEFAULT_TEST_FILE_PATTERNS",
    "DEFAULT_TEST_PATHS",
    "DEFAULT_TIMEOUT_SECONDS",
    "ERROR_MESSAGE_MAX_LENGTH",
    "Config",
    "CoverageData",
    "TestFile",
    "TestResult",
    "TestSuite",
]
