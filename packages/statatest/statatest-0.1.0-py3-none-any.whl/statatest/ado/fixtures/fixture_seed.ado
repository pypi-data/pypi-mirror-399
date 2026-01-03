*! fixture_seed v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Built-in fixture: Sets a reproducible random seed.
*!
*! Syntax:
*!   fixture_seed [, scope(string) seed(integer) Verbose]
*!
*! Example:
*!   use_fixture seed
*!   // Now have reproducible seed (default: 12345)
*!
*!   fixture_seed, seed(42)
*!   // Now have seed set to 42

program define fixture_seed, rclass
    version 16

    syntax [, Scope(string) SEED(integer 12345) Verbose]

    // Display creation message if verbose
    if "`verbose'" != "" {
        display as text "Setting random seed: seed=`seed'"
    }

    // Store original seed state for restoration
    local original_seed = c(rngstate)
    global _FIXTURE_seed_original "`original_seed'"

    // Set reproducible seed
    set seed `seed'

    // Display completion message if verbose
    if "`verbose'" != "" {
        display as text "Fixture created: seed"
    }

    return local seed "`seed'"
end

program define fixture_seed_teardown
    // Restore original seed state if stored
    if "$_FIXTURE_seed_original" != "" {
        set rngstate $_FIXTURE_seed_original
    }

    // Clear globals
    global _FIXTURE_seed_original

    // Clear fixture marker
    capture scalar drop _FIXTURE_seed

    // Emit marker
    noisily display "_STATATEST_FIXTURE_:teardown_:seed_END_"
end
