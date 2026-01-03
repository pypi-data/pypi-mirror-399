# statatest Package

Testing framework for Stata code with Python orchestration.

## Architecture

```plaintext
statatest/
├── cli.py              # Command-line interface
├── core/               # Domain models and configuration
├── discovery/          # Test file discovery and parsing
├── execution/          # Stata test execution
├── coverage/           # Code coverage instrumentation
├── fixtures/           # Python fixture management
├── reporting/          # JUnit XML and coverage reports
└── ado/                # Stata assertion and fixture commands
```

## Module Overview

| Module      | Purpose                                           |
| ----------- | ------------------------------------------------- |
| `core`      | Data models (TestFile, TestResult), configuration |
| `discovery` | Find and parse test files                         |
| `execution` | Run tests in Stata, parse results                 |
| `coverage`  | Instrument code, aggregate coverage               |
| `fixtures`  | Manage test fixtures                              |
| `reporting` | Generate JUnit XML, LCOV, HTML reports            |
| `ado`       | Stata commands for assertions and fixtures        |

## Entry Points

- **CLI**: `python -m statatest` or `statatest` command
- **Python API**: `from statatest import run_tests`
- **Stata**: `use_fixture`, `assert_*` commands

## Data Flow

```plaintext
1. Discovery: Find test_*.do files
2. Parsing: Extract markers, programs, fixtures
3. Execution: Run each test in Stata subprocess
4. Coverage: Parse SMCL logs for coverage markers
5. Reporting: Generate JUnit XML, coverage reports
```
