"""Stata output parsing for test results.

This module parses Stata log output to extract:
- Assertion pass/fail counts
- Error messages
- Coverage markers
"""

from __future__ import annotations

import re

from statatest.core.constants import (
    ERROR_MESSAGE_MAX_LENGTH,
    PATTERN_ASSERTION_FAILED,
    PATTERN_ASSERTION_PASSED,
    PATTERN_COVERAGE_MARKER,
)
from statatest.core.models import TestFile, TestResult
from statatest.execution.models import StataOutput

# Compiled regex patterns for performance
_PASS_PATTERN = re.compile(PATTERN_ASSERTION_PASSED)
_FAIL_PATTERN = re.compile(PATTERN_ASSERTION_FAILED)
_COVERAGE_PATTERN = re.compile(PATTERN_COVERAGE_MARKER)

# Error patterns for message extraction
_ERROR_PATTERNS = (
    re.compile(r"r\((\d+)\);"),  # Stata return codes
    re.compile(r"assertion is false", re.IGNORECASE),  # Assert failures
    re.compile(r"^error:?\s*(.+)$", re.MULTILINE | re.IGNORECASE),  # Generic errors
)


def parse_test_output(
    test: TestFile,
    output: StataOutput,
    coverage: bool,
) -> TestResult:
    """Parse Stata output into TestResult.

    This is a pure function with no I/O - only string parsing.

    Args:
        test: TestFile that was executed.
        output: Raw output from Stata subprocess.
        coverage: Whether to parse coverage markers.

    Returns:
        TestResult with parsed execution details.
    """
    passed = output.returncode == 0
    assertions_passed, assertions_failed = _count_assertions(output.log_content)

    if assertions_failed > 0:
        passed = False

    error_message = ""
    if not passed:
        error_message = extract_error_message(output.log_content, output.stderr)

    coverage_hits: dict[str, set[int]] = {}
    if coverage:
        coverage_hits = parse_coverage_markers(output.log_content)

    return TestResult(
        test_file=test.relative_path,
        passed=passed,
        duration=output.duration,
        rc=output.returncode,
        stdout=output.log_content,
        stderr=output.stderr,
        error_message=error_message,
        assertions_passed=assertions_passed,
        assertions_failed=assertions_failed,
        coverage_hits=coverage_hits,
    )


def _count_assertions(log_content: str) -> tuple[int, int]:
    """Count passed and failed assertions in log output.

    Args:
        log_content: Stata log file content.

    Returns:
        Tuple of (passed_count, failed_count).
    """
    passed = len(_PASS_PATTERN.findall(log_content))
    failed = len(_FAIL_PATTERN.findall(log_content))
    return passed, failed


def extract_error_message(log_content: str, stderr: str) -> str:
    """Extract error message from Stata output.

    Tries multiple patterns to find a meaningful error message.

    Args:
        log_content: Stata log file content.
        stderr: Standard error output.

    Returns:
        Human-readable error message.
    """
    # Try each error pattern
    for pattern in _ERROR_PATTERNS:
        match = pattern.search(log_content)
        if match:
            return match.group(0)

    # Fall back to stderr (truncated)
    if stderr.strip():
        return stderr.strip()[:ERROR_MESSAGE_MAX_LENGTH]

    # Generic failure message
    return "Test failed (check log for details)"


def parse_coverage_markers(smcl_content: str) -> dict[str, set[int]]:
    """Extract coverage hits from SMCL log file.

    Coverage markers are invisible SMCL comments in the format:
        {* COV:filename.ado:lineno }

    Args:
        smcl_content: Raw SMCL log content.

    Returns:
        Dictionary mapping filenames to sets of line numbers hit.
    """
    hits: dict[str, set[int]] = {}

    for match in _COVERAGE_PATTERN.finditer(smcl_content):
        filename, lineno = match.group(1), int(match.group(2))
        if filename not in hits:
            hits[filename] = set()
        hits[filename].add(lineno)

    return hits
