*! use_fixture v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Request a fixture by name, invoking setup if needed.
*!
*! Syntax:
*!   use_fixture name [, scope(string) Verbose]
*!
*! Scopes:
*!   - function (default): Setup/teardown per test function
*!   - module: Setup once per test file, teardown at end
*!   - session: Setup once per test run, teardown at end
*!
*! Example:
*!   use_fixture sample_panel
*!   use_fixture empty_dataset, scope(function)

program define use_fixture, rclass
    version 16

    syntax anything(name=fixture_name), [Scope(string) Verbose]

    // Default scope is function
    if `"`scope'"' == "" {
        local scope "function"
    }

    // Validate scope
    if !inlist(`"`scope'"', "function", "module", "session") {
        display as error "Invalid scope: `scope'"
        display as error "  Valid scopes: function, module, session"
        exit 198
    }

    // Check if fixture is already active (for module/session scopes)
    local fixture_var "_FIXTURE_`fixture_name'"
    capture confirm scalar `fixture_var'
    if _rc == 0 {
        // Fixture already active, skip setup
        return local fixture_name "`fixture_name'"
        return local scope "`scope'"
        return local already_active "1"
        exit
    }

    // Look for fixture setup program
    local setup_prog "fixture_`fixture_name'"
    capture which `setup_prog'
    if _rc != 0 {
        display as error "Fixture not found: `fixture_name'"
        display as error "  Expected program: `setup_prog'"
        exit 111
    }

    // Run fixture setup (pass verbose if specified)
    if "`verbose'" != "" {
        `setup_prog', scope(`scope') verbose
    }
    else {
        `setup_prog', scope(`scope')
    }

    // Mark fixture as active
    scalar `fixture_var' = 1

    // Emit marker for test runner
    noisily display "_STATATEST_FIXTURE_:setup_:`fixture_name'_END_"

    return local fixture_name "`fixture_name'"
    return local scope "`scope'"
    return local already_active "0"
end
