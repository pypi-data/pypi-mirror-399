"""Wrapper .do file generation for test execution.

This module generates the wrapper .do file that sets up the
Stata environment and runs the actual test file.
"""

from __future__ import annotations

from pathlib import Path


def create_wrapper_do(
    test_path: Path,
    ado_paths: dict[str, Path],
    conftest_files: list[Path],
    instrumented_dir: Path | None = None,
    setup_do: str | None = None,
    log_path: Path | None = None,
) -> str:
    """Create a wrapper .do file for test execution.

    The wrapper executes in this order:
    1. Clear and set Stata options
    2. Start SMCL log (for coverage marker capture)
    3. Add instrumented directory (for coverage) - highest priority
    4. Add statatest ado paths (assertions, fixtures)
    5. Run setup_do (if configured)
    6. Load conftest.do files (fixtures and shared setup)
    7. Run the actual test
    8. Close log

    Args:
        test_path: Path to the test file.
        ado_paths: Dictionary of ado paths to add (statatest assertions/fixtures).
        conftest_files: List of conftest.do files to load (in order).
        instrumented_dir: Path to instrumented source files (for coverage).
        setup_do: Optional path to a setup.do file for custom initialization.
        log_path: Path to save SMCL log (for coverage marker parsing).

    Returns:
        Contents of the wrapper .do file.
    """
    lines: list[str] = []

    # Header
    lines.extend(_generate_header())

    # Start SMCL log for coverage (must be before any instrumented code runs)
    if log_path:
        lines.extend(_generate_log_section(log_path))

    # Instrumented directory (highest priority for coverage)
    if instrumented_dir:
        lines.extend(_generate_instrumented_section(instrumented_dir))

    # Additional ado paths
    if ado_paths:
        lines.extend(_generate_adopath_section(ado_paths))

    # User setup script
    if setup_do:
        lines.extend(_generate_setup_section(setup_do))

    # Conftest files
    if conftest_files:
        lines.extend(_generate_conftest_section(conftest_files))

    # Test execution
    lines.extend(_generate_test_section(test_path))

    # Close log
    if log_path:
        lines.extend(_generate_log_close_section())

    return "\n".join(lines)


def _generate_header() -> list[str]:
    """Generate wrapper file header with Stata initialization."""
    return [
        "// Auto-generated wrapper by statatest",
        "// Test environment setup and execution",
        "",
        "clear all",
        "set more off",
        "",
    ]


def _generate_log_section(log_path: Path) -> list[str]:
    """Generate section to start SMCL log for coverage marker capture."""
    return [
        "// Start SMCL log for coverage marker capture",
        f'log using "{log_path}", smcl replace',
        "",
    ]


def _generate_log_close_section() -> list[str]:
    """Generate section to close the log file."""
    return [
        "",
        "// Close log",
        "log close",
    ]


def _generate_instrumented_section(instrumented_dir: Path) -> list[str]:
    """Generate section for instrumented source files (coverage).

    Uses adopath ++ (double plus) to PREPEND with highest priority,
    ensuring instrumented files are found before any user-added paths.

    Also uses 'discard' to clear any cached .ado programs, forcing Stata
    to reload them from the new adopath (instrumented versions).
    """
    return [
        "// Instrumented source files for coverage (highest priority)",
        f'adopath ++ "{instrumented_dir}"',
        "discard  // Clear cached programs to force reload from instrumented path",
        "",
    ]


def _generate_adopath_section(ado_paths: dict[str, Path]) -> list[str]:
    """Generate section for additional ado paths."""
    lines = ["// Additional ado paths"]
    for name, path in ado_paths.items():
        # Clean up internal naming for comments
        comment = name.replace("_", " ").replace("custom ", "user: ")
        lines.append(f"// {comment}")
        lines.append(f'adopath + "{path}"')
    lines.append("")
    return lines


def _generate_setup_section(setup_do: str) -> list[str]:
    """Generate section for user-defined setup script."""
    return [
        "// User-defined setup script",
        f'do "{setup_do}"',
        "",
    ]


def _generate_conftest_section(conftest_files: list[Path]) -> list[str]:
    """Generate section for conftest files."""
    lines = ["// Conftest files (fixtures and shared setup)"]
    lines.extend(f'do "{conftest}"' for conftest in conftest_files)
    lines.append("")
    return lines


def _generate_test_section(test_path: Path) -> list[str]:
    """Generate section for test execution."""
    return [
        "// Execute test",
        f'do "{test_path}"',
        "",
    ]
