"""Test executor for statatest.

This module provides the main test execution functionality:
- run_tests: Execute multiple tests
- Orchestrates environment setup, execution, and parsing
"""

from __future__ import annotations

import contextlib
import importlib.resources
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from statatest.core.config import Config
from statatest.core.logging import Colors, colorize
from statatest.core.models import TestFile, TestResult
from statatest.execution.models import StataOutput, TestEnvironment
from statatest.execution.parser import parse_test_output
from statatest.execution.wrapper import create_wrapper_do
from statatest.fixtures import discover_conftest


def run_tests(
    tests: list[TestFile],
    config: Config,
    coverage: bool = False,
    verbose: bool = False,
    instrumented_dir: Path | None = None,
) -> list[TestResult]:
    """Run all discovered tests.

    Args:
        tests: List of test files to execute.
        config: Configuration object.
        coverage: Whether to collect coverage data.
        verbose: Whether to show verbose output.
        instrumented_dir: Path to instrumented source files (for coverage).

    Returns:
        List of TestResult objects.
    """
    results: list[TestResult] = []

    for test in tests:
        if verbose:
            sys.stdout.write(f"Running: {test.relative_path} ")
            sys.stdout.flush()

        result = _run_single_test(test, config, coverage, instrumented_dir)
        results.append(result)

        _print_result(result, verbose)

    if not verbose:
        sys.stdout.write("\n")  # Newline after dots
        sys.stdout.flush()

    return results


def _run_single_test(
    test: TestFile,
    config: Config,
    coverage: bool = False,
    instrumented_dir: Path | None = None,
) -> TestResult:
    """Execute a single test file.

    Orchestrates three phases:
    1. Prepare environment (I/O) - create wrapper files
    2. Execute Stata (I/O) - run subprocess
    3. Parse results (computation) - analyze output

    Args:
        test: TestFile to execute.
        config: Configuration object.
        coverage: Whether to collect coverage data.
        instrumented_dir: Path to instrumented source files (for coverage).

    Returns:
        TestResult with execution details.
    """
    env = _prepare_environment(test, config, coverage, instrumented_dir)

    try:
        output = _execute_stata(test, config, env, coverage)
        return parse_test_output(test, output, coverage)

    except subprocess.TimeoutExpired:
        return TestResult(
            test_file=test.relative_path,
            passed=False,
            duration=0.0,
            rc=-1,
            error_message=f"Test timed out after {config.timeout} seconds",
        )

    except FileNotFoundError:
        return TestResult(
            test_file=test.relative_path,
            passed=False,
            duration=0.0,
            rc=-1,
            error_message=f"Stata executable not found: {config.stata_executable}",
        )

    finally:
        _cleanup_environment(env)


def _prepare_environment(
    test: TestFile,
    config: Config,
    coverage: bool,
    instrumented_dir: Path | None,
) -> TestEnvironment:
    """Prepare temporary files for test execution.

    Args:
        test: TestFile to execute.
        config: Configuration object.
        coverage: Whether coverage collection is enabled.
        instrumented_dir: Path to instrumented source files.

    Returns:
        TestEnvironment with paths to temporary files.
    """
    ado_paths = _get_ado_paths()
    conftest_files = discover_conftest(test.path.parent)

    # Create log file first (needed for wrapper when coverage is enabled)
    log_suffix = ".smcl" if coverage else ".log"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=log_suffix, delete=False
    ) as log_file:
        log_path = Path(log_file.name)

    # Use relative path for test file (we run from test.path.parent)
    # Pass log_path when coverage is enabled so wrapper uses `log using`
    wrapper_content = create_wrapper_do(
        test_path=Path(test.path.name),
        ado_paths=ado_paths,
        conftest_files=conftest_files,
        instrumented_dir=instrumented_dir,
        setup_do=config.setup_do,
        log_path=log_path if coverage else None,
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".do", delete=False
    ) as wrapper_file:
        wrapper_file.write(wrapper_content)
        wrapper_path = Path(wrapper_file.name)

    return TestEnvironment(wrapper_path=wrapper_path, log_path=log_path)


def _execute_stata(
    test: TestFile,
    config: Config,
    env: TestEnvironment,
    coverage: bool,
) -> StataOutput:
    """Execute Stata subprocess.

    Args:
        test: TestFile being executed.
        config: Configuration object.
        env: Test environment with temporary file paths.
        coverage: Whether coverage collection is enabled.

    Returns:
        StataOutput with raw subprocess results.

    Raises:
        subprocess.TimeoutExpired: If test exceeds timeout.
        FileNotFoundError: If Stata executable not found.
    """
    start_time = time.time()
    log_flag = "-s" if coverage else "-b"

    # Stata usage: stata-mp [-h -q -s -b] [filename.do]
    # With -b or -s flags, pass the do-file path directly (not "do filename")
    cmd = [
        config.stata_executable,
        log_flag,
        "-q",
        str(env.wrapper_path),
    ]

    process = subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=config.timeout,
        cwd=test.path.parent,
    )

    duration = time.time() - start_time

    try:
        log_content = env.log_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        log_content = ""

    return StataOutput(
        returncode=process.returncode,
        log_content=log_content,
        stderr=process.stderr,
        duration=duration,
    )


def _cleanup_environment(env: TestEnvironment) -> None:
    """Clean up temporary files.

    Args:
        env: Test environment with paths to clean up.
    """
    for path in [env.log_path, env.wrapper_path]:
        with contextlib.suppress(FileNotFoundError):
            path.unlink()


def _get_ado_paths() -> dict[str, Path]:
    """Get paths to statatest's built-in .ado files.

    Returns:
        Dictionary with 'assertions' and 'fixtures' paths.
    """
    paths: dict[str, Path] = {}

    try:
        files = importlib.resources.files("statatest")
        ado_base = Path(str(files.joinpath("ado")))
        if ado_base.exists():
            for subdir in ["assertions", "fixtures"]:
                subpath = ado_base / subdir
                if subpath.exists():
                    paths[subdir] = subpath
            if paths:
                return paths
    except (TypeError, AttributeError):
        pass

    # Fallback: relative to this module
    module_dir = Path(__file__).parent.parent
    ado_base = module_dir / "ado"
    if ado_base.exists():
        for subdir in ["assertions", "fixtures"]:
            subpath = ado_base / subdir
            if subpath.exists():
                paths[subdir] = subpath

    return paths


def _print_result(result: TestResult, verbose: bool) -> None:
    """Print test result to console.

    Args:
        result: Test result to print.
        verbose: Whether to show verbose output.
    """
    if verbose:
        if result.passed:
            sys.stdout.write(colorize("PASSED", Colors.GREEN))
        else:
            sys.stdout.write(colorize("FAILED", Colors.RED))
        sys.stdout.write(f" ({result.duration:.2f}s)\n")
    elif result.passed:
        sys.stdout.write(colorize(".", Colors.GREEN))
    else:
        sys.stdout.write(colorize("F", Colors.RED))
    sys.stdout.flush()
