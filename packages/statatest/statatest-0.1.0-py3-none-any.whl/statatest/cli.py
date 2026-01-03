"""Command-line interface for statatest.

This module provides the CLI entry point. It follows the Controller pattern:
- Parse arguments
- Delegate to services (discovery, execution, reporting)
- Handle exit codes
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click

from statatest import __version__
from statatest.core.config import Config
from statatest.core.logging import Colors, colorize, configure_logging
from statatest.coverage.instrument import (
    cleanup_instrumented_environment,
    setup_instrumented_environment,
)
from statatest.coverage.reporter import generate_html, generate_lcov
from statatest.discovery import discover_tests
from statatest.execution import run_tests
from statatest.reporting import write_junit_xml

if TYPE_CHECKING:
    from statatest.core.models import TestFile, TestResult


def _setup_coverage(
    config: Config, verbose: bool
) -> tuple[Path | None, dict[str, dict[int, int]]]:
    """Set up coverage instrumentation if source directories are configured.

    Args:
        config: Configuration object with coverage_source paths.
        verbose: Whether to print verbose output.

    Returns:
        Tuple of (instrumented_dir, line_maps). Both are None/empty if no sources.
    """
    source_dirs = [Path(p) for p in config.coverage_source]
    if not source_dirs:
        click.echo(
            colorize(
                "Warning: --coverage enabled but no coverage.source "
                "configured in statatest.toml",
                Colors.YELLOW,
            )
        )
        return None, {}

    if verbose:
        click.echo(
            colorize(f"Instrumenting source files from: {source_dirs}", Colors.DIM)
        )

    instrumented_dir, line_maps = setup_instrumented_environment(
        source_dirs, Path.cwd()
    )

    if verbose:
        click.echo(colorize(f"Instrumented {len(line_maps)} file(s)\n", Colors.DIM))

    return instrumented_dir, line_maps


def _run_test_session(
    tests: list[TestFile],
    config: Config,
    coverage: bool,
    cov_report: str | None,
    junit_xml: str | None,
    verbose: bool,
) -> int:
    """Execute tests and generate reports.

    Args:
        tests: List of test files to run.
        config: Configuration object.
        coverage: Whether coverage collection is enabled.
        cov_report: Coverage report format (lcov, html) or None.
        junit_xml: Path for JUnit XML output or None.
        verbose: Whether to print verbose output.

    Returns:
        Number of failed tests.
    """
    # Set up coverage instrumentation if enabled
    instrumented_dir: Path | None = None
    line_maps: dict[str, dict[int, int]] = {}

    if coverage:
        instrumented_dir, line_maps = _setup_coverage(config, verbose)

    # Run tests
    results = run_tests(
        tests,
        config,
        coverage=coverage,
        verbose=verbose,
        instrumented_dir=instrumented_dir,
    )

    # Generate reports
    if junit_xml:
        write_junit_xml(results, Path(junit_xml))
        click.echo(f"\nJUnit XML written to: {junit_xml}")

    if coverage and cov_report:
        _generate_coverage_report(results, cov_report, config, line_maps)

    # Clean up instrumented files
    if instrumented_dir:
        cleanup_instrumented_environment(Path.cwd())

    # Print summary
    _print_summary(results)

    return sum(1 for r in results if not r.passed)


@click.group(invoke_without_command=True)
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("-c", "--coverage", is_flag=True, help="Enable coverage collection.")
@click.option(
    "-r",
    "--cov-report",
    type=click.Choice(["lcov", "html"]),
    help="Coverage report format.",
)
@click.option("-j", "--junit-xml", type=click.Path(), help="Output JUnit XML to path.")
@click.option("-m", "--marker", type=str, help="Only run tests with this marker.")
@click.option("-k", "--keyword", type=str, help="Only run tests matching keyword.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.option("-V", "--version", "show_version", is_flag=True, help="Show version.")
@click.option("-i", "--init", is_flag=True, help="Create statatest.toml template.")
@click.pass_context
def main(
    ctx: click.Context,
    path: str | None,
    coverage: bool,
    cov_report: str | None,
    junit_xml: str | None,
    marker: str | None,
    keyword: str | None,
    verbose: bool,
    show_version: bool,
    init: bool,
) -> None:
    """statatest - Pytest-inspired testing framework for Stata.

    \b
    Examples:
        statatest tests/                Run all tests
        statatest tests/ -v             Verbose output
        statatest tests/ -c             Enable coverage
        statatest tests/ -c -r lcov     Coverage with LCOV report
        statatest tests/ -j junit.xml   Generate JUnit XML
        statatest tests/ -m unit        Run @marker: unit tests
        statatest tests/ -k panel       Run tests matching 'panel'
        statatest -i                    Create config template

    \b
    Configuration:
        Create statatest.toml in project root, or use [tool.statatest]
        in pyproject.toml. Run `statatest --init` to generate a template.
    """
    if show_version:
        click.echo(f"statatest version {__version__}")
        sys.exit(0)

    if init:
        _create_config_template()
        sys.exit(0)

    if ctx.invoked_subcommand is None and path is None:
        click.echo(colorize("Usage: statatest <path> [OPTIONS]", Colors.YELLOW))
        click.echo("Run 'statatest --help' for more information.")
        sys.exit(1)

    if path is None:
        return

    # Configure logging
    configure_logging(verbose)

    # Load configuration
    config = Config.from_project(Path.cwd())
    if verbose:
        config.verbose = True

    # Discover tests
    test_path = Path(path)
    click.echo(colorize(f"statatest v{__version__}", Colors.BOLD + Colors.BLUE))
    click.echo(f"Collecting tests from: {test_path}")

    tests = discover_tests(test_path, config, marker=marker, keyword=keyword)

    if not tests:
        click.echo(colorize("No tests found.", Colors.YELLOW))
        sys.exit(0)

    click.echo(f"Found {len(tests)} test file(s)\n")

    # Run test session and exit with appropriate code
    failed = _run_test_session(tests, config, coverage, cov_report, junit_xml, verbose)
    sys.exit(1 if failed > 0 else 0)


def _create_config_template() -> None:
    """Create a statatest.toml template in the current directory."""
    template = """[tool.statatest]
