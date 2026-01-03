"""Source code instrumentation for coverage collection.

This module instruments Stata .ado files with invisible SMCL coverage markers
that are preserved in .smcl log files but invisible in rendered output.

The instrumentation process:
1. Copy source files to .statatest/instrumented/
2. Inject SMCL comment markers: {* COV:filename:lineno }
3. Run tests with instrumented files
4. Parse .smcl logs to extract coverage data
5. Map coverage back to original file paths
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from statatest.core.constants import (
    INSTRUMENT_SKIP_KEYWORDS,
    INSTRUMENT_SKIP_PATTERNS,
)

_SKIP_REGEX = re.compile("|".join(INSTRUMENT_SKIP_PATTERNS), re.IGNORECASE)


def _ends_with_continuation(line: str) -> bool:
    """Check if line ends with continuation marker (///).

    In Stata, /// at the end of a line continues the command to the next line.
    This is common for long commands that exceed 80 characters.

    Args:
        line: The source code line.

    Returns:
        True if line ends with /// (continues to next line).
    """
    return line.rstrip().endswith("///")


def should_instrument_line(line: str, in_continuation: bool = False) -> bool:
    """Check if a line should be instrumented.

    Args:
        line: The source code line.
        in_continuation: Whether this line is part of a multi-line command
            started with /// on a previous line.

    Returns:
        True if the line should be instrumented.
    """
    # If we're in a continuation, always instrument the line
    # (it's part of an executable command spanning multiple lines)
    if in_continuation:
        return True

    # Skip lines matching skip patterns (comments, empty, structural)
    if _SKIP_REGEX.match(line):
        return False

    # Skip lines that are just closing braces or keywords
    stripped = line.strip().lower()
    return stripped not in INSTRUMENT_SKIP_KEYWORDS


def instrument_file(source_path: Path, dest_path: Path) -> dict[int, int]:
    """Instrument a single .ado file with SMCL coverage markers.

    Handles Stata continuation lines (///) so that all lines of a multi-line
    command are instrumented and reported as covered.

    Args:
        source_path: Path to the original .ado file
        dest_path: Path where instrumented file will be written

    Returns:
        Mapping of instrumented line numbers to original line numbers
    """
    content = source_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Track line number mapping (instrumented -> original)
    line_map: dict[int, int] = {}

    # Add marker header so `which` command shows this is instrumented
    instrumented_lines: list[str] = [
        f"*! INSTRUMENTED BY STATATEST - {source_path.name}",
    ]
    filename = source_path.name

    # Track continuation state across lines
    in_continuation = False

    for orig_lineno, line in enumerate(lines, start=1):
        if should_instrument_line(line, in_continuation=in_continuation):
            # Insert SMCL coverage marker before the line
            # Format: display `"{* COV:filename:lineno }"'
            marker = f'display `"{{* COV:{filename}:{orig_lineno} }}"\''
            instrumented_lines.append(marker)
            line_map[len(instrumented_lines)] = orig_lineno
            instrumented_lines.append(line)
        else:
            instrumented_lines.append(line)

        # Update continuation state for next line
        # If current line ends with ///, next line is a continuation
        in_continuation = _ends_with_continuation(line)

    # Write instrumented file
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text("\n".join(instrumented_lines), encoding="utf-8")

    return line_map


def instrument_directory(
    source_dir: Path,
    dest_dir: Path,
    patterns: list[str] | None = None,
) -> dict[str, dict[int, int]]:
    """Instrument all .ado files in a directory.

    Args:
        source_dir: Directory containing source .ado files
        dest_dir: Directory where instrumented files will be written
        patterns: Glob patterns for files to instrument (default: ["*.ado"])

    Returns:
        Dictionary mapping filenames to their line number mappings
    """
    if patterns is None:
        patterns = ["*.ado"]

    all_maps: dict[str, dict[int, int]] = {}

    for pattern in patterns:
        for source_path in source_dir.glob(pattern):
            if source_path.is_file():
                dest_path = dest_dir / source_path.name
                line_map = instrument_file(source_path, dest_path)
                all_maps[source_path.name] = line_map

    return all_maps


def setup_instrumented_environment(
    source_dirs: list[Path],
    work_dir: Path,
    patterns: list[str] | None = None,
) -> tuple[Path, dict[str, dict[int, int]]]:
    """Set up an instrumented environment for coverage collection.

    Args:
        source_dirs: List of directories containing source files
        work_dir: Working directory (usually project root)
        patterns: Glob patterns for files to instrument

    Returns:
        Tuple of (instrumented_dir, all_line_maps)
    """
    # Create .statatest/instrumented directory
    instrumented_dir = work_dir / ".statatest" / "instrumented"
    if instrumented_dir.exists():
        shutil.rmtree(instrumented_dir)
    instrumented_dir.mkdir(parents=True)

    all_maps: dict[str, dict[int, int]] = {}

    for source_dir in source_dirs:
        if source_dir.exists():
            maps = instrument_directory(source_dir, instrumented_dir, patterns)
            all_maps.update(maps)

    return instrumented_dir, all_maps


def cleanup_instrumented_environment(work_dir: Path) -> None:
    """Clean up the instrumented environment.

    Args:
        work_dir: Working directory containing .statatest folder
    """
    statatest_dir = work_dir / ".statatest"
    if statatest_dir.exists():
        shutil.rmtree(statatest_dir)


def get_total_lines(source_path: Path) -> set[int]:
    """Get the set of instrumentable line numbers in a source file.

    Handles Stata continuation lines (///) so that all lines of a multi-line
    command are counted as instrumentable.

    Args:
        source_path: Path to the source file

    Returns:
        Set of line numbers that are instrumentable
    """
    content = source_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    total_lines: set[int] = set()

    # Track continuation state across lines
    in_continuation = False

    for lineno, line in enumerate(lines, start=1):
        if should_instrument_line(line, in_continuation=in_continuation):
            total_lines.add(lineno)

        # Update continuation state for next line
        in_continuation = _ends_with_continuation(line)

    return total_lines
