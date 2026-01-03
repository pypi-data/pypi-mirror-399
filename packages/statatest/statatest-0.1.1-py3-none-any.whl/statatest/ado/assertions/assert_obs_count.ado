*! assert_obs_count v1.1.0  statatest  2025-12-30
*! Author: Jose Ignacio Gonzalez Rojas
*!
*! Assert that the observation count matches expected value.
*!
*! Syntax:
*!   assert_obs_count expected [if] [, message(string) verbose]
*!
*! Options:
*!   message(str)  - Custom error message
*!   verbose       - Show detailed output (PASS on success, full details on failure)
*!
*! Example:
*!   assert_obs_count 100
*!   assert_obs_count 50 if foreign == 1, verbose

program define assert_obs_count, rclass
    version 16

    syntax anything(name=expected) [if] [, Message(string) Verbose]

    // Count observations
    if `"`if'"' != "" {
        quietly count `if'
    }
    else {
        quietly count
    }
    local actual = r(N)

    if `actual' != `expected' {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_obs_count"
            display as error "  Expected: `expected'"
            display as error "  Actual:   `actual'"
            if `"`if'"' != "" {
                display as error "  Condition: `if'"
            }
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_obs_count: `actual' != `expected' observations"
        }
        // Emit failure marker
        noisily display "_STATATEST_FAIL_:assert_obs_count_:`actual' != `expected'_END_"
        exit 9
    }

    // Emit success marker (only if verbose)
    if "`verbose'" != "" {
        noisily display "PASS: assert_obs_count"
    }
    noisily display "_STATATEST_PASS_:assert_obs_count_"

    return local passed "1"
    return local count "`actual'"
end
