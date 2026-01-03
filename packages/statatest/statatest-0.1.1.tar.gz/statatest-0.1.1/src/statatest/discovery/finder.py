"""Test file discovery for statatest.

This module provides functionality to locate test files in a project.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from statatest.core.config import Config
from statatest.core.models import TestFile
from statatest.discovery.parser import parse_test_file


def discover_tests(
    path: Path,
    config: Config,
    marker: str | None = None,
    keyword: str | None = None,
) -> list[TestFile]:
    """Discover test files matching configuration patterns.

    Args:
        path: Path to search for tests (file or directory).
        config: Configuration object with test file patterns.
        marker: Optional marker to filter tests (e.g., "unit", "integration").
        keyword: Optional keyword to filter test files by name.

    Returns:
        List of TestFile objects representing discovered tests, sorted by path.
    """
    test_files: list[TestFile] = []

    if path.is_file():
        test_files = _discover_single_file(path, config, marker, keyword)
    else:
        test_files = _discover_directory(path, config, marker, keyword)

    # Sort by path for consistent ordering
    test_files.sort(key=lambda t: t.path)
    return test_files


def _discover_single_file(
    path: Path,
    config: Config,
    marker: str | None,
    keyword: str | None,
) -> list[TestFile]:
    """Discover tests from a single file.

    Args:
        path: Path to the test file.
        config: Configuration object.
        marker: Optional marker filter.
        keyword: Optional keyword filter.

    Returns:
        List containing the TestFile if it matches filters, empty otherwise.
    """
    if not _is_test_file(path, config.test_files):
        return []

    test_file = parse_test_file(path)
    if _matches_filters(test_file, marker, keyword):
        return [test_file]
    return []


def _discover_directory(
    path: Path,
    config: Config,
    marker: str | None,
    keyword: str | None,
) -> list[TestFile]:
    """Discover tests from a directory recursively.

    Args:
        path: Path to the directory.
        config: Configuration object.
        marker: Optional marker filter.
        keyword: Optional keyword filter.

    Returns:
        List of TestFile objects found in the directory.
    """
    test_files: list[TestFile] = []

    for pattern in config.test_files:
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                test_file = parse_test_file(file_path)
                if _matches_filters(test_file, marker, keyword):
                    test_files.append(test_file)

    return test_files


def _is_test_file(path: Path, patterns: list[str]) -> bool:
    """Check if path matches any test file pattern.

    Args:
        path: Path to check.
        patterns: List of glob patterns (e.g., ["test_*.do"]).

    Returns:
        True if the path matches any pattern.
    """
    return any(fnmatch(path.name, pattern) for pattern in patterns)


def _matches_filters(
    test_file: TestFile,
    marker: str | None,
    keyword: str | None,
) -> bool:
    """Check if test file matches the specified filters.

    Args:
        test_file: TestFile to check.
        marker: Marker that must be present (case-insensitive).
        keyword: Keyword that must be in the filename (case-insensitive).

    Returns:
        True if the test file matches all specified filters.
    """
    if marker and marker.lower() not in test_file.markers:
        return False

    return not (keyword and keyword.lower() not in test_file.name.lower())
