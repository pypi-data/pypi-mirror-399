"""Coverage report generation.

This module provides functions to generate coverage reports in
various formats (LCOV, HTML).
"""

from __future__ import annotations

from pathlib import Path

from statatest.core.constants import COVERAGE_HIGH_THRESHOLD, COVERAGE_MEDIUM_THRESHOLD
from statatest.core.models import TestResult
from statatest.coverage.aggregator import aggregate_coverage
from statatest.coverage.models import CoverageReport


def generate_lcov(results: list[TestResult], output_path: Path) -> None:
    """Generate LCOV coverage report.

    LCOV format is widely supported by CI tools like Codecov.

    Args:
        results: List of TestResult objects with coverage data.
        output_path: Path to write the LCOV file.
    """
    coverage = aggregate_coverage(results)
    lines = _build_lcov_content(coverage)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_html(results: list[TestResult], output_dir: Path) -> None:
    """Generate HTML coverage report.

    Creates an index.html with coverage summary table.

    Args:
        results: List of TestResult objects with coverage data.
        output_dir: Directory to write HTML files.
    """
    coverage = aggregate_coverage(results)
    html_content = _build_html_content(coverage)

    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.html"
    index_path.write_text("\n".join(html_content), encoding="utf-8")


def _build_lcov_content(coverage: CoverageReport) -> list[str]:
    """Build LCOV file content.

    Args:
        coverage: CoverageReport with aggregated data.

    Returns:
        List of lines for LCOV file.
    """
    lines: list[str] = ["TN:statatest"]

    for filename, file_cov in sorted(coverage.files.items()):
        lines.append(f"SF:{filename}")

        # Write all hit lines
        lines.extend(f"DA:{lineno},1" for lineno in sorted(file_cov.lines_hit))

        # Summary
        total = len(file_cov.lines_total) or len(file_cov.lines_hit)
        lines.append(f"LF:{total}")
        lines.append(f"LH:{len(file_cov.lines_hit)}")
        lines.append("end_of_record")

    return lines


def _build_html_content(coverage: CoverageReport) -> list[str]:
    """Build HTML coverage report content.

    Args:
        coverage: CoverageReport with aggregated data.

    Returns:
        List of lines for HTML file.
    """
    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>statatest Coverage Report</title>",
        "<style>",
        "body { font-family: sans-serif; margin: 20px; }",
        "table { border-collapse: collapse; width: 100%; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #4CAF50; color: white; }",
        "tr:nth-child(even) { background-color: #f2f2f2; }",
        ".high { color: green; }",
        ".medium { color: orange; }",
        ".low { color: red; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>statatest Coverage Report</h1>",
        f"<p>Overall coverage: <strong>{coverage.coverage_percent:.1f}%</strong></p>",
        "<table>",
        "<tr><th>File</th><th>Lines</th><th>Covered</th><th>Coverage</th></tr>",
    ]

    for filename, file_cov in sorted(coverage.files.items()):
        pct = file_cov.coverage_percent
        css_class = _get_coverage_class(pct)
        total = len(file_cov.lines_total) or len(file_cov.lines_hit)
        covered = len(file_cov.lines_hit)
        lines.append(
            f"<tr><td>{filename}</td><td>{total}</td><td>{covered}</td>"
            f"<td class='{css_class}'>{pct:.1f}%</td></tr>"
        )

    lines.extend(["</table>", "</body>", "</html>"])
    return lines


def _get_coverage_class(percent: float) -> str:
    """Get CSS class for coverage percentage.

    Args:
        percent: Coverage percentage (0-100).

    Returns:
        CSS class name ("high", "medium", or "low").
    """
    if percent >= COVERAGE_HIGH_THRESHOLD:
        return "high"
    if percent >= COVERAGE_MEDIUM_THRESHOLD:
        return "medium"
    return "low"
