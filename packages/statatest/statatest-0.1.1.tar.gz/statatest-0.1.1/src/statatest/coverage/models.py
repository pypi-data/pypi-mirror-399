"""Data models for coverage tracking.

This module defines data structures for coverage data:
- FileCoverage: Coverage data for a single source file
- CoverageReport: Aggregated coverage across all files
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileCoverage:
    """Coverage data for a single source file.

    Attributes:
        filepath: Path to the source file.
        lines_hit: Set of line numbers that were executed.
        lines_total: Set of all instrumentable line numbers.
    """

    filepath: str
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
        return len(self.lines_hit & self.lines_total) / len(self.lines_total) * 100

    @property
    def lines_covered(self) -> int:
        """Number of lines covered (intersection of hit and total)."""
        return len(self.lines_hit & self.lines_total)

    @property
    def lines_missed(self) -> int:
        """Number of lines not covered."""
        return len(self.lines_total - self.lines_hit)


@dataclass
class CoverageReport:
    """Aggregated coverage report across all files.

    Attributes:
        files: Dictionary mapping filenames to FileCoverage objects.
    """

    files: dict[str, FileCoverage] = field(default_factory=dict)

    def add_hit(self, filename: str, lineno: int) -> None:
        """Record a coverage hit for a file.

        Args:
            filename: Name of the source file.
            lineno: Line number that was executed.
        """
        if filename not in self.files:
            self.files[filename] = FileCoverage(filepath=filename)
        self.files[filename].lines_hit.add(lineno)

    def set_total_lines(self, filename: str, lines: set[int]) -> None:
        """Set the total instrumentable lines for a file.

        Args:
            filename: Name of the source file.
            lines: Set of all line numbers that could be executed.
        """
        if filename not in self.files:
            self.files[filename] = FileCoverage(filepath=filename)
        self.files[filename].lines_total = lines

    @property
    def total_lines(self) -> int:
        """Total number of instrumentable lines across all files."""
        return sum(len(f.lines_total) for f in self.files.values())

    @property
    def covered_lines(self) -> int:
        """Total number of covered lines across all files."""
        return sum(f.lines_covered for f in self.files.values())

    @property
    def coverage_percent(self) -> float:
        """Overall coverage percentage.

        Returns:
            Percentage of lines covered (0-100). Returns 100 if no lines.
        """
        if self.total_lines == 0:
            return 100.0
        return self.covered_lines / self.total_lines * 100
