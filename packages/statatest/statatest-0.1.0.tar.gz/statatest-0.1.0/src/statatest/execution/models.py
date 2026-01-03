"""Data models for test execution.

These models are internal to the execution module and represent
intermediate state during test execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestEnvironment:
    """Temporary files created for test execution.

    Attributes:
        wrapper_path: Path to the generated wrapper .do file.
        log_path: Path to the Stata log file.
    """

    wrapper_path: Path
    log_path: Path


@dataclass
class StataOutput:
    """Raw output from Stata subprocess.

    Attributes:
        returncode: Stata return code (0 = success).
        log_content: Content of the log file.
        stderr: Standard error output.
        duration: Execution time in seconds.
    """

    returncode: int
    log_content: str
    stderr: str
    duration: float
