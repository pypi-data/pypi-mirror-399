# statatest

[![PyPI version](https://img.shields.io/pypi/v/statatest.svg)](https://pypi.org/project/statatest/)
[![Python versions](https://img.shields.io/pypi/pyversions/statatest.svg)](https://pypi.org/project/statatest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/jigonr/statatest/actions/workflows/ci.yml/badge.svg)](https://github.com/jigonr/statatest/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/jigonr/statatest/branch/main/graph/badge.svg?token=BG2IGYM5BE)](https://codecov.io/gh/jigonr/statatest)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jigonzalez.com/statatest/)

A pytest-inspired testing and code coverage framework for Stata.

**[Documentation](https://jigonzalez.com/statatest/)** |
**[GitHub](https://github.com/jigonr/statatest)** |
**[PyPI](https://pypi.org/project/statatest/)**

## Features

- **Test Discovery**: Automatically find and run `test_*.do` files
- **Rich Assertions**: Built on Stata's native `assert` with detailed failure
  messages
- **Fixture System**: Reusable setup/teardown with pytest-like scoping
- **Code Coverage**: Line-level coverage via SMCL comment instrumentation
- **CI Integration**: JUnit XML output for GitHub Actions, LCOV for Codecov
- **Backward Compatible**: Works with existing test patterns

## Installation

### Using uv (recommended)

```bash
# Install globally
uv tool install statatest

# Or run directly without installing
uvx statatest tests/
```

### Using pip

```bash
pip install statatest
```

## Quick Start

```bash
# Run all tests in tests/ directory
statatest tests/

# Run with coverage
statatest tests/ --coverage

# Generate JUnit XML for CI
statatest tests/ --junit-xml=junit.xml
```

## Writing Tests

```stata
// tests/test_myfunction.do

// @marker: unit
program define test_basic_functionality
    // Setup
    clear
    set obs 10
    gen x = _n

    // Test
    myfunction x, gen(y)

    // Assert
    assert_var_exists y
    assert_equal _N, expected(10)
end
```

## Assertions

| Function              | Purpose             | Example                                                |
| --------------------- | ------------------- | ------------------------------------------------------ |
| `assert_equal`        | Value equality      | `assert_equal "\`r(mean)'"", expected("5")`            |
| `assert_true`         | Boolean true        | `assert_true _N > 0`                                   |
| `assert_false`        | Boolean false       | `assert_false missing(x)`                              |
| `assert_error`        | Command should fail | `assert_error "invalid_command"`                       |
| `assert_var_exists`   | Variable exists     | `assert_var_exists myvar`                              |
| `assert_approx_equal` | Float comparison    | `assert_approx_equal r(mean), expected(0.5) tol(0.01)` |

## Fixtures

Create reusable setup/teardown functions with `conftest.do`:

```stata
// tests/conftest.do - Shared fixtures

program define fixture_sample_panel
    clear
    set obs 100
    gen int firm_id = ceil(_n / 10)
    gen int year = 2010 + mod(_n, 10)
    gen double revenue = exp(rnormal(15, 2))
end

program define fixture_sample_panel_teardown
    clear
end
```

Use fixtures in your tests:

```stata
// tests/test_analysis.do
// @uses_fixture: sample_panel

program define test_panel_analysis
    use_fixture sample_panel

    assert_obs_count 100
    assert_var_exists revenue
end
```

Built-in fixtures:

| Fixture                 | Purpose                                        |
| ----------------------- | ---------------------------------------------- |
| `fixture_tempfile`      | Temporary file path (`$fixture_tempfile_path`) |
| `fixture_empty_dataset` | Empty dataset with optional obs count          |
| `fixture_seed`          | Reproducible random seed                       |

## Configuration

Create `statatest.toml` in your project root:

```toml
[tool.statatest]
testpaths = ["tests"]
test_files = ["test_*.do"]
stata_executable = "stata-mp"

[tool.statatest.coverage]
source = ["code/functions"]
omit = ["tests/*"]

[tool.statatest.reporting]
junit_xml = "junit.xml"
lcov = "coverage.lcov"
```

## GitHub Actions Integration

```yaml
name: Stata Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run:
          uvx statatest tests/ --junit-xml=junit.xml --coverage
          --cov-report=lcov
      - uses: codecov/codecov-action@v5
        with:
          files: coverage.lcov
```

## Requirements

- **Python**: 3.11+
- **Stata**: 16+

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [pytest](https://pytest.org/)
- SMCL parsing patterns adapted from
  [mcp-stata](https://github.com/tmonk/mcp-stata) (AGPL-3.0)
