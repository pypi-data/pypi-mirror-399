"""Reporting module - test result output generation.

This module provides report generation functionality:
- junit: JUnit XML reports for CI systems
"""

from statatest.reporting.junit import write_junit_xml

__all__ = [
    "write_junit_xml",
]
