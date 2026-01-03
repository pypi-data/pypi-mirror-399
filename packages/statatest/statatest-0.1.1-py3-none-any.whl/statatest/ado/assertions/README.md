# Assertions

Test assertion commands for Stata.

## Available Assertions

### Value Assertions

| Command               | Description                   |
| --------------------- | ----------------------------- |
| `assert_equal`        | Two values are equal          |
| `assert_approx_equal` | Values equal within tolerance |
| `assert_true`         | Condition is true             |
| `assert_false`        | Condition is false            |
| `assert_in_range`     | Value within min/max          |

### Data Assertions

| Command             | Description                    |
| ------------------- | ------------------------------ |
| `assert_count`      | Dataset has N observations     |
| `assert_obs_count`  | Observations match condition   |
| `assert_no_missing` | Variable has no missing values |
| `assert_positive`   | Variable values are positive   |
| `assert_unique`     | Variable values are unique     |
| `assert_sorted`     | Data is sorted by variable     |

### Variable Assertions

| Command               | Description                |
| --------------------- | -------------------------- |
| `assert_var_exists`   | Variable exists in dataset |
| `assert_var_type`     | Variable has expected type |
| `assert_label_exists` | Variable has value labels  |

### Error Assertions

| Command          | Description                |
| ---------------- | -------------------------- |
| `assert_error`   | Command produces error     |
| `assert_noerror` | Command runs without error |

### Other

| Command                  | Description                  |
| ------------------------ | ---------------------------- |
| `assert_file_exists`     | File exists on disk          |
| `assert_identity`        | Two datasets are identical   |
| `assert_sum_equals`      | Sum of variable equals value |
| `assert_panel_structure` | Valid panel data structure   |

## Common Options

All assertions support:

- `message(string)` - Custom failure message
- `verbose` - Detailed output on success/failure

## Example

```stata
sysuse auto, clear

// Basic assertions
assert_equal _N, expected(74)
assert_true _N > 0
assert_no_missing price

// With verbose
assert_var_type mpg, type("numeric") verbose
// Output: PASS: assert_var_type

// With custom message
assert_positive price, message("Prices must be positive")
```

## Internal Markers

For framework parsing:

- `_STATATEST_PASS_:<name>_` - Assertion passed
- `_STATATEST_FAIL_:<name>_:<reason>_END_` - Assertion failed
