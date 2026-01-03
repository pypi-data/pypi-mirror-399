# Coverage Module

Code coverage instrumentation and reporting.

## Components

| File            | Purpose                                  |
| --------------- | ---------------------------------------- |
| `instrument.py` | Add coverage markers to .ado files       |
| `aggregator.py` | Combine coverage from multiple test runs |
| `reporter.py`   | Generate LCOV and HTML reports           |
| `models.py`     | FileCoverage, CoverageReport classes     |

## How Coverage Works

### 1. Instrumentation

Before running tests, .ado files are instrumented:

```stata
// Original
program define myprogram
    local x = 1
    display `x'
end

// Instrumented
program define myprogram
    display as text "{* COV:myprogram.ado:2 }"
    local x = 1
    display as text "{* COV:myprogram.ado:3 }"
    display `x'
end
```

### 2. Marker Format

```plaintext
{* COV:filename:linenumber }
```

- Invisible in rendered output
- Preserved in raw SMCL logs
- Parsed by Python after test execution

### 3. Aggregation

```python
from statatest.coverage import aggregate_coverage

report = aggregate_coverage(test_results)
print(f"Overall: {report.overall_coverage:.1f}%")
```

## Output Formats

- **LCOV**: `coverage.lcov` - For CI tools (Codecov, Coveralls)
- **HTML**: `htmlcov/index.html` - Human-readable report

## Dependencies

- **Depends on**: `core`
- **Used by**: `execution`, `reporting`, `cli`
