"""Coverage aggregation from test results.

This module provides functions to aggregate coverage data
from multiple test results into a single report.
"""

from __future__ import annotations

from statatest.core.models import TestResult
from statatest.coverage.models import CoverageReport


def aggregate_coverage(results: list[TestResult]) -> CoverageReport:
    """Aggregate coverage data from multiple test results.

    Combines coverage hits from all test results into a single
    CoverageReport that tracks which lines were executed.

    Args:
        results: List of TestResult objects with coverage_hits data.

    Returns:
        CoverageReport with aggregated coverage data.
    """
    report = CoverageReport()

    for result in results:
        for filename, lines in result.coverage_hits.items():
            for lineno in lines:
                report.add_hit(filename, lineno)

    return report
