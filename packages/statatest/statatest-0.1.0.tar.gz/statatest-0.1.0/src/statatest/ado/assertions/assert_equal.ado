*! assert_equal v1.1.0  statatest  2025-12-30
*!
*! Assert that two values are equal.
*!
*! Syntax:
*!   assert_equal actual, expected(value) [message(string) verbose]
*!
*! Options:
*!   verbose  - Show detailed output (expected vs actual values)
*!
*! Example:
*!   assert_equal "`r(N)'", expected("100")
*!   assert_equal `x', expected(5) message("x should be 5") verbose

program define assert_equal, rclass
    version 16

    syntax anything(name=actual), Expected(string) [Message(string) Verbose]

    // Use capture assert to test equality
    capture assert `"`actual'"' == `"`expected'"'

    if _rc == 9 {
        // Minimal output by default
        if "`verbose'" == "" {
            display as error "FAIL: assert_equal: `actual' != `expected'"
        }
        else {
            // Verbose: detailed output
            display as error "ASSERTION FAILED: assert_equal"
            display as error "  Expected: `expected'"
            display as error "  Actual:   `actual'"
        }
        if `"`message'"' != "" {
            display as error "  Message:  `message'"
        }
        noisily display "_STATATEST_FAIL_:assert_equal_:`actual' != `expected'_END_"
        exit 9
    }
    else if _rc != 0 {
        error _rc
    }

    // Success: minimal by default, show PASS with verbose
    if "`verbose'" != "" {
        display as text "PASS: assert_equal"
    }
    noisily display "_STATATEST_PASS_:assert_equal_"

    return local passed "1"
end
