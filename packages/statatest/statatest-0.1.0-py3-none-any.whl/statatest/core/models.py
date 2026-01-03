"""Domain models for statatest.

This module defines the core data structures used throughout statatest:
- TestFile: Represents a discovered test file
- TestResult: Result of executing a single test
- TestSuite: Collection of test results
- CoverageData: Coverage information for a source file
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestFile:
    """Represents a test file to be executed.

    Attributes:
        path: Absolute path to the test file.
        markers: List of markers extracted from the file (e.g., "unit", "slow").
        programs: List of test program names defined in the file.
    """

    path: Path
    markers: list[str] = field(default_factory=list)
    programs: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Return the file name without extension."""
        return self.path.stem

    @property
    def relative_path(self) -> str:
        """Return path relative to current working directory.

        Returns:
            Relative path string, or absolute path if not relative to cwd.
        """
        try:
            return str(self.path.relative_to(Path.cwd()))
        except ValueError:
            return str(self.path)


@dataclass
class TestResult:
    """Result of running a single test file.

    Attributes:
        test_file: Path to the test file (relative).
        passed: Whether the test passed.
        duration: Execution time in seconds.
        rc: Stata return code.
        stdout: Standard output (log content).
        stderr: Standard error output.
        error_message: Human-readable error message if failed.
        assertions_passed: Number of passed assertions.
        assertions_failed: Number of failed assertions.
        coverage_hits: Dictionary mapping source files to hit line numbers.
    """

    test_file: str
    passed: bool
    duration: float
    rc: int = 0
    stdout: str = ""
    stderr: str = ""
    error_message: str = ""
    assertions_passed: int = 0
    assertions_failed: int = 0
    coverage_hits: dict[str, set[int]] = field(default_factory=dict)


@dataclass
class CoverageData:
    """Coverage data for a single source file.

    Attributes:
        file_path: Path to the source file.
        lines_hit: Set of line numbers that were executed.
        lines_total: Set of all instrumentable line numbers.
    """

    file_path: str
    lines_hit: set[int] = field(default_factory=set)
    lines_total: set[int] = field(default_factory=set)

    @property
    def coverage_percent(self) -> float:
        """Calculate coverage percentage.

        Returns:
            Percentage of lines covered (0-100). Returns 100 if no lines.
        """
        if not self.lines_total:
            return 100.0
        return len(self.lines_hit) / len(self.lines_total) * 100


@dataclass
class TestSuite:
    """Collection of test results for a suite.

    Attributes:
        name: Name of the test suite.
        tests: List of TestResult objects.
    """

    name: str
    tests: list[TestResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of tests in the suite."""
        return len(self.tests)

    @property
    def passed(self) -> int:
        """Number of passed tests."""
        return sum(1 for t in self.tests if t.passed)

    @property
    def failed(self) -> int:
        """Number of failed tests."""
        return sum(1 for t in self.tests if not t.passed)

    @property
    def total_time(self) -> float:
        """Total execution time in seconds."""
        return sum(t.duration for t in self.tests)
