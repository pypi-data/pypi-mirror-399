# Discovery Module

Find and parse Stata test files.

## Components

| File        | Purpose                                   |
| ----------- | ----------------------------------------- |
| `finder.py` | Locate test\_\*.do files in directories   |
| `parser.py` | Extract markers, programs from test files |

## Usage

```python
from statatest.discovery import discover_tests

# Find all test files
tests = discover_tests(Path("tests/"))

# With filters
tests = discover_tests(
    Path("tests/"),
    marker="unit",           # Only tests with @unit marker
    keyword="coverage"       # Only tests matching keyword
)

for test in tests:
    print(f"{test.path}: {test.markers}")
```

## Test File Format

```stata
// tests/test_example.do

// @marker unit
// @marker fast

program define test_basic
    sysuse auto, clear
    assert_true _N > 0
end
```

## Patterns

- **File pattern**: `test_*.do`
- **Marker pattern**: `// @marker <name>`
- **Program pattern**: `program define test_*`

## Dependencies

- **Depends on**: `core`
- **Used by**: `cli`, `execution`
