# Execution Module

Run Stata tests and parse results.

## Components

| File          | Purpose                                       |
| ------------- | --------------------------------------------- |
| `executor.py` | Main test runner, subprocess management       |
| `wrapper.py`  | Generate wrapper .do files for test execution |
| `parser.py`   | Parse Stata output, extract results           |
| `models.py`   | Execution-specific data structures            |

## Usage

```python
from statatest.execution import run_tests

results = run_tests(
    test_files=[test1, test2],
    config=config,
    coverage=True,
    verbose=True
)

for result in results:
    print(f"{result.test_file}: {'PASS' if result.passed else 'FAIL'}")
```

## Wrapper Generation

Each test runs in a wrapper that:

1. Sets up adopath for assertions/fixtures
2. Starts SMCL log (for coverage)
3. Loads conftest files
4. Executes the test
5. Closes log

```stata
// Generated wrapper
clear all
set more off
adopath ++ "/path/to/instrumented"  // Coverage: highest priority
adopath + "/path/to/assertions"
do "/path/to/conftest.do"
do "/path/to/test_example.do"
```

## Result Parsing

Parses Stata output for:

- `_STATATEST_PASS_:<name>_` - Assertion passed
- `_STATATEST_FAIL_:<name>_:<reason>_END_` - Assertion failed
- `{* COV:file:line }` - Coverage marker hit

## Dependencies

- **Depends on**: `core`, `coverage`
- **Used by**: `cli`
