"""Fixture system for statatest - pytest-like fixtures for Stata tests."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from statatest.core.models import TestFile


@dataclass(slots=True)
class Fixture:
    """Represents a fixture definition."""

    name: str
    scope: str = "function"  # function, module, session
    setup_program: str = ""
    teardown_program: str = ""
    source_file: Path | None = None


@dataclass(slots=True)
class FixtureManager:
    """Manages fixture lifecycle across test runs."""

    fixtures: dict[str, Fixture] = field(default_factory=dict)
    active_fixtures: dict[str, str] = field(default_factory=dict)  # name -> scope

    def register_fixture(self, fixture: Fixture) -> None:
        """Register a fixture definition."""
        self.fixtures[fixture.name] = fixture

    def get_fixture(self, name: str) -> Fixture | None:
        """Get a fixture by name."""
        return self.fixtures.get(name)

    def is_active(self, name: str) -> bool:
        """Check if a fixture is currently active."""
        return name in self.active_fixtures

    def activate(self, name: str, scope: str) -> None:
        """Mark a fixture as active."""
        self.active_fixtures[name] = scope

    def deactivate(self, name: str) -> None:
        """Mark a fixture as inactive."""
        self.active_fixtures.pop(name, None)

    def get_teardown_list(self, scope: str) -> list[str]:
        """Get list of fixtures to teardown for a given scope.

        Args:
            scope: The scope level (function, module, session)

        Returns:
            List of fixture names to teardown
        """
        return [
            name
            for name, fixture_scope in self.active_fixtures.items()
            if fixture_scope == scope
        ]


def discover_conftest(test_dir: Path) -> list[Path]:
    """Find all conftest.do files in directory hierarchy.

    Searches from test_dir up to the root, collecting conftest.do files.
    Files closer to the test take precedence (loaded last).

    Args:
        test_dir: Directory containing tests

    Returns:
        List of conftest.do paths, from root to test_dir
    """
    conftest_files: list[Path] = []

    # Walk up from test_dir to root
    current = test_dir.resolve()
    while current != current.parent:
        conftest = current / "conftest.do"
        if conftest.exists():
            conftest_files.append(conftest)
        current = current.parent

    # Reverse so root comes first (will be loaded first)
    conftest_files.reverse()
    return conftest_files


def parse_conftest(conftest_path: Path) -> list[Fixture]:
    """Parse a conftest.do file to extract fixture definitions.

    Looks for programs named fixture_* (but not fixture_*_teardown).

    Args:
        conftest_path: Path to conftest.do file

    Returns:
        List of Fixture objects found
    """
    content = conftest_path.read_text(encoding="utf-8")

    # Find all fixture_* programs
    fixture_pattern = re.compile(
        r"program\s+define\s+fixture_(\w+)",
        re.IGNORECASE | re.MULTILINE,
    )

    # Collect all fixture names (including teardown)
    all_names = [match.group(1) for match in fixture_pattern.finditer(content)]

    # Filter out teardown programs and create fixtures
    fixtures: list[Fixture] = []
    for name in all_names:
        # Skip if this is a teardown program
        if name.endswith("_teardown"):
            continue

        setup_prog = f"fixture_{name}"
        teardown_prog = f"fixture_{name}_teardown"

        # Check if teardown exists
        has_teardown = f"{name}_teardown" in all_names

        fixtures.append(
            Fixture(
                name=name,
                setup_program=setup_prog,
                teardown_program=teardown_prog if has_teardown else "",
                source_file=conftest_path,
            )
        )

    return fixtures


def get_test_fixtures(test: TestFile) -> list[str]:
    """Extract fixture requirements from a test file.

    Looks for @uses_fixture comments or use_fixture calls.

    Args:
        test: TestFile to analyze

    Returns:
        List of fixture names required by the test
    """
    content = test.path.read_text(encoding="utf-8")

    fixtures: set[str] = set()

    # Pattern: // @uses_fixture: name or // @uses_fixture: name1, name2
    comment_pattern = re.compile(
        r"//\s*@uses_fixture:\s*(\w+(?:\s*,\s*\w+)*)",
        re.IGNORECASE,
    )
    for match in comment_pattern.finditer(content):
        names = match.group(1)
        for name in re.split(r"\s*,\s*", names):
            fixtures.add(name.strip())

    # Pattern: use_fixture name
    call_pattern = re.compile(
        r"use_fixture\s+(\w+)",
        re.IGNORECASE,
    )
    for match in call_pattern.finditer(content):
        fixtures.add(match.group(1))

    return list(fixtures)
