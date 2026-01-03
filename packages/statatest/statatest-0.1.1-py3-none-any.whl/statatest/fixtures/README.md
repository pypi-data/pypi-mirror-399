# Fixtures Module (Python)

Manage test fixtures from Python side.

## Components

| File         | Purpose                                    |
| ------------ | ------------------------------------------ |
| `manager.py` | Fixture registration, activation, teardown |

## Overview

This module handles:

1. **Discovery**: Find `conftest.do` files
2. **Parsing**: Extract fixture definitions
3. **Management**: Track fixture state across tests

## Conftest Files

```stata
// conftest.do

// Define fixture setup
program define setup_mydata
    sysuse auto, clear
    keep if foreign == 1
end

// Define fixture teardown
program define teardown_mydata
    clear
end
```

## Fixture Flow

```plaintext
1. Before test: Execute setup programs
2. Test execution: Fixture data available
3. After test: Execute teardown programs
```

## Note

The actual fixture implementations (panel data, networks, etc.) are in
`ado/fixtures/`. This module coordinates their use from Python.

## Dependencies

- **Depends on**: `core`
- **Used by**: `execution`
