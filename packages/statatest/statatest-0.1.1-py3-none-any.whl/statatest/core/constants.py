"""Constants and configuration defaults for statatest.

This module centralizes all magic numbers and default values to:
1. Make them easy to find and modify
2. Prevent duplication across modules
3. Enable configuration override in the future

All constants follow UPPER_SNAKE_CASE naming convention per Google style guide.
"""

from __future__ import annotations

# =============================================================================
# Test Execution
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: int = 300
"""Default timeout for a single test file in seconds."""

DEFAULT_STATA_EXECUTABLE: str = "stata-mp"
"""Default Stata executable name."""

# =============================================================================
# Coverage Thresholds
# =============================================================================

COVERAGE_HIGH_THRESHOLD: int = 80
"""Coverage percentage considered "high" (green in reports)."""

COVERAGE_MEDIUM_THRESHOLD: int = 50
"""Coverage percentage considered "medium" (yellow in reports)."""

# =============================================================================
# Test Discovery
# =============================================================================

DEFAULT_TEST_PATHS: tuple[str, ...] = ("tests",)
"""Default paths to search for tests."""

DEFAULT_TEST_FILE_PATTERNS: tuple[str, ...] = ("test_*.do",)
"""Default patterns for test file names."""

# =============================================================================
# Output Markers (for parsing test results)
# =============================================================================

ASSERTION_PASSED_PREFIX: str = "_STATATEST_PASS_:"
"""Marker prefix for passed assertions in Stata output."""

ASSERTION_PASSED_SUFFIX: str = "_"
"""Marker suffix for passed assertions in Stata output."""

ASSERTION_FAILED_PREFIX: str = "_STATATEST_FAIL_:"
"""Marker prefix for failed assertions in Stata output."""

ASSERTION_FAILED_SUFFIX: str = "_END_"
"""Marker suffix for failed assertions in Stata output."""

# =============================================================================
# Coverage Markers (for SMCL log parsing)
# =============================================================================

COVERAGE_MARKER_FORMAT: str = "{{* COV:{filename}:{lineno} }}"
"""SMCL comment format for coverage markers. Format: {* COV:filename:lineno }."""

# =============================================================================
# Report Defaults
# =============================================================================

DEFAULT_LCOV_FILENAME: str = "coverage.lcov"
"""Default LCOV output filename."""

DEFAULT_HTML_COV_DIR: str = "htmlcov"
"""Default HTML coverage output directory."""

DEFAULT_JUNIT_FILENAME: str = "junit.xml"
"""Default JUnit XML output filename."""

# =============================================================================
# Truncation Limits
# =============================================================================

ERROR_MESSAGE_MAX_LENGTH: int = 200
"""Maximum length for error messages in characters."""

JUNIT_STDOUT_MAX_LENGTH: int = 5000
"""Maximum length for stdout in JUnit XML reports."""

JUNIT_STDERR_MAX_LENGTH: int = 2000
"""Maximum length for stderr in JUnit XML reports."""

JUNIT_FAILURE_MAX_LENGTH: int = 2000
"""Maximum length for failure messages in JUnit XML reports."""

# =============================================================================
# Regex Patterns (as strings - compile at import time in modules)
# =============================================================================

# Test output parsing patterns
PATTERN_ASSERTION_PASSED: str = r"_STATATEST_PASS_:(\w+)_"
"""Regex pattern for parsing passed assertion markers."""

PATTERN_ASSERTION_FAILED: str = r"_STATATEST_FAIL_:(\w+)_:(.+?)_END_"
"""Regex pattern for parsing failed assertion markers."""

PATTERN_COVERAGE_MARKER: str = r"\{\*\s*COV:([^:]+):(\d+)\s*\}"
"""Regex pattern for parsing SMCL coverage markers."""

# Test discovery patterns
PATTERN_MARKER: str = r"//\s*@marker:\s*(\w+)"
"""Regex pattern for parsing @marker: annotations."""

PATTERN_PROGRAM: str = r"^\s*program\s+(?:define\s+)?(\w+)"
"""Regex pattern for parsing Stata program definitions."""

# =============================================================================
# Instrumentation Skip Patterns
# =============================================================================

INSTRUMENT_SKIP_PATTERNS: tuple[str, ...] = (
    r"^\s*$",  # Empty lines
    r"^\s*\*",  # Comment lines
    r"^\s*//",  # Comment lines
    r"^\s*/\*",  # Block comment start
    r"^\s*\*/",  # Block comment end
    r"^\s*program\s+define\s+",  # Program definition
    r"^\s*program\s+drop\s+",  # Program drop
    r"^\s*end\s*$",  # Program end
    r"^\s*version\s+",  # Version statement
    r"^\s*syntax\s+",  # Syntax statement
    r"^\s*args\s+",  # Args statement
    r"^\s*marksample\s+",  # Marksample
    r"^\s*mata\s*:",  # Mata start
    r"^\s*mata\s*$",  # Mata start
    r"^\s*end\s+mata",  # Mata end
    r"^\s*\{",  # Block start
    r"^\s*\}",  # Block end
)
"""Lines matching these patterns should NOT be instrumented for coverage."""

INSTRUMENT_SKIP_KEYWORDS: frozenset[str] = frozenset({"}", "else", "else {"})
"""Keywords that should not be instrumented (after stripping)."""