testpaths = ["tests"]
test_files = ["test_*.do"]
stata_executable = "stata-mp"

[tool.statatest.coverage]
source = ["code/functions"]
omit = ["tests/*"]

[tool.statatest.reporting]
junit_xml = "junit.xml"
lcov = "coverage.lcov"
"""
    config_path = Path.cwd() / "statatest.toml"
    if config_path.exists():
        click.echo(colorize("statatest.toml already exists.", Colors.YELLOW))
        return

    config_path.write_text(template)
    click.echo(colorize("Created statatest.toml", Colors.GREEN))


def _generate_coverage_report(
    results: list[TestResult],
    report_format: str,
    config: Config,
    line_maps: dict[str, dict[int, int]] | None = None,
) -> None:
    """Generate coverage report in the specified format.

    Args:
        results: List of test results with coverage data.
        report_format: Output format ('lcov' or 'html').
        config: Configuration object.
        line_maps: Optional mapping of instrumented to original line numbers.
    """
    # TODO: Use line_maps to map instrumented line numbers back to original
    _ = line_maps  # Suppress unused warning for now

    match report_format.lower():
        case "lcov":
            lcov_path = Path(config.reporting.get("lcov", "coverage.lcov"))
            generate_lcov(results, lcov_path)
            click.echo(f"LCOV coverage written to: {lcov_path}")
        case "html":
            html_dir = Path(config.reporting.get("htmlcov", "htmlcov"))
            generate_html(results, html_dir)
            click.echo(f"HTML coverage written to: {html_dir}")
        case _:
            click.echo(
                colorize(f"Unknown coverage format: {report_format}", Colors.YELLOW)
            )


def _print_summary(results: list[TestResult]) -> None:
    """Print test results summary."""
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total_time = sum(r.duration for r in results)

    click.echo()
    click.echo("=" * 60)

    if failed == 0:
        click.echo(
            colorize(f"{passed} passed", Colors.BOLD + Colors.GREEN)
            + f" in {total_time:.2f}s"
        )
    else:
        click.echo(
            colorize(f"{failed} failed", Colors.BOLD + Colors.RED)
            + ", "
            + colorize(f"{passed} passed", Colors.GREEN)
            + f" in {total_time:.2f}s"
        )

        # Show failed tests
        click.echo("\n" + colorize("FAILURES:", Colors.BOLD + Colors.RED))
        for result in results:
            if not result.passed:
                click.echo(f"  - {result.test_file}: {result.error_message}")


if __name__ == "__main__":
    main()
