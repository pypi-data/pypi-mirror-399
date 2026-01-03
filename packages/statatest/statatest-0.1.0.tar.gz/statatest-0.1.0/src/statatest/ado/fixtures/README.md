# Fixtures

Test data fixtures for Stata.

## Available Fixtures

### Panel Data

| Fixture                    | Description                             |
| -------------------------- | --------------------------------------- |
| `fixture_balanced_panel`   | Balanced panel (all units, all periods) |
| `fixture_unbalanced_panel` | Unbalanced panel (varying periods)      |
| `fixture_multilevel_panel` | Nested panel structure                  |

### Network Data

| Fixture                     | Description                                |
| --------------------------- | ------------------------------------------ |
| `fixture_directed_network`  | Directed graph (edges have direction)      |
| `fixture_bipartite_network` | Two-mode network (e.g., employer-employee) |

### Utilities

| Fixture                 | Description                            |
| ----------------------- | -------------------------------------- |
| `fixture_empty_dataset` | Empty dataset with specified variables |
| `fixture_seed`          | Set reproducible random seed           |
| `fixture_tempfile`      | Create temporary file path             |
| `use_fixture`           | Load a fixture by name                 |

## Usage

### Direct Call

```stata
// Create balanced panel
fixture_balanced_panel, id(firm_id) time(year) n_units(100) t_periods(5)

// Create network
fixture_directed_network, source(from_id) dest(to_id) n_nodes(50) density(0.1)
```

### Via use_fixture

```stata
// Use default parameters
use_fixture balanced_panel

// With parameters
use_fixture seed, seed(42)
```

## Common Options

All fixtures support:

- `verbose` - Show creation progress and details

## Example

```stata
// Setup reproducible test data
fixture_seed, seed(12345) verbose
// Output: Setting random seed: seed=12345
// Output: Fixture created: seed

fixture_balanced_panel, id(id) time(t) n_units(10) t_periods(5) verbose
// Output: Creating balanced panel: n_units=10, t_periods=5
// Output: Fixture created: balanced_panel

// Verify structure
assert_count, expected(50)
assert_panel_structure, id(id) time(t)
```
