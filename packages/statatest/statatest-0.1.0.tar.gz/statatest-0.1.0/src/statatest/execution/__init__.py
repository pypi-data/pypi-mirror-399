"""Execution module - test execution via Stata subprocess.

This module provides test execution functionality:
- executor: Run tests via Stata subprocess
- wrapper: Generate wrapper .do files
- parser: Parse Stata output and logs
"""

from statatest.execution.executor import run_tests
from statatest.execution.models import StataOutput, TestEnvironment
from statatest.execution.parser import parse_test_output
from statatest.execution.wrapper import create_wrapper_do

__all__ = [
    "StataOutput",
    "TestEnvironment",
    "create_wrapper_do",
    "parse_test_output",
    "run_tests",
]
