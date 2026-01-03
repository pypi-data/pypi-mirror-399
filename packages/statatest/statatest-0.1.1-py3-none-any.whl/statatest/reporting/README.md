# Reporting Module

Generate test and coverage reports.

## Components

| File       | Purpose                     |
| ---------- | --------------------------- |
| `junit.py` | JUnit XML report generation |

## JUnit XML

Standard format for CI systems:

```python
from statatest.reporting import write_junit_xml

write_junit_xml(results, Path("results.xml"))
```

Output:

```xml
<?xml version="1.0" encoding="utf-8"?>
<testsuite name="statatest" tests="5" failures="1" time="12.34">
  <testcase name="test_basic" classname="tests.test_example" time="2.1"/>
  <testcase name="test_edge" classname="tests.test_example" time="1.5">
    <failure message="assert_equal failed">
      Expected: 10
      Actual: 5
    </failure>
  </testcase>
</testsuite>
```

## Coverage Reports

Coverage report generation is in `coverage/reporter.py`:

- **LCOV**: `generate_lcov(report, path)`
- **HTML**: `generate_html(report, output_dir)`

## Dependencies

- **Depends on**: `core`
- **Used by**: `cli`
