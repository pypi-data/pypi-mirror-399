"""Configuration management for statatest.

This module provides Config, a dataclass that holds all configuration options
and knows how to load itself from TOML files.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from statatest.core.constants import (
    DEFAULT_STATA_EXECUTABLE,
    DEFAULT_TEST_FILE_PATTERNS,
    DEFAULT_TEST_PATHS,
    DEFAULT_TIMEOUT_SECONDS,
)


@dataclass
class Config:
    """Configuration for statatest.

    Attributes:
        testpaths: Directories to search for test files.
        test_files: Glob patterns for test file names.
        stata_executable: Path or name of Stata executable.
        timeout: Timeout in seconds for each test file.
        verbose: Whether to show verbose output.
        setup_do: Path to a setup.do file to run before each test.
        coverage_source: Directories containing source files for coverage.
        coverage_omit: Patterns for files to exclude from coverage.
        reporting: Reporting configuration (junit_xml, lcov paths).
    """

    testpaths: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)
    stata_executable: str = DEFAULT_STATA_EXECUTABLE
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    verbose: bool = False
    setup_do: str | None = None
    coverage_source: list[str] = field(default_factory=list)
    coverage_omit: list[str] = field(default_factory=list)
    reporting: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Apply default values for empty lists.

        This method is called after dataclass __init__ completes.
        It sets default values from constants when lists are empty.
        """
        if not self.testpaths:
            self.testpaths = list(DEFAULT_TEST_PATHS)
        if not self.test_files:
            self.test_files = list(DEFAULT_TEST_FILE_PATTERNS)

    @classmethod
    def from_project(cls, project_root: Path) -> Config:
        """Load configuration from project directory.

        Config file precedence (first found wins):
        1. statatest.toml
        2. pyproject.toml [tool.statatest]

        Args:
            project_root: Root directory of the project.

        Returns:
            Config object with settings from file, or defaults if no config found.
        """
        settings = cls._load_settings(project_root)
        return cls(**settings)

    @classmethod
    def _load_settings(cls, project_root: Path) -> dict[str, Any]:
        """Load settings from TOML files in project directory.

        Args:
            project_root: Root directory of the project.

        Returns:
            Dictionary of settings suitable for Config.__init__.
        """
        # Try statatest.toml first
        statatest_toml = project_root / "statatest.toml"
        if statatest_toml.exists():
            data = cls._load_toml(statatest_toml)
            # statatest.toml can have settings at root or under [tool.statatest]
            raw_settings = data.get("tool", {}).get("statatest", data)
            return cls._extract_settings(raw_settings)

        # Fall back to pyproject.toml
        pyproject_toml = project_root / "pyproject.toml"
        if pyproject_toml.exists():
            data = cls._load_toml(pyproject_toml)
            raw_settings = data.get("tool", {}).get("statatest", {})
            if raw_settings:
                return cls._extract_settings(raw_settings)

        # No config found - return empty dict (dataclass defaults will apply)
        return {}

    @staticmethod
    def _load_toml(path: Path) -> dict[str, Any]:
        """Load and parse a TOML file.

        Args:
            path: Path to the TOML file.

        Returns:
            Parsed TOML content as dictionary.
        """
        with path.open("rb") as f:
            return tomllib.load(f)

    @classmethod
    def _extract_settings(cls, raw: dict[str, Any]) -> dict[str, Any]:
        """Extract and transform settings for Config.__init__.

        Args:
            raw: Raw settings dictionary from TOML file.

        Returns:
            Dictionary with keys matching Config field names.
        """
        settings: dict[str, Any] = {}

        # Direct mappings (TOML key == Config field name)
        direct_keys = [
            "testpaths",
            "test_files",
            "stata_executable",
            "timeout",
            "verbose",
            "setup_do",
            "reporting",
        ]
        for key in direct_keys:
            if key in raw:
                settings[key] = raw[key]

        # Nested coverage settings
        coverage = raw.get("coverage", {})
        if "source" in coverage:
            settings["coverage_source"] = coverage["source"]
        if "omit" in coverage:
            settings["coverage_omit"] = coverage["omit"]

        return settings
