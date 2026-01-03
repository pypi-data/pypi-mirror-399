"""Coverage module - instrumentation, collection, aggregation, and reporting.

This module provides coverage functionality:
- instrument: Source code instrumentation with SMCL markers
- models: FileCoverage and CoverageReport data classes
- aggregator: Aggregate coverage from test results
- reporter: Generate LCOV and HTML reports
"""

from statatest.coverage.aggregator import aggregate_coverage
from statatest.coverage.instrument import (
    cleanup_instrumented_environment,
    get_total_lines,
    instrument_directory,
    instrument_file,
    setup_instrumented_environment,
    should_instrument_line,
)
from statatest.coverage.models import CoverageReport, FileCoverage
from statatest.coverage.reporter import generate_html, generate_lcov

__all__ = [
    "CoverageReport",
    "FileCoverage",
    "aggregate_coverage",
    "cleanup_instrumented_environment",
    "generate_html",
    "generate_lcov",
    "get_total_lines",
    "instrument_directory",
    "instrument_file",
    "setup_instrumented_environment",
    "should_instrument_line",
]
