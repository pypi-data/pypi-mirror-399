# Core Module

Domain models, configuration, and constants for statatest.

## Components

| File           | Purpose                                                     |
| -------------- | ----------------------------------------------------------- |
| `models.py`    | Data classes: TestFile, TestResult, TestSuite, CoverageData |
| `config.py`    | Configuration loading from pyproject.toml or statatest.toml |
| `constants.py` | Framework constants, patterns, markers                      |
| `logging.py`   | Logging configuration                                       |

## Models

### TestFile

Represents a discovered test file:

```python
@dataclass
class TestFile:
    path: Path
    markers: list[str]      # e.g., ["unit", "slow"]
    programs: list[str]     # Test program names
```

### TestResult

Result of running a single test:

```python
@dataclass
class TestResult:
    test_file: str
    passed: bool
    duration: float
    rc: int                 # Stata return code
    stdout: str
    stderr: str
    error_message: str
    coverage_hits: dict[str, set[int]]
```

### Configuration

Load from `statatest.toml` or `pyproject.toml`:

```python
from statatest.core import Config

config = Config.from_project(Path("."))
print(config.stata_path)    # Path to Stata executable
print(config.timeout)       # Test timeout in seconds
```

## Dependencies

- **Used by**: All other modules
- **Depends on**: None (leaf module)
