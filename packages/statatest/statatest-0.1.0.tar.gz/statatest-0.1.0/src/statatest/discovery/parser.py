"""Test file parsing for statatest.

This module provides functionality to parse test files and extract metadata:
- Markers (e.g., @marker: unit)
- Program definitions (e.g., program define test_something)
"""

from __future__ import annotations

import re
from pathlib import Path

from statatest.core.constants import PATTERN_MARKER, PATTERN_PROGRAM
from statatest.core.models import TestFile

# Compiled regex patterns for performance
_MARKER_PATTERN = re.compile(PATTERN_MARKER, re.IGNORECASE)
_PROGRAM_PATTERN = re.compile(PATTERN_PROGRAM, re.MULTILINE | re.IGNORECASE)


def parse_test_file(path: Path) -> TestFile:
    """Parse a test file to extract markers and program definitions.

    Markers are extracted from comments like:
        // @marker: unit
        // @marker: slow

    Programs are extracted from:
        program define test_something
        program test_something

    Args:
        path: Path to the test file.

    Returns:
        TestFile with extracted markers and programs.
    """
    content = _read_file_content(path)
    markers = _extract_markers(content)
    programs = _extract_programs(content)

    return TestFile(path=path, markers=markers, programs=programs)


def _read_file_content(path: Path) -> str:
    """Read file content, handling encoding issues.

    Tries UTF-8 first, falls back to Latin-1 for legacy Stata files.

    Args:
        path: Path to the file.

    Returns:
        File content as string.
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _extract_markers(content: str) -> list[str]:
    """Extract markers from test file content.

    Args:
        content: File content string.

    Returns:
        List of marker names (lowercase).
    """
    return [match.group(1).lower() for match in _MARKER_PATTERN.finditer(content)]


def _extract_programs(content: str) -> list[str]:
    """Extract test program definitions from content.

    Only programs starting with "test_" are included.

    Args:
        content: File content string.

    Returns:
        List of test program names.
    """
    programs: list[str] = []
    for match in _PROGRAM_PATTERN.finditer(content):
        name = match.group(1)
        if name.startswith("test_"):
            programs.append(name)
    return programs
