# Ado Files

Stata commands for testing: assertions and fixtures.

## Structure

```plaintext
ado/
├── assertions/     # Test assertion commands
│   ├── assert_equal.ado
│   ├── assert_true.ado
│   └── ...
└── fixtures/       # Test fixture commands
    ├── fixture_balanced_panel.ado
    ├── use_fixture.ado
    └── ...
```

## Usage in Tests

```stata
// test_example.do

// Use a fixture
use_fixture balanced_panel

// Make assertions
assert_equal _N, expected(500)
assert_true _N > 0
assert_no_missing price
```

## Verbose Option

All commands support `verbose` for detailed output:

```stata
// Default: minimal output
assert_equal `x', expected(5)
// On failure: FAIL: assert_equal: 3 != 5

// Verbose: detailed output
assert_equal `x', expected(5) verbose
// On failure:
//   ASSERTION FAILED: assert_equal
//     Expected: 5
//     Actual: 3
```

## Adding New Commands

1. Create `.ado` file in appropriate directory
2. Follow the existing pattern (see assertions/README.md)
3. Include `_STATATEST_PASS_` and `_STATATEST_FAIL_` markers
4. Add `verbose` option for detailed output

## Path Setup

These files are automatically added to Stata's `adopath` when running tests via
statatest.
