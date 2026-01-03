"""JUnit XML report generation.

This module generates JUnit XML format reports compatible with CI systems.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

from statatest.core.constants import (
    JUNIT_FAILURE_MAX_LENGTH,
    JUNIT_STDERR_MAX_LENGTH,
    JUNIT_STDOUT_MAX_LENGTH,
)
from statatest.core.models import TestResult


def write_junit_xml(results: list[TestResult], output_path: Path) -> None:
    """Generate JUnit XML report for CI systems.

    JUnit XML format is compatible with:
    - GitHub Actions
    - Jenkins
    - CircleCI
    - GitLab CI
    - Codecov Test Analytics

    Args:
        results: List of test results.
        output_path: Path to write the XML file.
    """
    testsuites = _create_testsuites_element(results)
    suites = _group_by_directory(results)

    for suite_name, suite_results in suites.items():
        testsuite = _create_testsuite_element(testsuites, suite_name, suite_results)
        for result in suite_results:
            _create_testcase_element(testsuite, suite_name, result)

    _write_xml(testsuites, output_path)


def _create_testsuites_element(results: list[TestResult]) -> ET.Element:
    """Create the root testsuites element.

    Args:
        results: All test results.

    Returns:
        Root XML element.
    """
    testsuites = ET.Element("testsuites")
    testsuites.set("name", "Stata Tests")
    testsuites.set("tests", str(len(results)))
    testsuites.set("failures", str(sum(1 for r in results if not r.passed)))
    testsuites.set("time", f"{sum(r.duration for r in results):.3f}")
    testsuites.set("timestamp", datetime.now(tz=UTC).isoformat())
    return testsuites


def _group_by_directory(results: list[TestResult]) -> dict[str, list[TestResult]]:
    """Group test results by parent directory.

    Args:
        results: All test results.

    Returns:
        Dictionary mapping directory names to results.
    """
    suites: dict[str, list[TestResult]] = {}
    for result in results:
        suite_name = Path(result.test_file).parent.name or "root"
        if suite_name not in suites:
            suites[suite_name] = []
        suites[suite_name].append(result)
    return suites


def _create_testsuite_element(
    parent: ET.Element,
    suite_name: str,
    results: list[TestResult],
) -> ET.Element:
    """Create a testsuite element.

    Args:
        parent: Parent XML element.
        suite_name: Name of the test suite.
        results: Test results in this suite.

    Returns:
        Testsuite XML element.
    """
    testsuite = ET.SubElement(parent, "testsuite")
    testsuite.set("name", suite_name)
    testsuite.set("tests", str(len(results)))
    testsuite.set("failures", str(sum(1 for r in results if not r.passed)))
    testsuite.set("time", f"{sum(r.duration for r in results):.3f}")
    return testsuite


def _create_testcase_element(
    parent: ET.Element,
    suite_name: str,
    result: TestResult,
) -> ET.Element:
    """Create a testcase element.

    Args:
        parent: Parent testsuite element.
        suite_name: Name of the test suite (used as classname).
        result: Test result.

    Returns:
        Testcase XML element.
    """
    testcase = ET.SubElement(parent, "testcase")
    testcase.set("name", Path(result.test_file).stem)
    testcase.set("classname", suite_name)
    testcase.set("time", f"{result.duration:.3f}")

    if not result.passed:
        _add_failure_element(testcase, result)

    if result.stdout:
        _add_system_out(testcase, result.stdout)

    if result.stderr:
        _add_system_err(testcase, result.stderr)

    return testcase


def _add_failure_element(testcase: ET.Element, result: TestResult) -> None:
    """Add failure element to testcase.

    Args:
        testcase: Testcase XML element.
        result: Failed test result.
    """
    failure = ET.SubElement(testcase, "failure")
    failure.set("message", result.error_message)
    failure.set("type", "AssertionError")
    failure.text = result.stdout[-JUNIT_FAILURE_MAX_LENGTH:] if result.stdout else ""


def _add_system_out(testcase: ET.Element, stdout: str) -> None:
    """Add system-out element to testcase.

    Args:
        testcase: Testcase XML element.
        stdout: Standard output content.
    """
    system_out = ET.SubElement(testcase, "system-out")
    system_out.text = stdout[-JUNIT_STDOUT_MAX_LENGTH:]


def _add_system_err(testcase: ET.Element, stderr: str) -> None:
    """Add system-err element to testcase.

    Args:
        testcase: Testcase XML element.
        stderr: Standard error content.
    """
    system_err = ET.SubElement(testcase, "system-err")
    system_err.text = stderr[-JUNIT_STDERR_MAX_LENGTH:]


def _write_xml(root: ET.Element, output_path: Path) -> None:
    """Write XML tree to file with proper formatting.

    Args:
        root: Root XML element.
        output_path: Path to write the file.
    """
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
