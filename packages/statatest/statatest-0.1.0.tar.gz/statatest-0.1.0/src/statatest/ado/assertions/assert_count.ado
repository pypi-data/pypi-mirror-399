*! assert_count v1.1.0  statatest  2025-12-30
*! Assert that the dataset has the expected number of observations.
*!
*! Syntax:
*!   assert_count, expected(integer) [if] [message(string)] [Verbose]
*!
*! Examples:
*!   sysuse auto, clear
*!   assert_count, expected(74)
*!   assert_count if foreign == 1, expected(22)

program define assert_count, rclass
    version 16

    syntax [if], Expected(integer) [Message(string)] [Verbose]

    // Count observations (with optional if condition)
    if `"`if'"' != "" {
        quietly count `if'
    }
    else {
        quietly count
    }
    local actual = r(N)

    // Compare actual vs expected
    if `actual' != `expected' {
        if "`verbose'" != "" {
            display as error "ASSERTION FAILED: assert_count"
            display as error "  Expected: `expected' observations"
            display as error "  Actual:   `actual' observations"
            if `"`message'"' != "" {
                display as error "  Message:  `message'"
            }
        }
        else {
            display as error "FAIL: assert_count: `actual' != `expected' observations"
        }
        noisily display "_STATATEST_FAIL_:assert_count_:`actual' != `expected'_END_"
        exit 9
    }

    if "`verbose'" != "" {
        display as text "PASS: assert_count"
    }
    noisily display "_STATATEST_PASS_:assert_count_"

    return local passed "1"
    return scalar count = `actual'
end
