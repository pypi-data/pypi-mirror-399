"""Discovery module - test file discovery and parsing.

This module provides test file discovery functionality:
- finder: Locate test files matching patterns
- parser: Parse test files to extract markers and programs
"""

from statatest.discovery.finder import discover_tests
from statatest.discovery.parser import parse_test_file

__all__ = [
    "discover_tests",
    "parse_test_file",
]
