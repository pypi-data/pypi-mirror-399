"""Fixture system for statatest - pytest-like fixtures for Stata tests.

This module provides:
- Fixture: Dataclass representing a fixture definition
- FixtureManager: Manages fixture lifecycle across test runs
- discover_conftest: Find conftest.do files in directory hierarchy
- parse_conftest: Parse conftest.do to extract fixtures
- get_test_fixtures: Extract fixture requirements from test files
"""

from statatest.fixtures.manager import (
    Fixture,
    FixtureManager,
    discover_conftest,
    get_test_fixtures,
    parse_conftest,
)

__all__ = [
    "Fixture",
    "FixtureManager",
    "discover_conftest",
    "get_test_fixtures",
    "parse_conftest",
]
